#!/usr/bin/env node
/**
 * Script de Execução para Stryker Mutation Testing
 * ================================================
 * 
 * Tracing ID: MUTATION_TEST_002
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: ✅ IMPLEMENTAÇÃO
 * 
 * Script para executar mutation testing usando Stryker e gerar relatórios.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Configura o ambiente para mutation testing
 */
function setupEnvironment() {
    console.log('🔧 Configurando ambiente para Stryker mutation testing...');
    
    const directories = [
        'coverage/mutation/html',
        'coverage/mutation/json',
        'logs',
        'reports/mutation'
    ];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
            console.log(`  ✅ Diretório criado: ${dir}`);
        }
    });
}

/**
 * Executa mutation testing com Stryker
 */
function runStrykerTests(options = {}) {
    console.log('🧬 Executando Stryker mutation testing...');
    
    const {
        mode = 'run',
        concurrency = 4,
        timeout = 10000
    } = options;
    
    try {
        // Comando base do Stryker
        const cmd = `npx stryker run --mode=${mode} --concurrency=${concurrency} --timeoutMS=${timeout}`;
        
        console.log(`  🎯 Modo: ${mode}`);
        console.log(`  🔄 Concorrência: ${concurrency}`);
        console.log(`  ⏰ Timeout: ${timeout}ms`);
        
        // Executar Stryker
        const result = execSync(cmd, { 
            encoding: 'utf8',
            stdio: 'pipe',
            timeout: 1800000 // 30 minutos
        });
        
        console.log('  ✅ Stryker mutation testing executado com sucesso');
        return { success: true, output: result };
        
    } catch (error) {
        console.error(`  ❌ Erro na execução do Stryker: ${error.message}`);
        return { success: false, error: error.message };
    }
}

/**
 * Analisa os resultados do mutation testing
 */
function analyzeResults() {
    console.log('🔍 Analisando resultados do Stryker...');
    
    try {
        const reportFile = 'coverage/mutation/mutation-report.json';
        
        if (!fs.existsSync(reportFile)) {
            console.log('  ⚠️ Relatório não encontrado');
            return { status: 'error', message: 'Relatório não encontrado' };
        }
        
        const data = JSON.parse(fs.readFileSync(reportFile, 'utf8'));
        
        // Calcular métricas
        const totalMutations = data.mutationScore || 0;
        const killedMutations = data.killed || 0;
        const survivedMutations = data.survived || 0;
        const noCoverage = data.noCoverage || 0;
        
        const mutationScore = totalMutations > 0 ? (killedMutations / totalMutations) * 100 : 0;
        
        const results = {
            totalMutations,
            killedMutations,
            survivedMutations,
            noCoverage,
            mutationScore: Math.round(mutationScore * 100) / 100,
            timestamp: new Date().toISOString(),
            status: mutationScore >= 80 ? 'success' : 'warning'
        };
        
        console.log(`  📈 Total de mutações: ${totalMutations}`);
        console.log(`  💀 Mutações eliminadas: ${killedMutations}`);
        console.log(`  🧟 Mutações sobreviventes: ${survivedMutations}`);
        console.log(`  📊 Sem cobertura: ${noCoverage}`);
        console.log(`  🎯 Score de mutação: ${results.mutationScore}%`);
        
        return results;
        
    } catch (error) {
        console.error(`  ❌ Erro ao analisar resultados: ${error.message}`);
        return { status: 'error', message: error.message };
    }
}

/**
 * Salva relatório resumido
 */
function saveSummaryReport(results) {
    console.log('💾 Salvando relatório resumido...');
    
    const summary = {
        tracingId: 'MUTATION_TEST_002',
        timestamp: new Date().toISOString(),
        tool: 'stryker',
        results,
        recommendations: []
    };
    
    // Adicionar recomendações baseadas nos resultados
    if (results.mutationScore < 80) {
        summary.recommendations.push('Melhorar cobertura de testes para aumentar score de mutação');
    }
    
    if (results.survivedMutations > 0) {
        summary.recommendations.push('Revisar testes para eliminar mutações sobreviventes');
    }
    
    if (results.noCoverage > 0) {
        summary.recommendations.push('Adicionar testes para código sem cobertura');
    }
    
    // Salvar relatório
    const reportFile = 'reports/mutation/stryker_summary_report.json';
    fs.writeFileSync(reportFile, JSON.stringify(summary, null, 2));
    
    console.log(`  ✅ Relatório salvo: ${reportFile}`);
}

/**
 * Função principal
 */
function main() {
    console.log('🧬 Stryker Mutation Testing - Omni Keywords Finder');
    console.log('=' .repeat(50));
    
    // Configurar ambiente
    setupEnvironment();
    
    // Executar mutation testing
    const strykerResult = runStrykerTests({
        mode: 'run',
        concurrency: 4,
        timeout: 10000
    });
    
    if (strykerResult.success) {
        // Analisar resultados
        const results = analyzeResults();
        
        if (results.status !== 'error') {
            // Salvar relatório resumido
            saveSummaryReport(results);
            
            console.log('\n🎉 Stryker mutation testing concluído com sucesso!');
            
            // Exibir resumo
            if (results.status === 'success') {
                console.log('✅ Score de mutação aceitável');
            } else {
                console.log('⚠️ Score de mutação abaixo do esperado');
            }
        } else {
            console.log('❌ Falha ao analisar resultados');
        }
    } else {
        console.log('❌ Falha na execução do Stryker');
    }
}

// Executar se chamado diretamente
if (require.main === module) {
    main();
}

module.exports = {
    setupEnvironment,
    runStrykerTests,
    analyzeResults,
    saveSummaryReport
}; 