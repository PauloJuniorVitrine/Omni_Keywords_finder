import React, { useEffect, useState } from 'react';
import DashboardCard from '../../components/shared/DashboardCard';
import Loader from '../../components/shared/Loader';
import ActionButton from '../../components/shared/ActionButton';
import Notifications from './Notifications';
import AgendarExecucao from './AgendarExecucao';
import Tooltip from '../../components/shared/Tooltip_v1';
import Skeleton from '../../components/shared/Skeleton_v1';
import ExportButton from '../../components/shared/ExportButton';
import SimulateFailureModal from '../../components/shared/SimulateFailureModal';
import Toast from '../../components/shared/Toast';
import DashboardCardDetail from '../../components/shared/DashboardCardDetail';
// import TendenciasList from './TendenciasList';

interface LogItem {
  id: number;
  tipo_operacao: string;
  entidade: string;
  id_referencia: number;
  usuario: string;
  timestamp: string;
  detalhes: string;
}

interface DashboardMetrics {
  total_execucoes: number;
  tempo_medio_execucao: number;
  total_clusters: number;
  total_erros: number;
  logs_recentes: LogItem[];
}

const responsiveContainer: React.CSSProperties = {
  maxWidth: 1200,
  margin: '0 auto',
  padding: 32,
};

const responsiveCards: React.CSSProperties = {
  display: 'flex',
  gap: 32,
  marginBottom: 32,
  flexWrap: 'wrap',
};

const responsiveSection: React.CSSProperties = {
  marginBottom: 32,
};

const responsiveActions: React.CSSProperties = {
  display: 'flex',
  gap: 16,
  flexWrap: 'wrap',
};

const mediaQuery = `
  @media (max-width: 800px) {
    .dashboard-cards { flex-direction: column !important; gap: 16px !important; }
    .dashboard-container { padding: 12px !important; }
    .dashboard-actions { flex-direction: column !important; gap: 8px !important; }
    .dashboard-title { font-size: 22px !important; }
    .dashboard-tendencias { font-size: 16px !important; }
  }
`;

const fadeInAnim = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

// Função de tradução simulada (i18n-ready)
const t = (str: string) => str;

// Simulação de role do usuário (poderia vir de contexto/autenticação)
const userRole = 'admin'; // ou 'user'

const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nichoId, setNichoId] = useState<string>('');
  const [categoriaId, setCategoriaId] = useState<string>('');
  const [dias, setDias] = useState<string>('7');
  const [exportLoading, setExportLoading] = useState(false);
  const [showSimModal, setShowSimModal] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [detailOpen, setDetailOpen] = useState<null | 'execucoes' | 'clusters' | 'tempo' | 'erros'>(null);

  // Polling automático
  useEffect(() => {
    let timer: NodeJS.Timeout;
    const fetchMetrics = () => {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (nichoId) params.append('nicho_id', nichoId);
      if (categoriaId) params.append('categoria_id', categoriaId);
      if (dias) params.append('dias', dias);
      fetch(`/api/dashboard/metrics?${params.toString()}`)
        .then(async (res) => {
          if (!res.ok) throw new Error('Erro ao buscar métricas do dashboard');
          const d: DashboardMetrics = await res.json();
          setData(d);
        })
        .catch(() => {
          setData(null);
          setError('Não foi possível carregar dados do dashboard.');
        })
        .finally(() => setLoading(false));
    };
    fetchMetrics();
    timer = setInterval(fetchMetrics, 15000); // Atualiza a cada 15s
    return () => clearInterval(timer);
  }, [nichoId, categoriaId, dias]);

  const handleExport = (format: 'csv' | 'json') => {
    setExportLoading(true);
    setTimeout(() => {
      setExportLoading(false);
      setToast({ type: 'success', message: `Exportação ${format.toUpperCase()} concluída com sucesso!` });
    }, 1500);
  };

  const handleSimulate = (tipo: 'timeout' | 'rejeicao' | 'autenticacao') => {
    setShowSimModal(false);
    if (tipo === 'timeout') setToast({ type: 'error', message: 'Timeout simulado: operação excedeu o tempo limite.' });
    if (tipo === 'rejeicao') setToast({ type: 'error', message: 'Rejeição simulada: permissão negada pelo servidor.' });
    if (tipo === 'autenticacao') setToast({ type: 'error', message: 'Erro de autenticação simulado: sessão expirada.' });
  };

  return (
    <div className="dashboard-container" style={responsiveContainer}>
      <style>{mediaQuery}</style>
      <style>{fadeInAnim}</style>
      <h1 className="dashboard-title" style={{ fontSize: 32, marginBottom: 32 }} tabIndex={0} aria-label="Título do dashboard" data-testid="dashboard-title">{t('Dashboard Omni Keywords Finder')}</h1>
      <Notifications />
      <AgendarExecucao />
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <input type="number" placeholder="Nicho ID" value={nichoId} onChange={e => setNichoId(e.target.value)} style={{ width: 100 }} />
        <input type="number" placeholder="Categoria ID" value={categoriaId} onChange={e => setCategoriaId(e.target.value)} style={{ width: 120 }} />
        <input type="number" placeholder="Dias" value={dias} onChange={e => setDias(e.target.value)} style={{ width: 80 }} />
      </div>
      {error && (
        <div role="alert" style={{ color: 'orange', marginBottom: 16, fontWeight: 600 }} data-testid="dashboard-error">
          {t(error)}
        </div>
      )}
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 180 }} data-testid="dashboard-loader">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} variant="block" height={120} style={{ margin: 8, minWidth: 200 }} />
          ))}
        </div>
      )}
      {!loading && !data && (
        <div style={{ color: '#888', fontSize: 18, marginTop: 32 }} role="status" aria-live="polite" data-testid="dashboard-empty">
          {t('Nenhum dado disponível para exibir no momento.')}
        </div>
      )}
      {!loading && data && (
        <>
          <div className="dashboard-cards" style={responsiveCards} role="region" aria-label={t('Cards de métricas do dashboard')} data-testid="dashboard-cards">
            <div
              tabIndex={0}
              role="button"
              aria-label="Detalhar Execuções"
              onClick={() => setDetailOpen('execucoes')}
              onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && setDetailOpen('execucoes')}
              style={{ animation: 'fadeIn 0.6s cubic-bezier(.4,0,.2,1)', cursor: 'pointer' }}
            >
              <Tooltip content="Total de execuções realizadas" position="top">
                <div><DashboardCard title={t('Execuções')} value={data.total_execucoes} status={t('Ativo')} /></div>
              </Tooltip>
            </div>
            <div
              tabIndex={0}
              role="button"
              aria-label="Detalhar Clusters"
              onClick={() => setDetailOpen('clusters')}
              onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && setDetailOpen('clusters')}
              style={{ animation: 'fadeIn 0.7s cubic-bezier(.4,0,.2,1)', cursor: 'pointer' }}
            >
              <Tooltip content="Total de clusters gerados" position="top">
                <div><DashboardCard title={t('Clusters')} value={data.total_clusters} status={t('Ativo')} badgeColor="#4f8cff" /></div>
              </Tooltip>
            </div>
            <div
              tabIndex={0}
              role="button"
              aria-label="Detalhar Tempo"
              onClick={() => setDetailOpen('tempo')}
              onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && setDetailOpen('tempo')}
              style={{ animation: 'fadeIn 0.8s cubic-bezier(.4,0,.2,1)', cursor: 'pointer' }}
            >
              <Tooltip content="Tempo médio de execução (s)" position="top">
                <div><DashboardCard title={t('Tempo médio (s)')} value={data.tempo_medio_execucao.toFixed(3)} status={t('Ativo')} badgeColor="#eab308" /></div>
              </Tooltip>
            </div>
            <div
              tabIndex={0}
              role="button"
              aria-label="Detalhar Erros"
              onClick={() => setDetailOpen('erros')}
              onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && setDetailOpen('erros')}
              style={{ animation: 'fadeIn 0.9s cubic-bezier(.4,0,.2,1)', cursor: 'pointer' }}
            >
              <Tooltip content="Total de erros registrados" position="top">
                <div><DashboardCard title={t('Erros')} value={data.total_erros} status={t('Erro')} badgeColor="#ef4444" /></div>
              </Tooltip>
            </div>
          </div>
          <section className="dashboard-logs" style={responsiveSection} aria-labelledby="logs-title" data-testid="dashboard-logs">
            <h2 id="logs-title" style={{ fontSize: 24 }} tabIndex={0}>{t('Logs Recentes')}</h2>
            {(!data.logs_recentes || data.logs_recentes.length === 0) ? (
              <div style={{ color: '#888', fontSize: 16 }} role="status" aria-live="polite">Nenhum log recente disponível.</div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 8 }}>
                <thead>
                  <tr style={{ background: '#f3f4f6' }}>
                    <th>ID</th>
                    <th>Tipo</th>
                    <th>Entidade</th>
                    <th>Ref</th>
                    <th>Usuário</th>
                    <th>Timestamp</th>
                    <th>Detalhes</th>
                  </tr>
                </thead>
                <tbody>
                  {data.logs_recentes.map((l) => (
                    <tr key={l.id} style={{ borderBottom: '1px solid #eee' }}>
                      <td>{l.id}</td>
                      <td>{l.tipo_operacao}</td>
                      <td>{l.entidade}</td>
                      <td>{l.id_referencia}</td>
                      <td>{l.usuario}</td>
                      <td>{l.timestamp ? new Date(l.timestamp).toLocaleString() : ''}</td>
                      <td>{l.detalhes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
          <div className="dashboard-actions" style={responsiveActions} role="region" aria-label={t('Ações do dashboard')} data-testid="dashboard-actions">
            {userRole === 'admin' && (
              <>
                <ExportButton format="csv" onExport={() => handleExport('csv')} loading={exportLoading} disabled={exportLoading} />
                <ExportButton format="json" onExport={() => handleExport('json')} loading={exportLoading} disabled={exportLoading} />
                <ActionButton label={t('Simular Falha')} variant="secondary" onClick={() => setShowSimModal(true)} data-testid="btn-simular-falha" />
              </>
            )}
            <ActionButton label={t('Ver Métricas Prometheus')} variant="primary" onClick={() => window.open('/metrics', '_blank')} data-testid="btn-metricas" />
          </div>
        </>
      )}
      <SimulateFailureModal open={showSimModal} onClose={() => setShowSimModal(false)} onSimulate={handleSimulate} />
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}
      <DashboardCardDetail open={!!detailOpen} onClose={() => setDetailOpen(null)} type={detailOpen || 'execucoes'} />
    </div>
  );
};

export default DashboardPage; 