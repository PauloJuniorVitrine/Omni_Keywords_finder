# Sistema de Variação Semanal - Omni Keywords Finder

## 📋 Visão Geral

O **Sistema de Variação Semanal** é uma solução inteligente que garante que o Omni Keywords Finder sempre busque palavras novas e sugira clusters diferentes a cada semana, eliminando completamente o problema de conteúdo repetido.

## 🎯 Objetivos

- ✅ **Eliminar repetição**: Nunca processar as mesmas keywords duas vezes
- ✅ **Variação automática**: Algoritmos diferentes a cada semana
- ✅ **Novidade garantida**: Sempre buscar keywords inéditas
- ✅ **Clusters únicos**: Evitar clusters repetidos
- ✅ **Tendências temporais**: Capturar mudanças semanais
- ✅ **Performance otimizada**: Cache inteligente para velocidade

## 🏗️ Arquitetura do Sistema

### 1. **Sistema de Memória Inteligente** (`infrastructure/memory/`)

```
infrastructure/memory/
├── __init__.py
└── historico_inteligente.py
```

**Funcionalidades:**
- Registro de keywords já processadas
- Histórico de clusters gerados
- Variação algorítmica semanal
- Detecção de novidade
- Sugestões de clusters alternativos

### 2. **Etapas Variadas** (`infrastructure/orchestrator/etapas/`)

```
infrastructure/orchestrator/etapas/
├── etapa_coleta_variada.py
├── etapa_processamento_variado.py
└── fluxo_completo_orchestrator_variado.py
```

**Funcionalidades:**
- Coleta com variação algorítmica
- Processamento adaptativo
- Geração de clusters únicos
- Integração com memória inteligente

### 3. **Script de Execução** (`scripts/`)

```
scripts/
└── executar_fluxo_semanal_variado.py
```

**Funcionalidades:**
- Execução automática semanal
- Verificação de necessidade
- Relatórios detalhados
- Execução manual

## 🔄 Variações Algorítmicas Semanais

### **Semana 1: Alta Diversidade**
```python
{
    "nome": "Alta Diversidade",
    "descricao": "Foco em diversidade semântica e novidade",
    "parametros": {
        "min_similaridade": 0.6,
        "max_clusters": 15,
        "diversidade_minima": 0.8
    },
    "peso_diversidade": 0.7,
    "peso_novidade": 0.8,
    "peso_tendencia": 0.3
}
```

**Estratégia:**
- Prioriza keywords com baixa similaridade
- Gera clusters com alta diversidade semântica
- Foca em novidade sobre tendências

### **Semana 2: Tendências Emergentes**
```python
{
    "nome": "Tendências Emergentes",
    "descricao": "Foco em tendências e volume de busca",
    "parametros": {
        "min_similaridade": 0.7,
        "max_clusters": 12,
        "volume_minimo": 1000
    },
    "peso_diversidade": 0.5,
    "peso_novidade": 0.6,
    "peso_tendencia": 0.9
}
```

**Estratégia:**
- Prioriza keywords com alto volume
- Foca em tendências emergentes
- Usa coletores de tendências (Google Trends, Twitter)

### **Semana 3: Cauda Longa**
```python
{
    "nome": "Cauda Longa",
    "descricao": "Foco em keywords de cauda longa e baixa concorrência",
    "parametros": {
        "min_similaridade": 0.5,
        "max_clusters": 20,
        "concorrencia_maxima": 0.4
    },
    "peso_diversidade": 0.8,
    "peso_novidade": 0.9,
    "peso_tendencia": 0.2
}
```

**Estratégia:**
- Prioriza keywords específicas e longas
- Foca em baixa concorrência
- Gera mais clusters menores

### **Semana 4: Otimização Balanceada**
```python
{
    "nome": "Otimização Balanceada",
    "descricao": "Balanceamento entre todos os fatores",
    "parametros": {
        "min_similaridade": 0.65,
        "max_clusters": 15,
        "score_minimo": 0.6
    },
    "peso_diversidade": 0.6,
    "peso_novidade": 0.7,
    "peso_tendencia": 0.6
}
```

**Estratégia:**
- Equilibra todos os fatores
- Otimiza para qualidade geral
- Mantém consistência

## 🚀 Como Funciona o Fluxo

### **1. Verificação de Necessidade**
```python
async def verificar_necessidade_execucao() -> bool:
    # Verifica se já foi executado esta semana
    # Verifica se é segunda-feira (dia de execução)
    # Retorna True se deve executar
```

### **2. Coleta Variada**
```python
async def executar_fluxo_completo():
    # 1. Coleta inicial de keywords
    keywords_coletadas = await self._coletar_keywords_inicial()
    
    # 2. Verificar novidade baseada no histórico
    keywords_novas, keywords_repetidas = await historico_inteligente.verificar_novidade_keywords()
    
    # 3. Se não há keywords suficientes novas, tentar variação
    if novidade_insuficiente:
        keywords_variadas = await self._coletar_keywords_variadas()
        keywords_novas.extend(keywords_variadas)
    
    # 4. Registrar keywords no histórico
    await historico_inteligente.registrar_keywords(keywords_novas)
```

### **3. Processamento Variado**
```python
async def _gerar_clusters_variados():
    # Obtém variação atual
    variacao = historico_inteligente._get_variacao_atual()
    
    # Ajusta parâmetros do clusterizador
    self._ajustar_clusterizador_por_variacao(variacao)
    
    # Gera clusters
    clusters = self.clusterizador.gerar_clusters(keywords)
    
    # Verifica novidade dos clusters
    clusters_novos, clusters_repetidos = await self._verificar_novidade_clusters()
    
    # Se não há clusters suficientes novos, gerar alternativos
    if clusters_novos_insuficientes:
        clusters_alternativos = await self._gerar_clusters_alternativos()
        clusters_novos.extend(clusters_alternativos)
```

### **4. Registro no Histórico**
```python
# Registra keywords
await historico_inteligente.registrar_keywords(keywords_novas, nicho, categoria)

# Registra clusters
for cluster in clusters_novos:
    await historico_inteligente.registrar_cluster(cluster, nicho, categoria)
```

## 📊 Métricas e Relatórios

### **Relatório de Execução Semanal**
```json
{
    "execucao": {
        "data": "2024-12-27T10:00:00",
        "semana": "semana_52",
        "variacao_algoritmica": "Alta Diversidade"
    },
    "resumo_executivo": {
        "nichos_processados": 5,
        "total_keywords_coletadas": 850,
        "total_keywords_novas": 680,
        "total_clusters_gerados": 120,
        "total_clusters_novos": 95,
        "novidade_keywords": 0.80,
        "novidade_clusters": 0.79
    },
    "performance_por_nicho": {
        "tecnologia": {
            "keywords_coletadas": 200,
            "keywords_novas": 160,
            "novidade_keywords": 0.80
        }
    }
}
```

### **Estatísticas de Histórico**
```json
{
    "keywords_por_semana": {
        "semana_51": 750,
        "semana_52": 850
    },
    "clusters_por_semana": {
        "semana_51": 110,
        "semana_52": 120
    },
    "variacoes_utilizadas": {
        "Alta Diversidade": 25,
        "Tendências Emergentes": 22,
        "Cauda Longa": 28,
        "Otimização Balanceada": 20
    }
}
```

## 🛠️ Como Usar

### **1. Execução Automática Semanal**
```bash
# Executa automaticamente na segunda-feira
python scripts/executar_fluxo_semanal_variado.py --modo semanal
```

### **2. Execução Manual**
```bash
# Executa para nicho específico
python scripts/executar_fluxo_semanal_variado.py --modo manual --nicho tecnologia --termos "smartphone 2024" "laptop gaming"
```

### **3. Verificar Estatísticas**
```python
from infrastructure.memory.historico_inteligente import historico_inteligente

# Estatísticas de um nicho
estatisticas = await historico_inteligente.obter_estatisticas_historico("tecnologia")

# Variação atual
variacao = historico_inteligente._get_variacao_atual()
print(f"Variação atual: {variacao.nome}")
```

## 🔧 Configuração

### **Configuração dos Nichos**
```python
NICHOS_CONFIG = {
    "tecnologia": {
        "termos_iniciais": [
            "melhor smartphone 2024",
            "laptop gaming",
            "inteligência artificial"
        ],
        "categoria": "tecnologia",
        "coletores_prioritarios": ["google_suggest", "google_trends", "youtube"],
        "max_keywords": 200,
        "min_score": 0.6
    }
}
```

### **Configuração do Orquestrador**
```python
orchestrator_variado = FluxoCompletoOrchestratorVariado({
    'coleta': {
        'max_keywords_por_fonte': 50,
        'min_novidade_porcentagem': 0.7,
        'max_tentativas_variacao': 3
    },
    'processamento': {
        'tamanho_cluster': 5,
        'min_similaridade': 0.6,
        'max_clusters': 20,
        'min_clusters_novos': 5
    }
})
```

## 📈 Benefícios

### **1. Eliminação de Repetição**
- ✅ Nunca processa as mesmas keywords
- ✅ Evita clusters duplicados
- ✅ Garante conteúdo sempre novo

### **2. Variação Inteligente**
- ✅ 4 estratégias diferentes por mês
- ✅ Adaptação automática por nicho
- ✅ Otimização contínua

### **3. Performance**
- ✅ Cache inteligente
- ✅ Execução paralela
- ✅ Relatórios detalhados

### **4. Qualidade**
- ✅ Novidade garantida
- ✅ Diversidade semântica
- ✅ Tendências capturadas

## 🔍 Monitoramento

### **Logs Estruturados**
```json
{
    "event": "fluxo_semanal_concluido",
    "status": "success",
    "source": "executar_fluxo_semanal",
    "details": {
        "nichos_processados": 5,
        "total_keywords": 850,
        "total_artigos": 95,
        "variacao_utilizada": "Alta Diversidade"
    }
}
```

### **Métricas de Performance**
- Tempo de execução por etapa
- Taxa de novidade (keywords e clusters)
- Uso de cache
- Erros e warnings

## 🚨 Troubleshooting

### **Problema: Baixa Taxa de Novidade**
**Solução:**
1. Verificar histórico de keywords
2. Ajustar parâmetros de variação
3. Adicionar novos coletores
4. Expandir termos iniciais

### **Problema: Clusters Repetidos**
**Solução:**
1. Verificar critérios de diversidade
2. Ajustar similaridade mínima
3. Limpar cache se necessário
4. Verificar configuração de variação

### **Problema: Performance Lenta**
**Solução:**
1. Verificar conexão com Redis
2. Otimizar consultas ao banco
3. Ajustar paralelização
4. Verificar recursos do sistema

## 📝 Próximos Passos

1. **Implementar mais variações algorítmicas**
2. **Adicionar machine learning para otimização**
3. **Criar dashboard de monitoramento**
4. **Implementar alertas automáticos**
5. **Adicionar mais coletores especializados**

---

**Tracing ID**: SISTEMA_VARIACAO_SEMANAL_001_20241227  
**Versão**: 1.0  
**Autor**: IA-Cursor  
**Data**: 2024-12-27 