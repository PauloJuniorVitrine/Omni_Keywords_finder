/**
 * Sistema de Validação de Entrada
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 8.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'pattern' | 'email' | 'url' | 'number' | 'integer' | 'boolean' | 'date' | 'custom';
  value?: any;
  message: string;
  customValidator?: (value: any) => boolean | string;
}

export interface ValidationSchema {
  [field: string]: ValidationRule[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: { [field: string]: string[] };
  warnings: { [field: string]: string[] };
}

export interface SanitizationRule {
  type: 'trim' | 'lowercase' | 'uppercase' | 'removeSpecialChars' | 'escapeHtml' | 'normalizeWhitespace' | 'custom';
  customSanitizer?: (value: any) => any;
}

export interface SanitizationSchema {
  [field: string]: SanitizationRule[];
}

export class InputValidator {
  private static readonly EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  private static readonly URL_PATTERN = /^https?:\/\/.+/;
  private static readonly PHONE_PATTERN = /^[\+]?[1-9][\d]{0,15}$/;
  private static readonly CPF_PATTERN = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/;
  private static readonly CNPJ_PATTERN = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/;

  /**
   * Valida dados conforme schema
   */
  static validate(data: any, schema: ValidationSchema): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: {},
      warnings: {}
    };

    for (const [field, rules] of Object.entries(schema)) {
      const value = this.getNestedValue(data, field);
      const fieldErrors: string[] = [];
      const fieldWarnings: string[] = [];

      for (const rule of rules) {
        const validationResult = this.validateField(value, rule);
        
        if (typeof validationResult === 'string') {
          fieldErrors.push(validationResult);
        } else if (validationResult === false) {
          fieldErrors.push(rule.message);
        }
      }

      if (fieldErrors.length > 0) {
        result.errors[field] = fieldErrors;
        result.isValid = false;
      }

      if (fieldWarnings.length > 0) {
        result.warnings[field] = fieldWarnings;
      }
    }

    return result;
  }

  /**
   * Valida campo individual
   */
  private static validateField(value: any, rule: ValidationRule): boolean | string {
    switch (rule.type) {
      case 'required':
        return this.validateRequired(value, rule.message);

      case 'minLength':
        return this.validateMinLength(value, rule.value, rule.message);

      case 'maxLength':
        return this.validateMaxLength(value, rule.value, rule.message);

      case 'pattern':
        return this.validatePattern(value, rule.value, rule.message);

      case 'email':
        return this.validateEmail(value, rule.message);

      case 'url':
        return this.validateUrl(value, rule.message);

      case 'number':
        return this.validateNumber(value, rule.message);

      case 'integer':
        return this.validateInteger(value, rule.message);

      case 'boolean':
        return this.validateBoolean(value, rule.message);

      case 'date':
        return this.validateDate(value, rule.message);

      case 'custom':
        return this.validateCustom(value, rule);

      default:
        return true;
    }
  }

  /**
   * Validação de campo obrigatório
   */
  private static validateRequired(value: any, message: string): boolean | string {
    if (value === null || value === undefined || value === '') {
      return message;
    }
    return true;
  }

  /**
   * Validação de comprimento mínimo
   */
  private static validateMinLength(value: any, minLength: number, message: string): boolean | string {
    if (value && typeof value === 'string' && value.length < minLength) {
      return message;
    }
    return true;
  }

  /**
   * Validação de comprimento máximo
   */
  private static validateMaxLength(value: any, maxLength: number, message: string): boolean | string {
    if (value && typeof value === 'string' && value.length > maxLength) {
      return message;
    }
    return true;
  }

  /**
   * Validação de padrão regex
   */
  private static validatePattern(value: any, pattern: RegExp, message: string): boolean | string {
    if (value && typeof value === 'string' && !pattern.test(value)) {
      return message;
    }
    return true;
  }

  /**
   * Validação de email
   */
  private static validateEmail(value: any, message: string): boolean | string {
    if (value && typeof value === 'string' && !this.EMAIL_PATTERN.test(value)) {
      return message;
    }
    return true;
  }

  /**
   * Validação de URL
   */
  private static validateUrl(value: any, message: string): boolean | string {
    if (value && typeof value === 'string' && !this.URL_PATTERN.test(value)) {
      return message;
    }
    return true;
  }

  /**
   * Validação de número
   */
  private static validateNumber(value: any, message: string): boolean | string {
    if (value !== null && value !== undefined && isNaN(Number(value))) {
      return message;
    }
    return true;
  }

  /**
   * Validação de inteiro
   */
  private static validateInteger(value: any, message: string): boolean | string {
    if (value !== null && value !== undefined) {
      const num = Number(value);
      if (isNaN(num) || !Number.isInteger(num)) {
        return message;
      }
    }
    return true;
  }

  /**
   * Validação de boolean
   */
  private static validateBoolean(value: any, message: string): boolean | string {
    if (value !== null && value !== undefined && typeof value !== 'boolean') {
      return message;
    }
    return true;
  }

  /**
   * Validação de data
   */
  private static validateDate(value: any, message: string): boolean | string {
    if (value && isNaN(Date.parse(value))) {
      return message;
    }
    return true;
  }

  /**
   * Validação customizada
   */
  private static validateCustom(value: any, rule: ValidationRule): boolean | string {
    if (rule.customValidator) {
      const result = rule.customValidator(value);
      if (typeof result === 'string') {
        return result;
      }
      return result;
    }
    return true;
  }

  /**
   * Obtém valor aninhado do objeto
   */
  private static getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  /**
   * Sanitiza dados conforme schema
   */
  static sanitize(data: any, schema: SanitizationSchema): any {
    const sanitized = { ...data };

    for (const [field, rule] of Object.entries(schema)) {
      const value = this.getNestedValue(sanitized, field);
      if (value !== undefined) {
        const sanitizedValue = this.sanitizeField(value, rule);
        this.setNestedValue(sanitized, field, sanitizedValue);
      }
    }

    return sanitized;
  }

  /**
   * Sanitiza campo individual
   */
  private static sanitizeField(value: any, rule: SanitizationRule): any {
    if (value === null || value === undefined) {
      return value;
    }

    switch (rule.type) {
      case 'trim':
        return typeof value === 'string' ? value.trim() : value;

      case 'lowercase':
        return typeof value === 'string' ? value.toLowerCase() : value;

      case 'uppercase':
        return typeof value === 'string' ? value.toUpperCase() : value;

      case 'removeSpecialChars':
        return typeof value === 'string' ? value.replace(/[^a-zA-Z0-9\s]/g, '') : value;

      case 'escapeHtml':
        return typeof value === 'string' ? this.escapeHtml(value) : value;

      case 'normalizeWhitespace':
        return typeof value === 'string' ? value.replace(/\s+/g, ' ') : value;

      case 'custom':
        return rule.customSanitizer ? rule.customSanitizer(value) : value;

      default:
        return value;
    }
  }

  /**
   * Escapa caracteres HTML
   */
  private static escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Define valor aninhado no objeto
   */
  private static setNestedValue(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    const lastKey = keys.pop()!;
    const target = keys.reduce((current, key) => {
      if (!current[key] || typeof current[key] !== 'object') {
        current[key] = {};
      }
      return current[key];
    }, obj);
    target[lastKey] = value;
  }

  /**
   * Schemas de validação pré-definidos
   */
  static readonly schemas = {
    user: {
      name: [
        { type: 'required', message: 'Nome é obrigatório' },
        { type: 'minLength', value: 2, message: 'Nome deve ter pelo menos 2 caracteres' },
        { type: 'maxLength', value: 100, message: 'Nome deve ter no máximo 100 caracteres' }
      ],
      email: [
        { type: 'required', message: 'Email é obrigatório' },
        { type: 'email', message: 'Email inválido' }
      ],
      password: [
        { type: 'required', message: 'Senha é obrigatória' },
        { type: 'minLength', value: 8, message: 'Senha deve ter pelo menos 8 caracteres' },
        { 
          type: 'custom', 
          message: 'Senha deve conter pelo menos uma letra maiúscula, uma minúscula e um número',
          customValidator: (value) => {
            const hasUpperCase = /[A-Z]/.test(value);
            const hasLowerCase = /[a-z]/.test(value);
            const hasNumber = /\d/.test(value);
            return hasUpperCase && hasLowerCase && hasNumber;
          }
        }
      ]
    },

    contact: {
      phone: [
        { type: 'pattern', value: this.PHONE_PATTERN, message: 'Telefone inválido' }
      ],
      cpf: [
        { type: 'pattern', value: this.CPF_PATTERN, message: 'CPF inválido' },
        { 
          type: 'custom', 
          message: 'CPF inválido',
          customValidator: (value) => this.validateCPF(value)
        }
      ],
      cnpj: [
        { type: 'pattern', value: this.CNPJ_PATTERN, message: 'CNPJ inválido' },
        { 
          type: 'custom', 
          message: 'CNPJ inválido',
          customValidator: (value) => this.validateCNPJ(value)
        }
      ]
    },

    address: {
      zipCode: [
        { type: 'pattern', value: /^\d{5}-?\d{3}$/, message: 'CEP inválido' }
      ],
      street: [
        { type: 'required', message: 'Rua é obrigatória' },
        { type: 'minLength', value: 3, message: 'Rua deve ter pelo menos 3 caracteres' }
      ],
      number: [
        { type: 'required', message: 'Número é obrigatório' }
      ],
      city: [
        { type: 'required', message: 'Cidade é obrigatória' }
      ],
      state: [
        { type: 'required', message: 'Estado é obrigatório' },
        { type: 'pattern', value: /^[A-Z]{2}$/, message: 'Estado deve ter 2 letras' }
      ]
    }
  };

  /**
   * Valida CPF
   */
  private static validateCPF(cpf: string): boolean {
    cpf = cpf.replace(/[^\d]/g, '');
    
    if (cpf.length !== 11) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validar primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    // Validar segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(10))) return false;
    
    return true;
  }

  /**
   * Valida CNPJ
   */
  private static validateCNPJ(cnpj: string): boolean {
    cnpj = cnpj.replace(/[^\d]/g, '');
    
    if (cnpj.length !== 14) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{13}$/.test(cnpj)) return false;
    
    // Validar primeiro dígito verificador
    let sum = 0;
    const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    for (let i = 0; i < 12; i++) {
      sum += parseInt(cnpj.charAt(i)) * weights1[i];
    }
    let remainder = sum % 11;
    let digit1 = remainder < 2 ? 0 : 11 - remainder;
    if (digit1 !== parseInt(cnpj.charAt(12))) return false;
    
    // Validar segundo dígito verificador
    sum = 0;
    const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    for (let i = 0; i < 13; i++) {
      sum += parseInt(cnpj.charAt(i)) * weights2[i];
    }
    remainder = sum % 11;
    let digit2 = remainder < 2 ? 0 : 11 - remainder;
    if (digit2 !== parseInt(cnpj.charAt(13))) return false;
    
    return true;
  }
} 