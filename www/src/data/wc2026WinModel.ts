/**
 * 2026 본선 참가국별 «우승 확률» 추정치.
 * - 역대 월드컵 우승·준우승·4강·8강 등 누적 실적과 본선 경험을 가중한 단순 휴리스틱입니다.
 * - 실제 배당률·FIFA 랭킹·전력 모델과 무관하며 참고용입니다.
 */
import { getWc2026NationsFlat } from "./worldCup2026Schedule";

/** 내부 가중치 (합 = 임의 스케일, 이후 %로 정규화) */
export const WC_WIN_PRIOR: Record<string, number> = {
  Brazil: 185,
  Germany: 162,
  Argentina: 158,
  France: 152,
  Spain: 118,
  England: 112,
  Portugal: 102,
  Netherlands: 96,
  Belgium: 93,
  Uruguay: 78,
  Croatia: 72,
  Mexico: 58,
  USA: 54,
  Colombia: 52,
  Switzerland: 48,
  Morocco: 46,
  Japan: 44,
  Senegal: 40,
  Sweden: 36,
  "South Korea": 38,
  Australia: 32,
  Turkey: 34,
  Canada: 33,
  Ecuador: 30,
  Iran: 28,
  "Saudi Arabia": 26,
  Qatar: 28,
  Austria: 30,
  Scotland: 28,
  Norway: 32,
  Egypt: 26,
  Tunisia: 18,
  Algeria: 22,
  Ghana: 26,
  "Ivory Coast": 28,
  Paraguay: 22,
  Panama: 16,
  Haiti: 10,
  Jordan: 12,
  Uzbekistan: 14,
  Iraq: 12,
  "DR Congo": 14,
  "New Zealand": 12,
  "South Africa": 18,
  "Czech Republic": 36,
  "Bosnia & Herzegovina": 20,
  Curaçao: 8,
  "Cape Verde": 10,
};

const DEFAULT_PRIOR = 9;

export type WinProbRow = {
  code: string;
  /** 0–100, 소수 첫째 자리까지 합계 100.0 */
  pct: number;
};

/** 가장 큰 나머지를 가진 항목에 남는 0.1%를 배분해 합계를 100.0으로 맞춤 */
export function getWinProbabilities(): WinProbRow[] {
  const codes = getWc2026NationsFlat().map((n) => n.code);
  const weights = codes.map((code) => ({
    code,
    w: WC_WIN_PRIOR[code] ?? DEFAULT_PRIOR,
  }));
  const sumW = weights.reduce((a, b) => a + b.w, 0);
  const raw = weights.map(({ code, w }) => ({
    code,
    rawPct: (w / sumW) * 100,
  }));
  const tenths = raw.map((r) => ({
    code: r.code,
    t: Math.floor(r.rawPct * 10 + 1e-9),
    frac: r.rawPct * 10 - Math.floor(r.rawPct * 10 + 1e-9),
  }));
  let totalTenths = tenths.reduce((a, b) => a + b.t, 0);
  let missing = 1000 - totalTenths;
  const order = [...tenths]
    .map((r, i) => ({ i, frac: r.frac }))
    .sort((a, b) => b.frac - a.frac);
  const extra = new Map<string, number>();
  for (let k = 0; k < missing; k++) {
    const code = tenths[order[k % order.length]!.i]!.code;
    extra.set(code, (extra.get(code) ?? 0) + 1);
  }
  return tenths
    .map((r) => ({
      code: r.code,
      pct: (r.t + (extra.get(r.code) ?? 0)) / 10,
    }))
    .sort((a, b) => b.pct - a.pct);
}

export function getSouthKoreaWinPct(): number {
  return getWinProbabilities().find((r) => r.code === "South Korea")?.pct ?? 0;
}
