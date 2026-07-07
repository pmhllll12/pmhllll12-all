/**
 * FIFA 월드컵 2026 일정 (104경기).
 * 원본: https://github.com/openfootball/world-cup.json (2026/worldcup.json)
 * 킥오프는 JSON의 현지 시각·UTC 오프셋을 ISO로 복원한 뒤, UI에서는 Asia/Seoul 로 표시합니다.
 */
import wcRaw from "./wc2026.json";

export type WcMatch = {
  /** 표시·정렬용 정수 id (1…N) */
  id: number;
  /** 킥오프 시각 (파싱 가능한 ISO 8601, 오프셋 포함) */
  kickoffIso: string;
  round: string;
  home: string;
  away: string;
  groupOrSlot: string;
  venue: string;
};

type RawMatch = {
  round: string;
  date: string;
  time: string;
  team1: string;
  team2: string;
  group?: string;
  ground?: string;
  num?: number;
};

/** "13:00 UTC-6" | "20:30 UTC-4" → ISO 8601 with offset */
function parseKickoffToIso(date: string, timeField: string): string {
  const m = timeField.match(/^(\d{1,2}):(\d{2})\s+UTC([+-])(\d{1,2})$/);
  if (!m) {
    throw new Error(`Invalid WC time field: ${timeField}`);
  }
  const hh = m[1].padStart(2, "0");
  const mm = m[2].padStart(2, "0");
  const sign = m[3] as "+" | "-";
  const offH = String(parseInt(m[4], 10)).padStart(2, "0");
  const offsetPart = `${sign === "-" ? "-" : "+"}${offH}:00`;
  return `${date}T${hh}:${mm}:00${offsetPart}`;
}

function buildMatches(): WcMatch[] {
  const raw = (wcRaw as { matches: RawMatch[] }).matches;
  const mapped = raw.map((m, i) => ({
    id: i + 1,
    kickoffIso: parseKickoffToIso(m.date, m.time),
    round: m.round,
    home: m.team1,
    away: m.team2,
    groupOrSlot: m.group ?? (m.num != null ? `Match ${m.num}` : m.round),
    venue: m.ground ?? "",
  }));
  mapped.sort(
    (a, b) =>
      new Date(a.kickoffIso).getTime() - new Date(b.kickoffIso).getTime(),
  );
  return mapped.map((row, i) => ({ ...row, id: i + 1 }));
}

export const WC2026_MATCHES: WcMatch[] = buildMatches();

/** 본선 조별 4개국 (일정 JSON과 동일, 팀은 대회 일정 첫 등장 순) */
export type WcGroupDraw = {
  groupId: string;
  teams: string[];
};

const GROUP_IDS = [...Array(12)].map((_, i) => `Group ${String.fromCharCode(65 + i)}`);

export function getWc2026GroupDraw(): WcGroupDraw[] {
  const teamsByGroup = new Map<string, string[]>();
  for (const g of GROUP_IDS) teamsByGroup.set(g, []);

  for (const m of WC2026_MATCHES) {
    const g = m.groupOrSlot;
    if (!/^Group [A-L]$/.test(g)) continue;
    const list = teamsByGroup.get(g)!;
    const pushUnique = (t: string) => {
      if (!list.includes(t)) list.push(t);
    };
    pushUnique(m.home);
    pushUnique(m.away);
  }

  return GROUP_IDS.map((groupId) => ({
    groupId,
    teams: teamsByGroup.get(groupId) ?? [],
  }));
}

/** 본선 48개국 + 소속 조 (일정의 조별 리그와 동일) */
export type WcNationInGroup = { code: string; groupId: string };

export function getWc2026NationsFlat(): WcNationInGroup[] {
  const draw = getWc2026GroupDraw();
  const out: WcNationInGroup[] = [];
  for (const { groupId, teams } of draw) {
    for (const code of teams) out.push({ code, groupId });
  }
  out.sort((a, b) => {
    const g = a.groupId.localeCompare(b.groupId);
    if (g !== 0) return g;
    return a.code.localeCompare(b.code);
  });
  return out;
}

const kstShort = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  month: "numeric",
  day: "numeric",
  weekday: "short",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function formatMatchKstShort(iso: string): string {
  return kstShort.format(new Date(iso));
}

const kstDayKeyFmt = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Seoul",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

/** 한국시각 기준 달력일 키 (YYYY-MM-DD) */
export function kstCalendarDayKey(iso: string): string {
  return kstDayKeyFmt.format(new Date(iso));
}

/** `when` 달력의 한국시각 날짜에 킥오프하는 경기만 (시간순) */
export function getMatchesOnKstDay(when: Date = new Date()): WcMatch[] {
  const key = kstDayKeyFmt.format(when);
  return WC2026_MATCHES.filter((m) => kstCalendarDayKey(m.kickoffIso) === key).sort(
    (a, b) =>
      new Date(a.kickoffIso).getTime() - new Date(b.kickoffIso).getTime(),
  );
}

const kstTimeOnly = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

/** 네비 등 한 줄용 — 날짜 없이 시각만 (KST) */
export function formatMatchTimeKstOnly(iso: string): string {
  return kstTimeOnly.format(new Date(iso));
}

/** 현재 시각 이후 첫 경기 (모두 지났으면 마지막 경기) */
export function getHighlightMatch(now = new Date()): WcMatch {
  const t = now.getTime();
  const upcoming = WC2026_MATCHES.find((m) => new Date(m.kickoffIso).getTime() >= t);
  return upcoming ?? WC2026_MATCHES[WC2026_MATCHES.length - 1]!;
}
