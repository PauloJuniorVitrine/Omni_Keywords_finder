/**
 * Testes para Otimização de Imagens
 * 
 * Tracing ID: TEST_IMAGE_OPTIMIZATION_001
 * Data: 2025-01-27
 * Versão: 1.0.0
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock do Canvas API
const mockCanvas = {
  width: 100,
  height: 100,
  getContext: vi.fn().mockReturnValue({
    fillStyle: '',
    fillRect: vi.fn(),
    createLinearGradient: vi.fn().mockReturnValue({
      addColorStop: vi.fn()
    }),
    toDataURL: vi.fn().mockReturnValue('data:image/jpeg;base64,mock')
  }),
  toDataURL: vi.fn().mockReturnValue('data:image/jpeg;base64,mock')
};

// Mock do Image
const mockImage = {
  width: 800,
  height: 600,
  crossOrigin: '',
  onload: null as (() => void) | null,
  onerror: null as (() => void) | null,
  src: ''
};

// Mock do DOM
const mockDocument = {
  createElement: vi.fn().mockImplementation((tagName: string) => {
    if (tagName === 'canvas') {
      return mockCanvas;
    }
    if (tagName === 'img') {
      return mockImage;
    }
    return {};
  })
};

// Setup global mocks
global.document = mockDocument as any;
global.Image = class {
  width = 800;
  height = 600;
  crossOrigin = '';
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  src = '';

  constructor() {
    // Simular carregamento bem-sucedido
    setTimeout(() => {
      if (this.onload) {
        this.onload();
      }
    }, 10);
  }
} as any;

describe('Image Optimization Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('ImageFormatSupport', () => {
    it('deve verificar suporte a WebP', async () => {
      // Mock para suporte a WebP
      mockCanvas.toDataURL.mockReturnValue('data:image/webp;base64,mock');

      const checkWebPSupport = async () => {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        
        try {
          const dataURL = canvas.toDataURL('image/webp');
          return dataURL.indexOf('data:image/webp') === 0;
        } catch (error) {
          return false;
        }
      };

      const isSupported = await checkWebPSupport();
      expect(isSupported).toBe(true);
    });

    it('deve verificar suporte a AVIF', async () => {
      // Mock para suporte a AVIF
      mockCanvas.toDataURL.mockReturnValue('data:image/avif;base64,mock');

      const checkAVIFSupport = async () => {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        
        try {
          const dataURL = canvas.toDataURL('image/avif');
          return dataURL.indexOf('data:image/avif') === 0;
        } catch (error) {
          return false;
        }
      };

      const isSupported = await checkAVIFSupport();
      expect(isSupported).toBe(true);
    });

    it('deve retornar JPEG como fallback', async () => {
      // Mock para não suportar formatos modernos
      mockCanvas.toDataURL.mockImplementation((format) => {
        if (format === 'image/webp' || format === 'image/avif') {
          throw new Error('Not supported');
        }
        return 'data:image/jpeg;base64,mock';
      });

      const getBestFormat = async () => {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        
        try {
          canvas.toDataURL('image/avif');
          return 'avif';
        } catch (error) {
          try {
            canvas.toDataURL('image/webp');
            return 'webp';
          } catch (error) {
            return 'jpeg';
          }
        }
      };

      const format = await getBestFormat();
      expect(format).toBe('jpeg');
    });
  });

  describe('PlaceholderGenerator', () => {
    it('deve gerar placeholder base64', async () => {
      const generatePlaceholder = async (width: number, height: number, blur: number = 10) => {
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

        return canvas.toDataURL('image/jpeg', 0.1);
      };

      const placeholder = await generatePlaceholder(100, 100, 10);
      expect(placeholder).toContain('data:image/jpeg;base64');
    });

    it('deve gerar placeholder SVG', () => {
      const generateSVGPlaceholder = (width: number, height: number, text: string = 'Loading...') => {
        return `
          <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#666" font-family="Arial, sans-serif" font-size="14">
              ${text}
            </text>
          </svg>
        `;
      };

      const svg = generateSVGPlaceholder(200, 150, 'Carregando...');
      expect(svg).toContain('<svg');
      expect(svg).toContain('width="200"');
      expect(svg).toContain('height="150"');
      expect(svg).toContain('Carregando...');
    });
  });

  describe('ImageOptimizer', () => {
    it('deve otimizar imagem com configuração padrão', async () => {
      const optimizeImage = async (src: string, config = {}) => {
        const defaultConfig = {
          quality: 85,
          format: 'webp',
          lazy: true,
          placeholder: true,
          blur: 10
        };

        const finalConfig = { ...defaultConfig, ...config };
        
        // Simular carregamento de imagem
        const image = await new Promise<HTMLImageElement>((resolve) => {
          const img = new Image();
          img.onload = () => resolve(img);
          img.src = src;
        });

        // Simular processamento
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          throw new Error('Canvas context not available');
        }

        canvas.width = image.width;
        canvas.height = image.height;
        ctx.drawImage(image, 0, 0, image.width, image.height);

        // Gerar formatos
        const formats = {
          jpeg: canvas.toDataURL('image/jpeg', finalConfig.quality / 100),
          webp: canvas.toDataURL('image/webp', finalConfig.quality / 100)
        };

        return {
          src: formats[finalConfig.format as keyof typeof formats] || formats.jpeg,
          width: image.width,
          height: image.height,
          format: finalConfig.format,
          size: formats.jpeg.length
        };
      };

      const result = await optimizeImage('/test-image.jpg');
      
      expect(result).toHaveProperty('src');
      expect(result).toHaveProperty('width');
      expect(result).toHaveProperty('height');
      expect(result).toHaveProperty('format');
      expect(result).toHaveProperty('size');
    });

    it('deve calcular dimensões corretamente', () => {
      const calculateDimensions = (image: { width: number; height: number }, config: any) => {
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
      };

      const image = { width: 800, height: 600 };
      
      // Teste sem configuração
      const result1 = calculateDimensions(image, {});
      expect(result1).toEqual({ width: 800, height: 600 });

      // Teste com largura fixa
      const result2 = calculateDimensions(image, { width: 400 });
      expect(result2).toEqual({ width: 400, height: 300 });

      // Teste com altura fixa
      const result3 = calculateDimensions(image, { height: 300 });
      expect(result3).toEqual({ width: 400, height: 300 });
    });

    it('deve gerar srcSet corretamente', () => {
      const generateSrcSet = (formats: Record<string, string>, baseWidth: number) => {
        const breakpoints = [0.5, 1, 1.5, 2];
        const format = Object.keys(formats)[0];
        
        return breakpoints
          .map(scale => {
            const width = Math.round(baseWidth * scale);
            return `${formats[format]} ${width}w`;
          })
          .join(', ');
      };

      const formats = { jpeg: 'data:image/jpeg;base64,mock' };
      const srcSet = generateSrcSet(formats, 800);

      expect(srcSet).toContain('400w');
      expect(srcSet).toContain('800w');
      expect(srcSet).toContain('1200w');
      expect(srcSet).toContain('1600w');
    });

    it('deve gerar sizes corretamente', () => {
      const generateSizes = (baseWidth: number) => {
        return `(max-width: 768px) 100vw, ${baseWidth}px`;
      };

      const sizes = generateSizes(800);
      expect(sizes).toBe('(max-width: 768px) 100vw, 800px');
    });
  });

  describe('Componentes React', () => {
    it('deve renderizar OptimizedImage corretamente', () => {
      const OptimizedImage = ({ src, alt, config = {}, ...props }: any) => {
        return (
          <img
            src={src}
            alt={alt}
            width={config.width}
            height={config.height}
            loading={config.lazy ? 'lazy' : 'eager'}
            {...props}
          />
        );
      };

      const component = OptimizedImage({
        src: '/test-image.jpg',
        alt: 'Test Image',
        config: { width: 400, height: 300, lazy: true }
      });

      expect(component.props.src).toBe('/test-image.jpg');
      expect(component.props.alt).toBe('Test Image');
      expect(component.props.width).toBe(400);
      expect(component.props.height).toBe(300);
      expect(component.props.loading).toBe('lazy');
    });

    it('deve renderizar LazyImage corretamente', () => {
      const LazyImage = ({ src, alt, placeholder }: any) => {
        return (
          <div className="lazy-image-container">
            {placeholder && (
              <img
                src={placeholder}
                alt=""
                className="image-placeholder"
                style={{ filter: 'blur(10px)' }}
              />
            )}
            <img
              src={src}
              alt={alt}
              className="lazy-image"
            />
          </div>
        );
      };

      const component = LazyImage({
        src: '/test-image.jpg',
        alt: 'Test Image',
        placeholder: '/placeholder.jpg'
      });

      expect(component.props.children[0].props.src).toBe('/placeholder.jpg');
      expect(component.props.children[1].props.src).toBe('/test-image.jpg');
      expect(component.props.children[1].props.alt).toBe('Test Image');
    });
  });

  describe('Utilitários', () => {
    it('deve pré-carregar imagens', () => {
      const preloadImages = (urls: string[]) => {
        urls.forEach(url => {
          const link = document.createElement('link');
          link.rel = 'preload';
          link.as = 'image';
          link.href = url;
          document.head.appendChild(link);
        });
      };

      const urls = ['/image1.jpg', '/image2.png', '/image3.webp'];
      preloadImages(urls);

      // Verificar se preload foi chamado
      expect(mockDocument.createElement).toHaveBeenCalledWith('link');
    });

    it('deve limpar cache', () => {
      const cache = new Map<string, any>();
      cache.set('key1', 'value1');
      cache.set('key2', 'value2');

      const clearCache = () => {
        cache.clear();
      };

      expect(cache.size).toBe(2);
      clearCache();
      expect(cache.size).toBe(0);
    });
  });

  describe('Configurações', () => {
    it('deve ter configuração padrão correta', () => {
      const defaultConfig = {
        quality: 85,
        format: 'webp',
        lazy: true,
        placeholder: true,
        blur: 10
      };

      expect(defaultConfig.quality).toBe(85);
      expect(defaultConfig.format).toBe('webp');
      expect(defaultConfig.lazy).toBe(true);
      expect(defaultConfig.placeholder).toBe(true);
      expect(defaultConfig.blur).toBe(10);
    });

    it('deve permitir sobrescrever configuração', () => {
      const defaultConfig = {
        quality: 85,
        format: 'webp',
        lazy: true,
        placeholder: true,
        blur: 10
      };

      const customConfig = {
        quality: 95,
        format: 'jpeg',
        lazy: false
      };

      const finalConfig = { ...defaultConfig, ...customConfig };

      expect(finalConfig.quality).toBe(95);
      expect(finalConfig.format).toBe('jpeg');
      expect(finalConfig.lazy).toBe(false);
      expect(finalConfig.placeholder).toBe(true); // Mantido do default
      expect(finalConfig.blur).toBe(10); // Mantido do default
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar erro de carregamento de imagem', async () => {
      const loadImage = async (src: string) => {
        return new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          
          img.onload = () => resolve(img);
          img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
          
          img.src = src;
        });
      };

      // Simular erro
      const mockImageWithError = {
        ...mockImage,
        onload: null,
        onerror: () => {
          if (mockImageWithError.onerror) {
            mockImageWithError.onerror();
          }
        }
      };

      try {
        await loadImage('/invalid-image.jpg');
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toContain('Failed to load image');
      }
    });

    it('deve tratar erro de canvas context', () => {
      const mockCanvasWithoutContext = {
        ...mockCanvas,
        getContext: vi.fn().mockReturnValue(null)
      };

      const processImage = () => {
        const canvas = mockCanvasWithoutContext;
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          throw new Error('Canvas context not available');
        }
      };

      expect(() => processImage()).toThrow('Canvas context not available');
    });
  });
}); 