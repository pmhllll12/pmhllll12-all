"use client";

import { useEffect, useRef, useState } from "react";

type FormState = { toEmail: string; topic: string };
type Status = { type: "idle" | "loading" | "ok" | "spam" | "error"; message: string };
type Suggestion = { nickname: string; email: string };

export default function EmailPanel() {
  const [form, setForm] = useState<FormState>({ toEmail: "", topic: "" });
  const [status, setStatus] = useState<Status>({ type: "idle", message: "" });
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showDrop, setShowDrop] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dropRef = useRef<HTMLDivElement>(null);

  // 이메일 입력 → 200ms 디바운스 → 주소록 검색
  function handleEmailChange(value: string) {
    setForm((p) => ({ ...p, toEmail: value }));

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!value.trim()) {
      setSuggestions([]);
      setShowDrop(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `/api/community/juso/search?q=${encodeURIComponent(value.trim())}`,
        );
        if (!res.ok) return;
        const data = (await res.json()) as { results: Suggestion[] };
        setSuggestions(data.results ?? []);
        setShowDrop((data.results ?? []).length > 0);
      } catch {
        // 검색 실패는 조용히 무시
      }
    }, 200);
  }

  function pickSuggestion(email: string) {
    setForm((p) => ({ ...p, toEmail: email }));
    setSuggestions([]);
    setShowDrop(false);
  }

  // 드롭다운 바깥 클릭 시 닫기
  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) {
        setShowDrop(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setShowDrop(false);
    setStatus({ type: "loading", message: "EXAONE 스팸 판정 중..." });

    try {
      const res = await fetch("/api/community/email/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to_email: form.toEmail, topic: form.topic }),
      });

      if (res.ok) {
        setStatus({ type: "ok", message: "이메일이 성공적으로 발송됐습니다." });
        setForm({ toEmail: "", topic: "" });
      } else if (res.status === 400) {
        const data = await res.json();
        setStatus({ type: "spam", message: data.detail ?? "스팸으로 판정됐습니다." });
      } else {
        setStatus({ type: "error", message: "발송 실패. n8n 워크플로우를 확인하세요." });
      }
    } catch {
      setStatus({ type: "error", message: "네트워크 오류가 발생했습니다." });
    }
  }

  const statusColor: Record<Status["type"], string> = {
    idle: "",
    loading: "text-fg-2",
    ok: "text-green-400",
    spam: "text-yellow-400",
    error: "text-red-400",
  };

  return (
    <div className="max-w-[520px] flex flex-col gap-5">
      <div>
        <h2 className="m-0 text-base font-extrabold tracking-[0.04em]">📬 메일관리</h2>
        <p className="mt-1 text-[11px] text-fg-2">
          EXAONE 스팸 판정 → n8n → Gmail 자동 발송
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 bg-bg-1 border border-border rounded-2xl p-5 shadow-[0_8px_24px_rgba(0,0,0,0.35)]"
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-[11px] font-bold tracking-[0.06em] uppercase text-fg-2">
            수신자 이메일
          </span>
          {/* 상대 위치 컨테이너 — 드롭다운 기준점 */}
          <div className="relative" ref={dropRef}>
            <input
              type="email"
              required
              value={form.toEmail}
              onChange={(e) => handleEmailChange(e.target.value)}
              onFocus={() => suggestions.length > 0 && setShowDrop(true)}
              placeholder="example@gmail.com"
              className="w-full bg-bg-0 border border-border rounded-xl px-3 py-2.5 text-sm text-fg-0 placeholder:text-fg-2 focus:outline-none focus:border-accent"
              autoComplete="off"
            />

            {showDrop && (
              <ul className="absolute z-50 left-0 right-0 top-[calc(100%+4px)] bg-bg-1 border border-border rounded-xl shadow-[0_8px_24px_rgba(0,0,0,0.5)] overflow-hidden">
                {suggestions.map((s) => (
                  <li key={s.email}>
                    <button
                      type="button"
                      onMouseDown={(e) => {
                        // mousedown 으로 처리해야 input onBlur 보다 먼저 실행됨
                        e.preventDefault();
                        pickSuggestion(s.email);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-[rgba(0,229,255,0.08)] transition"
                    >
                      <span className="text-[13px] font-semibold text-fg-0 shrink-0">
                        {s.nickname}
                      </span>
                      <span className="text-[11px] text-accent truncate">{s.email}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-[11px] font-bold tracking-[0.06em] uppercase text-fg-2">
            이메일 주제
          </span>
          <textarea
            required
            rows={3}
            value={form.topic}
            onChange={(e) => setForm((p) => ({ ...p, topic: e.target.value }))}
            placeholder="내일 오후 2시 회의 일정 안내"
            className="w-full bg-bg-0 border border-border rounded-xl px-3 py-2.5 text-sm text-fg-0 placeholder:text-fg-2 focus:outline-none focus:border-accent resize-none"
          />
        </label>

        <button
          type="submit"
          disabled={status.type === "loading"}
          className="w-full py-2.5 rounded-xl font-bold text-sm tracking-[0.04em] bg-accent text-[#04131a] transition hover:bg-accent-strong disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status.type === "loading" ? "판정 중..." : "이메일 발송"}
        </button>

        {status.type !== "idle" && (
          <p className={`text-xs text-center ${statusColor[status.type]}`}>
            {status.message}
          </p>
        )}
      </form>
    </div>
  );
}
