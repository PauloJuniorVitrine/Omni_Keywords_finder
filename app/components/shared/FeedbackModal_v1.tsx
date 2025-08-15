import React, { useState } from 'react';

/**
 * FeedbackModal - Modal para envio de feedback do usuário.
 * @param open Se o modal está aberto
 * @param onClose Callback para fechar
 * @param onSubmit Callback ao enviar feedback
 */
export interface FeedbackModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: { message: string; category: string }) => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({ open, onClose, onSubmit }) => {
  const [message, setMessage] = useState('');
  const [category, setCategory] = useState('sugestao');
  if (!open) return null;
  return (
    <div role="dialog" aria-modal="true" style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.18)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2200 }}>
      <form onSubmit={e => { e.preventDefault(); onSubmit({ message, category }); setMessage(''); setCategory('sugestao'); onClose(); }} style={{ background: '#fff', borderRadius: 16, minWidth: 340, maxWidth: '90vw', boxShadow: '0 4px 24px rgba(0,0,0,0.10)', padding: 32, display: 'flex', flexDirection: 'column', gap: 16 }}>
        <h2 style={{ fontSize: 20, marginBottom: 8 }}>Envie seu feedback</h2>
        <select value={category} onChange={e => setCategory(e.target.value)} aria-label="Categoria do feedback" style={{ padding: 8, borderRadius: 8, border: '1px solid #d1d5db' }}>
          <option value="sugestao">Sugestão</option>
          <option value="bug">Bug</option>
          <option value="elogio">Elogio</option>
        </select>
        <textarea value={message} onChange={e => setMessage(e.target.value)} required minLength={8} maxLength={500} placeholder="Descreva sua sugestão, bug ou elogio..." aria-label="Mensagem de feedback" style={{ minHeight: 80, borderRadius: 8, border: '1px solid #d1d5db', padding: 10, fontSize: 15 }} />
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button type="button" onClick={onClose} style={{ background: '#eee', color: '#222', border: 'none', borderRadius: 8, padding: '10px 24px', fontWeight: 600, cursor: 'pointer' }}>Cancelar</button>
          <button type="submit" style={{ background: '#4f8cff', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', fontWeight: 600, cursor: 'pointer' }}>Enviar</button>
        </div>
      </form>
    </div>
  );
};

export default FeedbackModal; 