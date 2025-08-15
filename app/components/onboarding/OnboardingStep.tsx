import React from 'react';

export interface OnboardingStepProps {
  step: {
    id: string;
    title: string;
    description: string;
    content?: React.ReactNode;
  };
}

export const OnboardingStep: React.FC<OnboardingStepProps> = ({ step }) => {
  return (
    <div className="onboarding-step">
      <h2>{step.title}</h2>
      <p>{step.description}</p>
      {step.content && <div className="onboarding-step-content">{step.content}</div>}
    </div>
  );
}; 