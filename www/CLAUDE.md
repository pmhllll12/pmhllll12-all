# 프론트엔드 (`www`) — LLM 코딩 지침

Next.js (App Router) + Tailwind v4 UI. 개발·프리뷰 포트는 **3000 고정** ([`package.json`](package.json) 스크립트, [`next.config.ts`](next.config.ts)).

공통 4원칙 전문 ---> [`../_docs/CLAUDE.md`](../_docs/CLAUDE.md)  
모노레포 지도 ---> [`../CLAUDE.md`](../CLAUDE.md)

---

## 실행

```powershell
cd www
npm install   # 최초 1회
npm run dev
```

- 브라우저: `http://localhost:3000` (또는 터미널에 표시된 Network URL)
- `ERR_CONNECTION_REFUSED`: dev 서버가 꺼진 상태 — 터미널을 켠 채 유지한다.

상세 ---> [`../_docs/DEV_SERVER.md`](../_docs/DEV_SERVER.md)

---

## API 프록시

[`next.config.ts`](next.config.ts) 의 `rewrites()` 가 아래를 백엔드(`API_PORT`, 기본 8000)로 프록시한다.

| 경로 | 용도 |
|------|------|
| `/api/*` (예: `/api/titanic/...`) | 타이타닉 등 API |
| `/chat`, `/signup`, `/ping`, `/weather`, `/db-check` | 공통 API |

- 프론트 `fetch`는 **상대 경로** 우선: `fetch("/api/titanic/smith/chat", …)`.
- `NEXT_PUBLIC_API_BASE`는 LAN·정적 빌드에서만 필요 ([`.env.example`](.env.example)).

Docker: 브라우저는 **`localhost:3000`만** 호출하고, gateway가 백엔드로 넘긴다.

---

## 주요 페이지

| 경로 | 파일 |
|------|------|
| 레슨 셸 (레이아웃) | [`src/app/(site)/lesson/layout.tsx`](src/app/(site)/lesson/layout.tsx) |
| 타이타닉 업로드 | [`src/components/Titanic.tsx`](src/components/Titanic.tsx) |
| 스미스 채팅 | [`src/components/TitanicSmith.tsx`](src/components/TitanicSmith.tsx) |
| 루트 레이아웃 / 라우트 | [`src/app/layout.tsx`](src/app/layout.tsx), `src/app/**/page.tsx` (App Router 파일 기반 라우팅) |

---

## React 규칙 (정본)

폼·상태·보안 UX ---> [`_docs/react_rules.md`](_docs/react_rules.md)

요약:

- 관련 필드는 **단일 객체 state** 또는 제출 시 **`FormData`**.
- 비밀번호·PII를 `alert` / `console.log`에 넣지 않는다.
- 요청 범위 밖 UI 리팩터·포맷 정리 금지.

---

## Docker

```powershell
cd ..
docker compose up --build -d
```

프론트 이미지는 `npm run build` 후 `npm run start` (`next start`, 포트 3000, 컨테이너 내부).

## 다크모드

지침 ---> [`_docs/darkmode-spec.md`](_docs/darkmode-spec.md)

---

## Lint / Format

ESLint(`eslint.config.mjs`) + Prettier(`.prettierrc.json`)가 `npm run lint` /
`npm run format`, 커밋 전 `.pre-commit-config.yaml`, PR마다 `.github/workflows/lint.yml`로
강제된다. 상세·함정 ---> [`_docs/linting.md`](_docs/linting.md) 