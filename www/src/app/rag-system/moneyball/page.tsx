import { MoneyballHeroChat } from "@/components/moneyball/MoneyballHeroChat";

export default function LessonRagSystemMoneyballPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-8 border-b border-border pb-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-fg-3">
          Lesson · RAG System
        </p>
        <h1 className="mt-2 text-2xl font-semibold uppercase tracking-[0.06em] text-fg-0">
          Moneyball Soccer RAG
        </h1>
        <p className="mt-4 text-sm text-fg-2">
          축구 데이터베이스를 검색 증강 생성(RAG)으로 연결하는 실습입니다.
        </p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-6 py-8 text-center">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">
            ⚽ Football Intelligence
          </p>
          <h2 className="mt-3 text-2xl font-bold text-fg-0 sm:text-3xl">
            축구 마스터 챗봇
          </h2>
          <p className="mt-2 text-sm text-fg-2">
            선수 기록부터 경기 전술까지, 축구에 진심인 AI에게 물어보세요.
          </p>
        </div>

        <MoneyballHeroChat className="mx-auto" />
      </div>
    </div>
  );
}