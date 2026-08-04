import { ReceiptOcrPanel } from "@/components/receipt/ReceiptOcrPanel";

export default function LessonRagSystemReceiptPage() {
  return (
    <div className="flex h-full flex-col">
      <div className="mb-8 border-b border-border pb-8">
        <p className="text-[10px] uppercase tracking-[0.3em] text-fg-3">
          Lesson · RAG System
        </p>
        <h1 className="mt-2 text-2xl font-semibold uppercase tracking-[0.06em] text-fg-0">
          영수증
        </h1>
        <p className="mt-4 text-sm text-fg-2">
          S3 receipts/ 폴더의 영수증 이미지를 Gemini OCR로 읽어 표로 보여줍니다.
        </p>
      </div>

      <ReceiptOcrPanel />
    </div>
  );
}
