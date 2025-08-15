import React, { forwardRef } from 'react';
import { cn } from '../../../utils/cn';

// Tipos específicos para o sistema Omni Keywords Finder
export interface TextProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'p' | 'span' | 'div' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'label' | 'strong' | 'em' | 'small';
  variant?: 'body' | 'heading' | 'caption' | 'overline' | 'button' | 'code';
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | '6xl';
  weight?: 'light' | 'normal' | 'medium' | 'semibold' | 'bold' | 'extrabold' | 'black';
  color?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'muted';
  align?: 'left' | 'center' | 'right' | 'justify';
  truncate?: boolean;
  noWrap?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
  uppercase?: boolean;
  lowercase?: boolean;
  capitalize?: boolean;
}

export const Text = forwardRef<HTMLElement, TextProps>(
  (
    {
      className,
      as: Component = 'p',
      variant = 'body',
      size = 'base',
      weight = 'normal',
      color = 'default',
      align,
      truncate = false,
      noWrap = false,
      italic = false,
      underline = false,
      strikethrough = false,
      uppercase = false,
      lowercase = false,
      capitalize = false,
      children,
      ...props
    },
    ref
  ) => {
    // Design tokens específicos do Omni Keywords Finder
    const textVariants = {
      body: 'text-gray-900',
      heading: 'text-gray-900 font-semibold',
      caption: 'text-gray-600 text-sm',
      overline: 'text-gray-500 text-xs uppercase tracking-wide',
      button: 'text-gray-700 font-medium',
      code: 'font-mono bg-gray-100 px-1 py-0.5 rounded text-sm'
    };

    const textSizes = {
      xs: 'text-xs',
      sm: 'text-sm',
      base: 'text-base',
      lg: 'text-lg',
      xl: 'text-xl',
      '2xl': 'text-2xl',
      '3xl': 'text-3xl',
      '4xl': 'text-4xl',
      '5xl': 'text-5xl',
      '6xl': 'text-6xl'
    };

    const textWeights = {
      light: 'font-light',
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
      extrabold: 'font-extrabold',
      black: 'font-black'
    };

    const textColors = {
      default: 'text-gray-900',
      primary: 'text-blue-600',
      secondary: 'text-gray-600',
      success: 'text-green-600',
      warning: 'text-yellow-600',
      danger: 'text-red-600',
      info: 'text-blue-500',
      muted: 'text-gray-500'
    };

    const textAligns = {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
      justify: 'text-justify'
    };

    const textTransforms = {
      uppercase: 'uppercase',
      lowercase: 'lowercase',
      capitalize: 'capitalize'
    };

    const textDecorations = {
      italic: 'italic',
      underline: 'underline',
      strikethrough: 'line-through'
    };

    return (
      <Component
        ref={ref}
        className={cn(
          // Variante base
          textVariants[variant],
          
          // Tamanho
          textSizes[size],
          
          // Peso
          textWeights[weight],
          
          // Cor
          textColors[color],
          
          // Alinhamento
          align && textAligns[align],
          
          // Transformações
          uppercase && textTransforms.uppercase,
          lowercase && textTransforms.lowercase,
          capitalize && textTransforms.capitalize,
          
          // Decorações
          italic && textDecorations.italic,
          underline && textDecorations.underline,
          strikethrough && textDecorations.strikethrough,
          
          // Utilitários
          truncate && 'truncate',
          noWrap && 'whitespace-nowrap',
          
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

Text.displayName = 'Text';

// Componentes especializados para facilitar o uso
export const Heading = forwardRef<HTMLHeadingElement, Omit<TextProps, 'as' | 'variant'> & { level?: 1 | 2 | 3 | 4 | 5 | 6 }>(
  ({ level = 1, ...props }, ref) => {
    const headingMap = {
      1: 'h1',
      2: 'h2',
      3: 'h3',
      4: 'h4',
      5: 'h5',
      6: 'h6'
    } as const;

    return (
      <Text
        ref={ref}
        as={headingMap[level]}
        variant="heading"
        size={level === 1 ? '4xl' : level === 2 ? '3xl' : level === 3 ? '2xl' : level === 4 ? 'xl' : level === 5 ? 'lg' : 'base'}
        weight="semibold"
        {...props}
      />
    );
  }
);

Heading.displayName = 'Heading';

export const Body = forwardRef<HTMLParagraphElement, Omit<TextProps, 'as' | 'variant'>>(
  (props, ref) => (
    <Text ref={ref} as="p" variant="body" {...props} />
  )
);

Body.displayName = 'Body';

export const Caption = forwardRef<HTMLParagraphElement, Omit<TextProps, 'as' | 'variant'>>(
  (props, ref) => (
    <Text ref={ref} as="p" variant="caption" {...props} />
  )
);

Caption.displayName = 'Caption';

export const Code = forwardRef<HTMLElement, Omit<TextProps, 'as' | 'variant'>>(
  (props, ref) => (
    <Text ref={ref} as="code" variant="code" {...props} />
  )
);

Code.displayName = 'Code'; 