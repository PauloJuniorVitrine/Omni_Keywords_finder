import React from 'react';

/**
 * Filtros avançados dinâmicos para nicho, categoria, status e data.
 * @param nichos Lista de nichos disponíveis
 * @param categorias Lista de categorias disponíveis (filtradas pelo nicho)
 * @param statusOptions Opções de status
 * @param onChange Callback ao alterar qualquer filtro
 * @param values Valores atuais dos filtros
 * @param showDatePicker Exibir filtro de data
 */
export interface AdvancedFiltersProps {
  nichos: { id: string; nome: string }[];
  categorias: { id: string; nome: string }[];
  statusOptions?: string[];
  onChange: (values: AdvancedFiltersValues) => void;
  values: AdvancedFiltersValues;
  showDatePicker?: boolean;
}

export interface AdvancedFiltersValues {
  nichoId?: string;
  categoriaId?: string;
  status?: string;
  dataInicio?: string;
  dataFim?: string;
}

const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
  nichos,
  categorias,
  statusOptions = ['Ativo', 'Inativo', 'Pendente', 'Processado'],
  onChange,
  values,
  showDatePicker = true,
}) => {
  return (
    <form style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }} aria-label="Filtros avançados">
      <select
        value={values.nichoId || ''}
        onChange={e => onChange({ ...values, nichoId: e.target.value, categoriaId: '' })}
        aria-label="Filtrar por nicho"
        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', minWidth: 120 }}
      >
        <option value="">Todos os nichos</option>
        {nichos.map(n => <option key={n.id} value={n.id}>{n.nome}</option>)}
      </select>
      <select
        value={values.categoriaId || ''}
        onChange={e => onChange({ ...values, categoriaId: e.target.value })}
        aria-label="Filtrar por categoria"
        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', minWidth: 120 }}
        disabled={!values.nichoId}
      >
        <option value="">Todas as categorias</option>
        {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
      </select>
      <select
        value={values.status || ''}
        onChange={e => onChange({ ...values, status: e.target.value })}
        aria-label="Filtrar por status"
        style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', minWidth: 120 }}
      >
        <option value="">Todos os status</option>
        {statusOptions.map(s => <option key={s} value={s}>{s}</option>)}
      </select>
      {showDatePicker && (
        <>
          <input
            type="date"
            value={values.dataInicio || ''}
            onChange={e => onChange({ ...values, dataInicio: e.target.value })}
            aria-label="Data início"
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db' }}
          />
          <span style={{ fontSize: 14, color: '#888' }}>até</span>
          <input
            type="date"
            value={values.dataFim || ''}
            onChange={e => onChange({ ...values, dataFim: e.target.value })}
            aria-label="Data fim"
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db' }}
          />
        </>
      )}
      <button type="button" onClick={() => onChange({})} style={{ padding: '8px 18px', borderRadius: 6, border: 'none', background: '#eab308', color: '#fff', fontWeight: 600, cursor: 'pointer' }} aria-label="Limpar filtros">Limpar</button>
    </form>
  );
};

export default AdvancedFilters; 