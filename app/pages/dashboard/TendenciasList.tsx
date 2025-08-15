import React from 'react';

interface Tendencia {
  nome: string;
  volume: number;
}

interface TendenciasListProps {
  tendencias: Tendencia[];
}

const TendenciasList: React.FC<TendenciasListProps> = ({ tendencias }) => {
  if (!tendencias || tendencias.length === 0) {
    return <div style={{ color: '#888', fontSize: 16 }} role="status" aria-live="polite">Nenhuma tendência disponível.</div>;
  }
  return (
    <ul role="list" aria-label="Lista de tendências">
      {tendencias.map((t, i) => (
        <li
          key={t.nome}
          style={{ fontSize: 18, animation: `fadeIn 0.${i + 7}s cubic-bezier(.4,0,.2,1)` }}
          tabIndex={0}
          aria-label={`Tendência ${t.nome}: ${t.volume}`}
        >
          {/* Ícone opcional */}
          <span role="img" aria-label="ícone de tendência" style={{ marginRight: 8 }}>📈</span>
          {t.nome}: {t.volume}
        </li>
      ))}
    </ul>
  );
};

export default TendenciasList; 