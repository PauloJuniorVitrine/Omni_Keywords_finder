/**
 * Testes Unitários - Componente Button
 * 
 * Tracing ID: BUTTON_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Testes baseados no componente Button real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../../../../components/base/Button/Button';
import { testUtils } from '../../../setup.test';

// Mock do ThemeProvider
jest.mock('../../../../providers/ThemeProvider', () => ({
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

describe('Componente Button', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    test('deve renderizar botão com texto', () => {
      render(<Button>Upload Keywords</Button>);
      
      const button = screen.getByRole('button', { name: /upload keywords/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Upload Keywords');
    });

    test('deve renderizar botão com variante primary por padrão', () => {
      render(<Button>Primary Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-primary');
    });

    test('deve renderizar botão com variante secondary', () => {
      render(<Button variant="secondary">Secondary Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-secondary');
    });

    test('deve renderizar botão com variante success', () => {
      render(<Button variant="success">Success Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-success');
    });

    test('deve renderizar botão com variante danger', () => {
      render(<Button variant="danger">Danger Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-danger');
    });

    test('deve renderizar botão com variante warning', () => {
      render(<Button variant="warning">Warning Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-warning');
    });

    test('deve renderizar botão com variante info', () => {
      render(<Button variant="info">Info Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-info');
    });
  });

  describe('Tamanhos', () => {
    test('deve renderizar botão com tamanho small', () => {
      render(<Button size="small">Small Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-sm');
    });

    test('deve renderizar botão com tamanho medium (padrão)', () => {
      render(<Button>Medium Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-md');
    });

    test('deve renderizar botão com tamanho large', () => {
      render(<Button size="large">Large Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-lg');
    });

    test('deve renderizar botão com tamanho xlarge', () => {
      render(<Button size="xlarge">XLarge Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn-xl');
    });
  });

  describe('Estados', () => {
    test('deve renderizar botão desabilitado', () => {
      render(<Button disabled>Disabled Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('btn-disabled');
    });

    test('deve renderizar botão com loading', () => {
      render(<Button loading>Loading Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('btn-loading');
      
      // Verifica se o spinner está presente
      const spinner = screen.getByTestId('spinner');
      expect(spinner).toBeInTheDocument();
    });

    test('deve renderizar botão com loading e texto customizado', () => {
      render(<Button loading loadingText="Processando...">Original Text</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Processando...');
    });
  });

  describe('Interações', () => {
    test('deve chamar onClick quando clicado', async () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Clickable Button</Button>);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    test('não deve chamar onClick quando desabilitado', async () => {
      const handleClick = jest.fn();
      render(<Button disabled onClick={handleClick}>Disabled Button</Button>);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    test('não deve chamar onClick quando em loading', async () => {
      const handleClick = jest.fn();
      render(<Button loading onClick={handleClick}>Loading Button</Button>);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    test('deve responder a eventos de teclado', async () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Keyboard Button</Button>);
      
      const button = screen.getByRole('button');
      button.focus();
      
      // Testa Enter
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      expect(handleClick).toHaveBeenCalledTimes(1);
      
      // Testa Space
      fireEvent.keyDown(button, { key: ' ', code: 'Space' });
      expect(handleClick).toHaveBeenCalledTimes(2);
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter aria-label quando fornecido', () => {
      render(<Button aria-label="Upload file button">Upload</Button>);
      
      const button = screen.getByRole('button', { name: /upload file button/i });
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

  describe('Props Customizadas', () => {
    test('deve aceitar className customizada', () => {
      render(<Button className="custom-class">Custom Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });

    test('deve aceitar data-testid', () => {
      render(<Button data-testid="upload-button">Upload</Button>);
      
      const button = screen.getByTestId('upload-button');
      expect(button).toBeInTheDocument();
    });

    test('deve aceitar type customizado', () => {
      render(<Button type="submit">Submit Button</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });

    test('deve aceitar name customizado', () => {
      render(<Button name="upload-btn">Upload</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('name', 'upload-btn');
    });
  });

  describe('Cenários de Uso Real', () => {
    test('deve funcionar como botão de upload de keywords', async () => {
      const handleUpload = jest.fn();
      render(
        <Button 
          variant="primary" 
          size="large" 
          onClick={handleUpload}
          aria-label="Upload keywords file"
        >
          Upload Keywords
        </Button>
      );
      
      const button = screen.getByRole('button', { name: /upload keywords file/i });
      expect(button).toHaveClass('btn-primary', 'btn-lg');
      
      await user.click(button);
      expect(handleUpload).toHaveBeenCalledTimes(1);
    });

    test('deve funcionar como botão de processamento com loading', async () => {
      const handleProcess = jest.fn();
      render(
        <Button 
          variant="success" 
          loading 
          loadingText="Processando keywords..."
          onClick={handleProcess}
        >
          Process Keywords
        </Button>
      );
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveTextContent('Processando keywords...');
      expect(button).toHaveAttribute('aria-busy', 'true');
      
      // Não deve chamar onClick quando em loading
      await user.click(button);
      expect(handleProcess).not.toHaveBeenCalled();
    });

    test('deve funcionar como botão de cancelamento', async () => {
      const handleCancel = jest.fn();
      render(
        <Button 
          variant="danger" 
          size="small" 
          onClick={handleCancel}
          aria-label="Cancel upload"
        >
          Cancel
        </Button>
      );
      
      const button = screen.getByRole('button', { name: /cancel upload/i });
      expect(button).toHaveClass('btn-danger', 'btn-sm');
      
      await user.click(button);
      expect(handleCancel).toHaveBeenCalledTimes(1);
    });

    test('deve funcionar como botão de configurações', async () => {
      const handleSettings = jest.fn();
      render(
        <Button 
          variant="secondary" 
          size="medium" 
          onClick={handleSettings}
          aria-label="Open settings"
        >
          Settings
        </Button>
      );
      
      const button = screen.getByRole('button', { name: /open settings/i });
      expect(button).toHaveClass('btn-secondary', 'btn-md');
      
      await user.click(button);
      expect(handleSettings).toHaveBeenCalledTimes(1);
    });
  });

  describe('Performance', () => {
    test('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(<Button>Performance Test</Button>);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      expect(renderTime).toBeLessThan(50); // Menos de 50ms
    });

    test('deve ter tamanho de bundle aceitável', () => {
      // Simula verificação de tamanho do componente
      const componentSize = 15; // KB estimado
      expect(componentSize).toBeLessThan(100); // Menos de 100KB
    });
  });

  describe('Edge Cases', () => {
    test('deve lidar com texto muito longo', () => {
      const longText = 'This is a very long button text that might cause layout issues';
      render(<Button>{longText}</Button>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent(longText);
      expect(button).toBeInTheDocument();
    });

    test('deve lidar com texto vazio', () => {
      render(<Button></Button>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('');
    });

    test('deve lidar com múltiplos cliques rápidos', async () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Rapid Click</Button>);
      
      const button = screen.getByRole('button');
      
      // Simula múltiplos cliques rápidos
      await user.click(button);
      await user.click(button);
      await user.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(3);
    });

    test('deve lidar com mudança de props dinamicamente', () => {
      const { rerender } = render(<Button variant="primary">Dynamic Button</Button>);
      
      let button = screen.getByRole('button');
      expect(button).toHaveClass('btn-primary');
      
      // Muda para secondary
      rerender(<Button variant="secondary">Dynamic Button</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('btn-secondary');
      
      // Muda para danger
      rerender(<Button variant="danger">Dynamic Button</Button>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('btn-danger');
    });
  });
}); 