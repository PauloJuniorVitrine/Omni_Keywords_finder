/**
 * Componente de Lista Otimizada - Omni Keywords Finder
 * 
 * Demonstra o uso de todas as otimizações de performance:
 * - Virtualização para listas grandes
 * - Lazy loading de imagens
 * - Memoização de componentes
 * - Debounce e throttle
 * - Infinite scrolling
 * 
 * Autor: Sistema Omni Keywords Finder
 * Data: 2024-12-19
 * Versão: 1.0.0
 */

import React, { memo, useCallback, useState } from 'react';
import {
  useOptimizedQuery,
  useInfiniteScroll,
  useLazyLoad,
  useVirtualization,
  useLazyImage,
  useDebounce,
  useThrottle,
  useComponentOptimization,
} from '../../hooks/useOptimizedQueries';

// Interface para item da lista
interface ListItem {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  timestamp: number;
}

// Props do componente
interface OptimizedListProps {
  items: ListItem[];
  onItemClick?: (item: ListItem) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loading?: boolean;
  itemHeight?: number;
  containerHeight?: number;
  searchTerm?: string;
}

// Componente de item individual (memoizado)
const ListItemComponent = memo<{
  item: ListItem;
  onClick?: (item: ListItem) => void;
  height: number;
}>(({ item, onClick, height }) => {
  // Otimização de props
  const { memoizedProps } = useComponentOptimization(
    { item, onClick, height },
    ['item', 'onClick', 'height']
  );

  // Lazy loading de imagem
  const { isLoaded, src, imgRef } = useLazyImage(
    item.imageUrl || '/placeholder.png',
    '/placeholder.png'
  );

  const handleClick = useCallback(() => {
    onClick?.(item);
  }, [onClick, item]);

  return (
    <div
      style={{
        height: `${height}px`,
        border: '1px solid #eee',
        padding: '12px',
        margin: '4px 0',
        borderRadius: '8px',
        cursor: onClick ? 'pointer' : 'default',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}
      onClick={handleClick}
    >
      {item.imageUrl && (
        <img
          ref={imgRef}
          src={src}
          alt={item.title}
          style={{
            width: '60px',
            height: '60px',
            objectFit: 'cover',
            borderRadius: '4px',
            opacity: isLoaded ? 1 : 0.5,
            transition: 'opacity 0.3s ease',
          }}
        />
      )}
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: '0 0 4px 0', fontSize: '16px' }}>
          {item.title}
        </h4>
        <p style={{ margin: '0', fontSize: '14px', color: '#666' }}>
          {item.description}
        </p>
        <small style={{ color: '#999' }}>
          {new Date(item.timestamp).toLocaleDateString()}
        </small>
      </div>
    </div>
  );
});

ListItemComponent.displayName = 'ListItemComponent';

// Componente principal
export const OptimizedList: React.FC<OptimizedListProps> = ({
  items,
  onItemClick,
  onLoadMore,
  hasMore = false,
  loading = false,
  itemHeight = 80,
  containerHeight = 400,
  searchTerm = '',
}) => {
  // Debounce do termo de busca
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Throttle para scroll
  const throttledScroll = useThrottle((event: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = event.currentTarget;
    
    // Carrega mais itens quando chega próximo ao final
    if (scrollHeight - scrollTop - clientHeight < 100 && hasMore && !loading) {
      onLoadMore?.();
    }
  }, 100);

  // Virtualização para listas grandes
  const {
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
  } = useVirtualization(items, itemHeight, containerHeight, 10);

  // Combina scroll handlers
  const handleCombinedScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    handleScroll(event);
    throttledScroll(event);
  }, [handleScroll, throttledScroll]);

  // Filtra itens baseado no termo de busca
  const filteredItems = React.useMemo(() => {
    if (!debouncedSearchTerm) return items;
    
    return items.filter(item =>
      item.title.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
      item.description.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
    );
  }, [items, debouncedSearchTerm]);

  // Aplica virtualização aos itens filtrados
  const virtualizedItems = React.useMemo(() => {
    if (filteredItems.length > 1000) {
      // Usa virtualização para listas muito grandes
      return visibleItems;
    }
    return filteredItems;
  }, [filteredItems, visibleItems]);

  return (
    <div
      style={{
        height: `${containerHeight}px`,
        overflow: 'auto',
        border: '1px solid #ddd',
        borderRadius: '8px',
        position: 'relative',
      }}
      onScroll={handleCombinedScroll}
    >
      <div
        style={{
          height: `${totalHeight}px`,
          position: 'relative',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: `${offsetY}px`,
            left: 0,
            right: 0,
          }}
        >
          {virtualizedItems.map((item, index) => (
            <ListItemComponent
              key={item.id}
              item={item}
              onClick={onItemClick}
              height={itemHeight}
            />
          ))}
        </div>
      </div>
      
      {loading && (
        <div
          style={{
            position: 'absolute',
            bottom: '0',
            left: '0',
            right: '0',
            padding: '12px',
            textAlign: 'center',
            background: 'rgba(255, 255, 255, 0.9)',
            borderTop: '1px solid #eee',
          }}
        >
          Carregando mais itens...
        </div>
      )}
    </div>
  );
};

// Hook customizado para usar a lista otimizada
export const useOptimizedList = (
  initialItems: ListItem[],
  searchTerm: string = ''
) => {
  const [items, setItems] = useState<ListItem[]>(initialItems);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  // Query otimizada para buscar mais itens
  const [data, queryLoading, error, refetch] = useOptimizedQuery<ListItem[]>({
    key: `optimized-list-${searchTerm}`,
    fetcher: async () => {
      // Simula busca de dados
      await new Promise(resolve => setTimeout(resolve, 1000));
      return Array.from({ length: 20 }, (_, i) => ({
        id: `item-${Date.now()}-${i}`,
        title: `Item ${items.length + i + 1}`,
        description: `Descrição do item ${items.length + i + 1}`,
        imageUrl: `https://picsum.photos/60/60?random=${items.length + i}`,
        timestamp: Date.now() - Math.random() * 86400000,
      }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
    backgroundRefetch: true,
    deduplication: true,
  });

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      await refetch();
      if (data) {
        setItems(prev => [...prev, ...data]);
        setHasMore(data.length === 20); // Assume que 20 é o tamanho da página
      }
    } finally {
      setLoading(false);
    }
  }, [loading, hasMore, refetch, data]);

  return {
    items,
    loading: loading || queryLoading,
    error,
    hasMore,
    loadMore,
    refetch,
  };
};

export default OptimizedList; 