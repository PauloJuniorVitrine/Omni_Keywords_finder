/**
 * Sistema de Type Guards
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 8.4
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface User {
  id: string;
  name: string;
  email: string;
  cpf?: string;
  createdAt: string;
  isActive: boolean;
  profile?: UserProfile;
}

export interface UserProfile {
  avatar?: string;
  bio?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  notifications: boolean;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  tags: string[];
  inStock: boolean;
  metadata?: ProductMetadata;
}

export interface ProductMetadata {
  weight?: number;
  dimensions?: {
    width: number;
    height: number;
    depth: number;
  };
  manufacturer?: string;
}

export interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  total: number;
  status: OrderStatus;
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export class TypeGuards {
  /**
   * Type guard para verificar se é string
   */
  static isString(value: any): value is string {
    return typeof value === 'string';
  }

  /**
   * Type guard para verificar se é number
   */
  static isNumber(value: any): value is number {
    return typeof value === 'number' && !isNaN(value);
  }

  /**
   * Type guard para verificar se é boolean
   */
  static isBoolean(value: any): value is boolean {
    return typeof value === 'boolean';
  }

  /**
   * Type guard para verificar se é array
   */
  static isArray(value: any): value is any[] {
    return Array.isArray(value);
  }

  /**
   * Type guard para verificar se é objeto
   */
  static isObject(value: any): value is object {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
  }

  /**
   * Type guard para verificar se é null
   */
  static isNull(value: any): value is null {
    return value === null;
  }

  /**
   * Type guard para verificar se é undefined
   */
  static isUndefined(value: any): value is undefined {
    return value === undefined;
  }

  /**
   * Type guard para verificar se é null ou undefined
   */
  static isNullOrUndefined(value: any): value is null | undefined {
    return value === null || value === undefined;
  }

  /**
   * Type guard para verificar se é função
   */
  static isFunction(value: any): value is Function {
    return typeof value === 'function';
  }

  /**
   * Type guard para verificar se é Date
   */
  static isDate(value: any): value is Date {
    return value instanceof Date;
  }

  /**
   * Type guard para verificar se é RegExp
   */
  static isRegExp(value: any): value is RegExp {
    return value instanceof RegExp;
  }

  /**
   * Type guard para verificar se é Promise
   */
  static isPromise(value: any): value is Promise<any> {
    return value instanceof Promise;
  }

  /**
   * Type guard para verificar se é Error
   */
  static isError(value: any): value is Error {
    return value instanceof Error;
  }

  /**
   * Type guard para verificar se é Map
   */
  static isMap(value: any): value is Map<any, any> {
    return value instanceof Map;
  }

  /**
   * Type guard para verificar se é Set
   */
  static isSet(value: any): value is Set<any> {
    return value instanceof Set;
  }

  /**
   * Type guard para verificar se é WeakMap
   */
  static isWeakMap(value: any): value is WeakMap<any, any> {
    return value instanceof WeakMap;
  }

  /**
   * Type guard para verificar se é WeakSet
   */
  static isWeakSet(value: any): value is WeakSet<any> {
    return value instanceof WeakSet;
  }

  /**
   * Type guard para verificar se é ArrayBuffer
   */
  static isArrayBuffer(value: any): value is ArrayBuffer {
    return value instanceof ArrayBuffer;
  }

  /**
   * Type guard para verificar se é TypedArray
   */
  static isTypedArray(value: any): value is TypedArray {
    return ArrayBuffer.isView(value) && !(value instanceof DataView);
  }

  /**
   * Type guard para verificar se é DataView
   */
  static isDataView(value: any): value is DataView {
    return value instanceof DataView;
  }

  /**
   * Type guard para verificar se é URL
   */
  static isURL(value: any): value is URL {
    return value instanceof URL;
  }

  /**
   * Type guard para verificar se é FormData
   */
  static isFormData(value: any): value is FormData {
    return value instanceof FormData;
  }

  /**
   * Type guard para verificar se é File
   */
  static isFile(value: any): value is File {
    return value instanceof File;
  }

  /**
   * Type guard para verificar se é Blob
   */
  static isBlob(value: any): value is Blob {
    return value instanceof Blob;
  }

  /**
   * Type guard para verificar se é Event
   */
  static isEvent(value: any): value is Event {
    return value instanceof Event;
  }

  /**
   * Type guard para verificar se é Element
   */
  static isElement(value: any): value is Element {
    return value instanceof Element;
  }

  /**
   * Type guard para verificar se é HTMLElement
   */
  static isHTMLElement(value: any): value is HTMLElement {
    return value instanceof HTMLElement;
  }

  /**
   * Type guard para verificar se é Node
   */
  static isNode(value: any): value is Node {
    return value instanceof Node;
  }

  /**
   * Type guard para verificar se é NodeList
   */
  static isNodeList(value: any): value is NodeList {
    return value instanceof NodeList;
  }

  /**
   * Type guard para verificar se é HTMLCollection
   */
  static isHTMLCollection(value: any): value is HTMLCollection {
    return value instanceof HTMLCollection;
  }

  /**
   * Type guard para verificar se é Window
   */
  static isWindow(value: any): value is Window {
    return value === window;
  }

  /**
   * Type guard para verificar se é Document
   */
  static isDocument(value: any): value is Document {
    return value === document;
  }

  /**
   * Type guard para verificar se é User
   */
  static isUser(value: any): value is User {
    return (
      this.isObject(value) &&
      this.isString(value.id) &&
      this.isString(value.name) &&
      this.isString(value.email) &&
      this.isString(value.createdAt) &&
      this.isBoolean(value.isActive) &&
      (this.isNullOrUndefined(value.cpf) || this.isString(value.cpf)) &&
      (this.isNullOrUndefined(value.profile) || this.isUserProfile(value.profile))
    );
  }

  /**
   * Type guard para verificar se é UserProfile
   */
  static isUserProfile(value: any): value is UserProfile {
    return (
      this.isObject(value) &&
      this.isObject(value.preferences) &&
      this.isUserPreferences(value.preferences) &&
      (this.isNullOrUndefined(value.avatar) || this.isString(value.avatar)) &&
      (this.isNullOrUndefined(value.bio) || this.isString(value.bio))
    );
  }

  /**
   * Type guard para verificar se é UserPreferences
   */
  static isUserPreferences(value: any): value is UserPreferences {
    return (
      this.isObject(value) &&
      (value.theme === 'light' || value.theme === 'dark') &&
      this.isString(value.language) &&
      this.isBoolean(value.notifications)
    );
  }

  /**
   * Type guard para verificar se é Product
   */
  static isProduct(value: any): value is Product {
    return (
      this.isObject(value) &&
      this.isString(value.id) &&
      this.isString(value.name) &&
      this.isString(value.description) &&
      this.isNumber(value.price) &&
      this.isString(value.category) &&
      this.isArray(value.tags) &&
      value.tags.every((tag: any) => this.isString(tag)) &&
      this.isBoolean(value.inStock) &&
      (this.isNullOrUndefined(value.metadata) || this.isProductMetadata(value.metadata))
    );
  }

  /**
   * Type guard para verificar se é ProductMetadata
   */
  static isProductMetadata(value: any): value is ProductMetadata {
    return (
      this.isObject(value) &&
      (this.isNullOrUndefined(value.weight) || this.isNumber(value.weight)) &&
      (this.isNullOrUndefined(value.dimensions) || this.isProductDimensions(value.dimensions)) &&
      (this.isNullOrUndefined(value.manufacturer) || this.isString(value.manufacturer))
    );
  }

  /**
   * Type guard para verificar se é ProductDimensions
   */
  static isProductDimensions(value: any): value is { width: number; height: number; depth: number } {
    return (
      this.isObject(value) &&
      this.isNumber(value.width) &&
      this.isNumber(value.height) &&
      this.isNumber(value.depth)
    );
  }

  /**
   * Type guard para verificar se é Order
   */
  static isOrder(value: any): value is Order {
    return (
      this.isObject(value) &&
      this.isString(value.id) &&
      this.isString(value.userId) &&
      this.isArray(value.items) &&
      value.items.every((item: any) => this.isOrderItem(item)) &&
      this.isNumber(value.total) &&
      this.isOrderStatus(value.status) &&
      this.isString(value.createdAt) &&
      this.isString(value.updatedAt)
    );
  }

  /**
   * Type guard para verificar se é OrderItem
   */
  static isOrderItem(value: any): value is OrderItem {
    return (
      this.isObject(value) &&
      this.isString(value.productId) &&
      this.isNumber(value.quantity) &&
      this.isNumber(value.price)
    );
  }

  /**
   * Type guard para verificar se é OrderStatus
   */
  static isOrderStatus(value: any): value is OrderStatus {
    return (
      this.isString(value) &&
      ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'].includes(value)
    );
  }

  /**
   * Type guard para verificar se é ApiResponse
   */
  static isApiResponse<T = any>(value: any): value is ApiResponse<T> {
    return (
      this.isObject(value) &&
      this.isBoolean(value.success) &&
      this.isString(value.timestamp) &&
      (this.isNullOrUndefined(value.data) || true) && // T seria validado separadamente
      (this.isNullOrUndefined(value.error) || this.isString(value.error)) &&
      (this.isNullOrUndefined(value.message) || this.isString(value.message))
    );
  }

  /**
   * Type guard para verificar se é PaginatedResponse
   */
  static isPaginatedResponse<T = any>(value: any): value is PaginatedResponse<T> {
    return (
      this.isObject(value) &&
      this.isArray(value.data) &&
      this.isObject(value.pagination) &&
      this.isNumber(value.pagination.page) &&
      this.isNumber(value.pagination.limit) &&
      this.isNumber(value.pagination.total) &&
      this.isNumber(value.pagination.totalPages)
    );
  }

  /**
   * Type guard para verificar se é email válido
   */
  static isEmail(value: any): value is string {
    if (!this.isString(value)) return false;
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(value);
  }

  /**
   * Type guard para verificar se é URL válida
   */
  static isURL(value: any): value is string {
    if (!this.isString(value)) return false;
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Type guard para verificar se é UUID válido
   */
  static isUUID(value: any): value is string {
    if (!this.isString(value)) return false;
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidPattern.test(value);
  }

  /**
   * Type guard para verificar se é CPF válido
   */
  static isCPF(value: any): value is string {
    if (!this.isString(value)) return false;
    
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
  }

  /**
   * Type guard para verificar se é CNPJ válido
   */
  static isCNPJ(value: any): value is string {
    if (!this.isString(value)) return false;
    
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
  }

  /**
   * Type guard para verificar se é data válida
   */
  static isDate(value: any): value is string {
    if (!this.isString(value)) return false;
    return !isNaN(Date.parse(value));
  }

  /**
   * Type guard para verificar se é número de telefone válido
   */
  static isPhone(value: any): value is string {
    if (!this.isString(value)) return false;
    const phonePattern = /^[\+]?[1-9][\d]{0,15}$/;
    return phonePattern.test(value.replace(/\D/g, ''));
  }

  /**
   * Type guard para verificar se é CEP válido
   */
  static isCEP(value: any): value is string {
    if (!this.isString(value)) return false;
    const cepPattern = /^\d{5}-?\d{3}$/;
    return cepPattern.test(value);
  }

  /**
   * Type guard para verificar se é array de strings
   */
  static isStringArray(value: any): value is string[] {
    return this.isArray(value) && value.every(item => this.isString(item));
  }

  /**
   * Type guard para verificar se é array de números
   */
  static isNumberArray(value: any): value is number[] {
    return this.isArray(value) && value.every(item => this.isNumber(item));
  }

  /**
   * Type guard para verificar se é array de booleanos
   */
  static isBooleanArray(value: any): value is boolean[] {
    return this.isArray(value) && value.every(item => this.isBoolean(item));
  }

  /**
   * Type guard para verificar se é array de objetos
   */
  static isObjectArray(value: any): value is object[] {
    return this.isArray(value) && value.every(item => this.isObject(item));
  }

  /**
   * Type guard para verificar se é array de Users
   */
  static isUserArray(value: any): value is User[] {
    return this.isArray(value) && value.every(item => this.isUser(item));
  }

  /**
   * Type guard para verificar se é array de Products
   */
  static isProductArray(value: any): value is Product[] {
    return this.isArray(value) && value.every(item => this.isProduct(item));
  }

  /**
   * Type guard para verificar se é array de Orders
   */
  static isOrderArray(value: any): value is Order[] {
    return this.isArray(value) && value.every(item => this.isOrder(item));
  }

  /**
   * Type guard para verificar se é objeto vazio
   */
  static isEmptyObject(value: any): value is {} {
    return this.isObject(value) && Object.keys(value).length === 0;
  }

  /**
   * Type guard para verificar se é array vazio
   */
  static isEmptyArray(value: any): value is [] {
    return this.isArray(value) && value.length === 0;
  }

  /**
   * Type guard para verificar se é string vazia
   */
  static isEmptyString(value: any): value is '' {
    return this.isString(value) && value.length === 0;
  }

  /**
   * Type guard para verificar se é string não vazia
   */
  static isNonEmptyString(value: any): value is string {
    return this.isString(value) && value.length > 0;
  }

  /**
   * Type guard para verificar se é número positivo
   */
  static isPositiveNumber(value: any): value is number {
    return this.isNumber(value) && value > 0;
  }

  /**
   * Type guard para verificar se é número negativo
   */
  static isNegativeNumber(value: any): value is number {
    return this.isNumber(value) && value < 0;
  }

  /**
   * Type guard para verificar se é número inteiro
   */
  static isInteger(value: any): value is number {
    return this.isNumber(value) && Number.isInteger(value);
  }

  /**
   * Type guard para verificar se é número decimal
   */
  static isDecimal(value: any): value is number {
    return this.isNumber(value) && !Number.isInteger(value);
  }

  /**
   * Type guard para verificar se é número finito
   */
  static isFiniteNumber(value: any): value is number {
    return this.isNumber(value) && Number.isFinite(value);
  }

  /**
   * Type guard para verificar se é número infinito
   */
  static isInfiniteNumber(value: any): value is number {
    return this.isNumber(value) && !Number.isFinite(value);
  }
}

// Tipo auxiliar para TypedArray
type TypedArray = Int8Array | Uint8Array | Uint8ClampedArray | Int16Array | Uint16Array | Int32Array | Uint32Array | Float32Array | Float64Array; 