"use client";

import { useCallback, useEffect, useId, useMemo } from "react";
import { createPortal } from "react-dom";
import { koMatchMetaLine, koTeam } from "@/data/worldCup2026Ko";
import { formatMatchTimeKstOnly, getMatchesOnKstDay } from "@/data/worldCup2026Schedule";
import {
  WC_DAY_LIST,
  WC_MODAL,
  WC_MODAL_BACKDROP,
  WC_MODAL_BODY,
  WC_MODAL_CLOSE,
  WC_MODAL_FOOT,
  WC_MODAL_HEAD,
  WC_MODAL_SUB,
  WC_MODAL_TITLE,
  WC_ROW,
  WC_ROW_MATCH,
  WC_ROW_META,
  WC_ROW_TIME,
} from "./WorldCupScheduleModal";

type TodayBroadcastModalProps = {
  open: boolean;
  onClose: () => void;
};

const SECTION_TITLE = "mb-[10px] text-[13px] font-bold text-accent tracking-[0.02em]";

const BROADCAST_LINKS: { label: string; href: string; hint: string }[] = [
  {
    label: "FIFA+ · 공식",
    href: "https://www.fifa.com/fifaplus",
    hint: "FIFA 공식 플랫폼(하이라이트·정보)",
  },
  {
    label: "대회 공식 페이지",
    href: "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026",
    hint: "일정·뉴스·중계 안내",
  },
  {
    label: "FIFA 월드컵 YouTube",
    href: "https://www.youtube.com/@FIFAWorldCup",
    hint: "공식 채널 하이라이트·라이브",
  },
  {
    label: "KBS 스포츠",
    href: "https://sports.kbs.co.kr",
    hint: "국내 TV·디지털 중계 안내(방송사 페이지)",
  },
  {
    label: "JTBC",
    href: "https://www.jtbc.co.kr",
    hint: "국내 TV·디지털 중계 안내(방송사 페이지)",
  },
];

export default function TodayBroadcastModal({
  open,
  onClose,
}: TodayBroadcastModalProps) {
  const titleId = useId();

  const todayMatches = useMemo(
    () => (open ? getMatchesOnKstDay() : []),
    [open],
  );

  const handleKey = useCallback(
    (ev: KeyboardEvent) => {
      if (ev.key === "Escape") onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (!open) return;
    window.addEventListener("keydown", handleKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handleKey);
      document.body.style.overflow = prev;
    };
  }, [open, handleKey]);

  const handleBackdrop = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (e.target === e.currentTarget) onClose();
    },
    [onClose],
  );

  if (!open) return null;

  return createPortal(
    <div className={WC_MODAL_BACKDROP} role="presentation" onMouseDown={handleBackdrop}>
      <div
        className={WC_MODAL}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <header className={WC_MODAL_HEAD}>
          <div>
            <h2 id={titleId} className={WC_MODAL_TITLE}>
              오늘의 경기 · 중계 안내
            </h2>
            <p className={WC_MODAL_SUB}>
              경기 시각은 <strong>한국 표준시(KST)</strong> 기준입니다. 중계는
              방송사·FIFA 정책에 따라 달라질 수 있습니다.
            </p>
          </div>
          <button type="button" className={WC_MODAL_CLOSE} onClick={onClose} aria-label="닫기">
            ×
          </button>
        </header>

        <div className={WC_MODAL_BODY}>
          <h3 className={SECTION_TITLE}>오늘 예정 경기</h3>
          {todayMatches.length === 0 ? (
            <p className="mb-4 text-sm leading-[1.55] text-[rgba(226,232,240,0.82)]">
              한국시각 기준 오늘 날짜에 잡힌 월드컵 2026 경기가 없습니다. 아래
              링크에서 공식 중계·하이라이트를 확인해 보세요.
            </p>
          ) : (
            <ul className={WC_DAY_LIST}>
              {todayMatches.map((m) => (
                <li key={m.id} className={WC_ROW}>
                  <span className={WC_ROW_TIME}>{formatMatchTimeKstOnly(m.kickoffIso)}</span>
                  <span className={WC_ROW_MATCH}>
                    {koTeam(m.home)} 대 {koTeam(m.away)}
                  </span>
                  <span className={WC_ROW_META}>{koMatchMetaLine(m)}</span>
                </li>
              ))}
            </ul>
          )}

          <h3 className={`${SECTION_TITLE} mt-2`}>중계·라이브 보러가기</h3>
          <ul className="m-0 p-0 list-none flex flex-col gap-[10px]" aria-label="중계 관련 외부 링크">
            {BROADCAST_LINKS.map((item) => (
              <li key={item.href}>
                <a
                  className="block p-[12px_14px] rounded-[10px] border border-[rgba(0,229,255,0.22)] bg-[rgba(0,229,255,0.06)] text-fg-0 font-bold text-sm no-underline transition hover:border-[rgba(0,229,255,0.45)] hover:bg-[rgba(0,229,255,0.1)]"
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {item.label}
                  <span className="block mt-1 text-xs font-medium text-[rgba(148,163,184,0.95)]">
                    {item.hint}
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </div>

        <footer className={WC_MODAL_FOOT}>
          국내 TV·온라인 중계는{" "}
          <strong>KBS·JTBC</strong> 등 방송사 공지를 확인하세요. 일정 데이터는
          openfootball 기준이며 변경될 수 있습니다.
        </footer>
      </div>
    </div>,
    document.body,
  );
}
