/**
 * @fileoverview Tipos compartilhados para comunicação backend-frontend
 * @prompt COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md
 * @ruleset enterprise_control_layer.yaml
 * @execution 2025-01-27T15:30:00Z
 * @tracing_id COMM_CHECKLIST_20250127_001
 */

// ============================================================================
// TIPOS BASE
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  timestamp: string;
  requestId: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  stack?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// ============================================================================
// TIPOS DE AUTENTICAÇÃO
// ============================================================================

export interface AuthCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  user: UserProfile;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: string[];
  lastLogin?: string;
  isActive: boolean;
}

export type UserRole = 'admin' | 'user' | 'moderator' | 'guest';

export interface RefreshTokenRequest {
  refreshToken: string;
}

// ============================================================================
// TIPOS DE KEYWORDS
// ============================================================================

export interface Keyword {
  id: string;
  term: string;
  searchVolume: number;
  difficulty: number;
  cpc: number;
  competition: number;
  relatedKeywords: string[];
  createdAt: string;
  updatedAt: string;
}

export interface KeywordAnalysis {
  keyword: Keyword;
  seoScore: number;
  opportunities: string[];
  risks: string[];
  recommendations: string[];
}

export interface KeywordSearchParams extends PaginationParams {
  query?: string;
  minVolume?: number;
  maxDifficulty?: number;
  category?: string;
  language?: string;
}

// ============================================================================
// TIPOS DE BLOGS
// ============================================================================

export interface Blog {
  id: string;
  url: string;
  title: string;
  description?: string;
  keywords: string[];
  status: BlogStatus;
  lastAnalyzed?: string;
  createdAt: string;
  updatedAt: string;
}

export type BlogStatus = 'active' | 'inactive' | 'analyzing' | 'error';

export interface BlogAnalysis {
  blog: Blog;
  seoScore: number;
  keywordOpportunities: KeywordOpportunity[];
  contentGaps: ContentGap[];
  technicalIssues: TechnicalIssue[];
}

export interface KeywordOpportunity {
  keyword: string;
  searchVolume: number;
  difficulty: number;
  potentialTraffic: number;
}

export interface ContentGap {
  keyword: string;
  searchVolume: number;
  competition: number;
  suggestedContent: string;
}

export interface TechnicalIssue {
  type: 'seo' | 'performance' | 'security' | 'accessibility';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  recommendation: string;
}

// ============================================================================
// TIPOS DE ANÁLISE
// ============================================================================

export interface AnalysisRequest {
  type: 'keyword' | 'blog' | 'competitor';
  target: string;
  options?: Record<string, any>;
}

export interface AnalysisResponse {
  id: string;
  status: AnalysisStatus;
  progress: number;
  result?: any;
  error?: ApiError;
  estimatedCompletion?: string;
}

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// ============================================================================
// TIPOS DE NOTIFICAÇÕES
// ============================================================================

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  createdAt: string;
  actionUrl?: string;
}

export type NotificationType = 'analysis_complete' | 'error' | 'system' | 'update';

// ============================================================================
// TIPOS DE CONFIGURAÇÃO
// ============================================================================

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableCache: boolean;
  enableLogging: boolean;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  analysisSettings: {
    defaultLanguage: string;
    includeCompetitors: boolean;
    maxKeywords: number;
  };
}

// ============================================================================
// TIPOS DE WEBSOCKET
// ============================================================================

export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
  requestId?: string;
}

export interface AnalysisProgressMessage {
  analysisId: string;
  progress: number;
  status: AnalysisStatus;
  message: string;
}

export interface RealTimeNotification {
  type: NotificationType;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
}

// ============================================================================
// TIPOS DE CACHE
// ============================================================================

export interface CacheEntry<T = any> {
  key: string;
  data: T;
  timestamp: number;
  ttl: number;
  version: string;
}

export interface CacheConfig {
  enabled: boolean;
  defaultTTL: number;
  maxSize: number;
  strategy: 'lru' | 'fifo' | 'lfu';
}

// ============================================================================
// TIPOS DE TELEMETRIA
// ============================================================================

export interface TelemetryEvent {
  name: string;
  category: string;
  properties?: Record<string, any>;
  timestamp: string;
  sessionId: string;
  userId?: string;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  context?: Record<string, any>;
}

// ============================================================================
// TIPOS DE VALIDAÇÃO
// ============================================================================

export interface ValidationError {
  field: string;
  message: string;
  code: string;
  value?: any;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

// ============================================================================
// TIPOS DE RATE LIMITING
// ============================================================================

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  retryAfter?: number;
}

// ============================================================================
// TIPOS DE VERSÃO E COMPATIBILIDADE
// ============================================================================

export interface ApiVersion {
  version: string;
  deprecated: boolean;
  sunsetDate?: string;
  breakingChanges: string[];
}

export interface CompatibilityInfo {
  minVersion: string;
  recommendedVersion: string;
  latestVersion: string;
  deprecatedVersions: string[];
} 