import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Otimizações críticas de bundle size
    target: 'es2015',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
        passes: 2,
        unsafe: true,
        unsafe_comps: true,
        unsafe_Function: true,
        unsafe_math: true,
        unsafe_proto: true,
        unsafe_regexp: true,
        unsafe_undefined: true,
      },
      mangle: {
        safari10: true,
      },
    },
    rollupOptions: {
      output: {
        // Code splitting avançado por rota e funcionalidade
        manualChunks: (id) => {
          // Core React
          if (id.includes('react') || id.includes('react-dom')) {
            return 'react-core';
          }
          
          // Material-UI
          if (id.includes('@mui/material') || id.includes('@mui/icons-material')) {
            return 'mui-components';
          }
          
          // Query e estado
          if (id.includes('@tanstack/react-query') || id.includes('zustand')) {
            return 'state-management';
          }
          
          // Componentes por rota
          if (id.includes('/components/dashboard/')) {
            return 'dashboard-components';
          }
          
          if (id.includes('/components/analytics/')) {
            return 'analytics-components';
          }
          
          if (id.includes('/components/admin/')) {
            return 'admin-components';
          }
          
          if (id.includes('/components/keywords/')) {
            return 'keywords-components';
          }
          
          // Utilitários
          if (id.includes('/utils/') || id.includes('/hooks/')) {
            return 'utilities';
          }
          
          // APIs e serviços
          if (id.includes('/api/') || id.includes('/services/')) {
            return 'api-services';
          }
          
          // Vendor libraries
          if (id.includes('node_modules')) {
            if (id.includes('lodash') || id.includes('date-fns')) {
              return 'date-utils';
            }
            if (id.includes('chart') || id.includes('recharts')) {
              return 'charts';
            }
            if (id.includes('form') || id.includes('validation')) {
              return 'form-validation';
            }
            return 'vendor';
          }
        },
        // Nomes de arquivos otimizados com hash
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/\.(css)$/.test(assetInfo.name)) {
            return `assets/css/[name]-[hash].${ext}`;
          }
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return `assets/images/[name]-[hash].${ext}`;
          }
          return `assets/[ext]/[name]-[hash].[ext]`;
        },
      },
    },
    // Otimizações críticas de assets
    assetsInlineLimit: 4096, // 4kb
    chunkSizeWarningLimit: 500, // Reduzido para 500kb
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/*.setup.*',
      ],
    },
  },
  define: {
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development'),
  },
  // Otimizações críticas de desenvolvimento
  optimizeDeps: {
    include: [
      'react', 
      'react-dom',
      '@mui/material',
      '@mui/icons-material',
      '@tanstack/react-query'
    ],
    exclude: ['@vitejs/plugin-react'],
  },
  // Resolução de módulos otimizada
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './components'),
      '@hooks': resolve(__dirname, './hooks'),
      '@types': resolve(__dirname, './types'),
      '@utils': resolve(__dirname, './utils'),
      '@pages': resolve(__dirname, './pages'),
      '@api': resolve(__dirname, './api'),
      '@shared': resolve(__dirname, './components/shared'),
      '@prompt-system': resolve(__dirname, './components/prompt-system'),
    },
  },
  // Otimizações críticas de CSS
  css: {
    devSourcemap: false,
    postcss: {
      plugins: [
        require('autoprefixer'),
        require('cssnano')({
          preset: ['default', {
            discardComments: {
              removeAll: true,
            },
            normalizeWhitespace: true,
          }]
        })
      ]
    }
  },
}); 