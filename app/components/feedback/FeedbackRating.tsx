import React from 'react';

interface FeedbackRatingProps {
  rating: number;
  onRatingChange: (rating: number) => void;
}

export const FeedbackRating: React.FC<FeedbackRatingProps> = ({
  rating,
  onRatingChange
}) => {
  const stars = [1, 2, 3, 4, 5];

  const getStarIcon = (starNumber: number) => {
    if (rating >= starNumber) {
      return '★'; // Filled star
    }
    return '☆'; // Empty star
  };

  const getRatingText = (rating: number) => {
    switch (rating) {
      case 1: return 'Muito Ruim';
      case 2: return 'Ruim';
      case 3: return 'Regular';
      case 4: return 'Bom';
      case 5: return 'Excelente';
      default: return 'Avalie sua experiência';
    }
  };

  return (
    <div className="feedback-rating">
      <h3>Como você avalia sua experiência?</h3>
      
      <div className="stars-container">
        {stars.map((star) => (
          <button
            key={star}
            onClick={() => onRatingChange(star)}
            className={`star-button ${rating >= star ? 'filled' : 'empty'}`}
            aria-label={`Avaliar com ${star} estrela${star > 1 ? 's' : ''}`}
          >
            {getStarIcon(star)}
          </button>
        ))}
      </div>
      
      <p className="rating-text">{getRatingText(rating)}</p>
    </div>
  );
}; 