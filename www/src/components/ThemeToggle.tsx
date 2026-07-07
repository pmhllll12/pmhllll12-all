"use client";

import { useTheme } from "@/useTheme";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isLight = theme === "light";

  return (
    <button
      type="button"
      className="relative inline-flex items-center flex-none w-12 h-[26px] 720:w-14 720:h-[30px] p-[0_7px] rounded-full border border-border bg-chip-bg cursor-pointer transition hover:border-chip-border hover:bg-[rgba(148,163,184,0.14)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
      onClick={toggleTheme}
      role="switch"
      aria-checked={isLight}
      aria-label={isLight ? "다크 모드로 전환" : "라이트 모드로 전환"}
      title={isLight ? "다크 모드로 전환" : "라이트 모드로 전환"}
    >
      <span className="w-4 text-[13px] leading-none text-center mr-auto" aria-hidden="true">
        🌙
      </span>
      <span className="w-4 text-[13px] leading-none text-center ml-auto" aria-hidden="true">
        ☀️
      </span>
      <span
        className={`absolute top-[3px] w-[18px] h-[18px] 720:w-[22px] 720:h-[22px] rounded-full bg-accent shadow-[0_0_8px_var(--color-accent-soft)] transition-all duration-[250ms] ${
          isLight ? "left-[27px] 720:left-[31px] bg-accent-strong" : "left-[3px]"
        }`}
        aria-hidden="true"
      />
    </button>
  );
}
