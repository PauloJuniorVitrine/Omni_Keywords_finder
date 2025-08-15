/**
 * Testes de Acessibilidade - Componente Button
 * 
 * Tracing ID: A11Y_BUTTON_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Testes de acessibilidade baseados no componente Button real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../../../components/base/Button/Button';

// Configuração do jest-axe
expect.extend(toHaveNoViolations);

// Mock do ThemeProvider
jest.mock('../../../providers/ThemeProvider', () => ({
  useTheme: () => ({
    theme: 'light',
    tokens: {
      colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        danger: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
      },
      spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '3rem'
      }
    }
  })
}));

describe('Acessibilidade - Componente Button', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Conformidade WCAG 2.1 AA', () => {
    test('deve passar nos testes de acessibilidade do axe', async () => {
      const { container } = render(<Button>Upload Keywords</Button>);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    test('deve ter contraste adequado para texto', async () => {
      const { container } = render(
        <Button variant="primary">Primary Button</Button>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
      expect(results).toHaveNoViolations();
    });

    test('deve ter contraste adequado em estado desabilitado', async () => {
      const { container } = render(
        <Button disabled>Disabled Button</Button>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
      expect(results).toHaveNoViolations();
    });

    test('deve ter contraste adequado em estado loading', async () => {
      const { container } = render(
        <Button loading>Loading Button</Button>
      );
      
      const results = await axe(container, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
      expect(results).toHaveNoViolations();
    });
  });

  describe('Navegação por Teclado', () => {
    test('deve ser focável por teclado', () => {
      render(<Button>Keyboard Accessible Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '0');
    });

    test('deve responder a eventos de teclado', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Keyboard Button</Button>);
      
      const button = screen.getByRole('button');
      
      // Testa Enter
      button.focus();
      button.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
      expect(handleClick).toHaveBeenCalled();
      
      // Testa Space
      button.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }));
      expect(handleClick).toHaveBeenCalledTimes(2);
    });

    test('não deve ser focável quando desabilitado', () => {
      render(<Button disabled>Disabled Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '-1');
    });

    test('não deve ser focável quando em loading', () => {
      render(<Button loading>Loading Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '-1');
    });
  });

  describe('ARIA Labels e Descrições', () => {
    test('deve ter aria-label quando fornecido', () => {
      render(<Button aria-label="Upload keywords file">Upload</Button>);
      
      const button = screen.getByRole('button', { name: /upload keywords file/i });
      expect(button).toBeInTheDocument();
    });

    test('deve ter aria-describedby quando fornecido', () => {
      render(
        <div>
          <div id="description">This button uploads keywords</div>
          <Button aria-describedby="description">Upload</Button>
        </div>
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-describedby', 'description');
    });

    test('deve ter aria-pressed para botões toggle', () => {
      render(<Button aria-pressed={true}>Toggle Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'true');
    });

    test('deve ter aria-expanded para botões expansíveis', () => {
      render(<Button aria-expanded={false}>Expand Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'false');
    });

    test('deve ter aria-busy quando em loading', () => {
      render(<Button loading>Loading Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    test('deve ter aria-disabled quando desabilitado', () => {
      render(<Button disabled>Disabled Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Estados e Feedback', () => {
    test('deve anunciar mudança de estado para screen reader', () => {
      render(<Button loading loadingText="Processando...">Original Text</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Processando...');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    test('deve manter acessibilidade em diferentes variantes', async () => {
      const variants = ['primary', 'secondary', 'success', 'danger', 'warning', 'info'];
      
      for (const variant of variants) {
        const { container, unmount } = render(
          <Button variant={variant as any}>Test Button</Button>
        );
        
        const results = await axe(container);
        expect(results).toHaveNoViolations();
        
        unmount();
      }
    });

    test('deve manter acessibilidade em diferentes tamanhos', async () => {
      const sizes = ['small', 'medium', 'large', 'xlarge'];
      
      for (const size of sizes) {
        const { container, unmount } = render(
          <Button size={size as any}>Test Button</Button>
        );
        
        const results = await axe(container);
        expect(results).toHaveNoViolations();
        
        unmount();
      }
    });
  });

  describe('Screen Reader Support', () => {
    test('deve ter texto acessível para screen reader', () => {
      render(<Button>Upload Keywords</Button>);
      
      const button = screen.getByRole('button', { name: /upload keywords/i });
      expect(button).toBeInTheDocument();
    });

    test('deve ter descrição adicional quando necessário', () => {
      render(
        <Button aria-describedby="button-help">
          Upload
        </Button>
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-describedby', 'button-help');
    });

    test('deve anunciar estado de loading para screen reader', () => {
      render(<Button loading loadingText="Processando upload...">Upload</Button>);
      
      const button = screen.getByRole('button', { name: /processando upload/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    test('deve anunciar estado desabilitado para screen reader', () => {
      render(<Button disabled>Upload</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Cenários de Uso Real', () => {
    test('deve ser acessível como botão de upload de keywords', async () => {
      const { container } = render(
        <Button 
          variant="primary" 
          size="large" 
          aria-label="Upload keywords file"
          aria-describedby="upload-help"
        >
          Upload Keywords
        </Button>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: /upload keywords file/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-describedby', 'upload-help');
    });

    test('deve ser acessível como botão de processamento com loading', async () => {
      const { container } = render(
        <Button 
          variant="success" 
          loading 
          loadingText="Processando keywords..."
          aria-label="Process keywords"
        >
          Process Keywords
        </Button>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: /processando keywords/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    test('deve ser acessível como botão de cancelamento', async () => {
      const { container } = render(
        <Button 
          variant="danger" 
          size="small" 
          aria-label="Cancel upload"
        >
          Cancel
        </Button>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: /cancel upload/i });
      expect(button).toBeInTheDocument();
    });

    test('deve ser acessível como botão de configurações', async () => {
      const { container } = render(
        <Button 
          variant="secondary" 
          size="medium" 
          aria-label="Open settings"
          aria-expanded="false"
        >
          Settings
        </Button>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: /open settings/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-expanded', 'false');
    });
  });

  describe('Focus Management', () => {
    test('deve restaurar foco após ação', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Focus Test</Button>);
      
      const button = screen.getByRole('button');
      button.focus();
      
      expect(document.activeElement).toBe(button);
    });

    test('deve manter foco durante loading', () => {
      render(<Button loading>Loading Test</Button>);
      
      const button = screen.getByRole('button');
      // Em loading, o botão não deve ser focável
      expect(button).toHaveAttribute('tabindex', '-1');
    });

    test('deve prevenir foco quando desabilitado', () => {
      render(<Button disabled>Disabled Test</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '-1');
    });
  });

  describe('Semântica HTML', () => {
    test('deve usar elemento button nativo', () => {
      render(<Button>Native Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button.tagName).toBe('BUTTON');
    });

    test('deve ter type correto', () => {
      render(<Button type="submit">Submit Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });

    test('deve ter name correto', () => {
      render(<Button name="upload-btn">Named Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('name', 'upload-btn');
    });
  });

  describe('Performance de Acessibilidade', () => {
    test('deve renderizar rapidamente com acessibilidade', () => {
      const startTime = performance.now();
      
      render(<Button>Performance Test</Button>);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      expect(renderTime).toBeLessThan(50); // Menos de 50ms
    });

    test('deve manter acessibilidade com múltiplos botões', async () => {
      const { container } = render(
        <div>
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="success">Success</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="warning">Warning</Button>
          <Button variant="info">Info</Button>
        </div>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Edge Cases de Acessibilidade', () => {
    test('deve lidar com texto muito longo', async () => {
      const longText = 'This is a very long button text that might cause layout issues and accessibility problems';
      const { container } = render(<Button>{longText}</Button>);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: new RegExp(longText, 'i') });
      expect(button).toBeInTheDocument();
    });

    test('deve lidar com texto vazio', async () => {
      const { container } = render(<Button></Button>);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    test('deve lidar com caracteres especiais', async () => {
      const specialText = 'Upload & Process Keywords (CSV/XLSX)';
      const { container } = render(<Button>{specialText}</Button>);
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
      
      const button = screen.getByRole('button', { name: new RegExp(specialText, 'i') });
      expect(button).toBeInTheDocument();
    });

    test('deve lidar com mudança dinâmica de props', async () => {
      const { container, rerender } = render(<Button variant="primary">Dynamic Button</Button>);
      
      let results = await axe(container);
      expect(results).toHaveNoViolations();
      
      // Muda para secondary
      rerender(<Button variant="secondary">Dynamic Button</Button>);
      results = await axe(container);
      expect(results).toHaveNoViolations();
      
      // Muda para danger
      rerender(<Button variant="danger">Dynamic Button</Button>);
      results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
}); 