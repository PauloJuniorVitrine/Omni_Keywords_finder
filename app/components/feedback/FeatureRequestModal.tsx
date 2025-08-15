import React, { useState } from 'react';
import { FeatureRequestForm } from './FeatureRequestForm';

interface FeatureRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (featureRequest: any) => void;
}

export const FeatureRequestModal: React.FC<FeatureRequestModalProps> = ({
  isOpen,
  onClose,
  onSubmit
}) => {
  const [featureRequest, setFeatureRequest] = useState({
    title: '',
    description: '',
    useCase: '',
    priority: 'medium',
    category: 'general',
    email: ''
  });

  const handleSubmit = () => {
    const requestData = {
      ...featureRequest,
      timestamp: new Date().toISOString(),
      votes: 1 // Auto-vote do usuário que criou
    };
    
    onSubmit(requestData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="feature-request-modal-overlay">
      <div className="feature-request-modal">
        <div className="feature-request-modal-header">
          <h2>Sugerir Nova Funcionalidade</h2>
          <button onClick={onClose} className="close-button">
            ×
          </button>
        </div>
        
        <div className="feature-request-modal-content">
          <div className="feature-request-info">
            <p>
              Compartilhe sua ideia para melhorar o Omni Keywords Finder. 
              Suas sugestões nos ajudam a criar uma ferramenta ainda melhor!
            </p>
          </div>
          
          <FeatureRequestForm
            featureRequest={featureRequest}
            onFeatureRequestChange={setFeatureRequest}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
}; 