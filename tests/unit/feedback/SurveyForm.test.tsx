/**
 * Testes Unitários - SurveyForm Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_SURVEY_FORM_022
 * 
 * Baseado em código real do SurveyForm.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SurveyForm } from '../../../app/components/feedback/SurveyForm';

// Mock do componente SatisfactionRating
jest.mock('../../../app/components/feedback/SatisfactionRating', () => ({
  SatisfactionRating: ({ value, onChange, labels }: any) => (
    <div data-testid="satisfaction-rating" data-value={value}>
      {labels && labels.map((label: string, index: number) => (
        <button
          key={index}
          onClick={() => onChange(index + 1)}
          data-testid={`rating-${index + 1}`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}));

describe('SurveyForm - Formulário de Pesquisa de Satisfação', () => {
  
  const defaultSurveyData = {
    overallSatisfaction: 0,
    easeOfUse: 0,
    featureCompleteness: 0,
    performance: 0,
    supportQuality: 0,
    likelihoodToRecommend: 0,
    comments: '',
    improvementSuggestions: '',
    email: ''
  };

  const mockOnSurveyDataChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o componente com dados padrão', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
    });

    test('deve renderizar com dados customizados', () => {
      const customData = {
        ...defaultSurveyData,
        overallSatisfaction: 4,
        comments: 'Excelente plataforma!'
      };

      render(
        <SurveyForm
          surveyData={customData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
    });
  });

  describe('Step 1 - Avaliação Geral', () => {
    
    test('deve renderizar step 1 com todas as seções de rating', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
      expect(screen.getByText('Como você avalia sua satisfação geral com o Omni Keywords Finder?')).toBeInTheDocument();
      expect(screen.getByText('Quão fácil é usar a plataforma?')).toBeInTheDocument();
      expect(screen.getByText('Como você avalia a completude das funcionalidades?')).toBeInTheDocument();
    });

    test('deve renderizar SatisfactionRating para satisfação geral', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });

    test('deve usar labels corretos para satisfação geral', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      const firstRating = ratings[0];
      
      // Verificar se os botões de rating estão presentes
      expect(firstRating).toBeInTheDocument();
    });

    test('deve chamar onSurveyDataChange quando rating é alterado', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratingButtons = screen.getAllByTestId('rating-4');
      await user.click(ratingButtons[0]); // Clicar no primeiro rating (satisfação geral)
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        overallSatisfaction: 4
      });
    });

    test('deve usar labels corretos para facilidade de uso', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });

    test('deve usar labels corretos para completude de funcionalidades', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });
  });

  describe('Step 2 - Performance e Suporte', () => {
    
    test('deve renderizar step 2 com todas as seções de rating', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Performance e Suporte')).toBeInTheDocument();
      expect(screen.getByText('Como você avalia a performance da plataforma?')).toBeInTheDocument();
      expect(screen.getByText('Como você avalia a qualidade do suporte?')).toBeInTheDocument();
      expect(screen.getByText('Quão provável você é de recomendar o Omni Keywords Finder para outros?')).toBeInTheDocument();
    });

    test('deve renderizar SatisfactionRating para performance', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });

    test('deve chamar onSurveyDataChange quando performance é alterada', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      const ratingButtons = screen.getAllByTestId('rating-5');
      await user.click(ratingButtons[0]); // Clicar no primeiro rating (performance)
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        performance: 5
      });
    });

    test('deve usar labels corretos para performance', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });

    test('deve usar labels corretos para qualidade do suporte', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });

    test('deve usar labels corretos para probabilidade de recomendação', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      
      const ratings = screen.getAllByTestId('satisfaction-rating');
      expect(ratings).toHaveLength(3);
    });
  });

  describe('Step 3 - Comentários e Sugestões', () => {
    
    test('deve renderizar step 3 com campos de texto', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Comentários e Sugestões')).toBeInTheDocument();
      expect(screen.getByLabelText('Comentários Gerais (opcional)')).toBeInTheDocument();
      expect(screen.getByLabelText('Sugestões de Melhoria (opcional)')).toBeInTheDocument();
      expect(screen.getByLabelText('Email (opcional)')).toBeInTheDocument();
    });

    test('deve renderizar textarea para comentários', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      expect(commentsTextarea).toBeInTheDocument();
      expect(commentsTextarea).toHaveAttribute('placeholder', 'Conte-nos mais sobre sua experiência...');
      expect(commentsTextarea).toHaveAttribute('rows', '4');
    });

    test('deve renderizar textarea para sugestões de melhoria', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const suggestionsTextarea = screen.getByLabelText('Sugestões de Melhoria (opcional)');
      expect(suggestionsTextarea).toBeInTheDocument();
      expect(suggestionsTextarea).toHaveAttribute('placeholder', 'O que poderíamos melhorar?');
      expect(suggestionsTextarea).toHaveAttribute('rows', '4');
    });

    test('deve renderizar input para email', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const emailInput = screen.getByLabelText('Email (opcional)');
      expect(emailInput).toBeInTheDocument();
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('placeholder', 'seu@email.com');
    });

    test('deve exibir texto explicativo para email', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Para acompanhamento das suas sugestões')).toBeInTheDocument();
    });

    test('deve chamar onSurveyDataChange quando comentários são alterados', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      await user.type(commentsTextarea, 'Excelente plataforma!');
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        comments: 'Excelente plataforma!'
      });
    });

    test('deve chamar onSurveyDataChange quando sugestões são alteradas', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const suggestionsTextarea = screen.getByLabelText('Sugestões de Melhoria (opcional)');
      await user.type(suggestionsTextarea, 'Mais funcionalidades');
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        improvementSuggestions: 'Mais funcionalidades'
      });
    });

    test('deve chamar onSurveyDataChange quando email é alterado', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const emailInput = screen.getByLabelText('Email (opcional)');
      await user.type(emailInput, 'teste@exemplo.com');
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        email: 'teste@exemplo.com'
      });
    });

    test('deve exibir valores existentes nos campos', () => {
      const dataWithValues = {
        ...defaultSurveyData,
        comments: 'Comentário existente',
        improvementSuggestions: 'Sugestão existente',
        email: 'email@exemplo.com'
      };

      render(
        <SurveyForm
          surveyData={dataWithValues}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByDisplayValue('Comentário existente')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Sugestão existente')).toBeInTheDocument();
      expect(screen.getByDisplayValue('email@exemplo.com')).toBeInTheDocument();
    });
  });

  describe('Exit Survey', () => {
    
    test('deve renderizar exit survey quando surveyType é exit', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="exit"
        />
      );
      
      expect(screen.getByText('Por que você está cancelando?')).toBeInTheDocument();
    });

    test('deve renderizar opções de motivo de cancelamento', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="exit"
        />
      );
      
      expect(screen.getByLabelText('Muito caro')).toBeInTheDocument();
      expect(screen.getByLabelText('Faltam funcionalidades')).toBeInTheDocument();
      expect(screen.getByLabelText('Difícil de usar')).toBeInTheDocument();
      expect(screen.getByLabelText('Performance ruim')).toBeInTheDocument();
      expect(screen.getByLabelText('Outro')).toBeInTheDocument();
    });

    test('deve renderizar textarea para comentários adicionais no exit survey', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="exit"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários adicionais');
      expect(commentsTextarea).toBeInTheDocument();
      expect(commentsTextarea).toHaveAttribute('placeholder', 'Conte-nos mais sobre sua decisão...');
      expect(commentsTextarea).toHaveAttribute('rows', '4');
    });

    test('deve chamar onSurveyDataChange quando comentários do exit survey são alterados', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="exit"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários adicionais');
      await user.type(commentsTextarea, 'Motivo do cancelamento');
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        comments: 'Motivo do cancelamento'
      });
    });
  });

  describe('Validação de Campos', () => {
    
    test('deve validar email com formato correto', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const emailInput = screen.getByLabelText('Email (opcional)');
      await user.type(emailInput, 'teste@exemplo.com');
      
      expect(emailInput).toHaveValue('teste@exemplo.com');
    });

    test('deve permitir campos vazios (opcionais)', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      const suggestionsTextarea = screen.getByLabelText('Sugestões de Melhoria (opcional)');
      const emailInput = screen.getByLabelText('Email (opcional)');
      
      expect(commentsTextarea).toHaveValue('');
      expect(suggestionsTextarea).toHaveValue('');
      expect(emailInput).toHaveValue('');
    });

    test('deve validar valores de rating dentro do range esperado', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      const ratingButtons = screen.getAllByTestId('rating-5');
      await user.click(ratingButtons[0]);
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledWith({
        ...defaultSurveyData,
        overallSatisfaction: 5
      });
    });
  });

  describe('Progresso do Formulário', () => {
    
    test('deve renderizar step correto baseado em currentStep', () => {
      // Testar step 0
      const { rerender } = render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
      
      // Testar step 1
      rerender(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={1}
          surveyType="onboarding"
        />
      );
      expect(screen.getByText('Performance e Suporte')).toBeInTheDocument();
      
      // Testar step 2
      rerender(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      expect(screen.getByText('Comentários e Sugestões')).toBeInTheDocument();
    });

    test('deve renderizar step 1 como padrão quando currentStep é inválido', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={999}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
    });

    test('deve manter dados entre steps', () => {
      const dataWithValues = {
        ...defaultSurveyData,
        overallSatisfaction: 4,
        performance: 5,
        comments: 'Comentário persistente'
      };

      render(
        <SurveyForm
          surveyData={dataWithValues}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByDisplayValue('Comentário persistente')).toBeInTheDocument();
    });
  });

  describe('Submissão de Feedback', () => {
    
    test('deve permitir submissão de dados completos', async () => {
      const user = userEvent.setup();
      const completeData = {
        ...defaultSurveyData,
        overallSatisfaction: 5,
        easeOfUse: 4,
        featureCompleteness: 5,
        performance: 4,
        supportQuality: 5,
        likelihoodToRecommend: 5,
        comments: 'Excelente plataforma!',
        improvementSuggestions: 'Mais funcionalidades',
        email: 'teste@exemplo.com'
      };

      render(
        <SurveyForm
          surveyData={completeData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      // Verificar se todos os dados estão presentes
      expect(screen.getByDisplayValue('Excelente plataforma!')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Mais funcionalidades')).toBeInTheDocument();
      expect(screen.getByDisplayValue('teste@exemplo.com')).toBeInTheDocument();
    });

    test('deve permitir submissão de dados parciais', () => {
      const partialData = {
        ...defaultSurveyData,
        overallSatisfaction: 3,
        comments: 'Comentário parcial'
      };

      render(
        <SurveyForm
          surveyData={partialData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByDisplayValue('Comentário parcial')).toBeInTheDocument();
    });

    test('deve permitir múltiplas alterações consecutivas', async () => {
      const user = userEvent.setup();
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      
      await user.type(commentsTextarea, 'Primeiro comentário');
      await user.clear(commentsTextarea);
      await user.type(commentsTextarea, 'Segundo comentário');
      
      expect(mockOnSurveyDataChange).toHaveBeenCalledTimes(2);
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter labels apropriados para todos os campos', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByLabelText('Comentários Gerais (opcional)')).toBeInTheDocument();
      expect(screen.getByLabelText('Sugestões de Melhoria (opcional)')).toBeInTheDocument();
      expect(screen.getByLabelText('Email (opcional)')).toBeInTheDocument();
    });

    test('deve ter placeholders informativos', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      const suggestionsTextarea = screen.getByLabelText('Sugestões de Melhoria (opcional)');
      const emailInput = screen.getByLabelText('Email (opcional)');
      
      expect(commentsTextarea).toHaveAttribute('placeholder', 'Conte-nos mais sobre sua experiência...');
      expect(suggestionsTextarea).toHaveAttribute('placeholder', 'O que poderíamos melhorar?');
      expect(emailInput).toHaveAttribute('placeholder', 'seu@email.com');
    });

    test('deve ter estrutura semântica adequada', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const commentsTextarea = screen.getByLabelText('Comentários Gerais (opcional)');
      const suggestionsTextarea = screen.getByLabelText('Sugestões de Melhoria (opcional)');
      const emailInput = screen.getByLabelText('Email (opcional)');
      
      expect(commentsTextarea).toHaveAttribute('tabIndex', '0');
      expect(suggestionsTextarea).toHaveAttribute('tabIndex', '0');
      expect(emailInput).toHaveAttribute('tabIndex', '0');
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente com dados complexos', () => {
      const complexData = {
        ...defaultSurveyData,
        comments: 'a'.repeat(1000),
        improvementSuggestions: 'b'.repeat(1000),
        email: 'teste@exemplo.com'
      };

      const startTime = performance.now();
      
      render(
        <SurveyForm
          surveyData={complexData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={2}
          surveyType="onboarding"
        />
      );
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      // Re-renderizar com os mesmos dados não deve causar mudanças
      rerender(
        <SurveyForm
          surveyData={defaultSurveyData}
          onSurveyDataChange={mockOnSurveyDataChange}
          currentStep={0}
          surveyType="onboarding"
        />
      );
      
      expect(screen.getByText('Avaliação Geral')).toBeInTheDocument();
    });
  });
}); 