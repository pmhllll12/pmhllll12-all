"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import "./lesson-layout.css";

const TOP_CATS = [
  "ALL",
  "RAG SYSTEM",
  "ARCHITECTURE",
  "AGENT",
  "BACKEND",
  "MOBILE",
  "DEVOPS",
  "NLP",
] as const;

const MOBILE_NAV_QUERY = "(max-width: 800px)";

function sublinkClass(active: boolean) {
  return active
    ? "block px-3 py-[10px] rounded-lg text-sm font-bold text-[#0369a1] bg-[rgba(14,165,233,0.1)]"
    : "block px-3 py-[10px] rounded-lg text-sm font-semibold text-[#475569] transition hover:text-[#0f172a] hover:bg-[rgba(15,23,42,0.04)]";
}

export default function LessonLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobileNav, setIsMobileNav] = useState(false);

  const closeMenu = useCallback(() => setMenuOpen(false), []);
  const toggleMenu = useCallback(() => setMenuOpen((o) => !o), []);

  useEffect(() => {
    closeMenu();
  }, [pathname, closeMenu]);

  useEffect(() => {
    if (!menuOpen) return;
    const mq = window.matchMedia(MOBILE_NAV_QUERY);
    const sync = () => {
      if (!mq.matches) setMenuOpen(false);
    };
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, [menuOpen]);

  useEffect(() => {
    const mq = window.matchMedia(MOBILE_NAV_QUERY);
    const sync = () => setIsMobileNav(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [menuOpen]);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeMenu();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen, closeMenu]);

  return (
    <div
      className={
        menuOpen
          ? "lesson-shell lesson-shell--nav-open flex-1 w-full bg-white text-[#0f172a]"
          : "lesson-shell flex-1 w-full bg-white text-[#0f172a]"
      }
    >
      <div className="lesson-topbar border-b border-[#e2e8f0] bg-white">
        <div className="max-w-[1200px] mx-auto px-[clamp(12px,3vw,32px)] py-[10px] flex items-center gap-3">
          <button
            type="button"
            className="lesson-menu-btn w-11 h-11 p-0 border border-[#e2e8f0] rounded-[10px] bg-[#f8fafc] cursor-pointer items-center justify-center flex-col gap-[5px] shrink-0 transition hover:bg-[#f1f5f9] hover:border-[#cbd5e1]"
            aria-label={menuOpen ? "수업 메뉴 닫기" : "수업 메뉴 열기"}
            aria-expanded={menuOpen}
            aria-controls="lesson-sidebar"
            onClick={toggleMenu}
          >
            <span
              className="lesson-menu-btn__bar block w-[18px] h-[2px] rounded-[1px] bg-[#0f172a]"
              aria-hidden
            />
            <span
              className="lesson-menu-btn__bar block w-[18px] h-[2px] rounded-[1px] bg-[#0f172a]"
              aria-hidden
            />
            <span
              className="lesson-menu-btn__bar block w-[18px] h-[2px] rounded-[1px] bg-[#0f172a]"
              aria-hidden
            />
          </button>
          <nav
            className="lesson-topbar__nav flex-1 min-w-0 flex flex-wrap items-center justify-center gap-[8px_20px]"
            aria-label="수업·카테고리"
          >
            {TOP_CATS.map((label) => (
              <span
                key={label}
                className="text-[11px] font-bold tracking-[0.12em] uppercase text-[#64748b] py-[6px] px-[2px] cursor-default whitespace-nowrap opacity-55"
                title="준비 중"
              >
                {label}
              </span>
            ))}
            <Link
              href="/lesson"
              className={
                pathname.startsWith("/lesson")
                  ? "text-[11px] font-bold tracking-[0.12em] uppercase py-[6px] px-[2px] whitespace-nowrap text-[#0f172a] shadow-[inset_0_-2px_0_#0f172a] cursor-pointer hover:text-[#0f172a]"
                  : "text-[11px] font-bold tracking-[0.12em] uppercase py-[6px] px-[2px] whitespace-nowrap text-[#64748b] opacity-55"
              }
            >
              수업용
            </Link>
          </nav>
        </div>
      </div>

      <button
        type="button"
        className="lesson-drawer-backdrop bg-[rgba(15,23,42,0.45)] cursor-pointer"
        aria-label="메뉴 닫기"
        tabIndex={menuOpen ? 0 : -1}
        onClick={closeMenu}
      />

      <div className="grid grid-cols-1 800:grid-cols-[minmax(200px,260px)_minmax(0,1fr)] w-full max-w-[1200px] mx-auto items-start box-border px-4 800:px-[clamp(12px,3vw,32px)] py-4 800:py-7 800:pb-14">
        <aside
          id="lesson-sidebar"
          className="lesson-sidebar px-[18px] py-5 rounded-2xl border border-[#e2e8f0] bg-[#f8fafc] shadow-[0_4px_20px_rgba(15,23,42,0.06)] overflow-y-auto 800:shadow-[6px_0_32px_rgba(15,23,42,0.18)] 800:border-r 800:border-r-[#e2e8f0]"
          aria-label="수업용 메뉴"
        >
          <div className="flex items-start justify-between gap-3 800:block">
            <p className="mb-4 text-xs font-extrabold tracking-[0.12em] uppercase text-[#64748b]">
              수업용
            </p>
            <button
              type="button"
              className="lesson-sidebar__close hidden -mt-1 px-[10px] py-[6px] text-xs font-bold text-[#64748b] bg-white border border-[#e2e8f0] rounded-lg cursor-pointer transition hover:text-[#0f172a] hover:border-[#cbd5e1] inline-block"
              aria-label="메뉴 닫기"
              onClick={closeMenu}
            >
              닫기
            </button>
          </div>
          <details className="lesson-sidebar__details m-0 border-0" open={!isMobileNav}>
            <summary className="lesson-sidebar__summary cursor-pointer text-base font-extrabold text-[#0f172a] py-[10px_0_8px] flex items-center justify-between select-none">
              타이타닉
            </summary>
            <div className="flex flex-col gap-1 py-1 pb-2 pl-3 ml-1.5 border-l-2 border-[#e2e8f0]">
              <Link
                href="/lesson"
                className={sublinkClass(pathname === "/lesson")}
                onClick={closeMenu}
              >
                과정 개요
              </Link>
              <Link
                href="/lesson/titanic"
                className={sublinkClass(pathname === "/lesson/titanic")}
                onClick={closeMenu}
              >
                1. 데이터 수집 및 실습
              </Link>
              <Link
                href="/lesson/titanic/passengers"
                className={sublinkClass(pathname === "/lesson/titanic/passengers")}
                onClick={closeMenu}
              >
                2. 승객 목록
              </Link>
              <Link
                href="/lesson/titanic/smith"
                className={sublinkClass(pathname === "/lesson/titanic/smith")}
                onClick={closeMenu}
              >
                3. 스미스 선장과 대화하기
              </Link>
            </div>
          </details>
          <details className="lesson-sidebar__details m-0 border-0">
            <summary className="lesson-sidebar__summary cursor-pointer text-base font-extrabold text-[#0f172a] py-[10px_0_8px] flex items-center justify-between select-none">
              vision
            </summary>
            <div className="flex flex-col gap-1 py-1 pb-2 pl-3 ml-1.5 border-l-2 border-[#e2e8f0]">
              <Link
                href="/lesson/vision"
                className={sublinkClass(pathname === "/lesson/vision")}
                onClick={closeMenu}
              >
                과정 개요
              </Link>
              <Link
                href="/lesson/vision/detect"
                className={sublinkClass(pathname === "/lesson/vision/detect")}
                onClick={closeMenu}
              >
                객체 탐지
              </Link>
            </div>
          </details>
          <details className="lesson-sidebar__details m-0 border-0">
            <summary className="lesson-sidebar__summary cursor-pointer text-base font-extrabold text-[#0f172a] py-[10px_0_8px] flex items-center justify-between select-none">
              RAG
            </summary>
            <div className="flex flex-col gap-1 py-1 pb-2 pl-3 ml-1.5 border-l-2 border-[#e2e8f0]">
              <Link
                href="/rag-system/moneyball"
                className={sublinkClass(pathname === "/rag-system/moneyball")}
                onClick={closeMenu}
              >
                축구마스터
              </Link>
            </div>
          </details>
        </aside>
        <div className="min-w-0 pt-1 pl-0 800:pl-[clamp(12px,2vw,28px)]">
          {children}
        </div>
      </div>
    </div>
  );
}
