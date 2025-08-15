type IdiomaSuportado = 'pt-BR' | 'en-US';

const traducoes: Record<IdiomaSuportado, Record<string, string>> = {
  'pt-BR': {
    'dashboard.titulo': 'Dashboard de Monitoramento',
    'metricas.total_execucoes': 'Total execuções',
    'metricas.erros_execucoes': 'Erros execuções',
    'metricas.total_exportacoes': 'Total exportações',
    'metricas.erros_exportacoes': 'Erros exportações',
    'status_execucoes': 'Status das Execuções',
    'status_exportacoes': 'Status das Exportações',
    'tabela.id': 'ID',
    'tabela.status': 'Status',
    'tabela.inicio': 'Início',
    'tabela.fim': 'Fim',
    'tabela.tipo': 'Tipo',
    'tabela.erro': 'Erro',
    'tabela.arquivo': 'Arquivo',
    'tabela.data': 'Data',
  },
  'en-US': {
    'dashboard.titulo': 'Monitoring Dashboard',
    'metricas.total_execucoes': 'Total runs',
    'metricas.erros_execucoes': 'Run errors',
    'metricas.total_exportacoes': 'Total exports',
    'metricas.erros_exportacoes': 'Export errors',
    'status_execucoes': 'Execution Status',
    'status_exportacoes': 'Export Status',
    'tabela.id': 'ID',
    'tabela.status': 'Status',
    'tabela.inicio': 'Start',
    'tabela.fim': 'End',
    'tabela.tipo': 'Type',
    'tabela.erro': 'Error',
    'tabela.arquivo': 'File',
    'tabela.data': 'Date',
  },
};

let idiomaAtual: IdiomaSuportado = 'pt-BR';

export function setIdioma(idioma: IdiomaSuportado) {
  idiomaAtual = idioma;
}

export function t(chave: string): string {
  return traducoes[idiomaAtual][chave] || chave;
}

// Exemplo de uso:
// import { t, setIdioma } from 'app/i18n/i18n_v1';
// setIdioma('en-US');
// t('dashboard.titulo') // 'Monitoring Dashboard' 