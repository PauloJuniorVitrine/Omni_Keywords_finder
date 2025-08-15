/**
 * Sistema de Otimização de Imagens
 * Melhora performance de carregamento através de otimização automática de imagens
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';

// Tipos para configuração de otimização
interface ImageOptimizationConfig {
  quality?: number;
  format?: 'webp' | 'avif' | 'jpeg' | 'png';
  width?: number;
  height?: number;
  lazy?: boolean;
  placeholder?: 'blur' | 'color' | 'none';
  preload?: boolean;
  retryAttempts?: number;
}

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  config?: ImageOptimizationConfig;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

// Configuração padrão
const DEFAULT_CONFIG: ImageOptimizationConfig = {
  quality: 85,
  format: 'webp',
  lazy: true,
  placeholder: 'blur',
  preload: false,
  retryAttempts: 3
};

/**
 * Utilitários para otimização de imagens
 */
class ImageOptimizer {
  private cache = new Map<string, string>();
  private loadingImages = new Set<string>();
  private failedImages = new Set<string>();

  /**
   * Otimiza URL da imagem
   */
  optimizeImageUrl(
    originalUrl: string,
    config: ImageOptimizationConfig = {}
  ): string {
    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    
    // Se já está em cache, retorna
    const cacheKey = `${originalUrl}-${JSON.stringify(finalConfig)}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    // Em produção, isso seria uma transformação real da URL
    // Por exemplo, usando CDN como Cloudinary, ImageKit, etc.
    let optimizedUrl = originalUrl;

    // Adicionar parâmetros de otimização
    const params = new URLSearchParams();
    
    if (finalConfig.quality) {
      params.append('q', finalConfig.quality.toString());
    }
    
    if (finalConfig.format) {
      params.append('f', finalConfig.format);
    }
    
    if (finalConfig.width) {
      params.append('w', finalConfig.width.toString());
    }
    
    if (finalConfig.height) {
      params.append('h', finalConfig.height.toString());
    }

    if (params.toString()) {
      optimizedUrl += `?${params.toString()}`;
    }

    // Cache da URL otimizada
    this.cache.set(cacheKey, optimizedUrl);
    
    return optimizedUrl;
  }

  /**
   * Gera placeholder para imagem
   */
  generatePlaceholder(
    width: number,
    height: number,
    type: 'blur' | 'color' = 'blur'
  ): string {
    if (type === 'blur') {
      // Em produção, isso seria um placeholder real com blur
      return `data:image/svg+xml;base64,${btoa(`
        <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
          <rect width="100%" height="100%" fill="#f0f0f0"/>
          <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999">Carregando...</text>
        </svg>
      `)}`;
    } else {
      // Placeholder colorido
      const colors = ['#f0f0f0', '#e0e0e0', '#d0d0d0'];
      const color = colors[Math.floor(Math.random() * colors.length)];
      return `data:image/svg+xml;base64,${btoa(`
        <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
          <rect width="100%" height="100%" fill="${color}"/>
        </svg>
      `)}`;
    }
  }

  /**
   * Preload de imagem
   */
  async preloadImage(url: string): Promise<void> {
    if (this.loadingImages.has(url)) {
      return;
    }

    this.loadingImages.add(url);

    try {
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = url;
      });
    } catch (error) {
      this.failedImages.add(url);
      throw error;
    } finally {
      this.loadingImages.delete(url);
    }
  }

  /**
   * Verifica se imagem está carregada
   */
  isImageLoaded(url: string): boolean {
    return !this.loadingImages.has(url) && !this.failedImages.has(url);
  }

  /**
   * Limpa cache
   */
  clearCache() {
    this.cache.clear();
    this.loadingImages.clear();
    this.failedImages.clear();
  }
}

// Instância global do otimizador
export const imageOptimizer = new ImageOptimizer();

/**
 * Hook para otimização de imagem
 */
export function useImageOptimization(
  src: string,
  config: ImageOptimizationConfig = {}
) {
  const [optimizedSrc, setOptimizedSrc] = useState<string>('');
  const [placeholder, setPlaceholder] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [loaded, setLoaded] = useState(false);

  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  useEffect(() => {
    if (!src) return;

    const optimizedUrl = imageOptimizer.optimizeImageUrl(src, finalConfig);
    setOptimizedSrc(optimizedUrl);

    // Gerar placeholder
    if (finalConfig.placeholder !== 'none') {
      const placeholderUrl = imageOptimizer.generatePlaceholder(
        finalConfig.width || 300,
        finalConfig.height || 200,
        finalConfig.placeholder
      );
      setPlaceholder(placeholderUrl);
    }

    setLoading(true);
    setError(null);
    setLoaded(false);

    // Preload se configurado
    if (finalConfig.preload) {
      imageOptimizer.preloadImage(optimizedUrl)
        .then(() => {
          setLoaded(true);
          setLoading(false);
        })
        .catch((err) => {
          setError(err);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [src, finalConfig]);

  return {
    optimizedSrc,
    placeholder,
    loading,
    error,
    loaded,
    isOptimized: optimizedSrc !== src
  };
}

/**
 * Componente de imagem otimizada
 */
export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
  config,
  onLoad,
  onError,
  ...props
}: OptimizedImageProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const imgRef = useRef<HTMLImageElement>(null);

  const {
    optimizedSrc,
    placeholder,
    loading,
    error,
    loaded
  } = useImageOptimization(src, { width, height, ...config });

  const finalConfig = { ...DEFAULT_CONFIG, ...config };

  const handleLoad = useCallback(() => {
    setImageLoaded(true);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback((error: Event) => {
    const imgError = error as ErrorEvent;
    
    if (retryCount < finalConfig.retryAttempts!) {
      setRetryCount(prev => prev + 1);
      // Tentar novamente com delay
      setTimeout(() => {
        if (imgRef.current) {
          imgRef.current.src = optimizedSrc;
        }
      }, 1000 * (retryCount + 1));
    } else {
      onError?.(new Error(`Failed to load image after ${finalConfig.retryAttempts} attempts`));
    }
  }, [retryCount, finalConfig.retryAttempts, optimizedSrc, onError]);

  // Lazy loading com Intersection Observer
  const [isInView, setIsInView] = useState(!finalConfig.lazy);

  useEffect(() => {
    if (!finalConfig.lazy || !imgRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1
      }
    );

    observer.observe(imgRef.current);

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [finalConfig.lazy]);

  if (error) {
    return (
      <div 
        className={`image-error ${className || ''}`}
        style={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <span>Erro ao carregar imagem</span>
      </div>
    );
  }

  return (
    <div className={`optimized-image-container ${className || ''}`}>
      {/* Placeholder */}
      {placeholder && !imageLoaded && (
        <img
          src={placeholder}
          alt=""
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(10px)',
            transition: 'opacity 0.3s ease'
          }}
        />
      )}
      
      {/* Imagem principal */}
      {isInView && (
        <img
          ref={imgRef}
          src={optimizedSrc}
          alt={alt}
          width={width}
          height={height}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            opacity: imageLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease',
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
          loading={finalConfig.lazy ? 'lazy' : 'eager'}
          {...props}
        />
      )}
      
      {/* Loading spinner */}
      {loading && !imageLoaded && (
        <div className="image-loading">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
}

/**
 * Hook para lazy loading de imagens
 */
export function useLazyImage(
  src: string,
  options: IntersectionObserverInit = {}
) {
  const [isInView, setIsInView] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const ref = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
        ...options
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [options]);

  useEffect(() => {
    if (!isInView || !ref.current) return;

    const img = ref.current;
    img.src = src;

    const handleLoad = () => setLoaded(true);
    const handleError = () => setError(new Error('Failed to load image'));

    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);

    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
    };
  }, [isInView, src]);

  return { ref, isInView, loaded, error };
}

/**
 * Componente de imagem com lazy loading
 */
export function LazyImage({
  src,
  alt,
  width,
  height,
  className,
  observerOptions,
  ...props
}: {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  observerOptions?: IntersectionObserverInit;
} & Record<string, any>) {
  const { ref, isInView, loaded, error } = useLazyImage(src, observerOptions);

  if (error) {
    return (
      <div 
        className={`lazy-image-error ${className || ''}`}
        style={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <span>Erro ao carregar imagem</span>
      </div>
    );
  }

  return (
    <div className={`lazy-image-container ${className || ''}`}>
      {isInView && (
        <img
          ref={ref}
          alt={alt}
          width={width}
          height={height}
          style={{
            opacity: loaded ? 1 : 0,
            transition: 'opacity 0.3s ease',
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
          {...props}
        />
      )}
      
      {!loaded && (
        <div className="lazy-image-placeholder">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
}

/**
 * Sistema de cache de imagens
 */
class ImageCache {
  private cache = new Map<string, {
    data: string;
    timestamp: number;
    size: number;
  }>();
  private maxSize = 50 * 1024 * 1024; // 50MB
  private currentSize = 0;

  /**
   * Adiciona imagem ao cache
   */
  set(key: string, data: string, size: number) {
    // Limpar cache se necessário
    if (this.currentSize + size > this.maxSize) {
      this.cleanup();
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      size
    });
    this.currentSize += size;
  }

  /**
   * Obtém imagem do cache
   */
  get(key: string): string | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // Verificar se expirou (1 hora)
    if (Date.now() - item.timestamp > 60 * 60 * 1000) {
      this.delete(key);
      return null;
    }

    return item.data;
  }

  /**
   * Verifica se imagem está em cache
   */
  has(key: string): boolean {
    return this.cache.has(key);
  }

  /**
   * Remove imagem do cache
   */
  delete(key: string) {
    const item = this.cache.get(key);
    if (item) {
      this.currentSize -= item.size;
      this.cache.delete(key);
    }
  }

  /**
   * Limpa cache
   */
  clear() {
    this.cache.clear();
    this.currentSize = 0;
  }

  /**
   * Limpa cache antigo
   */
  private cleanup() {
    const entries = Array.from(this.cache.entries())
      .sort((a, b) => a[1].timestamp - b[1].timestamp);

    for (const [key, item] of entries) {
      if (this.currentSize <= this.maxSize * 0.8) break;
      this.delete(key);
    }
  }
}

// Instância global do cache de imagens
export const imageCache = new ImageCache();

/**
 * Hook para cache de imagens
 */
export function useImageCache(src: string) {
  const [cachedData, setCachedData] = useState<string | null>(null);

  useEffect(() => {
    const cached = imageCache.get(src);
    if (cached) {
      setCachedData(cached);
    }
  }, [src]);

  const cacheImage = useCallback((data: string, size: number) => {
    imageCache.set(src, data, size);
    setCachedData(data);
  }, [src]);

  return { cachedData, cacheImage };
}

/**
 * Utilitários para otimização de imagens
 */
export const ImageOptimizationUtils = {
  /**
   * Otimiza múltiplas imagens
   */
  optimizeImages: (images: string[], config: ImageOptimizationConfig = {}) => {
    return images.map(src => imageOptimizer.optimizeImageUrl(src, config));
  },

  /**
   * Preload de múltiplas imagens
   */
  preloadImages: async (urls: string[]) => {
    const preloadPromises = urls.map(url => 
      imageOptimizer.preloadImage(url).catch(error => {
        console.warn(`Failed to preload image ${url}:`, error);
      })
    );

    await Promise.all(preloadPromises);
  },

  /**
   * Limpa todos os caches
   */
  clearAllCaches: () => {
    imageOptimizer.clearCache();
    imageCache.clear();
  },

  /**
   * Obtém estatísticas de cache
   */
  getCacheStats: () => {
    return {
      optimizerCacheSize: imageOptimizer.cache.size,
      imageCacheSize: imageCache.cache.size,
      imageCacheCurrentSize: imageCache.currentSize
    };
  }
};

// Estilos CSS para componentes
export const imageStyles = `
  .optimized-image-container {
    position: relative;
    overflow: hidden;
  }

  .image-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .lazy-image-container {
    position: relative;
    overflow: hidden;
  }

  .lazy-image-placeholder {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  .image-error,
  .lazy-image-error {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #6c757d;
    font-size: 14px;
  }
`; 