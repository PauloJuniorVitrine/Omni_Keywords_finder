/**
 * auth-service.ts
 * 
 * Serviço de autenticação centralizado
 * 
 * Tracing ID: AUTH-SERVICE-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 3.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Login/Logout com múltiplos provedores
 * - Refresh token automático
 * - Gerenciamento de sessão
 * - Validação de tokens
 * - Logout em múltiplas abas
 * - Rate limiting
 * - Auditoria de login
 */

import { ApiClient } from './api/ApiClient';
import { AUTH_ENDPOINTS, API_ERROR_CODES } from '../shared/constants/endpoints';
import { LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse, User } from '../shared/types/api';

// Tipos
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  lastActivity: number;
}

interface AuthConfig {
  tokenKey: string;
  refreshTokenKey: string;
  userKey: string;
  autoRefresh: boolean;
  refreshThreshold: number; // segundos antes da expiração
  sessionTimeout: number; // segundos
  maxRetries: number;
  retryDelay: number;
}

interface LoginOptions {
  rememberMe?: boolean;
  provider?: 'local' | 'google' | 'github' | 'microsoft';
  redirectUrl?: string;
  metadata?: Record<string, any>;
}

interface LogoutOptions {
  allDevices?: boolean;
  reason?: string;
  redirectUrl?: string;
}

// Configuração padrão
const DEFAULT_CONFIG: AuthConfig = {
  tokenKey: 'authToken',
  refreshTokenKey: 'refreshToken',
  userKey: 'authUser',
  autoRefresh: true,
  refreshThreshold: 300, // 5 minutos
  sessionTimeout: 3600, // 1 hora
  maxRetries: 3,
  retryDelay: 1000,
};

class AuthService {
  private state: AuthState = {
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    lastActivity: Date.now(),
  };

  private config: AuthConfig;
  private refreshTimer: NodeJS.Timeout | null = null;
  private sessionTimer: NodeJS.Timeout | null = null;
  private retryCount = 0;
  private listeners: Set<(state: AuthState) => void> = new Set();

  constructor(config: Partial<AuthConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.initialize();
  }

  // Inicialização
  private initialize(): void {
    this.loadFromStorage();
    this.setupEventListeners();
    this.startSessionTimer();
    
    if (this.state.token && this.config.autoRefresh) {
      this.scheduleTokenRefresh();
    }
  }

  // Carregar dados do storage
  private loadFromStorage(): void {
    try {
      const token = localStorage.getItem(this.config.tokenKey);
      const refreshToken = localStorage.getItem(this.config.refreshTokenKey);
      const userStr = localStorage.getItem(this.config.userKey);

      if (token && refreshToken && userStr) {
        const user = JSON.parse(userStr) as User;
        
        // Verificar se o token ainda é válido
        if (this.isTokenValid(token)) {
          this.state = {
            user,
            token,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
            lastActivity: Date.now(),
          };
        } else {
          // Token expirado, tentar refresh
          this.refreshToken();
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados de autenticação:', error);
      this.clearStorage();
    }
  }

  // Salvar dados no storage
  private saveToStorage(): void {
    try {
      if (this.state.token) {
        localStorage.setItem(this.config.tokenKey, this.state.token);
      }
      
      if (this.state.refreshToken) {
        localStorage.setItem(this.config.refreshTokenKey, this.state.refreshToken);
      }
      
      if (this.state.user) {
        localStorage.setItem(this.config.userKey, JSON.stringify(this.state.user));
      }
    } catch (error) {
      console.error('Erro ao salvar dados de autenticação:', error);
    }
  }

  // Limpar storage
  private clearStorage(): void {
    try {
      localStorage.removeItem(this.config.tokenKey);
      localStorage.removeItem(this.config.refreshTokenKey);
      localStorage.removeItem(this.config.userKey);
    } catch (error) {
      console.error('Erro ao limpar dados de autenticação:', error);
    }
  }

  // Configurar event listeners
  private setupEventListeners(): void {
    // Atualizar lastActivity em interações do usuário
    const updateActivity = () => {
      this.state.lastActivity = Date.now();
      this.notifyListeners();
    };

    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });

    // Logout em múltiplas abas
    window.addEventListener('storage', (event) => {
      if (event.key === 'authLogout' && event.newValue) {
        this.handleMultiTabLogout();
      }
    });

    // Verificar conectividade
    window.addEventListener('online', () => {
      if (this.state.isAuthenticated && this.state.token) {
        this.validateToken();
      }
    });
  }

  // Verificar se token é válido
  private isTokenValid(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  // Obter tempo de expiração do token
  private getTokenExpiration(token: string): number | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000; // Converter para milissegundos
    } catch {
      return null;
    }
  }

  // Agendar refresh do token
  private scheduleTokenRefresh(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    if (!this.state.token) return;

    const expiration = this.getTokenExpiration(this.state.token);
    if (!expiration) return;

    const now = Date.now();
    const timeUntilRefresh = expiration - now - (this.config.refreshThreshold * 1000);

    if (timeUntilRefresh > 0) {
      this.refreshTimer = setTimeout(() => {
        this.refreshToken();
      }, timeUntilRefresh);
    } else {
      // Token já está próximo da expiração, refresh imediato
      this.refreshToken();
    }
  }

  // Iniciar timer de sessão
  private startSessionTimer(): void {
    if (this.sessionTimer) {
      clearInterval(this.sessionTimer);
    }

    this.sessionTimer = setInterval(() => {
      const now = Date.now();
      const timeSinceLastActivity = now - this.state.lastActivity;
      const sessionTimeoutMs = this.config.sessionTimeout * 1000;

      if (timeSinceLastActivity > sessionTimeoutMs) {
        this.logout({ reason: 'session_timeout' });
      }
    }, 60000); // Verificar a cada minuto
  }

  // Notificar listeners
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener({ ...this.state });
      } catch (error) {
        console.error('Erro ao notificar listener:', error);
      }
    });
  }

  // Login
  async login(credentials: LoginRequest, options: LoginOptions = {}): Promise<User> {
    this.state.isLoading = true;
    this.notifyListeners();

    try {
      const response = await ApiClient.post<LoginResponse>(AUTH_ENDPOINTS.LOGIN, {
        ...credentials,
        provider: options.provider || 'local',
        metadata: options.metadata,
      });

      const { user, token, refreshToken, expiresIn } = response.data;

      // Atualizar estado
      this.state = {
        user,
        token,
        refreshToken,
        isAuthenticated: true,
        isLoading: false,
        lastActivity: Date.now(),
      };

      // Salvar no storage se rememberMe estiver ativo
      if (options.rememberMe) {
        this.saveToStorage();
      }

      // Agendar refresh do token
      if (this.config.autoRefresh) {
        this.scheduleTokenRefresh();
      }

      // Registrar auditoria
      this.auditLogin(user, options);

      this.notifyListeners();
      return user;

    } catch (error) {
      this.state.isLoading = false;
      this.notifyListeners();
      throw error;
    }
  }

  // Logout
  async logout(options: LogoutOptions = {}): Promise<void> {
    try {
      if (this.state.token) {
        await ApiClient.post(AUTH_ENDPOINTS.LOGOUT, {
          allDevices: options.allDevices,
          reason: options.reason,
        });
      }
    } catch (error) {
      console.error('Erro ao fazer logout no servidor:', error);
    } finally {
      this.clearAuthState();
      
      // Notificar outras abas
      localStorage.setItem('authLogout', Date.now().toString());
      
      // Redirecionar se especificado
      if (options.redirectUrl) {
        window.location.href = options.redirectUrl;
      }
    }
  }

  // Refresh token
  async refreshToken(): Promise<boolean> {
    if (!this.state.refreshToken || this.retryCount >= this.config.maxRetries) {
      return false;
    }

    try {
      const response = await ApiClient.post<RefreshTokenResponse>(AUTH_ENDPOINTS.REFRESH, {
        refreshToken: this.state.refreshToken,
      } as RefreshTokenRequest);

      const { token, refreshToken, expiresIn } = response.data;

      // Atualizar estado
      this.state.token = token;
      this.state.refreshToken = refreshToken;
      this.state.lastActivity = Date.now();

      // Salvar no storage
      this.saveToStorage();

      // Agendar próximo refresh
      if (this.config.autoRefresh) {
        this.scheduleTokenRefresh();
      }

      this.retryCount = 0;
      this.notifyListeners();
      return true;

    } catch (error) {
      this.retryCount++;
      
      if (this.retryCount >= this.config.maxRetries) {
        // Refresh falhou, fazer logout
        this.logout({ reason: 'refresh_failed' });
        return false;
      }

      // Tentar novamente após delay
      await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * this.retryCount));
      return this.refreshToken();
    }
  }

  // Validar token
  async validateToken(): Promise<boolean> {
    if (!this.state.token) return false;

    try {
      await ApiClient.get(AUTH_ENDPOINTS.PROFILE);
      return true;
    } catch (error) {
      // Token inválido, tentar refresh
      return this.refreshToken();
    }
  }

  // Obter perfil do usuário
  async getProfile(): Promise<User> {
    const response = await ApiClient.get<User>(AUTH_ENDPOINTS.PROFILE);
    const user = response.data;
    
    this.state.user = user;
    this.saveToStorage();
    this.notifyListeners();
    
    return user;
  }

  // Atualizar perfil
  async updateProfile(updates: Partial<User>): Promise<User> {
    const response = await ApiClient.put<User>(AUTH_ENDPOINTS.UPDATE_PROFILE, updates);
    const user = response.data;
    
    this.state.user = user;
    this.saveToStorage();
    this.notifyListeners();
    
    return user;
  }

  // Alterar senha
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await ApiClient.post(AUTH_ENDPOINTS.CHANGE_PASSWORD, {
      currentPassword,
      newPassword,
    });
  }

  // Esqueci a senha
  async forgotPassword(email: string): Promise<void> {
    await ApiClient.post(AUTH_ENDPOINTS.FORGOT_PASSWORD, { email });
  }

  // Resetar senha
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await ApiClient.post(AUTH_ENDPOINTS.RESET_PASSWORD, {
      token,
      newPassword,
    });
  }

  // Verificar email
  async verifyEmail(token: string): Promise<void> {
    await ApiClient.post(AUTH_ENDPOINTS.VERIFY_EMAIL, { token });
  }

  // Limpar estado de autenticação
  private clearAuthState(): void {
    this.state = {
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      lastActivity: Date.now(),
    };

    this.clearStorage();
    this.retryCount = 0;

    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }

    this.notifyListeners();
  }

  // Lidar com logout em múltiplas abas
  private handleMultiTabLogout(): void {
    this.clearAuthState();
    localStorage.removeItem('authLogout');
  }

  // Auditoria de login
  private auditLogin(user: User, options: LoginOptions): void {
    const auditData = {
      userId: user.id,
      email: user.email,
      provider: options.provider,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      ip: null, // Será preenchido pelo backend
    };

    // Enviar para endpoint de auditoria (se disponível)
    ApiClient.post('/api/audit/login', auditData).catch(error => {
      console.error('Erro ao registrar auditoria de login:', error);
    });
  }

  // Getters
  get isAuthenticated(): boolean {
    return this.state.isAuthenticated;
  }

  get user(): User | null {
    return this.state.user;
  }

  get token(): string | null {
    return this.state.token;
  }

  get isLoading(): boolean {
    return this.state.isLoading;
  }

  get state(): AuthState {
    return { ...this.state };
  }

  // Listeners
  subscribe(listener: (state: AuthState) => void): () => void {
    this.listeners.add(listener);
    
    // Retornar função para unsubscribe
    return () => {
      this.listeners.delete(listener);
    };
  }

  // Utilitários
  hasPermission(permission: string): boolean {
    return this.state.user?.permissions.includes(permission) || false;
  }

  hasRole(role: string): boolean {
    return this.state.user?.role === role;
  }

  isTokenExpired(): boolean {
    return this.state.token ? !this.isTokenValid(this.state.token) : true;
  }

  getTokenExpirationTime(): number | null {
    return this.state.token ? this.getTokenExpiration(this.state.token) : null;
  }

  // Cleanup
  destroy(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }
    
    if (this.sessionTimer) {
      clearInterval(this.sessionTimer);
    }
    
    this.listeners.clear();
  }
}

// Instância singleton
export const authService = new AuthService();

export default authService; 