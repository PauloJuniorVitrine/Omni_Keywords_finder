import React, { useEffect, useState } from 'react';

interface ExecucaoStatus {
  id: string;
  status: string;
  inicio: string;
  fim: string;
  tipo: string;
  erro?: string;
}

interface ExportacaoStatus {
  arquivo: string;
  status: string;
  data: string;
}

interface Metricas {
  execucoes_total: number;
  execucoes_erro: number;
  exportacoes_total: number;
  exportacoes_erro: number;
}

// Simulação de fetch do backend
const fetchMonitoramento = async () => {
  return {
    execucoes: [
      { id: '1', status: 'ok', inicio: '2024-06-27T10:00', fim: '2024-06-27T10:01', tipo: 'lote' },
      { id: '2', status: 'erro', inicio: '2024-06-27T10:02', fim: '2024-06-27T10:03', tipo: 'agendada', erro: 'Timeout' },
    ],
    exportacoes: [
      { arquivo: 'nicho1/export.csv', status: 'ok', data: '2024-06-27T10:05' },
      { arquivo: 'nicho2/export.csv', status: 'erro', data: '2024-06-27T10:06' },
    ],
    metricas: {
      execucoes_total: 10,
      execucoes_erro: 2,
      exportacoes_total: 8,
      exportacoes_erro: 1,
    },
  };
};

const MonitoramentoDashboard: React.FC = () => {
  const [execucoes, setExecucoes] = useState<ExecucaoStatus[]>([]);
  const [exportacoes, setExportacoes] = useState<ExportacaoStatus[]>([]);
  const [metricas, setMetricas] = useState<Metricas | null>(null);

  useEffect(() => {
    fetchMonitoramento().then((data) => {
      setExecucoes(data.execucoes);
      setExportacoes(data.exportacoes);
      setMetricas(data.metricas);
    });
  }, []);

  return (
    <div>
      <h2>Dashboard de Monitoramento</h2>
      <section>
        <h3>Métricas</h3>
        {metricas && (
          <ul>
            <li>Total execuções: {metricas.execucoes_total}</li>
            <li>Erros execuções: {metricas.execucoes_erro}</li>
            <li>Total exportações: {metricas.exportacoes_total}</li>
            <li>Erros exportações: {metricas.exportacoes_erro}</li>
          </ul>
        )}
      </section>
      <section>
        <h3>Status das Execuções</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Status</th><th>Início</th><th>Fim</th><th>Tipo</th><th>Erro</th>
            </tr>
          </thead>
          <tbody>
            {execucoes.map((e) => (
              <tr key={e.id}>
                <td>{e.id}</td><td>{e.status}</td><td>{e.inicio}</td><td>{e.fim}</td><td>{e.tipo}</td><td>{e.erro || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section>
        <h3>Status das Exportações</h3>
        <table>
          <thead>
            <tr>
              <th>Arquivo</th><th>Status</th><th>Data</th>
            </tr>
          </thead>
          <tbody>
            {exportacoes.map((e) => (
              <tr key={e.arquivo}>
                <td>{e.arquivo}</td><td>{e.status}</td><td>{e.data}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default MonitoramentoDashboard; 