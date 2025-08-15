/**
 * Componente de Exemplo GraphQL - Omni Keywords Finder
 * 
 * Demonstra o uso do sistema GraphQL implementado:
 * - Queries otimizadas
 * - Mutations
 * - Cache inteligente
 * - Error handling
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import React, { useState } from 'react';
import {
  useNichos,
  useKeywords,
  useExecucoes,
  useBusinessMetrics,
  useCreateNicho,
  useCreateExecucao,
  clearGraphQLCache,
  getGraphQLCacheStats,
} from '../../hooks/useGraphQL';

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const GraphQLExample: React.FC = () => {
  const [selectedNicho, setSelectedNicho] = useState<string>('');
  const [newNichoName, setNewNichoName] = useState('');
  const [newNichoDesc, setNewNichoDesc] = useState('');

  // ===== QUERIES =====
  
  // Busca nichos
  const { data: nichos, loading: nichosLoading, error: nichosError, refetch: refetchNichos } = useNichos({
    fetchPolicy: 'cache-first',
    pollInterval: 30000, // Atualiza a cada 30 segundos
  });

  // Busca keywords com filtros
  const { data: keywords, loading: keywordsLoading, error: keywordsError } = useKeywords(
    selectedNicho ? { nicho_id: selectedNicho, limit: 50 } : undefined,
    { fetchPolicy: 'cache-and-network' }
  );

  // Busca execuções
  const { data: execucoes, loading: execucoesLoading, error: execucoesError } = useExecucoes(
    selectedNicho,
    { fetchPolicy: 'cache-first' }
  );

  // Busca métricas de negócio
  const { data: metrics, loading: metricsLoading, error: metricsError } = useBusinessMetrics(
    'roi',
    '30d',
    { fetchPolicy: 'network-only' }
  );

  // ===== MUTATIONS =====
  
  const { execute: createNicho, loading: createNichoLoading, error: createNichoError } = useCreateNicho();
  const { execute: createExecucao, loading: createExecucaoLoading, error: createExecucaoError } = useCreateExecucao();

  // ===== HANDLERS =====

  const handleCreateNicho = async () => {
    if (!newNichoName.trim()) return;

    try {
      const result = await createNicho({
        input: {
          nome: newNichoName,
          descricao: newNichoDesc,
          ativo: true,
        },
      });

      if (result.data?.createNicho?.success) {
        setNewNichoName('');
        setNewNichoDesc('');
        refetchNichos(); // Atualiza lista de nichos
        alert('Nicho criado com sucesso!');
      } else {
        alert(`Erro: ${result.data?.createNicho?.message}`);
      }
    } catch (error) {
      alert(`Erro ao criar nicho: ${error}`);
    }
  };

  const handleCreateExecucao = async () => {
    if (!selectedNicho) {
      alert('Selecione um nicho primeiro');
      return;
    }

    try {
      const result = await createExecucao({
        input: {
          nicho_id: selectedNicho,
          parametros: JSON.stringify({ limit: 100 }),
          agendada: false,
        },
      });

      if (result.data?.createExecucao?.success) {
        alert('Execução criada com sucesso!');
      } else {
        alert(`Erro: ${result.data?.createExecucao?.message}`);
      }
    } catch (error) {
      alert(`Erro ao criar execução: ${error}`);
    }
  };

  const handleClearCache = () => {
    clearGraphQLCache();
    alert('Cache limpo!');
  };

  const handleShowCacheStats = () => {
    const stats = getGraphQLCacheStats();
    alert(`Cache Stats:\nTamanho: ${stats.size}\nChaves: ${stats.keys.length}`);
  };

  // ===== RENDER =====

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>GraphQL Example - Omni Keywords Finder</h1>
      
      {/* ===== CONTROLES ===== */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h3>Controles</h3>
        
        <div style={{ marginBottom: '15px' }}>
          <label>Nicho Selecionado: </label>
          <select 
            value={selectedNicho} 
            onChange={(e) => setSelectedNicho(e.target.value)}
            style={{ marginLeft: '10px', padding: '5px' }}
          >
            <option value="">Selecione um nicho</option>
            {nichos?.nichos?.map((nicho: any) => (
              <option key={nicho.id} value={nicho.id}>
                {nicho.nome}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <button 
            onClick={refetchNichos}
            disabled={nichosLoading}
            style={{ marginRight: '10px', padding: '8px 16px' }}
          >
            {nichosLoading ? 'Atualizando...' : 'Atualizar Nichos'}
          </button>
          
          <button 
            onClick={handleClearCache}
            style={{ marginRight: '10px', padding: '8px 16px' }}
          >
            Limpar Cache
          </button>
          
          <button 
            onClick={handleShowCacheStats}
            style={{ padding: '8px 16px' }}
          >
            Stats do Cache
          </button>
        </div>
      </div>

      {/* ===== CRIAR NICHOS ===== */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h3>Criar Novo Nicho</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <label>Nome: </label>
          <input
            type="text"
            value={newNichoName}
            onChange={(e) => setNewNichoName(e.target.value)}
            placeholder="Nome do nicho"
            style={{ marginLeft: '10px', padding: '5px', width: '200px' }}
          />
        </div>
        
        <div style={{ marginBottom: '10px' }}>
          <label>Descrição: </label>
          <input
            type="text"
            value={newNichoDesc}
            onChange={(e) => setNewNichoDesc(e.target.value)}
            placeholder="Descrição do nicho"
            style={{ marginLeft: '10px', padding: '5px', width: '300px' }}
          />
        </div>
        
        <button 
          onClick={handleCreateNicho}
          disabled={createNichoLoading || !newNichoName.trim()}
          style={{ padding: '8px 16px' }}
        >
          {createNichoLoading ? 'Criando...' : 'Criar Nicho'}
        </button>
        
        {createNichoError && (
          <div style={{ color: 'red', marginTop: '10px' }}>
            Erro: {createNichoError.message}
          </div>
        )}
      </div>

      {/* ===== CRIAR EXECUÇÃO ===== */}
      <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h3>Criar Execução</h3>
        
        <button 
          onClick={handleCreateExecucao}
          disabled={createExecucaoLoading || !selectedNicho}
          style={{ padding: '8px 16px' }}
        >
          {createExecucaoLoading ? 'Criando...' : 'Criar Execução'}
        </button>
        
        {createExecucaoError && (
          <div style={{ color: 'red', marginTop: '10px' }}>
            Erro: {createExecucaoError.message}
          </div>
        )}
      </div>

      {/* ===== DADOS ===== */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        
        {/* Nichos */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Nichos {nichosLoading && '(Carregando...)'}</h3>
          
          {nichosError && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              Erro: {nichosError.message}
            </div>
          )}
          
          {nichos?.nichos?.length > 0 ? (
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {nichos.nichos.map((nicho: any) => (
                <div key={nicho.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #eee', borderRadius: '4px' }}>
                  <strong>{nicho.nome}</strong>
                  <br />
                  <small>{nicho.descricao}</small>
                  <br />
                  <span style={{ color: nicho.ativo ? 'green' : 'red' }}>
                    {nicho.ativo ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p>Nenhum nicho encontrado</p>
          )}
        </div>

        {/* Keywords */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Keywords {keywordsLoading && '(Carregando...)'}</h3>
          
          {keywordsError && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              Erro: {keywordsError.message}
            </div>
          )}
          
          {keywords?.keywords?.length > 0 ? (
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {keywords.keywords.slice(0, 10).map((keyword: any) => (
                <div key={keyword.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #eee', borderRadius: '4px' }}>
                  <strong>{keyword.keyword}</strong>
                  <br />
                  <small>
                    Volume: {keyword.volume} | 
                    Dificuldade: {keyword.dificuldade} | 
                    CPC: ${keyword.cpc}
                  </small>
                </div>
              ))}
              {keywords.keywords.length > 10 && (
                <p style={{ textAlign: 'center', color: '#666' }}>
                  ... e mais {keywords.keywords.length - 10} keywords
                </p>
              )}
            </div>
          ) : (
            <p>Nenhuma keyword encontrada</p>
          )}
        </div>

        {/* Execuções */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Execuções {execucoesLoading && '(Carregando...)'}</h3>
          
          {execucoesError && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              Erro: {execucoesError.message}
            </div>
          )}
          
          {execucoes?.execucoes?.length > 0 ? (
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {execucoes.execucoes.map((execucao: any) => (
                <div key={execucao.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #eee', borderRadius: '4px' }}>
                  <strong>Execução #{execucao.id}</strong>
                  <br />
                  <small>
                    Status: {execucao.status} | 
                    Início: {new Date(execucao.dataInicio).toLocaleString()}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <p>Nenhuma execução encontrada</p>
          )}
        </div>

        {/* Métricas */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
          <h3>Métricas de Negócio {metricsLoading && '(Carregando...)'}</h3>
          
          {metricsError && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              Erro: {metricsError.message}
            </div>
          )}
          
          {metrics?.businessMetrics?.length > 0 ? (
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {metrics.businessMetrics.map((metric: any) => (
                <div key={metric.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #eee', borderRadius: '4px' }}>
                  <strong>{metric.nome}</strong>
                  <br />
                  <small>
                    Valor: {metric.valor} | 
                    Tipo: {metric.tipo} | 
                    Tendência: {metric.tendencia}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <p>Nenhuma métrica encontrada</p>
          )}
        </div>
      </div>

      {/* ===== INFO ===== */}
      <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Informações do GraphQL</h3>
        <ul>
          <li><strong>Cache:</strong> Queries são cacheadas automaticamente por 5 minutos</li>
          <li><strong>Deduplication:</strong> Queries idênticas simultâneas são deduplicadas</li>
          <li><strong>Retry:</strong> Falhas são retentadas automaticamente com backoff exponencial</li>
          <li><strong>Polling:</strong> Nichos são atualizados automaticamente a cada 30 segundos</li>
          <li><strong>Error Handling:</strong> Erros são tratados e exibidos adequadamente</li>
          <li><strong>Type Safety:</strong> Tipagem completa com TypeScript</li>
        </ul>
      </div>
    </div>
  );
};

export default GraphQLExample; 