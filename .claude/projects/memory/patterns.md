# 코드 패턴

주제별 코드 패턴 메모. 새 패턴을 확인하면 이 파일에 누적한다.

## `www` (Next.js / TypeScript)

이번 세션에서 `www/src`를 실제 조사해 확인한 관행. 강제 규칙은 [`.claude/rules/typescript.md`](../../rules/typescript.md)에 별도로 정리돼 있다.

- **type 별칭 선호**: `interface` 선언이 0개, `type`이 43개. props는 `<컴포넌트명>Props` 네이밍의 `type`.
- **`any` 금지**: `@typescript-eslint/no-explicit-any`가 `error`. 실제 코드에 `any` 사용 0건. 모르면 `unknown`으로 좁혀 쓴다.
- **`enum` 대신 문자열 리터럴 유니온**: 예) `type Status = { type: "idle" | "loading" | "ok" | "error" }`.
- **컴포넌트 선언**: `React.FC` 없이 `export default function ComponentName({ ...props }: XxxProps)`.
- **`useState<T>`**: 빈 배열·`null` 초기값처럼 추론이 안 되면 제네릭 명시.
- **`catch (err)`**: 변수에 타입 주석을 붙이지 않는다(strict에서 `unknown` 추론).
- **세미콜론 사용**, import는 `@/` 별칭.
- ESLint에서 `no-console`·`no-unused-vars`도 `error`.
