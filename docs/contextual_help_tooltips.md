# 💡 **TOOLTIPS E AJUDA CONTEXTUAL: SISTEMA DE CREDENCIAIS**

## 📋 **VISÃO GERAL**

Este documento define os tooltips e mensagens de ajuda contextual implementados no sistema de credenciais do Omni Keywords Finder, garantindo uma experiência de usuário intuitiva e informativa.

---

## 🎯 **PRINCÍPIOS DE DESIGN**

### **Diretrizes Gerais**
- **Concisão**: Mensagens curtas e diretas
- **Clareza**: Linguagem simples e acessível
- **Contexto**: Informação relevante ao momento
- **Ação**: Orientações práticas quando possível
- **Acessibilidade**: Compatível com leitores de tela

### **Padrões de Implementação**
- **Tooltips**: Para campos e botões
- **Mensagens de Validação**: Para erros e avisos
- **Ajuda Contextual**: Para seções complexas
- **Tutoriais**: Para novos usuários

---

## 🔧 **TOOLTIPS POR SEÇÃO**

### **IAs Generativas**

#### **OpenAI**
```typescript
// API Key
tooltip: "Sua chave de API do OpenAI. Formato: sk-... (mínimo 20 caracteres)"

// Modelo
tooltip: "Modelo de IA a ser usado. Recomendado: gpt-4 para melhor qualidade"

// Máximo de Tokens
tooltip: "Número máximo de tokens por requisição (1-8192). Maior = mais contexto"

// Temperatura
tooltip: "Criatividade da IA (0.0-2.0). 0.0 = determinístico, 2.0 = muito criativo"

// Habilitado
tooltip: "Ativa ou desativa este provedor de IA"
```

#### **DeepSeek**
```typescript
// API Key
tooltip: "Sua chave de API do DeepSeek. Formato: sk-... (mínimo 20 caracteres)"

// Modelo
tooltip: "Modelo DeepSeek a ser usado. Padrão: deepseek-chat"

// Configurações Avançadas
tooltip: "Configurações específicas do DeepSeek (timeout, retry, etc.)"
```

#### **Claude (Anthropic)**
```typescript
// API Key
tooltip: "Sua chave de API do Anthropic. Formato: sk-ant-... (mínimo 25 caracteres)"

// Modelo
tooltip: "Modelo Claude a ser usado. Recomendado: Claude-3-Sonnet"

// Configurações de Segurança
tooltip: "Configurações de segurança e compliance do Claude"
```

#### **Gemini (Google)**
```typescript
// API Key
tooltip: "Sua chave de API do Google AI. Obtida no Google AI Studio"

// Modelo
tooltip: "Modelo Gemini a ser usado. Padrão: gemini-pro"

// Configurações do Google
tooltip: "Configurações específicas da plataforma Google AI"
```

### **Redes Sociais**

#### **Instagram**
```typescript
// Username
tooltip: "Seu nome de usuário do Instagram (sem @)"

// Password
tooltip: "Sua senha do Instagram (será criptografada)"

// Session ID
tooltip: "ID da sessão (opcional). Útil para evitar login frequente"

// Habilitado
tooltip: "Ativa ou desativa integração com Instagram"
```

#### **TikTok**
```typescript
// API Key
tooltip: "Sua chave de API do TikTok for Developers"

// API Secret
tooltip: "Seu segredo de API do TikTok (será criptografado)"

// Configurações de Rate Limit
tooltip: "Configurações de limite de requisições por minuto"
```

#### **YouTube**
```typescript
// Client ID
tooltip: "ID do cliente OAuth do Google Cloud Console"

// Client Secret
tooltip: "Segredo do cliente OAuth (será criptografado)"

// Configurações OAuth
tooltip: "Configurações de autenticação OAuth 2.0"
```

#### **Pinterest**
```typescript
// Access Token
tooltip: "Token de acesso OAuth do Pinterest (será criptografado)"

// Configurações de API
tooltip: "Configurações específicas da API do Pinterest"
```

#### **Reddit**
```typescript
// Client ID
tooltip: "ID do cliente da aplicação Reddit"

// Client Secret
tooltip: "Segredo do cliente Reddit (será criptografado)"

// Configurações de Aplicação
tooltip: "Configurações da aplicação Reddit"
```

### **Analytics**

#### **Google Analytics**
```typescript
// Client ID
tooltip: "ID do cliente OAuth do Google Analytics"

// Client Secret
tooltip: "Segredo do cliente OAuth (será criptografado)"

// Configurações GA4
tooltip: "Configurações específicas do Google Analytics 4"
```

#### **SEMrush**
```typescript
// API Key
tooltip: "Sua chave de API do SEMrush"

// Configurações de Limite
tooltip: "Configurações de limite de requisições diárias"
```

#### **Ahrefs**
```typescript
// API Key
tooltip: "Sua chave de API do Ahrefs"

// Configurações de Backlink
tooltip: "Configurações de análise de backlinks"
```

#### **Google Search Console**
```typescript
// Client ID
tooltip: "ID do cliente OAuth do Google Search Console"

// Client Secret
tooltip: "Segredo do cliente OAuth (será criptografado)"

// Refresh Token
tooltip: "Token de refresh OAuth (será criptografado)"

// Configurações GSC
tooltip: "Configurações específicas do Google Search Console"
```

### **Pagamentos**

#### **Stripe**
```typescript
// API Key
tooltip: "Sua chave secreta do Stripe (será criptografada)"

// Webhook Secret
tooltip: "Segredo do webhook Stripe (será criptografado)"

// Configurações de Pagamento
tooltip: "Configurações de processamento de pagamentos"
```

#### **PayPal**
```typescript
// Client ID
tooltip: "ID do cliente PayPal"

// Client Secret
tooltip: "Segredo do cliente PayPal (será criptografado)"

// Configurações PayPal
tooltip: "Configurações específicas do PayPal"
```

#### **Mercado Pago**
```typescript
// Access Token
tooltip: "Token de acesso do Mercado Pago (será criptografado)"

// Configurações MP
tooltip: "Configurações específicas do Mercado Pago"
```

### **Notificações**

#### **Slack**
```typescript
// Webhook URL
tooltip: "URL do webhook do Slack (https://hooks.slack.com/...)"

// Configurações de Canal
tooltip: "Configurações do canal de notificações"
```

#### **Discord**
```typescript
// Bot Token
tooltip: "Token do bot Discord (será criptografado)"

// Channel ID
tooltip: "ID do canal para notificações"

// Configurações do Bot
tooltip: "Configurações específicas do bot Discord"
```

#### **Telegram**
```typescript
// Bot Token
tooltip: "Token do bot Telegram (será criptografado)"

// Channel ID
tooltip: "ID do canal para notificações"

// Configurações do Bot
tooltip: "Configurações específicas do bot Telegram"
```

---

## ⚠️ **MENSAGENS DE VALIDAÇÃO**

### **Erros de Formato**

#### **API Keys**
```typescript
// OpenAI/DeepSeek
error: "API Key deve começar com 'sk-' e ter pelo menos 20 caracteres"

// Claude
error: "API Key deve começar com 'sk-ant-' e ter pelo menos 25 caracteres"

// Gemini
error: "API Key deve conter 'AIza' e ter pelo menos 20 caracteres"

// TikTok
error: "API Key deve ter pelo menos 20 caracteres"

// YouTube
error: "Client ID deve ter pelo menos 20 caracteres"

// Stripe
error: "API Key deve começar com 'sk_' e ter pelo menos 20 caracteres"
```

#### **URLs**
```typescript
// Slack Webhook
error: "URL deve começar com 'https://hooks.slack.com/'"

// URLs Gerais
error: "URL deve ser válida e usar HTTPS"
```

#### **Campos Obrigatórios**
```typescript
// Campo Vazio
error: "Este campo é obrigatório"

// Campo Muito Curto
error: "Mínimo de {min} caracteres"

// Campo Muito Longo
error: "Máximo de {max} caracteres"
```

### **Erros de Validação**

#### **Rate Limiting**
```typescript
// Rate Limit Excedido
error: "Rate limit excedido. Aguarde {time} segundos"

// Muitas Tentativas
error: "Muitas tentativas. Tente novamente em {time}"

// Bloqueio Temporário
error: "Acesso temporariamente bloqueado. Tente novamente em {time}"
```

#### **Conectividade**
```typescript
// Timeout
error: "Timeout na validação. Verifique sua conexão"

// API Indisponível
error: "API temporariamente indisponível. Tente novamente"

// Erro de Rede
error: "Erro de conectividade. Verifique sua internet"
```

#### **Credenciais**
```typescript
// Credencial Inválida
error: "Credencial inválida. Verifique e tente novamente"

// Credencial Expirada
error: "Credencial expirada. Renove sua chave de API"

// Limite Atingido
error: "Limite de uso atingido. Verifique sua conta"
```

---

## 💡 **AJUDA CONTEXTUAL**

### **Seções Principais**

#### **Configuração Geral**
```typescript
help: {
  title: "Configuração de Credenciais",
  content: `
    <h4>Como Configurar</h4>
    <ol>
      <li>Obtenha suas chaves de API dos provedores</li>
      <li>Cole as chaves nos campos correspondentes</li>
      <li>Clique em "Validar Credenciais"</li>
      <li>Salve a configuração</li>
    </ol>
    
    <h4>Segurança</h4>
    <ul>
      <li>Todas as credenciais são criptografadas</li>
      <li>Use HTTPS sempre</li>
      <li>Não compartilhe suas chaves</li>
      <li>Monitore o uso regularmente</li>
    </ul>
  `
}
```

#### **Fallback Automático**
```typescript
help: {
  title: "Fallback Automático",
  content: `
    <h4>Como Funciona</h4>
    <p>Quando um provedor falha, o sistema automaticamente tenta o próximo na lista.</p>
    
    <h4>Configuração</h4>
    <ul>
      <li>Defina a ordem de prioridade</li>
      <li>Configure timeout adequado</li>
      <li>Monitore métricas de fallback</li>
    </ul>
    
    <h4>Benefícios</h4>
    <ul>
      <li>Alta disponibilidade</li>
      <li>Redução de falhas</li>
      <li>Melhor experiência do usuário</li>
    </ul>
  `
}
```

#### **Monitoramento**
```typescript
help: {
  title: "Monitoramento de Credenciais",
  content: `
    <h4>Métricas Disponíveis</h4>
    <ul>
      <li>Taxa de sucesso por provedor</li>
      <li>Tempo de resposta médio</li>
      <li>Número de erros</li>
      <li>Uso de rate limiting</li>
    </ul>
    
    <h4>Alertas</h4>
    <ul>
      <li>Credenciais expiradas</li>
      <li>Taxa de erro alta</li>
      <li>Rate limit excedido</li>
      <li>Falhas de conectividade</li>
    </ul>
  `
}
```

### **Tutoriais Interativos**

#### **Primeira Configuração**
```typescript
tutorial: {
  steps: [
    {
      title: "Bem-vindo ao Sistema de Credenciais",
      content: "Vamos configurar suas primeiras credenciais de API",
      target: "#welcome-section"
    },
    {
      title: "Configurar OpenAI",
      content: "Comece configurando sua chave da OpenAI",
      target: "#openai-section"
    },
    {
      title: "Validar Credencial",
      content: "Clique em 'Validar Credenciais' para testar",
      target: "#validate-button"
    },
    {
      title: "Salvar Configuração",
      content: "Salve sua configuração para começar a usar",
      target: "#save-button"
    }
  ]
}
```

#### **Configuração Avançada**
```typescript
tutorial: {
  steps: [
    {
      title: "Fallback Automático",
      content: "Configure múltiplos provedores para alta disponibilidade",
      target: "#fallback-section"
    },
    {
      title: "Monitoramento",
      content: "Configure alertas e notificações",
      target: "#monitoring-section"
    },
    {
      title: "Backup",
      content: "Configure backup automático das credenciais",
      target: "#backup-section"
    }
  ]
}
```

---

## 🔧 **IMPLEMENTAÇÃO TÉCNICA**

### **Componente Tooltip**
```typescript
interface TooltipProps {
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  position = 'top',
  delay = 500,
  children
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null);

  const showTooltip = () => {
    const timeout = setTimeout(() => setIsVisible(true), delay);
    setTimer(timeout);
  };

  const hideTooltip = () => {
    if (timer) clearTimeout(timer);
    setIsVisible(false);
  };

  return (
    <div
      className="tooltip-container"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
    >
      {children}
      {isVisible && (
        <div className={`tooltip tooltip-${position}`}>
          {content}
        </div>
      )}
    </div>
  );
};
```

### **Componente de Ajuda Contextual**
```typescript
interface HelpProps {
  title: string;
  content: string;
  children: React.ReactNode;
}

const Help: React.FC<HelpProps> = ({ title, content, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="help-container">
      <div className="help-trigger" onClick={() => setIsOpen(!isOpen)}>
        {children}
        <Icon name="help" />
      </div>
      {isOpen && (
        <div className="help-modal">
          <div className="help-header">
            <h3>{title}</h3>
            <button onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="help-content" dangerouslySetInnerHTML={{ __html: content }} />
        </div>
      )}
    </div>
  );
};
```

### **Sistema de Mensagens**
```typescript
interface ValidationMessage {
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  field?: string;
  code?: string;
}

class ValidationSystem {
  private static messages: Record<string, string> = {
    'required': 'Este campo é obrigatório',
    'invalid_format': 'Formato inválido',
    'rate_limit': 'Rate limit excedido',
    'timeout': 'Timeout na validação',
    'network_error': 'Erro de conectividade',
    'invalid_credential': 'Credencial inválida',
    'expired_credential': 'Credencial expirada'
  };

  static getMessage(code: string, params?: Record<string, any>): string {
    let message = this.messages[code] || 'Erro desconhecido';
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        message = message.replace(`{${key}}`, String(value));
      });
    }
    
    return message;
  }

  static validateField(value: any, rules: ValidationRule[]): ValidationMessage[] {
    const errors: ValidationMessage[] = [];
    
    rules.forEach(rule => {
      if (!rule.validator(value)) {
        errors.push({
          type: 'error',
          message: this.getMessage(rule.code, rule.params),
          field: rule.field,
          code: rule.code
        });
      }
    });
    
    return errors;
  }
}
```

---

## 🎨 **ESTILOS CSS**

### **Tooltip Styles**
```css
.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip {
  position: absolute;
  background: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.tooltip::before {
  content: '';
  position: absolute;
  border: 5px solid transparent;
}

.tooltip-top {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 5px;
}

.tooltip-top::before {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: #333;
}

.tooltip-bottom {
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 5px;
}

.tooltip-bottom::before {
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: #333;
}

.tooltip-left {
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-right: 5px;
}

.tooltip-left::before {
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  border-left-color: #333;
}

.tooltip-right {
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 5px;
}

.tooltip-right::before {
  right: 100%;
  top: 50%;
  transform: translateY(-50%);
  border-right-color: #333;
}
```

### **Help Modal Styles**
```css
.help-container {
  position: relative;
  display: inline-block;
}

.help-trigger {
  cursor: pointer;
  color: #007bff;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.help-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.help-modal-content {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.help-header h3 {
  margin: 0;
  color: #333;
}

.help-header button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.help-content {
  padding: 20px;
  line-height: 1.6;
}

.help-content h4 {
  color: #333;
  margin-top: 16px;
  margin-bottom: 8px;
}

.help-content ul, .help-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.help-content li {
  margin: 4px 0;
}
```

---

## ♿ **ACESSIBILIDADE**

### **ARIA Labels**
```typescript
// Tooltip acessível
<div
  role="tooltip"
  aria-describedby="tooltip-content"
  className="tooltip"
>
  <span id="tooltip-content">{content}</span>
</div>

// Help modal acessível
<div
  role="dialog"
  aria-labelledby="help-title"
  aria-describedby="help-content"
  className="help-modal"
>
  <h2 id="help-title">{title}</h2>
  <div id="help-content">{content}</div>
</div>
```

### **Navegação por Teclado**
```typescript
// Suporte a teclado para tooltips
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    setIsVisible(!isVisible);
  }
};

// Suporte a teclado para help modal
const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    setIsOpen(false);
  }
};
```

### **Leitores de Tela**
```typescript
// Texto alternativo para ícones
<Icon name="help" aria-label="Ajuda" />

// Descrições para campos
<input
  aria-describedby="field-help"
  aria-invalid={hasError}
  aria-required={isRequired}
/>

<span id="field-help" className="sr-only">
  {helpText}
</span>
```

---

## 📱 **RESPONSIVIDADE**

### **Mobile Tooltips**
```css
@media (max-width: 768px) {
  .tooltip {
    position: fixed;
    bottom: 20px;
    left: 20px;
    right: 20px;
    transform: none;
    white-space: normal;
    max-width: none;
  }
  
  .tooltip::before {
    display: none;
  }
}
```

### **Mobile Help Modal**
```css
@media (max-width: 768px) {
  .help-modal-content {
    margin: 20px;
    max-width: none;
    max-height: calc(100vh - 40px);
  }
  
  .help-header {
    padding: 12px 16px;
  }
  
  .help-content {
    padding: 16px;
  }
}
```

---

## 🔄 **INTERNACIONALIZAÇÃO**

### **Estrutura de Tradução**
```typescript
const translations = {
  'pt-BR': {
    tooltips: {
      openai_api_key: 'Sua chave de API do OpenAI. Formato: sk-... (mínimo 20 caracteres)',
      openai_model: 'Modelo de IA a ser usado. Recomendado: gpt-4 para melhor qualidade',
      // ... mais traduções
    },
    errors: {
      required: 'Este campo é obrigatório',
      invalid_format: 'Formato inválido',
      // ... mais traduções
    },
    help: {
      configuration_title: 'Configuração de Credenciais',
      configuration_content: 'Como configurar suas credenciais...',
      // ... mais traduções
    }
  },
  'en-US': {
    tooltips: {
      openai_api_key: 'Your OpenAI API key. Format: sk-... (minimum 20 characters)',
      openai_model: 'AI model to use. Recommended: gpt-4 for better quality',
      // ... mais traduções
    },
    errors: {
      required: 'This field is required',
      invalid_format: 'Invalid format',
      // ... mais traduções
    },
    help: {
      configuration_title: 'Credential Configuration',
      configuration_content: 'How to configure your credentials...',
      // ... mais traduções
    }
  }
};
```

### **Hook de Tradução**
```typescript
const useTranslation = () => {
  const [language, setLanguage] = useState('pt-BR');
  
  const t = (key: string, params?: Record<string, any>): string => {
    const keys = key.split('.');
    let value = translations[language];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    if (!value) return key;
    
    if (params) {
      Object.entries(params).forEach(([key, val]) => {
        value = value.replace(`{${key}}`, String(val));
      });
    }
    
    return value;
  };
  
  return { t, language, setLanguage };
};
```

---

## 📊 **ANALYTICS E FEEDBACK**

### **Tracking de Uso**
```typescript
// Tracking de tooltips
const trackTooltipView = (tooltipId: string) => {
  analytics.track('tooltip_viewed', {
    tooltip_id: tooltipId,
    timestamp: new Date().toISOString(),
    user_id: getCurrentUserId()
  });
};

// Tracking de help modal
const trackHelpModalOpen = (helpId: string) => {
  analytics.track('help_modal_opened', {
    help_id: helpId,
    timestamp: new Date().toISOString(),
    user_id: getCurrentUserId()
  });
};

// Tracking de feedback
const trackHelpFeedback = (helpId: string, helpful: boolean) => {
  analytics.track('help_feedback', {
    help_id: helpId,
    helpful,
    timestamp: new Date().toISOString(),
    user_id: getCurrentUserId()
  });
};
```

### **Sistema de Feedback**
```typescript
const HelpFeedback: React.FC<{ helpId: string }> = ({ helpId }) => {
  const [feedback, setFeedback] = useState<'helpful' | 'not_helpful' | null>(null);
  
  const handleFeedback = (type: 'helpful' | 'not_helpful') => {
    setFeedback(type);
    trackHelpFeedback(helpId, type === 'helpful');
    
    if (type === 'not_helpful') {
      // Abrir formulário de feedback detalhado
      openFeedbackForm(helpId);
    }
  };
  
  return (
    <div className="help-feedback">
      <p>Esta ajuda foi útil?</p>
      <button
        onClick={() => handleFeedback('helpful')}
        disabled={feedback !== null}
      >
        👍 Sim
      </button>
      <button
        onClick={() => handleFeedback('not_helpful')}
        disabled={feedback !== null}
      >
        👎 Não
      </button>
    </div>
  );
};
```

---

## 🚀 **OTIMIZAÇÃO E PERFORMANCE**

### **Lazy Loading**
```typescript
// Carregar tooltips sob demanda
const LazyTooltip: React.FC<TooltipProps> = ({ content, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 100);
    return () => clearTimeout(timer);
  }, []);
  
  if (!isLoaded) return <div className="tooltip-placeholder" />;
  
  return <Tooltip content={content} {...props} />;
};
```

### **Cache de Conteúdo**
```typescript
// Cache de tooltips para melhor performance
const tooltipCache = new Map<string, string>();

const getTooltipContent = async (tooltipId: string): Promise<string> => {
  if (tooltipCache.has(tooltipId)) {
    return tooltipCache.get(tooltipId)!;
  }
  
  const content = await fetchTooltipContent(tooltipId);
  tooltipCache.set(tooltipId, content);
  
  return content;
};
```

---

**Última atualização**: 2025-01-27
**Versão da documentação**: 1.0
**Autor**: Paulo Júnior 