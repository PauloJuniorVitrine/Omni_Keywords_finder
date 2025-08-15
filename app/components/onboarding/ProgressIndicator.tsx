import React from 'react';

export interface ProgressIndicatorProps {
  steps: Array<{ id: string; title: string }>;
  currentStepIndex: number;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ steps, currentStepIndex }) => {
  return (
    <div className="progress-indicator">
      {steps.map((step, idx) => (
        <div
          key={step.id}
          className={`progress-step${idx === currentStepIndex ? ' active' : ''}`}
        >
          {step.title}
        </div>
      ))}
    </div>
  );
}; 