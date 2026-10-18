import js from '@eslint/js';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import hooks from 'eslint-plugin-react-hooks';
import refresh from 'eslint-plugin-react-refresh';

export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', 'playwright-report*/**', 'test-results/**'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.recommended,
      hooks.configs.flat.recommended, refresh.configs.vite],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
  {
    files: ['src/{domain,application}/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': ['error', { patterns: [
        'react', 'react-dom', 'react-dom/*', 'react-router', '@tanstack/*',
        '@mui/*', 'zod', '**/infrastructure/**', '**/presentation/**', '**/app/**',
      ] }],
    },
  },
  {
    files: ['src/presentation/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': ['error', {
        patterns: ['**/infrastructure/**', '**/app/**'],
      }],
    },
  },
);
