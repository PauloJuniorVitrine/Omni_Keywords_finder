import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utilitário para combinar classes CSS de forma inteligente
 * Combina clsx para lógica condicional e tailwind-merge para resolver conflitos
 * 
 * @param inputs - Classes CSS para combinar
 * @returns String com classes CSS combinadas e otimizadas
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Utilitário para criar variantes de componentes
 * 
 * @param base - Classes base do componente
 * @param variants - Objeto com variantes do componente
 * @param defaultVariants - Variantes padrão
 * @returns Função para gerar classes baseadas nas variantes
 */
export function cva<T extends Record<string, Record<string, string>>>(
  base: string,
  variants: T,
  defaultVariants?: Partial<Record<keyof T, keyof T[keyof T]>>
) {
  return (props?: Partial<Record<keyof T, keyof T[keyof T]>> & { className?: string }) => {
    const variantClasses = Object.entries(variants).map(([key, variant]) => {
      const value = props?.[key] ?? defaultVariants?.[key];
      return value ? variant[value] : '';
    });

    return cn(base, ...variantClasses, props?.className);
  };
} 