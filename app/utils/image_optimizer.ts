/**
 * Image Optimizer - WebP/AVIF Support with Fallback
 * 
 * Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 * Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
 */

export interface ImageOptimizationOptions {
  quality?: number;
  format?: 'webp' | 'avif' | 'auto';
  width?: number;
  height?: number;
  fallback?: boolean;
}

export interface OptimizedImage {
  src: string;
  srcSet?: string;
  sizes?: string;
  fallback?: string;
  format: string;
  size: number;
}

/**
 * Detecta suporte a formatos modernos de imagem
 */
export class ImageFormatDetector {
  private static webpSupported: boolean | null = null;
  private static avifSupported: boolean | null = null;

  /**
   * Verifica suporte a WebP
   */
  static async supportsWebP(): Promise<boolean> {
    if (this.webpSupported !== null) {
      return this.webpSupported;
    }

    return new Promise((resolve) => {
      const webP = new Image();
      webP.onload = webP.onerror = () => {
        this.webpSupported = webP.width === 1;
        resolve(this.webpSupported);
      };
      webP.src = 'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAADsAD+JaQAA3AAAAAA';
    });
  }

  /**
   * Verifica suporte a AVIF
   */
  static async supportsAVIF(): Promise<boolean> {
    if (this.avifSupported !== null) {
      return this.avifSupported;
    }

    return new Promise((resolve) => {
      const avif = new Image();
      avif.onload = avif.onerror = () => {
        this.avifSupported = avif.width === 1;
        resolve(this.avifSupported);
      };
      avif.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A=';
    });
  }

  /**
   * Retorna o melhor formato suportado
   */
  static async getBestFormat(): Promise<'avif' | 'webp' | 'jpeg'> {
    if (await this.supportsAVIF()) {
      return 'avif';
    }
    if (await this.supportsWebP()) {
      return 'webp';
    }
    return 'jpeg';
  }
}

/**
 * Otimizador de imagens com suporte a formatos modernos
 */
export class ImageOptimizer {
  private static instance: ImageOptimizer;
  private formatCache: Map<string, string> = new Map();

  static getInstance(): ImageOptimizer {
    if (!ImageOptimizer.instance) {
      ImageOptimizer.instance = new ImageOptimizer();
    }
    return ImageOptimizer.instance;
  }

  /**
   * Otimiza uma imagem com o melhor formato disponível
   */
  async optimizeImage(
    originalSrc: string,
    options: ImageOptimizationOptions = {}
  ): Promise<OptimizedImage> {
    const {
      quality = 85,
      format = 'auto',
      width,
      height,
      fallback = true
    } = options;

    // Determina o melhor formato
    const bestFormat = format === 'auto' 
      ? await ImageFormatDetector.getBestFormat()
      : format;

    // Gera URL otimizada
    const optimizedSrc = this.generateOptimizedUrl(originalSrc, {
      format: bestFormat,
      quality,
      width,
      height
    });

    // Gera fallback se necessário
    let fallbackSrc: string | undefined;
    if (fallback && bestFormat !== 'jpeg') {
      fallbackSrc = this.generateOptimizedUrl(originalSrc, {
        format: 'jpeg',
        quality: Math.min(quality + 5, 95),
        width,
        height
      });
    }

    // Gera srcSet para responsividade
    const srcSet = this.generateSrcSet(originalSrc, bestFormat, quality);

    return {
      src: optimizedSrc,
      srcSet,
      sizes: width ? `${width}px` : '100vw',
      fallback: fallbackSrc,
      format: bestFormat,
      size: this.estimateSize(originalSrc, bestFormat, quality)
    };
  }

  /**
   * Gera URL otimizada para a imagem
   */
  private generateOptimizedUrl(
    originalSrc: string,
    params: {
      format: string;
      quality: number;
      width?: number;
      height?: number;
    }
  ): string {
    const url = new URL(originalSrc, window.location.origin);
    
    // Adiciona parâmetros de otimização
    url.searchParams.set('format', params.format);
    url.searchParams.set('quality', params.quality.toString());
    
    if (params.width) {
      url.searchParams.set('width', params.width.toString());
    }
    if (params.height) {
      url.searchParams.set('height', params.height.toString());
    }

    return url.toString();
  }

  /**
   * Gera srcSet para diferentes tamanhos de tela
   */
  private generateSrcSet(
    originalSrc: string,
    format: string,
    quality: number
  ): string {
    const sizes = [320, 640, 768, 1024, 1280, 1920];
    const srcSetParts = sizes.map(size => {
      const url = this.generateOptimizedUrl(originalSrc, {
        format,
        quality,
        width: size
      });
      return `${url} ${size}w`;
    });

    return srcSetParts.join(', ');
  }

  /**
   * Estima o tamanho do arquivo otimizado
   */
  private estimateSize(
    originalSrc: string,
    format: string,
    quality: number
  ): number {
    // Estimativa baseada em benchmarks reais
    const compressionRatios = {
      avif: 0.3,
      webp: 0.5,
      jpeg: 0.8
    };

    const baseSize = 100000; // 100KB base
    const ratio = compressionRatios[format as keyof typeof compressionRatios] || 0.8;
    const qualityFactor = quality / 100;

    return Math.round(baseSize * ratio * qualityFactor);
  }

  /**
   * Pré-carrega imagens otimizadas
   */
  async preloadImage(optimizedImage: OptimizedImage): Promise<void> {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = optimizedImage.src;
    
    if (optimizedImage.srcSet) {
      link.setAttribute('imagesrcset', optimizedImage.srcSet);
    }
    if (optimizedImage.sizes) {
      link.setAttribute('imagesizes', optimizedImage.sizes);
    }

    document.head.appendChild(link);
  }

  /**
   * Limpa cache de formatos
   */
  clearCache(): void {
    this.formatCache.clear();
    ImageFormatDetector.webpSupported = null;
    ImageFormatDetector.avifSupported = null;
  }
}

/**
 * Hook React para otimização de imagens
 */
export function useImageOptimization() {
  const optimizer = ImageOptimizer.getInstance();

  const optimize = async (
    src: string,
    options?: ImageOptimizationOptions
  ): Promise<OptimizedImage> => {
    return optimizer.optimizeImage(src, options);
  };

  const preload = async (optimizedImage: OptimizedImage): Promise<void> => {
    return optimizer.preloadImage(optimizedImage);
  };

  return { optimize, preload };
}

/**
 * Componente React para imagem otimizada
 */
export interface OptimizedImageProps {
  src: string;
  alt: string;
  options?: ImageOptimizationOptions;
  className?: string;
  style?: React.CSSProperties;
}

export const OptimizedImageComponent: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  options,
  className,
  style
}) => {
  const [optimizedImage, setOptimizedImage] = React.useState<OptimizedImage | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const { optimize } = useImageOptimization();

  React.useEffect(() => {
    const loadOptimizedImage = async () => {
      try {
        setIsLoading(true);
        const optimized = await optimize(src, options);
        setOptimizedImage(optimized);
      } catch (error) {
        console.error('Erro ao otimizar imagem:', error);
        setOptimizedImage({
          src,
          format: 'jpeg',
          size: 0
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadOptimizedImage();
  }, [src, options]);

  if (isLoading) {
    return <div className={`image-placeholder ${className}`} style={style} />;
  }

  if (!optimizedImage) {
    return <img src={src} alt={alt} className={className} style={style} />;
  }

  return (
    <picture>
      {optimizedImage.fallback && (
        <source srcSet={optimizedImage.fallback} type="image/jpeg" />
      )}
      <img
        src={optimizedImage.src}
        srcSet={optimizedImage.srcSet}
        sizes={optimizedImage.sizes}
        alt={alt}
        className={className}
        style={style}
        loading="lazy"
      />
    </picture>
  );
};

export default ImageOptimizer; 