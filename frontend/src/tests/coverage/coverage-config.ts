/**
 * Configuração de Cobertura de Testes
 * 
 * Prompt: Implementar cobertura de testes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COVERAGE_CONFIG_20250127_001
 */

export const COVERAGE_CONFIG = {
  // Limites mínimos de cobertura por tipo
  thresholds: {
    statements: 85,
    branches: 80,
    functions: 85,
    lines: 85
  },

  // Diretórios e arquivos a incluir na cobertura
  include: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/*.spec.{ts,tsx}',
    '!src/tests/**/*',
    '!src/**/index.ts',
    '!src/**/types.ts'
  ],

  // Diretórios e arquivos a excluir da cobertura
  exclude: [
    'node_modules/**/*',
    'coverage/**/*',
    'dist/**/*',
    'build/**/*',
    '**/*.config.{js,ts}',
    '**/jest.config.*',
    '**/babel.config.*',
    '**/webpack.config.*',
    '**/vite.config.*'
  ],

  // Configurações específicas por diretório
  directoryThresholds: {
    'src/hooks': {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    },
    'src/services': {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    },
    'src/utils': {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    },
    'src/components': {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80
    },
    'src/pages': {
      statements: 75,
      branches: 70,
      functions: 75,
      lines: 75
    }
  },

  // Configurações de relatório
  reporter: {
    // Tipos de relatório a gerar
    types: ['text', 'text-summary', 'html', 'lcov', 'json'],
    
    // Diretório de saída
    dir: 'coverage',
    
    // Configurações do relatório HTML
    html: {
      dir: 'coverage/html',
      subdir: '.'
    },
    
    // Configurações do relatório LCOV
    lcov: {
      dir: 'coverage/lcov',
      file: 'lcov.info'
    }
  },

  // Configurações de cobertura de branches
  branchCoverage: {
    // Branches críticos que devem ter 100% de cobertura
    critical: [
      'src/hooks/useAuth.ts',
      'src/hooks/useApiClient.ts',
      'src/services/auth-service.ts',
      'src/utils/api-helpers.ts'
    ],
    
    // Branches que podem ter cobertura reduzida
    optional: [
      'src/components/ui/**/*',
      'src/pages/**/*'
    ]
  },

  // Configurações de cobertura de funções
  functionCoverage: {
    // Funções críticas que devem ter 100% de cobertura
    critical: [
      'authenticate',
      'refreshToken',
      'handleApiError',
      'validateInput',
      'sanitizeData'
    ],
    
    // Funções que podem ter cobertura reduzida
    optional: [
      'formatDate',
      'formatCurrency',
      'generateId'
    ]
  }
};

/**
 * Validador de cobertura
 */
export class CoverageValidator {
  private config = COVERAGE_CONFIG;

  /**
   * Valida se a cobertura atende aos limites mínimos
   */
  validateCoverage(coverageData: any): CoverageValidationResult {
    const result: CoverageValidationResult = {
      passed: true,
      errors: [],
      warnings: [],
      summary: {
        statements: 0,
        branches: 0,
        functions: 0,
        lines: 0
      }
    };

    // Validar cobertura geral
    Object.keys(this.config.thresholds).forEach(metric => {
      const actual = coverageData.total[metric].pct;
      const expected = this.config.thresholds[metric as keyof typeof this.config.thresholds];
      
      result.summary[metric as keyof typeof result.summary] = actual;
      
      if (actual < expected) {
        result.passed = false;
        result.errors.push(
          `${metric} coverage ${actual}% is below threshold ${expected}%`
        );
      }
    });

    // Validar cobertura por diretório
    Object.keys(this.config.directoryThresholds).forEach(dir => {
      const dirCoverage = coverageData[dir];
      if (dirCoverage) {
        const thresholds = this.config.directoryThresholds[dir];
        Object.keys(thresholds).forEach(metric => {
          const actual = dirCoverage[metric].pct;
          const expected = thresholds[metric as keyof typeof thresholds];
          
          if (actual < expected) {
            result.warnings.push(
              `${dir} ${metric} coverage ${actual}% is below threshold ${expected}%`
            );
          }
        });
      }
    });

    return result;
  }

  /**
   * Gera relatório de cobertura
   */
  generateReport(coverageData: any): CoverageReport {
    const validation = this.validateCoverage(coverageData);
    
    return {
      timestamp: new Date().toISOString(),
      tracingId: 'COVERAGE_REPORT_20250127_001',
      validation,
      details: {
        totalFiles: coverageData.totalFiles,
        coveredFiles: coverageData.coveredFiles,
        totalLines: coverageData.totalLines,
        coveredLines: coverageData.coveredLines,
        uncoveredLines: coverageData.uncoveredLines
      },
      recommendations: this.generateRecommendations(coverageData)
    };
  }

  /**
   * Gera recomendações para melhorar a cobertura
   */
  private generateRecommendations(coverageData: any): string[] {
    const recommendations: string[] = [];

    // Analisar arquivos com baixa cobertura
    Object.keys(coverageData).forEach(file => {
      if (file !== 'total' && coverageData[file]) {
        const fileCoverage = coverageData[file];
        const totalCoverage = (
          fileCoverage.statements.pct +
          fileCoverage.branches.pct +
          fileCoverage.functions.pct +
          fileCoverage.lines.pct
        ) / 4;

        if (totalCoverage < 70) {
          recommendations.push(
            `Priorizar testes para ${file} (cobertura: ${totalCoverage.toFixed(1)}%)`
          );
        }
      }
    });

    // Verificar branches não cobertos
    if (coverageData.total.branches.pct < 80) {
      recommendations.push(
        'Aumentar cobertura de branches - adicionar testes para condições condicionais'
      );
    }

    // Verificar funções não cobertas
    if (coverageData.total.functions.pct < 85) {
      recommendations.push(
        'Aumentar cobertura de funções - adicionar testes para funções não cobertas'
      );
    }

    return recommendations;
  }
}

/**
 * Tipos para validação de cobertura
 */
export interface CoverageValidationResult {
  passed: boolean;
  errors: string[];
  warnings: string[];
  summary: {
    statements: number;
    branches: number;
    functions: number;
    lines: number;
  };
}

export interface CoverageReport {
  timestamp: string;
  tracingId: string;
  validation: CoverageValidationResult;
  details: {
    totalFiles: number;
    coveredFiles: number;
    totalLines: number;
    coveredLines: number;
    uncoveredLines: number;
  };
  recommendations: string[];
}

/**
 * Utilitários para cobertura
 */
export const CoverageUtils = {
  /**
   * Calcula cobertura total
   */
  calculateTotalCoverage(coverageData: any): number {
    const total = coverageData.total;
    return (
      total.statements.pct +
      total.branches.pct +
      total.functions.pct +
      total.lines.pct
    ) / 4;
  },

  /**
   * Identifica arquivos com baixa cobertura
   */
  findLowCoverageFiles(coverageData: any, threshold: number = 70): string[] {
    const lowCoverageFiles: string[] = [];

    Object.keys(coverageData).forEach(file => {
      if (file !== 'total' && coverageData[file]) {
        const coverage = this.calculateTotalCoverage({ total: coverageData[file] });
        if (coverage < threshold) {
          lowCoverageFiles.push(file);
        }
      }
    });

    return lowCoverageFiles;
  },

  /**
   * Gera badge de cobertura para README
   */
  generateCoverageBadge(coverage: number): string {
    let color = 'red';
    if (coverage >= 90) color = 'brightgreen';
    else if (coverage >= 80) color = 'green';
    else if (coverage >= 70) color = 'yellow';
    else if (coverage >= 60) color = 'orange';

    return `![Coverage](https://img.shields.io/badge/coverage-${coverage}%25-${color})`;
  }
}; 