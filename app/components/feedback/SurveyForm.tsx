import React from 'react';
import { SatisfactionRating } from './SatisfactionRating';

interface SurveyFormProps {
  surveyData: {
    overallSatisfaction: number;
    easeOfUse: number;
    featureCompleteness: number;
    performance: number;
    supportQuality: number;
    likelihoodToRecommend: number;
    comments: string;
    improvementSuggestions: string;
    email: string;
  };
  onSurveyDataChange: (data: any) => void;
  currentStep: number;
  surveyType: 'onboarding' | 'periodic' | 'feature' | 'exit';
}

export const SurveyForm: React.FC<SurveyFormProps> = ({
  surveyData,
  onSurveyDataChange,
  currentStep,
  surveyType
}) => {
  const handleRatingChange = (field: string, value: number) => {
    onSurveyDataChange({
      ...surveyData,
      [field]: value
    });
  };

  const handleTextChange = (field: string, value: string) => {
    onSurveyDataChange({
      ...surveyData,
      [field]: value
    });
  };

  const renderStep1 = () => (
    <div className="survey-step">
      <h3>Avaliação Geral</h3>
      
      <div className="rating-section">
        <label>Como você avalia sua satisfação geral com o Omni Keywords Finder?</label>
        <SatisfactionRating
          value={surveyData.overallSatisfaction}
          onChange={(value) => handleRatingChange('overallSatisfaction', value)}
          labels={['Muito Insatisfeito', 'Insatisfeito', 'Neutro', 'Satisfeito', 'Muito Satisfeito']}
        />
      </div>

      <div className="rating-section">
        <label>Quão fácil é usar a plataforma?</label>
        <SatisfactionRating
          value={surveyData.easeOfUse}
          onChange={(value) => handleRatingChange('easeOfUse', value)}
          labels={['Muito Difícil', 'Difícil', 'Neutro', 'Fácil', 'Muito Fácil']}
        />
      </div>

      <div className="rating-section">
        <label>Como você avalia a completude das funcionalidades?</label>
        <SatisfactionRating
          value={surveyData.featureCompleteness}
          onChange={(value) => handleRatingChange('featureCompleteness', value)}
          labels={['Muito Limitado', 'Limitado', 'Aceitável', 'Bom', 'Excelente']}
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="survey-step">
      <h3>Performance e Suporte</h3>
      
      <div className="rating-section">
        <label>Como você avalia a performance da plataforma?</label>
        <SatisfactionRating
          value={surveyData.performance}
          onChange={(value) => handleRatingChange('performance', value)}
          labels={['Muito Lenta', 'Lenta', 'Aceitável', 'Rápida', 'Muito Rápida']}
        />
      </div>

      <div className="rating-section">
        <label>Como você avalia a qualidade do suporte?</label>
        <SatisfactionRating
          value={surveyData.supportQuality}
          onChange={(value) => handleRatingChange('supportQuality', value)}
          labels={['Muito Ruim', 'Ruim', 'Regular', 'Bom', 'Excelente']}
        />
      </div>

      <div className="rating-section">
        <label>Quão provável você é de recomendar o Omni Keywords Finder para outros?</label>
        <SatisfactionRating
          value={surveyData.likelihoodToRecommend}
          onChange={(value) => handleRatingChange('likelihoodToRecommend', value)}
          labels={['Definitivamente Não', 'Provavelmente Não', 'Talvez', 'Provavelmente Sim', 'Definitivamente Sim']}
        />
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="survey-step">
      <h3>Comentários e Sugestões</h3>
      
      <div className="form-group">
        <label htmlFor="comments">Comentários Gerais (opcional)</label>
        <textarea
          id="comments"
          value={surveyData.comments}
          onChange={(e) => handleTextChange('comments', e.target.value)}
          placeholder="Conte-nos mais sobre sua experiência..."
          className="form-textarea"
          rows={4}
        />
      </div>

      <div className="form-group">
        <label htmlFor="improvementSuggestions">Sugestões de Melhoria (opcional)</label>
        <textarea
          id="improvementSuggestions"
          value={surveyData.improvementSuggestions}
          onChange={(e) => handleTextChange('improvementSuggestions', e.target.value)}
          placeholder="O que poderíamos melhorar?"
          className="form-textarea"
          rows={4}
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email (opcional)</label>
        <input
          type="email"
          id="email"
          value={surveyData.email}
          onChange={(e) => handleTextChange('email', e.target.value)}
          placeholder="seu@email.com"
          className="form-input"
        />
        <small>Para acompanhamento das suas sugestões</small>
      </div>
    </div>
  );

  const renderExitSurvey = () => (
    <div className="survey-step">
      <h3>Por que você está cancelando?</h3>
      
      <div className="exit-reasons">
        <div className="reason-option">
          <input
            type="radio"
            id="too-expensive"
            name="exit-reason"
            value="too-expensive"
          />
          <label htmlFor="too-expensive">Muito caro</label>
        </div>
        
        <div className="reason-option">
          <input
            type="radio"
            id="missing-features"
            name="exit-reason"
            value="missing-features"
          />
          <label htmlFor="missing-features">Faltam funcionalidades</label>
        </div>
        
        <div className="reason-option">
          <input
            type="radio"
            id="difficult-to-use"
            name="exit-reason"
            value="difficult-to-use"
          />
          <label htmlFor="difficult-to-use">Difícil de usar</label>
        </div>
        
        <div className="reason-option">
          <input
            type="radio"
            id="poor-performance"
            name="exit-reason"
            value="poor-performance"
          />
          <label htmlFor="poor-performance">Performance ruim</label>
        </div>
        
        <div className="reason-option">
          <input
            type="radio"
            id="other"
            name="exit-reason"
            value="other"
          />
          <label htmlFor="other">Outro</label>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="exit-comments">Comentários adicionais</label>
        <textarea
          id="exit-comments"
          value={surveyData.comments}
          onChange={(e) => handleTextChange('comments', e.target.value)}
          placeholder="Conte-nos mais sobre sua decisão..."
          className="form-textarea"
          rows={4}
        />
      </div>
    </div>
  );

  if (surveyType === 'exit') {
    return renderExitSurvey();
  }

  switch (currentStep) {
    case 0:
      return renderStep1();
    case 1:
      return renderStep2();
    case 2:
      return renderStep3();
    default:
      return renderStep1();
  }
}; 