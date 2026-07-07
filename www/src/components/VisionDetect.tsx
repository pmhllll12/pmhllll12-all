"use client";

import { useCallback, useRef, useState, type ChangeEvent } from "react";

function apiUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.trim();
  if (base) {
    return `${base.replace(/\/$/, "")}${path}`;
  }
  return path;
}

/** `POST /api/vision/recognize-face` — 백엔드 `PredictFaceResponse` 와 동일 */
type RecognizeResponse = {
  ok?: boolean;
  message: string;
  predicted_name: string;
  confidence: number;
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

async function recognizeFace(file: File): Promise<RecognizeResponse> {
  const form = new FormData();
  form.append("file", file, file.name);
  const res = await fetch(apiUrl("/api/vision/recognize-face"), {
    method: "POST",
    body: form,
  });
  const body = (await res.json().catch(() => null)) as
    | { detail?: string | { msg?: string }[] }
    | RecognizeResponse
    | null;
  if (!res.ok) {
    throw new Error(
      parseApiError(body as { detail?: string | { msg?: string }[] } | null, res.status),
    );
  }
  return body as RecognizeResponse;
}

const INPUT_ID = "vision-face-recognize-input";

export default function VisionDetect() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecognizeResponse | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const ingest = useCallback(
    async (file: File) => {
      setError(null);
      setResult(null);
      if (!file.type.startsWith("image/")) {
        setError("이미지 파일만 업로드할 수 있습니다.");
        return;
      }
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(file));
      setBusy(true);
      try {
        const data = await recognizeFace(file);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "인식 중 오류가 발생했습니다.");
      } finally {
        setBusy(false);
      }
    },
    [previewUrl],
  );

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (f) void ingest(f);
  };

  return (
    <main className="flex-1 flex flex-col items-center bg-white text-[#0f172a] px-6 pt-8 pb-12">
      <div className="w-full max-w-[560px] flex flex-col items-stretch gap-4">
        <section aria-labelledby="vision-detect-heading">
          <h2 id="vision-detect-heading" className="text-lg font-bold">
            얼굴 인식 — 누구인가요?
          </h2>
          <p className="text-sm leading-[1.65] text-[#475569] [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:bg-[#f1f5f9] [&_code]:text-[13px]">
            사람 얼굴 사진을 업로드하면 파인튜닝된 YOLO 분류 모델이 이름을 예측합니다.{" "}
            <code>POST /api/vision/recognize-face</code>
          </p>

          <input
            id={INPUT_ID}
            ref={inputRef}
            type="file"
            accept="image/*"
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
            {previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewUrl}
                alt="업로드한 얼굴 사진 미리보기"
                className="max-h-[140px] rounded-xl object-contain"
              />
            ) : (
              <span
                className="flex items-center justify-center w-12 h-12 rounded-xl bg-[#e2e8f0] text-[22px] font-bold text-[#64748b]"
                aria-hidden
              >
                ↑
              </span>
            )}
            <span className="mt-1 text-[15px] font-extrabold text-[#0f172a]">업로드 창</span>
            <span className="max-w-[360px] text-[13px] leading-[1.55] text-[#64748b]">
              얼굴 사진을 여기로 드래그하거나, 이 영역을 클릭하세요.
            </span>
          </label>

          <div className="flex justify-center mt-5">
            <button
              type="button"
              className="px-6 py-3 border-none rounded-full text-sm font-bold cursor-pointer text-white bg-[linear-gradient(135deg,#0ea5e9,#0284c7)] shadow-[0_4px_14px_rgba(14,165,233,0.35)] transition enabled:hover:-translate-y-px enabled:hover:shadow-[0_6px_18px_rgba(14,165,233,0.45)] disabled:cursor-not-allowed disabled:opacity-55"
              disabled={busy}
              onClick={() => inputRef.current?.click()}
            >
              {busy ? "인식 중…" : "업로드 버튼 (파일 선택)"}
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
          {result ? (
            <p className="p-[12px_14px] rounded-[10px] text-sm leading-[1.5] text-center text-[#166534] bg-[#f0fdf4] border border-[#bbf7d0]">
              예측 결과: <strong>{result.predicted_name}</strong> ·{" "}
              {(result.confidence * 100).toFixed(1)}%
            </p>
          ) : null}
        </section>
      </div>
    </main>
  );
}
