/**
 * Componente de Tabela de Dados Otimizada - Omni Keywords Finder
 * 
 * Este componente demonstra o uso do hook useOptimizedQueries
 * com infinite scrolling, lazy loading e outras otimizações.
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import React, { useState, useCallback } from 'react';
import { useOptimizedQuery, useInfiniteScroll, useLazyLoad, useDebouncedQuery } from '../../hooks/useOptimizedQueries';

// Tipos para os dados
interface KeywordData {
  id: string;
  keyword: string;
  volume: number;
  difficulty: number;
  cpc: number;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
  category: string;
}

interface DataTableProps {
  title?: string;
  pageSize?: number;
  showSearch?: boolean;
  showFilters?: boolean;
  enableInfiniteScroll?: boolean;
  enableLazyLoading?: boolean;
}

// Mock API para demonstração
const mockApi = {
  fetchKeywords: async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    category?: string;
    status?: string;
  }): Promise<{ data: KeywordData[]; total: number }> => {
    // Simula delay de rede
    await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));

    const { page = 1, pageSize = 20, search = '', category = '', status = '' } = params;

    // Gera dados mock
    const mockData: KeywordData[] = Array.from({ length: pageSize }, (_, index) => ({
      id: `kw_${page}_${index}`,
      keyword: search ? `${search} keyword ${page}_${index}` : `keyword ${page}_${index}`,
      volume: Math.floor(Math.random() * 10000) + 100,
      difficulty: Math.floor(Math.random() * 100) + 1,
      cpc: Math.random() * 10,
      status: ['active', 'inactive', 'pending'][Math.floor(Math.random() * 3)] as any,
      created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      category: category || ['SEO', 'PPC', 'Content', 'Local'][Math.floor(Math.random() * 4)],
    }));

    // Filtra por search se fornecido
    const filteredData = search
      ? mockData.filter(item => item.keyword.toLowerCase().includes(search.toLowerCase()))
      : mockData;

    return {
      data: filteredData,
      total: 1000, // Total mock
    };
  },

  fetchKeywordDetails: async (id: string): Promise<KeywordData> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      id,
      keyword: `Detailed keyword ${id}`,
      volume: Math.floor(Math.random() * 10000) + 100,
      difficulty: Math.floor(Math.random() * 100) + 1,
      cpc: Math.random() * 10,
      status: 'active',
      created_at: new Date().toISOString(),
      category: 'SEO',
    };
  },
};

// Componente principal
export const OptimizedDataTable: React.FC<DataTableProps> = ({
  title = 'Keywords Otimizadas',
  pageSize = 20,
  showSearch = true,
  showFilters = true,
  enableInfiniteScroll = true,
  enableLazyLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Hook para busca debounced
  const { data: searchData, loading: searchLoading, error: searchError, setQueryKey } = useDebouncedQuery({
    key: 'keywords-search',
    fetcher: () => mockApi.fetchKeywords({ search: searchTerm, pageSize: 10 }),
    debounceTime: 500,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });

  // Hook para infinite scroll
  const {
    data: infiniteData,
    loading: infiniteLoading,
    error: infiniteError,
    hasMore,
    loadMore,
    reset: resetInfinite,
  } = useInfiniteScroll({
    key: 'keywords-infinite',
    fetcher: () => mockApi.fetchKeywords({ 
      pageSize, 
      category: selectedCategory, 
      status: selectedStatus 
    }).then(result => result.data), // Corrige o tipo de retorno
    pageSize,
    hasMore: (data) => data.length < 100, // Limite de 100 itens
    staleTime: 5 * 60 * 1000, // 5 minutos
    backgroundRefetch: true,
  });

  // Hook para lazy loading de detalhes
  const {
    data: lazyData,
    loading: lazyLoading,
    error: lazyError,
    elementRef: lazyRef,
  } = useLazyLoad({
    key: 'keywords-lazy-details',
    fetcher: () => mockApi.fetchKeywordDetails('lazy_example'),
    threshold: 200,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });

  // Hook para dados principais com cache persistente
  const [mainData, mainLoading, mainError, refetchMain] = useOptimizedQuery({
    key: 'keywords-main',
    fetcher: () => mockApi.fetchKeywords({ pageSize: 50 }),
    staleTime: 3 * 60 * 1000, // 3 minutos
    cacheTime: 15 * 60 * 1000, // 15 minutos
    backgroundRefetch: true,
    retryCount: 2,
  });

  // Handlers
  const handleSearch = useCallback((value: string) => {
    setSearchTerm(value);
    setQueryKey(`keywords-search-${value}`);
  }, [setQueryKey]);

  const handleCategoryChange = useCallback((category: string) => {
    setSelectedCategory(category);
    resetInfinite();
  }, [resetInfinite]);

  const handleStatusChange = useCallback((status: string) => {
    setSelectedStatus(status);
    resetInfinite();
  }, [resetInfinite]);

  const handleRefresh = useCallback(() => {
    refetchMain();
    resetInfinite();
  }, [refetchMain, resetInfinite]);

  // Dados para exibição
  const displayData = enableInfiniteScroll ? infiniteData : mainData?.data || [];

  return (
    <div style={{ margin: 16, padding: 16, border: '1px solid #d9d9d9', borderRadius: 8 }}>
      <h2>{title}</h2>
      
      {/* Barra de ferramentas */}
      <div style={{ marginBottom: 16 }}>
        {showSearch && (
          <div style={{ marginBottom: 8 }}>
            <input
              type="text"
              placeholder="Buscar keywords..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              style={{ 
                padding: '8px 12px', 
                border: '1px solid #d9d9d9', 
                borderRadius: 4, 
                width: 300,
                marginRight: 8
              }}
            />
            {searchLoading && <span>Carregando...</span>}
          </div>
        )}

        {showFilters && (
          <div style={{ marginBottom: 8 }}>
            <select
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              style={{ 
                padding: '8px 12px', 
                border: '1px solid #d9d9d9', 
                borderRadius: 4, 
                marginRight: 8
              }}
            >
              <option value="">Todas as categorias</option>
              <option value="SEO">SEO</option>
              <option value="PPC">PPC</option>
              <option value="Content">Content</option>
              <option value="Local">Local</option>
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => handleStatusChange(e.target.value)}
              style={{ 
                padding: '8px 12px', 
                border: '1px solid #d9d9d9', 
                borderRadius: 4, 
                marginRight: 8
              }}
            >
              <option value="">Todos os status</option>
              <option value="active">Ativo</option>
              <option value="inactive">Inativo</option>
              <option value="pending">Pendente</option>
            </select>
          </div>
        )}

        <button
          onClick={handleRefresh}
          disabled={mainLoading || infiniteLoading}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#1890ff', 
            color: 'white', 
            border: 'none', 
            borderRadius: 4,
            cursor: 'pointer'
          }}
        >
          {mainLoading || infiniteLoading ? 'Atualizando...' : 'Atualizar'}
        </button>
      </div>

      {/* Alertas de erro */}
      {(mainError || infiniteError || searchError) && (
        <div style={{ 
          padding: 12, 
          backgroundColor: '#fff2f0', 
          border: '1px solid #ffccc7', 
          borderRadius: 4, 
          marginBottom: 16,
          color: '#cf1322'
        }}>
          Erro ao carregar dados: {mainError?.message || infiniteError?.message || searchError?.message}
        </div>
      )}

      {/* Resultados da busca */}
      {searchTerm && searchData && (
        <div style={{ 
          padding: 12, 
          backgroundColor: '#f6ffed', 
          border: '1px solid #b7eb8f', 
          borderRadius: 4, 
          marginBottom: 16
        }}>
          <h4>Resultados da busca: "{searchTerm}"</h4>
          <div>
            {searchData.data.map(item => (
              <div key={item.id} style={{ padding: 4 }}>
                {item.keyword} - Volume: {item.volume.toLocaleString()}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabela principal */}
      <div style={{ marginBottom: 16 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#fafafa' }}>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Keyword</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Volume</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Dificuldade</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>CPC</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Status</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Categoria</th>
              <th style={{ padding: 12, textAlign: 'left', border: '1px solid #d9d9d9' }}>Criado em</th>
            </tr>
          </thead>
          <tbody>
            {displayData.map(item => (
              <tr key={item.id}>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>{item.keyword}</td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>
                  <span style={{ 
                    color: item.volume > 5000 ? '#52c41a' : item.volume > 1000 ? '#faad14' : '#ff4d4f' 
                  }}>
                    {item.volume.toLocaleString()}
                  </span>
                </td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>
                  <span style={{ 
                    color: item.difficulty < 30 ? '#52c41a' : item.difficulty < 70 ? '#faad14' : '#ff4d4f' 
                  }}>
                    {item.difficulty}%
                  </span>
                </td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>${item.cpc.toFixed(2)}</td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>
                  <span style={{ 
                    color: item.status === 'active' ? '#52c41a' : item.status === 'pending' ? '#faad14' : '#ff4d4f' 
                  }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>{item.category}</td>
                <td style={{ padding: 12, border: '1px solid #d9d9d9' }}>
                  {new Date(item.created_at).toLocaleDateString('pt-BR')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {(mainLoading || infiniteLoading) && (
          <div style={{ textAlign: 'center', padding: 20 }}>
            Carregando dados...
          </div>
        )}
      </div>

      {/* Botão de carregar mais (infinite scroll) */}
      {enableInfiniteScroll && hasMore && (
        <div style={{ textAlign: 'center', padding: 16 }}>
          <button
            onClick={loadMore}
            disabled={infiniteLoading}
            style={{ 
              padding: '8px 16px', 
              backgroundColor: '#1890ff', 
              color: 'white', 
              border: 'none', 
              borderRadius: 4,
              cursor: infiniteLoading ? 'not-allowed' : 'pointer',
              opacity: infiniteLoading ? 0.6 : 1
            }}
          >
            {infiniteLoading ? 'Carregando...' : 'Carregar Mais'}
          </button>
        </div>
      )}

      {/* Lazy loading demo */}
      {enableLazyLoading && (
        <div ref={lazyRef} style={{ 
          padding: 16, 
          border: '1px dashed #d9d9d9', 
          borderRadius: 6, 
          marginTop: 16 
        }}>
          <h4>Lazy Loading Demo</h4>
          {lazyLoading ? (
            <div>Carregando detalhes...</div>
          ) : lazyData ? (
            <div>
              <p><strong>Keyword:</strong> {lazyData.keyword}</p>
              <p><strong>Volume:</strong> {lazyData.volume.toLocaleString()}</p>
              <p><strong>Dificuldade:</strong> {lazyData.difficulty}%</p>
            </div>
          ) : (
            <p>Role para baixo para carregar dados...</p>
          )}
        </div>
      )}

      {/* Estatísticas */}
      <div style={{ 
        padding: 12, 
        backgroundColor: '#f6ffed', 
        border: '1px solid #b7eb8f', 
        borderRadius: 4,
        marginTop: 16
      }}>
        <h4>Estatísticas</h4>
        <div>
          <span>Total de itens: {displayData.length}</span>
          {enableInfiniteScroll && <span> | Has more: {hasMore ? 'Sim' : 'Não'}</span>}
          <span> | Última atualização: {new Date().toLocaleTimeString('pt-BR')}</span>
        </div>
      </div>
    </div>
  );
};

// Componente de exemplo de uso
export const OptimizedDataTableExample: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <h1>Exemplo de Tabela Otimizada</h1>
      <p>Este componente demonstra o uso do hook useOptimizedQueries com:</p>
      <ul>
        <li>✅ Query deduplication</li>
        <li>✅ Background refetching</li>
        <li>✅ Optimistic updates</li>
        <li>✅ Infinite scrolling</li>
        <li>✅ Lazy loading</li>
        <li>✅ Debounced search</li>
        <li>✅ Cache inteligente</li>
        <li>✅ Retry logic</li>
      </ul>

      <OptimizedDataTable
        title="Keywords com Otimizações Avançadas"
        pageSize={15}
        showSearch={true}
        showFilters={true}
        enableInfiniteScroll={true}
        enableLazyLoading={true}
      />
    </div>
  );
};

export default OptimizedDataTable; 