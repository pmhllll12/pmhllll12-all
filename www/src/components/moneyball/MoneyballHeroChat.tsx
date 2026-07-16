"use client";

import { useState, type FormEvent } from "react";
import { ChevronDown, Mic, Plus, Send, SlidersHorizontal } from "lucide-react";

type MoneyballHeroChatProps = {
  className?: string;
};

export function MoneyballHeroChat({ className }: MoneyballHeroChatProps) {
  const [input, setInput] = useState("");

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
  };

  return (
    <div className={`w-full max-w-2xl ${className ?? ""}`}>
      <form
        onSubmit={onSubmit}
        className="rounded-3xl border border-border bg-bg-1 p-4 text-left shadow-sm"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="어제 (2012년 8월 3일) 이긴 팀이 어디야."
          rows={1}
          className="w-full resize-none border-0 bg-transparent text-base text-fg-0 placeholder:text-fg-3 focus:outline-none"
        />

        <div className="mt-3 flex items-center justify-between border-t border-border pt-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="flex h-8 w-8 items-center justify-center rounded-full border border-border text-fg-2 hover:bg-chip-bg"
              aria-label="첨부"
            >
              <Plus className="h-4 w-4" />
            </button>
            <button
              type="button"
              className="flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-sm text-fg-2 hover:bg-chip-bg"
            >
              <SlidersHorizontal className="h-4 w-4" />
              도구
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="flex items-center gap-1 rounded-full border border-border px-3 py-1.5 text-sm text-fg-1 hover:bg-chip-bg"
            >
              빠른 응답
              <ChevronDown className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              className="flex h-8 w-8 items-center justify-center rounded-full text-fg-2 hover:bg-chip-bg"
              aria-label="음성 입력"
            >
              <Mic className="h-4 w-4" />
            </button>
            <button
              type="submit"
              disabled={!input.trim()}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600 text-white transition enabled:hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="보내기"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </form>

      <p className="mt-3 text-center text-xs text-fg-3">
        축구 마스터는 AI로서 실수를 할 수 있으며, 경기 기록·통계도 부정확할 수 있습니다.{" "}
        <a
          href="https://policies.google.com/privacy"
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-fg-1"
        >
          Google 개인정보처리방침
        </a>
      </p>
    </div>
  );
}
