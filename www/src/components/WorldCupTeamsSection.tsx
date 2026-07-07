"use client";

import { useMemo, useState } from "react";
import { koGroupLabel, koTeam } from "@/data/worldCup2026Ko";
import { getWc2026NationsFlat } from "@/data/worldCup2026Schedule";
import notablePlayers from "@/data/wc2026NotablePlayers.json";

type NotablePlayerRow = { name: string; club?: string };

const NOTABLE = notablePlayers as Record<string, NotablePlayerRow[]>;

export default function WorldCupTeamsSection() {
  const nations = useMemo(() => getWc2026NationsFlat(), []);
  const [q, setQ] = useState("");

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return nations;
    return nations.filter(({ code }) => {
      const ko = koTeam(code).toLowerCase();
      const en = code.toLowerCase();
      return ko.includes(s) || en.includes(s);
    });
  }, [nations, q]);

  return (
    <section
      id="teams"
      className="[scroll-margin-top:96px] p-[48px_0_72px] border-t border-[rgba(148,163,184,0.12)]"
      aria-labelledby="wc-teams-heading"
    >
      <div className="max-w-[960px] w-full mx-auto box-border">
        <h2 id="wc-teams-heading" className="mb-2 text-[clamp(1.35rem,2.5vw,1.6rem)] font-extrabold tracking-[-0.02em] text-fg-0">
          팀
        </h2>
        <p className="mb-5 max-w-[720px] text-sm leading-[1.6] text-fg-2">
          본선에 나오는 선수는 모두 아래 <strong>국가 대표팀</strong> 이름으로 출전합니다.
          표의 선수·클럽은 <strong>참고용 예시</strong>이며, 2026년 최종 엔트리는 FIFA 및
          각 축구협회 발표를 따릅니다.
        </p>

        <label className="flex flex-col gap-[6px] mb-[22px] max-w-[360px]">
          <span className="text-xs font-bold text-[rgba(226,232,240,0.85)]">대표팀 검색</span>
          <input
            type="search"
            className="text-sm p-[10px_14px] rounded-[10px] border border-[rgba(0,229,255,0.22)] bg-[rgba(6,10,18,0.85)] text-fg-0 placeholder:text-[rgba(148,163,184,0.65)] focus:outline-none focus:border-[rgba(0,229,255,0.45)] focus:shadow-[0_0_0_2px_rgba(0,229,255,0.12)]"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="예: 대한민국, Brazil…"
            autoComplete="off"
          />
        </label>

        <ul className="m-0 p-0 list-none grid grid-cols-1 480:grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-[14px]">
          {filtered.map(({ code, groupId }) => {
            const examples = NOTABLE[code] ?? [];
            return (
              <li
                key={code}
                className="p-[14px_16px_16px] rounded-xl border border-[rgba(148,163,184,0.14)] bg-[rgba(8,14,22,0.55)]"
              >
                <div className="flex items-baseline justify-between gap-3 mb-2">
                  <span className="text-base font-extrabold text-fg-0">{koTeam(code)}</span>
                  <span className="flex-shrink-0 text-xs font-bold text-accent tracking-[0.06em]">
                    {koGroupLabel(groupId)}
                  </span>
                </div>
                <p className="mb-[10px] text-[13px] text-[rgba(226,232,240,0.88)]">
                  소속: <strong>{koTeam(code)} 대표팀</strong>
                </p>
                {examples.length > 0 ? (
                  <>
                    <p className="mb-[6px] text-[11px] font-bold uppercase tracking-[0.08em] text-[rgba(148,163,184,0.9)]">
                      참고용 주요 선수 예시
                    </p>
                    <ul className="m-0 p-0 list-none flex flex-col gap-[6px]">
                      {examples.map((p) => (
                        <li key={`${code}-${p.name}`} className="flex flex-col gap-0.5 text-[13px] leading-[1.35]">
                          <span className="font-bold text-[rgba(241,245,249,0.96)]">{p.name}</span>
                          {p.club ? (
                            <span className="text-xs font-medium text-[rgba(148,163,184,0.95)]">{p.club}</span>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <p className="m-0 text-xs leading-[1.45] text-[rgba(148,163,184,0.88)]">
                    예시 명단은 준비 중입니다. 선수는 모두 위 대표팀 소속으로 출전합니다.
                  </p>
                )}
              </li>
            );
          })}
        </ul>

        {filtered.length === 0 ? (
          <p className="mt-4 text-sm text-[rgba(248,250,252,0.75)]">검색 결과가 없습니다.</p>
        ) : null}
      </div>
    </section>
  );
}
