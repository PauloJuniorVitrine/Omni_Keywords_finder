import React, { useState } from 'react';

interface CategoriaFormProps {
  onSubmit: (nome: string) => void;
  onCancel: () => void;
  initialNome?: string;
}

const CategoriaForm: React.FC<CategoriaFormProps> = ({ onSubmit, onCancel, initialNome = '' }) => {
  const [nome, setNome] = useState(initialNome);
  return (
    <form onSubmit={e => { e.preventDefault(); onSubmit(nome); }} style={{ padding: 24, minWidth: 320 }}>
      <label htmlFor="categoria-nome">Nome da Categoria</label>
      <input id="categoria-nome" value={nome} onChange={e => setNome(e.target.value)} placeholder="Ex: Emagrecimento, Investimentos..." style={{ width: '100%', marginBottom: 16 }} required />
      <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
        <button type="button" onClick={onCancel}>Cancelar</button>
        <button type="submit" disabled={!nome.trim()}>Salvar</button>
      </div>
    </form>
  );
};

export default CategoriaForm; 