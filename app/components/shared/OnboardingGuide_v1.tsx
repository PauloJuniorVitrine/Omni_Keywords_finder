import React from 'react';
import Joyride, { Step } from 'react-joyride';

/**
 * OnboardingGuide - Guia interativo de primeiros passos para novos usuários.
 * @param steps Lista de etapas do onboarding
 * @param run Se o onboarding está ativo
 * @param onClose Callback ao finalizar ou fechar o guia
 */
export interface OnboardingGuideProps {
  steps: Step[];
  run: boolean;
  onClose: () => void;
}

const OnboardingGuide: React.FC<OnboardingGuideProps> = ({ steps, run, onClose }) => {
  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showSkipButton
      showProgress
      disableScrolling
      locale={{ back: 'Voltar', close: 'Fechar', last: 'Finalizar', next: 'Próximo', skip: 'Pular' }}
      styles={{ options: { zIndex: 2000 } }}
      callback={data => {
        if (data.status === 'finished' || data.status === 'skipped') onClose();
      }}
    />
  );
};

export default OnboardingGuide; 