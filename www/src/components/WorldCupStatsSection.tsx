"use client";

import { useMemo } from "react";
import { koTeam } from "@/data/worldCup2026Ko";
import { getSouthKoreaWinPct, getWinProbabilities } from "@/data/wc2026WinModel";

export default function WorldCupStatsSection() {
  const rows = useMemo(() => getWinProbabilities(), []);
  const krPct = useMemo(() => getSouthKoreaWinPct(), []);

  return (
    <section
      id="stats"
      className="[scroll-margin-top:96px] p-[48px_0_80px] border-t border-[rgba(148,163,184,0.12)]"
      aria-labelledby="wc-stats-heading"
    >
      <div className="max-w-[720px] w-full mx-auto box-border">
        <h2 id="wc-stats-heading" className="mb-5 text-[clamp(1.35rem,2.5vw,1.6rem)] font-extrabold tracking-[-0.02em] text-fg-0">
          통계
        </h2>

        <div
          className="mb-6 p-[16px_18px] rounded-xl border border-[rgba(148,163,184,0.16)] bg-[rgba(6,10,18,0.55)]"
          role="region"
          aria-label="역대 월드컵 요약"
        >
          <h3 className="mb-[10px] text-sm font-extrabold text-accent">역대 본선 기준 요약</h3>
          <ul className="m-0 pl-[1.1rem] text-[13px] leading-[1.65] text-[rgba(226,232,240,0.9)] [&>li+li]:mt-2">
            <li>
              <strong>우승 횟수</strong>: 브라질 5회, 독일·이탈리아 각 4회, 아르헨티나 3회,
              프랑스·우루과이 각 2회, 잉글랜드·스페인 각 1회(2026 시점 역대 통계).
            </li>
            <li>
              <strong>대한민국</strong>: 1954년 첫 본선 이후 다수 회 출전, 2002년 한·일
              월드컵 4강, 그 외 주로 16강·조별 리그 단계.
            </li>
            <li>
              아래 비율은 위와 같은 <strong>누적 성적·본선 경험</strong>을 가중한 단순
              모델의 <strong>참고용 추정치</strong>이며, 실제 우승 확률·배당·FIFA
              랭킹과 다릅니다.
            </li>
          </ul>
        </div>

        <div
          className="mb-7 p-[18px_20px] rounded-2xl border border-[rgba(0,229,255,0.35)] bg-[linear-gradient(135deg,rgba(0,229,255,0.12),rgba(8,14,22,0.9))]"
          role="status"
        >
          <p className="mb-[6px] text-[13px] font-bold text-[rgba(226,232,240,0.88)]">모델 기준 대한민국 우승 확률</p>
          <p className="m-0 flex items-baseline gap-1">
            <span className="text-[clamp(2rem,5vw,2.75rem)] font-black [font-variant-numeric:tabular-nums] text-accent tracking-[-0.03em]">
              {krPct.toFixed(1)}
            </span>
            <span className="text-xl font-extrabold text-[rgba(226,232,240,0.85)]">%</span>
          </p>
        </div>

        <h3 className="mb-[6px] text-[15px] font-extrabold text-fg-0">참가국별 우승 확률 추정 (%)</h3>
        <p className="mb-3 text-xs text-[rgba(148,163,184,0.95)]">
          2026 본선 48개 대표팀 · 합계 100.0% · 소수 첫째 자리
        </p>

        <div className="overflow-x-auto rounded-xl border border-[rgba(148,163,184,0.14)]">
          <table className="w-full border-collapse text-[13px] [&_thead]:bg-[rgba(8,14,22,0.95)] [&_th]:p-[10px_12px] [&_th]:text-left [&_th]:font-extrabold [&_th]:text-[rgba(226,232,240,0.92)] [&_th]:border-b [&_th]:border-[rgba(148,163,184,0.15)] [&_td]:p-[8px_12px] [&_td]:border-b [&_td]:border-[rgba(148,163,184,0.08)] [&_td]:text-[rgba(241,245,249,0.92)] [&_tbody_tr:nth-child(even)_td]:bg-[rgba(255,255,255,0.02)]">
            <thead>
              <tr>
                <th scope="col" className="pr-[6px] 520:pr-3">
                  순위
                </th>
                <th scope="col">국가</th>
                <th scope="col">확률</th>
                <th scope="col" className="w-[38%] min-w-[120px]">
                  비교
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => {
                const max = rows[0]?.pct ?? 1;
                const w = max > 0 ? Math.min(100, (r.pct / max) * 100) : 0;
                const isKr = r.code === "South Korea";
                return (
                  <tr key={r.code} className={isKr ? "[&_td]:bg-[rgba(0,229,255,0.08)] [&_td]:font-bold" : ""}>
                    <td className="pr-[6px] 520:pr-3">{i + 1}</td>
                    <td>{koTeam(r.code)}</td>
                    <td className="[font-variant-numeric:tabular-nums] whitespace-nowrap">{r.pct.toFixed(1)}%</td>
                    <td className="align-middle">
                      <span
                        className="block h-[6px] rounded min-w-1 bg-[linear-gradient(90deg,rgba(0,229,255,0.55),rgba(34,211,238,0.25))]"
                        style={{ width: `${w}%` }}
                        aria-hidden
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
