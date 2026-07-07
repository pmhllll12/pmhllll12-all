"use client";

import { useCallback, useEffect, useState } from "react";

const PAGE_SIZE = 50;

type PassengersPageResponse = {
  ok: boolean;
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  columns: string[];
  items: Record<string, unknown>[];
};

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.trim();
  if (base) {
    return `${base.replace(/\/$/, "")}${path}`;
  }
  return path;
}

function buildPageItems(current: number, total: number): (number | "ellipsis")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  const items: (number | "ellipsis")[] = [];
  const windowStart = Math.max(2, current - 1);
  const windowEnd = Math.min(total - 1, current + 1);

  items.push(1);
  if (windowStart > 2) items.push("ellipsis");
  for (let p = windowStart; p <= windowEnd; p += 1) {
    items.push(p);
  }
  if (windowEnd < total - 1) items.push("ellipsis");
  items.push(total);
  return items;
}

const PAGINATION_BTN_BASE =
  "min-w-[40px] h-10 px-[10px] border border-[#cbd5e1] -ml-px bg-white text-[#2563eb] text-sm font-semibold cursor-pointer transition first:ml-0 first:rounded-l-lg last:rounded-r-lg disabled:opacity-45 disabled:cursor-not-allowed";
const PAGINATION_BTN = `${PAGINATION_BTN_BASE} enabled:hover:bg-[#f1f5f9]`;
const PAGINATION_BTN_ACTIVE = `${PAGINATION_BTN_BASE} bg-[#2563eb] text-white border-[#2563eb] z-[1]`;

export default function TitanicPassengers() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState<PassengersPageResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** 「2. 승객 목록」화면 진입 시 Walter 라우터 `introduce_myself` → 유스케이스·저장소 실행 */
  useEffect(() => {
    void fetch(apiUrl("/api/titanic/walter-roaster/myself"), { method: "GET" }).catch(() => {
      /* Walter 호출 실패는 승객 표시와 별개 */
    });
  }, []);

  const loadPage = useCallback(async (targetPage: number) => {
    setBusy(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: String(targetPage),
        page_size: String(PAGE_SIZE),
      });
      const res = await fetch(apiUrl(`/api/titanic/james/passengers?${params}`));
      const body = (await res.json().catch(() => null)) as
        | { detail?: string }
        | PassengersPageResponse
        | null;
      if (!res.ok) {
        let detail =
          body && typeof body === "object" && "detail" in body && typeof body.detail === "string"
            ? body.detail
            : `조회에 실패했습니다. (${res.status})`;
        if (res.status === 404) {
          detail =
            "승객 목록 API를 찾을 수 없습니다. backend 폴더에서 python main.py 로 서버를 재시작한 뒤 다시 시도하세요.";
        }
        throw new Error(detail);
      }
      const parsed = body as PassengersPageResponse;
      setData(parsed);
      if (parsed.total_pages > 0 && targetPage > parsed.total_pages) {
        setPage(parsed.total_pages);
      } else {
        setPage(targetPage);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "승객 목록을 불러오지 못했습니다.");
      setData(null);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    void loadPage(page);
  }, [page, loadPage]);

  const totalPages = data?.total_pages ?? 0;
  const pageItems = totalPages > 0 ? buildPageItems(page, totalPages) : [];

  return (
    <section className="p-6 bg-white" aria-labelledby="passengers-heading">
      <h2 id="passengers-heading" className="text-lg font-bold text-[#0f172a]">
        승객 목록
      </h2>
      <p className="mt-2 mb-5 text-sm text-[#64748b]">
        {data
          ? `전체 ${data.total_count.toLocaleString()}명 · 페이지당 ${PAGE_SIZE}명`
          : "데이터베이스에서 승객 정보를 불러옵니다."}
      </p>

      {error ? (
        <p
          className="mb-4 p-[12px_14px] rounded-[10px] text-sm text-[#991b1b] bg-[#fef2f2] border border-[#fecaca]"
          role="alert"
        >
          {error}
        </p>
      ) : null}

      {busy && !data ? <p className="text-sm text-[#64748b]">목록을 불러오는 중…</p> : null}

      {data && data.items.length > 0 ? (
        <div
          className={`overflow-x-auto mb-6${busy ? " opacity-55 pointer-events-none" : ""}`}
        >
          <table className="w-full border-collapse text-[13px] [&_th]:p-[8px_10px] [&_td]:p-[8px_10px] [&_th]:border [&_td]:border [&_th]:border-[#e2e8f0] [&_td]:border-[#e2e8f0] [&_th]:text-left [&_td]:text-left [&_th]:whitespace-nowrap [&_td]:whitespace-nowrap [&_th]:bg-[#f1f5f9] [&_th]:font-semibold [&_th]:text-[#0f172a] [&_tbody_tr:nth-child(even)]:bg-[#f8fafc]">
            <thead>
              <tr>
                {data.columns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.items.map((row, i) => (
                <tr key={`${page}-${i}-${String(row.PassengerId ?? i)}`}>
                  {data.columns.map((col) => (
                    <td key={col}>{String(row[col] ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {data && data.total_count === 0 && !busy ? (
        <p className="text-sm text-[#64748b]">
          저장된 승객이 없습니다. 「1. 데이터 수집 및 실습」에서 CSV를 먼저 업로드하세요.
        </p>
      ) : null}

      {totalPages > 0 ? (
        <nav className="flex flex-wrap items-center justify-center mt-2" aria-label="승객 목록 페이지">
          <button
            type="button"
            className={PAGINATION_BTN}
            disabled={page <= 1 || busy}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            aria-label="이전 페이지"
          >
            ‹
          </button>
          {pageItems.map((item, idx) =>
            item === "ellipsis" ? (
              <span
                key={`e-${idx}`}
                className="inline-flex items-center justify-center min-w-[40px] h-10 -ml-px border border-[#cbd5e1] bg-white text-[#64748b] text-sm"
              >
                …
              </span>
            ) : (
              <button
                key={item}
                type="button"
                className={item === page ? PAGINATION_BTN_ACTIVE : PAGINATION_BTN}
                disabled={busy}
                onClick={() => setPage(item)}
                aria-current={item === page ? "page" : undefined}
              >
                {item}
              </button>
            ),
          )}
          <button
            type="button"
            className={PAGINATION_BTN}
            disabled={page >= totalPages || busy}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            aria-label="다음 페이지"
          >
            ›
          </button>
        </nav>
      ) : null}
    </section>
  );
}
