import React from 'react';
import { OnboardingStep } from './OnboardingStep';
import { ProgressIndicator } from './ProgressIndicator';
import { useOnboarding } from '../../hooks/useOnboarding';

export const OnboardingFlow: React.FC = () => {
  const {
    steps,
    currentStepIndex,
    goToNextStep,
    goToPreviousStep,
    isCompleted
  } = useOnboarding();

  if (isCompleted) {
    return <div>Onboarding concluído!</div>;
  }

  return (
    <div className="onboarding-flow">
      <ProgressIndicator steps={steps} currentStepIndex={currentStepIndex} />
      <OnboardingStep step={steps[currentStepIndex]} />
      <div className="onboarding-actions">
        <button onClick={goToPreviousStep} disabled={currentStepIndex === 0}>Anterior</button>
        <button onClick={goToNextStep} disabled={currentStepIndex === steps.length - 1}>Próximo</button>
      </div>
    </div>
  );
}; 