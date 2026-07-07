"use client";

import { useEffect, useState } from "react";

type WeatherApi = {
  city: string;
  temp: number;
  description: string;
  icon: string;
};

type WeatherState =
  | { status: "loading" }
  | { status: "ok"; temp: number; label: string; icon: string }
  | { status: "error"; message?: string };

const REFRESH_MS = 15 * 60 * 1000;
const MINT = "#00e5ff";

function getWeatherUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  if (typeof base === "string" && base.trim()) {
    return `${base.replace(/\/$/, "")}/weather`;
  }
  return "/weather";
}

function pickIconKind(icon: string, description: string): string {
  if (icon.startsWith("01")) return "clear";
  if (icon.startsWith("02")) return "partly";
  if (icon.startsWith("03") || icon.startsWith("04")) return "cloud";
  if (icon.startsWith("09") || icon.startsWith("10")) return "rain";
  if (icon.startsWith("11")) return "storm";
  if (icon.startsWith("13")) return "snow";
  if (icon.startsWith("50")) return "fog";
  const d = description.toLowerCase();
  if (d.includes("맑")) return "clear";
  if (d.includes("비")) return "rain";
  if (d.includes("눈")) return "snow";
  return "clear";
}

function WeatherIcon({ kind }: { kind: string }) {
  const props = {
    className: "flex-shrink-0 [filter:drop-shadow(0_0_6px_rgba(0,229,255,0.45))]",
    width: 22,
    height: 22,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: MINT,
    strokeWidth: 2,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };

  if (kind === "clear" || kind === "partly") {
    return (
      <svg {...props}>
        <circle cx="12" cy="12" r="4.5" fill={MINT} stroke="none" />
        <path d="M12 2v2.5M12 19.5V22M4.5 4.5l1.8 1.8M17.7 17.7l1.8 1.8M2 12h2.5M19.5 12H22M4.5 19.5l1.8-1.8M17.7 6.3l1.8-1.8" />
        {kind === "partly" ? (
          <path
            d="M18 16a3.5 3.5 0 0 0-5-3.2A3 3 0 1 0 7 16h11"
            opacity="0.85"
          />
        ) : null}
      </svg>
    );
  }

  if (kind === "rain") {
    return (
      <svg {...props}>
        <path d="M18 14a4 4 0 0 0-7-2.5A4 4 0 1 0 6 18h12a3 3 0 0 0 0-6h-.5" />
        <path d="M8 20v2M12 20v2M16 20v2" />
      </svg>
    );
  }

  if (kind === "cloud" || kind === "fog") {
    return (
      <svg {...props}>
        <path d="M18 14a4 4 0 0 0-7-2.5A4 4 0 1 0 6 18h12a3 3 0 0 0 0-6h-.5" />
      </svg>
    );
  }

  return (
    <svg {...props}>
      <circle cx="12" cy="12" r="4.5" fill={MINT} stroke="none" />
      <path d="M12 2v2.5M12 19.5V22M4.5 4.5l1.8 1.8M17.7 17.7l1.8 1.8M2 12h2.5M19.5 12H22" />
    </svg>
  );
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => window.setTimeout(r, ms));
}

/** 백엔드 재시작 직후 등 일시적 실패 시 온도가 -- 로만 보이는 것을 줄임 */
async function fetchWithRetry(
  url: string,
  attempts = 3,
  delayMs = 400,
): Promise<Response> {
  let lastErr: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return res;
      if (res.status >= 500 && i < attempts - 1) {
        await sleep(delayMs);
        continue;
      }
      return res;
    } catch (e) {
      lastErr = e;
      if (i < attempts - 1) await sleep(delayMs);
    }
  }
  throw lastErr instanceof Error ? lastErr : new Error(String(lastErr));
}

async function fetchSeoulWeather(): Promise<WeatherState> {
  const res = await fetchWithRetry(getWeatherUrl());
  const raw = await res.text();
  if (!res.ok) {
    let message = "날씨를 불러올 수 없습니다.";
    try {
      const j = JSON.parse(raw) as { detail?: string };
      if (j.detail) message = j.detail;
    } catch {
      /* ignore */
    }
    return { status: "error", message };
  }

  const data = JSON.parse(raw) as WeatherApi;
  const icon = pickIconKind(data.icon, data.description);
  return {
    status: "ok",
    temp: data.temp,
    label: data.description,
    icon,
  };
}

export default function NavWeather() {
  const [weather, setWeather] = useState<WeatherState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const next = await fetchSeoulWeather();
        if (!cancelled) setWeather(next);
      } catch {
        if (!cancelled) {
          setWeather({
            status: "error",
            message:
              "백엔드(backend\\apps 에서 python main.py)가 켜져 있는지 확인하세요.",
          });
        }
      }
    };

    void load();
    const id = window.setInterval(() => void load(), REFRESH_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const iconKind =
    weather.status === "ok" ? weather.icon : "clear";
  const tempText =
    weather.status === "ok"
      ? `${weather.temp}°`
      : weather.status === "loading"
        ? "…"
        : "--°";

  const title =
    weather.status === "ok"
      ? `서울 · ${weather.label} · ${weather.temp}°C`
      : weather.status === "loading"
        ? "서울 날씨 불러오는 중"
        : weather.message ?? "서울 날씨를 불러올 수 없습니다";

  return (
    <div
      className="inline-flex items-center gap-[6px] 720:gap-2 ml-auto 720:ml-3 p-[5px_10px] 720:p-[6px_14px] rounded-full border border-[rgba(0,229,255,0.35)] bg-[rgba(0,229,255,0.08)] shadow-[0_0_12px_rgba(0,229,255,0.12)] flex-shrink-0"
      title={title}
      aria-label={title}
    >
      <span className="hidden 720:inline text-xs font-semibold tracking-[0.04em] text-[rgba(255,255,255,0.75)]">
        서울
      </span>
      <WeatherIcon kind={iconKind} />
      <span
        className={
          weather.status !== "ok"
            ? "text-[15px] font-semibold leading-none [font-variant-numeric:tabular-nums] text-[rgba(0,229,255,0.45)]"
            : "text-[15px] font-extrabold leading-none [font-variant-numeric:tabular-nums] text-[#00e5ff]"
        }
      >
        {tempText}
      </span>
    </div>
  );
}
