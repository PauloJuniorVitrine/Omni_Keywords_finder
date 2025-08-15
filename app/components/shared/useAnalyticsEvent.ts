import { useCallback } from 'react';

/**
 * useAnalyticsEvent - Hook para disparar eventos customizados no Plausible Analytics.
 * @param category Categoria do evento (ex: 'Feedback', 'Ajuda', 'Onboarding')
 * @returns Função para disparar evento: (action: string, props?: Record<string, any>) => void
 */
export function useAnalyticsEvent(category: string) {
  return useCallback((action: string, props?: Record<string, any>) => {
    if (typeof window !== 'undefined' && (window as any).plausible) {
      (window as any).plausible(action, { props: { category, ...props } });
    }
  }, [category]);
} 