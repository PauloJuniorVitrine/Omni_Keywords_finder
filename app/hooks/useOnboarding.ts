import { useState } from 'react';

export interface OnboardingStepData {
  id: string;
  title: string;
  description: string;
  content?: React.ReactNode;
}

const defaultSteps: OnboardingStepData[] = [
  { id: 'welcome', title: 'Bem-vindo', description: 'Introdução ao sistema.' },
  { id: 'features', title: 'Funcionalidades', description: 'Conheça as principais funções.' },
  { id: 'finish', title: 'Finalizar', description: 'Pronto para começar!' }
];

export function useOnboarding(steps: OnboardingStepData[] = defaultSteps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const isCompleted = currentStepIndex >= steps.length;

  function goToNextStep() {
    setCurrentStepIndex((idx) => Math.min(idx + 1, steps.length));
  }

  function goToPreviousStep() {
    setCurrentStepIndex((idx) => Math.max(idx - 1, 0));
  }

  return {
    steps,
    currentStepIndex,
    goToNextStep,
    goToPreviousStep,
    isCompleted
  };
} 