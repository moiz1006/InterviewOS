import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat({ baseDirectory: import.meta.dirname });

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript", "prettier"),
  {
    rules: {
      // Business logic doesn't belong in components — see
      // ../docs/architecture/ADR-0003-frontend-structure.md. This is a
      // reminder rule, not fully enforceable by ESLint alone; reviewers
      // should still check for it.
      "@typescript-eslint/no-explicit-any": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
];

export default eslintConfig;
