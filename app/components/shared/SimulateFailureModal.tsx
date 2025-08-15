import React from 'react';

interface SimulateFailureModalProps {
  open: boolean;
  onClose: () => void;
  onSimulate: (tipo: 'timeout' | 'rejeicao' | 'autenticacao') => void;
}

const SimulateFailureModal: React.FC<SimulateFailureModalProps> = ({ open, onClose, onSimulate }) => {
  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Simulação de Falhas de Integração"
      tabIndex={-1}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.18)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: '#fff',
          borderRadius: 16,
          minWidth: 340,
          minHeight: 120,
          boxShadow: '0 4px 24px rgba(0,0,0,0.10)',
          padding: 32,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
        onClick={e => e.stopPropagation()}
      >
        <h2 style={{ fontSize: 20, color: '#222', marginBottom: 24 }}>Simular Falha de Integração</h2>
        <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          <button
            style={{ background: '#eab308', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => onSimulate('timeout')}
            aria-label="Simular Timeout"
          >
            Timeout
          </button>
          <button
            style={{ background: '#ef4444', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => onSimulate('rejeicao')}
            aria-label="Simular Rejeição"
          >
            Rejeição
          </button>
          <button
            style={{ background: '#4f8cff', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontWeight: 600, cursor: 'pointer' }}
            onClick={() => onSimulate('autenticacao')}
            aria-label="Simular Erro de Autenticação"
          >
            Erro de Autenticação
          </button>
        </div>
        <button
          style={{ background: 'transparent', color: '#222', border: 'none', fontSize: 18, cursor: 'pointer', marginTop: 8 }}
          onClick={onClose}
          aria-label="Fechar modal"
        >
          Fechar
        </button>
      </div>
    </div>
  );
};

export default SimulateFailureModal; 