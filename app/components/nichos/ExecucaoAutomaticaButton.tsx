import React from 'react';
import Loader from '../shared/Loader';

interface ExecucaoAutomaticaButtonProps {
  disabled?: boolean;
  onClick: () => void;
  loading?: boolean;
}

const ExecucaoAutomaticaButton: React.FC<ExecucaoAutomaticaButtonProps> = ({ disabled, onClick, loading }) => (
  <button type="button" onClick={onClick} disabled={disabled || loading} style={{ padding: '12px 32px', fontWeight: 700, fontSize: 16, background: '#4f8cff', color: '#fff', border: 'none', borderRadius: 8, cursor: disabled ? 'not-allowed' : 'pointer', margin: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
    {loading ? <><Loader size="small" color="#fff" /><span style={{ fontSize: 16 }}>Executando...</span></> : 'Iniciar Busca Automática'}
  </button>
);

export default ExecucaoAutomaticaButton; 