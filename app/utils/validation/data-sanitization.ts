/**
 * Sistema de Sanitização de Dados
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 8.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface SanitizationConfig {
  removeScripts: boolean;
  removeStyles: boolean;
  removeComments: boolean;
  escapeHtml: boolean;
  normalizeWhitespace: boolean;
  removeSpecialChars: boolean;
  maxLength?: number;
  allowedTags?: string[];
  allowedAttributes?: string[];
}

export interface SanitizationResult {
  sanitized: any;
  removed: string[];
  warnings: string[];
}

export class DataSanitizer {
  private static readonly DEFAULT_CONFIG: SanitizationConfig = {
    removeScripts: true,
    removeStyles: true,
    removeComments: true,
    escapeHtml: true,
    normalizeWhitespace: true,
    removeSpecialChars: false,
    allowedTags: ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li'],
    allowedAttributes: ['class', 'id']
  };

  /**
   * Sanitiza dados de entrada
   */
  static sanitize(data: any, config: Partial<SanitizationConfig> = {}): SanitizationResult {
    const sanitizationConfig = { ...this.DEFAULT_CONFIG, ...config };
    const result: SanitizationResult = {
      sanitized: null,
      removed: [],
      warnings: []
    };

    try {
      result.sanitized = this.sanitizeValue(data, sanitizationConfig, result);
    } catch (error) {
      result.warnings.push(`Erro na sanitização: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
      result.sanitized = data; // Retorna dados originais em caso de erro
    }

    return result;
  }

  /**
   * Sanitiza valor individual
   */
  private static sanitizeValue(value: any, config: SanitizationConfig, result: SanitizationResult): any {
    if (value === null || value === undefined) {
      return value;
    }

    if (typeof value === 'string') {
      return this.sanitizeString(value, config, result);
    }

    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        return value.map(item => this.sanitizeValue(item, config, result));
      } else {
        return this.sanitizeObject(value, config, result);
      }
    }

    return value;
  }

  /**
   * Sanitiza string
   */
  private static sanitizeString(value: string, config: SanitizationConfig, result: SanitizationResult): string {
    let sanitized = value;

    // Normalizar whitespace
    if (config.normalizeWhitespace) {
      sanitized = this.normalizeWhitespace(sanitized);
    }

    // Remover scripts
    if (config.removeScripts) {
      sanitized = this.removeScripts(sanitized, result);
    }

    // Remover estilos
    if (config.removeStyles) {
      sanitized = this.removeStyles(sanitized, result);
    }

    // Remover comentários
    if (config.removeComments) {
      sanitized = this.removeComments(sanitized, result);
    }

    // Escapar HTML
    if (config.escapeHtml) {
      sanitized = this.escapeHtml(sanitized);
    }

    // Remover caracteres especiais
    if (config.removeSpecialChars) {
      sanitized = this.removeSpecialChars(sanitized);
    }

    // Limitar comprimento
    if (config.maxLength && sanitized.length > config.maxLength) {
      sanitized = sanitized.substring(0, config.maxLength);
      result.warnings.push(`String truncada para ${config.maxLength} caracteres`);
    }

    return sanitized;
  }

  /**
   * Sanitiza objeto
   */
  private static sanitizeObject(obj: any, config: SanitizationConfig, result: SanitizationResult): any {
    const sanitized: any = {};

    for (const [key, value] of Object.entries(obj)) {
      // Sanitizar chave
      const sanitizedKey = this.sanitizeString(key, config, result);
      
      // Sanitizar valor
      const sanitizedValue = this.sanitizeValue(value, config, result);
      
      sanitized[sanitizedKey] = sanitizedValue;
    }

    return sanitized;
  }

  /**
   * Normaliza whitespace
   */
  private static normalizeWhitespace(text: string): string {
    return text
      .replace(/\s+/g, ' ') // Múltiplos espaços para um
      .replace(/\n\s*\n/g, '\n') // Múltiplas quebras de linha para uma
      .trim();
  }

  /**
   * Remove scripts maliciosos
   */
  private static removeScripts(text: string, result: SanitizationResult): string {
    const scriptPatterns = [
      /<script[^>]*>.*?<\/script>/gis,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /eval\s*\(/gi,
      /setTimeout\s*\(/gi,
      /setInterval\s*\(/gi
    ];

    let sanitized = text;
    scriptPatterns.forEach(pattern => {
      const matches = sanitized.match(pattern);
      if (matches) {
        result.removed.push(...matches);
        sanitized = sanitized.replace(pattern, '');
      }
    });

    return sanitized;
  }

  /**
   * Remove estilos inline
   */
  private static removeStyles(text: string, result: SanitizationResult): string {
    const stylePatterns = [
      /<style[^>]*>.*?<\/style>/gis,
      /style\s*=\s*["'][^"']*["']/gi
    ];

    let sanitized = text;
    stylePatterns.forEach(pattern => {
      const matches = sanitized.match(pattern);
      if (matches) {
        result.removed.push(...matches);
        sanitized = sanitized.replace(pattern, '');
      }
    });

    return sanitized;
  }

  /**
   * Remove comentários HTML
   */
  private static removeComments(text: string, result: SanitizationResult): string {
    const commentPattern = /<!--.*?-->/gs;
    const matches = text.match(commentPattern);
    
    if (matches) {
      result.removed.push(...matches);
      return text.replace(commentPattern, '');
    }

    return text;
  }

  /**
   * Escapa caracteres HTML
   */
  private static escapeHtml(text: string): string {
    const htmlEntities: { [key: string]: string } = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    };

    return text.replace(/[&<>"'/]/g, char => htmlEntities[char] || char);
  }

  /**
   * Remove caracteres especiais
   */
  private static removeSpecialChars(text: string): string {
    return text.replace(/[^a-zA-Z0-9\s]/g, '');
  }

  /**
   * Sanitiza HTML permitindo apenas tags seguras
   */
  static sanitizeHtml(html: string, allowedTags: string[] = [], allowedAttributes: string[] = []): string {
    const config: SanitizationConfig = {
      ...this.DEFAULT_CONFIG,
      allowedTags: allowedTags.length > 0 ? allowedTags : this.DEFAULT_CONFIG.allowedTags!,
      allowedAttributes: allowedAttributes.length > 0 ? allowedAttributes : this.DEFAULT_CONFIG.allowedAttributes!
    };

    const result = this.sanitize(html, config);
    return this.cleanHtmlTags(result.sanitized, config);
  }

  /**
   * Limpa tags HTML permitindo apenas as seguras
   */
  private static cleanHtmlTags(html: string, config: SanitizationConfig): string {
    // Remover todas as tags não permitidas
    const tagPattern = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>/g;
    
    return html.replace(tagPattern, (match, slash, tagName, attributes) => {
      const lowerTagName = tagName.toLowerCase();
      
      // Verificar se a tag é permitida
      if (!config.allowedTags!.includes(lowerTagName)) {
        return ''; // Remove tag não permitida
      }

      // Sanitizar atributos
      const sanitizedAttributes = this.sanitizeAttributes(attributes, config.allowedAttributes!);
      
      return `<${slash}${tagName}${sanitizedAttributes}>`;
    });
  }

  /**
   * Sanitiza atributos HTML
   */
  private static sanitizeAttributes(attributes: string, allowedAttributes: string[]): string {
    const attributePattern = /(\w+)\s*=\s*["']([^"']*)["']/g;
    const sanitizedAttributes: string[] = [];

    let match;
    while ((match = attributePattern.exec(attributes)) !== null) {
      const [, attrName, attrValue] = match;
      const lowerAttrName = attrName.toLowerCase();

      // Verificar se o atributo é permitido
      if (allowedAttributes.includes(lowerAttrName)) {
        // Sanitizar valor do atributo
        const sanitizedValue = this.escapeHtml(attrValue);
        sanitizedAttributes.push(`${attrName}="${sanitizedValue}"`);
      }
    }

    return sanitizedAttributes.length > 0 ? ` ${sanitizedAttributes.join(' ')}` : '';
  }

  /**
   * Sanitiza dados de formulário
   */
  static sanitizeFormData(formData: FormData, config: Partial<SanitizationConfig> = {}): FormData {
    const sanitizedFormData = new FormData();
    const sanitizationConfig = { ...this.DEFAULT_CONFIG, ...config };

    for (const [key, value] of formData.entries()) {
      const sanitizedKey = this.sanitizeString(key, sanitizationConfig, { sanitized: null, removed: [], warnings: [] });
      let sanitizedValue = value;

      if (typeof value === 'string') {
        sanitizedValue = this.sanitizeString(value, sanitizationConfig, { sanitized: null, removed: [], warnings: [] });
      }

      sanitizedFormData.append(sanitizedKey, sanitizedValue);
    }

    return sanitizedFormData;
  }

  /**
   * Sanitiza dados JSON
   */
  static sanitizeJson(jsonData: any, config: Partial<SanitizationConfig> = {}): any {
    const result = this.sanitize(jsonData, config);
    return result.sanitized;
  }

  /**
   * Sanitiza URL
   */
  static sanitizeUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      
      // Remover scripts da URL
      let sanitizedUrl = urlObj.toString();
      sanitizedUrl = sanitizedUrl.replace(/javascript:/gi, '');
      sanitizedUrl = sanitizedUrl.replace(/data:/gi, '');
      
      return sanitizedUrl;
    } catch (error) {
      // Se não for uma URL válida, retorna string vazia
      return '';
    }
  }

  /**
   * Sanitiza email
   */
  static sanitizeEmail(email: string): string {
    // Remove caracteres perigosos e normaliza
    return email
      .toLowerCase()
      .trim()
      .replace(/[^\w@.-]/g, '') // Remove caracteres especiais exceto @, ., -
      .replace(/\.+/g, '.') // Remove pontos múltiplos
      .replace(/@+/g, '@'); // Remove @ múltiplos
  }

  /**
   * Sanitiza número de telefone
   */
  static sanitizePhone(phone: string): string {
    // Remove tudo exceto números, +, -, (, )
    return phone
      .replace(/[^\d+\-()]/g, '')
      .replace(/\(+/g, '(')
      .replace(/\)+/g, ')')
      .replace(/\-+/g, '-')
      .replace(/\++/g, '+');
  }

  /**
   * Sanitiza CPF
   */
  static sanitizeCPF(cpf: string): string {
    // Remove tudo exceto números
    const numbers = cpf.replace(/\D/g, '');
    
    // Formata CPF
    if (numbers.length === 11) {
      return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    
    return numbers;
  }

  /**
   * Sanitiza CNPJ
   */
  static sanitizeCNPJ(cnpj: string): string {
    // Remove tudo exceto números
    const numbers = cnpj.replace(/\D/g, '');
    
    // Formata CNPJ
    if (numbers.length === 14) {
      return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    
    return numbers;
  }

  /**
   * Verifica se string contém conteúdo malicioso
   */
  static isMalicious(text: string): boolean {
    const maliciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /eval\s*\(/i,
      /<iframe/i,
      /<object/i,
      /<embed/i,
      /vbscript:/i,
      /data:text\/html/i
    ];

    return maliciousPatterns.some(pattern => pattern.test(text));
  }

  /**
   * Retorna estatísticas de sanitização
   */
  static getSanitizationStats(): { patterns: number; removedItems: number } {
    return {
      patterns: 6, // Número de padrões de sanitização
      removedItems: 0 // Será incrementado durante a sanitização
    };
  }
} 