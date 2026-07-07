"use client";

import { useState } from "react";
import Link from "next/link";
import { openFullWorldCupSchedule } from "@/wcScheduleOpen";
import HeroPredictionPanel from "./HeroPredictionPanel";
import TodayBroadcastModal from "./TodayBroadcastModal";

const CHIPS = [
  "예측·P",
  "AI 분석",
  "본선",
  "조 편성",
  "16강",
  "8강",
  "라이브 스코어",
  "골 순위",
  "하이라이트",
  "응원단",
  "통계",
];

type HeroProps = {
  onGeminiPreset?: (text: string) => void;
  /** false면 예측 패널 미포함 — Home에서 제미나이 아래로 배치 */
  showPrediction?: boolean;
};

const BTN_BASE =
  "inline-flex items-center gap-[10px] p-[14px_26px] rounded-full font-bold text-[15px] border-none transition cursor-pointer w-full justify-center 380:w-auto 380:justify-normal";
const BTN_PRIMARY = "bg-accent text-[#04131a] hover:bg-accent-strong hover:-translate-y-px";
const BTN_GHOST =
  "bg-transparent text-fg-0 border border-[rgba(255,255,255,0.22)] hover:border-[rgba(255,255,255,0.55)] hover:bg-[rgba(255,255,255,0.04)]";

export default function Hero({
  onGeminiPreset,
  showPrediction = true,
}: HeroProps) {
  const [todayBroadcastOpen, setTodayBroadcastOpen] = useState(false);

  return (
    <section className="flex flex-row justify-center items-center w-full box-border min-h-0 1200:min-h-[calc(100vh-76px)]">
      <div className="relative w-full box-border mx-auto max-w-[min(720px,100%)] p-[40px_0_48px] 720:p-[32px_0_40px] 1200:max-w-[720px] 1200:p-[80px_20px_96px]">
        <div
          id="schedule"
          className="absolute top-0 left-0 w-px h-px overflow-hidden pointer-events-none [scroll-margin-top:96px]"
          aria-hidden
        />
        <span className="inline-flex items-center p-[8px_16px] rounded-full bg-accent-soft border border-[rgba(34,211,238,0.45)] text-accent font-bold text-[13px] tracking-[0.16em]">
          FIFA WORLD CUP 2026
        </span>

        <h1 className="mt-4 mb-5 720:mt-6 720:mb-7 font-extrabold tracking-[-0.02em] leading-[1.08] text-[clamp(26px,9.5vw,56px)] 720:text-[clamp(40px,6.4vw,80px)] text-fg-0">
          <span className="block">32개국 64경기를 한 화면에</span>
          <span className="block text-accent">
            축구 월드컵 일정·결과
          </span>
          <span className="block">&nbsp;&amp; 라이브 매치 안내</span>
        </h1>

        <p className="mb-9 text-fg-2 text-[clamp(15px,1.4vw,18px)] leading-[1.7] max-w-[720px] [&_br]:hidden 720:[&_br]:inline">
          조별 리그부터 결승까지 — 일정·대진·골 순위·하이라이트를 한 곳에 모아
          <br />
          월드컵의 모든 순간을 함께 안내하는 시스템입니다.
        </p>

        {showPrediction ? (
          <HeroPredictionPanel onAiPreset={onGeminiPreset} />
        ) : null}

        <div className="flex gap-3 flex-wrap mb-10 720:mb-14">
          <button
            type="button"
            className={`${BTN_BASE} ${BTN_PRIMARY}`}
            onClick={() => setTodayBroadcastOpen(true)}
            aria-haspopup="dialog"
            aria-expanded={todayBroadcastOpen}
          >
            오늘의 경기
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
            >
              <path
                d="M5 12h14M13 5l7 7-7 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            type="button"
            className={`${BTN_BASE} ${BTN_GHOST}`}
            onClick={openFullWorldCupSchedule}
          >
            전체 일정 보기
          </button>
          <Link
            href="/board"
            className={`${BTN_BASE} ${BTN_GHOST}`}
            title="자유 수다·건의·문의"
          >
            자유게시판·건의
          </Link>
        </div>

        <ul className="list-none m-0 p-0 flex flex-wrap gap-2" aria-label="주요 안내 카테고리">
          {CHIPS.map((c) => (
            <li
              key={c}
              className="p-[8px_14px] rounded-full bg-chip-bg border border-chip-border text-fg-1 text-[13px] font-medium whitespace-nowrap"
            >
              {c}
            </li>
          ))}
        </ul>
      </div>

      <TodayBroadcastModal
        open={todayBroadcastOpen}
        onClose={() => setTodayBroadcastOpen(false)}
      />
    </section>
  );
}
