/**
 * useOnboarding.test.ts
 * 
 * Testes unitários para o hook useOnboarding
 * 
 * Tracing ID: TEST-USE-ONBOARDING-001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import { renderHook, act } from '@testing-library/react';
import { useOnboarding, OnboardingStepData } from '../../app/hooks/useOnboarding';

describe('useOnboarding Hook', () => {
  describe('Inicialização', () => {
    it('deve inicializar com steps padrão', () => {
      const { result } = renderHook(() => useOnboarding());

      expect(result.current.steps).toEqual([
        { id: 'welcome', title: 'Bem-vindo', description: 'Introdução ao sistema.' },
        { id: 'features', title: 'Funcionalidades', description: 'Conheça as principais funções.' },
        { id: 'finish', title: 'Finalizar', description: 'Pronto para começar!' }
      ]);
      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);
    });

    it('deve inicializar com steps customizados', () => {
      const customSteps: OnboardingStepData[] = [
        { id: 'step1', title: 'Passo 1', description: 'Descrição do passo 1' },
        { id: 'step2', title: 'Passo 2', description: 'Descrição do passo 2' }
      ];

      const { result } = renderHook(() => useOnboarding(customSteps));

      expect(result.current.steps).toEqual(customSteps);
      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);
    });

    it('deve inicializar com array vazio', () => {
      const { result } = renderHook(() => useOnboarding([]));

      expect(result.current.steps).toEqual([]);
      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(true);
    });
  });

  describe('Navegação entre Steps', () => {
    it('deve avançar para o próximo step', () => {
      const { result } = renderHook(() => useOnboarding());

      expect(result.current.currentStepIndex).toBe(0);

      act(() => {
        result.current.goToNextStep();
      });

      expect(result.current.currentStepIndex).toBe(1);
      expect(result.current.isCompleted).toBe(false);
    });

    it('deve voltar para o step anterior', () => {
      const { result } = renderHook(() => useOnboarding());

      // Avançar primeiro
      act(() => {
        result.current.goToNextStep();
      });

      expect(result.current.currentStepIndex).toBe(1);

      // Voltar
      act(() => {
        result.current.goToPreviousStep();
      });

      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);
    });

    it('não deve avançar além do último step', () => {
      const { result } = renderHook(() => useOnboarding());

      // Avançar até o final
      act(() => {
        result.current.goToNextStep(); // 1
        result.current.goToNextStep(); // 2
        result.current.goToNextStep(); // 3 (deve parar aqui)
        result.current.goToNextStep(); // ainda 3
      });

      expect(result.current.currentStepIndex).toBe(3);
      expect(result.current.isCompleted).toBe(true);
    });

    it('não deve voltar antes do primeiro step', () => {
      const { result } = renderHook(() => useOnboarding());

      expect(result.current.currentStepIndex).toBe(0);

      act(() => {
        result.current.goToPreviousStep();
      });

      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);
    });
  });

  describe('Estado de Conclusão', () => {
    it('deve marcar como completo quando chegar ao último step', () => {
      const { result } = renderHook(() => useOnboarding());

      expect(result.current.isCompleted).toBe(false);

      act(() => {
        result.current.goToNextStep(); // 1
        result.current.goToNextStep(); // 2
        result.current.goToNextStep(); // 3
      });

      expect(result.current.isCompleted).toBe(true);
    });

    it('deve marcar como completo com array vazio', () => {
      const { result } = renderHook(() => useOnboarding([]));

      expect(result.current.isCompleted).toBe(true);
    });

    it('deve marcar como completo com apenas um step', () => {
      const singleStep: OnboardingStepData[] = [
        { id: 'single', title: 'Único', description: 'Apenas um step' }
      ];

      const { result } = renderHook(() => useOnboarding(singleStep));

      expect(result.current.isCompleted).toBe(false);

      act(() => {
        result.current.goToNextStep();
      });

      expect(result.current.isCompleted).toBe(true);
    });
  });

  describe('Steps com Conteúdo Customizado', () => {
    it('deve suportar steps com conteúdo React', () => {
      const stepsWithContent: OnboardingStepData[] = [
        { 
          id: 'welcome', 
          title: 'Bem-vindo', 
          description: 'Introdução ao sistema.',
          content: <div>Conteúdo customizado</div>
        },
        { 
          id: 'features', 
          title: 'Funcionalidades', 
          description: 'Conheça as principais funções.',
          content: <div>Lista de funcionalidades</div>
        }
      ];

      const { result } = renderHook(() => useOnboarding(stepsWithContent));

      expect(result.current.steps[0].content).toBeDefined();
      expect(result.current.steps[1].content).toBeDefined();
    });

    it('deve funcionar com steps sem conteúdo', () => {
      const stepsWithoutContent: OnboardingStepData[] = [
        { id: 'step1', title: 'Passo 1', description: 'Descrição 1' },
        { id: 'step2', title: 'Passo 2', description: 'Descrição 2' }
      ];

      const { result } = renderHook(() => useOnboarding(stepsWithoutContent));

      expect(result.current.steps[0].content).toBeUndefined();
      expect(result.current.steps[1].content).toBeUndefined();
    });
  });

  describe('Navegação Múltipla', () => {
    it('deve navegar corretamente entre múltiplos steps', () => {
      const { result } = renderHook(() => useOnboarding());

      // Sequência: 0 -> 1 -> 2 -> 1 -> 0 -> 1 -> 2 -> 3
      act(() => {
        result.current.goToNextStep(); // 0 -> 1
        expect(result.current.currentStepIndex).toBe(1);
        
        result.current.goToNextStep(); // 1 -> 2
        expect(result.current.currentStepIndex).toBe(2);
        
        result.current.goToPreviousStep(); // 2 -> 1
        expect(result.current.currentStepIndex).toBe(1);
        
        result.current.goToPreviousStep(); // 1 -> 0
        expect(result.current.currentStepIndex).toBe(0);
        
        result.current.goToNextStep(); // 0 -> 1
        expect(result.current.currentStepIndex).toBe(1);
        
        result.current.goToNextStep(); // 1 -> 2
        expect(result.current.currentStepIndex).toBe(2);
        
        result.current.goToNextStep(); // 2 -> 3
        expect(result.current.currentStepIndex).toBe(3);
      });

      expect(result.current.isCompleted).toBe(true);
    });

    it('deve manter estado correto após navegação intensiva', () => {
      const { result } = renderHook(() => useOnboarding());

      // Navegação intensiva
      act(() => {
        for (let i = 0; i < 10; i++) {
          result.current.goToNextStep();
        }
      });

      expect(result.current.currentStepIndex).toBe(3); // Máximo
      expect(result.current.isCompleted).toBe(true);

      act(() => {
        for (let i = 0; i < 10; i++) {
          result.current.goToPreviousStep();
        }
      });

      expect(result.current.currentStepIndex).toBe(0); // Mínimo
      expect(result.current.isCompleted).toBe(false);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com steps com IDs duplicados', () => {
      const stepsWithDuplicates: OnboardingStepData[] = [
        { id: 'duplicate', title: 'Primeiro', description: 'Primeiro step' },
        { id: 'duplicate', title: 'Segundo', description: 'Segundo step' }
      ];

      const { result } = renderHook(() => useOnboarding(stepsWithDuplicates));

      expect(result.current.steps).toHaveLength(2);
      expect(result.current.steps[0].id).toBe('duplicate');
      expect(result.current.steps[1].id).toBe('duplicate');
    });

    it('deve lidar com steps com títulos vazios', () => {
      const stepsWithEmptyTitles: OnboardingStepData[] = [
        { id: 'step1', title: '', description: 'Descrição válida' },
        { id: 'step2', title: 'Título válido', description: '' }
      ];

      const { result } = renderHook(() => useOnboarding(stepsWithEmptyTitles));

      expect(result.current.steps[0].title).toBe('');
      expect(result.current.steps[1].description).toBe('');
    });

    it('deve funcionar com steps muito longos', () => {
      const longSteps: OnboardingStepData[] = Array.from({ length: 100 }, (_, i) => ({
        id: `step${i}`,
        title: `Step ${i}`,
        description: `Descrição do step ${i}`
      }));

      const { result } = renderHook(() => useOnboarding(longSteps));

      expect(result.current.steps).toHaveLength(100);
      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);

      // Avançar até o final
      act(() => {
        for (let i = 0; i < 100; i++) {
          result.current.goToNextStep();
        }
      });

      expect(result.current.currentStepIndex).toBe(100);
      expect(result.current.isCompleted).toBe(true);
    });
  });

  describe('Integração com React', () => {
    it('deve manter estado entre re-renders', () => {
      const { result, rerender } = renderHook(() => useOnboarding());

      act(() => {
        result.current.goToNextStep();
      });

      expect(result.current.currentStepIndex).toBe(1);

      rerender();

      expect(result.current.currentStepIndex).toBe(1);
      expect(result.current.isCompleted).toBe(false);
    });

    it('deve resetar estado ao mudar steps', () => {
      const { result, rerender } = renderHook(
        ({ steps }) => useOnboarding(steps),
        { initialProps: { steps: [] } }
      );

      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(true);

      const newSteps: OnboardingStepData[] = [
        { id: 'new1', title: 'Novo 1', description: 'Descrição 1' },
        { id: 'new2', title: 'Novo 2', description: 'Descrição 2' }
      ];

      rerender({ steps: newSteps });

      expect(result.current.currentStepIndex).toBe(0);
      expect(result.current.isCompleted).toBe(false);
      expect(result.current.steps).toEqual(newSteps);
    });
  });
}); 