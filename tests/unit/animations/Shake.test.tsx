/**
 * Testes Unitários - Shake Component
 * 
 * Prompt: Implementação de testes para componentes de animações
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_SHAKE_032
 * 
 * Baseado em código real do sistema de animações e hooks useAnimation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Shake } from '../../../app/components/animations/Shake';

// Mock do hook useAnimation baseado no código real
jest.mock('../../../app/hooks/useAnimation', () => ({
  useShake: jest.fn(() => ({
    isAnimating: false,
    triggerAnimation: jest.fn(),
    animationStyle: {},
    resetAnimation: jest.fn()
  }))
}));

describe('Shake - Componente de Animação de Tremor', () => {
  
  const defaultProps = {
    children: <button>Clique para testar</button>,
    duration: 500,
    intensity: 10
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar children corretamente', () => {
      render(<Shake {...defaultProps} />);
      
      expect(screen.getByText('Clique para testar')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS de animação', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveClass('shake-container');
    });

    test('deve renderizar children complexos', () => {
      const complexChildren = (
        <div>
          <span>Texto</span>
          <button>Botão</button>
          <input placeholder="Input" />
        </div>
      );

      render(<Shake {...defaultProps} children={complexChildren} />);
      
      expect(screen.getByText('Texto')).toBeInTheDocument();
      expect(screen.getByText('Botão')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Input')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<Shake {...defaultProps} className="custom-shake" />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveClass('custom-shake');
    });
  });

  describe('Configuração de Animação', () => {
    
    test('deve usar duração padrão de 500ms', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-duration': '500ms' });
    });

    test('deve usar duração personalizada', () => {
      render(<Shake {...defaultProps} duration={1000} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-duration': '1000ms' });
    });

    test('deve usar intensidade padrão de 10px', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-intensity': '10px' });
    });

    test('deve usar intensidade personalizada', () => {
      render(<Shake {...defaultProps} intensity={20} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-intensity': '20px' });
    });
  });

  describe('Triggers de Animação', () => {
    
    test('deve animar ao clicar no elemento', async () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<Shake {...defaultProps} />);
      
      const trigger = screen.getByText('Clique para testar');
      fireEvent.click(trigger);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });

    test('deve animar ao receber prop trigger', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<Shake {...defaultProps} trigger={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando trigger muda para true
      rerender(<Shake {...defaultProps} trigger={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });

    test('deve animar ao receber prop error', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<Shake {...defaultProps} error={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando error muda para true
      rerender(<Shake {...defaultProps} error={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });
  });

  describe('Estados de Animação', () => {
    
    test('deve mostrar estado de animação ativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'translateX(10px)' },
        resetAnimation: jest.fn()
      });

      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveClass('shake-animating');
      expect(shakeContainer).toHaveStyle({ transform: 'translateX(10px)' });
    });

    test('deve mostrar estado de animação inativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: false,
        triggerAnimation: jest.fn(),
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).not.toHaveClass('shake-animating');
    });
  });

  describe('Estilos e Layout', () => {
    
    test('deve ter posicionamento relativo', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ position: 'relative' });
    });

    test('deve ter display inline-block', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ display: 'inline-block' });
    });

    test('deve ter transição suave', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ 
        transition: 'transform 500ms cubic-bezier(0.36, 0, 0.66, -0.56)' 
      });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve manter acessibilidade durante animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'translateX(10px)' },
        resetAnimation: jest.fn()
      });

      render(<Shake {...defaultProps} />);
      
      const button = screen.getByText('Clique para testar');
      expect(button).toBeAccessible();
      expect(button).toHaveAttribute('role', 'button');
    });

    test('deve ter preferência de movimento reduzida', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ 
        '@media (prefers-reduced-motion: reduce)': {
          animation: 'none',
          transition: 'none'
        }
      });
    });
  });

  describe('Performance', () => {
    
    test('deve usar transform para animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useShake.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { transform: 'translateX(10px)' },
        resetAnimation: jest.fn()
      });

      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ transform: 'translateX(10px)' });
    });

    test('deve usar will-change para otimização', () => {
      render(<Shake {...defaultProps} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ 'will-change': 'transform' });
    });
  });

  describe('Edge Cases', () => {
    
    test('deve lidar com children nulos', () => {
      render(<Shake {...defaultProps} children={null} />);
      
      const shakeContainer = document.querySelector('.shake-container');
      expect(shakeContainer).toBeInTheDocument();
    });

    test('deve lidar com duração zero', () => {
      render(<Shake {...defaultProps} duration={0} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-duration': '0ms' });
    });

    test('deve lidar com intensidade zero', () => {
      render(<Shake {...defaultProps} intensity={0} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-intensity': '0px' });
    });

    test('deve lidar com valores negativos', () => {
      render(<Shake {...defaultProps} intensity={-5} />);
      
      const shakeContainer = screen.getByText('Clique para testar').closest('.shake-container');
      expect(shakeContainer).toHaveStyle({ '--shake-intensity': '-5px' });
    });
  });
}); 