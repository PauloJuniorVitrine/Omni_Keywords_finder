/**
 * Sistema de Runtime Type Checking
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 8.5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface TypeDefinition {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array' | 'null' | 'undefined' | 'function' | 'date' | 'regexp' | 'promise' | 'error' | 'map' | 'set' | 'weakmap' | 'weakset' | 'arraybuffer' | 'typedarray' | 'dataview' | 'url' | 'formdata' | 'file' | 'blob' | 'event' | 'element' | 'htmlelement' | 'node' | 'nodelist' | 'htmlcollection' | 'window' | 'document' | 'custom';
  required?: boolean;
  nullable?: boolean;
  optional?: boolean;
  defaultValue?: any;
  validator?: (value: any) => boolean | string;
  transform?: (value: any) => any;
  customType?: string;
}

export interface ObjectSchema {
  [key: string]: TypeDefinition | ObjectSchema | ArraySchema;
}

export interface ArraySchema {
  type: 'array';
  items: TypeDefinition | ObjectSchema | ArraySchema;
  minLength?: number;
  maxLength?: number;
  unique?: boolean;
  required?: boolean;
  nullable?: boolean;
  optional?: boolean;
}

export interface ValidationContext {
  path: string[];
  value: any;
  schema: TypeDefinition | ObjectSchema | ArraySchema;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  strict?: boolean;
}

export interface ValidationError {
  path: string;
  message: string;
  code: string;
  value?: any;
  expected?: any;
  received?: any;
}

export interface ValidationWarning {
  path: string;
  message: string;
  code: string;
  value?: any;
  suggestion?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  transformed?: any;
}

export class RuntimeTypeChecker {
  private customTypes: Map<string, (value: any) => boolean> = new Map();
  private customValidators: Map<string, (value: any, context: ValidationContext) => boolean | string> = new Map();
  private customTransformers: Map<string, (value: any) => any> = new Map();

  constructor() {
    this.registerDefaultTypes();
    this.registerDefaultValidators();
    this.registerDefaultTransformers();
  }

  /**
   * Registra tipo customizado
   */
  registerCustomType(name: string, validator: (value: any) => boolean): void {
    this.customTypes.set(name, validator);
  }

  /**
   * Registra validador customizado
   */
  registerCustomValidator(name: string, validator: (value: any, context: ValidationContext) => boolean | string): void {
    this.customValidators.set(name, validator);
  }

  /**
   * Registra transformador customizado
   */
  registerCustomTransformer(name: string, transformer: (value: any) => any): void {
    this.customTransformers.set(name, transformer);
  }

  /**
   * Valida dados contra schema
   */
  validate(data: any, schema: TypeDefinition | ObjectSchema | ArraySchema, options: { strict?: boolean; transform?: boolean } = {}): ValidationResult {
    const context: ValidationContext = {
      path: [],
      value: data,
      schema,
      errors: [],
      warnings: [],
      strict: options.strict
    };

    const result = this.validateValue(context);
    
    if (options.transform && result.valid) {
      result.transformed = this.transformValue(data, schema);
    }

    return result;
  }

  /**
   * Valida valor individual
   */
  private validateValue(context: ValidationContext): ValidationResult {
    const { value, schema, path } = context;
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    // Verificar se é array schema
    if (this.isArraySchema(schema)) {
      return this.validateArray(value, schema, context);
    }

    // Verificar se é object schema
    if (this.isObjectSchema(schema)) {
      return this.validateObject(value, schema, context);
    }

    // Verificar se é type definition
    if (this.isTypeDefinition(schema)) {
      return this.validateTypeDefinition(value, schema, context);
    }

    // Schema inválido
    result.errors.push({
      path: path.join('.'),
      message: 'Schema inválido',
      code: 'INVALID_SCHEMA',
      value
    });
    result.valid = false;

    return result;
  }

  /**
   * Valida type definition
   */
  private validateTypeDefinition(value: any, schema: TypeDefinition, context: ValidationContext): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    const path = context.path.join('.');

    // Verificar se é obrigatório
    if (schema.required && (value === null || value === undefined)) {
      result.errors.push({
        path,
        message: 'Campo obrigatório',
        code: 'REQUIRED_FIELD',
        value,
        expected: 'valor não nulo'
      });
      result.valid = false;
      return result;
    }

    // Verificar se é opcional e está ausente
    if (schema.optional && (value === null || value === undefined)) {
      return result; // Campo opcional ausente é válido
    }

    // Verificar se é nullable
    if (value === null) {
      if (!schema.nullable) {
        result.errors.push({
          path,
          message: 'Valor não pode ser null',
          code: 'NULL_NOT_ALLOWED',
          value,
          expected: schema.type
        });
        result.valid = false;
      }
      return result;
    }

    // Verificar tipo
    const typeValid = this.checkType(value, schema.type, schema.customType);
    if (!typeValid) {
      result.errors.push({
        path,
        message: `Tipo inválido. Esperado: ${schema.type}, Recebido: ${typeof value}`,
        code: 'TYPE_MISMATCH',
        value,
        expected: schema.type,
        received: typeof value
      });
      result.valid = false;
    }

    // Executar validador customizado
    if (schema.validator) {
      const validationResult = schema.validator(value);
      if (typeof validationResult === 'string') {
        result.errors.push({
          path,
          message: validationResult,
          code: 'CUSTOM_VALIDATION_FAILED',
          value
        });
        result.valid = false;
      } else if (!validationResult) {
        result.errors.push({
          path,
          message: 'Validação customizada falhou',
          code: 'CUSTOM_VALIDATION_FAILED',
          value
        });
        result.valid = false;
      }
    }

    // Executar validador customizado por nome
    if (schema.customType && this.customValidators.has(schema.customType)) {
      const validator = this.customValidators.get(schema.customType)!;
      const validationResult = validator(value, context);
      if (typeof validationResult === 'string') {
        result.errors.push({
          path,
          message: validationResult,
          code: 'CUSTOM_VALIDATION_FAILED',
          value
        });
        result.valid = false;
      } else if (!validationResult) {
        result.errors.push({
          path,
          message: `Validação customizada '${schema.customType}' falhou`,
          code: 'CUSTOM_VALIDATION_FAILED',
          value
        });
        result.valid = false;
      }
    }

    return result;
  }

  /**
   * Valida array
   */
  private validateArray(value: any, schema: ArraySchema, context: ValidationContext): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    const path = context.path.join('.');

    // Verificar se é array
    if (!Array.isArray(value)) {
      result.errors.push({
        path,
        message: 'Valor deve ser um array',
        code: 'NOT_ARRAY',
        value,
        expected: 'array'
      });
      result.valid = false;
      return result;
    }

    // Verificar comprimento mínimo
    if (schema.minLength && value.length < schema.minLength) {
      result.errors.push({
        path,
        message: `Array deve ter pelo menos ${schema.minLength} itens`,
        code: 'ARRAY_TOO_SHORT',
        value: value.length,
        expected: `>= ${schema.minLength}`
      });
      result.valid = false;
    }

    // Verificar comprimento máximo
    if (schema.maxLength && value.length > schema.maxLength) {
      result.errors.push({
        path,
        message: `Array deve ter no máximo ${schema.maxLength} itens`,
        code: 'ARRAY_TOO_LONG',
        value: value.length,
        expected: `<= ${schema.maxLength}`
      });
      result.valid = false;
    }

    // Verificar itens únicos
    if (schema.unique) {
      const seen = new Set();
      for (let i = 0; i < value.length; i++) {
        const item = value[i];
        const itemStr = JSON.stringify(item);
        if (seen.has(itemStr)) {
          result.errors.push({
            path: `${path}[${i}]`,
            message: 'Item duplicado encontrado',
            code: 'DUPLICATE_ITEM',
            value: item
          });
          result.valid = false;
        }
        seen.add(itemStr);
      }
    }

    // Validar cada item
    for (let i = 0; i < value.length; i++) {
      const itemContext: ValidationContext = {
        ...context,
        path: [...context.path, `[${i}]`],
        value: value[i],
        schema: schema.items
      };

      const itemResult = this.validateValue(itemContext);
      result.errors.push(...itemResult.errors);
      result.warnings.push(...itemResult.warnings);
      if (!itemResult.valid) {
        result.valid = false;
      }
    }

    return result;
  }

  /**
   * Valida objeto
   */
  private validateObject(value: any, schema: ObjectSchema, context: ValidationContext): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    const path = context.path.join('.');

    // Verificar se é objeto
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      result.errors.push({
        path,
        message: 'Valor deve ser um objeto',
        code: 'NOT_OBJECT',
        value,
        expected: 'object'
      });
      result.valid = false;
      return result;
    }

    // Validar cada propriedade
    for (const [key, propSchema] of Object.entries(schema)) {
      const propContext: ValidationContext = {
        ...context,
        path: [...context.path, key],
        value: value[key],
        schema: propSchema
      };

      const propResult = this.validateValue(propContext);
      result.errors.push(...propResult.errors);
      result.warnings.push(...propResult.warnings);
      if (!propResult.valid) {
        result.valid = false;
      }
    }

    // Verificar propriedades extras em modo estrito
    if (context.strict) {
      const schemaKeys = Object.keys(schema);
      const valueKeys = Object.keys(value);
      const extraKeys = valueKeys.filter(key => !schemaKeys.includes(key));

      if (extraKeys.length > 0) {
        result.warnings.push({
          path,
          message: `Propriedades extras encontradas: ${extraKeys.join(', ')}`,
          code: 'EXTRA_PROPERTIES',
          value: extraKeys,
          suggestion: 'Considere remover propriedades não definidas no schema'
        });
      }
    }

    return result;
  }

  /**
   * Verifica tipo
   */
  private checkType(value: any, type: string, customType?: string): boolean {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      case 'array':
        return Array.isArray(value);
      case 'null':
        return value === null;
      case 'undefined':
        return value === undefined;
      case 'function':
        return typeof value === 'function';
      case 'date':
        return value instanceof Date;
      case 'regexp':
        return value instanceof RegExp;
      case 'promise':
        return value instanceof Promise;
      case 'error':
        return value instanceof Error;
      case 'map':
        return value instanceof Map;
      case 'set':
        return value instanceof Set;
      case 'weakmap':
        return value instanceof WeakMap;
      case 'weakset':
        return value instanceof WeakSet;
      case 'arraybuffer':
        return value instanceof ArrayBuffer;
      case 'typedarray':
        return ArrayBuffer.isView(value) && !(value instanceof DataView);
      case 'dataview':
        return value instanceof DataView;
      case 'url':
        return value instanceof URL;
      case 'formdata':
        return value instanceof FormData;
      case 'file':
        return value instanceof File;
      case 'blob':
        return value instanceof Blob;
      case 'event':
        return value instanceof Event;
      case 'element':
        return value instanceof Element;
      case 'htmlelement':
        return value instanceof HTMLElement;
      case 'node':
        return value instanceof Node;
      case 'nodelist':
        return value instanceof NodeList;
      case 'htmlcollection':
        return value instanceof HTMLCollection;
      case 'window':
        return value === window;
      case 'document':
        return value === document;
      case 'custom':
        if (customType && this.customTypes.has(customType)) {
          return this.customTypes.get(customType)!(value);
        }
        return false;
      default:
        return false;
    }
  }

  /**
   * Transforma valor
   */
  private transformValue(value: any, schema: TypeDefinition | ObjectSchema | ArraySchema): any {
    if (this.isTypeDefinition(schema) && schema.transform) {
      return schema.transform(value);
    }

    if (this.isTypeDefinition(schema) && schema.customType && this.customTransformers.has(schema.customType)) {
      return this.customTransformers.get(schema.customType)!(value);
    }

    if (this.isArraySchema(schema)) {
      if (Array.isArray(value)) {
        return value.map(item => this.transformValue(item, schema.items));
      }
    }

    if (this.isObjectSchema(schema)) {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        const transformed: any = {};
        for (const [key, propSchema] of Object.entries(schema)) {
          if (key in value) {
            transformed[key] = this.transformValue(value[key], propSchema);
          }
        }
        return transformed;
      }
    }

    return value;
  }

  /**
   * Verifica se é array schema
   */
  private isArraySchema(schema: any): schema is ArraySchema {
    return schema && typeof schema === 'object' && schema.type === 'array';
  }

  /**
   * Verifica se é object schema
   */
  private isObjectSchema(schema: any): schema is ObjectSchema {
    return schema && typeof schema === 'object' && !this.isArraySchema(schema) && !this.isTypeDefinition(schema);
  }

  /**
   * Verifica se é type definition
   */
  private isTypeDefinition(schema: any): schema is TypeDefinition {
    return schema && typeof schema === 'object' && 'type' in schema && typeof schema.type === 'string';
  }

  /**
   * Registra tipos padrão
   */
  private registerDefaultTypes(): void {
    // Email
    this.registerCustomType('email', (value) => {
      if (typeof value !== 'string') return false;
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailPattern.test(value);
    });

    // URL
    this.registerCustomType('url', (value) => {
      if (typeof value !== 'string') return false;
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    });

    // UUID
    this.registerCustomType('uuid', (value) => {
      if (typeof value !== 'string') return false;
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      return uuidPattern.test(value);
    });

    // CPF
    this.registerCustomType('cpf', (value) => {
      if (typeof value !== 'string') return false;
      const cpf = value.replace(/\D/g, '');
      if (cpf.length !== 11) return false;
      if (/^(\d)\1{10}$/.test(cpf)) return false;
      
      let sum = 0;
      for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
      }
      let remainder = (sum * 10) % 11;
      if (remainder === 10 || remainder === 11) remainder = 0;
      if (remainder !== parseInt(cpf.charAt(9))) return false;
      
      sum = 0;
      for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
      }
      remainder = (sum * 10) % 11;
      if (remainder === 10 || remainder === 11) remainder = 0;
      if (remainder !== parseInt(cpf.charAt(10))) return false;
      
      return true;
    });

    // CNPJ
    this.registerCustomType('cnpj', (value) => {
      if (typeof value !== 'string') return false;
      const cnpj = value.replace(/\D/g, '');
      if (cnpj.length !== 14) return false;
      if (/^(\d)\1{13}$/.test(cnpj)) return false;
      
      let sum = 0;
      const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
      for (let i = 0; i < 12; i++) {
        sum += parseInt(cnpj.charAt(i)) * weights1[i];
      }
      let remainder = sum % 11;
      let digit1 = remainder < 2 ? 0 : 11 - remainder;
      if (digit1 !== parseInt(cnpj.charAt(12))) return false;
      
      sum = 0;
      const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
      for (let i = 0; i < 13; i++) {
        sum += parseInt(cnpj.charAt(i)) * weights2[i];
      }
      remainder = sum % 11;
      let digit2 = remainder < 2 ? 0 : 11 - remainder;
      if (digit2 !== parseInt(cnpj.charAt(13))) return false;
      
      return true;
    });

    // Data
    this.registerCustomType('date', (value) => {
      if (typeof value !== 'string') return false;
      return !isNaN(Date.parse(value));
    });

    // Telefone
    this.registerCustomType('phone', (value) => {
      if (typeof value !== 'string') return false;
      const phonePattern = /^[\+]?[1-9][\d]{0,15}$/;
      return phonePattern.test(value.replace(/\D/g, ''));
    });

    // CEP
    this.registerCustomType('cep', (value) => {
      if (typeof value !== 'string') return false;
      const cepPattern = /^\d{5}-?\d{3}$/;
      return cepPattern.test(value);
    });
  }

  /**
   * Registra validadores padrão
   */
  private registerDefaultValidators(): void {
    // Validador de comprimento mínimo
    this.registerCustomValidator('minLength', (value, context) => {
      if (typeof value !== 'string') return 'Valor deve ser string';
      const minLength = context.schema as any;
      if (value.length < minLength) {
        return `String deve ter pelo menos ${minLength} caracteres`;
      }
      return true;
    });

    // Validador de comprimento máximo
    this.registerCustomValidator('maxLength', (value, context) => {
      if (typeof value !== 'string') return 'Valor deve ser string';
      const maxLength = context.schema as any;
      if (value.length > maxLength) {
        return `String deve ter no máximo ${maxLength} caracteres`;
      }
      return true;
    });

    // Validador de valor mínimo
    this.registerCustomValidator('min', (value, context) => {
      if (typeof value !== 'number') return 'Valor deve ser número';
      const min = context.schema as any;
      if (value < min) {
        return `Número deve ser maior ou igual a ${min}`;
      }
      return true;
    });

    // Validador de valor máximo
    this.registerCustomValidator('max', (value, context) => {
      if (typeof value !== 'number') return 'Valor deve ser número';
      const max = context.schema as any;
      if (value > max) {
        return `Número deve ser menor ou igual a ${max}`;
      }
      return true;
    });
  }

  /**
   * Registra transformadores padrão
   */
  private registerDefaultTransformers(): void {
    // Transformador para trim
    this.registerCustomTransformer('trim', (value) => {
      if (typeof value === 'string') {
        return value.trim();
      }
      return value;
    });

    // Transformador para lowercase
    this.registerCustomTransformer('lowercase', (value) => {
      if (typeof value === 'string') {
        return value.toLowerCase();
      }
      return value;
    });

    // Transformador para uppercase
    this.registerCustomTransformer('uppercase', (value) => {
      if (typeof value === 'string') {
        return value.toUpperCase();
      }
      return value;
    });

    // Transformador para número
    this.registerCustomTransformer('number', (value) => {
      if (typeof value === 'string') {
        const num = Number(value);
        return isNaN(num) ? value : num;
      }
      return value;
    });

    // Transformador para boolean
    this.registerCustomTransformer('boolean', (value) => {
      if (typeof value === 'string') {
        return value.toLowerCase() === 'true' || value === '1';
      }
      return Boolean(value);
    });
  }

  /**
   * Schemas pré-definidos
   */
  static readonly schemas = {
    user: {
      id: { type: 'string', customType: 'uuid', required: true },
      name: { type: 'string', required: true, validator: (value) => value.length >= 2 ? true : 'Nome deve ter pelo menos 2 caracteres' },
      email: { type: 'string', customType: 'email', required: true },
      cpf: { type: 'string', customType: 'cpf', optional: true },
      createdAt: { type: 'string', customType: 'date', required: true },
      isActive: { type: 'boolean', required: true, defaultValue: true }
    },

    product: {
      id: { type: 'string', customType: 'uuid', required: true },
      name: { type: 'string', required: true, validator: (value) => value.length >= 1 ? true : 'Nome é obrigatório' },
      description: { type: 'string', required: true },
      price: { type: 'number', required: true, validator: (value) => value >= 0 ? true : 'Preço deve ser positivo' },
      category: { type: 'string', required: true },
      tags: {
        type: 'array',
        items: { type: 'string' },
        unique: true,
        required: true
      },
      inStock: { type: 'boolean', required: true, defaultValue: true }
    },

    order: {
      id: { type: 'string', customType: 'uuid', required: true },
      userId: { type: 'string', customType: 'uuid', required: true },
      items: {
        type: 'array',
        items: {
          productId: { type: 'string', customType: 'uuid', required: true },
          quantity: { type: 'number', required: true, validator: (value) => value > 0 ? true : 'Quantidade deve ser positiva' },
          price: { type: 'number', required: true, validator: (value) => value >= 0 ? true : 'Preço deve ser positivo' }
        },
        required: true
      },
      total: { type: 'number', required: true, validator: (value) => value >= 0 ? true : 'Total deve ser positivo' },
      status: { type: 'string', required: true, validator: (value) => ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'].includes(value) ? true : 'Status inválido' },
      createdAt: { type: 'string', customType: 'date', required: true },
      updatedAt: { type: 'string', customType: 'date', required: true }
    }
  };
} 