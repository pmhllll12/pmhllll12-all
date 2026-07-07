import VisionDetect from "@/components/VisionDetect";

export const revalidate = 60;

export default function LessonVisionDetect() {
  return (
    <article className="max-w-[720px]">
      <p className="mb-2 text-[11px] font-extrabold tracking-[0.16em] uppercase text-[#94a3b8]">
        LESSON
      </p>
      <h1 className="mb-5 text-[clamp(1.5rem,4vw,2rem)] font-extrabold tracking-[-0.02em] text-[#0f172a]">
        객체 탐지 — 얼굴 인식
      </h1>
      <div className="rounded-xl overflow-hidden border border-[#e2e8f0]">
        <VisionDetect />
      </div>
    </article>
  );
}
