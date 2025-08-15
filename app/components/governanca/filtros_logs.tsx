import React from 'react';

interface FiltrosLogsProps {
  event: string;
  status: string;
  dataInicio: string;
  dataFim: string;
  onChange: (filtros: {
    event: string;
    status: string;
    dataInicio: string;
    dataFim: string;
  }) => void;
}

const FiltrosLogs: React.FC<FiltrosLogsProps> = ({ event, status, dataInicio, dataFim, onChange }) => {
  return (
    <div style={{ display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
      <div>
        <label htmlFor="filtro-evento">Evento:</label><br />
        <input
          id="filtro-evento"
          type="text"
          value={event}
          onChange={(e) => onChange({ event: e.target.value, status, dataInicio, dataFim })}
          placeholder="Ex: validacao_keywords"
          style={{ width: 180 }}
        />
      </div>
      <div>
        <label htmlFor="filtro-status">Status:</label><br />
        <select
          id="filtro-status"
          value={status}
          onChange={(e) => onChange({ event, status: e.target.value, dataInicio, dataFim })}
          style={{ width: 120 }}
        >
          <option value="">Todos</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
          <option value="audit">Audit</option>
        </select>
      </div>
      <div>
        <label htmlFor="filtro-data-inicio">Data início:</label><br />
        <input
          id="filtro-data-inicio"
          type="date"
          value={dataInicio}
          onChange={(e) => onChange({ event, status, dataInicio: e.target.value, dataFim })}
        />
      </div>
      <div>
        <label htmlFor="filtro-data-fim">Data fim:</label><br />
        <input
          id="filtro-data-fim"
          type="date"
          value={dataFim}
          onChange={(e) => onChange({ event, status, dataInicio, dataFim: e.target.value })}
        />
      </div>
    </div>
  );
};

export default FiltrosLogs; 