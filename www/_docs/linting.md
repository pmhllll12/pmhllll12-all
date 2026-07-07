# Lint / Format 하네스

이전에는 `package.json`에 `"lint": "eslint ."`만 있었고 ESLint·Prettier가 실제로는
설치돼 있지 않았다 (`devDependencies`에 없었음). 이제 둘 다 실제로 동작한다.

## 설정 파일

- [`eslint.config.mjs`](../eslint.config.mjs) — `eslint-config-next`의 flat config +
  `no-console: error`, `@typescript-eslint/no-explicit-any: error`,
  `@typescript-eslint/no-unused-vars: error`.
- [`.prettierrc.json`](../.prettierrc.json) — `semi: false`, `singleQuote: true`,
  `tabWidth: 2`, `printWidth: 80`.

## FlatCompat 함정 (다시 겪지 않기 위한 기록)

`eslint-config-next`(16.x)는 이미 **네이티브 flat config 배열**을 내보낸다. 이걸
`@eslint/eslintrc`의 `FlatCompat`(구 `.eslintrc` 브리지)으로 또 감싸면
`eslint-plugin-react`의 자기참조 플러그인 객체 때문에
`Converting circular structure to JSON`으로 깨진다 — 실제 검증 에러가 아니라
에러 메시지를 만드는 중에 직렬화가 죽는 것이라 원인이 안 보인다. **FlatCompat 없이
`eslint-config-next/core-web-vitals`를 직접 import**해서 해결했다.

## 규칙 강도 조정

`eslint-config-next`의 최신 recommended에 새로 포함된
`react-hooks/set-state-in-effect`가, "마운트 후 `localStorage`를 읽어 `setState`"하는
기존 패턴 8곳(`useTheme.ts`, `Nav.tsx`, `GeminiChat.tsx` 등)을 전부 `error`로 잡아
도입 즉시 전부 커밋이 막혔다. 버그가 아니라 더 엄격한 권장 스타일이라 일단 `warn`으로
낮췄다 — 점진적으로 `useState(() => ...)` 형태의 lazy init으로 정리되면 다시 `error`로
올린다.

## 알려진 실제 위반

`no-console`이 `LoginModal.tsx:80`, `:314`에서 실제 `console.*` 호출을 잡아냈다.
[`CLAUDE.md`](../CLAUDE.md)의 "비밀번호·PII를 alert/console.log에 넣지 않는다" 규칙과
관련될 수 있어 별도 확인이 필요하다 — 이 작업(하네스 설정)의 범위 밖이라 고치지 않았다.

## 실행

```powershell
cd www
npm install        # eslint/prettier 등 devDependencies 설치 (최초 1회)
npm run lint        # eslint .
npm run format       # prettier --check .
```

## CI / pre-commit

`www`는 서브모듈(별도 저장소 `cloud.pmhllll12.www`)이라 `.github/workflows/lint.yml`과
`.pre-commit-config.yaml`이 여기 자체에 있다 (저장소 루트에 두면 www 자신의 PR에서
실행되지 않는다). pre-commit 설치: `npm install && pip install pre-commit && pre-commit install` (www/ 안에서).
