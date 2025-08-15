import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip as RTooltip, ResponsiveContainer, Legend
} from 'recharts';

/**
 * Componente de gráfico reutilizável para resultados (barra, linha, pizza).
 * @param data Dados do gráfico
 * @param type Tipo de gráfico ('bar' | 'line' | 'pie')
 * @param xKey Chave do eixo X
 * @param yKey Chave do eixo Y
 * @param title Título do gráfico
 * @param colors Paleta de cores opcional
 * @param height Altura do gráfico
 */
export interface ResultsChartProps {
  data: any[];
  type: 'bar' | 'line' | 'pie';
  xKey: string;
  yKey: string;
  title?: string;
  colors?: string[];
  height?: number;
}

const defaultColors = ['#4f8cff', '#eab308', '#22c55e', '#ef4444', '#a1a1aa', '#f59e42'];

const ResultsChart: React.FC<ResultsChartProps> = ({ data, type, xKey, yKey, title, colors = defaultColors, height = 320 }) => {
  return (
    <section aria-label={title || 'Gráfico de resultados'} style={{ width: '100%', maxWidth: 700, margin: '0 auto' }}>
      {title && <h4 style={{ textAlign: 'center', marginBottom: 12 }}>{title}</h4>}
      <ResponsiveContainer width="100%" height={height}>
        {type === 'bar' && (
          <BarChart data={data} aria-label="Gráfico de barras">
            <XAxis dataKey={xKey} stroke="#888" fontSize={14} />
            <YAxis stroke="#888" fontSize={14} />
            <RTooltip />
            <Legend />
            <Bar dataKey={yKey} fill={colors[0]} radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
        {type === 'line' && (
          <LineChart data={data} aria-label="Gráfico de linha">
            <XAxis dataKey={xKey} stroke="#888" fontSize={14} />
            <YAxis stroke="#888" fontSize={14} />
            <RTooltip />
            <Legend />
            <Line type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        )}
        {type === 'pie' && (
          <PieChart aria-label="Gráfico de pizza">
            <RTooltip />
            <Legend />
            <Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" outerRadius={90} label>
              {data.map((entry, i) => (
                <Cell key={`cell-${i}`} fill={colors[i % colors.length]} />
              ))}
            </Pie>
          </PieChart>
        )}
      </ResponsiveContainer>
    </section>
  );
};

export default ResultsChart; 