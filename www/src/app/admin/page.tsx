"use client";

import { useState } from "react";
import EmailPanel from "./EmailPanel";
import AddressBookPanel from "./AddressBookPanel";
import TelegramPanel from "./TelegramPanel";

type NavItem = { key: string; label: string; icon: string; parent?: string };

const NAV_ITEMS: NavItem[] = [
  { key: "dashboard", label: "DASHBOARD", icon: "🏠" },
  { key: "chart", label: "CHART", icon: "📊" },
  { key: "apps", label: "APPS", icon: "⭐" },
  { key: "form", label: "FORM", icon: "📝" },
  { key: "email", label: "EMAIL", icon: "✉️" },
  { key: "mail", label: "메일관리", icon: "📬" },
  { key: "addressbook", label: "주소록", icon: "📒", parent: "mail" },
  { key: "telegram", label: "텔레그램", icon: "✈️", parent: "mail" },
  { key: "setting", label: "SETTING", icon: "⚙️" },
  { key: "lorem", label: "LOREM", icon: "📷" },
  { key: "contrary", label: "CONTRARY", icon: "📁" },
  { key: "belief", label: "BELIEF", icon: "📦" },
];

const TABS = ["LOREM IPSUM", "CONTRARY", "POPULAR", "BELIEF", "AENEAN"];

const ROW_ITEMS = [
  { percent: 20, label: "LOREM IPSUM" },
  { percent: 60, label: "LOREM IPSUM" },
  { percent: 80, label: "LOREM IPSUM" },
  { percent: 20, label: "LOREM IPSUM" },
];

const BAR_DATA = [
  { year: "2013", value: 35 },
  { year: "2014", value: 55 },
  { year: "2015", value: 40 },
  { year: "2016", value: 70 },
  { year: "2017", value: 50 },
  { year: "2018", value: 85 },
];

const MINI_RINGS = [60, 70, 60];

const THIN_BARS = [
  { label: "LOREM IPSUM", percent: 80 },
  { label: "LOREM IPSUM", percent: 55 },
  { label: "LOREM IPSUM", percent: 40 },
];

const CARD =
  "flex flex-col gap-3 min-w-0 bg-bg-1 border border-border rounded-2xl p-4 shadow-[0_8px_24px_rgba(0,0,0,0.35)]";
const CARD_HEAD = "flex items-start justify-between gap-2";
const CARD_TITLE = "m-0 text-[11px] font-bold tracking-[0.06em] uppercase text-fg-2";
const CARD_HINT = "mt-1 text-[11px] leading-[1.4] text-fg-2";
const CARD_MORE =
  "flex-none w-6 h-6 rounded-full border border-border bg-chip-bg text-fg-2 text-[13px] leading-none cursor-pointer";

function ProgressRing({
  percent,
  size = 64,
  stroke = 7,
  gradientId,
  fontSize,
}: {
  percent: number;
  size?: number;
  stroke?: number;
  gradientId: string;
  fontSize?: number;
}) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - percent / 100);
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={`${percent}%`}
    >
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ec4899" />
          <stop offset="55%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#38bdf8" />
        </linearGradient>
      </defs>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="rgba(148, 163, 184, 0.18)"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="53%"
        textAnchor="middle"
        dominantBaseline="middle"
        className="font-extrabold fill-fg-0"
        fontSize={fontSize ?? Math.round(size / 4.5)}
      >
        {percent}%
      </text>
    </svg>
  );
}

export default function Admin() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeNav, setActiveNav] = useState("dashboard");
  const [activeTab, setActiveTab] = useState(TABS[0]);

  return (
    <div className="relative flex flex-col min-h-screen w-full bg-bg-0 text-fg-0 text-sm 900:flex-row">
      {sidebarOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 border-0 p-0 bg-[rgba(15,17,26,0.5)] 900:hidden"
          aria-label="메뉴 닫기"
          onClick={() => setSidebarOpen(false)}
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[min(78vw,280px)] h-screen flex flex-col gap-2 p-[20px_14px] bg-bg-1 border-r-4 [border-image:linear-gradient(180deg,#38bdf8,#ec4899)_1] transition-transform duration-[250ms] overflow-y-auto 900:sticky 900:top-0 900:flex-[0_0_230px] 900:w-[230px] 900:h-screen 900:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-[10px] p-[6px_10px_18px] text-fg-0">
          <span className="text-[22px]" aria-hidden>
            🛡️
          </span>
          <span className="flex flex-col leading-[1.25]">
            <strong>LOREM IPSUM</strong>
            <small className="text-[10px] tracking-[0.08em] text-fg-2">LOREM IPSUM</small>
          </span>
        </div>
        <nav className="flex flex-col gap-0.5" aria-label="관리자 메뉴">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`flex items-center gap-3 w-full border-0 bg-none rounded-[10px] text-xs tracking-[0.04em] text-left cursor-pointer ${
                item.parent ? "p-[9px_10px_9px_28px]" : "p-[11px_10px]"
              } ${
                activeNav === item.key
                  ? "bg-accent-soft text-accent"
                  : "text-fg-2"
              }`}
              onClick={() => {
                setActiveNav(item.key);
                setSidebarOpen(false);
              }}
            >
              <span className="text-base w-5 text-center" aria-hidden>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-start gap-3 p-4 text-white bg-[linear-gradient(120deg,#6d28d9_0%,#9333ea_35%,#db2777_75%,#ec4899_100%)] 900:p-[22px_28px]">
          <button
            type="button"
            className="flex-none border-0 bg-[rgba(255,255,255,0.18)] text-white w-[34px] h-[34px] rounded-[9px] text-base cursor-pointer 900:hidden"
            aria-label="메뉴 열기"
            aria-expanded={sidebarOpen}
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>
          <div className="flex-1 min-w-0">
            <p className="m-0 mb-0.5 text-[11px] font-bold tracking-[0.08em]">
              DASHBOARD USER ADMIN PANEL
            </p>
            <p className="m-0 text-[11px] opacity-85 overflow-hidden [display:-webkit-box] [-webkit-line-clamp:2] [-webkit-box-orient:vertical]">
              Contrary to popular belief, Lorem Ipsum is not.
            </p>
          </div>
          <div className="flex-none flex items-center gap-2">
            <span className="hidden 480:inline text-xs font-semibold">LOREM IPSUM</span>
            <span
              className="w-[30px] h-[30px] rounded-full bg-[rgba(255,255,255,0.25)] flex items-center justify-center text-[15px]"
              aria-hidden
            >
              🙂
            </span>
          </div>
        </header>

        <nav
          className="flex gap-[18px] p-[10px_16px] bg-bg-1 border-b border-border overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden 900:p-[12px_28px]"
          aria-label="대시보드 탭"
        >
          {TABS.map((tab) => (
            <button
              key={tab}
              type="button"
              className={`relative flex-none border-0 bg-none p-[4px_0_11px] text-[11px] tracking-[0.04em] whitespace-nowrap cursor-pointer ${
                activeTab === tab
                  ? "text-fg-0 font-bold after:content-[''] after:absolute after:left-0 after:right-0 after:bottom-0 after:h-0.5 after:bg-[linear-gradient(90deg,#6d28d9,#ec4899)]"
                  : "text-fg-2"
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </nav>

        {activeNav === "mail" ? (
          <main className="flex-1 p-[14px] 900:p-[22px_28px_32px]">
            <EmailPanel />
          </main>
        ) : null}
        {activeNav === "addressbook" ? (
          <main className="flex-1 p-[14px] 900:p-[22px_28px_32px]">
            <AddressBookPanel />
          </main>
        ) : null}
        {activeNav === "telegram" ? (
          <main className="flex-1 p-[14px] 900:p-[22px_28px_32px]">
            <TelegramPanel />
          </main>
        ) : null}
        <main className={`flex-1 grid grid-cols-1 gap-[14px] p-[14px] 900:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)] 900:gap-5 900:p-[22px_28px_32px] ${["mail", "addressbook", "telegram"].includes(activeNav) ? "hidden" : ""}`}>
          <section className={CARD}>
            <header className={CARD_HEAD}>
              <div>
                <p className={CARD_TITLE}>LOREM IPSUM</p>
                <p className={CARD_HINT}>
                  Currency to popular belief, Lorem Ipsum is not.
                </p>
              </div>
              <button type="button" className={CARD_MORE} aria-label="더 보기">
                +
              </button>
            </header>
            <p className="m-0 text-2xl font-extrabold">$ 4,837.26</p>
            <svg
              className="block w-full h-[90px]"
              viewBox="0 0 300 110"
              preserveAspectRatio="none"
              aria-hidden
            >
              <defs>
                <linearGradient id="admin-area-line" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#38bdf8" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
                <linearGradient id="admin-area-fill" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#ec4899" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#ec4899" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d="M0 95 L300 95 L300 25 L275 10 L250 35 L225 20 L200 45 L175 30 L150 50 L125 40 L100 65 L75 55 L50 75 L25 60 L0 70 Z"
                fill="url(#admin-area-fill)"
              />
              <path
                d="M0 70 L25 60 L50 75 L75 55 L100 65 L125 40 L150 50 L175 30 L200 45 L225 20 L250 35 L275 10 L300 25"
                fill="none"
                stroke="url(#admin-area-line)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </section>

          <section className={CARD}>
            <header className={CARD_HEAD}>
              <p className={CARD_TITLE}>LOREM IPSUM</p>
              <button type="button" className={CARD_MORE} aria-label="더 보기">
                +
              </button>
            </header>
            <div className="flex items-center justify-center p-[6px_0]">
              <ProgressRing percent={75} size={120} stroke={10} gradientId="ring-main" />
            </div>
          </section>

          <section className={CARD}>
            <header className={CARD_HEAD}>
              <div>
                <p className={CARD_TITLE}>LOREM IPSUM</p>
                <p className={CARD_HINT}>
                  Contrary to popular belief, Lorem Ipsum is not simply random text.
                </p>
              </div>
            </header>
            <ul className="m-0 p-0 list-none flex flex-col gap-[10px]">
              {ROW_ITEMS.map((row, i) => (
                <li className="flex items-center gap-[10px]" key={i}>
                  <ProgressRing
                    percent={row.percent}
                    size={56}
                    stroke={6}
                    gradientId={`ring-row-${i}`}
                  />
                  <span className="flex-1 min-w-0 bg-chip-bg rounded-[10px] p-[8px_10px] text-[11px] font-bold text-fg-0 whitespace-nowrap overflow-hidden text-ellipsis">
                    {row.label}
                  </span>
                  <span
                    className="flex-none w-2 h-2 rounded-full bg-[linear-gradient(135deg,#ec4899,#38bdf8)]"
                    aria-hidden
                  />
                  <span className="flex-none max-w-16 text-[10px] text-fg-2 whitespace-nowrap overflow-hidden text-ellipsis">
                    {row.label}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className={CARD}>
            <header className={CARD_HEAD}>
              <p className={CARD_TITLE}>LOREM IPSUM</p>
              <button type="button" className={CARD_MORE} aria-label="더 보기">
                +
              </button>
            </header>
            <div className="flex items-end gap-[6px] h-[120px] pt-2">
              {BAR_DATA.map((bar) => (
                <div
                  className="flex-1 h-full flex flex-col items-center justify-end gap-[6px]"
                  key={bar.year}
                >
                  <div
                    className="w-[60%] max-w-4 rounded-[6px_6px_2px_2px] bg-[linear-gradient(180deg,#ec4899,#38bdf8)]"
                    style={{ height: `${bar.value}%` }}
                  />
                  <span className="text-[9px] text-fg-2">{bar.year}</span>
                </div>
              ))}
            </div>
          </section>

          <section className={CARD}>
            <header className={CARD_HEAD}>
              <p className={CARD_TITLE}>LOREM IPSUM</p>
            </header>
            <p className="m-0 text-xs leading-[1.6] text-fg-2">
              Contrary to popular belief, Lorem Ipsum is not simply random text. It
              has roots in a piece of classical Latin literature.
            </p>
            <ul className="m-0 p-0 list-none flex flex-col gap-[10px]">
              {THIN_BARS.map((bar, i) => (
                <li key={i} className="flex items-center gap-[10px]">
                  <span className="flex-none w-[88px] text-[10px] text-fg-2 whitespace-nowrap overflow-hidden text-ellipsis">
                    {bar.label}
                  </span>
                  <span className="flex-1 h-[6px] rounded-full bg-chip-bg overflow-hidden">
                    <span
                      className="block h-full rounded-full bg-[linear-gradient(90deg,#6d28d9,#ec4899)]"
                      style={{ width: `${bar.percent}%` }}
                    />
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className={`${CARD} flex-row items-center justify-around p-[22px_12px]`}>
            {MINI_RINGS.map((percent, i) => (
              <ProgressRing
                key={i}
                percent={percent}
                size={64}
                stroke={7}
                gradientId={`ring-mini-${i}`}
              />
            ))}
          </section>
        </main>
      </div>
    </div>
  );
}
