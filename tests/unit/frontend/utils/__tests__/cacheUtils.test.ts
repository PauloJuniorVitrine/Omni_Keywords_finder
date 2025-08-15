import { describe, it, expect, vi, beforeEach } from 'vitest'
import { cacheUtils } from '../../../../app/utils/cacheUtils'

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('cacheUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('should set cache item with TTL', () => {
    const key = 'test-key'
    const value = { data: 'test-data' }
    const ttl = 60000 // 1 minuto
    
    cacheUtils.set(key, value, ttl)
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      key,
      expect.stringContaining('test-data')
    )
  })

  it('should get cache item when not expired', () => {
    const key = 'test-key'
    const value = { data: 'test-data' }
    const ttl = 60000
    
    // Simula item no cache
    const cachedItem = {
      value,
      timestamp: Date.now(),
      ttl,
    }
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(cachedItem))
    
    const result = cacheUtils.get(key)
    
    expect(result).toEqual(value)
  })

  it('should return null for expired cache item', () => {
    const key = 'test-key'
    const value = { data: 'test-data' }
    const ttl = 1000 // 1 segundo
    
    // Simula item expirado
    const expiredItem = {
      value,
      timestamp: Date.now() - 2000, // 2 segundos atrás
      ttl,
    }
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredItem))
    
    const result = cacheUtils.get(key)
    
    expect(result).toBeNull()
  })

  it('should remove cache item', () => {
    const key = 'test-key'
    
    cacheUtils.remove(key)
    
    expect(localStorageMock.removeItem).toHaveBeenCalledWith(key)
  })

  it('should clear all cache', () => {
    cacheUtils.clear()
    
    expect(localStorageMock.clear).toHaveBeenCalled()
  })

  it('should check if cache item exists', () => {
    const key = 'test-key'
    
    // Simula item existente
    localStorageMock.getItem.mockReturnValue('{"value": "test", "timestamp": 123, "ttl": 60000}')
    
    const exists = cacheUtils.has(key)
    
    expect(exists).toBe(true)
  })

  it('should return false for non-existent cache item', () => {
    const key = 'non-existent-key'
    
    localStorageMock.getItem.mockReturnValue(null)
    
    const exists = cacheUtils.has(key)
    
    expect(exists).toBe(false)
  })

  it('should handle invalid cache data gracefully', () => {
    const key = 'invalid-key'
    
    // Simula dados inválidos
    localStorageMock.getItem.mockReturnValue('invalid-json')
    
    const result = cacheUtils.get(key)
    
    expect(result).toBeNull()
  })

  it('should set cache without TTL (default)', () => {
    const key = 'default-key'
    const value = 'default-value'
    
    cacheUtils.set(key, value)
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      key,
      expect.stringContaining('default-value')
    )
  })
})
