export const revalidate = 60;

export default function LessonOverview() {
  return (
    <article className="max-w-[960px] mx-auto text-[#1e293b]">
      <div className="grid grid-cols-1 800:grid-cols-[minmax(0,1fr)_minmax(220px,280px)] gap-[clamp(24px,4vw,40px)] items-start">
        <div className="min-w-0">
          <p className="mb-2 text-[11px] font-bold tracking-[0.2em] uppercase text-[#94a3b8]">
            LESSON
          </p>
          <h1 className="mb-4 text-[clamp(1.65rem,3.5vw,2.15rem)] font-extrabold tracking-[-0.03em] leading-[1.2] text-[#0f172a]">
            타이타닉 모델 분석
          </h1>
          <p className="mb-7 text-[15px] leading-[1.75] text-[#475569]">
            본 수업은 타이타닉 침몰 사건을 데이터 분석과 머신러닝 관점에서 살펴보고,
            승객 정보를 바탕으로 생존 여부를 예측하는 분류 모델을 다룹니다.
          </p>

          <section className="mb-7" aria-labelledby="lesson-goals">
            <h2 id="lesson-goals" className="mb-3 text-[17px] font-extrabold text-[#0f172a]">
              학습 목표
            </h2>
            <ul className="pl-5 text-[15px] leading-[1.7] text-[#334155] [&>li]:mb-1.5">
              <li>데이터 수집 및 전처리 기술 습득</li>
              <li>탐색적 데이터 분석(EDA) 실습</li>
              <li>분류 모델 개발 및 성능 평가</li>
              <li>실제 데이터 기반 인사이트 도출</li>
            </ul>
          </section>

          <section className="mb-7" aria-labelledby="lesson-topics">
            <h2 id="lesson-topics" className="mb-3 text-[17px] font-extrabold text-[#0f172a]">
              주요 내용
            </h2>
            <ul className="pl-5 text-[15px] leading-[1.7] text-[#334155] [&>li]:mb-1.5">
              <li>타이타닉 탑승객 데이터셋 분석</li>
              <li>성별, 연령, 좌석 등급에 따른 생존율 분석</li>
              <li>로지스틱 회귀 모델을 이용한 생존 예측</li>
              <li>모델 성능 평가 및 해석</li>
            </ul>
          </section>
        </div>

        <aside
          className="order-[-1] 800:order-none rounded-2xl p-[20px_18px] bg-[#f8fafc] border border-[#e2e8f0] shadow-[0_4px_24px_rgba(15,23,42,0.06)] flex flex-col gap-[18px]"
          aria-label="타이타닉 수업 요약"
        >
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              🚢
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">Titanic</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">1912년 침몰</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">1,500명 이상 사망</p>
            </div>
          </div>
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              📊
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">데이터</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">2,224명 탑승객</p>
            </div>
          </div>
          <div className="flex gap-[14px] items-start">
            <span
              className="shrink-0 w-10 h-10 flex items-center justify-center text-xl bg-white rounded-xl border border-[#e2e8f0]"
              aria-hidden
            >
              🔍
            </span>
            <div>
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">데이터 분석</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">EDA · 시각화</p>
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
              <p className="mb-1 text-sm font-extrabold text-[#0f172a]">머신러닝 모델</p>
              <p className="text-[13px] text-[#64748b] leading-[1.45]">분류 · 평가</p>
            </div>
          </div>
        </aside>
      </div>

      <p className="mt-7 p-[14px_16px] rounded-xl text-[13px] leading-[1.55] text-[#475569] bg-[#f1f5f9] border border-[#e2e8f0]">
        실습 화면은 사이드바의 <strong>「1. 데이터 수집 및 실습」</strong>, 승객 표는{" "}
        <strong>「2. 승객 목록」</strong>, 스미스 선장 API는 <strong>「3. 스미스 선장과 대화하기」</strong>에서
        열 수 있습니다.
      </p>
    </article>
  );
}
