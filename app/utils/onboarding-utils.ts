// Utilitários para onboarding interativo

export function getDefaultOnboardingSteps() {
  return [
    { id: 'welcome', title: 'Bem-vindo', description: 'Introdução ao sistema.' },
    { id: 'features', title: 'Funcionalidades', description: 'Conheça as principais funções.' },
    { id: 'finish', title: 'Finalizar', description: 'Pronto para começar!' }
  ];
}

export function isOnboardingCompleted(currentStep: number, totalSteps: number) {
  return currentStep >= totalSteps;
} 