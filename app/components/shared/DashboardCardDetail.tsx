import React, { useEffect, useRef, useState } from 'react';

interface DashboardCardDetailProps {
  open: boolean;
  onClose: () => void;
  type: 'execucoes' | 'clusters' | 'tempo' | 'erros';
}

const mockData = {
  execucoes: { total: 1234, ultimas: ['Execução 1', 'Execução 2'] },
  clusters: { total: 98, ultimas: ['Cluster A', 'Cluster B'] },
  tempo: { media: 12.34, ultimas: [12.1, 13.2] },
  erros: { total: 5, ultimos: ['Timeout', 'Permissão negada'] },
};

const DashboardCardDetail: React.FC<DashboardCardDetailProps> = ({ open, onClose, type }) => {
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [dados, setDados] = useState<any>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      setLoading(true);
      setErro(null);
      setDados(null);
      ref.current?.focus();
      // Simula fetch
      setTimeout(() => {
        if (type === 'erros' && Math.random() < 0.2) {
          setErro('Erro ao carregar detalhes.');
        } else if (type === 'clusters' && Math.random() < 0.2) {
          setDados([]); // vazio
        } else {
          setDados(mockData[type]);
        }
        setLoading(false);
      }, 900);
    }
  }, [open, type]);

  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Detalhe do Card do Dashboard"
      tabIndex={-1}
      ref={ref}
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
        zIndex: 1200,
      }}
      onKeyDown={e => e.key === 'Escape' && onClose()}
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
        tabIndex={0}
      >
        <h2 style={{ fontSize: 20, color: '#222', marginBottom: 24 }}>Detalhe: {type}</h2>
        {loading && <div style={{ color: '#4f8cff', fontWeight: 600 }}>Carregando...</div>}
        {erro && <div style={{ color: '#ef4444', fontWeight: 600 }}>{erro}</div>}
        {!loading && !erro && (!dados || (Array.isArray(dados) && dados.length === 0)) && (
          <div style={{ color: '#888', fontWeight: 600 }}>Nenhum dado disponível.</div>
        )}
        {!loading && !erro && dados && (
          <pre style={{ textAlign: 'left', background: '#f3f4f6', borderRadius: 8, padding: 16, width: '100%', maxWidth: 400, marginTop: 12 }}>{JSON.stringify(dados, null, 2)}</pre>
        )}
        <button
          style={{ background: '#4f8cff', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', fontWeight: 600, fontSize: 16, marginTop: 24, cursor: 'pointer' }}
          onClick={onClose}
          aria-label="Fechar detalhe"
        >
          Fechar
        </button>
      </div>
    </div>
  );
};

export default DashboardCardDetail; 