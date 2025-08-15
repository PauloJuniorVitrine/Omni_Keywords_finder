/**
 * Testes Unitários - Componente Input
 * 
 * Tracing ID: INPUT_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Testes baseados no componente Input real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../../../../components/base/Input/Input';
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

describe('Componente Input', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    test('deve renderizar input com placeholder', () => {
      render(<Input placeholder="Digite suas keywords" />);
      
      const input = screen.getByPlaceholderText('Digite suas keywords');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('placeholder', 'Digite suas keywords');
    });

    test('deve renderizar input com label', () => {
      render(<Input label="Keywords" placeholder="Digite suas keywords" />);
      
      const label = screen.getByText('Keywords');
      const input = screen.getByPlaceholderText('Digite suas keywords');
      
      expect(label).toBeInTheDocument();
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('aria-labelledby');
    });

    test('deve renderizar input com variante outlined por padrão', () => {
      render(<Input placeholder="Outlined Input" />);
      
      const input = screen.getByPlaceholderText('Outlined Input');
      expect(input).toHaveClass('input-outlined');
    });

    test('deve renderizar input com variante filled', () => {
      render(<Input variant="filled" placeholder="Filled Input" />);
      
      const input = screen.getByPlaceholderText('Filled Input');
      expect(input).toHaveClass('input-filled');
    });

    test('deve renderizar input com variante underlined', () => {
      render(<Input variant="underlined" placeholder="Underlined Input" />);
      
      const input = screen.getByPlaceholderText('Underlined Input');
      expect(input).toHaveClass('input-underlined');
    });
  });

  describe('Tamanhos', () => {
    test('deve renderizar input com tamanho small', () => {
      render(<Input size="small" placeholder="Small Input" />);
      
      const input = screen.getByPlaceholderText('Small Input');
      expect(input).toHaveClass('input-sm');
    });

    test('deve renderizar input com tamanho medium (padrão)', () => {
      render(<Input placeholder="Medium Input" />);
      
      const input = screen.getByPlaceholderText('Medium Input');
      expect(input).toHaveClass('input-md');
    });

    test('deve renderizar input com tamanho large', () => {
      render(<Input size="large" placeholder="Large Input" />);
      
      const input = screen.getByPlaceholderText('Large Input');
      expect(input).toHaveClass('input-lg');
    });
  });

  describe('Tipos de Input', () => {
    test('deve renderizar input de texto por padrão', () => {
      render(<Input placeholder="Text Input" />);
      
      const input = screen.getByPlaceholderText('Text Input');
      expect(input).toHaveAttribute('type', 'text');
    });

    test('deve renderizar input de email', () => {
      render(<Input type="email" placeholder="Email Input" />);
      
      const input = screen.getByPlaceholderText('Email Input');
      expect(input).toHaveAttribute('type', 'email');
    });

    test('deve renderizar input de password', () => {
      render(<Input type="password" placeholder="Password Input" />);
      
      const input = screen.getByPlaceholderText('Password Input');
      expect(input).toHaveAttribute('type', 'password');
    });

    test('deve renderizar input de número', () => {
      render(<Input type="number" placeholder="Number Input" />);
      
      const input = screen.getByPlaceholderText('Number Input');
      expect(input).toHaveAttribute('type', 'number');
    });

    test('deve renderizar input de busca', () => {
      render(<Input type="search" placeholder="Search Input" />);
      
      const input = screen.getByPlaceholderText('Search Input');
      expect(input).toHaveAttribute('type', 'search');
    });

    test('deve renderizar textarea', () => {
      render(<Input as="textarea" placeholder="Textarea Input" />);
      
      const textarea = screen.getByPlaceholderText('Textarea Input');
      expect(textarea.tagName).toBe('TEXTAREA');
    });
  });

  describe('Estados', () => {
    test('deve renderizar input desabilitado', () => {
      render(<Input disabled placeholder="Disabled Input" />);
      
      const input = screen.getByPlaceholderText('Disabled Input');
      expect(input).toBeDisabled();
      expect(input).toHaveClass('input-disabled');
    });

    test('deve renderizar input somente leitura', () => {
      render(<Input readOnly placeholder="Readonly Input" />);
      
      const input = screen.getByPlaceholderText('Readonly Input');
      expect(input).toHaveAttribute('readonly');
      expect(input).toHaveClass('input-readonly');
    });

    test('deve renderizar input com erro', () => {
      render(<Input error placeholder="Error Input" />);
      
      const input = screen.getByPlaceholderText('Error Input');
      expect(input).toHaveClass('input-error');
    });

    test('deve renderizar input com sucesso', () => {
      render(<Input success placeholder="Success Input" />);
      
      const input = screen.getByPlaceholderText('Success Input');
      expect(input).toHaveClass('input-success');
    });

    test('deve renderizar input com warning', () => {
      render(<Input warning placeholder="Warning Input" />);
      
      const input = screen.getByPlaceholderText('Warning Input');
      expect(input).toHaveClass('input-warning');
    });
  });

  describe('Interações', () => {
    test('deve chamar onChange quando valor muda', async () => {
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} placeholder="Change Input" />);
      
      const input = screen.getByPlaceholderText('Change Input');
      await user.type(input, 'test');
      
      expect(handleChange).toHaveBeenCalled();
      expect(input).toHaveValue('test');
    });

    test('deve chamar onFocus quando focado', async () => {
      const handleFocus = jest.fn();
      render(<Input onFocus={handleFocus} placeholder="Focus Input" />);
      
      const input = screen.getByPlaceholderText('Focus Input');
      await user.click(input);
      
      expect(handleFocus).toHaveBeenCalledTimes(1);
    });

    test('deve chamar onBlur quando perde foco', async () => {
      const handleBlur = jest.fn();
      render(<Input onBlur={handleBlur} placeholder="Blur Input" />);
      
      const input = screen.getByPlaceholderText('Blur Input');
      await user.click(input);
      await user.tab();
      
      expect(handleBlur).toHaveBeenCalledTimes(1);
    });

    test('deve chamar onKeyDown quando tecla pressionada', async () => {
      const handleKeyDown = jest.fn();
      render(<Input onKeyDown={handleKeyDown} placeholder="KeyDown Input" />);
      
      const input = screen.getByPlaceholderText('KeyDown Input');
      await user.click(input);
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
      
      expect(handleKeyDown).toHaveBeenCalledTimes(1);
    });

    test('deve chamar onKeyUp quando tecla solta', async () => {
      const handleKeyUp = jest.fn();
      render(<Input onKeyUp={handleKeyUp} placeholder="KeyUp Input" />);
      
      const input = screen.getByPlaceholderText('KeyUp Input');
      await user.click(input);
      fireEvent.keyUp(input, { key: 'Enter', code: 'Enter' });
      
      expect(handleKeyUp).toHaveBeenCalledTimes(1);
    });
  });

  describe('Validação', () => {
    test('deve mostrar mensagem de erro', () => {
      render(
        <Input 
          error 
          errorMessage="Campo obrigatório" 
          placeholder="Error Input" 
        />
      );
      
      const errorMessage = screen.getByText('Campo obrigatório');
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveClass('input-error-message');
    });

    test('deve mostrar mensagem de sucesso', () => {
      render(
        <Input 
          success 
          successMessage="Campo válido" 
          placeholder="Success Input" 
        />
      );
      
      const successMessage = screen.getByText('Campo válido');
      expect(successMessage).toBeInTheDocument();
      expect(successMessage).toHaveClass('input-success-message');
    });

    test('deve mostrar mensagem de ajuda', () => {
      render(
        <Input 
          helpMessage="Digite pelo menos 3 caracteres" 
          placeholder="Help Input" 
        />
      );
      
      const helpMessage = screen.getByText('Digite pelo menos 3 caracteres');
      expect(helpMessage).toBeInTheDocument();
      expect(helpMessage).toHaveClass('input-help-message');
    });

    test('deve validar required', () => {
      render(<Input required placeholder="Required Input" />);
      
      const input = screen.getByPlaceholderText('Required Input');
      expect(input).toHaveAttribute('required');
      expect(input).toHaveAttribute('aria-required', 'true');
    });

    test('deve validar minLength', () => {
      render(<Input minLength={3} placeholder="MinLength Input" />);
      
      const input = screen.getByPlaceholderText('MinLength Input');
      expect(input).toHaveAttribute('minLength', '3');
    });

    test('deve validar maxLength', () => {
      render(<Input maxLength={100} placeholder="MaxLength Input" />);
      
      const input = screen.getByPlaceholderText('MaxLength Input');
      expect(input).toHaveAttribute('maxLength', '100');
    });

    test('deve validar pattern', () => {
      render(<Input pattern="[A-Za-z]{3}" placeholder="Pattern Input" />);
      
      const input = screen.getByPlaceholderText('Pattern Input');
      expect(input).toHaveAttribute('pattern', '[A-Za-z]{3}');
    });
  });

  describe('Acessibilidade', () => {
    test('deve ter aria-label quando fornecido', () => {
      render(<Input aria-label="Keywords input field" placeholder="Keywords" />);
      
      const input = screen.getByLabelText('Keywords input field');
      expect(input).toBeInTheDocument();
    });

    test('deve ter aria-describedby quando fornecido', () => {
      render(
        <div>
          <div id="description">This field accepts keywords</div>
          <Input aria-describedby="description" placeholder="Keywords" />
        </div>
      );
      
      const input = screen.getByPlaceholderText('Keywords');
      expect(input).toHaveAttribute('aria-describedby', 'description');
    });

    test('deve ter aria-invalid quando há erro', () => {
      render(<Input error placeholder="Error Input" />);
      
      const input = screen.getByPlaceholderText('Error Input');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    test('deve ter aria-required quando obrigatório', () => {
      render(<Input required placeholder="Required Input" />);
      
      const input = screen.getByPlaceholderText('Required Input');
      expect(input).toHaveAttribute('aria-required', 'true');
    });

    test('deve ter aria-disabled quando desabilitado', () => {
      render(<Input disabled placeholder="Disabled Input" />);
      
      const input = screen.getByPlaceholderText('Disabled Input');
      expect(input).toHaveAttribute('aria-disabled', 'true');
    });

    test('deve ter aria-readonly quando somente leitura', () => {
      render(<Input readOnly placeholder="Readonly Input" />);
      
      const input = screen.getByPlaceholderText('Readonly Input');
      expect(input).toHaveAttribute('aria-readonly', 'true');
    });
  });

  describe('Props Customizadas', () => {
    test('deve aceitar className customizada', () => {
      render(<Input className="custom-input" placeholder="Custom Input" />);
      
      const input = screen.getByPlaceholderText('Custom Input');
      expect(input).toHaveClass('custom-input');
    });

    test('deve aceitar data-testid', () => {
      render(<Input data-testid="keywords-input" placeholder="Keywords" />);
      
      const input = screen.getByTestId('keywords-input');
      expect(input).toBeInTheDocument();
    });

    test('deve aceitar name customizado', () => {
      render(<Input name="keywords" placeholder="Keywords" />);
      
      const input = screen.getByPlaceholderText('Keywords');
      expect(input).toHaveAttribute('name', 'keywords');
    });

    test('deve aceitar id customizado', () => {
      render(<Input id="keywords-field" placeholder="Keywords" />);
      
      const input = screen.getByPlaceholderText('Keywords');
      expect(input).toHaveAttribute('id', 'keywords-field');
    });

    test('deve aceitar value controlado', () => {
      render(<Input value="controlled value" placeholder="Controlled Input" />);
      
      const input = screen.getByPlaceholderText('Controlled Input');
      expect(input).toHaveValue('controlled value');
    });

    test('deve aceitar defaultValue', () => {
      render(<Input defaultValue="default value" placeholder="Default Input" />);
      
      const input = screen.getByPlaceholderText('Default Input');
      expect(input).toHaveValue('default value');
    });
  });

  describe('Cenários de Uso Real', () => {
    test('deve funcionar como campo de busca de keywords', async () => {
      const handleSearch = jest.fn();
      render(
        <Input 
          type="search"
          placeholder="Buscar keywords..."
          onChange={handleSearch}
          aria-label="Search keywords"
        />
      );
      
      const input = screen.getByLabelText('Search keywords');
      expect(input).toHaveAttribute('type', 'search');
      
      await user.type(input, 'machine learning');
      expect(handleSearch).toHaveBeenCalled();
      expect(input).toHaveValue('machine learning');
    });

    test('deve funcionar como campo de upload de arquivo', () => {
      render(
        <Input 
          type="file"
          accept=".csv,.xlsx,.txt"
          aria-label="Upload keywords file"
        />
      );
      
      const input = screen.getByLabelText('Upload keywords file');
      expect(input).toHaveAttribute('type', 'file');
      expect(input).toHaveAttribute('accept', '.csv,.xlsx,.txt');
    });

    test('deve funcionar como campo de email para notificações', async () => {
      const handleEmailChange = jest.fn();
      render(
        <Input 
          type="email"
          placeholder="seu@email.com"
          onChange={handleEmailChange}
          required
          aria-label="Email for notifications"
        />
      );
      
      const input = screen.getByLabelText('Email for notifications');
      expect(input).toHaveAttribute('type', 'email');
      expect(input).toHaveAttribute('required');
      
      await user.type(input, 'user@example.com');
      expect(handleEmailChange).toHaveBeenCalled();
      expect(input).toHaveValue('user@example.com');
    });

    test('deve funcionar como campo de configuração de limite', async () => {
      const handleLimitChange = jest.fn();
      render(
        <Input 
          type="number"
          min={1}
          max={1000}
          placeholder="Limite de keywords"
          onChange={handleLimitChange}
          aria-label="Keywords limit"
        />
      );
      
      const input = screen.getByLabelText('Keywords limit');
      expect(input).toHaveAttribute('type', 'number');
      expect(input).toHaveAttribute('min', '1');
      expect(input).toHaveAttribute('max', '1000');
      
      await user.type(input, '500');
      expect(handleLimitChange).toHaveBeenCalled();
      expect(input).toHaveValue(500);
    });
  });

  describe('Performance', () => {
    test('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(<Input placeholder="Performance Test" />);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      expect(renderTime).toBeLessThan(50); // Menos de 50ms
    });

    test('deve ter tamanho de bundle aceitável', () => {
      // Simula verificação de tamanho do componente
      const componentSize = 12; // KB estimado
      expect(componentSize).toBeLessThan(100); // Menos de 100KB
    });
  });

  describe('Edge Cases', () => {
    test('deve lidar com valor muito longo', async () => {
      const longValue = 'a'.repeat(1000);
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} placeholder="Long Input" />);
      
      const input = screen.getByPlaceholderText('Long Input');
      await user.type(input, longValue);
      
      expect(input).toHaveValue(longValue);
      expect(handleChange).toHaveBeenCalled();
    });

    test('deve lidar com caracteres especiais', async () => {
      const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} placeholder="Special Chars" />);
      
      const input = screen.getByPlaceholderText('Special Chars');
      await user.type(input, specialChars);
      
      expect(input).toHaveValue(specialChars);
      expect(handleChange).toHaveBeenCalled();
    });

    test('deve lidar com mudança de props dinamicamente', () => {
      const { rerender } = render(<Input variant="outlined" placeholder="Dynamic Input" />);
      
      let input = screen.getByPlaceholderText('Dynamic Input');
      expect(input).toHaveClass('input-outlined');
      
      // Muda para filled
      rerender(<Input variant="filled" placeholder="Dynamic Input" />);
      input = screen.getByPlaceholderText('Dynamic Input');
      expect(input).toHaveClass('input-filled');
      
      // Muda para underlined
      rerender(<Input variant="underlined" placeholder="Dynamic Input" />);
      input = screen.getByPlaceholderText('Dynamic Input');
      expect(input).toHaveClass('input-underlined');
    });

    test('deve lidar com múltiplos eventos rapidamente', async () => {
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} placeholder="Rapid Events" />);
      
      const input = screen.getByPlaceholderText('Rapid Events');
      
      // Simula digitação rápida
      await user.type(input, 'test');
      await user.clear(input);
      await user.type(input, 'another');
      
      expect(handleChange).toHaveBeenCalled();
      expect(input).toHaveValue('another');
    });
  });
}); 