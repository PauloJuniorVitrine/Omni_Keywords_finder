/**
 * Índice dos Componentes de Onboarding - Omni Keywords Finder
 * Exporta todos os componentes modulares do sistema de onboarding
 * 
 * Tracing ID: ONBOARDING_STEPS_INDEX_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

export { default as WelcomeStep } from './WelcomeStep';
export { default as CompanyStep } from './CompanyStep';
export { default as GoalsStep } from './GoalsStep';
export { default as KeywordsStep } from './KeywordsStep';
export { default as FinishStep } from './FinishStep';

// Tipos compartilhados
export interface OnboardingData {
  user: {
    name: string;
    email: string;
    company: string;
    role: string;
  };
  company: {
    name: string;
    industry: string;
    size: string;
    website: string;
    country: string;
  };
  goals: {
    primary: string[];
    secondary: string[];
    timeframe: string;
    budget: string;
    priority: string;
  };
  keywords: {
    initial: string[];
    competitors: string[];
    suggestions: string[];
  };
}

export interface StepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
  onBack: () => void;
  isActive: boolean;
  errors: string[];
}

// Configurações dos passos
export const ONBOARDING_STEPS = [
  {
    id: 'welcome',
    title: 'Boas-vindas',
    description: 'Dados básicos do usuário',
    component: 'WelcomeStep',
    icon: '👋',
    required: true
  },
  {
    id: 'company',
    title: 'Empresa',
    description: 'Informações da empresa',
    component: 'CompanyStep',
    icon: '🏢',
    required: true
  },
  {
    id: 'goals',
    title: 'Objetivos',
    description: 'Definição de metas',
    component: 'GoalsStep',
    icon: '🎯',
    required: true
  },
  {
    id: 'keywords',
    title: 'Palavras-chave',
    description: 'Configuração inicial',
    component: 'KeywordsStep',
    icon: '🔍',
    required: true
  },
  {
    id: 'finish',
    title: 'Finalização',
    description: 'Resumo e conclusão',
    component: 'FinishStep',
    icon: '✅',
    required: true
  }
] as const;

// Validações específicas por passo
export const STEP_VALIDATIONS = {
  welcome: {
    required: ['user.name', 'user.email'],
    email: true,
    minLength: { 'user.name': 2 }
  },
  company: {
    required: ['company.name', 'company.industry', 'company.size'],
    minLength: { 'company.name': 2 }
  },
  goals: {
    required: ['goals.primary', 'goals.timeframe', 'goals.priority'],
    minArrayLength: { 'goals.primary': 1 }
  },
  keywords: {
    required: ['keywords.initial'],
    minArrayLength: { 'keywords.initial': 1 }
  },
  finish: {
    required: []
  }
} as const;

// Configurações de animação
export const ANIMATION_CONFIG = {
  stepTransition: {
    duration: 0.3,
    ease: 'easeInOut'
  },
  staggerDelay: 0.1,
  springConfig: {
    type: 'spring',
    stiffness: 200,
    damping: 20
  }
} as const; 