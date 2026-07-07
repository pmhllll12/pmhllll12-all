"use client";

import { useCallback, useRef, useState, type ChangeEvent } from "react";

type Contact = { nickname: string; email: string; name?: string };

function parseCsvLine(line: string): string[] {
  const result: string[] = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]!;
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
      else inQuotes = !inQuotes;
    } else if (ch === "," && !inQuotes) {
      result.push(current.trim());
      current = "";
    } else {
      current += ch;
    }
  }
  result.push(current.trim());
  return result;
}

function parseCsv(text: string): Contact[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = parseCsvLine(lines[0]!).map((h) => h.toLowerCase());

  // 단순 CSV: nickname/이메일 | Google 연락처: e-mail 1 - value
  const emailIdx = headers.findIndex(
    (h) => h === "email" || h === "이메일" || h === "e-mail 1 - value"
  );
  if (emailIdx === -1) return [];

  const nicknameIdx = headers.findIndex((h) => h === "nickname" || h === "닉네임");
  const firstNameIdx = headers.findIndex((h) => h === "first name");
  const lastNameIdx = headers.findIndex((h) => h === "last name");
  const nameIdx = headers.findIndex((h) => h === "name" || h === "이름");

  return lines.slice(1).flatMap((line) => {
    const cols = parseCsvLine(line);
    const email = cols[emailIdx] ?? "";
    if (!email) return [];

    // Nickname → First+Last → 이메일 앞부분 순으로 폴백
    let nickname = nicknameIdx !== -1 ? (cols[nicknameIdx] ?? "") : "";
    if (!nickname) {
      const first = firstNameIdx !== -1 ? (cols[firstNameIdx] ?? "") : "";
      const last = lastNameIdx !== -1 ? (cols[lastNameIdx] ?? "") : "";
      nickname = [first, last].filter(Boolean).join(" ");
    }
    if (!nickname) nickname = email.split("@")[0] ?? "";

    const name = nameIdx !== -1 ? (cols[nameIdx] ?? "") : undefined;
    return [{ nickname, email, name }];
  });
}

export default function AddressBookPanel() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [pickedName, setPickedName] = useState<string | null>(null);
  const [uploadMsg, setUploadMsg] = useState<{ type: "ok" | "error"; text: string } | null>(null);

  const ingest = useCallback((file: File) => {
    setUploadMsg(null);
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setUploadMsg({ type: "error", text: "CSV 파일만 업로드할 수 있습니다." });
      return;
    }
    setBusy(true);
    setPickedName(file.name);

    // 1) 백엔드 DB에 저장 (자동완성용)
    const formData = new FormData();
    formData.append("file", file);
    fetch("/api/community/juso/upload", { method: "POST", body: formData }).catch(() => {
      // 저장 실패는 조용히 무시 — 로컬 미리보기는 계속 동작
    });

    // 2) 로컬 미리보기
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const parsed = parseCsv(text);
      if (parsed.length === 0) {
        setUploadMsg({
          type: "error",
          text: "파싱된 데이터가 없습니다. 헤더에 nickname/이메일 컬럼이 있는지 확인하세요.",
        });
      } else {
        setContacts((prev) => {
          const map = new Map(prev.map((c) => [c.email, c]));
          parsed.forEach((c) => map.set(c.email, c));
          return Array.from(map.values());
        });
        setUploadMsg({ type: "ok", text: `${parsed.length}명 등록됐습니다.` });
      }
      setBusy(false);
    };
    reader.readAsText(file, "utf-8");
  }, []);

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (f) ingest(f);
  };

  return (
    <div className="flex flex-col gap-5 h-full">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="m-0 text-base font-extrabold tracking-[0.04em]">📒 주소록</h2>
          <p className="mt-1 text-[11px] text-fg-2">CSV 파일로 연락처를 일괄 등록합니다.</p>
        </div>
        <button
          type="button"
          onClick={() => { setUploadMsg(null); setPickedName(null); setModalOpen(true); }}
          className="px-4 py-2 rounded-xl font-bold text-sm bg-accent text-[#04131a] transition hover:bg-accent-strong"
        >
          + 등록
        </button>
      </div>

      {/* 주소록 목록 */}
      <div className="flex-1 bg-bg-1 border border-border rounded-2xl overflow-hidden shadow-[0_8px_24px_rgba(0,0,0,0.35)]">
        {contacts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-fg-2 text-sm gap-2">
            <span className="text-3xl">📭</span>
            <span>등록된 주소록이 없습니다.</span>
            <span className="text-[11px]">우상단 등록 버튼으로 CSV를 업로드하세요.</span>
          </div>
        ) : (
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-bg-0">
                <th className="text-left p-[10px_14px] font-bold tracking-[0.04em] text-fg-2 uppercase">닉네임</th>
                <th className="text-left p-[10px_14px] font-bold tracking-[0.04em] text-fg-2 uppercase">이메일</th>
                <th className="text-left p-[10px_14px] font-bold tracking-[0.04em] text-fg-2 uppercase">이름</th>
                <th className="p-[10px_14px]" />
              </tr>
            </thead>
            <tbody>
              {contacts.map((c, i) => (
                <tr key={c.email} className={`border-b border-border ${i % 2 === 0 ? "" : "bg-bg-0"}`}>
                  <td className="p-[10px_14px] font-semibold text-fg-0">{c.nickname}</td>
                  <td className="p-[10px_14px] text-accent">{c.email}</td>
                  <td className="p-[10px_14px] text-fg-2">{c.name ?? "-"}</td>
                  <td className="p-[10px_14px] text-right">
                    <button
                      type="button"
                      onClick={() => setContacts((prev) => prev.filter((x) => x.email !== c.email))}
                      className="text-[11px] text-red-400 hover:text-red-300 transition"
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 업로드 모달 */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(0,0,0,0.6)]">
          <div className="relative w-[min(90vw,480px)] flex flex-col gap-4 bg-bg-1 border border-border rounded-2xl p-6 shadow-[0_24px_64px_rgba(0,0,0,0.6)]">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="m-0 text-sm font-extrabold tracking-[0.04em]">주소록 CSV 업로드</h3>
                <p className="mt-1 text-[11px] text-fg-2">
                  헤더: <code className="bg-bg-0 px-1 rounded">nickname, email, name</code> (name 선택)
                </p>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="text-fg-2 text-lg leading-none hover:text-fg-0 transition"
                aria-label="닫기"
              >
                ×
              </button>
            </div>

            <input
              ref={inputRef}
              type="file"
              accept=".csv,text/csv"
              className="sr-only"
              onChange={onInputChange}
            />

            <label
              className={`flex flex-col items-center justify-center gap-2 min-h-[180px] px-5 py-7 border-2 border-dashed rounded-2xl text-center transition cursor-pointer ${
                dragOver
                  ? "border-accent bg-[rgba(0,229,255,0.08)] shadow-[0_0_0_3px_rgba(0,229,255,0.2)]"
                  : "border-border bg-bg-0 hover:border-accent hover:bg-[rgba(0,229,255,0.04)]"
              }${busy ? " pointer-events-none opacity-55" : ""}`}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                const f = e.dataTransfer.files?.[0];
                if (f) ingest(f);
              }}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => inputRef.current?.click()}
            >
              <span className="flex items-center justify-center w-12 h-12 rounded-xl bg-bg-0 border border-border text-2xl" aria-hidden>
                ↑
              </span>
              <span className="text-[13px] font-extrabold text-fg-0">업로드 창</span>
              <span className="max-w-[300px] text-[11px] leading-[1.55] text-fg-2">
                {pickedName
                  ? `선택된 파일: ${pickedName}`
                  : "CSV를 여기로 드래그하거나, 이 영역을 클릭하세요."}
              </span>
            </label>

            <button
              type="button"
              disabled={busy}
              onClick={() => inputRef.current?.click()}
              className="w-full py-2.5 rounded-xl font-bold text-sm bg-accent text-[#04131a] transition hover:bg-accent-strong disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {busy ? "처리 중…" : "파일 선택"}
            </button>

            {uploadMsg && (
              <p className={`text-xs text-center rounded-xl p-2 ${
                uploadMsg.type === "ok"
                  ? "text-green-400 bg-[rgba(74,222,128,0.08)] border border-[rgba(74,222,128,0.2)]"
                  : "text-red-400 bg-[rgba(248,113,113,0.08)] border border-[rgba(248,113,113,0.2)]"
              }`}>
                {uploadMsg.text}
              </p>
            )}

            {uploadMsg?.type === "ok" && (
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="w-full py-2 rounded-xl font-bold text-sm border border-border text-fg-2 hover:text-fg-0 transition"
              >
                닫기
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
