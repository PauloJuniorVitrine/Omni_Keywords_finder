/**
 * Exemplos de Uso - Hooks e Stores
 * 
 * Prompt: Criar exemplos de uso
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: EXAMPLES_USAGE_20250127_001
 */

import React, { useState, useEffect } from 'react';
import { useApiClient, useApiQuery, useApiMutation, useWebSocket } from '@/hooks';
import { useAuth } from '@/hooks/useAuth';
import { useLocalStorage, useDebounce, useThrottle } from '@/hooks/utils';

// ============================================================================
// EXEMPLO 1: COMPONENTE DE LISTA DE USUÁRIOS COM API
// ============================================================================

export const UserListExample: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);
  
  // Query para buscar usuários
  const { 
    data: users, 
    loading, 
    error, 
    refetch 
  } = useApiQuery(`/api/users?search=${debouncedSearch}`, {
    cacheTime: 300000, // 5 minutos
    staleTime: 60000,  // 1 minuto
    refetchOnWindowFocus: true
  });

  // Mutation para deletar usuário
  const { mutate: deleteUser, loading: deleting } = useApiMutation('/api/users', {
    method: 'DELETE',
    onSuccess: () => {
      refetch(); // Reexecutar query após deletar
    }
  });

  const handleDelete = (userId: string) => {
    deleteUser({ id: userId });
  };

  if (loading) return <div>Carregando usuários...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  return (
    <div>
      <input
        type="text"
        placeholder="Buscar usuários..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      <div>
        {users?.map(user => (
          <div key={user.id}>
            <span>{user.name}</span>
            <button 
              onClick={() => handleDelete(user.id)}
              disabled={deleting}
            >
              {deleting ? 'Deletando...' : 'Deletar'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// EXEMPLO 2: FORMULÁRIO DE LOGIN COM AUTENTICAÇÃO
// ============================================================================

export const LoginFormExample: React.FC = () => {
  const { login, isAuthenticated, user } = useAuth();
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });

  const { mutate: submitLogin, loading, error } = useApiMutation('/api/auth/login', {
    method: 'POST',
    onSuccess: (data) => {
      login(data.token);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitLogin(credentials);
  };

  if (isAuthenticated) {
    return <div>Bem-vindo, {user?.name}!</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={credentials.email}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          email: e.target.value
        }))}
      />
      
      <input
        type="password"
        placeholder="Senha"
        value={credentials.password}
        onChange={(e) => setCredentials(prev => ({
          ...prev,
          password: e.target.value
        }))}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Entrando...' : 'Entrar'}
      </button>
      
      {error && <div>Erro: {error.message}</div>}
    </form>
  );
};

// ============================================================================
// EXEMPLO 3: CHAT EM TEMPO REAL COM WEBSOCKET
// ============================================================================

export const ChatExample: React.FC = () => {
  const [messages, setMessages] = useState<Array<{id: string, text: string, user: string}>>([]);
  const [newMessage, setNewMessage] = useState('');
  
  const { send, lastMessage, readyState, connect, disconnect } = useWebSocket(
    'wss://api.example.com/chat',
    {
      reconnectInterval: 3000,
      heartbeatInterval: 30000
    }
  );

  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage.data);
      setMessages(prev => [...prev, message]);
    }
  }, [lastMessage]);

  const handleSend = () => {
    if (newMessage.trim()) {
      send(JSON.stringify({
        text: newMessage,
        timestamp: new Date().toISOString()
      }));
      setNewMessage('');
    }
  };

  return (
    <div>
      <div>
        Status: {readyState === 1 ? 'Conectado' : 'Desconectado'}
        <button onClick={connect}>Conectar</button>
        <button onClick={disconnect}>Desconectar</button>
      </div>
      
      <div style={{ height: '300px', overflow: 'auto' }}>
        {messages.map(msg => (
          <div key={msg.id}>
            <strong>{msg.user}:</strong> {msg.text}
          </div>
        ))}
      </div>
      
      <div>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Enviar</button>
      </div>
    </div>
  );
};

// ============================================================================
// EXEMPLO 4: CONFIGURAÇÕES PERSISTENTES
// ============================================================================

export const SettingsExample: React.FC = () => {
  const [settings, setSettings] = useLocalStorage('app-settings', {
    theme: 'light',
    language: 'pt-BR',
    notifications: true,
    autoSave: true
  });

  const { mutate: updateSettings, loading } = useApiMutation('/api/settings', {
    method: 'PUT',
    onSuccess: () => {
      console.log('Configurações salvas no servidor');
    }
  });

  const handleSettingChange = (key: string, value: any) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    updateSettings(newSettings);
  };

  return (
    <div>
      <h3>Configurações</h3>
      
      <div>
        <label>
          Tema:
          <select
            value={settings.theme}
            onChange={(e) => handleSettingChange('theme', e.target.value)}
          >
            <option value="light">Claro</option>
            <option value="dark">Escuro</option>
          </select>
        </label>
      </div>
      
      <div>
        <label>
          Idioma:
          <select
            value={settings.language}
            onChange={(e) => handleSettingChange('language', e.target.value)}
          >
            <option value="pt-BR">Português</option>
            <option value="en-US">English</option>
          </select>
        </label>
      </div>
      
      <div>
        <label>
          <input
            type="checkbox"
            checked={settings.notifications}
            onChange={(e) => handleSettingChange('notifications', e.target.checked)}
          />
          Notificações
        </label>
      </div>
      
      <div>
        <label>
          <input
            type="checkbox"
            checked={settings.autoSave}
            onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
          />
          Auto-save
        </label>
      </div>
      
      {loading && <div>Salvando...</div>}
    </div>
  );
};

// ============================================================================
// EXEMPLO 5: SCROLL INFINITO COM THROTTLE
// ============================================================================

export const InfiniteScrollExample: React.FC = () => {
  const [items, setItems] = useState<Array<{id: string, title: string}>>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const { data: newItems, loading } = useApiQuery(`/api/items?page=${page}`, {
    cacheTime: 600000, // 10 minutos
    enabled: hasMore
  });

  const throttledLoadMore = useThrottle(() => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  }, 500);

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
        throttledLoadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [throttledLoadMore]);

  useEffect(() => {
    if (newItems) {
      setItems(prev => [...prev, ...newItems]);
      setHasMore(newItems.length > 0);
    }
  }, [newItems]);

  return (
    <div>
      {items.map(item => (
        <div key={item.id}>
          <h3>{item.title}</h3>
        </div>
      ))}
      
      {loading && <div>Carregando mais itens...</div>}
      {!hasMore && <div>Não há mais itens</div>}
    </div>
  );
};

// ============================================================================
// EXEMPLO 6: UPLOAD DE ARQUIVOS COM PROGRESSO
// ============================================================================

export const FileUploadExample: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  
  const { mutate: uploadFile, loading } = useApiMutation('/api/upload', {
    method: 'POST',
    onUploadProgress: (progressEvent) => {
      const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      setUploadProgress(prev => ({
        ...prev,
        [progressEvent.target?.responseURL || '']: progress
      }));
    }
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      
      uploadFile(formData);
    }
  };

  return (
    <div>
      <input
        type="file"
        multiple
        onChange={handleFileSelect}
      />
      
      <button onClick={handleUpload} disabled={loading || files.length === 0}>
        {loading ? 'Enviando...' : 'Enviar Arquivos'}
      </button>
      
      <div>
        {files.map(file => (
          <div key={file.name}>
            {file.name} - {uploadProgress[file.name] || 0}%
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// EXEMPLO 7: DASHBOARD COM MÚLTIPLAS QUERIES
// ============================================================================

export const DashboardExample: React.FC = () => {
  // Múltiplas queries para dashboard
  const { data: stats } = useApiQuery('/api/dashboard/stats');
  const { data: recentActivity } = useApiQuery('/api/dashboard/activity');
  const { data: charts } = useApiQuery('/api/dashboard/charts');
  
  const { mutate: refreshData } = useApiMutation('/api/dashboard/refresh', {
    method: 'POST',
    onSuccess: () => {
      // Reexecutar todas as queries
      window.location.reload();
    }
  });

  return (
    <div>
      <h2>Dashboard</h2>
      
      <button onClick={() => refreshData()}>
        Atualizar Dados
      </button>
      
      <div>
        <h3>Estatísticas</h3>
        {stats && (
          <div>
            <div>Usuários: {stats.totalUsers}</div>
            <div>Ativos: {stats.activeUsers}</div>
            <div>Receita: R$ {stats.revenue}</div>
          </div>
        )}
      </div>
      
      <div>
        <h3>Atividade Recente</h3>
        {recentActivity?.map(activity => (
          <div key={activity.id}>
            {activity.description} - {activity.timestamp}
          </div>
        ))}
      </div>
      
      <div>
        <h3>Gráficos</h3>
        {charts && (
          <div>
            {/* Renderizar gráficos */}
            <div>Gráfico de Vendas</div>
            <div>Gráfico de Usuários</div>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// EXEMPLO 8: COMPONENTE COM CACHE PERSONALIZADO
// ============================================================================

export const CachedDataExample: React.FC = () => {
  const apiClient = useApiClient();
  const [cacheKey, setCacheKey] = useState('user-data');
  
  const { data, loading, error } = useApiQuery(`/api/data/${cacheKey}`, {
    cacheTime: 300000, // 5 minutos
    staleTime: 60000,  // 1 minuto
    refetchOnMount: false,
    refetchOnWindowFocus: false
  });

  const clearCache = () => {
    apiClient.clearCache();
  };

  return (
    <div>
      <div>
        <input
          type="text"
          value={cacheKey}
          onChange={(e) => setCacheKey(e.target.value)}
          placeholder="Chave do cache"
        />
        <button onClick={clearCache}>Limpar Cache</button>
      </div>
      
      {loading && <div>Carregando...</div>}
      {error && <div>Erro: {error.message}</div>}
      {data && (
        <div>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// EXEMPLO 9: FORMULÁRIO COM VALIDAÇÃO E OPTIMISTIC UPDATE
// ============================================================================

export const FormWithOptimisticUpdateExample: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  
  const { mutate: saveUser, loading } = useApiMutation('/api/users', {
    method: 'POST',
    optimisticUpdate: (newData) => {
      // Atualizar cache otimisticamente
      console.log('Dados salvos otimisticamente:', newData);
    },
    onSuccess: (data) => {
      console.log('Dados salvos com sucesso:', data);
      setFormData({ name: '', email: '', phone: '' });
    },
    onError: (error) => {
      console.error('Erro ao salvar:', error);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveUser(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Nome:</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            name: e.target.value
          }))}
          required
        />
      </div>
      
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            email: e.target.value
          }))}
          required
        />
      </div>
      
      <div>
        <label>Telefone:</label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            phone: e.target.value
          }))}
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Salvando...' : 'Salvar'}
      </button>
    </form>
  );
};

// ============================================================================
// EXEMPLO 10: COMPONENTE COM RETRY AUTOMÁTICO
// ============================================================================

export const RetryExample: React.FC = () => {
  const { data, loading, error, refetch } = useApiQuery('/api/unreliable-endpoint', {
    retry: 3,
    retryDelay: 1000,
    retryOnMount: true
  });

  return (
    <div>
      <h3>Teste de Retry Automático</h3>
      
      <button onClick={() => refetch()}>
        Tentar Novamente
      </button>
      
      {loading && <div>Carregando...</div>}
      {error && <div>Erro: {error.message}</div>}
      {data && (
        <div>
          <h4>Dados carregados com sucesso:</h4>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// EXPORTAÇÃO DE TODOS OS EXEMPLOS
// ============================================================================

export const Examples = {
  UserList: UserListExample,
  LoginForm: LoginFormExample,
  Chat: ChatExample,
  Settings: SettingsExample,
  InfiniteScroll: InfiniteScrollExample,
  FileUpload: FileUploadExample,
  Dashboard: DashboardExample,
  CachedData: CachedDataExample,
  FormWithOptimisticUpdate: FormWithOptimisticUpdateExample,
  Retry: RetryExample
};

export default Examples; 