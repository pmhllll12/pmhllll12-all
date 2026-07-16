"use client";

import { useState, type FormEvent } from "react";

type Mode = "crawler" | "scraper";

type CrawlResponse = {
  ok: boolean;
  website: string;
  keyword: string;
  pages_crawled: number;
  urls: string[];
  output_path: string;
};

type ScrapeResponse = {
  ok: boolean;
  website: string;
  keyword: string;
  pages_scanned: number;
  matched_count: number;
  output_path: string;
};

const TABS: { id: Mode; label: string }[] = [
  { id: "crawler", label: "크롤러" },
  { id: "scraper", label: "스크래퍼" },
];

const COMMAND_PLACEHOLDER: Record<Mode, string> = {
  crawler: "이 사이트 내부 링크를 2단계까지 돌아줘",
  scraper: "이 사이트에서 '파이썬' 관련 내용을 찾아줘",
};

function parseApiError(
  body: { detail?: string | { msg?: string }[] } | null,
  status: number,
): string {
  if (body && typeof body === "object" && "detail" in body) {
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((d) => (typeof d === "object" && d?.msg ? d.msg : String(d)))
        .join(", ");
    }
  }
  return `요청에 실패했습니다. (${status})`;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(parseApiError(body as { detail?: string | { msg?: string }[] } | null, res.status));
  }
  return body as T;
}

export function CrawlerScraperPanel() {
  const [mode, setMode] = useState<Mode>("crawler");
  const [website, setWebsite] = useState("");
  const [command, setCommand] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [crawlResult, setCrawlResult] = useState<CrawlResponse | null>(null);
  const [scrapeResult, setScrapeResult] = useState<ScrapeResponse | null>(null);

  const switchMode = (next: Mode) => {
    if (next === mode) return;
    setMode(next);
    setError(null);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmedWebsite = website.trim();
    const trimmedCommand = command.trim();
    if (!trimmedWebsite || !trimmedCommand || busy) return;

    setBusy(true);
    setError(null);
    try {
      if (mode === "crawler") {
        const result = await postJson<CrawlResponse>("/api/ontology/crawl/submit", {
          website: trimmedWebsite,
          command: trimmedCommand,
        });
        setCrawlResult(result);
      } else {
        const result = await postJson<ScrapeResponse>("/api/ontology/scrape/submit", {
          website: trimmedWebsite,
          command: trimmedCommand,
        });
        setScrapeResult(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "요청 중 오류가 발생했습니다.");
    } finally {
      setBusy(false);
    }
  };

  const result = mode === "crawler" ? crawlResult : scrapeResult;

  return (
    <div className="w-full max-w-2xl">
      <div className="mb-4 inline-flex rounded-full border border-border bg-bg-1 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => switchMode(tab.id)}
            aria-pressed={mode === tab.id}
            className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
              mode === tab.id ? "bg-emerald-600 text-white" : "text-fg-2 hover:bg-chip-bg"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <form
        onSubmit={onSubmit}
        className="flex flex-col gap-3 rounded-3xl border border-border bg-bg-1 p-4 text-left shadow-sm"
      >
        <div>
          <label htmlFor="crawler-website" className="mb-1 block text-xs font-semibold text-fg-2">
            사이트 주소
          </label>
          <input
            id="crawler-website"
            type="url"
            required
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="https://example.com"
            className="w-full rounded-xl border border-border bg-transparent px-3 py-2 text-sm text-fg-0 placeholder:text-fg-3 focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="crawler-command" className="mb-1 block text-xs font-semibold text-fg-2">
            자연어 명령어
          </label>
          <textarea
            id="crawler-command"
            required
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder={COMMAND_PLACEHOLDER[mode]}
            rows={2}
            className="w-full resize-none rounded-xl border border-border bg-transparent px-3 py-2 text-sm text-fg-0 placeholder:text-fg-3 focus:outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={busy || !website.trim() || !command.trim()}
          className="self-end rounded-full bg-emerald-600 px-5 py-2 text-sm font-semibold text-white transition enabled:hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {busy ? "실행 중…" : mode === "crawler" ? "크롤링 실행" : "스크래핑 실행"}
        </button>
      </form>

      {error ? (
        <p
          className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
          role="alert"
        >
          {error}
        </p>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-2xl border border-border bg-bg-1 p-4 text-sm text-fg-1">
          <p>
            <strong>keyword</strong>: {result.keyword}
          </p>
          {mode === "crawler" && crawlResult ? (
            <>
              <p className="mt-1">수집한 페이지: {crawlResult.pages_crawled}건</p>
              <ul className="mt-2 max-h-48 list-disc space-y-1 overflow-y-auto pl-5 text-fg-2">
                {crawlResult.urls.map((url) => (
                  <li key={url} className="break-all">
                    {url}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          {mode === "scraper" && scrapeResult ? (
            <p className="mt-1">
              스캔한 페이지 {scrapeResult.pages_scanned}건 중 매칭 {scrapeResult.matched_count}건
            </p>
          ) : null}
          <p className="mt-2 text-xs text-fg-3">저장 경로: {result.output_path}</p>
        </div>
      ) : null}
    </div>
  );
}
