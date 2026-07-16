import { CrawlerScraperPanel } from "@/components/crawler/CrawlerScraperPanel";

export default function LessonRagSystemCrawlerPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-8 border-b border-border pb-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-fg-3">
          Lesson · RAG System
        </p>
        <h1 className="mt-2 text-2xl font-semibold uppercase tracking-[0.06em] text-fg-0">
          크롤러 · 스크래퍼
        </h1>
        <p className="mt-4 text-sm text-fg-2">
          사이트 주소와 자연어 명령을 입력하면 대상을 이해해 크롤링/스크래핑을 실행합니다.
        </p>
      </div>

      <CrawlerScraperPanel />
    </div>
  );
}
