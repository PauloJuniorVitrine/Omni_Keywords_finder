/**
 * Testes Unitários - Componentes de Onboarding
 * Omni Keywords Finder
 * 
 * Tracing ID: TEST_ONBOARDING_COMPONENTS_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Testes de Componentes de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { motion } from 'framer-motion';

// Mock framer-motion para testes
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>
  }
}));

// Importar componentes
import {
  WelcomeStep,
  CompanyStep,
  GoalsStep,
  KeywordsStep,
  FinishStep,
  OnboardingData,
  StepProps
} from '../../app/components/onboarding/steps';

// Dados de teste baseados no código real
const mockOnboardingData: OnboardingData = {
  user: {
    name: 'João Silva',
    email: 'joao@empresa.com',
    company: 'Empresa Teste',
    role: 'Marketing Manager'
  },
  company: {
    name: 'Empresa Teste LTDA',
    industry: 'Tecnologia',
    size: '11-50',
    website: 'https://empresa-teste.com',
    country: 'Brasil'
  },
  goals: {
    primary: ['increase-traffic', 'improve-rankings'],
    secondary: ['content-optimization'],
    timeframe: '3-6-months',
    budget: 'medium',
    priority: 'high'
  },
  keywords: {
    initial: ['software desenvolvimento', 'sistema gestão'],
    competitors: ['concorrente palavra-chave'],
    suggestions: ['tecnologia inovação', 'startup tecnologia']
  }
};

// Props padrão para testes
const createStepProps = (data: Partial<OnboardingData> = {}): StepProps => ({
  data: { ...mockOnboardingData, ...data },
  updateData: jest.fn(),
  onNext: jest.fn(),
  onBack: jest.fn(),
  isActive: true,
  errors: []
});

describe('WelcomeStep Component', () => {
  const renderWelcomeStep = (props = createStepProps()) => {
    return render(<WelcomeStep {...props} />);
  };

  test('deve renderizar campos de nome e email', () => {
    renderWelcomeStep();
    
    expect(screen.getByLabelText(/nome completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument();
  });

  test('deve validar nome obrigatório', async () => {
    const user = userEvent.setup();
    renderWelcomeStep();
    
    const emailInput = screen.getByLabelText(/e-mail/i);
    await user.type(emailInput, 'teste@email.com');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar email obrigatório', async () => {
    const user = userEvent.setup();
    renderWelcomeStep();
    
    const nameInput = screen.getByLabelText(/nome completo/i);
    await user.type(nameInput, 'João Silva');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar formato de email', async () => {
    const user = userEvent.setup();
    renderWelcomeStep();
    
    const nameInput = screen.getByLabelText(/nome completo/i);
    const emailInput = screen.getByLabelText(/e-mail/i);
    
    await user.type(nameInput, 'João Silva');
    await user.type(emailInput, 'email-invalido');
    
    expect(screen.getByText(/e-mail deve ter um formato válido/i)).toBeInTheDocument();
  });

  test('deve habilitar botão quando dados são válidos', async () => {
    const user = userEvent.setup();
    const onNext = jest.fn();
    renderWelcomeStep({ ...createStepProps(), onNext });
    
    const nameInput = screen.getByLabelText(/nome completo/i);
    const emailInput = screen.getByLabelText(/e-mail/i);
    
    await user.type(nameInput, 'João Silva');
    await user.type(emailInput, 'joao@empresa.com');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeEnabled();
    
    await user.click(continueButton);
    expect(onNext).toHaveBeenCalled();
  });

  test('deve permitir navegação com Enter', async () => {
    const user = userEvent.setup();
    const onNext = jest.fn();
    renderWelcomeStep({ ...createStepProps(), onNext });
    
    const nameInput = screen.getByLabelText(/nome completo/i);
    const emailInput = screen.getByLabelText(/e-mail/i);
    
    await user.type(nameInput, 'João Silva');
    await user.type(emailInput, 'joao@empresa.com');
    await user.keyboard('{Enter}');
    
    expect(onNext).toHaveBeenCalled();
  });
});

describe('CompanyStep Component', () => {
  const renderCompanyStep = (props = createStepProps()) => {
    return render(<CompanyStep {...props} />);
  };

  test('deve renderizar campos da empresa', () => {
    renderCompanyStep();
    
    expect(screen.getByLabelText(/nome da empresa/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/setor\/indústria/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tamanho da empresa/i)).toBeInTheDocument();
  });

  test('deve validar nome da empresa obrigatório', async () => {
    const user = userEvent.setup();
    renderCompanyStep();
    
    const industrySelect = screen.getByLabelText(/setor\/indústria/i);
    const sizeSelect = screen.getByLabelText(/tamanho da empresa/i);
    
    await user.selectOptions(industrySelect, 'Tecnologia');
    await user.selectOptions(sizeSelect, '11-50');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar indústria obrigatória', async () => {
    const user = userEvent.setup();
    renderCompanyStep();
    
    const companyInput = screen.getByLabelText(/nome da empresa/i);
    const sizeSelect = screen.getByLabelText(/tamanho da empresa/i);
    
    await user.type(companyInput, 'Empresa Teste');
    await user.selectOptions(sizeSelect, '11-50');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar website opcional', async () => {
    const user = userEvent.setup();
    renderCompanyStep();
    
    const companyInput = screen.getByLabelText(/nome da empresa/i);
    const industrySelect = screen.getByLabelText(/setor\/indústria/i);
    const sizeSelect = screen.getByLabelText(/tamanho da empresa/i);
    const websiteInput = screen.getByLabelText(/website da empresa/i);
    
    await user.type(companyInput, 'Empresa Teste');
    await user.selectOptions(industrySelect, 'Tecnologia');
    await user.selectOptions(sizeSelect, '11-50');
    await user.type(websiteInput, 'website-invalido');
    
    expect(screen.getByText(/website deve ter um formato válido/i)).toBeInTheDocument();
  });

  test('deve habilitar botão quando dados obrigatórios são preenchidos', async () => {
    const user = userEvent.setup();
    const onNext = jest.fn();
    renderCompanyStep({ ...createStepProps(), onNext });
    
    const companyInput = screen.getByLabelText(/nome da empresa/i);
    const industrySelect = screen.getByLabelText(/setor\/indústria/i);
    const sizeSelect = screen.getByLabelText(/tamanho da empresa/i);
    
    await user.type(companyInput, 'Empresa Teste');
    await user.selectOptions(industrySelect, 'Tecnologia');
    await user.selectOptions(sizeSelect, '11-50');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeEnabled();
    
    await user.click(continueButton);
    expect(onNext).toHaveBeenCalled();
  });

  test('deve chamar onBack ao clicar em voltar', async () => {
    const user = userEvent.setup();
    const onBack = jest.fn();
    renderCompanyStep({ ...createStepProps(), onBack });
    
    const backButton = screen.getByRole('button', { name: /voltar/i });
    await user.click(backButton);
    
    expect(onBack).toHaveBeenCalled();
  });
});

describe('GoalsStep Component', () => {
  const renderGoalsStep = (props = createStepProps()) => {
    return render(<GoalsStep {...props} />);
  };

  test('deve renderizar objetivos primários', () => {
    renderGoalsStep();
    
    expect(screen.getByText(/aumentar tráfego orgânico/i)).toBeInTheDocument();
    expect(screen.getByText(/melhorar posicionamento/i)).toBeInTheDocument();
    expect(screen.getByText(/gerar mais leads/i)).toBeInTheDocument();
  });

  test('deve permitir seleção de objetivos primários', async () => {
    const user = userEvent.setup();
    renderGoalsStep();
    
    const trafficGoal = screen.getByText(/aumentar tráfego orgânico/i);
    await user.click(trafficGoal);
    
    expect(trafficGoal.closest('button')).toHaveClass('border-blue-500');
  });

  test('deve validar pelo menos um objetivo primário', async () => {
    const user = userEvent.setup();
    renderGoalsStep();
    
    const timeframeButton = screen.getByText(/3-6 meses/i);
    const priorityButton = screen.getByText(/alta prioridade/i);
    
    await user.click(timeframeButton);
    await user.click(priorityButton);
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar prazo obrigatório', async () => {
    const user = userEvent.setup();
    renderGoalsStep();
    
    const trafficGoal = screen.getByText(/aumentar tráfego orgânico/i);
    const priorityButton = screen.getByText(/alta prioridade/i);
    
    await user.click(trafficGoal);
    await user.click(priorityButton);
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve validar prioridade obrigatória', async () => {
    const user = userEvent.setup();
    renderGoalsStep();
    
    const trafficGoal = screen.getByText(/aumentar tráfego orgânico/i);
    const timeframeButton = screen.getByText(/3-6 meses/i);
    
    await user.click(trafficGoal);
    await user.click(timeframeButton);
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve habilitar botão quando todos os campos obrigatórios são preenchidos', async () => {
    const user = userEvent.setup();
    const onNext = jest.fn();
    renderGoalsStep({ ...createStepProps(), onNext });
    
    const trafficGoal = screen.getByText(/aumentar tráfego orgânico/i);
    const timeframeButton = screen.getByText(/3-6 meses/i);
    const priorityButton = screen.getByText(/alta prioridade/i);
    
    await user.click(trafficGoal);
    await user.click(timeframeButton);
    await user.click(priorityButton);
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeEnabled();
    
    await user.click(continueButton);
    expect(onNext).toHaveBeenCalled();
  });

  test('deve permitir seleção de objetivos secundários', async () => {
    const user = userEvent.setup();
    renderGoalsStep();
    
    const contentGoal = screen.getByText(/otimização de conteúdo/i);
    await user.click(contentGoal);
    
    expect(contentGoal.closest('button')).toHaveClass('border-green-500');
  });
});

describe('KeywordsStep Component', () => {
  const renderKeywordsStep = (props = createStepProps()) => {
    return render(<KeywordsStep {...props} />);
  };

  test('deve renderizar campo de palavras-chave', () => {
    renderKeywordsStep();
    
    expect(screen.getByPlaceholderText(/digite uma palavra-chave/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /continuar/i })).toBeInTheDocument();
  });

  test('deve permitir adicionar palavra-chave', async () => {
    const user = userEvent.setup();
    renderKeywordsStep();
    
    const keywordInput = screen.getByPlaceholderText(/digite uma palavra-chave/i);
    const addButton = screen.getByRole('button', { name: /continuar/i }).previousElementSibling;
    
    await user.type(keywordInput, 'palavra-chave teste');
    await user.click(addButton!);
    
    expect(screen.getByText(/palavra-chave teste/i)).toBeInTheDocument();
  });

  test('deve permitir adicionar palavra-chave com Enter', async () => {
    const user = userEvent.setup();
    renderKeywordsStep();
    
    const keywordInput = screen.getByPlaceholderText(/digite uma palavra-chave/i);
    
    await user.type(keywordInput, 'palavra-chave teste');
    await user.keyboard('{Enter}');
    
    expect(screen.getByText(/palavra-chave teste/i)).toBeInTheDocument();
  });

  test('deve permitir remover palavra-chave', async () => {
    const user = userEvent.setup();
    renderKeywordsStep();
    
    const keywordInput = screen.getByPlaceholderText(/digite uma palavra-chave/i);
    const addButton = screen.getByRole('button', { name: /continuar/i }).previousElementSibling;
    
    await user.type(keywordInput, 'palavra-chave teste');
    await user.click(addButton!);
    
    const removeButton = screen.getByRole('button', { name: '' }); // Botão X
    await user.click(removeButton);
    
    expect(screen.queryByText(/palavra-chave teste/i)).not.toBeInTheDocument();
  });

  test('deve validar pelo menos uma palavra-chave', async () => {
    renderKeywordsStep();
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeDisabled();
  });

  test('deve mostrar sugestões baseadas na indústria', () => {
    renderKeywordsStep();
    
    expect(screen.getByText(/sugestões para tecnologia/i)).toBeInTheDocument();
    expect(screen.getByText(/software desenvolvimento/i)).toBeInTheDocument();
  });

  test('deve permitir adicionar sugestão', async () => {
    const user = userEvent.setup();
    renderKeywordsStep();
    
    const suggestionButton = screen.getByText(/software desenvolvimento/i);
    await user.click(suggestionButton);
    
    expect(suggestionButton.closest('button')).toHaveClass('border-green-500');
  });

  test('deve permitir adicionar palavras-chave de concorrentes', async () => {
    const user = userEvent.setup();
    renderKeywordsStep();
    
    const competitorInput = screen.getByPlaceholderText(/palavra-chave do concorrente/i);
    const addCompetitorButton = screen.getByRole('button', { name: /continuar/i }).previousElementSibling?.nextElementSibling;
    
    await user.type(competitorInput, 'palavra concorrente');
    await user.keyboard('{Enter}');
    
    expect(screen.getByText(/palavra concorrente/i)).toBeInTheDocument();
  });

  test('deve habilitar botão quando pelo menos uma palavra-chave é adicionada', async () => {
    const user = userEvent.setup();
    const onNext = jest.fn();
    renderKeywordsStep({ ...createStepProps(), onNext });
    
    const keywordInput = screen.getByPlaceholderText(/digite uma palavra-chave/i);
    const addButton = screen.getByRole('button', { name: /continuar/i }).previousElementSibling;
    
    await user.type(keywordInput, 'palavra-chave teste');
    await user.click(addButton!);
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    expect(continueButton).toBeEnabled();
    
    await user.click(continueButton);
    expect(onNext).toHaveBeenCalled();
  });
});

describe('FinishStep Component', () => {
  const renderFinishStep = (props = createStepProps()) => {
    return render(<FinishStep {...props} />);
  };

  test('deve renderizar resumo dos dados', () => {
    renderFinishStep();
    
    expect(screen.getByText(/joão silva/i)).toBeInTheDocument();
    expect(screen.getByText(/joao@empresa.com/i)).toBeInTheDocument();
    expect(screen.getByText(/empresa teste ltda/i)).toBeInTheDocument();
    expect(screen.getByText(/tecnologia/i)).toBeInTheDocument();
  });

  test('deve mostrar objetivos selecionados', () => {
    renderFinishStep();
    
    expect(screen.getByText(/aumentar tráfego orgânico/i)).toBeInTheDocument();
    expect(screen.getByText(/melhorar posicionamento/i)).toBeInTheDocument();
  });

  test('deve mostrar palavras-chave selecionadas', () => {
    renderFinishStep();
    
    expect(screen.getByText(/software desenvolvimento/i)).toBeInTheDocument();
    expect(screen.getByText(/sistema gestão/i)).toBeInTheDocument();
  });

  test('deve chamar onFinish ao clicar em começar otimização', async () => {
    const user = userEvent.setup();
    const onFinish = jest.fn();
    renderFinishStep({ ...createStepProps(), onFinish });
    
    const finishButton = screen.getByRole('button', { name: /começar otimização/i });
    await user.click(finishButton);
    
    await waitFor(() => {
      expect(onFinish).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  test('deve mostrar loading durante submissão', async () => {
    const user = userEvent.setup();
    const onFinish = jest.fn();
    renderFinishStep({ ...createStepProps(), onFinish });
    
    const finishButton = screen.getByRole('button', { name: /começar otimização/i });
    await user.click(finishButton);
    
    expect(screen.getByText(/finalizando/i)).toBeInTheDocument();
  });

  test('deve chamar onBack ao clicar em voltar', async () => {
    const user = userEvent.setup();
    const onBack = jest.fn();
    renderFinishStep({ ...createStepProps(), onBack });
    
    const backButton = screen.getByRole('button', { name: /voltar/i });
    await user.click(backButton);
    
    expect(onBack).toHaveBeenCalled();
  });

  test('deve mostrar informações de contato', () => {
    renderFinishStep();
    
    expect(screen.getByText(/você receberá um e-mail de confirmação/i)).toBeInTheDocument();
    expect(screen.getByText(/nossa equipe entrará em contato/i)).toBeInTheDocument();
  });
});

describe('Integração entre Componentes', () => {
  test('deve manter dados entre passos', async () => {
    const user = userEvent.setup();
    const updateData = jest.fn();
    const onNext = jest.fn();
    
    // Teste WelcomeStep
    const { rerender } = render(
      <WelcomeStep 
        {...createStepProps({ updateData, onNext })}
      />
    );
    
    const nameInput = screen.getByLabelText(/nome completo/i);
    const emailInput = screen.getByLabelText(/e-mail/i);
    
    await user.type(nameInput, 'João Silva');
    await user.type(emailInput, 'joao@empresa.com');
    
    const continueButton = screen.getByRole('button', { name: /continuar/i });
    await user.click(continueButton);
    
    expect(updateData).toHaveBeenCalledWith({
      user: {
        ...mockOnboardingData.user,
        name: 'João Silva',
        email: 'joao@empresa.com'
      }
    });
    
    // Teste CompanyStep com dados atualizados
    const updatedData = {
      ...mockOnboardingData,
      user: {
        ...mockOnboardingData.user,
        name: 'João Silva',
        email: 'joao@empresa.com'
      }
    };
    
    rerender(
      <CompanyStep 
        {...createStepProps({ data: updatedData, updateData, onNext })}
      />
    );
    
    expect(screen.getByDisplayValue(/joão silva/i)).toBeInTheDocument();
  });
});

describe('Validações de Acessibilidade', () => {
  test('deve ter labels apropriados', () => {
    render(<WelcomeStep {...createStepProps()} />);
    
    expect(screen.getByLabelText(/nome completo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument();
  });

  test('deve ter botões com texto descritivo', () => {
    render(<WelcomeStep {...createStepProps()} />);
    
    expect(screen.getByRole('button', { name: /continuar/i })).toBeInTheDocument();
  });

  test('deve mostrar mensagens de erro acessíveis', async () => {
    const user = userEvent.setup();
    render(<WelcomeStep {...createStepProps()} />);
    
    const emailInput = screen.getByLabelText(/e-mail/i);
    await user.type(emailInput, 'email-invalido');
    
    expect(screen.getByText(/e-mail deve ter um formato válido/i)).toBeInTheDocument();
  });
}); 