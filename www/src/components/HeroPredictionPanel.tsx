"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { getHighlightMatch, type WcMatch } from "@/data/worldCup2026Schedule";
import { koTeam } from "@/data/worldCup2026Ko";

const LS_POINTS = "wc_gamify_points";
const LS_VOTES = "wc_gamify_votes";
const LS_PICKS = "wc_gamify_picks";

type Pick = "H" | "D" | "A";

type VoteBag = Record<string, { H: number; D: number; A: number }>;

type PickRow = { id: number; pick: Pick; t: number };

function readPoints(): number {
  try {
    const n = Number(localStorage.getItem(LS_POINTS));
    if (Number.isFinite(n) && n >= 0) return Math.floor(n);
  } catch {
    /* ignore */
  }
  return 1000;
}

function readVotes(): VoteBag {
  try {
    const raw = localStorage.getItem(LS_VOTES);
    if (raw) return JSON.parse(raw) as VoteBag;
  } catch {
    /* ignore */
  }
  return {};
}

function writeVotes(v: VoteBag) {
  try {
    localStorage.setItem(LS_VOTES, JSON.stringify(v));
  } catch {
    /* ignore */
  }
}

function readPicks(): PickRow[] {
  try {
    const raw = localStorage.getItem(LS_PICKS);
    if (raw) {
      const arr = JSON.parse(raw) as PickRow[];
      return Array.isArray(arr) ? arr : [];
    }
  } catch {
    /* ignore */
  }
  return [];
}

function writePicks(rows: PickRow[]) {
  try {
    localStorage.setItem(LS_PICKS, JSON.stringify(rows.slice(-200)));
  } catch {
    /* ignore */
  }
}

function seedTotals(mid: number): { H: number; D: number; A: number } {
  /* 데모용 초기 분포 — 실서비스에서는 서버 집계로 교체 */
  if (mid <= 2) return { H: 52, D: 22, A: 26 };
  return { H: 40, D: 30, A: 30 };
}

function sessionVoteKey(mid: number) {
  return `wc_gamify_vote_${mid}`;
}

function readSessionVote(mid: number): Pick | null {
  try {
    const v = sessionStorage.getItem(sessionVoteKey(mid));
    if (v === "H" || v === "D" || v === "A") return v;
  } catch {
    /* ignore */
  }
  return null;
}

function writeSessionVote(mid: number, p: Pick | null) {
  try {
    if (p === null) sessionStorage.removeItem(sessionVoteKey(mid));
    else sessionStorage.setItem(sessionVoteKey(mid), p);
  } catch {
    /* ignore */
  }
}

type HeroPredictionPanelProps = {
  onAiPreset?: (text: string) => void;
};

const CARD = "p-[14px_14px_12px] rounded-xl bg-[rgba(4,10,22,0.55)] border border-[rgba(148,163,184,0.12)]";
const CARD_TITLE =
  "mb-2 text-[13px] font-extrabold tracking-[0.04em] uppercase text-[rgba(34,211,238,0.95)]";
const CARD_SUB = "mb-[10px] text-xs text-[rgba(148,163,184,0.95)]";
const PICK_BASE =
  "flex-1 min-w-[72px] rounded-[10px] border border-[rgba(255,255,255,0.18)] bg-[rgba(255,255,255,0.04)] text-fg-0 font-bold cursor-pointer transition hover:border-[rgba(34,211,238,0.55)] hover:bg-[rgba(34,211,238,0.08)]";
const PICK_ON = "border-accent text-accent bg-[rgba(34,211,238,0.12)]";

export default function HeroPredictionPanel({
  onAiPreset,
}: HeroPredictionPanelProps) {
  /* getHighlightMatch()의 기본값(new Date())은 서버 렌더 시각과 클라이언트 하이드레이션
     시각이 갈라지면(특히 이 페이지처럼 정적으로 캐시된 경우) 서로 다른 경기를 골라 텍스트가
     달라져 하이드레이션 에러(#418)를 낸다. 첫 렌더는 시각과 무관한 고정값으로 그리고,
     마운트 후에 실제 "다음 경기"로 갱신한다 — 아래 localStorage 패턴과 동일한 이유. */
  const [match, setMatch] = useState<WcMatch>(() => getHighlightMatch(new Date(0)));
  const mid = match.id;
  const homeKo = koTeam(match.home);
  const awayKo = koTeam(match.away);

  const [points, setPoints] = useState(1000);
  const [totals, setTotals] = useState(() => seedTotals(mid));
  const [userVote, setUserVote] = useState<Pick | null>(null);
  const [picks, setPicks] = useState<PickRow[]>([]);
  const [lastPick, setLastPick] = useState<Pick | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    setMatch(getHighlightMatch());
  }, []);

  /* localStorage 는 클라이언트에만 있어 SSR과 다를 수 있으므로 마운트 후에 읽는다 */
  useEffect(() => {
    setPoints(readPoints());
    const bag = readVotes();
    const key = String(mid);
    setTotals(bag[key] ?? seedTotals(mid));
    setUserVote(readSessionVote(mid));
    const rows = readPicks();
    setPicks(rows);
    const forMid = rows.filter((p) => p.id === mid);
    setLastPick(forMid.length ? forMid[forMid.length - 1]!.pick : null);
  }, [mid]);

  const pickCount = picks.filter((r) => r.id === mid).length;

  const pct = useMemo(() => {
    const t = totals.H + totals.D + totals.A;
    if (t <= 0) return { H: 0, D: 0, A: 0 };
    return {
      H: Math.round((100 * totals.H) / t),
      D: Math.round((100 * totals.D) / t),
      A: Math.round((100 * totals.A) / t),
    };
  }, [totals]);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  const applyVote = useCallback(
    (choice: Pick) => {
      const bag = readVotes();
      const key = String(mid);
      const cur = { ...(bag[key] ?? seedTotals(mid)) };
      const prev = readSessionVote(mid);
      if (prev === choice) return;
      if (prev) cur[prev] = Math.max(0, cur[prev] - 1);
      cur[choice] += 1;
      const next = { ...bag, [key]: cur };
      writeVotes(next);
      setTotals(cur);
      writeSessionVote(mid, choice);
      setUserVote(choice);
      showToast("투표가 반영되었습니다. (브라우저 누적 데모)");
    },
    [mid, showToast],
  );

  const onPredict = useCallback(
    (choice: Pick) => {
      const rows = [...readPicks(), { id: mid, pick: choice, t: Date.now() }];
      writePicks(rows);
      setPicks(rows);
      setLastPick(choice);
      showToast(
        "예측 저장 완료. 맞추면 +P · 틀리면 −P 는 결과 확정 후 정산(가상 포인트, 비현금).",
      );
    },
    [mid, showToast],
  );

  const aiPrompt = useMemo(() => {
    return `${match.home} 대 ${match.away} 경기의 승·무·패 쪽으로 승리 확률(%)과 예상 스코어를 한국어로 짧게 정리해 줘. (월드컵 2026)`;
  }, [match.home, match.away]);

  const onAiClick = useCallback(() => {
    onAiPreset?.(aiPrompt);
    showToast("오른쪽 제미나이 입력창에 프롬프트를 넣었습니다.");
  }, [aiPrompt, onAiPreset, showToast]);

  return (
    <div
      id="today"
      className="mb-7 p-[16px_14px_14px] 720:p-[20px_20px_18px] rounded-2xl bg-[rgba(8,14,28,0.72)] border border-[rgba(34,211,238,0.22)] shadow-[0_18px_48px_rgba(0,0,0,0.28)] max-w-full box-border"
      aria-labelledby="pred-panel-title"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-3 mb-[10px]">
        <h2 id="pred-panel-title" className="m-0 text-[17px] font-extrabold tracking-[-0.02em] text-fg-0">
          예측 · 게임화{" "}
          <span className="ml-2 px-2 py-0.5 rounded-md text-[11px] font-extrabold text-[#04131a] bg-[linear-gradient(135deg,#22d3ee,#38bdf8)] align-middle">
            가상 P
          </span>
        </h2>
        <p className="m-0 text-sm text-fg-1 text-left w-full 640:text-right 640:w-auto" aria-live="polite">
          <strong className="text-[22px] font-extrabold text-accent tracking-[-0.02em]">
            {points.toLocaleString("ko-KR")} P
          </strong>
          <span className="block mt-1 text-[11px] font-medium text-[rgba(148,163,184,0.95)] max-w-none ml-0 640:max-w-[320px] 640:ml-auto">
            시작 1,000P · 적중 + / 미적중 − (결과 연동 시) ·{" "}
            <em className="not-italic text-[#fda4af]">현금·배팅 아님</em>
          </span>
        </p>
      </div>

      <p className="mb-4 text-xs leading-[1.55] text-[rgba(203,213,225,0.88)]">
        규제 부담이 적은 <strong>예측 + 게임화</strong>로 오래 즐기는 구조를
        지향합니다. 경품·기프티콘은 별도 <strong>이벤트 공지·조건</strong> 하에만
        운영하세요.
      </p>

      <div className="grid grid-cols-1 640:grid-cols-2 gap-3">
        <section className={CARD} aria-labelledby="pred-today-title">
          <h3 id="pred-today-title" className={CARD_TITLE}>
            오늘 경기 예측하기
          </h3>
          <p className="mb-[10px] text-[15px] font-bold text-fg-0">
            {homeKo}{" "}
            <span className="font-semibold text-[rgba(148,163,184,0.95)] px-1">대</span>{" "}
            {awayKo}
          </p>
          <div className="flex flex-wrap gap-2">
            {(
              [
                ["H", "홈 승"],
                ["D", "무"],
                ["A", "원정 승"],
              ] as const
            ).map(([k, label]) => (
              <button
                key={k}
                type="button"
                className={`${PICK_BASE} p-[10px_12px] text-sm ${lastPick === k ? PICK_ON : ""}`}
                onClick={() => onPredict(k)}
              >
                {label}
              </button>
            ))}
          </div>
          <p className="mt-[10px] text-[11px] text-[rgba(148,163,184,0.85)]">
            클릭 1번으로 저장 · 이 기기 기준 누적 예측{" "}
            <strong>{pickCount}회</strong> (이 경기)
          </p>
        </section>

        <section className={CARD} aria-labelledby="pred-vote-title">
          <h3 id="pred-vote-title" className={CARD_TITLE}>
            실시간 투표
          </h3>
          <p className={CARD_SUB}>홈 / 무 / 원정 비율 (브라우저 간 누적 데모)</p>
          <div className="flex h-[10px] rounded-full overflow-hidden bg-[rgba(255,255,255,0.06)] mb-2" role="img" aria-label="투표 비율 막대">
            <span
              className="h-full min-w-[2px] transition-[width] duration-[250ms] bg-[linear-gradient(90deg,#22d3ee,#06b6d4)]"
              style={{ width: `${pct.H}%` }}
            />
            <span
              className="h-full min-w-[2px] transition-[width] duration-[250ms] bg-[linear-gradient(90deg,#94a3b8,#64748b)]"
              style={{ width: `${pct.D}%` }}
            />
            <span
              className="h-full min-w-[2px] transition-[width] duration-[250ms] bg-[linear-gradient(90deg,#a78bfa,#7c3aed)]"
              style={{ width: `${pct.A}%` }}
            />
          </div>
          <p className="mb-2 text-xs text-fg-1 [&_strong]:text-fg-0">
            홈 <strong>{pct.H}%</strong> · 무 <strong>{pct.D}%</strong> · 원정{" "}
            <strong>{pct.A}%</strong>
            {userVote ? (
              <span className="text-accent font-semibold"> · 내 선택 반영됨</span>
            ) : null}
          </p>
          <div className="flex flex-wrap gap-2">
            {(
              [
                ["H", "홈"],
                ["D", "무"],
                ["A", "원정"],
              ] as const
            ).map(([k, label]) => (
              <button
                key={k}
                type="button"
                className={`${PICK_BASE} bg-transparent p-[8px_12px] text-[13px] ${userVote === k ? PICK_ON : ""}`}
                onClick={() => applyVote(k)}
              >
                {label}
              </button>
            ))}
          </div>
        </section>

        <section
          className={`${CARD} [grid-column:auto] 640:[grid-column:1/-1]`}
          aria-labelledby="pred-rank-title"
        >
          <h3 id="pred-rank-title" className={CARD_TITLE}>
            랭킹 · 내 적중률 · 보상
          </h3>
          <ul className="m-0 pl-[18px] text-sm leading-[1.55] text-[rgba(226,232,240,0.92)] [&>li]:mb-1.5 [&>li:last-child]:mb-0">
            <li>
              <strong>오늘 적중률 1위</strong> ·{" "}
              <strong>주간 TOP 10</strong> ·{" "}
              <strong>월드컵 예측왕</strong> — 리더보드 연동 시 표시
            </li>
            <li>
              <strong>내 적중률</strong> — 누적 예측{" "}
              <strong>{picks.length}건</strong> · 실제 적중률은{" "}
              <strong>경기 결과 API</strong> 연동 후 집계 (사용자 리텐션 핵심)
            </li>
            <li>
              <strong>보상</strong> — 뱃지 · 랭킹 · 커뮤니티 명예 (기프티콘·경품은
              이벤트 한정·조건 명시)
            </li>
          </ul>
        </section>

        <section
          className={`${CARD} flex flex-wrap flex-col 640:flex-row items-start 640:items-center justify-between gap-3 [grid-column:auto] 640:[grid-column:1/-1]`}
          aria-labelledby="pred-ai-title"
        >
          <div className="flex-1 min-w-0">
            <h3 id="pred-ai-title" className={`${CARD_TITLE} mb-1`}>
              AI 승부 예측
            </h3>
            <p className={CARD_SUB}>
              오른쪽 <strong>Gemini</strong>로 승리 확률·예상 스코어 질문
            </p>
          </div>
          <button
            type="button"
            className="flex-shrink-0 p-[10px_18px] rounded-full border border-[rgba(34,211,238,0.55)] bg-[rgba(34,211,238,0.14)] text-accent font-extrabold text-[13px] cursor-pointer transition hover:bg-[rgba(34,211,238,0.24)] hover:-translate-y-px"
            onClick={onAiClick}
          >
            AI에게 이 경기 물어보기 →
          </button>
        </section>
      </div>

      {toast ? (
        <p
          className="mt-[14px] p-[10px_12px] rounded-[10px] text-xs text-[#0f172a] bg-[rgba(34,211,238,0.92)] font-semibold"
          role="status"
        >
          {toast}
        </p>
      ) : null}
    </div>
  );
}
