"use client";

import { useCallback, useEffect, useId, useMemo } from "react";
import { createPortal } from "react-dom";
import { koMatchMetaLine, koTeam } from "@/data/worldCup2026Ko";
import { WC2026_MATCHES, type WcMatch } from "@/data/worldCup2026Schedule";

type WorldCupScheduleModalProps = {
  open: boolean;
  onClose: () => void;
};

export const WC_MODAL_BACKDROP =
  "fixed inset-0 z-[100] flex items-start justify-center p-[48px_16px_32px] bg-[rgba(2,6,12,0.78)] backdrop-blur-md";
export const WC_MODAL =
  "w-[min(720px,100%)] max-h-[min(88vh,900px)] flex flex-col rounded-2xl border border-[rgba(0,229,255,0.28)] bg-[linear-gradient(165deg,rgba(12,18,28,0.98),rgba(6,10,18,0.99))] shadow-[0_24px_80px_rgba(0,0,0,0.55)]";
export const WC_MODAL_HEAD =
  "flex items-start justify-between gap-4 p-[20px_22px_12px] border-b border-[rgba(148,163,184,0.12)]";
export const WC_MODAL_TITLE = "m-0 text-xl font-extrabold tracking-[0.04em] text-fg-0";
export const WC_MODAL_SUB = "mt-[6px] mb-0 text-[13px] text-[rgba(226,232,240,0.72)]";
export const WC_MODAL_CLOSE =
  "flex-shrink-0 w-10 h-10 border-none rounded-[10px] bg-[rgba(255,255,255,0.06)] text-fg-0 text-2xl leading-none cursor-pointer transition hover:bg-[rgba(0,229,255,0.12)] hover:text-accent";
export const WC_MODAL_BODY = "flex-1 overflow-auto p-[12px_8px_16px_16px]";
export const WC_DAY = "mb-5";
export const WC_DAY_TITLE = "mb-2 text-sm font-bold text-accent tracking-[0.02em]";
export const WC_DAY_LIST = "m-0 p-0 list-none";
export const WC_ROW =
  "grid grid-cols-[72px_1fr] grid-rows-[auto_auto] gap-x-3 gap-y-0.5 p-[10px_8px] rounded-[10px] border-b border-[rgba(148,163,184,0.08)]";
export const WC_ROW_TIME =
  "[grid-row:1/span_2] self-center text-[13px] font-bold [font-variant-numeric:tabular-nums] text-[rgba(241,245,249,0.92)]";
export const WC_ROW_MATCH = "text-sm font-semibold text-fg-0";
export const WC_ROW_META = "text-xs text-[rgba(148,163,184,0.95)]";
export const WC_MODAL_FOOT =
  "p-[12px_18px_16px] text-[11px] leading-[1.5] text-[rgba(148,163,184,0.85)] border-t border-[rgba(148,163,184,0.1)] [&_a]:text-accent";

function groupByKstDate(matches: WcMatch[]): Map<string, WcMatch[]> {
  const ymdFmt = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const wdFmt = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    weekday: "short",
  });
  const map = new Map<string, WcMatch[]>();
  for (const m of matches) {
    const d = new Date(m.kickoffIso);
    const key = `${ymdFmt.format(d)}|${wdFmt.format(d)}`;
    const list = map.get(key);
    if (list) list.push(m);
    else map.set(key, [m]);
  }
  return map;
}

export default function WorldCupScheduleModal({
  open,
  onClose,
}: WorldCupScheduleModalProps) {
  const titleId = useId();

  const grouped = useMemo(() => groupByKstDate(WC2026_MATCHES), []);

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
              FIFA 월드컵 2026 경기일정
            </h2>
            <p className={WC_MODAL_SUB}>
              표시 시각은 <strong>한국 표준시(한국 시각)</strong> 기준입니다.
            </p>
          </div>
          <button type="button" className={WC_MODAL_CLOSE} onClick={onClose} aria-label="닫기">
            ×
          </button>
        </header>

        <div className={WC_MODAL_BODY}>
          {Array.from(grouped.entries()).map(([dateKey, rows]) => {
            const [ymd, weekday] = dateKey.split("|");
            return (
              <section key={dateKey} className={WC_DAY}>
                <h3 className={WC_DAY_TITLE}>
                  {ymd} ({weekday}) (한국 시각)
                </h3>
                <ul className={WC_DAY_LIST}>
                  {rows.map((m) => (
                    <li key={m.id} className={WC_ROW}>
                      <span className={WC_ROW_TIME}>
                        {new Intl.DateTimeFormat("ko-KR", {
                          timeZone: "Asia/Seoul",
                          hour: "2-digit",
                          minute: "2-digit",
                          hour12: false,
                        }).format(new Date(m.kickoffIso))}
                      </span>
                      <span className={WC_ROW_MATCH}>
                        {koTeam(m.home)} 대 {koTeam(m.away)}
                      </span>
                      <span className={WC_ROW_META}>{koMatchMetaLine(m)}</span>
                    </li>
                  ))}
                </ul>
              </section>
            );
          })}
        </div>

        <footer className={WC_MODAL_FOOT}>
          데이터 출처: openfootball/world-cup.json (2026). 변경 시 최종 일정은{" "}
          <a
            href="https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026"
            target="_blank"
            rel="noreferrer"
          >
            FIFA 공식
          </a>
          을 확인하세요.
        </footer>
      </div>
    </div>,
    document.body,
  );
}
