"use client";

import { useMemo } from "react";
import { koGroupLabel, koTeam } from "@/data/worldCup2026Ko";
import { getWc2026GroupDraw } from "@/data/worldCup2026Schedule";

export default function WorldCupGroupsSection() {
  const groups = useMemo(() => getWc2026GroupDraw(), []);

  return (
    <section
      id="groups"
      className="[scroll-margin-top:96px] p-[48px_0_64px] border-t border-[rgba(148,163,184,0.12)]"
      aria-labelledby="wc-groups-heading"
    >
      <div className="max-w-[960px] w-full mx-auto box-border">
        <h2 id="wc-groups-heading" className="mb-2 text-[clamp(1.35rem,2.5vw,1.6rem)] font-extrabold tracking-[-0.02em] text-fg-0">
          조 편성
        </h2>
        <p className="mb-7 max-w-[640px] text-sm leading-[1.55] text-fg-2">
          FIFA 월드컵 2026 본선 12개 조 · 조별 리그 일정 데이터와 동일한 팀 구성입니다.
        </p>
        <div className="grid grid-cols-1 480:grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-[14px]">
          {groups.map(({ groupId, teams }) => (
            <article
              key={groupId}
              className="m-0 p-[14px_16px_16px] rounded-xl border border-[rgba(0,229,255,0.18)] bg-[rgba(8,14,22,0.65)] shadow-[0_8px_28px_rgba(0,0,0,0.25)]"
            >
              <h3 className="mb-3 text-[15px] font-extrabold text-accent tracking-[0.04em]">
                {koGroupLabel(groupId)}
              </h3>
              <ol className="m-0 p-[0_0_0_18px] flex flex-col gap-[6px] text-sm font-semibold text-fg-0 leading-[1.35]">
                {teams.map((t) => (
                  <li key={t} className="pl-0.5">
                    {koTeam(t)}
                  </li>
                ))}
              </ol>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
