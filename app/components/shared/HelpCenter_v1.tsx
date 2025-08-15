import React from 'react';

/**
 * HelpCenter - Central de ajuda e FAQ acessível.
 * @param open Se o painel/modal está aberto
 * @param onClose Callback para fechar
 * @param topics Lista de tópicos/FAQ
 * @param supportLink Link para suporte externo
 */
export interface HelpCenterProps {
  open: boolean;
  onClose: () => void;
  topics: { title: string; content: React.ReactNode }[];
  supportLink?: string;
}

const HelpCenter: React.FC<HelpCenterProps> = ({ open, onClose, topics, supportLink }) => {
  if (!open) return null;
  return (
    <aside role="dialog" aria-modal="true" style={{ position: 'fixed', right: 0, top: 0, width: 400, maxWidth: '100vw', height: '100vh', background: '#fff', boxShadow: '-2px 0 16px rgba(0,0,0,0.08)', zIndex: 2100, padding: 32, overflowY: 'auto' }}>
      <button onClick={onClose} aria-label="Fechar ajuda" style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', fontSize: 22, cursor: 'pointer' }}>×</button>
      <h2 style={{ fontSize: 22, marginBottom: 24 }}>Central de Ajuda</h2>
      <ul style={{ padding: 0, listStyle: 'none' }}>
        {topics.map((t, i) => (
          <li key={i} style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>{t.title}</h3>
            <div style={{ color: '#444', fontSize: 15 }}>{t.content}</div>
          </li>
        ))}
      </ul>
      {supportLink && (
        <a href={supportLink} target="_blank" rel="noopener noreferrer" style={{ color: '#4f8cff', fontWeight: 600 }}>Fale com o suporte</a>
      )}
    </aside>
  );
};

export default HelpCenter; 