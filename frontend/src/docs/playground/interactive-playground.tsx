/**
 * Playground Interativo - Hooks e Stores
 * 
 * Prompt: Criar playground interativo
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: PLAYGROUND_INTERACTIVE_20250127_001
 */

import React, { useState, useEffect } from 'react';
import { useApiClient, useApiQuery, useApiMutation, useWebSocket } from '@/hooks';
import { useAuth } from '@/hooks/useAuth';
import { useLocalStorage, useDebounce, useThrottle } from '@/hooks/utils';

// ============================================================================
// COMPONENTE PRINCIPAL DO PLAYGROUND
// ============================================================================

export const InteractivePlayground: React.FC = () => {
  const [activeTab, setActiveTab] = useState('api');
  const [playgroundData, setPlaygroundData] = useState({
    apiEndpoint: '/api/users',
    apiMethod: 'GET',
    apiPayload: '{}',
    websocketUrl: 'wss://echo.websocket.org',
    websocketMessage: 'Hello WebSocket!',
    localStorageKey: 'playground-data',
    localStorageValue: 'Test Value',
    debounceValue: '',
    throttleValue: ''
  });

  return (
    <div className="playground-container">
      <header className="playground-header">
        <h1>🧪 Playground Interativo - Hooks e Stores</h1>
        <p>Teste todos os hooks e stores em tempo real</p>
      </header>

      <nav className="playground-nav">
        <button 
          className={activeTab === 'api' ? 'active' : ''}
          onClick={() => setActiveTab('api')}
        >
          🔌 API Hooks
        </button>
        <button 
          className={activeTab === 'websocket' ? 'active' : ''}
          onClick={() => setActiveTab('websocket')}
        >
          🌐 WebSocket
        </button>
        <button 
          className={activeTab === 'auth' ? 'active' : ''}
          onClick={() => setActiveTab('auth')}
        >
          🔐 Autenticação
        </button>
        <button 
          className={activeTab === 'storage' ? 'active' : ''}
          onClick={() => setActiveTab('storage')}
        >
          💾 LocalStorage
        </button>
        <button 
          className={activeTab === 'utils' ? 'active' : ''}
          onClick={() => setActiveTab('utils')}
        >
          🛠️ Utilitários
        </button>
      </nav>

      <main className="playground-content">
        {activeTab === 'api' && (
          <ApiPlayground 
            data={playgroundData} 
            setData={setPlaygroundData} 
          />
        )}
        {activeTab === 'websocket' && (
          <WebSocketPlayground 
            data={playgroundData} 
            setData={setPlaygroundData} 
          />
        )}
        {activeTab === 'auth' && (
          <AuthPlayground 
            data={playgroundData} 
            setData={setPlaygroundData} 
          />
        )}
        {activeTab === 'storage' && (
          <StoragePlayground 
            data={playgroundData} 
            setData={setPlaygroundData} 
          />
        )}
        {activeTab === 'utils' && (
          <UtilsPlayground 
            data={playgroundData} 
            setData={setPlaygroundData} 
          />
        )}
      </main>

      <footer className="playground-footer">
        <p>Tracing ID: PLAYGROUND_20250127_001 | Versão: 1.0.0</p>
      </footer>
    </div>
  );
};

// ============================================================================
// PLAYGROUND DE API
// ============================================================================

const ApiPlayground: React.FC<{
  data: any;
  setData: (data: any) => void;
}> = ({ data, setData }) => {
  const [queryResult, setQueryResult] = useState<any>(null);
  const [mutationResult, setMutationResult] = useState<any>(null);

  // API Query
  const { data: queryData, isLoading: queryLoading, error: queryError } = useApiQuery(
    data.apiEndpoint,
    {
      enabled: false, // Não executar automaticamente
      retry: 1
    }
  );

  // API Mutation
  const { mutate: executeMutation, isLoading: mutationLoading, error: mutationError } = useApiMutation(
    data.apiEndpoint,
    {
      method: data.apiMethod as any,
      onSuccess: (result) => {
        setMutationResult(result);
      },
      onError: (error) => {
        setMutationResult({ error: error.message });
      }
    }
  );

  const handleQuery = () => {
    // Simular query
    setQueryResult({
      data: [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ],
      timestamp: new Date().toISOString()
    });
  };

  const handleMutation = () => {
    try {
      const payload = JSON.parse(data.apiPayload);
      executeMutation(payload);
    } catch (error) {
      setMutationResult({ error: 'Payload JSON inválido' });
    }
  };

  return (
    <div className="playground-section">
      <h2>🔌 API Hooks Playground</h2>
      
      <div className="playground-controls">
        <div className="control-group">
          <label>Endpoint:</label>
          <input
            type="text"
            value={data.apiEndpoint}
            onChange={(e) => setData({ ...data, apiEndpoint: e.target.value })}
            placeholder="/api/users"
          />
        </div>

        <div className="control-group">
          <label>Método:</label>
          <select
            value={data.apiMethod}
            onChange={(e) => setData({ ...data, apiMethod: e.target.value })}
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>

        <div className="control-group">
          <label>Payload (JSON):</label>
          <textarea
            value={data.apiPayload}
            onChange={(e) => setData({ ...data, apiPayload: e.target.value })}
            placeholder='{"name": "John", "email": "john@example.com"}'
            rows={4}
          />
        </div>

        <div className="control-buttons">
          <button onClick={handleQuery} disabled={queryLoading}>
            {queryLoading ? 'Executando...' : 'Testar Query'}
          </button>
          <button onClick={handleMutation} disabled={mutationLoading}>
            {mutationLoading ? 'Executando...' : 'Testar Mutation'}
          </button>
        </div>
      </div>

      <div className="playground-results">
        <div className="result-section">
          <h3>Query Result:</h3>
          <pre>{JSON.stringify(queryResult, null, 2)}</pre>
        </div>

        <div className="result-section">
          <h3>Mutation Result:</h3>
          <pre>{JSON.stringify(mutationResult, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// PLAYGROUND DE WEBSOCKET
// ============================================================================

const WebSocketPlayground: React.FC<{
  data: any;
  setData: (data: any) => void;
}> = ({ data, setData }) => {
  const [messages, setMessages] = useState<Array<{id: string, text: string, timestamp: string}>>([]);
  const [isConnected, setIsConnected] = useState(false);

  const { send, lastMessage, readyState, connect, disconnect } = useWebSocket(
    data.websocketUrl,
    {
      onOpen: () => {
        setIsConnected(true);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          text: 'Conectado ao WebSocket',
          timestamp: new Date().toISOString()
        }]);
      },
      onClose: () => {
        setIsConnected(false);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          text: 'Desconectado do WebSocket',
          timestamp: new Date().toISOString()
        }]);
      },
      onError: (error) => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          text: `Erro: ${error.message}`,
          timestamp: new Date().toISOString()
        }]);
      }
    }
  );

  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: `Recebido: ${lastMessage.data}`,
        timestamp: new Date().toISOString()
      }]);
    }
  }, [lastMessage]);

  const handleSend = () => {
    if (data.websocketMessage.trim()) {
      send(data.websocketMessage);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: `Enviado: ${data.websocketMessage}`,
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const handleConnect = () => {
    connect();
  };

  const handleDisconnect = () => {
    disconnect();
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <div className="playground-section">
      <h2>🌐 WebSocket Playground</h2>
      
      <div className="playground-controls">
        <div className="control-group">
          <label>WebSocket URL:</label>
          <input
            type="text"
            value={data.websocketUrl}
            onChange={(e) => setData({ ...data, websocketUrl: e.target.value })}
            placeholder="wss://echo.websocket.org"
          />
        </div>

        <div className="control-group">
          <label>Mensagem:</label>
          <input
            type="text"
            value={data.websocketMessage}
            onChange={(e) => setData({ ...data, websocketMessage: e.target.value })}
            placeholder="Digite sua mensagem..."
          />
        </div>

        <div className="control-buttons">
          <button onClick={handleConnect} disabled={isConnected}>
            Conectar
          </button>
          <button onClick={handleDisconnect} disabled={!isConnected}>
            Desconectar
          </button>
          <button onClick={handleSend} disabled={!isConnected}>
            Enviar
          </button>
          <button onClick={clearMessages}>
            Limpar Mensagens
          </button>
        </div>

        <div className="status-indicator">
          Status: {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
        </div>
      </div>

      <div className="playground-results">
        <h3>Mensagens:</h3>
        <div className="messages-container">
          {messages.map(msg => (
            <div key={msg.id} className="message">
              <span className="timestamp">{msg.timestamp}</span>
              <span className="text">{msg.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// PLAYGROUND DE AUTENTICAÇÃO
// ============================================================================

const AuthPlayground: React.FC<{
  data: any;
  setData: (data: any) => void;
}> = ({ data, setData }) => {
  const [credentials, setCredentials] = useState({
    email: 'test@example.com',
    password: 'password123'
  });

  const { user, isAuthenticated, login, logout } = useAuth();

  const handleLogin = () => {
    login(credentials);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="playground-section">
      <h2>🔐 Autenticação Playground</h2>
      
      <div className="playground-controls">
        <div className="control-group">
          <label>Email:</label>
          <input
            type="email"
            value={credentials.email}
            onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
            placeholder="test@example.com"
          />
        </div>

        <div className="control-group">
          <label>Senha:</label>
          <input
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
            placeholder="password123"
          />
        </div>

        <div className="control-buttons">
          <button onClick={handleLogin} disabled={isAuthenticated}>
            Login
          </button>
          <button onClick={handleLogout} disabled={!isAuthenticated}>
            Logout
          </button>
        </div>

        <div className="status-indicator">
          Status: {isAuthenticated ? '🟢 Autenticado' : '🔴 Não autenticado'}
        </div>
      </div>

      <div className="playground-results">
        <h3>Dados do Usuário:</h3>
        <pre>{JSON.stringify(user, null, 2)}</pre>
      </div>
    </div>
  );
};

// ============================================================================
// PLAYGROUND DE LOCALSTORAGE
// ============================================================================

const StoragePlayground: React.FC<{
  data: any;
  setData: (data: any) => void;
}> = ({ data, setData }) => {
  const [storedValue, setStoredValue] = useLocalStorage(data.localStorageKey, '');
  const [allKeys, setAllKeys] = useState<string[]>([]);

  useEffect(() => {
    // Listar todas as chaves do localStorage
    const keys = Object.keys(localStorage);
    setAllKeys(keys);
  }, [storedValue]);

  const handleSave = () => {
    setStoredValue(data.localStorageValue);
  };

  const handleDelete = () => {
    localStorage.removeItem(data.localStorageKey);
    setStoredValue('');
  };

  const handleClearAll = () => {
    localStorage.clear();
    setStoredValue('');
    setAllKeys([]);
  };

  return (
    <div className="playground-section">
      <h2>💾 LocalStorage Playground</h2>
      
      <div className="playground-controls">
        <div className="control-group">
          <label>Chave:</label>
          <input
            type="text"
            value={data.localStorageKey}
            onChange={(e) => setData({ ...data, localStorageKey: e.target.value })}
            placeholder="minha-chave"
          />
        </div>

        <div className="control-group">
          <label>Valor:</label>
          <input
            type="text"
            value={data.localStorageValue}
            onChange={(e) => setData({ ...data, localStorageValue: e.target.value })}
            placeholder="meu-valor"
          />
        </div>

        <div className="control-buttons">
          <button onClick={handleSave}>
            Salvar
          </button>
          <button onClick={handleDelete}>
            Deletar
          </button>
          <button onClick={handleClearAll}>
            Limpar Tudo
          </button>
        </div>
      </div>

      <div className="playground-results">
        <div className="result-section">
          <h3>Valor Armazenado:</h3>
          <pre>{storedValue || '(vazio)'}</pre>
        </div>

        <div className="result-section">
          <h3>Todas as Chaves:</h3>
          <ul>
            {allKeys.map(key => (
              <li key={key}>{key}: {localStorage.getItem(key)}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// PLAYGROUND DE UTILITÁRIOS
// ============================================================================

const UtilsPlayground: React.FC<{
  data: any;
  setData: (data: any) => void;
}> = ({ data, setData }) => {
  const [debounceResult, setDebounceResult] = useState('');
  const [throttleResult, setThrottleResult] = useState('');
  const [throttleCount, setThrottleCount] = useState(0);

  const debouncedValue = useDebounce(data.debounceValue, 500);
  const throttledFunction = useThrottle(() => {
    setThrottleCount(prev => prev + 1);
    setThrottleResult(`Throttled: ${new Date().toISOString()}`);
  }, 1000);

  useEffect(() => {
    setDebounceResult(`Debounced: ${debouncedValue}`);
  }, [debouncedValue]);

  const handleThrottleTest = () => {
    throttledFunction();
  };

  return (
    <div className="playground-section">
      <h2>🛠️ Utilitários Playground</h2>
      
      <div className="playground-controls">
        <div className="control-group">
          <label>Debounce Test:</label>
          <input
            type="text"
            value={data.debounceValue}
            onChange={(e) => setData({ ...data, debounceValue: e.target.value })}
            placeholder="Digite para testar debounce..."
          />
        </div>

        <div className="control-group">
          <label>Throttle Test:</label>
          <button onClick={handleThrottleTest}>
            Clicar para testar throttle
          </button>
        </div>
      </div>

      <div className="playground-results">
        <div className="result-section">
          <h3>Debounce Result:</h3>
          <pre>{debounceResult || '(aguardando...)'}</pre>
        </div>

        <div className="result-section">
          <h3>Throttle Result:</h3>
          <pre>{throttleResult || '(aguardando...)'}</pre>
          <p>Contador: {throttleCount}</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// ESTILOS CSS INLINE
// ============================================================================

const playgroundStyles = `
  .playground-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .playground-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .playground-header h1 {
    color: #333;
    margin-bottom: 10px;
  }

  .playground-nav {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }

  .playground-nav button {
    padding: 10px 20px;
    border: 2px solid #ddd;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
  }

  .playground-nav button.active {
    border-color: #007bff;
    background: #007bff;
    color: white;
  }

  .playground-section {
    background: white;
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 20px;
  }

  .playground-section h2 {
    color: #333;
    margin-bottom: 20px;
  }

  .playground-controls {
    margin-bottom: 30px;
  }

  .control-group {
    margin-bottom: 15px;
  }

  .control-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #555;
  }

  .control-group input,
  .control-group select,
  .control-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }

  .control-group textarea {
    resize: vertical;
    min-height: 80px;
  }

  .control-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
  }

  .control-buttons button {
    padding: 10px 20px;
    border: none;
    background: #007bff;
    color: white;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.3s;
  }

  .control-buttons button:hover {
    background: #0056b3;
  }

  .control-buttons button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .status-indicator {
    margin-top: 15px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
    font-weight: 600;
  }

  .playground-results {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
  }

  .result-section {
    margin-bottom: 20px;
  }

  .result-section h3 {
    color: #333;
    margin-bottom: 10px;
  }

  .result-section pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 12px;
  }

  .messages-container {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 10px;
  }

  .message {
    padding: 8px;
    border-bottom: 1px solid #eee;
    display: flex;
    gap: 10px;
  }

  .message:last-child {
    border-bottom: none;
  }

  .timestamp {
    color: #666;
    font-size: 12px;
    min-width: 150px;
  }

  .text {
    flex: 1;
  }

  .playground-footer {
    text-align: center;
    margin-top: 30px;
    padding: 20px;
    color: #666;
    border-top: 1px solid #ddd;
  }

  @media (max-width: 768px) {
    .playground-nav {
      flex-direction: column;
    }
    
    .control-buttons {
      flex-direction: column;
    }
  }
`;

// ============================================================================
// COMPONENTE COM ESTILOS
// ============================================================================

export const StyledInteractivePlayground: React.FC = () => {
  useEffect(() => {
    // Injetar estilos
    const style = document.createElement('style');
    style.textContent = playgroundStyles;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return <InteractivePlayground />;
};

export default StyledInteractivePlayground; 