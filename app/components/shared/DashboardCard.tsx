import React from 'react';
import Badge from './Badge';

/**
 * Card informativo do dashboard com microanimações.
 * @param title Título do card
 * @param value Valor principal
 * @param status Status textual (ex: 'Ativo', 'Pendente')
 * @param badgeColor Cor do badge (opcional)
 */
interface DashboardCardProps {
  title: string;
  value: string | number;
  status?: string;
  badgeColor?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, value, status, badgeColor }) => (
  <div
    style={{
      borderRadius: 16,
      border: '1px solid #d1d5db',
      background: '#fff',
      padding: 24,
      minWidth: 200,
      minHeight: 120,
      boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative',
      transition: 'box-shadow 0.18s, transform 0.12s',
      outline: 'none',
      cursor: 'pointer',
    }}
    aria-label={`Card: ${title}`}
    tabIndex={0}
    onMouseOver={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(79,140,255,0.10)'}
    onMouseOut={e => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.03)'}
    onFocus={e => e.currentTarget.style.boxShadow = '0 0 0 3px #a5b4fc'}
    onBlur={e => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.03)'}
  >
    <div style={{ fontSize: 18, color: '#333', marginBottom: 8 }}>{title}</div>
    <div style={{ fontSize: 32, fontWeight: 700, color: '#222' }}>{value}</div>
    {status && (
      <div style={{ position: 'absolute', top: 16, right: 16 }}>
        <Badge label={status} color={badgeColor} />
      </div>
    )}
  </div>
);

export default DashboardCard; 