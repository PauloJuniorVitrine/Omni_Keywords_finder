import { t, setIdioma } from '../i18n_v1';

describe('i18n_v1', () => {
  it('traduz para pt-BR', () => {
    setIdioma('pt-BR');
    expect(t('dashboard.titulo')).toBe('Dashboard de Monitoramento');
  });
  it('traduz para en-US', () => {
    setIdioma('en-US');
    expect(t('dashboard.titulo')).toBe('Monitoring Dashboard');
  });
  it('faz fallback para chave se não existir', () => {
    setIdioma('pt-BR');
    expect(t('nao.existe')).toBe('nao.existe');
  });
}); 