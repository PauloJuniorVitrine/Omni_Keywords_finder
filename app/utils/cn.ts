/**
 * cn.ts
 * 
 * Utilitário para combinação de classes CSS
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Data: 2025-01-27
 */

/**
 * Combina classes CSS de forma inteligente
 * Remove duplicatas e conflitos
 */
export function cn(...inputs: (string | undefined | null | false)[]) {
  return inputs.filter(Boolean).join(' ');
}

export default cn; 