"use client";

import { useState } from "react";

type Status = { type: "idle" | "loading" | "ok" | "error"; message: string };

export default function TelegramPanel() {
  const [chatId, setChatId] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<Status>({ type: "idle", message: "" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus({ type: "loading", message: "전송 중..." });

    try {
      const res = await fetch("/api/community/telegram/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, message }),
      });

      if (res.ok) {
        setStatus({ type: "ok", message: "텔레그램 메시지가 전송됐습니다." });
        setMessage("");
      } else {
        const data = await res.json().catch(() => ({}));
        setStatus({
          type: "error",
          message: (data as { detail?: string }).detail ?? "전송 실패. 봇 토큰·채팅 ID를 확인하세요.",
        });
      }
    } catch {
      setStatus({ type: "error", message: "네트워크 오류가 발생했습니다." });
    }
  }

  const statusColor: Record<Status["type"], string> = {
    idle: "",
    loading: "text-fg-2",
    ok: "text-green-400",
    error: "text-red-400",
  };

  return (
    <div className="max-w-[520px] flex flex-col gap-5">
      <div>
        <h2 className="m-0 text-base font-extrabold tracking-[0.04em]">✈️ 텔레그램</h2>
        <p className="mt-1 text-[11px] text-fg-2">
          Telegram Bot API → 채팅방으로 메시지 전송
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        noValidate
        className="flex flex-col gap-4 bg-bg-1 border border-border rounded-2xl p-5 shadow-[0_8px_24px_rgba(0,0,0,0.35)]"
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-[11px] font-bold tracking-[0.06em] uppercase text-fg-2">
            채팅 ID <span className="text-fg-2 font-normal normal-case">(비우면 .env의 DEVELOPER_CHAT_ID 사용)</span>
          </span>
          <input
            type="text"
            value={chatId}
            onChange={(e) => setChatId(e.target.value)}
            placeholder="@username 또는 숫자 Chat ID (선택)"
            className="w-full bg-bg-0 border border-border rounded-xl px-3 py-2.5 text-sm text-fg-0 placeholder:text-fg-2 focus:outline-none focus:border-accent"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-[11px] font-bold tracking-[0.06em] uppercase text-fg-2">
            메시지 <span className="text-fg-2 font-normal normal-case">(비우면 기본 메시지 전송)</span>
          </span>
          <textarea
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="전송할 메시지를 입력하세요 (선택)"
            className="w-full bg-bg-0 border border-border rounded-xl px-3 py-2.5 text-sm text-fg-0 placeholder:text-fg-2 focus:outline-none focus:border-accent resize-none"
          />
        </label>

        <button
          type="submit"
          disabled={status.type === "loading"}
          className="w-full py-2.5 rounded-xl font-bold text-sm tracking-[0.04em] bg-accent text-[#04131a] transition hover:bg-accent-strong disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status.type === "loading" ? "전송 중..." : "메시지 전송"}
        </button>

        {status.type !== "idle" && (
          <p className={`text-xs text-center ${statusColor[status.type]}`}>
            {status.message}
          </p>
        )}
      </form>

      <div className="bg-bg-1 border border-border rounded-2xl p-4 text-[11px] text-fg-2 leading-[1.7]">
        <p className="m-0 font-bold text-fg-0 mb-1">설정 방법</p>
        <ol className="m-0 pl-4 flex flex-col gap-0.5">
          <li>@BotFather 에서 봇 생성 → 토큰 발급</li>
          <li><code className="bg-bg-0 px-1 rounded">minho/.env</code>에 <code className="bg-bg-0 px-1 rounded">TELEGRAM_BOT_TOKEN=...</code> 추가</li>
          <li>봇을 채팅방에 초대 후 채팅 ID 입력</li>
        </ol>
      </div>
    </div>
  );
}
