import React from 'react';

interface BugReportFormProps {
  bugReport: {
    title: string;
    description: string;
    steps: string;
    expected: string;
    actual: string;
    severity: string;
    browser: string;
    os: string;
    url: string;
  };
  onBugReportChange: (bugReport: any) => void;
  onSubmit: () => void;
}

export const BugReportForm: React.FC<BugReportFormProps> = ({
  bugReport,
  onBugReportChange,
  onSubmit
}) => {
  const handleChange = (field: string, value: string) => {
    onBugReportChange({
      ...bugReport,
      [field]: value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="bug-report-form">
      <div className="form-group">
        <label htmlFor="title">Título do Bug *</label>
        <input
          type="text"
          id="title"
          value={bugReport.title}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="Descreva brevemente o problema"
          className="form-input"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Descrição Detalhada *</label>
        <textarea
          id="description"
          value={bugReport.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Descreva o problema em detalhes"
          className="form-textarea"
          rows={4}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="steps">Passos para Reproduzir *</label>
        <textarea
          id="steps"
          value={bugReport.steps}
          onChange={(e) => handleChange('steps', e.target.value)}
          placeholder="1. Acesse...&#10;2. Clique em...&#10;3. Observe que..."
          className="form-textarea"
          rows={3}
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="expected">Comportamento Esperado</label>
          <textarea
            id="expected"
            value={bugReport.expected}
            onChange={(e) => handleChange('expected', e.target.value)}
            placeholder="O que deveria acontecer"
            className="form-textarea"
            rows={2}
          />
        </div>

        <div className="form-group">
          <label htmlFor="actual">Comportamento Atual</label>
          <textarea
            id="actual"
            value={bugReport.actual}
            onChange={(e) => handleChange('actual', e.target.value)}
            placeholder="O que está acontecendo"
            className="form-textarea"
            rows={2}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="severity">Severidade</label>
          <select
            id="severity"
            value={bugReport.severity}
            onChange={(e) => handleChange('severity', e.target.value)}
            className="form-select"
          >
            <option value="low">Baixa</option>
            <option value="medium">Média</option>
            <option value="high">Alta</option>
            <option value="critical">Crítica</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="browser">Navegador</label>
          <input
            type="text"
            id="browser"
            value={bugReport.browser}
            onChange={(e) => handleChange('browser', e.target.value)}
            placeholder="Chrome, Firefox, Safari..."
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="os">Sistema Operacional</label>
          <input
            type="text"
            id="os"
            value={bugReport.os}
            onChange={(e) => handleChange('os', e.target.value)}
            placeholder="Windows, macOS, Linux..."
            className="form-input"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="url">URL da Página</label>
        <input
          type="url"
          id="url"
          value={bugReport.url}
          onChange={(e) => handleChange('url', e.target.value)}
          className="form-input"
        />
      </div>

      <button type="submit" className="submit-button">
        Enviar Report de Bug
      </button>
    </form>
  );
}; 