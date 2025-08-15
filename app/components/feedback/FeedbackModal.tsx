import React, { useState } from 'react';
import { FeedbackForm } from './FeedbackForm';
import { FeedbackRating } from './FeedbackRating';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: any) => void;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  onSubmit
}) => {
  const [rating, setRating] = useState<number>(0);
  const [feedback, setFeedback] = useState<string>('');

  const handleSubmit = () => {
    onSubmit({
      rating,
      feedback,
      timestamp: new Date().toISOString()
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="feedback-modal-overlay">
      <div className="feedback-modal">
        <div className="feedback-modal-header">
          <h2>Envie seu Feedback</h2>
          <button onClick={onClose} className="close-button">
            ×
          </button>
        </div>
        
        <div className="feedback-modal-content">
          <FeedbackRating 
            rating={rating} 
            onRatingChange={setRating} 
          />
          
          <FeedbackForm
            feedback={feedback}
            onFeedbackChange={setFeedback}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
}; 