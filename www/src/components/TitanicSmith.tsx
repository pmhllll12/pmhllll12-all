"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";

type ChatMessage = {
  id: string;
  role: "user" | "model";
  text: string;
  pending?: boolean;
};

type SmithChatResponse = {
  reply: string;
  model: string;
};

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.trim();
  if (base) {
    return `${base.replace(/\/$/, "")}${path}`;
  }
  return path;
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

async function postSmithChat(message: string): Promise<SmithChatResponse> {
  const res = await fetch(apiUrl("/api/titanic/smith/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const raw = await res.text();
  if (!res.ok) {
    throw new Error(parseApiError(raw, res.status));
  }
  const data = JSON.parse(raw) as SmithChatResponse;
  if (!data.reply?.trim()) {
    throw new Error("선장이 비어 있는 응답을 반환했습니다.");
  }
  return { reply: data.reply.trim(), model: data.model ?? "" };
}

const WELCOME =
  "안녕하시오. 나는 RMS 타이타닉의 선장 에드워드 스미스라오. 배와 바다, 그날의 일—무엇이든 물어보시오.";

export default function TitanicSmith() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: "welcome", role: "model", text: WELCOME },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  useEffect(() => {
    requestAnimationFrame(scrollToBottom);
  }, [messages, scrollToBottom]);

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
      text: "…잠시만 기다려 주시오.",
      pending: true,
    };

    setMessages((prev) => [...prev, userMsg, pending]);
    setLoading(true);
    try {
      const { reply, model } = await postSmithChat(text);
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
    <section
      className="flex flex-col w-full min-h-[min(520px,calc(100vh-200px))] max-h-[min(720px,calc(100vh-160px))] box-border"
      aria-labelledby="smith-chat-heading"
    >
      <div className="flex-shrink-0 mb-3">
        <span className="inline-block px-[10px] py-1 rounded-md text-[11px] font-extrabold tracking-[0.08em] uppercase text-[#0c4a6e] bg-[linear-gradient(135deg,#bae6fd,#7dd3fc)]">
          LESSON
        </span>
        <h2
          id="smith-chat-heading"
          className="mt-[10px] mb-[6px] text-[1.2rem] font-extrabold text-[#0f172a] tracking-[-0.02em]"
        >
          스미스 선장과의 대화
        </h2>
        <p className="mb-2 text-xs text-[#64748b] [&_code]:text-[11px] [&_code]:px-[5px] [&_code]:py-px [&_code]:rounded [&_code]:bg-[#f1f5f9] [&_code]:text-[#0369a1]">
          API: <code>POST /api/titanic/smith/chat</code>
          {modelName ? (
            <>
              {" "}
              · 모델: <code>{modelName}</code>
            </>
          ) : null}
        </p>
        <p className="p-[10px_12px] text-xs leading-[1.55] text-[#475569] bg-[#f8fafc] border border-[#e2e8f0] rounded-lg [&_code]:text-[11px] [&_code]:break-all">
          타이타닉·항해·1912년에 대해 물어보세요. 백엔드 <code>apps/.env</code> 에{" "}
          <code>GEMINI_API_KEY</code> 가 있어야 답변이 생성됩니다.
        </p>
      </div>

      {error ? (
        <div
          className="flex-shrink-0 mb-[10px] p-[10px_12px] text-[13px] leading-[1.5] text-[#b91c1c] bg-[#fef2f2] border border-[#fecaca] rounded-lg"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <div
        className="flex-1 min-h-[200px] overflow-y-auto p-[12px_4px] mb-3 border border-[#e2e8f0] rounded-xl bg-white flex flex-col gap-[10px]"
        ref={listRef}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            className={
              m.role === "user"
                ? "max-w-[min(92%,560px)] p-[10px_14px] rounded-xl leading-[1.5] self-end bg-[#0ea5e9] text-white rounded-br-[4px]"
                : "max-w-[min(92%,560px)] p-[10px_14px] rounded-xl leading-[1.5] self-start bg-[#f1f5f9] text-[#0f172a] border border-[#e2e8f0] rounded-bl-[4px]"
            }
          >
            <span
              className={
                m.role === "user"
                  ? "block text-[11px] font-bold tracking-[0.04em] uppercase mb-1 opacity-85 text-[rgba(255,255,255,0.9)]"
                  : "block text-[11px] font-bold tracking-[0.04em] uppercase mb-1 opacity-85 text-[#64748b]"
              }
            >
              {m.role === "user" ? "나" : "스미스 선장"}
            </span>
            <p
              className={
                m.pending
                  ? "m-0 text-sm whitespace-pre-wrap break-words opacity-75 italic"
                  : "m-0 text-sm whitespace-pre-wrap break-words"
              }
            >
              {m.text}
            </p>
          </div>
        ))}
      </div>

      <form
        className="flex-shrink-0 flex flex-col items-stretch gap-[10px] 600:flex-row 600:items-end"
        onSubmit={onSubmit}
      >
        <textarea
          className="flex-1 resize-y min-h-[44px] max-h-[160px] p-[10px_12px] text-sm border border-[#cbd5e1] rounded-[10px] bg-white text-[#0f172a] focus:outline-none focus:border-[#0ea5e9] focus:shadow-[0_0_0_3px_rgba(14,165,233,0.2)] disabled:opacity-65 disabled:cursor-not-allowed"
          rows={2}
          placeholder="타이타닉에 대해 물어보세요…"
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
          className="flex-shrink-0 w-full 600:w-auto px-[18px] py-[10px] text-sm font-bold text-white bg-[#0369a1] border-none rounded-[10px] cursor-pointer transition enabled:hover:bg-[#075985] disabled:opacity-55 disabled:cursor-not-allowed"
          disabled={loading || !input.trim()}
        >
          {loading ? "전송 중…" : "보내기"}
        </button>
      </form>
    </section>
  );
}
