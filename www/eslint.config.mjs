// eslint-config-next는 이미 네이티브 flat config 배열을 내보낸다 — FlatCompat으로 감싸면
// (구버전 .eslintrc 브리지) eslint-plugin-react의 자기참조 플러그인 객체가 순환 구조라
// "Converting circular structure to JSON" 에러로 깨진다. 그래서 직접 import 한다.
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

// no-console/no-explicit-any/no-unused-vars를 warn이 아니라 error로 — 통과 못 하면
// 빌드/pre-commit이 막혀야 한다는 하네스 원칙(경고만 남기면 결국 무시된다).
const eslintConfig = [
  ...nextCoreWebVitals,
  {
    rules: {
      "no-console": "error",
      // eslint-config-next의 recommended가 새로 포함한 규칙. "마운트 후 localStorage를
      // 읽어 setState" 같은 기존 패턴 8곳을 전부 error로 잡아 첫 도입부터 커밋을 막는다 —
      // 버그가 아니라 더 엄격한 권장 스타일이라 일단 warn으로 낮춤. 점진적으로 정리되면 error로.
      "react-hooks/set-state-in-effect": "warn",
    },
  },
  // @typescript-eslint 플러그인은 next/typescript 블록에서만 등록되므로, 같은 files
  // 범위(.ts/.tsx)에 한정해야 "plugin not found" 에러 없이 적용된다.
  {
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": "error",
    },
  },
];

export default eslintConfig;
