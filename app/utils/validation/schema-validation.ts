/**
 * Sistema de Schema Validation
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 8.3
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface JsonSchema {
  $schema?: string;
  $id?: string;
  title?: string;
  description?: string;
  type?: 'object' | 'array' | 'string' | 'number' | 'integer' | 'boolean' | 'null';
  properties?: { [key: string]: JsonSchema };
  required?: string[];
  additionalProperties?: boolean | JsonSchema;
  items?: JsonSchema | JsonSchema[];
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  format?: string;
  minimum?: number;
  maximum?: number;
  exclusiveMinimum?: boolean | number;
  exclusiveMaximum?: boolean | number;
  multipleOf?: number;
  enum?: any[];
  const?: any;
  allOf?: JsonSchema[];
  anyOf?: JsonSchema[];
  oneOf?: JsonSchema[];
  not?: JsonSchema;
  if?: JsonSchema;
  then?: JsonSchema;
  else?: JsonSchema;
  dependencies?: { [key: string]: string[] | JsonSchema };
  propertyNames?: JsonSchema;
  minProperties?: number;
  maxProperties?: number;
  definitions?: { [key: string]: JsonSchema };
  $ref?: string;
}

export interface ValidationError {
  path: string;
  message: string;
  code: string;
  value?: any;
  schema?: JsonSchema;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

export class SchemaValidator {
  private schemas: Map<string, JsonSchema> = new Map();
  private customFormats: Map<string, (value: any) => boolean> = new Map();
  private customValidators: Map<string, (value: any, schema: JsonSchema) => boolean | string> = new Map();

  constructor() {
    this.registerDefaultFormats();
    this.registerDefaultValidators();
  }

  /**
   * Registra schema para validação
   */
  registerSchema(id: string, schema: JsonSchema): void {
    this.schemas.set(id, schema);
  }

  /**
   * Registra formato customizado
   */
  registerFormat(name: string, validator: (value: any) => boolean): void {
    this.customFormats.set(name, validator);
  }

  /**
   * Registra validador customizado
   */
  registerValidator(name: string, validator: (value: any, schema: JsonSchema) => boolean | string): void {
    this.customValidators.set(name, validator);
  }

  /**
   * Valida dados contra schema
   */
  validate(data: any, schema: JsonSchema): ValidationResult {
    const result: ValidationResult = {
      valid: true,
      errors: [],
      warnings: []
    };

    try {
      this.validateValue(data, schema, '#', result);
    } catch (error) {
      result.errors.push({
        path: '#',
        message: `Erro de validação: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
        code: 'VALIDATION_ERROR'
      });
      result.valid = false;
    }

    return result;
  }

  /**
   * Valida valor individual
   */
  private validateValue(value: any, schema: JsonSchema, path: string, result: ValidationResult): void {
    // Resolver referências
    if (schema.$ref) {
      const resolvedSchema = this.resolveReference(schema.$ref);
      if (resolvedSchema) {
        this.validateValue(value, resolvedSchema, path, result);
        return;
      }
    }

    // Validar tipo
    if (schema.type) {
      this.validateType(value, schema.type, path, result);
    }

    // Validar formato
    if (schema.format && typeof value === 'string') {
      this.validateFormat(value, schema.format, path, result);
    }

    // Validar enum
    if (schema.enum && !schema.enum.includes(value)) {
      result.errors.push({
        path,
        message: `Valor deve ser um dos: ${schema.enum.join(', ')}`,
        code: 'ENUM_MISMATCH',
        value,
        schema
      });
      result.valid = false;
    }

    // Validar const
    if (schema.const !== undefined && value !== schema.const) {
      result.errors.push({
        path,
        message: `Valor deve ser exatamente: ${schema.const}`,
        code: 'CONST_MISMATCH',
        value,
        schema
      });
      result.valid = false;
    }

    // Validar objeto
    if (schema.type === 'object' && typeof value === 'object' && value !== null && !Array.isArray(value)) {
      this.validateObject(value, schema, path, result);
    }

    // Validar array
    if (schema.type === 'array' && Array.isArray(value)) {
      this.validateArray(value, schema, path, result);
    }

    // Validar string
    if (schema.type === 'string' && typeof value === 'string') {
      this.validateString(value, schema, path, result);
    }

    // Validar número
    if ((schema.type === 'number' || schema.type === 'integer') && typeof value === 'number') {
      this.validateNumber(value, schema, path, result);
    }

    // Validar boolean
    if (schema.type === 'boolean' && typeof value === 'boolean') {
      // Boolean não tem validações específicas além do tipo
    }

    // Validar null
    if (schema.type === 'null' && value !== null) {
      result.errors.push({
        path,
        message: 'Valor deve ser null',
        code: 'NULL_REQUIRED',
        value,
        schema
      });
      result.valid = false;
    }

    // Validar condições (if/then/else)
    if (schema.if) {
      const ifResult: ValidationResult = { valid: true, errors: [], warnings: [] };
      this.validateValue(value, schema.if, path, ifResult);
      
      if (ifResult.valid && schema.then) {
        this.validateValue(value, schema.then, path, result);
      } else if (!ifResult.valid && schema.else) {
        this.validateValue(value, schema.else, path, result);
      }
    }

    // Validar allOf
    if (schema.allOf) {
      schema.allOf.forEach((subSchema, index) => {
        this.validateValue(value, subSchema, `${path}/allOf/${index}`, result);
      });
    }

    // Validar anyOf
    if (schema.anyOf) {
      const anyValid = schema.anyOf.some((subSchema, index) => {
        const subResult: ValidationResult = { valid: true, errors: [], warnings: [] };
        this.validateValue(value, subSchema, `${path}/anyOf/${index}`, subResult);
        return subResult.valid;
      });

      if (!anyValid) {
        result.errors.push({
          path,
          message: 'Valor deve corresponder a pelo menos um dos schemas',
          code: 'ANYOF_MISMATCH',
          value,
          schema
        });
        result.valid = false;
      }
    }

    // Validar oneOf
    if (schema.oneOf) {
      const validCount = schema.oneOf.filter((subSchema, index) => {
        const subResult: ValidationResult = { valid: true, errors: [], warnings: [] };
        this.validateValue(value, subSchema, `${path}/oneOf/${index}`, subResult);
        return subResult.valid;
      }).length;

      if (validCount !== 1) {
        result.errors.push({
          path,
          message: `Valor deve corresponder exatamente a um dos schemas (${validCount} válidos encontrados)`,
          code: 'ONEOF_MISMATCH',
          value,
          schema
        });
        result.valid = false;
      }
    }

    // Validar not
    if (schema.not) {
      const notResult: ValidationResult = { valid: true, errors: [], warnings: [] };
      this.validateValue(value, schema.not, `${path}/not`, notResult);
      
      if (notResult.valid) {
        result.errors.push({
          path,
          message: 'Valor não deve corresponder ao schema negado',
          code: 'NOT_MISMATCH',
          value,
          schema
        });
        result.valid = false;
      }
    }
  }

  /**
   * Valida tipo
   */
  private validateType(value: any, type: string, path: string, result: ValidationResult): void {
    let isValid = false;

    switch (type) {
      case 'object':
        isValid = typeof value === 'object' && value !== null && !Array.isArray(value);
        break;
      case 'array':
        isValid = Array.isArray(value);
        break;
      case 'string':
        isValid = typeof value === 'string';
        break;
      case 'number':
        isValid = typeof value === 'number' && !isNaN(value);
        break;
      case 'integer':
        isValid = typeof value === 'number' && Number.isInteger(value);
        break;
      case 'boolean':
        isValid = typeof value === 'boolean';
        break;
      case 'null':
        isValid = value === null;
        break;
    }

    if (!isValid) {
      result.errors.push({
        path,
        message: `Tipo deve ser ${type}`,
        code: 'TYPE_MISMATCH',
        value,
        schema: { type }
      });
      result.valid = false;
    }
  }

  /**
   * Valida objeto
   */
  private validateObject(obj: any, schema: JsonSchema, path: string, result: ValidationResult): void {
    // Validar propriedades obrigatórias
    if (schema.required) {
      for (const requiredProp of schema.required) {
        if (!(requiredProp in obj)) {
          result.errors.push({
            path: `${path}/${requiredProp}`,
            message: `Propriedade obrigatória ausente: ${requiredProp}`,
            code: 'REQUIRED_PROPERTY_MISSING',
            schema
          });
          result.valid = false;
        }
      }
    }

    // Validar propriedades
    if (schema.properties) {
      for (const [propName, propValue] of Object.entries(obj)) {
        const propSchema = schema.properties[propName];
        if (propSchema) {
          this.validateValue(propValue, propSchema, `${path}/${propName}`, result);
        } else if (schema.additionalProperties === false) {
          result.errors.push({
            path: `${path}/${propName}`,
            message: `Propriedade não permitida: ${propName}`,
            code: 'ADDITIONAL_PROPERTY_FORBIDDEN',
            value: propValue,
            schema
          });
          result.valid = false;
        } else if (typeof schema.additionalProperties === 'object') {
          this.validateValue(propValue, schema.additionalProperties, `${path}/${propName}`, result);
        }
      }
    }

    // Validar número de propriedades
    const propCount = Object.keys(obj).length;
    if (schema.minProperties && propCount < schema.minProperties) {
      result.errors.push({
        path,
        message: `Objeto deve ter pelo menos ${schema.minProperties} propriedades`,
        code: 'MIN_PROPERTIES',
        value: propCount,
        schema
      });
      result.valid = false;
    }

    if (schema.maxProperties && propCount > schema.maxProperties) {
      result.errors.push({
        path,
        message: `Objeto deve ter no máximo ${schema.maxProperties} propriedades`,
        code: 'MAX_PROPERTIES',
        value: propCount,
        schema
      });
      result.valid = false;
    }

    // Validar dependências
    if (schema.dependencies) {
      for (const [propName, dependency] of Object.entries(schema.dependencies)) {
        if (propName in obj) {
          if (Array.isArray(dependency)) {
            // Dependência de propriedades
            for (const depProp of dependency) {
              if (!(depProp in obj)) {
                result.errors.push({
                  path: `${path}/${depProp}`,
                  message: `Propriedade ${depProp} é obrigatória quando ${propName} está presente`,
                  code: 'DEPENDENCY_MISSING',
                  schema
                });
                result.valid = false;
              }
            }
          } else {
            // Dependência de schema
            this.validateValue(obj, dependency, path, result);
          }
        }
      }
    }
  }

  /**
   * Valida array
   */
  private validateArray(arr: any[], schema: JsonSchema, path: string, result: ValidationResult): void {
    // Validar número de itens
    if (schema.minItems && arr.length < schema.minItems) {
      result.errors.push({
        path,
        message: `Array deve ter pelo menos ${schema.minItems} itens`,
        code: 'MIN_ITEMS',
        value: arr.length,
        schema
      });
      result.valid = false;
    }

    if (schema.maxItems && arr.length > schema.maxItems) {
      result.errors.push({
        path,
        message: `Array deve ter no máximo ${schema.maxItems} itens`,
        code: 'MAX_ITEMS',
        value: arr.length,
        schema
      });
      result.valid = false;
    }

    // Validar itens
    if (schema.items) {
      if (Array.isArray(schema.items)) {
        // Schema de tupla
        for (let i = 0; i < Math.min(arr.length, schema.items.length); i++) {
          this.validateValue(arr[i], schema.items[i], `${path}/${i}`, result);
        }
      } else {
        // Schema único para todos os itens
        for (let i = 0; i < arr.length; i++) {
          this.validateValue(arr[i], schema.items, `${path}/${i}`, result);
        }
      }
    }

    // Validar itens únicos
    if (schema.uniqueItems) {
      const seen = new Set();
      for (let i = 0; i < arr.length; i++) {
        const item = arr[i];
        const itemStr = JSON.stringify(item);
        if (seen.has(itemStr)) {
          result.errors.push({
            path: `${path}/${i}`,
            message: 'Array deve conter apenas itens únicos',
            code: 'UNIQUE_ITEMS',
            value: item,
            schema
          });
          result.valid = false;
        }
        seen.add(itemStr);
      }
    }
  }

  /**
   * Valida string
   */
  private validateString(str: string, schema: JsonSchema, path: string, result: ValidationResult): void {
    // Validar comprimento
    if (schema.minLength && str.length < schema.minLength) {
      result.errors.push({
        path,
        message: `String deve ter pelo menos ${schema.minLength} caracteres`,
        code: 'MIN_LENGTH',
        value: str.length,
        schema
      });
      result.valid = false;
    }

    if (schema.maxLength && str.length > schema.maxLength) {
      result.errors.push({
        path,
        message: `String deve ter no máximo ${schema.maxLength} caracteres`,
        code: 'MAX_LENGTH',
        value: str.length,
        schema
      });
      result.valid = false;
    }

    // Validar padrão
    if (schema.pattern) {
      const regex = new RegExp(schema.pattern);
      if (!regex.test(str)) {
        result.errors.push({
          path,
          message: `String deve corresponder ao padrão: ${schema.pattern}`,
          code: 'PATTERN_MISMATCH',
          value: str,
          schema
        });
        result.valid = false;
      }
    }
  }

  /**
   * Valida número
   */
  private validateNumber(num: number, schema: JsonSchema, path: string, result: ValidationResult): void {
    // Validar mínimo
    if (schema.minimum !== undefined) {
      const min = typeof schema.exclusiveMinimum === 'boolean' ? schema.minimum : schema.exclusiveMinimum;
      const exclusive = typeof schema.exclusiveMinimum === 'boolean' ? schema.exclusiveMinimum : false;
      
      if (exclusive ? num <= min : num < min) {
        result.errors.push({
          path,
          message: `Número deve ser ${exclusive ? 'maior que' : 'maior ou igual a'} ${min}`,
          code: exclusive ? 'EXCLUSIVE_MINIMUM' : 'MINIMUM',
          value: num,
          schema
        });
        result.valid = false;
      }
    }

    // Validar máximo
    if (schema.maximum !== undefined) {
      const max = typeof schema.exclusiveMaximum === 'boolean' ? schema.maximum : schema.exclusiveMaximum;
      const exclusive = typeof schema.exclusiveMaximum === 'boolean' ? schema.exclusiveMaximum : false;
      
      if (exclusive ? num >= max : num > max) {
        result.errors.push({
          path,
          message: `Número deve ser ${exclusive ? 'menor que' : 'menor ou igual a'} ${max}`,
          code: exclusive ? 'EXCLUSIVE_MAXIMUM' : 'MAXIMUM',
          value: num,
          schema
        });
        result.valid = false;
      }
    }

    // Validar múltiplo
    if (schema.multipleOf && num % schema.multipleOf !== 0) {
      result.errors.push({
        path,
        message: `Número deve ser múltiplo de ${schema.multipleOf}`,
        code: 'MULTIPLE_OF',
        value: num,
        schema
      });
      result.valid = false;
    }
  }

  /**
   * Valida formato
   */
  private validateFormat(value: string, format: string, path: string, result: ValidationResult): void {
    const validator = this.customFormats.get(format);
    if (validator && !validator(value)) {
      result.errors.push({
        path,
        message: `Valor deve ter formato ${format}`,
        code: 'FORMAT_MISMATCH',
        value,
        schema: { format }
      });
      result.valid = false;
    }
  }

  /**
   * Resolve referência de schema
   */
  private resolveReference(ref: string): JsonSchema | null {
    if (ref.startsWith('#')) {
      // Referência local
      const id = ref.substring(1);
      return this.schemas.get(id) || null;
    }
    
    // Referência externa (não implementada completamente)
    return null;
  }

  /**
   * Registra formatos padrão
   */
  private registerDefaultFormats(): void {
    // Email
    this.registerFormat('email', (value) => {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    });

    // URI
    this.registerFormat('uri', (value) => {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    });

    // Data
    this.registerFormat('date', (value) => {
      return !isNaN(Date.parse(value));
    });

    // Data-time
    this.registerFormat('date-time', (value) => {
      return !isNaN(Date.parse(value));
    });

    // UUID
    this.registerFormat('uuid', (value) => {
      return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
    });

    // CPF
    this.registerFormat('cpf', (value) => {
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
  }

  /**
   * Registra validadores padrão
   */
  private registerDefaultValidators(): void {
    // Validador customizado para CPF
    this.registerValidator('cpf', (value) => {
      if (typeof value !== 'string') return false;
      return this.customFormats.get('cpf')!(value);
    });
  }

  /**
   * Schemas pré-definidos
   */
  static readonly predefinedSchemas = {
    user: {
      type: 'object',
      properties: {
        id: { type: 'string', format: 'uuid' },
        name: { type: 'string', minLength: 2, maxLength: 100 },
        email: { type: 'string', format: 'email' },
        cpf: { type: 'string', format: 'cpf' },
        createdAt: { type: 'string', format: 'date-time' },
        isActive: { type: 'boolean' }
      },
      required: ['name', 'email'],
      additionalProperties: false
    },

    address: {
      type: 'object',
      properties: {
        street: { type: 'string', minLength: 3 },
        number: { type: 'string' },
        complement: { type: 'string' },
        neighborhood: { type: 'string' },
        city: { type: 'string' },
        state: { type: 'string', pattern: '^[A-Z]{2}$' },
        zipCode: { type: 'string', pattern: '^\\d{5}-?\\d{3}$' }
      },
      required: ['street', 'number', 'city', 'state', 'zipCode']
    },

    product: {
      type: 'object',
      properties: {
        id: { type: 'string', format: 'uuid' },
        name: { type: 'string', minLength: 1, maxLength: 200 },
        description: { type: 'string', maxLength: 1000 },
        price: { type: 'number', minimum: 0 },
        category: { type: 'string' },
        tags: { type: 'array', items: { type: 'string' }, uniqueItems: true },
        inStock: { type: 'boolean' }
      },
      required: ['name', 'price']
    }
  };
} 