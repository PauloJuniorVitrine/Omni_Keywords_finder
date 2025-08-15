/**
 * @fileoverview Schemas de validação compartilhados backend-frontend
 * @prompt COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md
 * @ruleset enterprise_control_layer.yaml
 * @execution 2025-01-27T15:30:00Z
 * @tracing_id COMM_CHECKLIST_20250127_001
 */

import { z } from 'zod';

// ============================================================================
// SCHEMAS BASE
// ============================================================================

export const PaginationSchema = z.object({
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('asc'),
});

export const ApiErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  details: z.record(z.any()).optional(),
  stack: z.string().optional(),
});

export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: ApiErrorSchema.optional(),
    message: z.string().optional(),
    timestamp: z.string().datetime(),
    requestId: z.string().uuid(),
  });

// ============================================================================
// SCHEMAS DE AUTENTICAÇÃO
// ============================================================================

export const AuthCredentialsSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Senha deve ter pelo menos 8 caracteres'),
});

export const RefreshTokenSchema = z.object({
  refreshToken: z.string().min(1, 'Refresh token é obrigatório'),
});

export const UserRoleSchema = z.enum(['admin', 'user', 'moderator', 'guest']);

export const UserProfileSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1, 'Nome é obrigatório'),
  role: UserRoleSchema,
  permissions: z.array(z.string()),
  lastLogin: z.string().datetime().optional(),
  isActive: z.boolean(),
});

export const AuthResponseSchema = z.object({
  accessToken: z.string().min(1, 'Access token é obrigatório'),
  refreshToken: z.string().min(1, 'Refresh token é obrigatório'),
  expiresIn: z.number().int().positive(),
  user: UserProfileSchema,
});

// ============================================================================
// SCHEMAS DE KEYWORDS
// ============================================================================

export const KeywordSchema = z.object({
  id: z.string().uuid(),
  term: z.string().min(1, 'Termo é obrigatório'),
  searchVolume: z.number().int().min(0),
  difficulty: z.number().min(0).max(100),
  cpc: z.number().min(0),
  competition: z.number().min(0).max(1),
  relatedKeywords: z.array(z.string()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export const KeywordSearchParamsSchema = PaginationSchema.extend({
  query: z.string().optional(),
  minVolume: z.number().int().min(0).optional(),
  maxDifficulty: z.number().min(0).max(100).optional(),
  category: z.string().optional(),
  language: z.string().length(2).optional(),
});

export const KeywordAnalysisSchema = z.object({
  keyword: KeywordSchema,
  seoScore: z.number().min(0).max(100),
  opportunities: z.array(z.string()),
  risks: z.array(z.string()),
  recommendations: z.array(z.string()),
});

// ============================================================================
// SCHEMAS DE BLOGS
// ============================================================================

export const BlogStatusSchema = z.enum(['active', 'inactive', 'analyzing', 'error']);

export const BlogSchema = z.object({
  id: z.string().uuid(),
  url: z.string().url('URL inválida'),
  title: z.string().min(1, 'Título é obrigatório'),
  description: z.string().optional(),
  keywords: z.array(z.string()),
  status: BlogStatusSchema,
  lastAnalyzed: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export const KeywordOpportunitySchema = z.object({
  keyword: z.string().min(1),
  searchVolume: z.number().int().min(0),
  difficulty: z.number().min(0).max(100),
  potentialTraffic: z.number().int().min(0),
});

export const ContentGapSchema = z.object({
  keyword: z.string().min(1),
  searchVolume: z.number().int().min(0),
  competition: z.number().min(0).max(1),
  suggestedContent: z.string().min(1),
});

export const TechnicalIssueSchema = z.object({
  type: z.enum(['seo', 'performance', 'security', 'accessibility']),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  description: z.string().min(1),
  recommendation: z.string().min(1),
});

export const BlogAnalysisSchema = z.object({
  blog: BlogSchema,
  seoScore: z.number().min(0).max(100),
  keywordOpportunities: z.array(KeywordOpportunitySchema),
  contentGaps: z.array(ContentGapSchema),
  technicalIssues: z.array(TechnicalIssueSchema),
});

// ============================================================================
// SCHEMAS DE ANÁLISE
// ============================================================================

export const AnalysisTypeSchema = z.enum(['keyword', 'blog', 'competitor']);

export const AnalysisStatusSchema = z.enum([
  'pending',
  'running',
  'completed',
  'failed',
  'cancelled',
]);

export const AnalysisRequestSchema = z.object({
  type: AnalysisTypeSchema,
  target: z.string().min(1, 'Target é obrigatório'),
  options: z.record(z.any()).optional(),
});

export const AnalysisResponseSchema = z.object({
  id: z.string().uuid(),
  status: AnalysisStatusSchema,
  progress: z.number().min(0).max(100),
  result: z.any().optional(),
  error: ApiErrorSchema.optional(),
  estimatedCompletion: z.string().datetime().optional(),
});

// ============================================================================
// SCHEMAS DE NOTIFICAÇÕES
// ============================================================================

export const NotificationTypeSchema = z.enum([
  'analysis_complete',
  'error',
  'system',
  'update',
]);

export const NotificationSchema = z.object({
  id: z.string().uuid(),
  type: NotificationTypeSchema,
  title: z.string().min(1, 'Título é obrigatório'),
  message: z.string().min(1, 'Mensagem é obrigatória'),
  severity: z.enum(['info', 'warning', 'error', 'success']),
  read: z.boolean(),
  createdAt: z.string().datetime(),
  actionUrl: z.string().url().optional(),
});

// ============================================================================
// SCHEMAS DE CONFIGURAÇÃO
// ============================================================================

export const ApiConfigSchema = z.object({
  baseUrl: z.string().url('URL base inválida'),
  timeout: z.number().int().positive(),
  retryAttempts: z.number().int().min(0),
  retryDelay: z.number().int().positive(),
  enableCache: z.boolean(),
  enableLogging: z.boolean(),
});

export const UserPreferencesSchema = z.object({
  theme: z.enum(['light', 'dark', 'auto']),
  language: z.string().length(2),
  notifications: z.object({
    email: z.boolean(),
    push: z.boolean(),
    sms: z.boolean(),
  }),
  analysisSettings: z.object({
    defaultLanguage: z.string().length(2),
    includeCompetitors: z.boolean(),
    maxKeywords: z.number().int().positive(),
  }),
});

// ============================================================================
// SCHEMAS DE WEBSOCKET
// ============================================================================

export const WebSocketMessageSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    type: z.string().min(1),
    data: dataSchema,
    timestamp: z.string().datetime(),
    requestId: z.string().uuid().optional(),
  });

export const AnalysisProgressMessageSchema = z.object({
  analysisId: z.string().uuid(),
  progress: z.number().min(0).max(100),
  status: AnalysisStatusSchema,
  message: z.string().min(1),
});

export const RealTimeNotificationSchema = z.object({
  type: NotificationTypeSchema,
  title: z.string().min(1),
  message: z.string().min(1),
  severity: z.enum(['info', 'warning', 'error', 'success']),
});

// ============================================================================
// SCHEMAS DE CACHE
// ============================================================================

export const CacheEntrySchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    key: z.string().min(1),
    data: dataSchema,
    timestamp: z.number().int().positive(),
    ttl: z.number().int().positive(),
    version: z.string().min(1),
  });

export const CacheConfigSchema = z.object({
  enabled: z.boolean(),
  defaultTTL: z.number().int().positive(),
  maxSize: z.number().int().positive(),
  strategy: z.enum(['lru', 'fifo', 'lfu']),
});

// ============================================================================
// SCHEMAS DE TELEMETRIA
// ============================================================================

export const TelemetryEventSchema = z.object({
  name: z.string().min(1),
  category: z.string().min(1),
  properties: z.record(z.any()).optional(),
  timestamp: z.string().datetime(),
  sessionId: z.string().min(1),
  userId: z.string().uuid().optional(),
});

export const PerformanceMetricSchema = z.object({
  name: z.string().min(1),
  value: z.number(),
  unit: z.string().min(1),
  timestamp: z.string().datetime(),
  context: z.record(z.any()).optional(),
});

// ============================================================================
// SCHEMAS DE VALIDAÇÃO
// ============================================================================

export const ValidationErrorSchema = z.object({
  field: z.string().min(1),
  message: z.string().min(1),
  code: z.string().min(1),
  value: z.any().optional(),
});

export const ValidationResultSchema = z.object({
  isValid: z.boolean(),
  errors: z.array(ValidationErrorSchema),
});

// ============================================================================
// SCHEMAS DE RATE LIMITING
// ============================================================================

export const RateLimitInfoSchema = z.object({
  limit: z.number().int().positive(),
  remaining: z.number().int().min(0),
  reset: z.number().int().positive(),
  retryAfter: z.number().int().positive().optional(),
});

// ============================================================================
// SCHEMAS DE VERSÃO E COMPATIBILIDADE
// ============================================================================

export const ApiVersionSchema = z.object({
  version: z.string().min(1),
  deprecated: z.boolean(),
  sunsetDate: z.string().datetime().optional(),
  breakingChanges: z.array(z.string()),
});

export const CompatibilityInfoSchema = z.object({
  minVersion: z.string().min(1),
  recommendedVersion: z.string().min(1),
  latestVersion: z.string().min(1),
  deprecatedVersions: z.array(z.string()),
});

// ============================================================================
// SCHEMAS DE RESPOSTAS PAGINADAS
// ============================================================================

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  ApiResponseSchema(z.array(dataSchema)).extend({
    pagination: z.object({
      page: z.number().int().positive(),
      limit: z.number().int().positive(),
      total: z.number().int().min(0),
      totalPages: z.number().int().min(0),
      hasNext: z.boolean(),
      hasPrev: z.boolean(),
    }),
  });

// ============================================================================
// SCHEMAS DE FILTROS COMUNS
// ============================================================================

export const DateRangeSchema = z.object({
  start: z.string().datetime(),
  end: z.string().datetime(),
}).refine(
  (data) => new Date(data.start) <= new Date(data.end),
  {
    message: 'Data de início deve ser anterior à data de fim',
    path: ['start'],
  }
);

export const SearchFiltersSchema = z.object({
  query: z.string().optional(),
  dateRange: DateRangeSchema.optional(),
  categories: z.array(z.string()).optional(),
  status: z.array(z.string()).optional(),
  tags: z.array(z.string()).optional(),
});

// ============================================================================
// SCHEMAS DE ORDENAÇÃO
// ============================================================================

export const SortOptionSchema = z.object({
  field: z.string().min(1),
  direction: z.enum(['asc', 'desc']),
});

export const SortOptionsSchema = z.array(SortOptionSchema);

// ============================================================================
// SCHEMAS DE AGRUPAMENTO
// ============================================================================

export const GroupBySchema = z.object({
  field: z.string().min(1),
  includeCount: z.boolean().default(true),
  includeSum: z.boolean().default(false),
  includeAverage: z.boolean().default(false),
});

// ============================================================================
// SCHEMAS DE EXPORTAÇÃO
// ============================================================================

export const ExportFormatSchema = z.enum(['json', 'csv', 'xlsx', 'pdf']);

export const ExportRequestSchema = z.object({
  format: ExportFormatSchema,
  filters: SearchFiltersSchema.optional(),
  sortOptions: SortOptionsSchema.optional(),
  groupBy: GroupBySchema.optional(),
  includeHeaders: z.boolean().default(true),
});

// ============================================================================
// SCHEMAS DE BATCH OPERATIONS
// ============================================================================

export const BatchOperationSchema = z.object({
  operation: z.enum(['create', 'update', 'delete', 'export']),
  items: z.array(z.any()),
  options: z.record(z.any()).optional(),
});

export const BatchResponseSchema = z.object({
  success: z.boolean(),
  processed: z.number().int().min(0),
  failed: z.number().int().min(0),
  errors: z.array(ApiErrorSchema).optional(),
  results: z.array(z.any()).optional(),
});

// ============================================================================
// SCHEMAS DE AUDITORIA
// ============================================================================

export const AuditLogSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid().optional(),
  action: z.string().min(1),
  resourceType: z.string().min(1),
  resourceId: z.string().optional(),
  details: z.record(z.any()),
  ipAddress: z.string().ip().optional(),
  userAgent: z.string().optional(),
  createdAt: z.string().datetime(),
  metadata: z.record(z.any()).optional(),
});

// ============================================================================
// SCHEMAS DE SISTEMA
// ============================================================================

export const SystemLogSchema = z.object({
  id: z.string().uuid(),
  level: z.enum(['debug', 'info', 'warning', 'error', 'critical']),
  message: z.string().min(1),
  module: z.string().min(1),
  function: z.string().optional(),
  line: z.number().int().positive().optional(),
  stackTrace: z.string().optional(),
  context: z.record(z.any()),
  createdAt: z.string().datetime(),
  tracingId: z.string().min(1),
});

// ============================================================================
// SCHEMAS DE HEALTH CHECK
// ============================================================================

export const HealthCheckSchema = z.object({
  status: z.enum(['healthy', 'unhealthy', 'degraded']),
  timestamp: z.string().datetime(),
  version: z.string().min(1),
  uptime: z.number().positive(),
  services: z.record(z.object({
    status: z.enum(['healthy', 'unhealthy', 'degraded']),
    responseTime: z.number().positive().optional(),
    error: z.string().optional(),
  })),
});

// ============================================================================
// EXPORTAÇÕES
// ============================================================================

export {
  // Schemas base
  PaginationSchema,
  ApiErrorSchema,
  ApiResponseSchema,
  
  // Schemas de autenticação
  AuthCredentialsSchema,
  RefreshTokenSchema,
  UserRoleSchema,
  UserProfileSchema,
  AuthResponseSchema,
  
  // Schemas de keywords
  KeywordSchema,
  KeywordSearchParamsSchema,
  KeywordAnalysisSchema,
  
  // Schemas de blogs
  BlogStatusSchema,
  BlogSchema,
  KeywordOpportunitySchema,
  ContentGapSchema,
  TechnicalIssueSchema,
  BlogAnalysisSchema,
  
  // Schemas de análise
  AnalysisTypeSchema,
  AnalysisStatusSchema,
  AnalysisRequestSchema,
  AnalysisResponseSchema,
  
  // Schemas de notificações
  NotificationTypeSchema,
  NotificationSchema,
  
  // Schemas de configuração
  ApiConfigSchema,
  UserPreferencesSchema,
  
  // Schemas de WebSocket
  WebSocketMessageSchema,
  AnalysisProgressMessageSchema,
  RealTimeNotificationSchema,
  
  // Schemas de cache
  CacheEntrySchema,
  CacheConfigSchema,
  
  // Schemas de telemetria
  TelemetryEventSchema,
  PerformanceMetricSchema,
  
  // Schemas de validação
  ValidationErrorSchema,
  ValidationResultSchema,
  
  // Schemas de rate limiting
  RateLimitInfoSchema,
  
  // Schemas de versão
  ApiVersionSchema,
  CompatibilityInfoSchema,
  
  // Schemas de respostas paginadas
  PaginatedResponseSchema,
  
  // Schemas de filtros
  DateRangeSchema,
  SearchFiltersSchema,
  
  // Schemas de ordenação
  SortOptionSchema,
  SortOptionsSchema,
  
  // Schemas de agrupamento
  GroupBySchema,
  
  // Schemas de exportação
  ExportFormatSchema,
  ExportRequestSchema,
  
  // Schemas de batch operations
  BatchOperationSchema,
  BatchResponseSchema,
  
  // Schemas de auditoria
  AuditLogSchema,
  SystemLogSchema,
  
  // Schemas de health check
  HealthCheckSchema,
}; 