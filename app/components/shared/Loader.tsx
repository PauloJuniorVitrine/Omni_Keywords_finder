import React from 'react';

/**
 * Loader animado para feedback visual.
 * @param size Tamanho ('small' | 'large')
 * @param color Cor do loader
 */
interface LoaderProps {
  size?: 'small' | 'large';
  color?: string;
}

const Loader: React.FC<LoaderProps> = ({ size = 'small', color = '#4f8cff' }) => {
  const dim = size === 'large' ? 36 : 18;
  return (
    <span
      role="status"
      aria-label="Carregando"
      style={{
        display: 'inline-block',
        width: dim,
        height: dim,
        verticalAlign: 'middle',
      }}
    >
      <svg width={dim} height={dim} viewBox={`0 0 ${dim} ${dim}`}>
        <circle
          cx={dim / 2}
          cy={dim / 2}
          r={dim / 2 - 2}
          fill="none"
          stroke={color}
          strokeWidth={4}
          strokeDasharray={Math.PI * (dim - 4)}
          strokeDashoffset={Math.PI * (dim - 4) * 0.25}
          style={{
            opacity: 0.3,
            transformOrigin: 'center',
            animation: 'spin 1s linear infinite',
          } as React.CSSProperties}
        />
        <style>{`
          @keyframes spin {
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </svg>
    </span>
  );
};

export default Loader; 