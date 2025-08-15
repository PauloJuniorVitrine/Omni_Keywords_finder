import React from 'react';
import Loader from './Loader';

interface ExportButtonProps {
  format: 'csv' | 'json';
  onExport: () => void;
  loading?: boolean;
  disabled?: boolean;
}

const ExportButton: React.FC<ExportButtonProps> = ({ format, onExport, loading = false, disabled = false }) => {
  const label = format === 'csv' ? 'Exportar CSV' : 'Exportar JSON';
  const icon = format === 'csv' ? '📄' : '🗒️';
  return (
    <button
      onClick={onExport}
      disabled={disabled || loading}
      aria-label={label}
      title={label}
      style={{
        background: '#4f8cff',
        color: '#fff',
        border: 'none',
        borderRadius: 8,
        padding: '10px 24px',
        fontWeight: 600,
        fontSize: 16,
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        opacity: disabled || loading ? 0.6 : 1,
        margin: 4,
        display: 'flex',
        alignItems: 'center',
        gap: 8,
      }}
      tabIndex={0}
    >
      {loading ? <Loader size="small" color="#fff" /> : icon}
      <span>{label}</span>
    </button>
  );
};

export default ExportButton; 