/**
 * Lazy Image Component - Intersection Observer Implementation
 * 
 * Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.1.2
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 * Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ImageOptimizationOptions, OptimizedImage, useImageOptimization } from '../../utils/image_optimizer';

export interface LazyImageProps {
  src: string;
  alt: string;
  placeholder?: string;
  threshold?: number;
  rootMargin?: string;
  optimizationOptions?: ImageOptimizationOptions;
  className?: string;
  style?: React.CSSProperties;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  fallbackSrc?: string;
  preload?: boolean;
}

export interface LazyImageState {
  isLoaded: boolean;
  isInView: boolean;
  hasError: boolean;
  optimizedImage: OptimizedImage | null;
}

/**
 * Hook para Intersection Observer
 */
function useIntersectionObserver(
  elementRef: React.RefObject<HTMLElement>,
  options: {
    threshold?: number;
    rootMargin?: string;
    enabled?: boolean;
  } = {}
): boolean {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const { threshold = 0.1, rootMargin = '50px', enabled = true } = options;

  useEffect(() => {
    const element = elementRef.current;
    if (!element || !enabled) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, threshold, rootMargin, enabled]);

  return isIntersecting;
}

/**
 * Componente de placeholder para imagem
 */
const ImagePlaceholder: React.FC<{
  src?: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
}> = ({ src, alt, className, style }) => {
  if (src) {
    return (
      <img
        src={src}
        alt={`${alt} placeholder`}
        className={`lazy-image-placeholder ${className || ''}`}
        style={{
          filter: 'blur(10px)',
          transform: 'scale(1.1)',
          transition: 'filter 0.3s ease-out',
          ...style
        }}
      />
    );
  }

  return (
    <div
      className={`lazy-image-placeholder ${className || ''}`}
      style={{
        backgroundColor: '#f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#666',
        fontSize: '14px',
        ...style
      }}
    >
      <svg
        width="40"
        height="40"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21,15 16,10 5,21" />
      </svg>
    </div>
  );
};

/**
 * Componente principal de Lazy Image
 */
export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder,
  threshold = 0.1,
  rootMargin = '50px',
  optimizationOptions,
  className,
  style,
  onLoad,
  onError,
  fallbackSrc,
  preload = false
}) => {
  const imageRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<LazyImageState>({
    isLoaded: false,
    isInView: false,
    hasError: false,
    optimizedImage: null
  });

  const { optimize } = useImageOptimization();
  const isInView = useIntersectionObserver(imageRef, {
    threshold,
    rootMargin,
    enabled: !state.isLoaded
  });

  // Atualiza estado quando imagem entra na viewport
  useEffect(() => {
    if (isInView && !state.isInView) {
      setState(prev => ({ ...prev, isInView: true }));
    }
  }, [isInView, state.isInView]);

  // Carrega imagem quando entra na viewport
  useEffect(() => {
    if (!state.isInView || state.isLoaded || state.hasError) return;

    const loadImage = async () => {
      try {
        let optimizedImage: OptimizedImage | null = null;

        // Otimiza imagem se opções fornecidas
        if (optimizationOptions) {
          optimizedImage = await optimize(src, optimizationOptions);
        } else {
          // Cria objeto básico se não houver otimização
          optimizedImage = {
            src,
            format: 'jpeg',
            size: 0
          };
        }

        // Pré-carrega se solicitado
        if (preload && optimizedImage) {
          const link = document.createElement('link');
          link.rel = 'preload';
          link.as = 'image';
          link.href = optimizedImage.src;
          document.head.appendChild(link);
        }

        setState(prev => ({
          ...prev,
          optimizedImage,
          isLoaded: true
        }));

        onLoad?.();
      } catch (error) {
        console.error('Erro ao carregar imagem:', error);
        setState(prev => ({
          ...prev,
          hasError: true
        }));
        onError?.(error as Error);
      }
    };

    loadImage();
  }, [state.isInView, state.isLoaded, state.hasError, src, optimizationOptions, preload, onLoad, onError, optimize]);

  // Renderiza placeholder enquanto não carregou
  if (!state.isLoaded && !state.hasError) {
    return (
      <div ref={imageRef} className={`lazy-image-container ${className || ''}`} style={style}>
        <ImagePlaceholder
          src={placeholder}
          alt={alt}
          className="lazy-image-placeholder"
        />
      </div>
    );
  }

  // Renderiza fallback em caso de erro
  if (state.hasError && fallbackSrc) {
    return (
      <div ref={imageRef} className={`lazy-image-container ${className || ''}`} style={style}>
        <img
          src={fallbackSrc}
          alt={alt}
          className="lazy-image-fallback"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
        />
      </div>
    );
  }

  // Renderiza imagem otimizada
  if (state.optimizedImage) {
    return (
      <div ref={imageRef} className={`lazy-image-container ${className || ''}`} style={style}>
        <picture>
          {state.optimizedImage.fallback && (
            <source srcSet={state.optimizedImage.fallback} type="image/jpeg" />
          )}
          <img
            src={state.optimizedImage.src}
            srcSet={state.optimizedImage.srcSet}
            sizes={state.optimizedImage.sizes}
            alt={alt}
            className="lazy-image-loaded"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: state.isLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease-in-out'
            }}
            onLoad={() => {
              setState(prev => ({ ...prev, isLoaded: true }));
              onLoad?.();
            }}
            onError={(e) => {
              console.error('Erro ao carregar imagem otimizada:', e);
              setState(prev => ({ ...prev, hasError: true }));
              onError?.(new Error('Falha ao carregar imagem'));
            }}
          />
        </picture>
      </div>
    );
  }

  // Fallback para imagem simples
  return (
    <div ref={imageRef} className={`lazy-image-container ${className || ''}`} style={style}>
      <img
        src={src}
        alt={alt}
        className="lazy-image-simple"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          opacity: state.isLoaded ? 1 : 0,
          transition: 'opacity 0.3s ease-in-out'
        }}
        onLoad={() => {
          setState(prev => ({ ...prev, isLoaded: true }));
          onLoad?.();
        }}
        onError={(e) => {
          console.error('Erro ao carregar imagem:', e);
          setState(prev => ({ ...prev, hasError: true }));
          onError?.(new Error('Falha ao carregar imagem'));
        }}
      />
    </div>
  );
};

/**
 * Hook para gerenciar múltiplas imagens lazy
 */
export function useLazyImages() {
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());

  const markAsLoaded = useCallback((src: string) => {
    setLoadedImages(prev => new Set(prev).add(src));
  }, []);

  const isLoaded = useCallback((src: string) => {
    return loadedImages.has(src);
  }, [loadedImages]);

  const clearLoadedImages = useCallback(() => {
    setLoadedImages(new Set());
  }, []);

  return {
    loadedImages: Array.from(loadedImages),
    markAsLoaded,
    isLoaded,
    clearLoadedImages
  };
}

/**
 * Componente de grid de imagens lazy
 */
export interface LazyImageGridProps {
  images: Array<{
    src: string;
    alt: string;
    optimizationOptions?: ImageOptimizationOptions;
  }>;
  columns?: number;
  gap?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const LazyImageGrid: React.FC<LazyImageGridProps> = ({
  images,
  columns = 3,
  gap = 16,
  className,
  style
}) => {
  return (
    <div
      className={`lazy-image-grid ${className || ''}`}
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: `${gap}px`,
        ...style
      }}
    >
      {images.map((image, index) => (
        <LazyImage
          key={`${image.src}-${index}`}
          src={image.src}
          alt={image.alt}
          optimizationOptions={image.optimizationOptions}
          threshold={0.1}
          rootMargin="100px"
        />
      ))}
    </div>
  );
};

export default LazyImage; 