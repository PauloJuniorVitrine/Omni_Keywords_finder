/**
 * Scripts de Build
 * 
 * Prompt: Implementação de itens de criticidade baixa - 11.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { execSync } from 'child_process';
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join } from 'path';

interface BuildConfig {
  environment: 'development' | 'staging' | 'production';
  minify: boolean;
  sourceMaps: boolean;
  optimize: boolean;
  analyze: boolean;
  outputDir: string;
}

/**
 * Configurações de build por ambiente
 */
const buildConfigs: Record<string, BuildConfig> = {
  development: {
    environment: 'development',
    minify: false,
    sourceMaps: true,
    optimize: false,
    analyze: false,
    outputDir: 'dist/dev',
  },
  staging: {
    environment: 'staging',
    minify: true,
    sourceMaps: true,
    optimize: true,
    analyze: false,
    outputDir: 'dist/staging',
  },
  production: {
    environment: 'production',
    minify: true,
    sourceMaps: false,
    optimize: true,
    analyze: true,
    outputDir: 'dist/prod',
  },
};

/**
 * Utilitário para executar comandos
 */
function executeCommand(command: string, cwd?: string): void {
  try {
    console.log(`[BUILD] Executando: ${command}`);
    execSync(command, { 
      stdio: 'inherit', 
      cwd,
      env: { ...process.env, FORCE_COLOR: '1' }
    });
  } catch (error) {
    console.error(`[BUILD] Erro ao executar comando: ${command}`);
    throw error;
  }
}

/**
 * Limpa diretório de output
 */
function cleanOutput(outputDir: string): void {
  try {
    if (existsSync(outputDir)) {
      executeCommand(`rm -rf ${outputDir}`);
    }
    mkdirSync(outputDir, { recursive: true });
    console.log(`[BUILD] Diretório limpo: ${outputDir}`);
  } catch (error) {
    console.error(`[BUILD] Erro ao limpar diretório: ${outputDir}`);
    throw error;
  }
}

/**
 * Gera arquivo de configuração de ambiente
 */
function generateEnvConfig(environment: string): void {
  const envFile = join(process.cwd(), 'config', 'env.config.js');
  const envContent = `
// Configuração de ambiente gerada automaticamente
export const ENV_CONFIG = {
  environment: '${environment}',
  timestamp: '${new Date().toISOString()}',
  buildId: '${Date.now()}',
  version: '${process.env.npm_package_version || '1.0.0'}',
};
`;

  writeFileSync(envFile, envContent);
  console.log(`[BUILD] Configuração de ambiente gerada: ${envFile}`);
}

/**
 * Executa análise de bundle (apenas produção)
 */
function runBundleAnalysis(outputDir: string): void {
  try {
    const bundleAnalyzer = join(process.cwd(), 'node_modules', '.bin', 'webpack-bundle-analyzer');
    if (existsSync(bundleAnalyzer)) {
      executeCommand(`${bundleAnalyzer} ${outputDir}/stats.json`);
    }
  } catch (error) {
    console.warn('[BUILD] Bundle analyzer não disponível');
  }
}

/**
 * Valida build
 */
function validateBuild(outputDir: string): void {
  const requiredFiles = ['index.html', 'static/js/main.js'];
  
  for (const file of requiredFiles) {
    const filePath = join(outputDir, file);
    if (!existsSync(filePath)) {
      throw new Error(`Arquivo obrigatório não encontrado: ${filePath}`);
    }
  }
  
  console.log('[BUILD] Validação concluída com sucesso');
}

/**
 * Gera relatório de build
 */
function generateBuildReport(config: BuildConfig, startTime: number): void {
  const endTime = Date.now();
  const duration = endTime - startTime;
  
  const report = {
    environment: config.environment,
    timestamp: new Date().toISOString(),
    duration: `${duration}ms`,
    outputDir: config.outputDir,
    features: {
      minify: config.minify,
      sourceMaps: config.sourceMaps,
      optimize: config.optimize,
      analyze: config.analyze,
    },
  };
  
  const reportFile = join(config.outputDir, 'build-report.json');
  writeFileSync(reportFile, JSON.stringify(report, null, 2));
  
  console.log(`[BUILD] Relatório gerado: ${reportFile}`);
  console.log(`[BUILD] Build concluído em ${duration}ms`);
}

/**
 * Build principal
 */
function build(environment: string = 'development'): void {
  const startTime = Date.now();
  const config = buildConfigs[environment];
  
  if (!config) {
    throw new Error(`Ambiente inválido: ${environment}`);
  }
  
  console.log(`[BUILD] Iniciando build para ambiente: ${environment}`);
  
  try {
    // 1. Limpar output
    cleanOutput(config.outputDir);
    
    // 2. Gerar configuração de ambiente
    generateEnvConfig(environment);
    
    // 3. Instalar dependências se necessário
    if (!existsSync(join(process.cwd(), 'node_modules'))) {
      console.log('[BUILD] Instalando dependências...');
      executeCommand('npm install');
    }
    
    // 4. Executar build
    const buildCommand = config.analyze 
      ? 'npm run build:analyze'
      : 'npm run build';
    
    executeCommand(buildCommand);
    
    // 5. Validar build
    validateBuild(config.outputDir);
    
    // 6. Análise de bundle (se habilitado)
    if (config.analyze) {
      runBundleAnalysis(config.outputDir);
    }
    
    // 7. Gerar relatório
    generateBuildReport(config, startTime);
    
    console.log(`[BUILD] ✅ Build concluído com sucesso para ${environment}`);
    
  } catch (error) {
    console.error(`[BUILD] ❌ Erro no build: ${error}`);
    process.exit(1);
  }
}

/**
 * Build para desenvolvimento
 */
export function buildDev(): void {
  build('development');
}

/**
 * Build para staging
 */
export function buildStaging(): void {
  build('staging');
}

/**
 * Build para produção
 */
export function buildProd(): void {
  build('production');
}

/**
 * Build com análise de bundle
 */
export function buildAnalyze(): void {
  const config = buildConfigs.production;
  config.analyze = true;
  build('production');
}

// Execução direta via CLI
if (require.main === module) {
  const environment = process.argv[2] || 'development';
  build(environment);
} 