import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AdvancedFilters, { AdvancedFiltersValues } from '../AdvancedFilters_v1';

describe('AdvancedFilters_v1', () => {
  const nichos = [
    { id: 'n1', nome: 'Saúde' },
    { id: 'n2', nome: 'Finanças' },
  ];
  const categorias = [
    { id: 'c1', nome: 'Emagrecimento' },
    { id: 'c2', nome: 'Investimentos' },
  ];
  const statusOptions = ['Ativo', 'Inativo'];
  const defaultValues: AdvancedFiltersValues = {};

  it('renderiza selects e datepickers', () => {
    render(
      <AdvancedFilters
        nichos={nichos}
        categorias={categorias}
        statusOptions={statusOptions}
        onChange={() => {}}
        values={defaultValues}
      />
    );
    expect(screen.getByLabelText('Filtrar por nicho')).toBeInTheDocument();
    expect(screen.getByLabelText('Filtrar por categoria')).toBeInTheDocument();
    expect(screen.getByLabelText('Filtrar por status')).toBeInTheDocument();
    expect(screen.getByLabelText('Data início')).toBeInTheDocument();
    expect(screen.getByLabelText('Data fim')).toBeInTheDocument();
  });

  it('dispara onChange ao selecionar filtros', () => {
    const onChange = jest.fn();
    render(
      <AdvancedFilters
        nichos={nichos}
        categorias={categorias}
        statusOptions={statusOptions}
        onChange={onChange}
        values={defaultValues}
      />
    );
    fireEvent.change(screen.getByLabelText('Filtrar por nicho'), { target: { value: 'n1' } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ nichoId: 'n1', categoriaId: '' }));
    fireEvent.change(screen.getByLabelText('Filtrar por categoria'), { target: { value: 'c1' } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ categoriaId: 'c1' }));
    fireEvent.change(screen.getByLabelText('Filtrar por status'), { target: { value: 'Ativo' } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ status: 'Ativo' }));
    fireEvent.change(screen.getByLabelText('Data início'), { target: { value: '2024-01-01' } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ dataInicio: '2024-01-01' }));
    fireEvent.change(screen.getByLabelText('Data fim'), { target: { value: '2024-01-31' } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ dataFim: '2024-01-31' }));
  });

  it('limpa filtros ao clicar em Limpar', () => {
    const onChange = jest.fn();
    render(
      <AdvancedFilters
        nichos={nichos}
        categorias={categorias}
        statusOptions={statusOptions}
        onChange={onChange}
        values={{ nichoId: 'n1', categoriaId: 'c1', status: 'Ativo', dataInicio: '2024-01-01', dataFim: '2024-01-31' }}
      />
    );
    fireEvent.click(screen.getByLabelText('Limpar filtros'));
    expect(onChange).toHaveBeenCalledWith({});
  });

  it('é acessível via aria-label', () => {
    render(
      <AdvancedFilters
        nichos={nichos}
        categorias={categorias}
        onChange={() => {}}
        values={defaultValues}
      />
    );
    expect(screen.getByLabelText('Filtros avançados')).toBeInTheDocument();
  });
}); 