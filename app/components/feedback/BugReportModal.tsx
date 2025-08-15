import React, { useState } from 'react';
import { BugReportForm } from './BugReportForm';

interface BugReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (bugReport: any) => void;
  error?: Error;
}

export const BugReportModal: React.FC<BugReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  error
}) => {
  const [bugReport, setBugReport] = useState({
    title: '',
    description: '',
    steps: '',
    expected: '',
    actual: '',
    severity: 'medium',
    browser: '',
    os: '',
    url: window.location.href
  });

  const handleSubmit = () => {
    const reportData = {
      ...bugReport,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : null,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    };
    
    onSubmit(reportData);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="bug-report-modal-overlay">
      <div className="bug-report-modal">
        <div className="bug-report-modal-header">
          <h2>Reportar Bug</h2>
          <button onClick={onClose} className="close-button">
            ×
          </button>
        </div>
        
        <div className="bug-report-modal-content">
          {error && (
            <div className="error-summary">
              <h3>Erro Detectado</h3>
              <p><strong>Mensagem:</strong> {error.message}</p>
              <p><strong>Tipo:</strong> {error.name}</p>
            </div>
          )}
          
          <BugReportForm
            bugReport={bugReport}
            onBugReportChange={setBugReport}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
}; 