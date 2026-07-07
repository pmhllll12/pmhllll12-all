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
};

function getChatUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  if (typeof base === "string" && base.trim()) {
    return `${base.replace(/\/$/, "")}/chat`;
  }
  return "/chat";
}

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
  const res = await fetch(getChatUrl(), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const raw = await res.text();
  if (!res.ok) {
    throw new Error(parseApiError(raw, res.status));
  }

  const data = JSON.parse(raw) as ChatResponse;
  if (!data.reply?.trim()) {
    throw new Error("모델이 비어 있는 응답을 반환했습니다.");
  }
  return { reply: data.reply.trim(), model: data.model ?? "" };
}

type GeminiChatProps = {
  preset?: { key: number; text: string } | null;
  onPresetConsumed?: () => void;
};

export default function GeminiChat({
  preset,
  onPresetConsumed,
}: GeminiChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!preset?.text) return;
    setInput(preset.text);
    onPresetConsumed?.();
    requestAnimationFrame(() => {
      inputRef.current?.focus();
      inputRef.current?.select();
    });
  }, [preset?.key, preset?.text, onPresetConsumed]);

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
      const { reply, model } = await postChat(text);
      if (model) setModelName(model);

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
      className="gemini-chat flex flex-col w-full max-w-[min(400px,100%)] 1200:max-w-none min-h-[min(560px,calc(100vh-120px))] 1200:min-h-0 max-h-[calc(100vh-100px)] 1200:max-h-none mx-auto p-4 rounded-2xl bg-[rgba(10,16,32,0.75)] border border-[rgba(148,163,184,0.22)] shadow-[0_0_0_1px_rgba(34,211,238,0.08),0_24px_48px_rgba(0,0,0,0.35)] backdrop-blur-md box-border"
      aria-label="Gemini 채팅"
      id="gemini-chat"
    >
      <div className="flex-shrink-0 mb-2 1200:mb-3 flex flex-wrap 1200:block items-center gap-[8px_12px]">
        <span className="inline-block px-[10px] py-1 rounded-md text-[11px] font-extrabold tracking-[0.08em] uppercase text-[#04131a] bg-[linear-gradient(135deg,#22d3ee,#38bdf8)]">
          Gemini
        </span>
        <h2 className="m-0 flex-1 1200:flex-none min-w-0 text-[17px] 1200:text-lg font-extrabold text-fg-0 leading-[1.2] 1200:mt-2 1200:mb-1">
          제미나이와 대화
        </h2>
        <p className="m-0 text-xs text-fg-3 [&_code]:text-[11px] [&_code]:text-accent">
          API: <code>POST /chat</code>
          {modelName ? (
            <>
              {" "}
              · 모델: <code>{modelName}</code>
            </>
          ) : null}
        </p>
      </div>

      <p className="hidden 1200:block flex-shrink-0 mb-3 p-[10px_12px] text-xs leading-[1.55] text-fg-2 bg-[rgba(34,211,238,0.08)] border border-[rgba(34,211,238,0.25)] rounded-[10px] [&_a]:text-accent [&_a]:underline [&_code]:text-[11px] [&_code]:break-all">
        백엔드 <code>POST /chat</code> 로 연결됩니다. PC 브라우저에서는 Next.js가{" "}
        <code>/chat</code> 을 같은 PC의 API(기본 <code>127.0.0.1:8000</code>)로 프록시합니다.
        <br />
        <strong>폰·다른 기기·웹뷰 앱</strong>에서는 <code>localhost</code> 가 그 기기를 가리키므로,
        PC 브라우저는 <code>http://localhost:3000</code> 만 사용하세요. 폰은 터미널의{" "}
        <code>Network</code> 주소(예: <code>http://192.168.x.x:3000</code>)로 접속합니다. 빌드된 앱이 API를 직접 부를 때는{" "}
        <code>.env</code> 의 <code>NEXT_PUBLIC_API_BASE=http://&lt;PC_LAN_IP&gt;:8000</code> 로 빌드하고,
        API는 <code>API_HOST=0.0.0.0</code> 로 실행합니다. 자세히는{" "}
        <code>frontend/DEV_SERVER.md</code> 를 보세요.
        <br />
        <code>backend/apps/.env</code> 에 <code>GEMINI_API_KEY</code> 를 넣고 API 서버(
        <code>python main.py</code>)를 켜 두세요.
      </p>

      <p className="hidden 1200:block flex-shrink-0 mb-3 p-[8px_10px] text-xs leading-[1.5] text-[rgba(226,232,240,0.92)] border-l-[3px] border-l-accent bg-[rgba(255,255,255,0.03)] rounded-[0_8px_8px_0] [&_strong]:text-accent">
        <strong>AI 승부 예측</strong> — 예측 패널의「AI에게 이 경기 물어보기」를 누르면
        여기에 질문이 채워집니다. 승률·예상 스코어를 물어보세요.
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
              월드컵 일정, 규칙, 팀 정보 등 무엇이든 물어보세요.
            </p>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={
                  m.role === "user"
                    ? "p-[10px_12px] rounded-xl max-w-full self-end bg-[rgba(34,211,238,0.18)] border border-[rgba(34,211,238,0.35)]"
                    : "p-[10px_12px] rounded-xl max-w-full self-start bg-[rgba(148,163,184,0.1)] border border-[rgba(148,163,184,0.2)]"
                }
              >
                <span className="block text-[10px] font-extrabold tracking-[0.06em] uppercase text-fg-3 mb-1">
                  {m.role === "user" ? "나" : "Gemini"}
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
          className="flex-1 1200:w-full min-w-0 min-h-[44px] 1200:min-h-0 max-h-[100px] 1200:max-h-none resize-none rounded-[10px] border border-[rgba(148,163,184,0.25)] bg-[rgba(4,7,15,0.6)] text-fg-0 text-[13px] leading-[1.45] p-[10px_12px] box-border focus:outline-none focus:border-accent focus:shadow-[0_0_0_2px_rgba(34,211,238,0.2)] disabled:opacity-55 disabled:cursor-not-allowed"
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
          className="self-stretch 1200:self-end flex-none px-4 1200:px-5 py-[10px] rounded-xl 1200:rounded-full font-bold text-[13px] cursor-pointer bg-accent text-[#04131a] transition enabled:hover:bg-accent-strong disabled:opacity-45 disabled:cursor-not-allowed"
          disabled={loading || !input.trim()}
        >
          {loading ? "전송 중…" : "보내기"}
        </button>
      </form>
    </aside>
  );
}
