/**
 * Testes Unitários - FadeIn Component
 * 
 * Prompt: Implementação de testes para componentes de animações
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_FADE_IN_034
 * 
 * Baseado em código real do sistema de animações e hooks useAnimation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FadeIn } from '../../../app/components/animations/FadeIn';

// Mock do hook useAnimation baseado no código real
jest.mock('../../../app/hooks/useAnimation', () => ({
  useFadeIn: jest.fn(() => ({
    isAnimating: false,
    triggerAnimation: jest.fn(),
    animationStyle: {},
    resetAnimation: jest.fn()
  }))
}));

describe('FadeIn - Componente de Animação de Aparição', () => {
  
  const defaultProps = {
    children: <div>Conteúdo que aparece</div>,
    duration: 300,
    delay: 0
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar children corretamente', () => {
      render(<FadeIn {...defaultProps} />);
      
      expect(screen.getByText('Conteúdo que aparece')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS de animação', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveClass('fade-in-container');
    });

    test('deve renderizar children complexos', () => {
      const complexChildren = (
        <div>
          <h1>Título</h1>
          <p>Parágrafo de texto</p>
          <button>Botão</button>
        </div>
      );

      render(<FadeIn {...defaultProps} children={complexChildren} />);
      
      expect(screen.getByText('Título')).toBeInTheDocument();
      expect(screen.getByText('Parágrafo de texto')).toBeInTheDocument();
      expect(screen.getByText('Botão')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<FadeIn {...defaultProps} className="custom-fade-in" />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveClass('custom-fade-in');
    });
  });

  describe('Configuração de Animação', () => {
    
    test('deve usar duração padrão de 300ms', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-duration': '300ms' });
    });

    test('deve usar duração personalizada', () => {
      render(<FadeIn {...defaultProps} duration={500} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-duration': '500ms' });
    });

    test('deve usar delay padrão de 0ms', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-delay': '0ms' });
    });

    test('deve usar delay personalizado', () => {
      render(<FadeIn {...defaultProps} delay={200} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-delay': '200ms' });
    });
  });

  describe('Triggers de Animação', () => {
    
    test('deve animar automaticamente ao montar', async () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<FadeIn {...defaultProps} />);
      
      await waitFor(() => {
        expect(mockTriggerAnimation).toHaveBeenCalled();
      });
    });

    test('deve animar ao receber prop trigger', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<FadeIn {...defaultProps} trigger={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando trigger muda para true
      rerender(<FadeIn {...defaultProps} trigger={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });

    test('deve animar ao receber prop visible', () => {
      const mockTriggerAnimation = jest.fn();
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: false,
        triggerAnimation: mockTriggerAnimation,
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      const { rerender } = render(<FadeIn {...defaultProps} visible={false} />);
      
      // Inicialmente não deve animar
      expect(mockTriggerAnimation).not.toHaveBeenCalled();
      
      // Deve animar quando visible muda para true
      rerender(<FadeIn {...defaultProps} visible={true} />);
      
      expect(mockTriggerAnimation).toHaveBeenCalled();
    });
  });

  describe('Estados de Animação', () => {
    
    test('deve mostrar estado de animação ativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { opacity: 0.5 },
        resetAnimation: jest.fn()
      });

      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveClass('fade-in-animating');
      expect(fadeInContainer).toHaveStyle({ opacity: 0.5 });
    });

    test('deve mostrar estado de animação inativa', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: false,
        triggerAnimation: jest.fn(),
        animationStyle: {},
        resetAnimation: jest.fn()
      });

      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).not.toHaveClass('fade-in-animating');
    });

    test('deve iniciar com opacity 0', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ opacity: 0 });
    });
  });

  describe('Estilos e Layout', () => {
    
    test('deve ter posicionamento relativo', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ position: 'relative' });
    });

    test('deve ter display block', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ display: 'block' });
    });

    test('deve ter transição suave', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ 
        transition: 'opacity 300ms ease-in-out' 
      });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve manter acessibilidade durante animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { opacity: 0.5 },
        resetAnimation: jest.fn()
      });

      render(<FadeIn {...defaultProps} />);
      
      const content = screen.getByText('Conteúdo que aparece');
      expect(content).toBeAccessible();
    });

    test('deve ter preferência de movimento reduzida', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ 
        '@media (prefers-reduced-motion: reduce)': {
          animation: 'none',
          transition: 'none',
          opacity: 1
        }
      });
    });

    test('deve ter aria-hidden durante animação inicial', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Performance', () => {
    
    test('deve usar opacity para animação', () => {
      jest.requireMock('../../../app/hooks/useAnimation').useFadeIn.mockReturnValue({
        isAnimating: true,
        triggerAnimation: jest.fn(),
        animationStyle: { opacity: 0.5 },
        resetAnimation: jest.fn()
      });

      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ opacity: 0.5 });
    });

    test('deve usar will-change para otimização', () => {
      render(<FadeIn {...defaultProps} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ 'will-change': 'opacity' });
    });
  });

  describe('Edge Cases', () => {
    
    test('deve lidar com children nulos', () => {
      render(<FadeIn {...defaultProps} children={null} />);
      
      const fadeInContainer = document.querySelector('.fade-in-container');
      expect(fadeInContainer).toBeInTheDocument();
    });

    test('deve lidar com duração zero', () => {
      render(<FadeIn {...defaultProps} duration={0} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-duration': '0ms' });
    });

    test('deve lidar com delay negativo', () => {
      render(<FadeIn {...defaultProps} delay={-100} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-delay': '-100ms' });
    });

    test('deve lidar com delay muito alto', () => {
      render(<FadeIn {...defaultProps} delay={10000} />);
      
      const fadeInContainer = screen.getByText('Conteúdo que aparece').closest('.fade-in-container');
      expect(fadeInContainer).toHaveStyle({ '--fade-in-delay': '10000ms' });
    });
  });
}); 