/**
 * 🔍 Contract Validator Utility
 * 🎯 Objetivo: Validação client-side de contratos com detecção de incompatibilidades
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: CONTRACT_VALIDATOR_UTIL_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import { z } from 'zod';

// Tipos para validação de contratos
export interface ContractDefinition {
  name: string;
  version: string;
  schema: any;
  description: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  hash: string;
  dependencies?: string[];
  breakingChanges?: string[];
}

export interface ContractValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  compatibility: CompatibilityStatus;
  suggestions: string[];
  timestamp: string;
}

export interface ValidationError {
  path: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  code: string;
  details?: any;
}

export interface ValidationWarning {
  path: string;
  message: string;
  type: 'deprecation' | 'performance' | 'security' | 'compatibility';
  recommendation: string;
}

export interface CompatibilityStatus {
  isCompatible: boolean;
  breakingChanges: BreakingChange[];
  versionMismatches: VersionMismatch[];
  schemaDrift: SchemaDrift[];
}

export interface BreakingChange {
  field: string;
  oldType: string;
  newType: string;
  impact: 'high' | 'medium' | 'low';
  migrationGuide?: string;
}

export interface VersionMismatch {
  expectedVersion: string;
  actualVersion: string;
  component: string;
  severity: 'error' | 'warning';
}

export interface SchemaDrift {
  field: string;
  expectedSchema: any;
  actualSchema: any;
  driftType: 'added' | 'removed' | 'modified';
}

export interface ContractValidationOptions {
  strictMode?: boolean;
  allowDeprecated?: boolean;
  validateTypes?: boolean;
  checkCompatibility?: boolean;
  autoFix?: boolean;
  reportLevel?: 'error' | 'warning' | 'info';
}

// Schemas de validação
const ContractDefinitionSchema = z.object({
  name: z.string().min(1),
  version: z.string().regex(/^\d+\.\d+\.\d+$/),
  schema: z.any(),
  description: z.string(),
  tags: z.array(z.string()),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  hash: z.string().min(1),
  dependencies: z.array(z.string()).optional(),
  breakingChanges: z.array(z.string()).optional()
});

export class ContractValidator {
  private contracts: Map<string, ContractDefinition> = new Map();
  private schemas: Map<string, z.ZodSchema> = new Map();
  private validationCache: Map<string, ContractValidationResult> = new Map();
  private options: ContractValidationOptions;

  constructor(options: ContractValidationOptions = {}) {
    this.options = {
      strictMode: false,
      allowDeprecated: true,
      validateTypes: true,
      checkCompatibility: true,
      autoFix: false,
      reportLevel: 'warning',
      ...options
    };
  }

  /**
   * Registra um contrato para validação
   */
  registerContract(contract: ContractDefinition): void {
    try {
      // Validar definição do contrato
      const validatedContract = ContractDefinitionSchema.parse(contract);
      
      // Gerar schema Zod
      const zodSchema = this.generateZodSchema(contract.schema);
      
      // Armazenar
      this.contracts.set(contract.name, validatedContract);
      this.schemas.set(contract.name, zodSchema);
      
      console.info(`[CONTRACT_VALIDATOR] Contrato registrado: ${contract.name} v${contract.version}`);
      
    } catch (error) {
      console.error(`[CONTRACT_VALIDATOR] Erro ao registrar contrato ${contract.name}:`, error);
      throw error;
    }
  }

  /**
   * Valida dados contra um contrato específico
   */
  validateData(
    contractName: string, 
    data: any, 
    options?: Partial<ContractValidationOptions>
  ): ContractValidationResult {
    const mergedOptions = { ...this.options, ...options };
    const cacheKey = `${contractName}_${JSON.stringify(data)}_${JSON.stringify(mergedOptions)}`;
    
    // Verificar cache
    if (this.validationCache.has(cacheKey)) {
      return this.validationCache.get(cacheKey)!;
    }

    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    const suggestions: string[] = [];

    try {
      const contract = this.contracts.get(contractName);
      if (!contract) {
        throw new Error(`Contrato não encontrado: ${contractName}`);
      }

      const schema = this.schemas.get(contractName);
      if (!schema) {
        throw new Error(`Schema não encontrado para: ${contractName}`);
      }

      // Validar dados
      const validationResult = schema.safeParse(data);
      
      if (!validationResult.success) {
        validationResult.error.issues.forEach(issue => {
          errors.push({
            path: issue.path.join('.'),
            message: issue.message,
            severity: 'error',
            code: 'VALIDATION_ERROR',
            details: issue
          });
        });
      }

      // Verificar compatibilidade se habilitado
      if (mergedOptions.checkCompatibility) {
        const compatibility = this.checkCompatibility(contractName, data);
        if (!compatibility.isCompatible) {
          compatibility.breakingChanges.forEach(change => {
            errors.push({
              path: change.field,
              message: `Breaking change detected: ${change.oldType} -> ${change.newType}`,
              severity: 'error',
              code: 'BREAKING_CHANGE',
              details: change
            });
          });
        }
      }

      // Verificar tipos se habilitado
      if (mergedOptions.validateTypes) {
        const typeWarnings = this.validateTypes(contractName, data);
        warnings.push(...typeWarnings);
      }

      // Gerar sugestões
      suggestions.push(...this.generateSuggestions(errors, warnings, contract));

      const result: ContractValidationResult = {
        isValid: errors.length === 0,
        errors,
        warnings,
        compatibility: this.checkCompatibility(contractName, data),
        suggestions,
        timestamp: new Date().toISOString()
      };

      // Armazenar no cache
      this.validationCache.set(cacheKey, result);

      return result;

    } catch (error) {
      const errorResult: ContractValidationResult = {
        isValid: false,
        errors: [{
          path: '',
          message: error instanceof Error ? error.message : 'Unknown error',
          severity: 'error',
          code: 'VALIDATION_EXCEPTION'
        }],
        warnings: [],
        compatibility: { isCompatible: false, breakingChanges: [], versionMismatches: [], schemaDrift: [] },
        suggestions: ['Check contract registration and schema definition'],
        timestamp: new Date().toISOString()
      };

      this.validationCache.set(cacheKey, errorResult);
      return errorResult;
    }
  }

  /**
   * Valida múltiplos contratos simultaneamente
   */
  validateMultipleContracts(
    validations: Array<{ contractName: string; data: any }>,
    options?: Partial<ContractValidationOptions>
  ): Map<string, ContractValidationResult> {
    const results = new Map<string, ContractValidationResult>();
    
    validations.forEach(({ contractName, data }) => {
      const result = this.validateData(contractName, data, options);
      results.set(contractName, result);
    });

    return results;
  }

  /**
   * Verifica compatibilidade entre versões
   */
  checkCompatibility(contractName: string, data: any): CompatibilityStatus {
    const contract = this.contracts.get(contractName);
    if (!contract) {
      return {
        isCompatible: false,
        breakingChanges: [],
        versionMismatches: [],
        schemaDrift: []
      };
    }

    const breakingChanges: BreakingChange[] = [];
    const versionMismatches: VersionMismatch[] = [];
    const schemaDrift: SchemaDrift[] = [];

    // Verificar dependências
    if (contract.dependencies) {
      contract.dependencies.forEach(dep => {
        const depContract = this.contracts.get(dep);
        if (depContract && depContract.version !== contract.version) {
          versionMismatches.push({
            expectedVersion: contract.version,
            actualVersion: depContract.version,
            component: dep,
            severity: 'warning'
          });
        }
      });
    }

    // Verificar breaking changes conhecidos
    if (contract.breakingChanges) {
      contract.breakingChanges.forEach(change => {
        breakingChanges.push({
          field: change,
          oldType: 'unknown',
          newType: 'unknown',
          impact: 'medium',
          migrationGuide: `Check breaking changes documentation for ${change}`
        });
      });
    }

    return {
      isCompatible: breakingChanges.length === 0 && versionMismatches.length === 0,
      breakingChanges,
      versionMismatches,
      schemaDrift
    };
  }

  /**
   * Valida tipos de dados
   */
  validateTypes(contractName: string, data: any): ValidationWarning[] {
    const warnings: ValidationWarning[] = [];
    const contract = this.contracts.get(contractName);

    if (!contract) return warnings;

    // Verificar tipos específicos
    this.traverseObject(data, (value, path) => {
      if (typeof value === 'string' && value.length > 1000) {
        warnings.push({
          path: path.join('.'),
          message: 'Large string detected - consider using text type',
          type: 'performance',
          recommendation: 'Use appropriate data types for large content'
        });
      }

      if (typeof value === 'number' && (value > Number.MAX_SAFE_INTEGER || value < Number.MIN_SAFE_INTEGER)) {
        warnings.push({
          path: path.join('.'),
          message: 'Number outside safe integer range',
          type: 'compatibility',
          recommendation: 'Use BigInt or string for large numbers'
        });
      }

      if (Array.isArray(value) && value.length > 1000) {
        warnings.push({
          path: path.join('.'),
          message: 'Large array detected - consider pagination',
          type: 'performance',
          recommendation: 'Implement pagination for large datasets'
        });
      }
    });

    return warnings;
  }

  /**
   * Gera sugestões baseadas em erros e warnings
   */
  generateSuggestions(
    errors: ValidationError[], 
    warnings: ValidationWarning[], 
    contract: ContractDefinition
  ): string[] {
    const suggestions: string[] = [];

    // Sugestões baseadas em erros
    const errorTypes = new Set(errors.map(e => e.code));
    
    if (errorTypes.has('VALIDATION_ERROR')) {
      suggestions.push('Review data structure against contract schema');
    }
    
    if (errorTypes.has('BREAKING_CHANGE')) {
      suggestions.push('Update client code to handle breaking changes');
      suggestions.push('Consider implementing backward compatibility layer');
    }

    // Sugestões baseadas em warnings
    const warningTypes = new Set(warnings.map(w => w.type));
    
    if (warningTypes.has('performance')) {
      suggestions.push('Optimize data structures for better performance');
    }
    
    if (warningTypes.has('security')) {
      suggestions.push('Review security implications of data changes');
    }

    // Sugestões gerais
    if (errors.length > 0) {
      suggestions.push('Run contract validation in development environment');
    }

    if (warnings.length > 0) {
      suggestions.push('Monitor performance and security metrics');
    }

    return suggestions;
  }

  /**
   * Gera schema Zod a partir de schema JSON
   */
  private generateZodSchema(schema: any): z.ZodSchema {
    if (typeof schema === 'object' && schema !== null) {
      if (schema.type === 'string') {
        let zodSchema = z.string();
        
        if (schema.minLength !== undefined) {
          zodSchema = zodSchema.min(schema.minLength);
        }
        if (schema.maxLength !== undefined) {
          zodSchema = zodSchema.max(schema.maxLength);
        }
        if (schema.pattern) {
          zodSchema = zodSchema.regex(new RegExp(schema.pattern));
        }
        if (schema.enum) {
          zodSchema = z.enum(schema.enum as [string, ...string[]]);
        }
        
        return schema.required !== false ? zodSchema : zodSchema.optional();
      }
      
      if (schema.type === 'number' || schema.type === 'integer') {
        let zodSchema = z.number();
        
        if (schema.minimum !== undefined) {
          zodSchema = zodSchema.min(schema.minimum);
        }
        if (schema.maximum !== undefined) {
          zodSchema = zodSchema.max(schema.maximum);
        }
        
        return schema.required !== false ? zodSchema : zodSchema.optional();
      }
      
      if (schema.type === 'boolean') {
        const zodSchema = z.boolean();
        return schema.required !== false ? zodSchema : zodSchema.optional();
      }
      
      if (schema.type === 'array') {
        const itemsSchema = this.generateZodSchema(schema.items);
        let zodSchema = z.array(itemsSchema);
        
        if (schema.minItems !== undefined) {
          zodSchema = zodSchema.min(schema.minItems);
        }
        if (schema.maxItems !== undefined) {
          zodSchema = zodSchema.max(schema.maxItems);
        }
        
        return schema.required !== false ? zodSchema : zodSchema.optional();
      }
      
      if (schema.type === 'object' || schema.properties) {
        const properties: Record<string, z.ZodSchema> = {};
        const required = schema.required || [];
        
        if (schema.properties) {
          Object.entries(schema.properties).forEach(([key, propSchema]) => {
            const isRequired = required.includes(key);
            const zodPropSchema = this.generateZodSchema(propSchema);
            properties[key] = isRequired ? zodPropSchema : zodPropSchema.optional();
          });
        }
        
        let zodSchema = z.object(properties);
        
        if (schema.additionalProperties === false) {
          zodSchema = zodSchema.strict();
        }
        
        return schema.required !== false ? zodSchema : zodSchema.optional();
      }
    }
    
    // Fallback para qualquer tipo
    return z.any();
  }

  /**
   * Percorre objeto recursivamente
   */
  private traverseObject(obj: any, callback: (value: any, path: string[]) => void, path: string[] = []): void {
    if (obj === null || obj === undefined) {
      return;
    }

    callback(obj, path);

    if (typeof obj === 'object' && !Array.isArray(obj)) {
      Object.entries(obj).forEach(([key, value]) => {
        this.traverseObject(value, callback, [...path, key]);
      });
    } else if (Array.isArray(obj)) {
      obj.forEach((value, index) => {
        this.traverseObject(value, callback, [...path, index.toString()]);
      });
    }
  }

  /**
   * Limpa cache de validação
   */
  clearCache(): void {
    this.validationCache.clear();
    console.info('[CONTRACT_VALIDATOR] Cache limpo');
  }

  /**
   * Obtém estatísticas de validação
   */
  getValidationStats(): {
    totalContracts: number;
    totalValidations: number;
    cacheHits: number;
    cacheSize: number;
  } {
    return {
      totalContracts: this.contracts.size,
      totalValidations: this.validationCache.size,
      cacheHits: 0, // Implementar contador de hits
      cacheSize: this.validationCache.size
    };
  }

  /**
   * Exporta contratos registrados
   */
  exportContracts(): ContractDefinition[] {
    return Array.from(this.contracts.values());
  }

  /**
   * Importa contratos
   */
  importContracts(contracts: ContractDefinition[]): void {
    contracts.forEach(contract => {
      this.registerContract(contract);
    });
  }
}

// Hook React para validação de contratos
export function useContractValidator(options?: ContractValidationOptions) {
  const [validator] = React.useState(() => new ContractValidator(options));
  const [validationResults, setValidationResults] = React.useState<Map<string, ContractValidationResult>>(new Map());

  const validateContract = React.useCallback((
    contractName: string, 
    data: any, 
    validationOptions?: Partial<ContractValidationOptions>
  ) => {
    const result = validator.validateData(contractName, data, validationOptions);
    setValidationResults(prev => new Map(prev).set(contractName, result));
    return result;
  }, [validator]);

  const validateMultiple = React.useCallback((
    validations: Array<{ contractName: string; data: any }>,
    validationOptions?: Partial<ContractValidationOptions>
  ) => {
    const results = validator.validateMultipleContracts(validations, validationOptions);
    setValidationResults(results);
    return results;
  }, [validator]);

  const registerContract = React.useCallback((contract: ContractDefinition) => {
    validator.registerContract(contract);
  }, [validator]);

  const clearCache = React.useCallback(() => {
    validator.clearCache();
  }, [validator]);

  const getStats = React.useCallback(() => {
    return validator.getValidationStats();
  }, [validator]);

  return {
    validator,
    validationResults,
    validateContract,
    validateMultiple,
    registerContract,
    clearCache,
    getStats
  };
}

// Utilitários para integração com TypeScript
export function createContractType<T>(schema: any): z.ZodSchema<T> {
  return schema as z.ZodSchema<T>;
}

export function validateType<T>(schema: z.ZodSchema<T>, data: any): T {
  return schema.parse(data);
}

export function validateTypeSafe<T>(schema: z.ZodSchema<T>, data: any): { success: true; data: T } | { success: false; error: string } {
  try {
    const result = schema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

// Testes unitários (não executar)
export function testContractValidator() {
  /**
   * Testa criação do validador
   */
  function testValidatorCreation() {
    const validator = new ContractValidator();
    expect(validator).toBeDefined();
  }

  /**
   * Testa registro de contratos
   */
  function testContractRegistration() {
    const validator = new ContractValidator();
    
    const contract: ContractDefinition = {
      name: 'test_contract',
      version: '1.0.0',
      schema: { type: 'object', properties: { name: { type: 'string' } } },
      description: 'Test contract',
      tags: ['test'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      hash: 'abc123'
    };
    
    validator.registerContract(contract);
    expect(validator.exportContracts()).toHaveLength(1);
  }

  /**
   * Testa validação de dados
   */
  function testDataValidation() {
    const validator = new ContractValidator();
    
    const contract: ContractDefinition = {
      name: 'user_contract',
      version: '1.0.0',
      schema: { 
        type: 'object', 
        properties: { 
          name: { type: 'string', required: true },
          age: { type: 'number', minimum: 0 }
        },
        required: ['name']
      },
      description: 'User contract',
      tags: ['user'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      hash: 'def456'
    };
    
    validator.registerContract(contract);
    
    // Dados válidos
    const validData = { name: 'John', age: 30 };
    const validResult = validator.validateData('user_contract', validData);
    expect(validResult.isValid).toBe(true);
    
    // Dados inválidos
    const invalidData = { age: -5 };
    const invalidResult = validator.validateData('user_contract', invalidData);
    expect(invalidResult.isValid).toBe(false);
  }
}

// Exportações
export type {
  ContractDefinition,
  ContractValidationResult,
  ValidationError,
  ValidationWarning,
  CompatibilityStatus,
  BreakingChange,
  VersionMismatch,
  SchemaDrift,
  ContractValidationOptions
}; 