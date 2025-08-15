import React from 'react';

interface SatisfactionRatingProps {
  value: number;
  onChange: (value: number) => void;
  labels?: string[];
  maxRating?: number;
  size?: 'small' | 'medium' | 'large';
  showLabels?: boolean;
}

export const SatisfactionRating: React.FC<SatisfactionRatingProps> = ({
  value,
  onChange,
  labels = ['Muito Ruim', 'Ruim', 'Regular', 'Bom', 'Excelente'],
  maxRating = 5,
  size = 'medium',
  showLabels = true
}) => {
  const handleStarClick = (rating: number) => {
    onChange(rating);
  };

  const handleStarHover = (rating: number) => {
    // Implementar hover effect se necessário
  };

  const getStarSize = () => {
    switch (size) {
      case 'small':
        return 'w-4 h-4';
      case 'large':
        return 'w-8 h-8';
      default:
        return 'w-6 h-6';
    }
  };

  const getStarColor = (starIndex: number) => {
    if (starIndex < value) {
      return 'text-yellow-400 fill-current';
    }
    return 'text-gray-300 hover:text-yellow-300';
  };

  return (
    <div className="satisfaction-rating">
      <div className="stars-container">
        {Array.from({ length: maxRating }, (_, index) => (
          <button
            key={index}
            type="button"
            className={`star-button ${getStarSize()} ${getStarColor(index)} transition-colors duration-200`}
            onClick={() => handleStarClick(index + 1)}
            onMouseEnter={() => handleStarHover(index + 1)}
            aria-label={`Avaliar ${index + 1} de ${maxRating} estrelas`}
          >
            <svg
              viewBox="0 0 24 24"
              className="w-full h-full"
              fill="currentColor"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
          </button>
        ))}
      </div>
      
      {showLabels && value > 0 && (
        <div className="rating-label">
          <span className="text-sm text-gray-600">
            {labels[value - 1]}
          </span>
        </div>
      )}
      
      <div className="rating-value">
        <span className="text-xs text-gray-500">
          {value} de {maxRating}
        </span>
      </div>
    </div>
  );
};

interface NPSRatingProps {
  value: number;
  onChange: (value: number) => void;
  showLabels?: boolean;
}

export const NPSRating: React.FC<NPSRatingProps> = ({
  value,
  onChange,
  showLabels = true
}) => {
  const handleScoreClick = (score: number) => {
    onChange(score);
  };

  const getScoreColor = (score: number) => {
    if (score <= 6) return 'bg-red-500 hover:bg-red-600';
    if (score <= 8) return 'bg-yellow-500 hover:bg-yellow-600';
    return 'bg-green-500 hover:bg-green-600';
  };

  const getScoreLabel = (score: number) => {
    if (score <= 6) return 'Detrator';
    if (score <= 8) return 'Passivo';
    return 'Promotor';
  };

  return (
    <div className="nps-rating">
      <div className="nps-scores">
        {Array.from({ length: 11 }, (_, index) => (
          <button
            key={index}
            type="button"
            className={`nps-score ${getScoreColor(index)} ${
              value === index ? 'ring-2 ring-blue-500' : ''
            } text-white font-bold rounded-full w-10 h-10 transition-all duration-200`}
            onClick={() => handleScoreClick(index)}
            aria-label={`NPS Score ${index}`}
          >
            {index}
          </button>
        ))}
      </div>
      
      {showLabels && value >= 0 && (
        <div className="nps-label">
          <span className="text-sm font-medium">
            {getScoreLabel(value)} ({value}/10)
          </span>
        </div>
      )}
    </div>
  );
};

interface EmojiRatingProps {
  value: number;
  onChange: (value: number) => void;
  labels?: string[];
  emojis?: string[];
}

export const EmojiRating: React.FC<EmojiRatingProps> = ({
  value,
  onChange,
  labels = ['Muito Ruim', 'Ruim', 'Regular', 'Bom', 'Excelente'],
  emojis = ['😞', '😐', '😊', '😄', '🤩']
}) => {
  const handleEmojiClick = (rating: number) => {
    onChange(rating);
  };

  return (
    <div className="emoji-rating">
      <div className="emoji-container">
        {emojis.map((emoji, index) => (
          <button
            key={index}
            type="button"
            className={`emoji-button text-2xl p-2 rounded-lg transition-all duration-200 ${
              value === index + 1 
                ? 'bg-blue-100 scale-110' 
                : 'hover:bg-gray-100 hover:scale-105'
            }`}
            onClick={() => handleEmojiClick(index + 1)}
            aria-label={labels[index]}
          >
            {emoji}
          </button>
        ))}
      </div>
      
      {value > 0 && (
        <div className="emoji-label">
          <span className="text-sm text-gray-600">
            {labels[value - 1]}
          </span>
        </div>
      )}
    </div>
  );
}; 