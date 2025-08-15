import React from 'react';

/**
 * Painel de histórico de execuções/resultados.
 * @param items Lista de execuções/resultados
 * @param onSelect Callback ao selecionar item
 * @param selectedId ID do item selecionado
 * @param title Título do painel
 */
export interface HistoryItem {
  id: string;
  data: string; // ISO date
  status?: string;
  resumo?: string;
}

export interface HistoryPanelProps {
  items: HistoryItem[];
  onSelect: (id: string) => void;
  selectedId?: string;
  title?: string;
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({ items, onSelect, selectedId, title = 'Histórico de Execuções' }) => {
  return (
    <aside aria-label={title} style={{ width: 320, maxWidth: '100%', background: '#f9fafb', borderRight: '1px solid #eee', padding: 16, height: '100%', overflowY: 'auto' }}>
      <h4 style={{ marginBottom: 16, fontSize: 18 }}>{title}</h4>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {items.length === 0 && <li style={{ color: '#888', fontStyle: 'italic' }}>Nenhuma execução encontrada.</li>}
        {items.map(item => (
          <li key={item.id} style={{ marginBottom: 10 }}>
            <button
              onClick={() => onSelect(item.id)}
              style={{
                width: '100%',
                textAlign: 'left',
                background: item.id === selectedId ? '#e0e7ef' : 'none',
                border: 'none',
                borderRadius: 6,
                padding: '10px 14px',
                fontWeight: item.id === selectedId ? 700 : 400,
                color: '#222',
                cursor: 'pointer',
                outline: 'none',
                transition: 'background 0.15s',
              }}
              aria-current={item.id === selectedId}
              aria-label={`Execução de ${new Date(item.data).toLocaleString()}${item.status ? ' - ' + item.status : ''}`}
            >
              <div style={{ fontSize: 15 }}>{new Date(item.data).toLocaleString()}</div>
              {item.status && <span style={{ fontSize: 13, color: '#888' }}>{item.status}</span>}
              {item.resumo && <div style={{ fontSize: 13, color: '#555', marginTop: 2 }}>{item.resumo}</div>}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default HistoryPanel; 