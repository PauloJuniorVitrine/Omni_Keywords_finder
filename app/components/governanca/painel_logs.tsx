import React, { useState } from 'react';
import PropTypes from 'prop-types';

interface LogItem {
  timestamp: string;
  event: string;
  status: string;
  source: string;
  details: Record<string, unknown>;
}

interface PainelLogsProps {
  logs: LogItem[];
  renderStatus?: (status: string) => React.ReactNode;
}

const PainelLogs: React.FC<PainelLogsProps> = ({ logs, renderStatus }) => {
  const [logSelecionado, setLogSelecionado] = useState<LogItem | null>(null);

  return (
    <div className="painel-logs">
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 16 }}>
        <thead>
          <tr style={{ background: '#f0f0f0' }}>
            <th style={{ padding: 8, border: '1px solid #ddd' }}>Data/Hora</th>
            <th style={{ padding: 8, border: '1px solid #ddd' }}>Evento</th>
            <th style={{ padding: 8, border: '1px solid #ddd' }}>Status</th>
            <th style={{ padding: 8, border: '1px solid #ddd' }}>Fonte</th>
            <th style={{ padding: 8, border: '1px solid #ddd' }}>Resumo</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 && (
            <tr>
              <td colSpan={5} style={{ textAlign: 'center', padding: 16 }}>
                Nenhum log disponível.
              </td>
            </tr>
          )}
          {logs.map((log, idx) => (
            <tr
              key={idx}
              style={{ cursor: 'pointer', background: logSelecionado === log ? '#e6f7ff' : undefined }}
              onClick={() => setLogSelecionado(log)}
            >
              <td style={{ padding: 8, border: '1px solid #ddd' }}>{log.timestamp}</td>
              <td style={{ padding: 8, border: '1px solid #ddd' }}>{log.event}</td>
              <td style={{ padding: 8, border: '1px solid #ddd' }}>{renderStatus ? renderStatus(log.status) : log.status}</td>
              <td style={{ padding: 8, border: '1px solid #ddd' }}>{log.source}</td>
              <td style={{ padding: 8, border: '1px solid #ddd' }}>
                {log.details && typeof log.details === 'object'
                  ? Object.keys(log.details).slice(0, 2).map((k) => `${k}: ${String(log.details[k])}`).join(', ')
                  : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {logSelecionado && (
        <div style={{ background: '#fafafa', border: '1px solid #ddd', borderRadius: 8, padding: 16, marginBottom: 16 }}>
          <h4>Detalhes do Log</h4>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {JSON.stringify(logSelecionado, null, 2)}
          </pre>
          <button type="button" onClick={() => setLogSelecionado(null)} style={{ marginTop: 8 }}>
            Fechar
          </button>
        </div>
      )}
    </div>
  );
};

PainelLogs.propTypes = {
  logs: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.string.isRequired,
      event: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      details: PropTypes.object.isRequired,
    })
  ).isRequired,
  renderStatus: PropTypes.func,
};

export default PainelLogs; 