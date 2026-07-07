"use client";

import { useCallback, useEffect, useId, useState, type FormEvent } from "react";
import Link from "next/link";

const LS_KEY = "wc_community_posts_v1";

type BoardPost = {
  id: string;
  body: string;
  createdAt: number;
};

function readPosts(): BoardPost[] {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as BoardPost[];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function writePosts(rows: BoardPost[]) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(rows.slice(-80)));
  } catch {
    /* ignore */
  }
}

export default function Board() {
  const formId = useId();
  const [posts, setPosts] = useState<BoardPost[]>([]);
  const [draft, setDraft] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    setPosts(readPosts());
  }, []);

  const onSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const body = draft.trim();
      if (body.length < 2) {
        setNotice("두 글자 이상 입력해 주세요.");
        return;
      }
      if (body.length > 2000) {
        setNotice("2000자 이내로 작성해 주세요.");
        return;
      }
      const row: BoardPost = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        body,
        createdAt: Date.now(),
      };
      const next = [...readPosts(), row];
      writePosts(next);
      setPosts(next);
      setDraft("");
      setNotice("등록되었습니다. (이 브라우저에만 저장됩니다)");
      window.setTimeout(() => setNotice(null), 2800);
    },
    [draft],
  );

  return (
    <main className="flex-1 px-5 pt-7 pb-16 bg-[linear-gradient(180deg,var(--color-bg-1)_0%,var(--color-bg-0)_40%)]">
      <div className="max-w-[640px] mx-auto">
        <nav className="mb-5">
          <Link
            href="/"
            className="inline-flex text-sm font-semibold text-accent hover:underline"
          >
            ← 홈으로
          </Link>
        </nav>

        <h1 className="mb-4 text-[clamp(26px,5vw,36px)] font-extrabold tracking-[-0.02em] text-fg-0">
          자유게시판 · 건의사항
        </h1>
        <p className="mb-7 text-[15px] leading-[1.65] text-fg-2">
          월드컵 이야기·응원·잡담은 물론, 사이트 개선 건의나 문의도 남겨 주세요.
          <strong className="text-fg-1 font-bold"> 비로그인·가벼운 마음으로</strong> 쓰시면 됩니다. (현재는 이
          기기 브라우저에만 저장되는 데모입니다. 서버 게시판 연동 시 공개·관리
          정책이 적용됩니다.)
        </p>

        <form
          className="mb-4 p-[18px] rounded-[14px] border border-border bg-[rgba(10,16,32,0.55)]"
          onSubmit={onSubmit}
          aria-labelledby={formId}
        >
          <label
            id={formId}
            className="block mb-2 text-[13px] font-bold text-accent tracking-[0.04em] uppercase"
            htmlFor="board-body"
          >
            글 작성
          </label>
          <textarea
            id="board-body"
            className="w-full p-[12px_14px] rounded-[10px] border border-[rgba(148,163,184,0.25)] bg-[rgba(4,7,15,0.65)] text-fg-0 text-[15px] leading-[1.55] resize-y min-h-[120px] placeholder:text-fg-3 focus:outline-none focus:border-[rgba(34,211,238,0.55)] focus:shadow-[0_0_0_1px_rgba(34,211,238,0.2)]"
            rows={5}
            maxLength={2000}
            placeholder="예: ○○ 경기 중계 화면이 있었으면 좋겠어요 / 오타 제보 / 응원글 자유"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <div className="flex items-center justify-between mt-3 gap-3">
            <span className="text-xs text-fg-3">{draft.length} / 2000</span>
            <button
              type="submit"
              className="px-[22px] py-[10px] rounded-full border-none bg-accent text-[#04131a] font-extrabold text-sm cursor-pointer transition hover:bg-accent-strong hover:-translate-y-px"
            >
              등록하기
            </button>
          </div>
        </form>

        {notice ? (
          <p
            className="mb-5 px-3 py-[10px] rounded-[10px] text-[13px] font-semibold text-[#0f172a] bg-[rgba(34,211,238,0.88)]"
            role="status"
          >
            {notice}
          </p>
        ) : null}

        <section className="mt-2" aria-labelledby="board-list-title">
          <h2 id="board-list-title" className="mb-3 text-[15px] font-extrabold text-fg-0">
            최근 글
          </h2>
          {posts.length === 0 ? (
            <p className="p-5 rounded-xl border border-dashed border-[rgba(148,163,184,0.35)] text-sm text-fg-3 text-center">
              아직 등록된 글이 없습니다. 첫 글을 남겨 보세요.
            </p>
          ) : (
            <ul className="list-none flex flex-col gap-3">
              {[...posts]
                .sort((a, b) => b.createdAt - a.createdAt)
                .map((p) => (
                  <li
                    key={p.id}
                    className="p-[14px_16px] rounded-xl border border-[rgba(148,163,184,0.12)] bg-[rgba(8,14,28,0.45)]"
                  >
                    <time
                      className="block mb-2 text-xs font-semibold text-accent"
                      dateTime={new Date(p.createdAt).toISOString()}
                    >
                      {new Intl.DateTimeFormat("ko-KR", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }).format(new Date(p.createdAt))}
                    </time>
                    <p className="text-[15px] leading-[1.55] text-fg-1 whitespace-pre-wrap break-words">
                      {p.body}
                    </p>
                  </li>
                ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
