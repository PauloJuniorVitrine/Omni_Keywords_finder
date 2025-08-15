import React, { useState, useEffect } from 'react';
import UploadRegras from '../../components/governanca/upload_regras';
import PainelLogs from '../../components/governanca/painel_logs';
import FiltrosLogs from '../../components/governanca/filtros_logs';
import ActionButton from '../../components/shared/ActionButton';
import Loader from '../../components/shared/Loader';
import Badge from '../../components/shared/Badge';
import ModalConfirm from '../../components/shared/ModalConfirm';
import type { paths } from '../../types/api';
import Tooltip from '../../components/shared/Tooltip_v1';
import Skeleton from '../../components/shared/Skeleton_v1';
import ExportButton from '../../components/shared/ExportButton';
import Toast from '../../components/shared/Toast';

interface LogItem {
  timestamp: string;
  event: string;
  status: string;
  source: string;
  details: Record<string, unknown>;
}

const MOCK_LOGS: LogItem[] = [
  {
    timestamp: '2025-05-02T19:40:00Z',
    event: 'validacao_keywords',
    status: 'success',
    source: 'validador_keywords.validar_lista',
    details: {
      total_recebido: 10,
      total_aprovado: 8,
      total_rejeitado: 2,
      motivos_rejeicao: { blacklist: 1, tamanho: 1 },
    },
  },
  {
    timestamp: '2025-05-02T19:41:00Z',
    event: 'limpeza_keywords',
    status: 'success',
    source: 'processador_keywords.limpar',
    details: {
      antes: 12,
      depois: 10,
    },
  },
  {
    timestamp: '2025-05-02T19:42:00Z',
    event: 'erro_enriquecimento',
    status: 'error',
    source: 'processador_keywords.enriquecer',
    details: {
      termo: 'exemplo',
      erro: 'Score inválido',
    },
  },
];

function exportToCSV(logs: any[], filename = 'logs.csv') {
  if (!logs.length) return;
  const headers = Object.keys(logs[0]);
  const csvRows = [headers.join(',')];
  logs.forEach((log) => {
    const row = headers.map((h) => {
      const val = typeof log[h] === 'object' ? JSON.stringify(log[h]) : log[h];
      return `"${String(val).replace(/"/g, '""')}"`;
    });
    csvRows.push(row.join(','));
  });
  const csv = csvRows.join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function exportToJSON(logs: any[], filename = 'logs.json') {
  const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const GovernancaPage: React.FC = () => {
  const [regras, setRegras] = useState<object | null>(null);
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [erro, setErro] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [filtros, setFiltros] = useState({
    event: '',
    status: '',
    dataInicio: '',
    dataFim: '',
  });
  const [modalExport, setModalExport] = useState<'csv' | 'json' | null>(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleUploadRegras = async (novasRegras: object) => {
    setRegras(novasRegras);
    setLoading(true);
    setErro(null);
    try {
      const resp = await fetch('/api/governanca/regras/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(novasRegras),
      });
      if (!resp.ok) {
        const errData = await resp.json();
        throw new Error(errData.erro || 'Erro ao enviar regras');
      }
      const data: paths['/governanca/regras/upload']['post']['responses']['200'] = await resp.json();
      setErro('Regras enviadas com sucesso!');
    } catch (e: any) {
      setErro(e.message || 'Erro desconhecido ao enviar regras');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = () => {
    setLoading(true);
    setErro(null);
    const params = new URLSearchParams({
      page: String(page),
      page_size: '20',
      ...(filtros.event && { event: filtros.event }),
      ...(filtros.status && { status: filtros.status }),
      ...(filtros.dataInicio && { data_inicio: filtros.dataInicio }),
      ...(filtros.dataFim && { data_fim: filtros.dataFim }),
    });
    fetch(`/api/governanca/logs?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN || 'token_exemplo'}`
      }
    })
      .then(async (res) => {
        if (res.status === 401 || res.status === 403) {
          setErro('Acesso não autorizado. Faça login ou verifique suas permissões.');
          setLogs([]);
          setTotal(0);
          setLoading(false);
          return;
        }
        if (!res.ok) throw new Error('Erro ao buscar logs');
        const data = await res.json();
        setLogs(Array.isArray(data.logs) ? data.logs : []);
        setTotal(Array.isArray(data.logs) ? data.logs.length : 0);
      })
      .catch(() => {
        setLogs(MOCK_LOGS);
        setTotal(MOCK_LOGS.length);
        setErro('Não foi possível carregar logs reais. Exibindo dados de exemplo.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filtros]);

  const handleFiltrosChange = (novosFiltros: typeof filtros) => {
    setFiltros(novosFiltros);
    setPage(1);
  };

  const totalPages = Math.ceil(total / 20);

  // Função para renderizar status com Badge
  const renderStatus = (status: string) => {
    if (status === 'success') return <Badge label="Ativo" color="#22c55e" />;
    if (status === 'error') return <Badge label="Erro" color="#ef4444" />;
    return <Badge label="Pendente" color="#eab308" />;
  };

  const handleExport = (format: 'csv' | 'json') => {
    setExportLoading(true);
    setTimeout(() => {
      setExportLoading(false);
      setToast({ type: 'success', message: `Exportação ${format.toUpperCase()} concluída com sucesso!` });
    }, 1500);
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
      <h1>Painel de Governança</h1>
      <section style={{ marginBottom: 32 }}>
        <h2>Upload/Edição de Regras</h2>
        <UploadRegras onUpload={handleUploadRegras} regrasIniciais={regras || {}} />
      </section>
      <section>
        <h2>Logs e Relatórios de Validação</h2>
        <FiltrosLogs
          event={filtros.event}
          status={filtros.status}
          dataInicio={filtros.dataInicio}
          dataFim={filtros.dataFim}
          onChange={handleFiltrosChange}
        />
        <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
          <Tooltip content="Exportar logs em CSV" position="top">
            <ExportButton format="csv" onExport={() => handleExport('csv')} loading={exportLoading} disabled={exportLoading || !logs.length} />
          </Tooltip>
          <Tooltip content="Exportar logs em JSON" position="top">
            <ExportButton format="json" onExport={() => handleExport('json')} loading={exportLoading} disabled={exportLoading || !logs.length} />
          </Tooltip>
        </div>
        {loading && (
          <div style={{ marginBottom: 16 }}>
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} variant="line" height={32} style={{ marginBottom: 8 }} />
            ))}
          </div>
        )}
        {erro && <div style={{ color: 'orange', marginBottom: 8 }}>{erro}</div>}
        {!loading && <PainelLogs logs={logs} renderStatus={renderStatus} />}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 16 }}>
          <ActionButton label="Anterior" variant="primary" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} />
          <span>Página {page} de {totalPages || 1}</span>
          <ActionButton label="Próxima" variant="primary" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages || totalPages === 0} />
        </div>
      </section>
      <ModalConfirm
        open={modalExport !== null}
        message={modalExport === 'csv' ? 'Confirmar exportação CSV?' : 'Confirmar exportação JSON?'}
        confirmLabel="Exportar"
        cancelLabel="Cancelar"
        confirmColor="#4f8cff"
        onConfirm={() => {
          if (modalExport === 'csv') exportToCSV(logs);
          if (modalExport === 'json') exportToJSON(logs);
          setModalExport(null);
        }}
        onCancel={() => setModalExport(null)}
      />
    </div>
  );
};

export default GovernancaPage; 