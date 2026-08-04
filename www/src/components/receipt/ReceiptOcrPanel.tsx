"use client";

import { useCallback, useEffect, useState } from "react";

type ReceiptOcrRow = {
  key: string;
  filename: string;
  uploaded_at: string;
  ocr_text: string;
};

type LoadState = { type: "loading" } | { type: "error"; message: string } | { type: "ok" };

function parseApiError(body: { detail?: string } | null, status: number): string {
  if (body && typeof body === "object" && typeof body.detail === "string") {
    return body.detail;
  }
  return `요청에 실패했습니다. (${status})`;
}

export function ReceiptOcrPanel() {
  const [rows, setRows] = useState<ReceiptOcrRow[]>([]);
  const [state, setState] = useState<LoadState>({ type: "loading" });

  const load = useCallback(async () => {
    setState({ type: "loading" });
    try {
      const res = await fetch("/api/admin/s3/receipts");
      const body = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(parseApiError(body as { detail?: string } | null, res.status));
      }
      setRows(body as ReceiptOcrRow[]);
      setState({ type: "ok" });
    } catch (err) {
      setState({
        type: "error",
        message: err instanceof Error ? err.message : "요청 중 오류가 발생했습니다.",
      });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="w-full">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs text-fg-3">receipts/ 폴더의 이미지를 Gemini OCR로 읽어옵니다.</p>
        <button
          type="button"
          onClick={load}
          disabled={state.type === "loading"}
          className="rounded-full border border-border px-4 py-1.5 text-sm font-semibold text-fg-1 transition enabled:hover:bg-chip-bg disabled:cursor-not-allowed disabled:opacity-40"
        >
          {state.type === "loading" ? "불러오는 중…" : "새로고침"}
        </button>
      </div>

      {state.type === "error" ? (
        <p
          className="mb-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
          role="alert"
        >
          {state.message}
        </p>
      ) : null}

      {state.type === "loading" && rows.length === 0 ? (
        <p className="text-sm text-fg-2">불러오는 중…</p>
      ) : null}

      {state.type === "ok" && rows.length === 0 ? (
        <p className="text-sm text-fg-2">receipts/ 폴더에 이미지가 없습니다.</p>
      ) : null}

      {rows.length > 0 ? (
        <div className="overflow-x-auto rounded-2xl border border-border">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-border bg-bg-1">
                <th className="px-4 py-2 font-semibold text-fg-1">파일명</th>
                <th className="px-4 py-2 font-semibold text-fg-1">업로드 일시</th>
                <th className="px-4 py-2 font-semibold text-fg-1">OCR 텍스트</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.key} className="border-b border-border last:border-b-0">
                  <td className="px-4 py-3 align-top text-fg-1">{row.filename}</td>
                  <td className="px-4 py-3 align-top whitespace-nowrap text-fg-2">
                    {row.uploaded_at}
                  </td>
                  <td className="px-4 py-3 align-top whitespace-pre-wrap text-fg-1">
                    {row.ocr_text}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
