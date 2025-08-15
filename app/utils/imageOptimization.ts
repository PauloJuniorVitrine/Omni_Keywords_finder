/**
 * Sistema de Otimização de Imagens
 * Otimiza automaticamente imagens para melhor performance
 * 
 * Tracing ID: IMAGE_OPTIMIZATION_001
 * Data: 2025-01-27
 * Versão: 1.0.0
 */

// Tipos para configuração de otimização
interface ImageOptimizationConfig {
  quality?: number;
  format?: 'webp' | 'avif' | 'jpeg' | 'png';
  width?: number;
  height?: number;
  lazy?: boolean;
  placeholder?: boolean;
  blur?: number;
}

interface OptimizedImage {
  src: string;
  srcSet?: string;
  sizes?: string;
  placeholder?: string;
  width: number;
  height: number;
  format: string;
  size: number;
}

// Configuração padrão
const DEFAULT_CONFIG: ImageOptimizationConfig = {
  quality: 85,
  format: 'webp',
  lazy: true,
  placeholder: true,
  blur: 10
};

/**
 * Verifica suporte a formatos de imagem
 */
class ImageFormatSupport {
  private static webpSupported: boolean | null = null;
  private static avifSupported: boolean | null = null;

  /**
   * Verifica suporte a WebP
   */
  static async checkWebPSupport(): Promise<boolean> {
    if (this.webpSupported !== null) {
      return this.webpSupported;
    }

    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    
    try {
      const dataURL = canvas.toDataURL('image/webp');
      this.webpSupported = dataURL.indexOf('data:image/webp') === 0;
    } catch (error) {
      this.webpSupported = false;
    }

    return this.webpSupported;
  }

  /**
   * Verifica suporte a AVIF
   */
  static async checkAVIFSupport(): Promise<boolean> {
    if (this.avifSupported !== null) {
      return this.avifSupported;
    }

    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    
    try {
      const dataURL = canvas.toDataURL('image/avif');
      this.avifSupported = dataURL.indexOf('data:image/avif') === 0;
    } catch (error) {
      this.avifSupported = false;
    }

    return this.avifSupported;
  }

  /**
   * Obtém melhor formato suportado
   */
  static async getBestFormat(): Promise<string> {
    const avifSupported = await this.checkAVIFSupport();
    if (avifSupported) return 'avif';

    const webpSupported = await this.checkWebPSupport();
    if (webpSupported) return 'webp';

    return 'jpeg';
  }
}

/**
 * Gera placeholder blur
 */
class PlaceholderGenerator {
  /**
   * Gera placeholder base64
   */
  static async generatePlaceholder(
    width: number,
    height: number,
    blur: number = 10
  ): Promise<string> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      throw new Error('Canvas context not available');
    }

    canvas.width = width;
    canvas.height = height;

    // Criar gradiente simples
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#f0f0f0');
    gradient.addColorStop(1, '#e0e0e0');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Aplicar blur se suportado
    if ('filter' in ctx) {
      (ctx as any).filter = `blur(${blur}px)`;
      ctx.fillRect(0, 0, width, height);
    }

    return canvas.toDataURL('image/jpeg', 0.1);
  }

  /**
   * Gera placeholder SVG
   */
  static generateSVGPlaceholder(
    width: number,
    height: number,
    text: string = 'Loading...'
  ): string {
    return `
      <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f0f0f0"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#666" font-family="Arial, sans-serif" font-size="14">
          ${text}
        </text>
      </svg>
    `;
  }
}

/**
 * Otimizador de imagens
 */
class ImageOptimizer {
  private static cache = new Map<string, OptimizedImage>();

  /**
   * Otimiza uma imagem
   */
  static async optimizeImage(
    src: string,
    config: ImageOptimizationConfig = {}
  ): Promise<OptimizedImage> {
    const cacheKey = `${src}_${JSON.stringify(config)}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    const bestFormat = await ImageFormatSupport.getBestFormat();

    try {
      const image = await this.loadImage(src);
      const optimized = await this.processImage(image, finalConfig, bestFormat);
      
      this.cache.set(cacheKey, optimized);
      return optimized;
    } catch (error) {
      console.error('Image optimization failed:', error);
      throw error;
    }
  }

  /**
   * Carrega imagem
   */
  private static loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
      
      img.src = src;
    });
  }

  /**
   * Processa imagem
   */
  private static async processImage(
    image: HTMLImageElement,
    config: ImageOptimizationConfig,
    format: string
  ): Promise<OptimizedImage> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    if (!ctx) {
      throw new Error('Canvas context not available');
    }

    // Calcular dimensões
    const { width, height } = this.calculateDimensions(image, config);
    canvas.width = width;
    canvas.height = height;

    // Desenhar imagem
    ctx.drawImage(image, 0, 0, width, height);

    // Gerar formatos
    const formats = await this.generateFormats(canvas, config);
    const placeholder = config.placeholder 
      ? await PlaceholderGenerator.generatePlaceholder(width, height, config.blur)
      : undefined;

    return {
      src: formats[format] || formats.jpeg,
      srcSet: this.generateSrcSet(formats, width),
      sizes: this.generateSizes(width),
      placeholder,
      width,
      height,
      format,
      size: this.getFileSize(formats[format] || formats.jpeg)
    };
  }

  /**
   * Calcula dimensões
   */
  private static calculateDimensions(
    image: HTMLImageElement,
    config: ImageOptimizationConfig
  ): { width: number; height: number } {
    let { width, height } = config;
    
    if (!width && !height) {
      return { width: image.width, height: image.height };
    }

    const aspectRatio = image.width / image.height;

    if (width && height) {
      return { width, height };
    }

    if (width) {
      height = Math.round(width / aspectRatio);
    } else {
      width = Math.round(height * aspectRatio);
    }

    return { width, height };
  }

  /**
   * Gera múltiplos formatos
   */
  private static async generateFormats(
    canvas: HTMLCanvasElement,
    config: ImageOptimizationConfig
  ): Promise<Record<string, string>> {
    const formats: Record<string, string> = {};

    // JPEG
    formats.jpeg = canvas.toDataURL('image/jpeg', config.quality! / 100);

    // WebP
    try {
      formats.webp = canvas.toDataURL('image/webp', config.quality! / 100);
    } catch (error) {
      console.warn('WebP not supported');
    }

    // AVIF
    try {
      formats.avif = canvas.toDataURL('image/avif', config.quality! / 100);
    } catch (error) {
      console.warn('AVIF not supported');
    }

    return formats;
  }

  /**
   * Gera srcSet
   */
  private static generateSrcSet(
    formats: Record<string, string>,
    baseWidth: number
  ): string {
    const breakpoints = [0.5, 1, 1.5, 2];
    const format = Object.keys(formats)[0];
    
    return breakpoints
      .map(scale => {
        const width = Math.round(baseWidth * scale);
        return `${formats[format]} ${width}w`;
      })
      .join(', ');
  }

  /**
   * Gera sizes
   */
  private static generateSizes(baseWidth: number): string {
    return `(max-width: 768px) 100vw, ${baseWidth}px`;
  }

  /**
   * Calcula tamanho do arquivo
   */
  private static getFileSize(dataURL: string): number {
    const base64 = dataURL.split(',')[1];
    const binary = atob(base64);
    return binary.length;
  }

  /**
   * Limpa cache
   */
  static clearCache(): void {
    this.cache.clear();
  }
}

/**
 * Hook para otimização de imagens
 */
export function useImageOptimization(
  src: string,
  config: ImageOptimizationConfig = {}
) {
  const [optimizedImage, setOptimizedImage] = React.useState<OptimizedImage | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    let mounted = true;

    const optimize = async () => {
      try {
        setLoading(true);
        setError(null);

        const optimized = await ImageOptimizer.optimizeImage(src, config);
        
        if (mounted) {
          setOptimizedImage(optimized);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };

    optimize();

    return () => {
      mounted = false;
    };
  }, [src, JSON.stringify(config)]);

  return { optimizedImage, loading, error };
}

/**
 * Componente de imagem otimizada
 */
export function OptimizedImage({
  src,
  alt,
  config = {},
  className,
  ...props
}: {
  src: string;
  alt: string;
  config?: ImageOptimizationConfig;
  className?: string;
} & React.ImgHTMLAttributes<HTMLImageElement>) {
  const { optimizedImage, loading, error } = useImageOptimization(src, config);

  if (error) {
    return <img src={src} alt={alt} className={className} {...props} />;
  }

  if (loading || !optimizedImage) {
    return (
      <div 
        className={`image-placeholder ${className || ''}`}
        style={{
          width: config.width || '100%',
          height: config.height || 'auto',
          backgroundColor: '#f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        Carregando...
      </div>
    );
  }

  return (
    <img
      src={optimizedImage.src}
      srcSet={optimizedImage.srcSet}
      sizes={optimizedImage.sizes}
      alt={alt}
      width={optimizedImage.width}
      height={optimizedImage.height}
      className={className}
      loading={config.lazy ? 'lazy' : 'eager'}
      {...props}
    />
  );
}

/**
 * Componente de imagem com lazy loading
 */
export function LazyImage({
  src,
  alt,
  placeholder,
  threshold = 0.1,
  ...props
}: {
  src: string;
  alt: string;
  placeholder?: string;
  threshold?: number;
} & React.ImgHTMLAttributes<HTMLImageElement>) {
  const [isVisible, setIsVisible] = React.useState(false);
  const [imageLoaded, setImageLoaded] = React.useState(false);
  const imgRef = React.useRef<HTMLImageElement>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return (
    <div ref={imgRef} className="lazy-image-container">
      {!imageLoaded && placeholder && (
        <img
          src={placeholder}
          alt=""
          className="image-placeholder"
          style={{ filter: 'blur(10px)' }}
        />
      )}
      
      {isVisible && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setImageLoaded(true)}
          className={`lazy-image ${imageLoaded ? 'loaded' : ''}`}
          {...props}
        />
      )}
    </div>
  );
}

/**
 * Utilitários para otimização
 */
export const ImageOptimizationUtils = {
  /**
   * Pré-carrega imagens
   */
  preloadImages: (urls: string[]) => {
    urls.forEach(url => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = url;
      document.head.appendChild(link);
    });
  },

  /**
   * Gera placeholder
   */
  generatePlaceholder: PlaceholderGenerator.generatePlaceholder,

  /**
   * Verifica suporte a formatos
   */
  checkFormatSupport: ImageFormatSupport.getBestFormat,

  /**
   * Limpa cache
   */
  clearCache: ImageOptimizer.clearCache
};

export default ImageOptimizer; 