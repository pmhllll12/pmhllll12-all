"use client";

import { useCallback, useRef, useState, type ChangeEvent } from "react";

type TitanicProps = {
  hideOuterTitle?: boolean;
};

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.trim();
  if (base) {
    return `${base.replace(/\/$/, "")}${path}`;
  }
  return path;
}

/** `POST /api/titanic/james/upload` — 백엔드 `JamesDirectorUploadResponse` 와 동일 */
type UploadResponse = {
  ok?: boolean;
  message: string;
  filename: string;
  row_count: number;
  note?: string;
  /** 있으면 CSV 헤더 목록 (없을 수 있음 — `columns` 없이 응답하는 경우 대비) */
  columns?: string[];
  preview?: Record<string, unknown>[];
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

async function uploadJamesCsv(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file, file.name);
  const res = await fetch(apiUrl("/api/titanic/james/upload"), {
    method: "POST",
    body: form,
  });
  const body = (await res.json().catch(() => null)) as
    | { detail?: string | { msg?: string }[] }
    | UploadResponse
    | null;
  if (!res.ok) {
    throw new Error(
      parseApiError(body as { detail?: string | { msg?: string }[] } | null, res.status),
    );
  }
  return body as UploadResponse;
}

const INPUT_ID = "titanic-james-csv-input";

export default function Titanic({ hideOuterTitle = false }: TitanicProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [pickedName, setPickedName] = useState<string | null>(null);

  const ingest = useCallback(async (file: File) => {
    setError(null);
    setOk(null);
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("CSV 파일만 업로드할 수 있습니다.");
      return;
    }
    setBusy(true);
    setPickedName(file.name);
    try {
      const data = await uploadJamesCsv(file);
      const cols = Array.isArray(data.columns) ? data.columns : [];
      const hasGender = cols.includes("gender");
      setOk(
        `${data.message} · ${data.row_count.toLocaleString()}행, ${(file.size / 1024).toFixed(1)} KB` +
          (hasGender ? " · Sex → gender 변환됨" : ""),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "파일을 업로드하는 중 오류가 발생했습니다.");
    } finally {
      setBusy(false);
    }
  }, []);

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (f) void ingest(f);
  };

  return (
    <main className="flex-1 flex flex-col items-center bg-white text-[#0f172a] px-6 pt-8 pb-12">
      <div className="w-full max-w-[560px] flex flex-col items-stretch gap-4">
        {!hideOuterTitle ? (
          <h1 className="text-[clamp(36px,7vw,64px)] font-extrabold tracking-[-0.02em] text-center">
            타이타닉 홈
          </h1>
        ) : null}

        <section
          className={hideOuterTitle ? "mt-0" : "mt-9"}
          aria-labelledby="titanic-upload-heading"
        >
          <h2 id="titanic-upload-heading" className="text-lg font-bold">
            James — Titanic 데이터
          </h2>
          <p className="text-sm leading-[1.65] text-[#475569] [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:bg-[#f1f5f9] [&_code]:text-[13px]">
            Kaggle 형식의 Titanic CSV(예: <code>Titanic-Dataset.csv</code>)를
            업로드합니다. <code>POST /api/titanic/james/upload</code>
          </p>

          <input
            id={INPUT_ID}
            ref={inputRef}
            type="file"
            accept=".csv,text/csv"
            className="sr-only"
            onChange={onInputChange}
          />

          <label
            htmlFor={INPUT_ID}
            className={`flex flex-col items-center justify-center gap-2 mt-6 min-h-[200px] px-5 py-7 border-2 border-dashed rounded-2xl text-center transition cursor-pointer ${
              dragOver
                ? "border-[#0ea5e9] bg-[#e0f2fe] shadow-[0_0_0_3px_rgba(14,165,233,0.2)]"
                : "border-[#cbd5e1] bg-[#f8fafc] hover:border-[#38bdf8] hover:bg-[#f0f9ff]"
            }${busy ? " pointer-events-none opacity-65" : ""}`}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const f = e.dataTransfer.files?.[0];
              if (f) void ingest(f);
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
          >
            <span
              className="flex items-center justify-center w-12 h-12 rounded-xl bg-[#e2e8f0] text-[22px] font-bold text-[#64748b]"
              aria-hidden
            >
              ↑
            </span>
            <span className="mt-1 text-[15px] font-extrabold text-[#0f172a]">업로드 창</span>
            <span className="max-w-[360px] text-[13px] leading-[1.55] text-[#64748b]">
              {pickedName
                ? `선택된 파일: ${pickedName}`
                : "Titanic CSV를 여기로 드래그하거나, 이 영역을 클릭하세요."}
            </span>
          </label>

          <div className="flex justify-center mt-5">
            <button
              type="button"
              className="px-6 py-3 border-none rounded-full text-sm font-bold cursor-pointer text-white bg-[linear-gradient(135deg,#0ea5e9,#0284c7)] shadow-[0_4px_14px_rgba(14,165,233,0.35)] transition enabled:hover:-translate-y-px enabled:hover:shadow-[0_6px_18px_rgba(14,165,233,0.45)] disabled:cursor-not-allowed disabled:opacity-55"
              disabled={busy}
              onClick={() => inputRef.current?.click()}
            >
              {busy ? "처리 중…" : "업로드 버튼 (파일 선택)"}
            </button>
          </div>

          {error ? (
            <p
              className="p-[12px_14px] rounded-[10px] text-sm leading-[1.5] text-center text-[#991b1b] bg-[#fef2f2] border border-[#fecaca]"
              role="alert"
            >
              {error}
            </p>
          ) : null}
          {ok ? (
            <p className="p-[12px_14px] rounded-[10px] text-sm leading-[1.5] text-center text-[#166534] bg-[#f0fdf4] border border-[#bbf7d0]">
              {ok}
            </p>
          ) : null}
        </section>
      </div>
    </main>
  );
}
