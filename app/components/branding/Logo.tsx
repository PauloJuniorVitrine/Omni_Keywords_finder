/**
 * Logo.tsx
 * 
 * Componente de logo responsivo com suporte a temas e animações
 * 
 * Tracing ID: UI_BRANDING_LOGO_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 14.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect } from 'react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/utils/cn';

interface LogoProps {
  variant?: 'default' | 'compact' | 'icon' | 'text';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  animated?: boolean;
  className?: string;
  onClick?: () => void;
  href?: string;
}

export const Logo: React.FC<LogoProps> = ({
  variant = 'default',
  size = 'md',
  animated = true,
  className = '',
  onClick,
  href
}) => {
  const { theme } = useTheme();
  const [isHovered, setIsHovered] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // Configurações de tamanho
  const sizeConfig = {
    sm: {
      icon: 'w-6 h-6',
      text: 'text-sm',
      container: 'h-8'
    },
    md: {
      icon: 'w-8 h-8',
      text: 'text-lg',
      container: 'h-10'
    },
    lg: {
      icon: 'w-10 h-10',
      text: 'text-xl',
      container: 'h-12'
    },
    xl: {
      icon: 'w-12 h-12',
      text: 'text-2xl',
      container: 'h-16'
    }
  };

  // Cores baseadas no tema
  const colors = {
    light: {
      primary: '#3B82F6',
      secondary: '#1E40AF',
      text: '#1F2937',
      accent: '#60A5FA'
    },
    dark: {
      primary: '#60A5FA',
      secondary: '#93C5FD',
      text: '#F9FAFB',
      accent: '#3B82F6'
    }
  };

  const currentColors = colors[theme as keyof typeof colors] || colors.light;

  // Componente do ícone
  const LogoIcon = () => (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(
        sizeConfig[size].icon,
        'transition-all duration-300 ease-in-out',
        animated && 'hover:scale-110',
        isHovered && animated && 'animate-pulse',
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Círculo de fundo */}
      <circle
        cx="12"
        cy="12"
        r="10"
        fill={currentColors.primary}
        className={cn(
          'transition-all duration-300',
          animated && isHovered && 'animate-ping'
        )}
        opacity="0.2"
      />
      
      {/* Círculo principal */}
      <circle
        cx="12"
        cy="12"
        r="8"
        fill={currentColors.primary}
        className="transition-all duration-300"
      />
      
      {/* Símbolo central - Omni */}
      <g fill={currentColors.text}>
        {/* O */}
        <path
          d="M12 6C9.79 6 8 7.79 8 10s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 6c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"
          className={cn(
            'transition-all duration-300',
            animated && isHovered && 'animate-bounce'
          )}
        />
        
        {/* M */}
        <path
          d="M6 16h2v-6h2v6h2v-6h2v6h2v-8h-2v2h-2v-2h-2v2h-2v-2H8v2H6v-2H4v8h2z"
          className={cn(
            'transition-all duration-300',
            animated && isHovered && 'animate-pulse'
          )}
        />
        
        {/* N */}
        <path
          d="M16 16h2v-8h-2v6h-2v-6h-2v8h2v-6h2v6z"
          className={cn(
            'transition-all duration-300',
            animated && isHovered && 'animate-pulse'
          )}
        />
        
        {/* I */}
        <path
          d="M20 8h-2v8h2V8z"
          className={cn(
            'transition-all duration-300',
            animated && isHovered && 'animate-bounce'
          )}
        />
      </g>
      
      {/* Efeito de brilho */}
      {animated && (
        <defs>
          <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={currentColors.accent} stopOpacity="0" />
            <stop offset="50%" stopColor={currentColors.accent} stopOpacity="0.5" />
            <stop offset="100%" stopColor={currentColors.accent} stopOpacity="0" />
          </linearGradient>
        </defs>
      )}
      
      {animated && isHovered && (
        <rect
          x="0"
          y="0"
          width="24"
          height="24"
          fill="url(#shine)"
          className="animate-pulse"
        />
      )}
    </svg>
  );

  // Componente do texto
  const LogoText = () => (
    <span
      className={cn(
        'font-bold tracking-tight transition-all duration-300',
        sizeConfig[size].text,
        animated && 'hover:scale-105',
        className
      )}
      style={{ color: currentColors.text }}
    >
      Omni
      <span
        className="font-light"
        style={{ color: currentColors.primary }}
      >
        Keywords
      </span>
    </span>
  );

  // Componente do slogan
  const LogoSlogan = () => (
    <div className="flex flex-col">
      <LogoText />
      <span
        className={cn(
          'text-xs font-light tracking-wider transition-all duration-300',
          size === 'sm' ? 'text-xs' : 'text-sm',
          className
        )}
        style={{ color: currentColors.secondary }}
      >
        FINDER
      </span>
    </div>
  );

  // Renderizar baseado na variante
  const renderLogo = () => {
    switch (variant) {
      case 'icon':
        return <LogoIcon />;
      case 'text':
        return <LogoText />;
      case 'compact':
        return (
          <div className="flex items-center gap-2">
            <LogoIcon />
            <span
              className={cn(
                'font-bold tracking-tight transition-all duration-300',
                sizeConfig[size].text,
                animated && 'hover:scale-105',
                className
              )}
              style={{ color: currentColors.text }}
            >
              Omni
            </span>
          </div>
        );
      case 'default':
      default:
        return (
          <div className="flex items-center gap-3">
            <LogoIcon />
            <LogoSlogan />
          </div>
        );
    }
  };

  // Container com animação de entrada
  const Container = href ? 'a' : 'div';
  const containerProps = href ? { href } : {};

  return (
    <Container
      {...containerProps}
      className={cn(
        'flex items-center transition-all duration-300 ease-in-out cursor-pointer',
        sizeConfig[size].container,
        animated && 'hover:scale-105',
        isLoaded && 'animate-fade-in',
        className
      )}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {renderLogo()}
    </Container>
  );
};

// Componente de logo animado para loading
export const AnimatedLogo: React.FC<LogoProps> = (props) => {
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsAnimating(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative">
      <Logo {...props} animated={isAnimating} />
      {isAnimating && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
      )}
    </div>
  );
};

// Componente de logo com fallback
export const LogoWithFallback: React.FC<LogoProps & { fallback?: React.ReactNode }> = ({
  fallback,
  ...props
}) => {
  const [hasError, setHasError] = useState(false);

  if (hasError && fallback) {
    return <>{fallback}</>;
  }

  return (
    <div onError={() => setHasError(true)}>
      <Logo {...props} />
    </div>
  );
};

// Componente de logo responsivo
export const ResponsiveLogo: React.FC<LogoProps> = (props) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <Logo
      {...props}
      variant={isMobile ? 'compact' : props.variant}
      size={isMobile ? 'sm' : props.size}
    />
  );
};

export default Logo; 