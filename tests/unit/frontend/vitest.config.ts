import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./conftest.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/*.setup.*',
        'dist/',
        'build/',
        'coverage/',
      ],
      thresholds: {
        global: {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90,
        },
      },
    },
    testTimeout: 10000,
    hookTimeout: 10000,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '../../app/'),
      '@components': resolve(__dirname, '../../app/components'),
      '@hooks': resolve(__dirname, '../../app/hooks'),
      '@contexts': resolve(__dirname, '../../app/contexts'),
      '@utils': resolve(__dirname, '../../app/utils'),
      '@types': resolve(__dirname, '../../app/types'),
      '@services': resolve(__dirname, '../../app/services'),
    },
  },
})
