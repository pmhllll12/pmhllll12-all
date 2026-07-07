export const revalidate = 60;

export default function LessonVision() {
  return (
    <article className="max-w-[960px] mx-auto text-[#1e293b]">
      <div className="grid grid-cols-1 800:grid-cols-[minmax(0,1fr)_minmax(220px,280px)] gap-[clamp(24px,4vw,40px)] items-start">
        <div className="min-w-0">
          <p className="mb-2 text-[11px] font-bold tracking-[0.2em] uppercase text-[#94a3b8]">
            LESSON
          </p>
          <h1 className="mb-4 text-[clamp(1.65rem,3.5vw,2.15rem)] font-extrabold tracking-[-0.03em] leading-[1.2] text-[#0f172a]">
            이미지 분석 (Vision)
          </h1>
          <p className="mb-7 text-[15px] leading-[1.75] text-[#475569]">
            본 수업은 업로드한 이미지를 Gemini 멀티모달 모델로 분석해 설명(caption)과
            태그를 생성하고, 결과를 데이터베이스에 저장·조회하는 컴퓨터 비전 파이프라인을
            다룹니다.
          </p>

          <section className="mb-7" aria-labelledby="lesson-goals">
            <h2 id="lesson-goals" className="mb-3 text-[17px] font-extrabold text-[#0f172a]">
              학습 목표
            </h2>
            <ul className="pl-5 text-[15px] leading-[1.7] text-[#334155] [&>li]:mb-1.5">
              <li>이미지 업로드 → 멀티모달 모델 분석 파이프라인 이해</li>
              <li>캡션·태그 생성 결과의 구조화 및 저장</li>
              <li>분석 로그 조회 API 설계</li>
            </ul>
          </section>

          <section className="mb-7" aria-labelledby="lesson-topics">
            <h2 id="lesson-topics" className="mb-3 text-[17px] font-extrabold text-[#0f172a]">
              주요 내용
            </h2>
            <ul className="pl-5 text-[15px] leading-[1.7] text-[#334155] [&>li]:mb-1.5">
              <li>Gemini 멀티모달로 이미지 설명·태그 생성</li>
              <li>분석 결과 pgvector 저장</li>
              <li>최근 분석 로그 최신순 조회</li>
            </ul>
          </section>
        </div>

        <aside
          className="order-[-1] 800:order-none rounded-2xl p-[20px_18px] bg-[#f8fafc] border border-[#e2e8f0] shadow-[0_4px_24px_rgba(15,23,42,0.06)] flex flex-col gap-[18px]"
          aria-label="vision 수업 요약"
        >
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              🖼️
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">Vision</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">이미지 캡션·태그 분석</p>
            </div>
          </div>
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              🤖
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">모델</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">Gemini 멀티모달</p>
            </div>
          </div>
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              💾
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">저장소</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">pgvector · 분석 로그</p>
            </div>
          </div>
        </aside>
      </div>

      <p className="mt-7 p-[14px_16px] rounded-xl text-[13px] leading-[1.55] text-[#475569] bg-[#f1f5f9] border border-[#e2e8f0]">
        실습 화면은 준비 중입니다. 백엔드 API는 <strong>POST /api/vision/analyze</strong>
        (이미지 업로드·분석)와 <strong>GET /api/vision/logs</strong>(분석 로그 조회)로 제공됩니다.
      </p>
    </article>
  );
}
