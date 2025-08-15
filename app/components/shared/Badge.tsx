import React from 'react';
import { colors } from '../../../ui/theme';

/**
 * Badge de status para feedback visual.
 * @param label Texto do badge
 * @param color Cor de fundo do badge (hex ou nome)
 */
interface BadgeProps {
  label: string;
  color?: string;
}

const Badge: React.FC<BadgeProps> = ({ label, color = colors.secondary }) => (
  <span
    style={{
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: 8,
      background: color,
      color: colors.textLight,
      fontWeight: 700,
      fontSize: 14,
      letterSpacing: 0.5,
    }}
    aria-label={label}
  >
    {label}
  </span>
);

export default Badge; 