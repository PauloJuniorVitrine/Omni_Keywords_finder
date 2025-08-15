import React, { useState } from 'react';
import ResultsChart from '../shared/ResultsChart_v1';
import HistoryPanel, { HistoryItem } from '../shared/HistoryPanel_v1';

interface PalavraResultado {
  termo: string;
  score: number;
  categoria: string;
  prompt: string;
  dataExecucao?: string;
}

interface ResultadosPainelProps {
  resultados: PalavraResultado[];
  nichoNome: string;
  onExport: (formato: 'csv' | 'json') => void;
}

// Utilitário para exportação CSV
function exportToCSV(data: PalavraResultado[], filename: string) {
  const header = Object.keys(data[0] || {}).join(',');
  const rows = data.map(r => Object.values(r).join(','));
  const csv = [header, ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Utilitário para exportação JSON
function exportToJSON(data: PalavraResultado[], filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Placeholder para exportação PDF (pode ser aprimorado com jsPDF)
function exportToPDF(data: PalavraResultado[], filename: string) {
  const win = window.open('', '_blank');
  if (win) {
    win.document.write('<pre>' + JSON.stringify(data, null, 2) + '</pre>');
    win.document.title = filename;
    win.print();
  }
}

const ResultadosPainel: React.FC<ResultadosPainelProps> = ({ resultados, nichoNome, onExport }) => {
  // Histórico simulado (usar dados reais na integração)
  const historico: HistoryItem[] = resultados.length > 0 ? [
    ...Array.from(new Set(resultados.map(r => r.dataExecucao || '2024-06-27T10:00:00Z'))).map((data, i) => ({
      id: String(i),
      data,
      status: 'Concluído',
      resumo: `Execução ${i + 1}`
    }))
  ] : [];
  const [selectedExecId, setSelectedExecId] = useState<string | undefined>(historico[0]?.id);
  // Filtrar resultados pela execução selecionada (simulação)
  const resultadosFiltrados = selectedExecId
    ? resultados.filter(r => (r.dataExecucao || '2024-06-27T10:00:00Z') === historico.find(h => h.id === selectedExecId)?.data)
    : resultados;
  // Dados para gráfico de barras (distribuição de scores por categoria)
  const chartData = Object.values(resultadosFiltrados.reduce((acc, r) => {
    if (!acc[r.categoria]) acc[r.categoria] = { categoria: r.categoria, score: 0 };
    acc[r.categoria].score += r.score;
    return acc;
  }, {} as Record<string, { categoria: string; score: number }>));

  return (
    <div style={{ display: 'flex', width: '100%' }}>
      <HistoryPanel items={historico} onSelect={setSelectedExecId} selectedId={selectedExecId} />
      <section style={{ flex: 1, padding: 24 }}>
        <h2>Resultados do Nicho: {nichoNome}</h2>
        <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
          <button onClick={() => exportToCSV(resultadosFiltrados, `resultados_${nichoNome}.csv`)}>Exportar CSV</button>
          <button onClick={() => exportToJSON(resultadosFiltrados, `resultados_${nichoNome}.json`)}>Exportar JSON</button>
        </div>
        <ResultsChart
          data={chartData}
          type="bar"
          xKey="categoria"
          yKey="score"
          title="Distribuição de Scores por Categoria"
        />
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 32 }}>
          <thead>
            <tr>
              <th>Termo</th>
              <th>Score</th>
              <th>Categoria</th>
              <th>Prompt</th>
            </tr>
          </thead>
          <tbody>
            {resultadosFiltrados.map((r, i) => (
              <tr key={i}>
                <td>{r.termo}</td>
                <td>{r.score}</td>
                <td>{r.categoria}</td>
                <td>{r.prompt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default ResultadosPainel; 