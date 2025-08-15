/**
 * Tipos TypeScript para o Sistema de Preenchimento de Lacunas
 */

export interface Nicho {
  id: number;
  nome: string;
  descricao?: string;
  created_at: string;
  updated_at: string;
  categorias?: Categoria[];
  dados_coletados?: DadosColetados[];
}

export interface Categoria {
  id: number;
  nicho_id: number;
  nome: string;
  descricao?: string;
  created_at: string;
  updated_at: string;
  nicho?: Nicho;
  prompt_base?: PromptBase;
  dados_coletados?: DadosColetados[];
}

export interface PromptBase {
  id: number;
  categoria_id: number;
  nome_arquivo: string;
  conteudo: string;
  hash_conteudo: string;
  created_at: string;
  updated_at: string;
  categoria?: Categoria;
  prompts_preenchidos?: PromptPreenchido[];
}

export interface DadosColetados {
  id: number;
  nicho_id: number;
  categoria_id: number;
  primary_keyword: string;
  secondary_keywords?: string;
  cluster_content: string;
  status: string;
  created_at: string;
  updated_at: string;
  nicho?: Nicho;
  categoria?: Categoria;
  prompts_preenchidos?: PromptPreenchido[];
}

export interface PromptPreenchido {
  id: number;
  dados_coletados_id: number;
  prompt_base_id: number;
  prompt_original: string;
  prompt_preenchido: string;
  lacunas_detectadas?: string; // JSON string
  lacunas_preenchidas?: string; // JSON string
  status: string;
  tempo_processamento?: number;
  created_at: string;
  updated_at: string;
  dados_coletados?: DadosColetados;
  prompt_base?: PromptBase;
}

export interface LogOperacao {
  id: number;
  tipo_operacao: string;
  entidade: string;
  entidade_id?: number;
  detalhes?: string; // JSON string
  status: string;
  tempo_execucao?: number;
  created_at: string;
}

// Schemas para criação/atualização
export interface NichoCreate {
  nome: string;
  descricao?: string;
}

export interface NichoUpdate {
  nome?: string;
  descricao?: string;
}

export interface CategoriaCreate {
  nicho_id: number;
  nome: string;
  descricao?: string;
}

export interface CategoriaUpdate {
  nicho_id?: number;
  nome?: string;
  descricao?: string;
}

export interface DadosColetadosCreate {
  nicho_id: number;
  categoria_id: number;
  primary_keyword: string;
  secondary_keywords?: string;
  cluster_content: string;
}

export interface DadosColetadosUpdate {
  primary_keyword?: string;
  secondary_keywords?: string;
  cluster_content?: string;
  status?: string;
}

export interface PromptBaseCreate {
  categoria_id: number;
  nome_arquivo: string;
  conteudo: string;
}

// Respostas de API
export interface ProcessamentoResponse {
  nicho_id?: number;
  categoria_id?: number;
  dados_id?: number;
  total_processados: number;
  sucessos: number;
  erros: number;
  resultados: Array<{
    id: number;
    status: string;
  }>;
  tempo_total?: number;
}

export interface DeteccaoLacunasResponse {
  categoria_id: number;
  total_lacunas: number;
  lacunas: Array<{
    tipo: string;
    original: string;
    quantidade: number;
    posicoes: number[];
  }>;
  conteudo_preview: string;
}

export interface EstatisticasNicho {
  nicho_id: number;
  nome_nicho: string;
  total_categorias: number;
  categorias_com_prompt: number;
  categorias_com_dados: number;
  prompts_preenchidos: number;
  tempo_medio_processamento?: number;
}

export interface EstatisticasGerais {
  total_nichos: number;
  total_categorias: number;
  total_prompts_base: number;
  total_dados_coletados: number;
  total_prompts_preenchidos: number;
  tempo_medio_processamento?: number;
  taxa_sucesso?: number;
  estatisticas_por_nicho: EstatisticasNicho[];
}

// Tipos para validação
export interface ValidacaoPromptRequest {
  categoria_id: number;
  conteudo: string;
}

export interface ValidacaoPromptResponse {
  valido: boolean;
  lacunas_detectadas: string[];
  lacunas_obrigatorias: string[];
  lacunas_opcionais: string[];
  erros: string[];
  avisos: string[];
}

// Tipos para lacunas
export interface LacunaDetectada {
  tipo: 'primary_keyword' | 'secondary_keywords' | 'cluster_content';
  original: string;
  quantidade: number;
  posicoes: number[];
}

export interface LacunaPreenchida {
  tipo: 'primary_keyword' | 'secondary_keywords' | 'cluster_content';
  original: string;
  substituido_por: string;
  quantidade: number;
}

// Tipos para metadados de processamento
export interface MetadadosProcessamento {
  lacunas_detectadas: Record<string, string[]>;
  lacunas_preenchidas: Record<string, LacunaPreenchida>;
  tempo_processamento: number;
  hash_original: string;
  hash_preenchido: string;
}

// Tipos para configurações
export interface ConfiguracaoSistema {
  placeholders: Record<string, string>;
  limites: {
    primary_keyword_max: number;
    secondary_keywords_max: number;
    cluster_content_max: number;
  };
  processamento: {
    timeout_ms: number;
    max_retries: number;
    batch_size: number;
  };
}

// Tipos para notificações
export interface Notificacao {
  id: string;
  tipo: 'sucesso' | 'erro' | 'aviso' | 'info';
  titulo: string;
  mensagem: string;
  timestamp: string;
  lida: boolean;
}

// Tipos para auditoria
export interface EventoAuditoria {
  id: string;
  usuario_id?: string;
  acao: string;
  entidade: string;
  entidade_id?: number;
  dados_anteriores?: any;
  dados_novos?: any;
  timestamp: string;
  ip?: string;
  user_agent?: string;
} 