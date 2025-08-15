import React, { useEffect, useState } from 'react';
import Loader from '../../components/shared/Loader';
import ActionButton from '../../components/shared/ActionButton';
import Tooltip from '../../components/shared/Tooltip_v1';
import Skeleton from '../../components/shared/Skeleton_v1';

interface Notificacao {
  id: number;
  titulo: string;
  mensagem: string;
  tipo: 'info' | 'warning' | 'error';
  lida: boolean;
  usuario?: string;
  timestamp: string;
}

const tipoCor = {
  info: '#4f8cff',
  warning: '#eab308',
  error: '#ef4444',
};

const Notifications: React.FC = () => {
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [polling, setPolling] = useState(true);

  const fetchNotificacoes = () => {
    setLoading(true);
    setErro(null);
    fetch('/api/notificacoes?limit=10')
      .then(async (res) => {
        if (!res.ok) throw new Error('Erro ao buscar notificações');
        const data: Notificacao[] = await res.json();
        setNotificacoes(data);
      })
      .catch(() => setErro('Não foi possível carregar notificações.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchNotificacoes();
    if (polling) {
      const timer = setInterval(fetchNotificacoes, 10000);
      return () => clearInterval(timer);
    }
  }, [polling]);

  const marcarComoLida = (id: number) => {
    fetch(`/api/notificacoes/${id}`, { method: 'PATCH' })
      .then(() => {
        setNotificacoes((prev) => prev.map((n) => n.id === id ? { ...n, lida: true } : n));
      });
  };

  return (
    <section aria-labelledby="notificacoes-title" style={{ marginBottom: 32 }} data-testid="dashboard-notificacoes">
      <h2 id="notificacoes-title" style={{ fontSize: 22, marginBottom: 12 }} tabIndex={0}>Notificações</h2>
      <div style={{ marginBottom: 8 }}>
        <Tooltip content={polling ? 'Pausar atualização automática' : 'Ativar atualização automática'} position="top">
          <ActionButton label={polling ? 'Pausar Atualização' : 'Atualizar'} variant="secondary" onClick={() => setPolling((p) => !p)} />
        </Tooltip>
      </div>
      {erro && <div style={{ color: 'orange', marginBottom: 8 }}>{erro}</div>}
      {loading ? (
        <div style={{ marginBottom: 12 }}>
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} variant="block" height={48} style={{ marginBottom: 8 }} />
          ))}
        </div>
      ) : notificacoes.length === 0 ? (
        <div style={{ color: '#888', fontSize: 16 }}>Nenhuma notificação recente.</div>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {notificacoes.map((n) => (
            <li key={n.id} style={{
              background: n.lida ? '#f3f4f6' : '#fff',
              borderLeft: `6px solid ${tipoCor[n.tipo]}`,
              marginBottom: 12,
              padding: '12px 16px',
              borderRadius: 8,
              boxShadow: n.lida ? 'none' : '0 2px 8px rgba(0,0,0,0.04)',
              opacity: n.lida ? 0.7 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              animation: n.lida ? undefined : 'fadeIn 0.5s',
            }} aria-live={n.lida ? undefined : 'polite'} tabIndex={0}>
              <span style={{ fontWeight: 700, color: tipoCor[n.tipo], minWidth: 80 }}>{n.titulo}</span>
              <span style={{ flex: 1 }}>{n.mensagem}</span>
              <span style={{ fontSize: 12, color: '#888' }}>{new Date(n.timestamp).toLocaleString()}</span>
              {!n.lida && (
                <Tooltip content="Marcar notificação como lida" position="top">
                  <ActionButton label="Marcar como lida" variant="primary" onClick={() => marcarComoLida(n.id)} />
                </Tooltip>
              )}
            </li>
          ))}
        </ul>
      )}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </section>
  );
};

export default Notifications; 