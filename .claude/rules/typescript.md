---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

## TypeScript 규칙 (`www` 실사용 패턴 기준)

- strict mode 필수 (`tsconfig.json`의 `strict: true` 유지)
- `any` 사용 금지 — `@typescript-eslint/no-explicit-any`가 `error`로 설정되어 있어 위반 시 빌드/pre-commit이 막힌다. 타입을 모르면 `unknown`을 쓰고 좁혀서 사용한다.
- 인터페이스보다 타입 별칭(`type`) 선호 — `www/src`에는 `interface` 선언이 없고 전부 `type`이다.
- `enum` 대신 문자열 리터럴 유니온을 쓴다.
  ```ts
  type Status = { type: "idle" | "loading" | "ok" | "error"; message: string };
  ```
- 컴포넌트 props 타입은 `<컴포넌트명>Props` 네이밍의 `type`으로 선언하고, 컴포넌트 바로 위에 둔다.
  ```ts
  type HeroProps = {
    onGeminiPreset?: (text: string) => void;
    showPrediction?: boolean;
  };
  ```
- 컴포넌트는 `React.FC` 없이 `export default function ComponentName({ ...props }: XxxProps)` 형태로 작성한다.
- `useState`는 초기값에서 타입 추론이 안 되는 경우(빈 배열, `null` 초기값 등) 제네릭을 명시한다: `useState<ChatMessage[]>([])`, `useState<string | null>(null)`.
- `catch` 블록은 변수에 타입을 직접 쓰지 않는다(`catch (err)`, `catch (e)`) — strict mode에서 이미 `unknown`으로 추론된다. 내부에서 좁혀 쓴다.
- non-null assertion(`!`)은 최소한으로만 쓴다.
- `console.*` 직접 호출 금지 — `no-console`이 `error`로 설정되어 있다.
- 사용하지 않는 변수/임포트를 남기지 않는다 — `no-unused-vars`가 `error`로 설정되어 있다.
- import는 상대 경로 대신 `@/` 경로 별칭을 사용한다(`tsconfig.json`의 `paths` 참고).
