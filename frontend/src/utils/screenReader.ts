/**
 * Utilitário de Suporte a Screen Reader - screenReader.ts
 * 
 * Fornece funcionalidades para suporte a screen readers
 * Baseado em WCAG 2.1 AA e padrões de acessibilidade
 * 
 * Tracing ID: screenReader_utils_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

/**
 * Tipos de anúncios para screen reader
 */
export type AnnouncementType = 'polite' | 'assertive' | 'status' | 'log' | 'alert';

/**
 * Prioridade de anúncio
 */
export type AnnouncementPriority = 'low' | 'normal' | 'high' | 'critical';

/**
 * Configuração de anúncio
 */
export interface AnnouncementConfig {
  /** Tipo de anúncio */
  type: AnnouncementType;
  /** Prioridade do anúncio */
  priority: AnnouncementPriority;
  /** Se deve interromper anúncios em andamento */
  interrupt?: boolean;
  /** Tempo de duração do anúncio (ms) */
  duration?: number;
  /** Se deve repetir o anúncio */
  repeat?: boolean;
  /** Número de repetições */
  repeatCount?: number;
}

/**
 * Resultado de anúncio
 */
export interface AnnouncementResult {
  /** ID único do anúncio */
  id: string;
  /** Mensagem anunciada */
  message: string;
  /** Timestamp do anúncio */
  timestamp: number;
  /** Se o anúncio foi bem-sucedido */
  success: boolean;
  /** Erro se houver */
  error?: string;
}

/**
 * Estado do screen reader
 */
export interface ScreenReaderState {
  /** Se o screen reader está ativo */
  isActive: boolean;
  /** Anúncios em fila */
  queue: AnnouncementResult[];
  /** Anúncio atual */
  current: AnnouncementResult | null;
  /** Configurações atuais */
  config: AnnouncementConfig;
}

/**
 * Gera ID único para anúncios
 */
export const generateAnnouncementId = (): string => {
  return `sr-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Detecta se screen reader está ativo
 */
export const detectScreenReader = (): boolean => {
  // Verifica se há tecnologias assistivas ativas
  const hasScreenReader = 
    'speechSynthesis' in window ||
    'webkitSpeechSynthesis' in window ||
    navigator.userAgent.includes('NVDA') ||
    navigator.userAgent.includes('JAWS') ||
    navigator.userAgent.includes('VoiceOver') ||
    navigator.userAgent.includes('TalkBack');
  
  // Verifica preferências de acessibilidade
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
  
  return hasScreenReader || prefersReducedMotion || prefersHighContrast;
};

/**
 * Cria elemento live region para anúncios
 */
export const createLiveRegion = (
  type: AnnouncementType = 'polite',
  atomic: boolean = true
): HTMLElement => {
  const liveRegion = document.createElement('div');
  
  // Define atributos ARIA
  liveRegion.setAttribute('aria-live', type);
  liveRegion.setAttribute('aria-atomic', atomic.toString());
  liveRegion.setAttribute('aria-relevant', 'additions text');
  liveRegion.setAttribute('role', 'status');
  
  // Estilo para ocultar visualmente
  liveRegion.style.position = 'absolute';
  liveRegion.style.left = '-10000px';
  liveRegion.style.width = '1px';
  liveRegion.style.height = '1px';
  liveRegion.style.overflow = 'hidden';
  liveRegion.style.clip = 'rect(0 0 0 0)';
  liveRegion.style.whiteSpace = 'nowrap';
  liveRegion.style.border = '0';
  
  // Adiciona ao DOM
  document.body.appendChild(liveRegion);
  
  return liveRegion;
};

/**
 * Remove elemento live region
 */
export const removeLiveRegion = (liveRegion: HTMLElement): void => {
  if (document.body.contains(liveRegion)) {
    document.body.removeChild(liveRegion);
  }
};

/**
 * Anuncia mensagem para screen reader
 */
export const announce = (
  message: string,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const {
    type = 'polite',
    priority = 'normal',
    interrupt = false,
    duration = 1000,
    repeat = false,
    repeatCount = 1
  } = config;

  const id = generateAnnouncementId();
  const timestamp = Date.now();
  
  try {
    // Cria live region
    const liveRegion = createLiveRegion(type, true);
    
    // Define conteúdo
    liveRegion.textContent = message;
    
    // Configura repetição se necessário
    let currentRepeat = 0;
    const repeatAnnouncement = () => {
      if (repeat && currentRepeat < repeatCount) {
        liveRegion.textContent = message;
        currentRepeat++;
        setTimeout(repeatAnnouncement, duration);
      } else {
        removeLiveRegion(liveRegion);
      }
    };
    
    // Inicia repetição se configurada
    if (repeat) {
      setTimeout(repeatAnnouncement, duration);
    } else {
      // Remove após duração
      setTimeout(() => {
        removeLiveRegion(liveRegion);
      }, duration);
    }
    
    return {
      id,
      message,
      timestamp,
      success: true
    };
    
  } catch (error) {
    return {
      id,
      message,
      timestamp,
      success: false,
      error: error instanceof Error ? error.message : 'Erro desconhecido'
    };
  }
};

/**
 * Anuncia mudança de estado
 */
export const announceStateChange = (
  element: HTMLElement,
  newState: string,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const message = `${accessibleText} ${newState}`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia erro
 */
export const announceError = (
  error: string,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  return announce(`Erro: ${error}`, {
    type: 'alert',
    priority: 'high',
    interrupt: true,
    ...config
  });
};

/**
 * Anuncia sucesso
 */
export const announceSuccess = (
  message: string,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  return announce(`Sucesso: ${message}`, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia carregamento
 */
export const announceLoading = (
  message: string = 'Carregando...',
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia conclusão de carregamento
 */
export const announceLoaded = (
  message: string = 'Carregamento concluído',
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia navegação
 */
export const announceNavigation = (
  destination: string,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  return announce(`Navegando para ${destination}`, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia foco em elemento
 */
export const announceFocus = (
  element: HTMLElement,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const role = element.getAttribute('role') || getElementRole(element);
  const state = getElementState(element);
  
  let message = `Focado em ${accessibleText}`;
  if (role) message += `, ${role}`;
  if (state) message += `, ${state}`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia seleção
 */
export const announceSelection = (
  element: HTMLElement,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const message = `${accessibleText} selecionado`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia deseleção
 */
export const announceDeselection = (
  element: HTMLElement,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const message = `${accessibleText} deselecionado`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia expansão
 */
export const announceExpansion = (
  element: HTMLElement,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const message = `${accessibleText} expandido`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Anuncia colapso
 */
export const announceCollapse = (
  element: HTMLElement,
  config: Partial<AnnouncementConfig> = {}
): AnnouncementResult => {
  const accessibleText = getAccessibleText(element);
  const message = `${accessibleText} recolhido`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal',
    ...config
  });
};

/**
 * Obtém texto acessível de elemento
 */
export const getAccessibleText = (element: HTMLElement): string => {
  let text = '';

  // Prioridade 1: aria-label
  const ariaLabel = element.getAttribute('aria-label');
  if (ariaLabel) {
    text = ariaLabel;
  }
  // Prioridade 2: aria-labelledby
  else {
    const labelledBy = element.getAttribute('aria-labelledby');
    if (labelledBy) {
      const labelElement = document.getElementById(labelledBy);
      if (labelElement) {
        text = labelElement.textContent || '';
      }
    }
  }
  // Prioridade 3: title
  if (!text) {
    const title = element.getAttribute('title');
    if (title) {
      text = title;
    }
  }
  // Prioridade 4: alt (para imagens)
  if (!text && element.tagName === 'IMG') {
    const alt = element.getAttribute('alt');
    if (alt) {
      text = alt;
    }
  }
  // Prioridade 5: textContent
  if (!text) {
    text = element.textContent?.trim() || '';
  }

  return text || 'elemento';
};

/**
 * Obtém role do elemento
 */
export const getElementRole = (element: HTMLElement): string => {
  const role = element.getAttribute('role');
  if (role) return role;

  // Inferência baseada na tag
  const tagName = element.tagName.toLowerCase();
  switch (tagName) {
    case 'button': return 'botão';
    case 'input': return 'campo de entrada';
    case 'a': return 'link';
    case 'img': return 'imagem';
    case 'table': return 'tabela';
    case 'form': return 'formulário';
    case 'nav': return 'navegação';
    case 'main': return 'conteúdo principal';
    case 'header': return 'cabeçalho';
    case 'footer': return 'rodapé';
    case 'aside': return 'conteúdo complementar';
    case 'article': return 'artigo';
    case 'section': return 'seção';
    default: return '';
  }
};

/**
 * Obtém estado do elemento
 */
export const getElementState = (element: HTMLElement): string => {
  const states: string[] = [];

  // Estados ARIA
  if (element.getAttribute('aria-expanded') === 'true') states.push('expandido');
  if (element.getAttribute('aria-expanded') === 'false') states.push('recolhido');
  if (element.getAttribute('aria-selected') === 'true') states.push('selecionado');
  if (element.getAttribute('aria-checked') === 'true') states.push('marcado');
  if (element.getAttribute('aria-checked') === 'false') states.push('desmarcado');
  if (element.getAttribute('aria-checked') === 'mixed') states.push('indeterminado');
  if (element.getAttribute('aria-pressed') === 'true') states.push('pressionado');
  if (element.getAttribute('aria-pressed') === 'false') states.push('não pressionado');
  if (element.getAttribute('aria-invalid') === 'true') states.push('inválido');
  if (element.getAttribute('aria-required') === 'true') states.push('obrigatório');
  if (element.getAttribute('aria-disabled') === 'true') states.push('desabilitado');
  if (element.getAttribute('aria-busy') === 'true') states.push('ocupado');

  // Estados HTML
  if (element.hasAttribute('disabled')) states.push('desabilitado');
  if (element.hasAttribute('readonly')) states.push('somente leitura');
  if (element.hasAttribute('required')) states.push('obrigatório');

  return states.join(', ');
};

/**
 * Cria fila de anúncios
 */
export class AnnouncementQueue {
  private queue: Array<{
    id: string;
    message: string;
    config: AnnouncementConfig;
    timestamp: number;
  }> = [];
  private isProcessing = false;

  /**
   * Adiciona anúncio à fila
   */
  add(message: string, config: Partial<AnnouncementConfig> = {}): string {
    const id = generateAnnouncementId();
    const fullConfig: AnnouncementConfig = {
      type: 'polite',
      priority: 'normal',
      interrupt: false,
      duration: 1000,
      repeat: false,
      repeatCount: 1,
      ...config
    };

    this.queue.push({
      id,
      message,
      config: fullConfig,
      timestamp: Date.now()
    });

    // Processa fila se não estiver processando
    if (!this.isProcessing) {
      this.processQueue();
    }

    return id;
  }

  /**
   * Processa fila de anúncios
   */
  private async processQueue(): Promise<void> {
    if (this.queue.length === 0) {
      this.isProcessing = false;
      return;
    }

    this.isProcessing = true;

    while (this.queue.length > 0) {
      const item = this.queue.shift();
      if (!item) continue;

      try {
        await announce(item.message, item.config);
        
        // Aguarda um pouco entre anúncios
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error('Erro ao processar anúncio:', error);
      }
    }

    this.isProcessing = false;
  }

  /**
   * Limpa fila
   */
  clear(): void {
    this.queue = [];
  }

  /**
   * Obtém tamanho da fila
   */
  get size(): number {
    return this.queue.length;
  }
}

/**
 * Instância global da fila de anúncios
 */
export const announcementQueue = new AnnouncementQueue();

/**
 * Anuncia usando fila
 */
export const announceQueued = (
  message: string,
  config: Partial<AnnouncementConfig> = {}
): string => {
  return announcementQueue.add(message, config);
};

/**
 * Anuncia progresso
 */
export const announceProgress = (
  current: number,
  total: number,
  label?: string
): AnnouncementResult => {
  const percentage = Math.round((current / total) * 100);
  const message = label 
    ? `${label}: ${percentage}% completo (${current} de ${total})`
    : `${percentage}% completo (${current} de ${total})`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal'
  });
};

/**
 * Anuncia contagem
 */
export const announceCount = (
  count: number,
  label: string
): AnnouncementResult => {
  const message = `${count} ${label}${count !== 1 ? 's' : ''}`;
  
  return announce(message, {
    type: 'status',
    priority: 'normal'
  });
};

/**
 * Anuncia tempo
 */
export const announceTime = (
  seconds: number
): AnnouncementResult => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  let message: string;
  if (minutes > 0) {
    message = `${minutes} minuto${minutes !== 1 ? 's' : ''} e ${remainingSeconds} segundo${remainingSeconds !== 1 ? 's' : ''}`;
  } else {
    message = `${remainingSeconds} segundo${remainingSeconds !== 1 ? 's' : ''}`;
  }
  
  return announce(message, {
    type: 'status',
    priority: 'normal'
  });
};

export default {
  generateAnnouncementId,
  detectScreenReader,
  createLiveRegion,
  removeLiveRegion,
  announce,
  announceStateChange,
  announceError,
  announceSuccess,
  announceLoading,
  announceLoaded,
  announceNavigation,
  announceFocus,
  announceSelection,
  announceDeselection,
  announceExpansion,
  announceCollapse,
  getAccessibleText,
  getElementRole,
  getElementState,
  AnnouncementQueue,
  announcementQueue,
  announceQueued,
  announceProgress,
  announceCount,
  announceTime
}; 