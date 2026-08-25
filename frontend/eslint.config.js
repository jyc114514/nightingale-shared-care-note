import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: ["dist", "node_modules", "coverage", "playwright-report", "test-results"],
  },
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      globals: {
        clearTimeout: "readonly",
        console: "readonly",
        document: "readonly",
        fetch: "readonly",
        setTimeout: "readonly",
        window: "readonly",
      },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    },
  },
);

