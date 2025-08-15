import React from 'react';

interface FeatureRequestFormProps {
  featureRequest: {
    title: string;
    description: string;
    useCase: string;
    priority: string;
    category: string;
    email: string;
  };
  onFeatureRequestChange: (featureRequest: any) => void;
  onSubmit: () => void;
}

export const FeatureRequestForm: React.FC<FeatureRequestFormProps> = ({
  featureRequest,
  onFeatureRequestChange,
  onSubmit
}) => {
  const handleChange = (field: string, value: string) => {
    onFeatureRequestChange({
      ...featureRequest,
      [field]: value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="feature-request-form">
      <div className="form-group">
        <label htmlFor="title">Título da Funcionalidade *</label>
        <input
          type="text"
          id="title"
          value={featureRequest.title}
          onChange={(e) => handleChange('title', e.target.value)}
          placeholder="Ex: Integração com Google Analytics"
          className="form-input"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Descrição Detalhada *</label>
        <textarea
          id="description"
          value={featureRequest.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Descreva a funcionalidade que você gostaria de ver implementada..."
          className="form-textarea"
          rows={4}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="useCase">Caso de Uso</label>
        <textarea
          id="useCase"
          value={featureRequest.useCase}
          onChange={(e) => handleChange('useCase', e.target.value)}
          placeholder="Como você usaria essa funcionalidade? Que problema ela resolveria?"
          className="form-textarea"
          rows={3}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="category">Categoria</label>
          <select
            id="category"
            value={featureRequest.category}
            onChange={(e) => handleChange('category', e.target.value)}
            className="form-select"
          >
            <option value="general">Geral</option>
            <option value="analytics">Analytics</option>
            <option value="integration">Integração</option>
            <option value="ui_ux">Interface</option>
            <option value="api">API</option>
            <option value="export">Exportação</option>
            <option value="automation">Automação</option>
            <option value="reporting">Relatórios</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="priority">Prioridade</label>
          <select
            id="priority"
            value={featureRequest.priority}
            onChange={(e) => handleChange('priority', e.target.value)}
            className="form-select"
          >
            <option value="low">Baixa</option>
            <option value="medium">Média</option>
            <option value="high">Alta</option>
            <option value="critical">Crítica</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="email">Email (opcional)</label>
        <input
          type="email"
          id="email"
          value={featureRequest.email}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="seu@email.com"
          className="form-input"
        />
        <small>Para notificações sobre o status da sua sugestão</small>
      </div>

      <button type="submit" className="submit-button">
        Enviar Sugestão
      </button>
    </form>
  );
}; 