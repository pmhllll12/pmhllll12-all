"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { koTeam } from "@/data/worldCup2026Ko";
import {
  getMatchesOnKstDay,
  formatMatchTimeKstOnly,
} from "@/data/worldCup2026Schedule";
import LoginModal from "./LoginModal";
import NavWeather from "./NavWeather";
import ThemeToggle from "./ThemeToggle";
import WorldCupScheduleModal from "./WorldCupScheduleModal";
import { WC_OPEN_FULL_SCHEDULE } from "@/wcScheduleOpen";

const MENU_OTHER = [
  { label: "조 편성", href: "#groups" },
  { label: "팀", href: "#teams" },
  { label: "통계", href: "#stats" },
];

const SESSION_EMAIL_KEY = "worldcup_session_email";

const NAV_BTN_BASE =
  "inline-flex items-center justify-center box-border rounded-full font-bold tracking-[0.02em] whitespace-nowrap transition flex-[0_1_auto] min-w-0 h-[34px] p-[7px_10px] text-[11px] 380:p-[0_12px] 380:text-xs 720:h-10 720:p-[0_16px] 720:text-sm";
const NAV_BTN_GHOST =
  "bg-transparent text-fg-0 border border-[rgba(255,255,255,0.22)] hover:border-[rgba(255,255,255,0.55)] hover:bg-[rgba(255,255,255,0.04)]";
const NAV_BTN_PRIMARY =
  "bg-accent text-[#04131a] border border-accent hover:bg-accent-strong hover:border-accent-strong hover:-translate-y-px";

type NavUiState = {
  authModal: null | "login" | "signup";
  sessionEmail: string | null;
  scheduleOpen: boolean;
};

function createInitialNavUi(sessionEmail: string | null = null): NavUiState {
  return {
    authModal: null,
    sessionEmail,
    scheduleOpen: false,
  };
}

export default function Nav() {
  const [ui, setUi] = useState<NavUiState>(() => createInitialNavUi());

  const patch = useCallback((p: Partial<NavUiState>) => {
    setUi((prev) => ({ ...prev, ...p }));
  }, []);

  useEffect(() => {
    try {
      const v = sessionStorage.getItem(SESSION_EMAIL_KEY);
      setUi((prev) => ({ ...prev, sessionEmail: v }));
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    const open = () => patch({ scheduleOpen: true });
    window.addEventListener(WC_OPEN_FULL_SCHEDULE, open);
    return () => window.removeEventListener(WC_OPEN_FULL_SCHEDULE, open);
  }, [patch]);

  const todayMatches = useMemo(() => getMatchesOnKstDay(), []);

  const scheduleHint = useMemo(() => {
    if (todayMatches.length === 0) {
      return "오늘(KST) 예정 경기 없음";
    }
    if (todayMatches.length === 1) {
      const m = todayMatches[0]!;
      return `${formatMatchTimeKstOnly(m.kickoffIso)} · ${koTeam(m.home)} 대 ${koTeam(m.away)}`;
    }
    const m0 = todayMatches[0]!;
    const more = todayMatches.length - 1;
    return `${formatMatchTimeKstOnly(m0.kickoffIso)} · ${koTeam(m0.home)} 대 ${koTeam(m0.away)} 외 ${more}경기`;
  }, [todayMatches]);

  const scheduleTitle = useMemo(() => {
    if (todayMatches.length === 0) {
      return "한국시각 기준 오늘 날짜에 예정된 월드컵 경기가 없습니다. 클릭하면 전체 일정을 볼 수 있습니다.";
    }
    return [
      `한국시각(KST) 오늘 ${todayMatches.length}경기`,
      ...todayMatches.map(
        (m) =>
          `${formatMatchTimeKstOnly(m.kickoffIso)} ${koTeam(m.home)} vs ${koTeam(m.away)}`,
      ),
      "",
      "클릭 시 전체 대회 일정",
    ].join("\n");
  }, [todayMatches]);

  const handleLogout = useCallback(() => {
    try {
      sessionStorage.removeItem(SESSION_EMAIL_KEY);
    } catch {
      /* ignore */
    }
    patch({ sessionEmail: null });
  }, [patch]);

  const handleLoginSuccess = useCallback(
    (email: string) => {
      try {
        sessionStorage.setItem(SESSION_EMAIL_KEY, email);
      } catch {
        /* ignore */
      }
      patch({ sessionEmail: email });
    },
    [patch],
  );

  return (
    <header className="sticky top-0 z-10 w-full backdrop-blur-md bg-[rgba(4,7,15,0.92)] border-b border-[rgba(148,163,184,0.1)]">
      <div className="max-w-[1200px] mx-auto w-full box-border grid grid-cols-[auto_minmax(0,1fr)] grid-rows-[auto_auto] items-center gap-[10px] p-[10px] 380:p-3 720:grid-cols-[auto_minmax(0,1fr)_auto] 720:grid-rows-none 720:gap-5 720:p-[16px_32px]">
        <Link
          href="/"
          className="[grid-column:1] [grid-row:1] 720:[grid-column:auto] 720:[grid-row:auto] inline-flex items-center gap-2 min-w-0"
          aria-label="WORLDCUP 홈"
        >
          <span className="font-extrabold text-fg-0 text-sm tracking-[0.12em] 520:text-lg 520:tracking-[0.18em]">
            WORLDCUP
          </span>
        </Link>

        <nav
          className="[grid-column:2] [grid-row:1] 720:[grid-column:auto] 720:[grid-row:auto] flex justify-end 720:justify-center items-center gap-0 min-w-0 w-full 720:w-auto"
          aria-label="주요 메뉴"
        >
          <div className="hidden 720:flex items-center shrink min-w-0 gap-[14px] overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            <button
              type="button"
              className="flex flex-col items-start shrink-0 gap-0.5 p-[6px_4px] m-0 border-none bg-none cursor-pointer text-left text-fg-1 rounded-lg transition hover:text-accent hover:bg-[rgba(0,229,255,0.06)]"
              onClick={() => patch({ scheduleOpen: true })}
              aria-haspopup="dialog"
              aria-expanded={ui.scheduleOpen}
            >
              <span className="text-[15px] font-semibold whitespace-nowrap">{"Today's 경기"}</span>
              <span className="hidden" title={scheduleTitle}>
                {scheduleHint}
              </span>
            </button>
            {MENU_OTHER.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="inline-flex items-center shrink-0 whitespace-nowrap text-fg-1 text-[15px] font-medium p-[8px_4px] transition hover:text-accent"
              >
                {item.label}
              </a>
            ))}
          </div>
          <NavWeather />
        </nav>

        <div className="[grid-column:1/-1] [grid-row:2] justify-self-stretch 720:justify-self-auto w-full 720:w-auto max-w-full 720:max-w-none 720:[grid-column:auto] 720:[grid-row:auto] inline-flex flex-wrap justify-start 720:justify-end items-center gap-2 720:gap-[10px] min-w-0">
          <button
            type="button"
            className="inline-flex items-center rounded-full font-bold cursor-pointer flex-[0_1_auto] min-w-0 border border-[rgba(0,229,255,0.45)] bg-[rgba(0,229,255,0.08)] text-accent transition hover:bg-[rgba(0,229,255,0.16)] p-[7px_10px] text-[11px] 380:p-[8px_12px] 380:text-xs 720:hidden"
            onClick={() => patch({ scheduleOpen: true })}
            aria-label="전체 경기일정 열기 (오늘 KST 경기 요약)"
          >
            {"Today's 경기"}
          </button>
          <Link
            href="/lesson"
            className="inline-flex items-center gap-[6px] 720:gap-2 h-[34px] 720:h-10 box-border p-[0_10px] 720:p-[0_14px] rounded-full border border-[rgba(0,229,255,0.35)] bg-[rgba(0,229,255,0.06)] flex-shrink-0 transition hover:bg-[rgba(0,229,255,0.12)] hover:border-[rgba(0,229,255,0.55)] hover:-translate-y-px"
            aria-label="Lesson 수업용 페이지로 이동"
          >
            <span
              className="text-sm 720:text-base leading-none [filter:drop-shadow(0_0_6px_rgba(0,229,255,0.35))]"
              aria-hidden
            >
              🚢
            </span>
            <span className="flex flex-col items-start gap-0 leading-[1.15] min-w-0">
              <span className="text-xs 720:text-[13px] font-extrabold tracking-[0.06em] text-fg-0">
                lesson
              </span>
              <span className="hidden 720:block text-[10px] font-semibold text-[rgba(148,163,184,0.95)] tracking-[0.02em]">
                생존 예측 · ML
              </span>
            </span>
          </Link>
          <ThemeToggle />
          <div className="inline-flex items-center flex-nowrap flex-shrink-0 gap-2">
            <Link
              href="/admin"
              className={`${NAV_BTN_BASE} ${NAV_BTN_GHOST}`}
              aria-label="관리자 화면으로 이동"
            >
              관리자
            </Link>
            {ui.sessionEmail ? (
              <>
                <span
                  className="max-w-[120px] overflow-hidden text-ellipsis whitespace-nowrap text-[13px] font-semibold text-[rgba(0,229,255,0.95)]"
                  title={ui.sessionEmail}
                >
                  {ui.sessionEmail.split("@")[0]}
                </span>
                <button
                  type="button"
                  className={`${NAV_BTN_BASE} ${NAV_BTN_GHOST}`}
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </>
            ) : (
              <div className="flex flex-wrap 720:inline-flex items-center gap-2">
                <button
                  type="button"
                  className={`${NAV_BTN_BASE} ${NAV_BTN_PRIMARY}`}
                  onClick={() => patch({ authModal: "login" })}
                >
                  로그인
                </button>
                <button
                  type="button"
                  className={`${NAV_BTN_BASE} ${NAV_BTN_GHOST}`}
                  onClick={() => patch({ authModal: "signup" })}
                >
                  회원가입
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <LoginModal
        open={ui.authModal !== null}
        variant={ui.authModal ?? "login"}
        onClose={() => patch({ authModal: null })}
        onSuccess={handleLoginSuccess}
      />
      <WorldCupScheduleModal
        open={ui.scheduleOpen}
        onClose={() => patch({ scheduleOpen: false })}
      />
    </header>
  );
}
