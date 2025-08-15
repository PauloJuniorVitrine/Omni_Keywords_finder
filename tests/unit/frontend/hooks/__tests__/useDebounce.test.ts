import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDebounce } from '../../../../app/hooks/useDebounce'

describe('useDebounce Hook', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500))
    
    expect(result.current).toBe('initial')
  })

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    )
    
    // Primeira mudança
    rerender({ value: 'changed1', delay: 500 })
    expect(result.current).toBe('initial')
    
    // Segunda mudança
    rerender({ value: 'changed2', delay: 500 })
    expect(result.current).toBe('initial')
    
    // Avança o tempo
    act(() => {
      vi.advanceTimersByTime(500)
    })
    
    expect(result.current).toBe('changed2')
  })

  it('should respect custom delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 1000 } }
    )
    
    rerender({ value: 'changed', delay: 1000 })
    expect(result.current).toBe('initial')
    
    // Avança menos que o delay
    act(() => {
      vi.advanceTimersByTime(500)
    })
    expect(result.current).toBe('initial')
    
    // Avança o tempo completo
    act(() => {
      vi.advanceTimersByTime(500)
    })
    expect(result.current).toBe('changed')
  })

  it('should handle multiple rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 300 } }
    )
    
    // Múltiplas mudanças rápidas
    rerender({ value: 'change1', delay: 300 })
    rerender({ value: 'change2', delay: 300 })
    rerender({ value: 'change3', delay: 300 })
    rerender({ value: 'final', delay: 300 })
    
    expect(result.current).toBe('initial')
    
    // Avança o tempo
    act(() => {
      vi.advanceTimersByTime(300)
    })
    
    expect(result.current).toBe('final')
  })

  it('should handle zero delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 0 } }
    )
    
    rerender({ value: 'changed', delay: 0 })
    expect(result.current).toBe('changed')
  })

  it('should handle negative delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: -100 } }
    )
    
    rerender({ value: 'changed', delay: -100 })
    expect(result.current).toBe('changed')
  })
})
