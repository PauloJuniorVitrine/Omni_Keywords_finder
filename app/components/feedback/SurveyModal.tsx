import React, { useState, useEffect } from 'react';
import { SurveyForm } from './SurveyForm';

interface SurveyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (surveyData: any) => void;
  surveyType: 'onboarding' | 'periodic' | 'feature' | 'exit';
  triggerReason?: string;
}

export const SurveyModal: React.FC<SurveyModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  surveyType,
  triggerReason
}) => {
  const [surveyData, setSurveyData] = useState({
    overallSatisfaction: 0,
    easeOfUse: 0,
    featureCompleteness: 0,
    performance: 0,
    supportQuality: 0,
    likelihoodToRecommend: 0,
    comments: '',
    improvementSuggestions: '',
    email: ''
  });

  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
      setSurveyData({
        overallSatisfaction: 0,
        easeOfUse: 0,
        featureCompleteness: 0,
        performance: 0,
        supportQuality: 0,
        likelihoodToRecommend: 0,
        comments: '',
        improvementSuggestions: '',
        email: ''
      });
    }
  }, [isOpen]);

  const getSurveyTitle = () => {
    switch (surveyType) {
      case 'onboarding':
        return 'Como foi sua experiência inicial?';
      case 'periodic':
        return 'Pesquisa de Satisfação';
      case 'feature':
        return 'Avaliação de Funcionalidade';
      case 'exit':
        return 'Por que você está saindo?';
      default:
        return 'Pesquisa de Satisfação';
    }
  };

  const getSurveyDescription = () => {
    switch (surveyType) {
      case 'onboarding':
        return 'Ajude-nos a melhorar a experiência de novos usuários. Sua opinião é muito importante!';
      case 'periodic':
        return 'Estamos sempre buscando melhorar. Conte-nos como está sua experiência com o Omni Keywords Finder.';
      case 'feature':
        return `Como você avalia a funcionalidade: ${triggerReason}?`;
      case 'exit':
        return 'Antes de você sair, gostaríamos de entender como podemos melhorar. Sua opinião nos ajudará muito.';
      default:
        return 'Sua opinião é muito importante para nós.';
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const finalData = {
        ...surveyData,
        surveyType,
        triggerReason,
        timestamp: new Date().toISOString(),
        step: currentStep
      };
      
      await onSubmit(finalData);
      onClose();
    } catch (error) {
      console.error('Erro ao enviar pesquisa:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="survey-modal-overlay">
      <div className="survey-modal">
        <div className="survey-modal-header">
          <h2>{getSurveyTitle()}</h2>
          <button onClick={onClose} className="close-button" disabled={isSubmitting}>
            ×
          </button>
        </div>
        
        <div className="survey-modal-content">
          <div className="survey-info">
            <p>{getSurveyDescription()}</p>
            <div className="survey-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${((currentStep + 1) / 3) * 100}%` }}
                />
              </div>
              <span className="progress-text">
                {currentStep + 1} de 3
              </span>
            </div>
          </div>
          
          <SurveyForm
            surveyData={surveyData}
            onSurveyDataChange={setSurveyData}
            currentStep={currentStep}
            surveyType={surveyType}
          />
          
          <div className="survey-actions">
            {currentStep > 0 && (
              <button 
                onClick={handleBack} 
                className="back-button"
                disabled={isSubmitting}
              >
                Voltar
              </button>
            )}
            
            <button 
              onClick={handleNext} 
              className="next-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Enviando...' : currentStep === 2 ? 'Enviar' : 'Próximo'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 