/**
 * 월드컵 일정 UI용 한국어 표기 (원본 JSON은 영문).
 */
import type { WcMatch } from "./worldCup2026Schedule";

const TEAM_KO: Record<string, string> = {
  Algeria: "알제리",
  Argentina: "아르헨티나",
  Australia: "호주",
  Austria: "오스트리아",
  Belgium: "벨기에",
  "Bosnia & Herzegovina": "보스니아 헤르체고비나",
  Brazil: "브라질",
  Canada: "캐나다",
  "Cape Verde": "까보베르데",
  Colombia: "콜롬비아",
  Croatia: "크로아티아",
  Curaçao: "퀴라소",
  "Czech Republic": "체코",
  "DR Congo": "콩고 민주 공화국",
  Ecuador: "에콰도르",
  Egypt: "이집트",
  England: "잉글랜드",
  France: "프랑스",
  Germany: "독일",
  Ghana: "가나",
  Haiti: "아이티",
  Iran: "이란",
  Iraq: "이라크",
  "Ivory Coast": "코트디부아르",
  Japan: "일본",
  Jordan: "요르단",
  Mexico: "멕시코",
  Morocco: "모로코",
  Netherlands: "네덜란드",
  "New Zealand": "뉴질랜드",
  Norway: "노르웨이",
  Panama: "파나마",
  Paraguay: "파라과이",
  Portugal: "포르투갈",
  Qatar: "카타르",
  "Saudi Arabia": "사우디아라비아",
  Scotland: "스코틀랜드",
  Senegal: "세네갈",
  "South Africa": "남아프리카 공화국",
  "South Korea": "대한민국",
  Spain: "스페인",
  Sweden: "스웨덴",
  Switzerland: "스위스",
  Tunisia: "튀니지",
  Turkey: "튀르키예",
  USA: "미국",
  Uruguay: "우루과이",
  Uzbekistan: "우즈베키스탄",
};

const VENUE_KO: Record<string, string> = {
  Atlanta: "애틀랜타",
  "Boston (Foxborough)": "보스턴(폭스버러)",
  "Dallas (Arlington)": "댈러스(알링턴)",
  "Guadalajara (Zapopan)": "과달라하라(사포판)",
  Houston: "휴스턴",
  "Kansas City": "캔자스시티",
  "Los Angeles (Inglewood)": "로스앤젤레스(잉글우드)",
  "Mexico City": "멕시코시티",
  "Miami (Miami Gardens)": "마이애미(마이애미가든스)",
  "Monterrey (Guadalupe)": "몬테레이(과달루페)",
  "New York/New Jersey (East Rutherford)": "뉴욕·뉴저지(이스트러더포드)",
  Philadelphia: "필라델피아",
  "San Francisco Bay Area (Santa Clara)": "샌프란시스코 베이(샌타클래라)",
  Seattle: "시애틀",
  Toronto: "토론토",
  Vancouver: "밴쿠버",
};

function koBracketSlot(name: string): string | null {
  const w = name.match(/^W(\d+)$/);
  if (w) return `${w[1]}번 경기 승자`;
  const l = name.match(/^L(\d+)$/);
  if (l) return `${l[1]}번 경기 패자`;
  const rank = name.match(/^([12])([A-L])$/);
  if (rank) {
    const g = rank[2];
    return rank[1] === "1" ? `${g}조 1위` : `${g}조 2위`;
  }
  const third = name.match(/^3((?:[A-L]\/)+[A-L])$/);
  if (third) {
    const letters = third[1].split("/");
    return `${letters.join("·")}조 3위`;
  }
  return null;
}

/** 국가·대진 슬롯명 → 한국어 */
export function koTeam(name: string): string {
  return TEAM_KO[name] ?? koBracketSlot(name) ?? name;
}

/** 경기장(영문 그대로) → 한국어 */
export function koVenue(venue: string): string {
  if (!venue) return "";
  return VENUE_KO[venue] ?? venue;
}

/** "Group A" → "A조" */
export function koGroupLabel(group: string): string {
  const m = group.match(/^Group ([A-L])$/);
  if (m) return `${m[1]}조`;
  return group;
}

/** 라운드 영문 → 한국어 */
export function koRound(round: string): string {
  switch (round) {
    case "Final":
      return "결승";
    case "Match for third place":
      return "3·4위전";
    case "Semi-final":
      return "준결승";
    case "Quarter-final":
      return "8강";
    case "Round of 16":
      return "16강";
    case "Round of 32":
      return "32강";
    default: {
      const md = round.match(/^Matchday (\d+)$/);
      if (md) return `조별리그 ${md[1]}차전`;
      return round;
    }
  }
}

/** 모달 한 줄 메타(조·라운드·경기번호·경기장) */
export function koMatchMetaLine(m: WcMatch): string {
  const venue = koVenue(m.venue);
  const vSuffix = venue ? ` · ${venue}` : "";

  if (m.groupOrSlot.startsWith("Group ")) {
    return `${koGroupLabel(m.groupOrSlot)}${vSuffix}`;
  }

  const numMatch = m.groupOrSlot.match(/^Match (\d+)$/);
  if (numMatch) {
    return `${koRound(m.round)} · 제${numMatch[1]}경기${vSuffix}`;
  }

  return `${koRound(m.round)}${vSuffix}`;
}
