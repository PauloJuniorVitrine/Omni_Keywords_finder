/**
 * Tipos TypeScript sincronizados com o backend
 * 
 * Este arquivo contém todos os tipos que devem estar sincronizados
 * entre frontend e backend para garantir consistência de dados.
 * 
 * Tracing ID: FIXTYPE-001_TYPES_SYNC_20241227_001
 * Data: 2024-12-27
 */

// ============================================================================
// 🏗️ TIPOS BASE
// ============================================================================

export interface BaseEntity {
  id: string; // ✅ Sincronizado: backend retorna string, não number
  created_at: string;
  updated_at: string;
}

// ============================================================================
// 📊 TIPOS DE NICHOS
// ============================================================================

export interface Nicho extends BaseEntity {
  nome: string;
  descricao: string;
  status: NichoStatus;
  total_categorias: number;
  ultima_execucao?: string;
}

export type NichoStatus = 'ativo' | 'inativo' | 'pendente';

// ============================================================================
// 📂 TIPOS DE CATEGORIAS
// ============================================================================

export interface Categoria extends BaseEntity {
  nome: string;
  descricao: string;
  nicho_id: string;
  palavras_chave: string[];
  status_execucao: StatusExecucao; // ✅ Sincronizado: enum consistente
  ultima_execucao?: string;
  total_clusters: number;
}

export type StatusExecucao = 'pendente' | 'processando' | 'concluida' | 'erro';

// ============================================================================
// 🔄 TIPOS DE EXECUÇÕES
// ============================================================================

export interface Execucao extends BaseEntity {
  blog_dominio: string;
  categoria: string;
  tipo_execucao: TipoExecucao;
  modelo_ia: string;
  inicio_execucao: string;
  fim_execucao?: string;
  status: StatusExecucao;
  clusters_gerados: string[];
  erros: string[];
  metricas: MetricasExecucao;
}

export type TipoExecucao = 'individual' | 'lote';

export interface MetricasExecucao {
  duracao_segundos: number;
  total_clusters: number;
  total_erros: number;
  media_tempo_cluster: number;
  taxa_sucesso: number;
}

// ============================================================================
// 📝 TIPOS DE PROMPTS
// ============================================================================

export interface PromptBase extends BaseEntity {
  categoria_id: string;
  template: string;
  lacunas: string[];
  status: PromptStatus;
  versao: number;
}

export type PromptStatus = 'ativo' | 'inativo' | 'rascunho';

export interface DadosColetados extends BaseEntity {
  categoria_id: string;
  dados: Record<string, any>;
  fonte: string;
  validado: boolean;
  score_qualidade: number;
}

// ============================================================================
// 📊 TIPOS DE ESTATÍSTICAS
// ============================================================================

export interface DashboardStats {
  total_nichos: number;
  total_categorias: number;
  total_prompts_base: number;
  total_dados_coletados: number;
  total_prompts_preenchidos: number;
  tempo_medio_processamento: number;
  taxa_sucesso: number;
}

// ============================================================================
// 🔐 TIPOS DE AUTENTICAÇÃO
// ============================================================================

export interface User extends BaseEntity {
  username: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  last_login?: string;
  is_active: boolean;
}

export type UserRole = 'admin' | 'user' | 'viewer';

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
}

export interface Role extends BaseEntity {
  name: string;
  description: string;
  permissions: Permission[];
  is_default: boolean;
}

// ============================================================================
// 📋 TIPOS DE LOGS
// ============================================================================

export interface Log extends BaseEntity {
  event: string;
  status: LogStatus;
  source: string;
  details: Record<string, any>;
  user_id?: string;
  ip_address?: string;
  user_agent?: string;
}

export type LogStatus = 'success' | 'error' | 'warning' | 'info';

// ============================================================================
// 🔔 TIPOS DE NOTIFICAÇÕES
// ============================================================================

export interface Notificacao extends BaseEntity {
  user_id: string;
  titulo: string;
  mensagem: string;
  tipo: TipoNotificacao;
  lida: boolean;
  dados_adicional?: Record<string, any>;
}

export type TipoNotificacao = 'info' | 'success' | 'warning' | 'error';

// ============================================================================
// 🧪 TIPOS DE A/B TESTING
// ============================================================================

export interface ABTest extends BaseEntity {
  nome: string;
  descricao: string;
  status: ABTestStatus;
  variantes: ABTestVariante[];
  metricas: ABTestMetricas;
  data_inicio: string;
  data_fim?: string;
}

export type ABTestStatus = 'ativo' | 'pausado' | 'concluido';

export interface ABTestVariante {
  id: string;
  nome: string;
  configuracao: Record<string, any>;
  trafego_percentual: number;
}

export interface ABTestMetricas {
  total_usuarios: number;
  conversoes: number;
  taxa_conversao: number;
  confianca: number;
}

// ============================================================================
// 📈 TIPOS DE ANALYTICS
// ============================================================================

export interface AnalyticsEvent extends BaseEntity {
  event_name: string;
  user_id?: string;
  session_id: string;
  properties: Record<string, any>;
  timestamp: string;
  source: string;
}

// ============================================================================
// 🔧 TIPOS DE CONFIGURAÇÃO
// ============================================================================

export interface Configuracao extends BaseEntity {
  chave: string;
  valor: string;
  tipo: TipoConfiguracao;
  descricao: string;
  ambiente: string;
}

export type TipoConfiguracao = 'string' | 'number' | 'boolean' | 'json';

// ============================================================================
// 📄 TIPOS DE RESPOSTAS DE API
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
  tracing_id: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// ============================================================================
// 🎯 TIPOS DE FILTROS E QUERIES
// ============================================================================

export interface QueryFilters {
  page?: number;
  per_page?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  filters?: Record<string, any>;
}

export interface NichoFilters extends QueryFilters {
  status?: NichoStatus;
  created_after?: string;
  created_before?: string;
}

export interface CategoriaFilters extends QueryFilters {
  nicho_id?: string;
  status_execucao?: StatusExecucao;
  has_prompts?: boolean;
}

export interface ExecucaoFilters extends QueryFilters {
  tipo_execucao?: TipoExecucao;
  status?: StatusExecucao;
  modelo_ia?: string;
  data_inicio?: string;
  data_fim?: string;
}

// ============================================================================
// 🔄 TIPOS DE MUTAÇÕES
// ============================================================================

export interface CreateNichoRequest {
  nome: string;
  descricao: string;
}

export interface UpdateNichoRequest {
  nome?: string;
  descricao?: string;
  status?: NichoStatus;
}

export interface CreateCategoriaRequest {
  nome: string;
  descricao: string;
  nicho_id: string;
  palavras_chave: string[];
}

export interface UpdateCategoriaRequest {
  nome?: string;
  descricao?: string;
  palavras_chave?: string[];
  status_execucao?: StatusExecucao;
}

export interface CreateExecucaoRequest {
  blog_dominio: string;
  categoria: string;
  tipo_execucao: TipoExecucao;
  modelo_ia: string;
}

// ============================================================================
// 🎨 TIPOS DE UI/UX
// ============================================================================

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
  progress?: number;
  message?: string;
}

// ============================================================================
// 🔍 TIPOS DE VALIDAÇÃO
// ============================================================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

// ============================================================================
// 📊 TIPOS DE MÉTRICAS DE PERFORMANCE
// ============================================================================

export interface PerformanceMetrics {
  endpoint: string;
  method: string;
  response_time: number;
  status_code: number;
  timestamp: string;
  user_id?: string;
  session_id: string;
}

// ============================================================================
// 🎯 EXPORT DEFAULT
// ============================================================================

export default {
  // Tipos base
  BaseEntity,
  Nicho,
  Categoria,
  Execucao,
  PromptBase,
  DadosColetados,
  DashboardStats,
  
  // Autenticação
  User,
  Role,
  Permission,
  
  // Logs e notificações
  Log,
  Notificacao,
  
  // A/B Testing
  ABTest,
  
  // Analytics
  AnalyticsEvent,
  
  // Configuração
  Configuracao,
  
  // Respostas de API
  ApiResponse,
  PaginatedResponse,
  
  // Filtros
  QueryFilters,
  NichoFilters,
  CategoriaFilters,
  ExecucaoFilters,
  
  // Mutações
  CreateNichoRequest,
  UpdateNichoRequest,
  CreateCategoriaRequest,
  UpdateCategoriaRequest,
  CreateExecucaoRequest,
  
  // UI/UX
  ToastMessage,
  LoadingState,
  
  // Validação
  ValidationError,
  ValidationResult,
  
  // Performance
  PerformanceMetrics,
}; 