/**
 * Configuração do Stryker para Mutation Testing em TypeScript
 * Tracing ID: MUTATION_TEST_002
 * Data: 2025-01-27
 */

module.exports = function(config) {
  config.set({
    // Configurações básicas
    packageManager: 'npm',
    reporters: ['html', 'clear-text', 'progress', 'json'],
    testRunner: 'jest',
    coverageAnalysis: 'perTest',
    
    // Diretórios a serem testados
    mutate: [
      'app/**/*.ts',
      'app/**/*.tsx',
      '!app/**/*.test.ts',
      '!app/**/*.test.tsx',
      '!app/**/*.spec.ts',
      '!app/**/*.spec.tsx'
    ],
    
    // Configurações do Jest
    jest: {
      config: {
        testEnvironment: 'jsdom',
        setupFilesAfterEnv: ['<rootDir>/app/setupTests.ts'],
        moduleNameMapping: {
          '^@/(.*)$': '<rootDir>/app/$1'
        }
      }
    },
    
    // Configurações de mutação
    mutator: {
      name: 'typescript',
      excludedMutations: [
        'StringLiteral',
        'ArrayLiteral',
        'ObjectLiteral'
      ]
    },
    
    // Configurações de relatório
    htmlReporter: {
      baseDir: 'coverage/mutation/html'
    },
    
    jsonReporter: {
      fileName: 'coverage/mutation/mutation-report.json'
    },
    
    // Configurações de timeout
    timeoutMS: 10000,
    timeoutFactor: 2,
    
    // Configurações de concorrência
    concurrency: 4,
    
    // Configurações de logging
    logLevel: 'info',
    
    // Configurações de exclusão
    ignoreStatic: true,
    ignorePatterns: [
      'node_modules/**',
      'coverage/**',
      'dist/**',
      'build/**',
      '*.config.js',
      '*.config.ts'
    ],
    
    // Configurações de plugins
    plugins: [
      '@stryker-mutator/jest-runner',
      '@stryker-mutator/typescript-checker'
    ],
    
    // Configurações de TypeScript
    typescriptChecker: {
      configFile: 'tsconfig.json'
    },
    
    // Configurações de dashboard (opcional)
    dashboard: {
      project: 'omni-keywords-finder',
      version: 'main',
      module: 'frontend'
    }
  });
}; 