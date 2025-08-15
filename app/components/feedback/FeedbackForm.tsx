import React, { useState } from 'react';

interface FeedbackFormProps {
  feedback: string;
  onFeedbackChange: (feedback: string) => void;
  onSubmit: () => void;
}

export const FeedbackForm: React.FC<FeedbackFormProps> = ({
  feedback,
  onFeedbackChange,
  onSubmit
}) => {
  const [category, setCategory] = useState<string>('general');
  const [email, setEmail] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="feedback-form">
      <div className="form-group">
        <label htmlFor="category">Categoria:</label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="form-select"
        >
          <option value="general">Geral</option>
          <option value="bug">Bug</option>
          <option value="feature">Sugestão de Feature</option>
          <option value="improvement">Melhoria</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="feedback">Seu Feedback:</label>
        <textarea
          id="feedback"
          value={feedback}
          onChange={(e) => onFeedbackChange(e.target.value)}
          placeholder="Conte-nos sua experiência..."
          className="form-textarea"
          rows={4}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email (opcional):</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="seu@email.com"
          className="form-input"
        />
      </div>

      <button type="submit" className="submit-button">
        Enviar Feedback
      </button>
    </form>
  );
}; 