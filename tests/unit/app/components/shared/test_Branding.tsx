/**
 * test_Branding.tsx
 * 
 * Testes unitários para o componente de branding
 * Cobertura completa de todas as funcionalidades
 * 
 * Tracing ID: UI-007-TEST
 * Data/Hora: 2024-12-20 08:30:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Branding, { SimpleLogo, Favicon, brandingConfig } from '../../../../app/components/shared/Branding';

// Mock do window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock do Image
global.Image = class {
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  src: string = '';

  constructor() {
    setTimeout(() => {
      if (this.src.includes('error')) {
        this.onerror?.();
      } else {
        this.onload?.();
      }
    }, 0);
  }
} as any;

describe('Componente de Branding - UI-007', () => {
  describe('Configuração de Branding', () => {
    it('deve ter configuração completa', () => {
      expect(brandingConfig).toHaveProperty('name');
      expect(brandingConfig).toHaveProperty('tagline');
      expect(brandingConfig).toHaveProperty('shortName');
      expect(brandingConfig).toHaveProperty('logo');
      expect(brandingConfig).toHaveProperty('colors');
    });

    it('deve ter nome da aplicação correto', () => {
      expect(brandingConfig.name).toBe('Omni Keywords Finder');
    });

    it('deve ter tagline definida', () => {
      expect(brandingConfig.tagline).toBe('Descubra oportunidades de SEO com inteligência artificial');
    });

    it('deve ter nome curto definido', () => {
      expect(brandingConfig.shortName).toBe('OKF');
    });

    it('deve ter configuração de logo', () => {
      expect(brandingConfig.logo).toHaveProperty('primary');
      expect(brandingConfig.logo).toHaveProperty('fallback');
      expect(brandingConfig.logo).toHaveProperty('icon');
    });

    it('deve ter configuração de cores', () => {
      expect(brandingConfig.colors).toHaveProperty('primary');
      expect(brandingConfig.colors).toHaveProperty('secondary');
      expect(brandingConfig.colors).toHaveProperty('accent');
    });
  });

  describe('Componente Branding - Renderização', () => {
    it('deve renderizar com configurações padrão', () => {
      render(<Branding />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
      expect(screen.getByText('Descubra oportunidades de SEO com inteligência artificial')).toBeInTheDocument();
    });

    it('deve renderizar com tamanho pequeno', () => {
      render(<Branding size="sm" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });

    it('deve renderizar com tamanho grande', () => {
      render(<Branding size="lg" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });

    it('deve renderizar com tamanho extra grande', () => {
      render(<Branding size="xl" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });
  });

  describe('Variantes do Componente', () => {
    it('deve renderizar variante padrão', () => {
      render(<Branding variant="default" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
      expect(screen.getByText('Descubra oportunidades de SEO com inteligência artificial')).toBeInTheDocument();
    });

    it('deve renderizar variante compacta', () => {
      render(<Branding variant="compact" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
      expect(screen.queryByText('Descubra oportunidades de SEO com inteligência artificial')).not.toBeInTheDocument();
    });

    it('deve renderizar variante completa', () => {
      render(<Branding variant="full" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
      expect(screen.getByText('Descubra oportunidades de SEO com inteligência artificial')).toBeInTheDocument();
    });

    it('deve renderizar apenas ícone', () => {
      render(<Branding variant="icon-only" />);
      expect(screen.queryByText('Omni Keywords Finder')).not.toBeInTheDocument();
      expect(screen.queryByText('Descubra oportunidades de SEO com inteligência artificial')).not.toBeInTheDocument();
    });
  });

  describe('Configuração de Tagline', () => {
    it('deve mostrar tagline por padrão', () => {
      render(<Branding />);
      expect(screen.getByText('Descubra oportunidades de SEO com inteligência artificial')).toBeInTheDocument();
    });

    it('deve ocultar tagline quando showTagline é false', () => {
      render(<Branding showTagline={false} />);
      expect(screen.queryByText('Descubra oportunidades de SEO com inteligência artificial')).not.toBeInTheDocument();
    });

    it('deve mostrar tagline customizada', () => {
      const customTagline = 'Tagline personalizada';
      render(<Branding customTagline={customTagline} />);
      expect(screen.getByText(customTagline)).toBeInTheDocument();
    });
  });

  describe('Navegação e Interação', () => {
    it('deve renderizar como link quando href é fornecido', () => {
      render(<Branding href="/home" />);
      const link = screen.getByRole('link');
      expect(link).toHaveAttribute('href', '/home');
    });

    it('deve renderizar como botão quando onClick é fornecido', () => {
      const handleClick = jest.fn();
      render(<Branding onClick={handleClick} />);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('deve executar onClick quando clicado', () => {
      const handleClick = jest.fn();
      render(<Branding onClick={handleClick} />);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('deve executar onClick quando link é clicado', () => {
      const handleClick = jest.fn();
      render(<Branding href="/home" onClick={handleClick} />);
      const link = screen.getByRole('link');
      fireEvent.click(link);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Estados de Loading', () => {
    it('deve mostrar estado de loading', () => {
      render(<Branding loading={true} />);
      const loadingElement = screen.getByText('Omni Keywords Finder').closest('.branding-loading');
      expect(loadingElement).toBeInTheDocument();
    });

    it('deve ter opacidade reduzida no estado de loading', () => {
      render(<Branding loading={true} />);
      const loadingElement = screen.getByText('Omni Keywords Finder').closest('.branding-loading');
      expect(loadingElement).toHaveStyle({ opacity: '0.6' });
    });
  });

  describe('Fallback e Tratamento de Erro', () => {
    it('deve mostrar fallback quando logo não carrega', async () => {
      render(<Branding />);
      await waitFor(() => {
        expect(screen.getByText('OKF')).toBeInTheDocument();
      });
    });

    it('deve mostrar texto customizado de fallback', async () => {
      render(<Branding fallbackText="Custom Fallback" />);
      await waitFor(() => {
        expect(screen.getByText('Custom Fallback')).toBeInTheDocument();
      });
    });
  });

  describe('Temas', () => {
    it('deve renderizar com tema claro por padrão', () => {
      render(<Branding theme="light" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });

    it('deve renderizar com tema escuro', () => {
      render(<Branding theme="dark" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });

    it('deve renderizar com tema automático', () => {
      render(<Branding theme="auto" />);
      const branding = screen.getByText('Omni Keywords Finder');
      expect(branding).toBeInTheDocument();
    });
  });

  describe('Classes CSS e Estilos', () => {
    it('deve aplicar classes CSS customizadas', () => {
      render(<Branding className="custom-class" />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toHaveClass('custom-class');
    });

    it('deve aplicar estilos inline customizados', () => {
      const customStyle = { backgroundColor: 'red' };
      render(<Branding style={customStyle} />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toHaveStyle({ backgroundColor: 'red' });
    });
  });

  describe('Componente SimpleLogo', () => {
    it('deve renderizar SimpleLogo com tamanho padrão', () => {
      render(<SimpleLogo />);
      const logo = screen.getByAltText('Omni Keywords Finder Icon');
      expect(logo).toBeInTheDocument();
    });

    it('deve renderizar SimpleLogo com tamanho customizado', () => {
      render(<SimpleLogo size="48px" />);
      const logo = screen.getByAltText('Omni Keywords Finder Icon');
      expect(logo).toBeInTheDocument();
    });

    it('deve renderizar SimpleLogo com tema claro', () => {
      render(<SimpleLogo theme="light" />);
      const logo = screen.getByAltText('Omni Keywords Finder Icon');
      expect(logo).toBeInTheDocument();
    });

    it('deve renderizar SimpleLogo com tema escuro', () => {
      render(<SimpleLogo theme="dark" />);
      const logo = screen.getByAltText('Omni Keywords Finder Icon');
      expect(logo).toBeInTheDocument();
    });

    it('deve renderizar fallback quando logo não carrega', async () => {
      render(<SimpleLogo />);
      await waitFor(() => {
        expect(screen.getByText('OKF')).toBeInTheDocument();
      });
    });
  });

  describe('Componente Favicon', () => {
    it('deve renderizar componente Favicon', () => {
      render(<Favicon />);
      const favicon = document.querySelector('link[rel="icon"]');
      expect(favicon).toBeInTheDocument();
    });

    it('deve ter atributos corretos no favicon', () => {
      render(<Favicon />);
      const favicon = document.querySelector('link[rel="icon"]');
      expect(favicon).toHaveAttribute('rel', 'icon');
      expect(favicon).toHaveAttribute('type', 'image/svg+xml');
      expect(favicon).toHaveAttribute('href', brandingConfig.logo.icon);
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter texto alternativo no logo', () => {
      render(<Branding />);
      const logo = screen.getByAltText('Omni Keywords Finder Logo');
      expect(logo).toBeInTheDocument();
    });

    it('deve ter texto alternativo no ícone', () => {
      render(<SimpleLogo />);
      const icon = screen.getByAltText('Omni Keywords Finder Icon');
      expect(icon).toBeInTheDocument();
    });

    it('deve ter cursor pointer quando é clicável', () => {
      render(<Branding href="/home" />);
      const link = screen.getByRole('link');
      expect(link).toHaveStyle({ cursor: 'pointer' });
    });

    it('deve ter cursor default quando não é clicável', () => {
      render(<Branding />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toHaveStyle({ cursor: 'default' });
    });
  });

  describe('Responsividade', () => {
    it('deve ter transições suaves', () => {
      render(<Branding />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toHaveStyle({ transition: 'all 0.2s ease-in-out' });
    });

    it('deve ter gap adequado entre elementos', () => {
      render(<Branding size="md" />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toHaveStyle({ gap: '12px' });
    });
  });

  describe('Integridade do Sistema', () => {
    it('deve manter consistência entre variantes', () => {
      const { rerender } = render(<Branding variant="default" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();

      rerender(<Branding variant="compact" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();

      rerender(<Branding variant="full" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
    });

    it('deve manter consistência entre tamanhos', () => {
      const { rerender } = render(<Branding size="sm" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();

      rerender(<Branding size="md" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();

      rerender(<Branding size="lg" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();

      rerender(<Branding size="xl" />);
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
    });

    it('deve integrar com sistema de cores', () => {
      render(<Branding />);
      const branding = screen.getByText('Omni Keywords Finder').closest('.branding');
      expect(branding).toBeInTheDocument();
    });

    it('deve integrar com sistema de tipografia', () => {
      render(<Branding />);
      const text = screen.getByText('Omni Keywords Finder');
      expect(text).toBeInTheDocument();
    });
  });

  describe('Exportações', () => {
    it('deve exportar componente principal', () => {
      expect(Branding).toBeDefined();
    });

    it('deve exportar SimpleLogo', () => {
      expect(SimpleLogo).toBeDefined();
    });

    it('deve exportar Favicon', () => {
      expect(Favicon).toBeDefined();
    });

    it('deve exportar configuração de branding', () => {
      expect(brandingConfig).toBeDefined();
    });

    it('deve ter exportação padrão', () => {
      expect(Branding).toBeDefined();
    });
  });
}); 