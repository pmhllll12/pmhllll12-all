"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";

type ChatMessage = {
  id: string;
  role: "user" | "model";
  text: string;
  pending?: boolean;
};

type ChatResponse = {
  reply: string;
  model: string;
  intentLabel: string;
  intentConfidence: number;
};

const CHAT_URL = "/api/ontology/semantic-chat";

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function parseApiError(raw: string, status: number): string {
  try {
    const j = JSON.parse(raw) as {
      detail?: string | Array<{ msg?: string }>;
    };
    if (typeof j.detail === "string") return j.detail;
    if (Array.isArray(j.detail)) {
      const parts = j.detail
        .map((d) => (typeof d === "object" && d?.msg ? d.msg : String(d)))
        .filter(Boolean);
      if (parts.length) return parts.join(", ");
    }
  } catch {
    /* ignore */
  }
  return raw.trim() || `HTTP ${status}`;
}

async function postChat(message: string): Promise<ChatResponse> {
  const res = await fetch(CHAT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const raw = await res.text();
  if (!res.ok) {
    throw new Error(parseApiError(raw, res.status));
  }

  const data = JSON.parse(raw) as {
    reply: string;
    model: string;
    intent_label: string;
    intent_confidence: number;
  };
  if (!data.reply?.trim()) {
    throw new Error("모델이 비어 있는 응답을 반환했습니다.");
  }
  return {
    reply: data.reply.trim(),
    model: data.model ?? "",
    intentLabel: data.intent_label ?? "",
    intentConfidence: data.intent_confidence ?? 0,
  };
}

export default function LangchainChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string | null>(null);
  const [intent, setIntent] = useState<{ label: string; confidence: number } | null>(
    null,
  );
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const scrollToBottom = useCallback(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setInput("");

    const userMsg: ChatMessage = { id: uid(), role: "user", text };
    const pendingId = uid();
    const pending: ChatMessage = {
      id: pendingId,
      role: "model",
      text: "답변을 생성하는 중…",
      pending: true,
    };

    setMessages((prev) => [...prev, userMsg, pending]);
    requestAnimationFrame(scrollToBottom);

    setLoading(true);
    try {
      const { reply, model, intentLabel, intentConfidence } = await postChat(text);
      if (model) setModelName(model);
      if (intentLabel) setIntent({ label: intentLabel, confidence: intentConfidence });

      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId ? { ...m, text: reply, pending: false } : m,
        ),
      );
    } catch (e) {
      const msg =
        e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다.";
      setMessages((prev) => prev.filter((m) => m.id !== pendingId));
      setError(msg);
    } finally {
      setLoading(false);
      requestAnimationFrame(scrollToBottom);
    }
  }, [input, loading, scrollToBottom]);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void send();
  };

  return (
    <aside
      className="langchain-chat flex flex-col w-full max-w-[min(400px,100%)] 1200:max-w-none min-h-[min(560px,calc(100vh-120px))] 1200:min-h-0 max-h-[calc(100vh-100px)] 1200:max-h-none mx-auto p-4 rounded-2xl bg-[rgba(10,16,32,0.75)] border border-[rgba(148,163,184,0.22)] shadow-[0_0_0_1px_rgba(52,211,153,0.08),0_24px_48px_rgba(0,0,0,0.35)] backdrop-blur-md box-border"
      aria-label="LangChain 채팅"
      id="langchain-chat"
    >
      <div className="flex-shrink-0 mb-2 1200:mb-3 flex flex-wrap 1200:block items-center gap-[8px_12px]">
        <span className="inline-block px-[10px] py-1 rounded-md text-[11px] font-extrabold tracking-[0.08em] uppercase text-[#041a12] bg-[linear-gradient(135deg,#34d399,#22c55e)]">
          LangChain
        </span>
        <h2 className="m-0 flex-1 1200:flex-none min-w-0 text-[17px] 1200:text-lg font-extrabold text-fg-0 leading-[1.2] 1200:mt-2 1200:mb-1">
          LangChain과 대화
        </h2>
        <p className="m-0 text-xs text-fg-3 [&_code]:text-[11px] [&_code]:text-accent">
          API: <code>POST /api/ontology/semantic-chat</code>
          {modelName ? (
            <>
              {" "}
              · 모델: <code>{modelName}</code>
            </>
          ) : null}
          {intent ? (
            <>
              {" "}
              · 의도: <code>{intent.label}</code> ({intent.confidence.toFixed(2)})
            </>
          ) : null}
        </p>
      </div>

      <p className="hidden 1200:block flex-shrink-0 mb-3 p-[10px_12px] text-xs leading-[1.55] text-fg-2 bg-[rgba(52,211,153,0.08)] border border-[rgba(52,211,153,0.25)] rounded-[10px]">
        메시지를 먼저 시멘틱 라우터가 의도(인사·질문·요청·잡담·불만)로 분류한 뒤,
        LangChain(LCEL) + 로컬 Ollama 챗봇 엔진이 그 의도를 참고해 답합니다. 위
        제미나이 채팅과 달리 월드컵 데이터 없이 일반 대화만 나눕니다. 로컬에{" "}
        <code>ollama serve</code>가 켜져 있어야(임베딩·채팅 모델 모두) 답이
        옵니다.
      </p>

      {error ? (
        <div
          className="flex-shrink-0 mb-[10px] p-[10px_12px] text-xs leading-[1.5] text-[#fecaca] bg-[rgba(239,68,68,0.15)] border border-[rgba(239,68,68,0.35)] rounded-[10px] max-h-[120px] overflow-y-auto"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
        <div
          className="flex-1 min-h-0 overflow-y-auto p-[4px_2px_12px] flex flex-col gap-[10px]"
          ref={listRef}
        >
          {messages.length === 0 ? (
            <p className="m-0 p-[20px_12px] text-center text-[13px] leading-[1.6] text-fg-3">
              무엇이든 편하게 물어보세요.
            </p>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={
                  m.role === "user"
                    ? "p-[10px_12px] rounded-xl max-w-full self-end bg-[rgba(52,211,153,0.18)] border border-[rgba(52,211,153,0.35)]"
                    : "p-[10px_12px] rounded-xl max-w-full self-start bg-[rgba(148,163,184,0.1)] border border-[rgba(148,163,184,0.2)]"
                }
              >
                <span className="block text-[10px] font-extrabold tracking-[0.06em] uppercase text-fg-3 mb-1">
                  {m.role === "user" ? "나" : "LangChain"}
                </span>
                <p
                  className={
                    m.pending
                      ? "m-0 text-[13px] leading-[1.55] text-fg-3 italic whitespace-pre-wrap break-words"
                      : "m-0 text-[13px] leading-[1.55] text-fg-1 whitespace-pre-wrap break-words"
                  }
                >
                  {m.text}
                </p>
              </div>
            ))
          )}
        </div>
      </div>

      <form
        className="flex-shrink-0 flex flex-row 1200:flex-col items-stretch gap-[10px] 1200:gap-2 pt-[10px] 1200:pt-2 border-t border-[rgba(148,163,184,0.15)]"
        onSubmit={onSubmit}
      >
        <textarea
          ref={inputRef}
          className="flex-1 1200:w-full min-w-0 min-h-[44px] 1200:min-h-0 max-h-[100px] 1200:max-h-none resize-none rounded-[10px] border border-[rgba(148,163,184,0.25)] bg-[rgba(4,7,15,0.6)] text-fg-0 text-[13px] leading-[1.45] p-[10px_12px] box-border focus:outline-none focus:border-accent focus:shadow-[0_0_0_2px_rgba(52,211,153,0.2)] disabled:opacity-55 disabled:cursor-not-allowed"
          rows={2}
          placeholder="메시지를 입력하세요…"
          value={input}
          disabled={loading}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
        />
        <button
          type="submit"
          className="self-stretch 1200:self-end flex-none px-4 1200:px-5 py-[10px] rounded-xl 1200:rounded-full font-bold text-[13px] cursor-pointer bg-[#34d399] text-[#041a12] transition enabled:hover:bg-[#22c55e] disabled:opacity-45 disabled:cursor-not-allowed"
          disabled={loading || !input.trim()}
        >
          {loading ? "전송 중…" : "보내기"}
        </button>
      </form>
    </aside>
  );
}
