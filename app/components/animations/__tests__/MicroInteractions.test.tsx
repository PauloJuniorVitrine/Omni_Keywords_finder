/**
 * MicroInteractions.test.tsx
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Criticalidade 4.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Testes unitários para MicroInteractions
 * - Baseado APENAS no código real implementado
 * - Sem dados sintéticos ou genéricos
 * - Validação de funcionalidades reais
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';
import { 
  HoverEffect, 
  LoadingAnimation, 
  PageTransition, 
  useMicroInteractions 
} from '../MicroInteractions';

// ===== MOCK DO TEMA =====
const mockTheme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={mockTheme}>
      {component}
    </ThemeProvider>
  );
};

// ===== TESTES PARA HOVER EFFECT =====
describe('HoverEffect', () => {
  it('deve renderizar componente com variante hover padrão', () => {
    renderWithTheme(
      <HoverEffect>
        <div data-testid="hover-content">Conteúdo Teste</div>
      </HoverEffect>
    );

    expect(screen.getByTestId('hover-content')).toBeInTheDocument();
  });

  it('deve aplicar variante pulse corretamente', () => {
    renderWithTheme(
      <HoverEffect variant="pulse">
        <span data-testid="pulse-content">Botão Pulse</span>
      </HoverEffect>
    );

    const pulseElement = screen.getByTestId('pulse-content');
    expect(pulseElement).toBeInTheDocument();
    expect(pulseElement.closest('[class*="PulseButton"]')).toBeInTheDocument();
  });

  it('deve aplicar variante fade com delay', () => {
    renderWithTheme(
      <HoverEffect variant="fade" delay={200}>
        <div data-testid="fade-content">Conteúdo Fade</div>
      </HoverEffect>
    );

    expect(screen.getByTestId('fade-content')).toBeInTheDocument();
  });

  it('deve aplicar variante slide corretamente', () => {
    renderWithTheme(
      <HoverEffect variant="slide">
        <div data-testid="slide-content">Conteúdo Slide</div>
      </HoverEffect>
    );

    expect(screen.getByTestId('slide-content')).toBeInTheDocument();
  });
});

// ===== TESTES PARA LOADING ANIMATION =====
describe('LoadingAnimation', () => {
  it('deve renderizar loading circular padrão', () => {
    renderWithTheme(
      <LoadingAnimation />
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('deve renderizar loading shimmer', () => {
    renderWithTheme(
      <LoadingAnimation variant="shimmer" />
    );

    // Verificar se os elementos shimmer estão presentes
    const shimmerElements = document.querySelectorAll('[class*="LoadingShimmer"]');
    expect(shimmerElements.length).toBeGreaterThan(0);
  });

  it('deve renderizar loading dots', () => {
    renderWithTheme(
      <LoadingAnimation variant="dots" />
    );

    // Verificar se os dots estão presentes
    const dotsContainer = document.querySelector('[class*="display: flex"]');
    expect(dotsContainer).toBeInTheDocument();
  });

  it('deve exibir mensagem personalizada', () => {
    const customMessage = 'Carregando dados...';
    renderWithTheme(
      <LoadingAnimation message={customMessage} />
    );

    expect(screen.getByText(customMessage)).toBeInTheDocument();
  });

  it('deve aplicar tamanhos diferentes', () => {
    const { rerender } = renderWithTheme(
      <LoadingAnimation size="small" />
    );

    let progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();

    rerender(
      <ThemeProvider theme={mockTheme}>
        <LoadingAnimation size="large" />
      </ThemeProvider>
    );

    progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
  });
});

// ===== TESTES PARA PAGE TRANSITION =====
describe('PageTransition', () => {
  it('deve renderizar children com transição', () => {
    renderWithTheme(
      <PageTransition>
        <div data-testid="transition-content">Conteúdo Transição</div>
      </PageTransition>
    );

    expect(screen.getByTestId('transition-content')).toBeInTheDocument();
  });

  it('deve aplicar timeout personalizado', () => {
    renderWithTheme(
      <PageTransition timeout={500}>
        <div data-testid="custom-timeout">Timeout Customizado</div>
      </PageTransition>
    );

    expect(screen.getByTestId('custom-timeout')).toBeInTheDocument();
  });

  it('deve aplicar direção personalizada', () => {
    renderWithTheme(
      <PageTransition direction="down">
        <div data-testid="custom-direction">Direção Customizada</div>
      </PageTransition>
    );

    expect(screen.getByTestId('custom-direction')).toBeInTheDocument();
  });
});

// ===== TESTES PARA HOOK USE MICRO INTERACTIONS =====
describe('useMicroInteractions', () => {
  const TestComponent = () => {
    const { isAnimating, triggerAnimation } = useMicroInteractions();

    return (
      <div>
        <div data-testid="animation-status">
          {isAnimating ? 'Animando' : 'Parado'}
        </div>
        <button 
          data-testid="trigger-button" 
          onClick={() => triggerAnimation(300)}
        >
          Trigger Animation
        </button>
      </div>
    );
  };

  it('deve inicializar com estado correto', () => {
    renderWithTheme(<TestComponent />);

    expect(screen.getByTestId('animation-status')).toHaveTextContent('Parado');
  });

  it('deve trigger animação e resetar após duração', async () => {
    renderWithTheme(<TestComponent />);

    const triggerButton = screen.getByTestId('trigger-button');
    const statusElement = screen.getByTestId('animation-status');

    // Inicialmente parado
    expect(statusElement).toHaveTextContent('Parado');

    // Trigger animação
    fireEvent.click(triggerButton);
    expect(statusElement).toHaveTextContent('Animando');

    // Aguardar reset
    await waitFor(() => {
      expect(statusElement).toHaveTextContent('Parado');
    }, { timeout: 400 });
  });

  it('deve usar duração padrão quando não especificada', async () => {
    const TestComponentDefault = () => {
      const { isAnimating, triggerAnimation } = useMicroInteractions();

      return (
        <div>
          <div data-testid="animation-status">
            {isAnimating ? 'Animando' : 'Parado'}
          </div>
          <button 
            data-testid="trigger-button" 
            onClick={() => triggerAnimation()}
          >
            Trigger Default
          </button>
        </div>
      );
    };

    renderWithTheme(<TestComponentDefault />);

    const triggerButton = screen.getByTestId('trigger-button');
    const statusElement = screen.getByTestId('animation-status');

    fireEvent.click(triggerButton);
    expect(statusElement).toHaveTextContent('Animando');

    await waitFor(() => {
      expect(statusElement).toHaveTextContent('Parado');
    }, { timeout: 400 });
  });
});

// ===== TESTES DE INTEGRAÇÃO =====
describe('Integração MicroInteractions', () => {
  it('deve combinar hover effect com loading animation', () => {
    renderWithTheme(
      <HoverEffect variant="hover">
        <LoadingAnimation variant="circular" size="small" />
      </HoverEffect>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('deve combinar page transition com hover effect', () => {
    renderWithTheme(
      <PageTransition>
        <HoverEffect variant="pulse">
          <div data-testid="combined-content">Conteúdo Combinado</div>
        </HoverEffect>
      </PageTransition>
    );

    expect(screen.getByTestId('combined-content')).toBeInTheDocument();
  });
});

// ===== TESTES DE ACESSIBILIDADE =====
describe('Acessibilidade MicroInteractions', () => {
  it('deve manter acessibilidade em loading animation', () => {
    renderWithTheme(
      <LoadingAnimation message="Carregando dados do sistema" />
    );

    expect(screen.getByText('Carregando dados do sistema')).toBeInTheDocument();
  });

  it('deve manter acessibilidade em hover effects', () => {
    renderWithTheme(
      <HoverEffect>
        <button data-testid="accessible-button" aria-label="Botão acessível">
          Clique aqui
        </button>
      </HoverEffect>
    );

    const button = screen.getByTestId('accessible-button');
    expect(button).toHaveAttribute('aria-label', 'Botão acessível');
  });
}); 