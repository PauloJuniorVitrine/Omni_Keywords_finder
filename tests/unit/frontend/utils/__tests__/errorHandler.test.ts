import { describe, it, expect, vi, beforeEach } from 'vitest'
import { errorHandler } from '../../../../app/utils/errorHandler'

// Mock do console
const consoleSpy = {
  error: vi.spyOn(console, 'error').mockImplementation(() => {}),
  warn: vi.spyOn(console, 'warn').mockImplementation(() => {}),
  log: vi.spyOn(console, 'log').mockImplementation(() => {}),
}

// Mock do toast
vi.mock('react-hot-toast', () => ({
  toast: {
    error: vi.fn(),
    warning: vi.fn(),
    success: vi.fn(),
  },
}))

describe('errorHandler Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should handle generic errors', () => {
    const error = new Error('Generic error message')
    
    errorHandler.handle(error)
    
    expect(consoleSpy.error).toHaveBeenCalledWith('Error handled:', error)
  })

  it('should handle network errors', () => {
    const networkError = new Error('Network Error')
    networkError.name = 'NetworkError'
    
    errorHandler.handle(networkError)
    
    expect(consoleSpy.error).toHaveBeenCalledWith('Network error:', networkError)
  })

  it('should handle validation errors', () => {
    const validationError = new Error('Validation failed')
    validationError.name = 'ValidationError'
    
    errorHandler.handle(validationError)
    
    expect(consoleSpy.warn).toHaveBeenCalledWith('Validation error:', validationError)
  })

  it('should handle authentication errors', () => {
    const authError = new Error('Unauthorized')
    authError.name = 'AuthenticationError'
    
    errorHandler.handle(authError)
    
    expect(consoleSpy.error).toHaveBeenCalledWith('Authentication error:', authError)
  })

  it('should handle unknown error types', () => {
    const unknownError = new Error('Unknown error')
    unknownError.name = 'UnknownErrorType'
    
    errorHandler.handle(unknownError)
    
    expect(consoleSpy.error).toHaveBeenCalledWith('Unknown error type:', unknownError)
  })

  it('should format error messages correctly', () => {
    const error = new Error('Test error')
    
    const formattedMessage = errorHandler.formatMessage(error)
    
    expect(formattedMessage).toContain('Test error')
  })

  it('should log error with context', () => {
    const error = new Error('Context error')
    const context = 'UserComponent'
    
    errorHandler.handleWithContext(error, context)
    
    expect(consoleSpy.error).toHaveBeenCalledWith(`Error in ${context}:`, error)
  })

  it('should handle async errors', async () => {
    const asyncError = new Error('Async error')
    
    await errorHandler.handleAsync(asyncError)
    
    expect(consoleSpy.error).toHaveBeenCalledWith('Async error handled:', asyncError)
  })
})
