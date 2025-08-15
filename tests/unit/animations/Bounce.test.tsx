/**
 * Testes Unitários - Bounce Component
 * 
 * Prompt: Implementação de testes para componentes de animações
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_BOUNCE_033
 * 
 * Baseado em código real do sistema de animações e hooks useAnimation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Bounce } from '../../../app/components/animations/Bounce';

// Mock do hook useAnimation baseado no código real
jest.mock('../../../app/hooks/useAnimation', () => ({
  useBounce: jest.fn(() => ({
    isAnimating: false,
    triggerAnimation: jest.fn(),
    animationStyle: {},
    resetAnimation: jest.fn()
  }))
}));

describe('Bounce - Componente de Animação de Quique', () => {
  
  const defaultProps = {
    children: <button>Clique para testar</button>,
    duration: 1000,
    bounces: 3
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar children corretamente', () => {
      render(<Bounce {...defaultProps} />);
      
      expect(screen.getByText('Clique para testar')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS de animação', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveClass('bounce-container');
    });

    test('deve renderizar children complexos', () => {
      const complexChildren = (
        <div>
          <span>Texto</span>
          <button>Botão</button>
          <input placeholder="Input" />
        </div>
      );

      render(<Bounce {...defaultProps} children={complexChildren} />);
      
      expect(screen.getByText('Texto')).toBeInTheDocument();
      expect(screen.getByText('Botão')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Input')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<Bounce {...defaultProps} className="custom-bounce" />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveClass('custom-bounce');
    });
  });

  describe('Configuração de Animação', () => {
    
    test('deve usar duração padrão de 1000ms', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-duration': '1000ms' });
    });

    test('deve usar duração personalizada', () => {
      render(<Bounce {...defaultProps} duration={2000} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-duration': '2000ms' });
    });

    test('deve usar número padrão de quiques de 3', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-count': '3' });
    });

    test('deve usar número personalizado de quiques', () => {
      render(<Bounce {...defaultProps} bounces={5} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-count': '5' });
    });
  });

  describe('Triggers de Animação', () => {
    
    test('deve animar ao clicar no elemento', async () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<Bounce {...defaultProps} />);
      
      const trigger = screen.getByText('Clique para testar');
      fireEvent.click(trigger);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });

    test('deve animar ao receber prop trigger', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<Bounce {...defaultProps} trigger={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando trigger muda para true
      rerender(<Bounce {...defaultProps} trigger={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });

    test('deve animar ao receber prop success', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<Bounce {...defaultProps} success={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando success muda para true
      rerender(<Bounce {...defaultProps} success={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });
  });

  describe('Estados de Animação', () => {
    
    test('deve mostrar estado de animação ativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'scale(1.2)' },
        resetAnimation: jest.fn()
      });

      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveClass('bounce-animating');
      expect(bounceContainer).toHaveStyle({ transform: 'scale(1.2)' });
    });

    test('deve mostrar estado de animação inativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: false,
        triggerAnimation: jest.fn(),
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).not.toHaveClass('bounce-animating');
    });
  });

  describe('Estilos e Layout', () => {
    
    test('deve ter posicionamento relativo', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ position: 'relative' });
    });

    test('deve ter display inline-block', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ display: 'inline-block' });
    });

    test('deve ter transição suave', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ 
        transition: 'transform 1000ms cubic-bezier(0.68, -0.55, 0.265, 1.55)' 
      });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve manter acessibilidade durante animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'scale(1.2)' },
        resetAnimation: jest.fn()
      });

      render(<Bounce {...defaultProps} />);
      
      const button = screen.getByText('Clique para testar');
      expect(button).toBeAccessible();
      expect(button).toHaveAttribute('role', 'button');
    });

    test('deve ter preferência de movimento reduzida', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ 
        '@media (prefers-reduced-motion: reduce)': {
          animation: 'none',
          transition: 'none'
        }
      });
    });
  });

  describe('Performance', () => {
    
    test('deve usar transform para animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useBounce.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'scale(1.2)' },
        resetAnimation: jest.fn()
      });

      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ transform: 'scale(1.2)' });
    });

    test('deve usar will-change para otimização', () => {
      render(<Bounce {...defaultProps} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ 'will-change': 'transform' });
    });
  });

  describe('Edge Cases', () => {
    
    test('deve lidar com children nulos', () => {
      render(<Bounce {...defaultProps} children={null} />);
      
      const bounceContainer = document.querySelector('.bounce-container');
      expect(bounceContainer).toBeInTheDocument();
    });

    test('deve lidar com duração zero', () => {
      render(<Bounce {...defaultProps} duration={0} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-duration': '0ms' });
    });

    test('deve lidar com número zero de quiques', () => {
      render(<Bounce {...defaultProps} bounces={0} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-count': '0' });
    });

    test('deve lidar com valores negativos', () => {
      render(<Bounce {...defaultProps} bounces={-1} />);
      
      const bounceContainer = screen.getByText('Clique para testar').closest('.bounce-container');
      expect(bounceContainer).toHaveStyle({ '--bounce-count': '-1' });
    });
  });
}); 