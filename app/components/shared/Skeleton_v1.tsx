import React from 'react';

/**
 * Skeleton para carregamento visual.
 * @param variant Tipo de skeleton ('line' | 'block' | 'circle')
 * @param width Largura (px ou %)
 * @param height Altura (px)
 * @param style Estilo adicional
 * @param className Classe CSS opcional
 */
export interface SkeletonProps {
  variant?: 'line' | 'block' | 'circle';
  width?: number | string;
  height?: number;
  style?: React.CSSProperties;
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'line',
  width = '100%',
  height = 16,
  style = {},
  className = '',
}) => {
  let borderRadius: string | number = 4;
  if (variant === 'circle') borderRadius = '50%';
  if (variant === 'block') borderRadius = 8;

  return (
    <span
      className={className}
      aria-busy="true"
      aria-label="Carregando..."
      style={{
        display: 'inline-block',
        width,
        height,
        background: 'linear-gradient(90deg, #f3f3f3 25%, #e0e0e0 37%, #f3f3f3 63%)',
        backgroundSize: '400% 100%',
        borderRadius,
        animation: 'skeleton-shimmer 1.2s ease-in-out infinite',
        ...style,
      }}
    >
      <style>{`
        @keyframes skeleton-shimmer {
          0% { background-position: 100% 0; }
          100% { background-position: 0 0; }
        }
      `}</style>
    </span>
  );
};

export default Skeleton; 