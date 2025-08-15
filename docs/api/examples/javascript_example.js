/**
 * Exemplo de uso da API Omni Keywords Finder - JavaScript/Node.js
 * Tracing ID: API_EXAMPLE_JS_001
 * Data: 2025-01-27
 */

const axios = require('axios');

class OmniKeywordsFinderAPI {
    constructor(baseUrl = 'https://api.omnikeywords.com/v2') {
        this.baseUrl = baseUrl;
        this.accessToken = null;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    /**
     * Realizar login na API
     * @param {string} email - Email do usuário
     * @param {string} password - Senha do usuário
     * @returns {Promise<boolean>} - Sucesso do login
     */
    async login(email, password) {
        try {
            const response = await this.client.post('/auth/login', {
                email,
                password
            });

            if (response.status === 200) {
                this.accessToken = response.data.access_token;
                this.client.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
                console.log('✅ Login realizado com sucesso');
                return true;
            }
        } catch (error) {
            console.error('❌ Erro durante login:', error.response?.data || error.message);
            return false;
        }
    }

    /**
     * Analisar uma palavra-chave específica
     * @param {string} keyword - Palavra-chave para análise
     * @param {Object} options - Opções de análise
     * @returns {Promise<Object|null>} - Resultado da análise
     */
    async analyzeKeyword(keyword, options = {}) {
        try {
            const payload = {
                keyword,
                language: options.language || 'pt-BR',
                market: options.market || 'BR',
                include_competitors: options.includeCompetitors !== false,
                include_trends: options.includeTrends !== false
            };

            const response = await this.client.post('/keywords/analyze', payload);
            return response.data;
        } catch (error) {
            console.error('❌ Erro na análise:', error.response?.data || error.message);
            return null;
        }
    }

    /**
     * Descobrir novas palavras-chave relacionadas
     * @param {Array<string>} seedKeywords - Palavras-chave iniciais
     * @param {Object} options - Opções de descoberta
     * @returns {Promise<Object|null>} - Resultado da descoberta
     */
    async discoverKeywords(seedKeywords, options = {}) {
        try {
            const payload = {
                seed_keywords: seedKeywords,
                language: options.language || 'pt-BR',
                market: options.market || 'BR',
                max_results: options.maxResults || 20
            };

            const response = await this.client.post('/keywords/discover', payload);
            return response.data;
        } catch (error) {
            console.error('❌ Erro na descoberta:', error.response?.data || error.message);
            return null;
        }
    }

    /**
     * Otimizar conteúdo para SEO
     * @param {string} content - Conteúdo para otimizar
     * @param {Array<string>} targetKeywords - Palavras-chave alvo
     * @param {Object} options - Opções de otimização
     * @returns {Promise<Object|null>} - Resultado da otimização
     */
    async optimizeContent(content, targetKeywords, options = {}) {
        try {
            const payload = {
                content,
                target_keywords: targetKeywords,
                content_type: options.contentType || 'blog',
                language: options.language || 'pt-BR'
            };

            const response = await this.client.post('/content/optimize', payload);
            return response.data;
        } catch (error) {
            console.error('❌ Erro na otimização:', error.response?.data || error.message);
            return null;
        }
    }

    /**
     * Obter métricas de performance
     * @param {Object} options - Opções de filtro
     * @returns {Promise<Object|null>} - Métricas de performance
     */
    async getPerformanceMetrics(options = {}) {
        try {
            const params = {};
            if (options.startDate) params.start_date = options.startDate;
            if (options.endDate) params.end_date = options.endDate;

            const response = await this.client.get('/analytics/performance', { params });
            return response.data;
        } catch (error) {
            console.error('❌ Erro ao obter métricas:', error.response?.data || error.message);
            return null;
        }
    }
}

/**
 * Exibir resultados da análise de palavra-chave
 * @param {Object} analysis - Resultado da análise
 */
function printKeywordAnalysis(analysis) {
    console.log('\n' + '='.repeat(60));
    console.log('📊 ANÁLISE DE PALAVRA-CHAVE');
    console.log('='.repeat(60));

    const keyword = analysis.keyword || 'N/A';
    const analysisData = analysis.analysis || {};

    console.log(`🔍 Palavra-chave: ${keyword}`);
    console.log(`📈 Volume de busca: ${analysisData.search_volume?.toLocaleString() || 'N/A'}`);
    console.log(`🎯 Dificuldade: ${analysisData.difficulty || 'N/A'}/100`);
    console.log(`💰 CPC médio: R$ ${analysisData.cpc || 'N/A'}`);
    console.log(`🏆 Competição: ${((analysisData.competition || 0) * 100).toFixed(1)}%`);
    console.log(`🎯 Intenção: ${analysisData.intent || 'N/A'}`);

    // Competidores
    const competitors = analysis.competitors || [];
    if (competitors.length > 0) {
        console.log(`\n🏢 TOP COMPETIDORES (${competitors.length}):`);
        competitors.slice(0, 5).forEach((comp, i) => {
            console.log(`  ${i + 1}. ${comp.domain || 'N/A'} (Rank: ${comp.rank || 'N/A'})`);
        });
    }

    // Tendências
    const trends = analysis.trends || {};
    if (Object.keys(trends).length > 0) {
        console.log(`\n📈 TENDÊNCIAS:`);
        console.log(`  Padrão sazonal: ${trends.seasonal_pattern || 'N/A'}`);
        console.log(`  Taxa de crescimento: ${trends.growth_rate || 'N/A'}%`);
    }

    // Recomendações
    const recommendations = analysis.recommendations || [];
    if (recommendations.length > 0) {
        console.log(`\n💡 RECOMENDAÇÕES:`);
        recommendations.forEach((rec, i) => {
            console.log(`  ${i + 1}. ${rec}`);
        });
    }
}

/**
 * Exibir resultados da descoberta de palavras-chave
 * @param {Object} discovery - Resultado da descoberta
 */
function printDiscoveryResults(discovery) {
    console.log('\n' + '='.repeat(60));
    console.log('🔍 DESCOBERTA DE PALAVRAS-CHAVE');
    console.log('='.repeat(60));

    const discovered = discovery.discovered_keywords || [];
    console.log(`📊 Total descoberto: ${discovered.length} palavras-chave`);

    if (discovered.length > 0) {
        console.log(`\n🏆 TOP 10 OPORTUNIDADES:`);
        discovered.slice(0, 10).forEach((kw, i) => {
            console.log(`  ${i + 1}. ${kw.keyword || 'N/A'}`);
            console.log(`     Volume: ${kw.search_volume?.toLocaleString() || 'N/A'} | ` +
                       `Dificuldade: ${kw.difficulty || 'N/A'}/100 | ` +
                       `Relevância: ${((kw.relevance_score || 0) * 100).toFixed(1)}%`);
        });
    }

    // Clusters
    const clusters = discovery.clusters || [];
    if (clusters.length > 0) {
        console.log(`\n📦 CLUSTERS IDENTIFICADOS (${clusters.length}):`);
        clusters.forEach((cluster, i) => {
            console.log(`  ${i + 1}. ${cluster.name || 'N/A'}`);
            console.log(`     Média volume: ${cluster.avg_volume?.toLocaleString() || 'N/A'}`);
            console.log(`     Média dificuldade: ${cluster.avg_difficulty || 'N/A'}/100`);
        });
    }
}

/**
 * Exibir resultados da otimização de conteúdo
 * @param {Object} optimization - Resultado da otimização
 */
function printOptimizationResults(optimization) {
    console.log('\n' + '='.repeat(60));
    console.log('✏️ OTIMIZAÇÃO DE CONTEÚDO');
    console.log('='.repeat(60));

    const seoScore = optimization.seo_score || 0;
    console.log(`📊 Score SEO: ${seoScore}/100`);

    const suggestions = optimization.suggestions || [];
    if (suggestions.length > 0) {
        console.log(`\n💡 SUGESTÕES DE MELHORIA (${suggestions.length}):`);
        suggestions.forEach((suggestion, i) => {
            console.log(`  ${i + 1}. [${(suggestion.type || 'N/A').toUpperCase()}] ` +
                       `[${(suggestion.priority || 'N/A').toUpperCase()}]`);
            console.log(`     ${suggestion.description || 'N/A'}`);
            if (suggestion.suggested_value) {
                console.log(`     Sugestão: ${suggestion.suggested_value}`);
            }
        });
    }
}

/**
 * Função principal com exemplos de uso
 */
async function main() {
    console.log('🚀 EXEMPLO DE USO - API OMNİ KEYWORDS FINDER (JavaScript)');
    console.log('='.repeat(60));

    // Inicializar cliente
    const api = new OmniKeywordsFinderAPI();

    // Credenciais (substitua pelas suas)
    const email = 'seu_email@exemplo.com';
    const password = 'sua_senha';

    // Login
    const loginSuccess = await api.login(email, password);
    if (!loginSuccess) {
        console.log('❌ Não foi possível fazer login. Verifique as credenciais.');
        return;
    }

    // Exemplo 1: Análise de palavra-chave
    console.log('\n🔍 EXEMPLO 1: Análise de palavra-chave');
    const keywordAnalysis = await api.analyzeKeyword('marketing digital');
    if (keywordAnalysis) {
        printKeywordAnalysis(keywordAnalysis);
    }

    // Exemplo 2: Descoberta de palavras-chave
    console.log('\n🔍 EXEMPLO 2: Descoberta de palavras-chave');
    const discovery = await api.discoverKeywords(['marketing digital', 'seo'], {
        maxResults: 15
    });
    if (discovery) {
        printDiscoveryResults(discovery);
    }

    // Exemplo 3: Otimização de conteúdo
    console.log('\n✏️ EXEMPLO 3: Otimização de conteúdo');
    const content = `
        Marketing digital é uma estratégia essencial para empresas modernas. 
        Com o crescimento da internet, as empresas precisam se adaptar e 
        usar ferramentas digitais para alcançar seus clientes.
    `;
    const optimization = await api.optimizeContent(content, ['marketing digital', 'estratégia']);
    if (optimization) {
        printOptimizationResults(optimization);
    }

    // Exemplo 4: Métricas de performance
    console.log('\n📊 EXEMPLO 4: Métricas de performance');
    const metrics = await api.getPerformanceMetrics({
        startDate: '2024-01-01',
        endDate: '2024-12-31'
    });
    if (metrics) {
        console.log('📈 Métricas obtidas com sucesso');
        console.log(`Total de análises: ${metrics.metrics?.total_analyses || 'N/A'}`);
        console.log(`Taxa de sucesso: ${metrics.metrics?.success_rate || 'N/A'}%`);
    }

    console.log('\n✅ Exemplos concluídos com sucesso!');
}

// Executar se for o arquivo principal
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    OmniKeywordsFinderAPI,
    printKeywordAnalysis,
    printDiscoveryResults,
    printOptimizationResults
}; 