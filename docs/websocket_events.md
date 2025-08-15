# 📡 **DOCUMENTAÇÃO DE EVENTOS WEBSOCKET - OMNİ KEYWORDS FINDER**

**Tracing ID**: `WEBSOCKET_DOCS_001`  
**Data**: 2024-12-19  
**Versão**: 1.0  
**Status**: ✅ **CONCLUÍDO**

---

## 🎯 **RESUMO EXECUTIVO**

Esta documentação descreve todos os eventos WebSocket implementados no sistema Omni Keywords Finder, incluindo:
- Eventos de execução de keywords
- Notificações em tempo real
- Monitoramento de performance
- Controle de sessão
- Integração com frontend

---

## 🔗 **CONFIGURAÇÃO DE CONEXÃO**

### **Endpoint WebSocket**
```
ws://localhost:5000/ws
wss://omni-keywords-finder.com/ws (produção)
```

### **Autenticação**
```javascript
// Conectar com token de autenticação
const ws = new WebSocket('ws://localhost:5000/ws', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
});
```

### **Reconexão Automática**
```javascript
// Implementação recomendada
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:5000/ws');
  
  ws.onclose = () => {
    console.log('WebSocket desconectado. Reconectando...');
    setTimeout(connectWebSocket, 3000);
  };
  
  return ws;
}
```

---

## 📨 **EVENTOS DE ENVIO (Client → Server)**

### **1. EXECUCAO_INICIAR**
Inicia uma nova execução de keywords.

```json
{
  "event": "EXECUCAO_INICIAR",
  "data": {
    "blog_url": "https://exemplo.com",
    "categoria_id": 1,
    "configuracoes": {
      "max_keywords": 100,
      "profundidade": 3,
      "timeout": 30
    },
    "request_id": "req_123456"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

**Resposta Esperada:**
```json
{
  "event": "EXECUCAO_INICIADA",
  "data": {
    "execucao_id": "exec_789012",
    "status": "iniciada",
    "request_id": "req_123456"
  },
  "timestamp": "2024-12-19T23:00:01Z"
}
```

### **2. EXECUCAO_PAUSAR**
Pausa uma execução em andamento.

```json
{
  "event": "EXECUCAO_PAUSAR",
  "data": {
    "execucao_id": "exec_789012",
    "request_id": "req_123457"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

**Resposta Esperada:**
```json
{
  "event": "EXECUCAO_PAUSADA",
  "data": {
    "execucao_id": "exec_789012",
    "status": "pausada",
    "request_id": "req_123457"
  },
  "timestamp": "2024-12-19T23:00:01Z"
}
```

### **3. EXECUCAO_RESUMIR**
Resume uma execução pausada.

```json
{
  "event": "EXECUCAO_RESUMIR",
  "data": {
    "execucao_id": "exec_789012",
    "request_id": "req_123458"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **4. EXECUCAO_CANCELAR**
Cancela uma execução em andamento.

```json
{
  "event": "EXECUCAO_CANCELAR",
  "data": {
    "execucao_id": "exec_789012",
    "request_id": "req_123459"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **5. NOTIFICACAO_CONFIGURAR**
Configura preferências de notificação.

```json
{
  "event": "NOTIFICACAO_CONFIGURAR",
  "data": {
    "tipos": ["execucao_concluida", "erro", "aviso"],
    "canal": "websocket",
    "request_id": "req_123460"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **6. MONITORAMENTO_INICIAR**
Inicia monitoramento de performance.

```json
{
  "event": "MONITORAMENTO_INICIAR",
  "data": {
    "metricas": ["cpu", "memoria", "tempo_resposta"],
    "intervalo": 5000,
    "request_id": "req_123461"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **7. SESSAO_PING**
Mantém a sessão ativa.

```json
{
  "event": "SESSAO_PING",
  "data": {
    "request_id": "req_123462"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

**Resposta Esperada:**
```json
{
  "event": "SESSAO_PONG",
  "data": {
    "request_id": "req_123462",
    "server_time": "2024-12-19T23:00:00Z"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

---

## 📨 **EVENTOS DE RECEPÇÃO (Server → Client)**

### **1. EXECUCAO_STATUS**
Atualização de status de execução.

```json
{
  "event": "EXECUCAO_STATUS",
  "data": {
    "execucao_id": "exec_789012",
    "status": "em_andamento",
    "progresso": {
      "total": 100,
      "atual": 45,
      "percentual": 45.0
    },
    "keywords_encontradas": 23,
    "tempo_decorrido": 120,
    "tempo_estimado": 180
  },
  "timestamp": "2024-12-19T23:02:00Z"
}
```

### **2. KEYWORD_ENCONTRADA**
Nova keyword encontrada durante execução.

```json
{
  "event": "KEYWORD_ENCONTRADA",
  "data": {
    "execucao_id": "exec_789012",
    "keyword": {
      "termo": "palavra-chave",
      "frequencia": 15,
      "relevancia": 0.85,
      "posicao": 3,
      "url": "https://exemplo.com/pagina"
    },
    "cluster_id": "cluster_123"
  },
  "timestamp": "2024-12-19T23:02:15Z"
}
```

### **3. CLUSTER_FORMADO**
Novo cluster de keywords formado.

```json
{
  "event": "CLUSTER_FORMADO",
  "data": {
    "execucao_id": "exec_789012",
    "cluster": {
      "id": "cluster_123",
      "nome": "Tecnologia",
      "keywords": ["tech", "tecnologia", "inovação"],
      "tamanho": 3,
      "relevancia_media": 0.78
    }
  },
  "timestamp": "2024-12-19T23:02:30Z"
}
```

### **4. EXECUCAO_CONCLUIDA**
Execução finalizada com sucesso.

```json
{
  "event": "EXECUCAO_CONCLUIDA",
  "data": {
    "execucao_id": "exec_789012",
    "resultado": {
      "total_keywords": 156,
      "clusters_formados": 12,
      "tempo_total": 300,
      "taxa_sucesso": 0.95
    },
    "download_url": "https://api.exemplo.com/download/exec_789012"
  },
  "timestamp": "2024-12-19T23:05:00Z"
}
```

### **5. EXECUCAO_ERRO**
Erro durante execução.

```json
{
  "event": "EXECUCAO_ERRO",
  "data": {
    "execucao_id": "exec_789012",
    "erro": {
      "codigo": "TIMEOUT_ERROR",
      "mensagem": "Timeout ao processar URL",
      "detalhes": {
        "url": "https://exemplo.com/pagina-lenta",
        "timeout": 30
      }
    },
    "recomendacao": "Aumentar timeout ou verificar conectividade"
  },
  "timestamp": "2024-12-19T23:03:00Z"
}
```

### **6. NOTIFICACAO_GERAL**
Notificação geral do sistema.

```json
{
  "event": "NOTIFICACAO_GERAL",
  "data": {
    "tipo": "info",
    "titulo": "Sistema Atualizado",
    "mensagem": "Nova versão disponível com melhorias de performance",
    "acao": {
      "tipo": "link",
      "url": "https://exemplo.com/changelog"
    }
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **7. METRICA_PERFORMANCE**
Métrica de performance em tempo real.

```json
{
  "event": "METRICA_PERFORMANCE",
  "data": {
    "cpu_uso": 45.2,
    "memoria_uso": 67.8,
    "tempo_resposta_medio": 125,
    "requisicoes_por_segundo": 12.5,
    "execucoes_ativas": 3
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

### **8. SISTEMA_ALERTA**
Alerta do sistema.

```json
{
  "event": "SISTEMA_ALERTA",
  "data": {
    "nivel": "warning",
    "categoria": "performance",
    "mensagem": "Uso de CPU acima de 80%",
    "acoes": [
      "Reduzir número de execuções simultâneas",
      "Verificar processos em background"
    ]
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

---

## 🔄 **ESTADOS DE EXECUÇÃO**

### **Fluxo de Estados**
```
INICIADA → EM_ANDAMENTO → PAUSADA → EM_ANDAMENTO → CONCLUIDA
     ↓           ↓           ↓           ↓           ↓
  PAUSADA    PAUSADA    CANCELADA   CANCLUIDA   ERRO
     ↓           ↓           ↓           ↓
  CANCELADA  CANCELADA    ERRO       ERRO
     ↓           ↓
    ERRO       ERRO
```

### **Códigos de Status**
- `iniciada`: Execução foi iniciada
- `em_andamento`: Execução está processando
- `pausada`: Execução foi pausada pelo usuário
- `concluida`: Execução finalizada com sucesso
- `cancelada`: Execução foi cancelada pelo usuário
- `erro`: Execução falhou com erro

---

## ⚠️ **CÓDIGOS DE ERRO**

### **Códigos de Erro Comuns**
- `AUTHENTICATION_ERROR`: Token inválido ou expirado
- `PERMISSION_ERROR`: Usuário sem permissão
- `VALIDATION_ERROR`: Dados de entrada inválidos
- `TIMEOUT_ERROR`: Timeout na operação
- `NETWORK_ERROR`: Erro de conectividade
- `RATE_LIMIT_ERROR`: Limite de requisições excedido
- `SYSTEM_ERROR`: Erro interno do sistema

### **Exemplo de Erro**
```json
{
  "event": "ERRO",
  "data": {
    "codigo": "AUTHENTICATION_ERROR",
    "mensagem": "Token de autenticação inválido",
    "detalhes": {
      "token_expira_em": "2024-12-19T23:30:00Z"
    },
    "recomendacao": "Renovar token de autenticação"
  },
  "timestamp": "2024-12-19T23:00:00Z"
}
```

---

## 🔧 **IMPLEMENTAÇÃO NO FRONTEND**

### **Classe WebSocket Manager**
```javascript
class WebSocketManager {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.listeners = new Map();
  }

  connect() {
    this.ws = new WebSocket(this.url, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });

    this.ws.onopen = () => {
      console.log('WebSocket conectado');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log('WebSocket desconectado');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('Erro WebSocket:', error);
    };
  }

  handleMessage(data) {
    const { event, data: eventData } = data;
    
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        callback(eventData);
      });
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  send(event, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        event,
        data,
        timestamp: new Date().toISOString()
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      
      setTimeout(() => {
        this.connect();
      }, 3000 * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
```

### **Uso no React**
```javascript
import { useEffect, useState } from 'react';

function useWebSocket(url, token) {
  const [wsManager, setWsManager] = useState(null);
  const [execucoes, setExecucoes] = useState([]);
  const [notificacoes, setNotificacoes] = useState([]);

  useEffect(() => {
    const manager = new WebSocketManager(url, token);
    
    // Configurar listeners
    manager.on('EXECUCAO_STATUS', (data) => {
      setExecucoes(prev => 
        prev.map(exec => 
          exec.id === data.execucao_id 
            ? { ...exec, ...data }
            : exec
        )
      );
    });

    manager.on('NOTIFICACAO_GERAL', (data) => {
      setNotificacoes(prev => [...prev, data]);
    });

    manager.on('EXECUCAO_CONCLUIDA', (data) => {
      // Atualizar estado da execução
      setExecucoes(prev => 
        prev.map(exec => 
          exec.id === data.execucao_id 
            ? { ...exec, status: 'concluida', resultado: data.resultado }
            : exec
        )
      );
    });

    manager.connect();
    setWsManager(manager);

    return () => {
      manager.disconnect();
    };
  }, [url, token]);

  const iniciarExecucao = (dados) => {
    wsManager?.send('EXECUCAO_INICIAR', dados);
  };

  const pausarExecucao = (execucaoId) => {
    wsManager?.send('EXECUCAO_PAUSAR', { execucao_id: execucaoId });
  };

  return {
    execucoes,
    notificacoes,
    iniciarExecucao,
    pausarExecucao
  };
}
```

---

## 🧪 **TESTES**

### **Teste de Conexão**
```javascript
// Teste básico de conexão
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onopen = () => {
  console.log('Conexão estabelecida');
  
  // Enviar ping
  ws.send(JSON.stringify({
    event: 'SESSAO_PING',
    data: { request_id: 'test_001' },
    timestamp: new Date().toISOString()
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Mensagem recebida:', data);
  
  if (data.event === 'SESSAO_PONG') {
    console.log('Ping/Pong funcionando');
    ws.close();
  }
};
```

### **Teste de Execução**
```javascript
// Teste de execução completa
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onopen = () => {
  // Iniciar execução
  ws.send(JSON.stringify({
    event: 'EXECUCAO_INICIAR',
    data: {
      blog_url: 'https://exemplo.com',
      categoria_id: 1,
      configuracoes: {
        max_keywords: 10,
        profundidade: 2
      },
      request_id: 'test_exec_001'
    },
    timestamp: new Date().toISOString()
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evento:', data.event, data.data);
  
  // Monitorar progresso
  if (data.event === 'EXECUCAO_STATUS') {
    console.log(`Progresso: ${data.data.progresso.percentual}%`);
  }
  
  // Verificar conclusão
  if (data.event === 'EXECUCAO_CONCLUIDA') {
    console.log('Execução concluída!');
    ws.close();
  }
};
```

---

## 📊 **MONITORAMENTO E MÉTRICAS**

### **Métricas WebSocket**
- **Conexões ativas**: Número de clientes conectados
- **Mensagens por segundo**: Taxa de mensagens enviadas/recebidas
- **Latência**: Tempo entre envio e recebimento
- **Taxa de reconexão**: Frequência de reconexões
- **Erros**: Tipos e frequência de erros

### **Logs de Auditoria**
```json
{
  "timestamp": "2024-12-19T23:00:00Z",
  "event": "websocket_message",
  "client_id": "client_123",
  "user_id": "user_456",
  "message": {
    "event": "EXECUCAO_INICIAR",
    "data": { ... }
  },
  "response_time": 150,
  "status": "success"
}
```

---

## 🔒 **SEGURANÇA**

### **Autenticação**
- JWT token obrigatório para conexão
- Validação de permissões por evento
- Rate limiting por cliente

### **Validação**
- Validação de schema para todos os eventos
- Sanitização de dados de entrada
- Proteção contra ataques de injeção

### **Monitoramento**
- Logs de auditoria para todas as ações
- Detecção de comportamento suspeito
- Alertas de segurança em tempo real

---

## 📝 **CHANGELOG**

### **v1.0 (2024-12-19)**
- ✅ Implementação inicial do WebSocket
- ✅ Eventos de execução de keywords
- ✅ Sistema de notificações
- ✅ Monitoramento de performance
- ✅ Documentação completa

---

**🎯 DOCUMENTAÇÃO CONCLUÍDA**

**Tracing ID**: `WEBSOCKET_DOCS_001`  
**Status**: ✅ **PRONTO PARA USO** 