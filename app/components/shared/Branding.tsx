/**
 * Branding.tsx
 * 
 * Componente de identidade visual para o Omni Keywords Finder
 * Logo, nome da aplicação e elementos de marca
 * 
 * Tracing ID: UI-007
 * Data/Hora: 2024-12-20 08:30:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect } from 'react';
import { colors } from '../../ui/theme/colors';
import { typography } from '../../ui/theme/typography';

// Tipos para o componente
interface BrandingProps {
  /** Tamanho do componente */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Variante do componente */
  variant?: 'default' | 'compact' | 'full' | 'icon-only';
  /** Modo de tema */
  theme?: 'light' | 'dark' | 'auto';
  /** Mostrar tagline */
  showTagline?: boolean;
  /** Texto da tagline customizada */
  customTagline?: string;
  /** Link para navegação */
  href?: string;
  /** Função de clique customizada */
  onClick?: () => void;
  /** Classes CSS adicionais */
  className?: string;
  /** Estilo inline customizado */
  style?: React.CSSProperties;
  /** Mostrar animação de loading */
  loading?: boolean;
  /** Fallback para quando logo não carrega */
  fallbackText?: string;
}

// Configurações de branding
const brandingConfig = {
  name: 'Omni Keywords Finder',
  tagline: 'Descubra oportunidades de SEO com inteligência artificial',
  shortName: 'OKF',
  logo: {
    primary: '/assets/logo/omni-keywords-finder-logo.svg',
    fallback: '/assets/logo/omni-keywords-finder-logo.png',
    icon: '/assets/logo/omni-keywords-finder-icon.svg'
  },
  colors: {
    primary: colors.primary[600],
    secondary: colors.secondary[600],
    accent: colors.state.info[600]
  }
} as const;

// Tamanhos do componente
const sizeConfig = {
  sm: {
    logoSize: '24px',
    fontSize: typography.sizes.sm,
    spacing: '8px',
    height: '32px'
  },
  md: {
    logoSize: '32px',
    fontSize: typography.sizes.base,
    spacing: '12px',
    height: '40px'
  },
  lg: {
    logoSize: '40px',
    fontSize: typography.sizes.lg,
    spacing: '16px',
    height: '48px'
  },
  xl: {
    logoSize: '48px',
    fontSize: typography.sizes.xl,
    spacing: '20px',
    height: '56px'
  }
} as const;

// Hook para gerenciar tema
const useTheme = (theme: 'light' | 'dark' | 'auto') => {
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    if (theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      setCurrentTheme(mediaQuery.matches ? 'dark' : 'light');

      const handler = (e: MediaQueryListEvent) => {
        setCurrentTheme(e.matches ? 'dark' : 'light');
      };

      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    } else {
      setCurrentTheme(theme);
    }
  }, [theme]);

  return currentTheme;
};

// Hook para gerenciar carregamento do logo
const useLogoLoading = (logoUrl: string) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (!logoUrl) {
      setHasError(true);
      return;
    }

    const img = new Image();
    img.onload = () => setIsLoaded(true);
    img.onerror = () => setHasError(true);
    img.src = logoUrl;
  }, [logoUrl]);

  return { isLoaded, hasError };
};

// Componente de Logo
const Logo: React.FC<{
  size: string;
  theme: 'light' | 'dark';
  variant: string;
  onError: () => void;
}> = ({ size, theme, variant, onError }) => {
  const logoUrl = variant === 'icon-only' 
    ? brandingConfig.logo.icon 
    : brandingConfig.logo.primary;
  
  const { isLoaded, hasError } = useLogoLoading(logoUrl);

  if (hasError) {
    onError();
    return (
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          backgroundColor: theme === 'dark' ? colors.secondary[700] : colors.primary[100],
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: `calc(${size} * 0.4)`,
          fontWeight: typography.weights.bold,
          color: theme === 'dark' ? colors.secondary[100] : colors.primary[600]
        }}
      >
        {brandingConfig.shortName}
      </div>
    );
  }

  return (
    <img
      src={logoUrl}
      alt={`${brandingConfig.name} Logo`}
      style={{
        width: size,
        height: size,
        opacity: isLoaded ? 1 : 0,
        transition: 'opacity 0.3s ease-in-out',
        filter: theme === 'dark' ? 'invert(1)' : 'none'
      }}
    />
  );
};

// Componente principal de Branding
export const Branding: React.FC<BrandingProps> = ({
  size = 'md',
  variant = 'default',
  theme = 'auto',
  showTagline = true,
  customTagline,
  href,
  onClick,
  className = '',
  style = {},
  loading = false,
  fallbackText
}) => {
  const currentTheme = useTheme(theme);
  const [logoError, setLogoError] = useState(false);
  
  const config = sizeConfig[size];
  const taglineText = customTagline || brandingConfig.tagline;

  // Estilos base
  const baseStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: config.spacing,
    height: config.height,
    cursor: href || onClick ? 'pointer' : 'default',
    transition: 'all 0.2s ease-in-out',
    ...style
  };

  // Estilos do texto
  const textStyles: React.CSSProperties = {
    fontSize: config.fontSize,
    fontWeight: typography.weights.semibold,
    color: currentTheme === 'dark' ? colors.text.inverse : colors.text.primary,
    fontFamily: typography.families.primary.sans,
    lineHeight: typography.lineHeights.snug,
    margin: 0
  };

  // Estilos da tagline
  const taglineStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.normal,
    color: currentTheme === 'dark' ? colors.text.secondary : colors.text.tertiary,
    fontFamily: typography.families.primary.sans,
    lineHeight: typography.lineHeights.snug,
    margin: 0,
    opacity: 0.8
  };

  // Renderizar conteúdo baseado na variante
  const renderContent = () => {
    switch (variant) {
      case 'icon-only':
        return (
          <Logo
            size={config.logoSize}
            theme={currentTheme}
            variant={variant}
            onError={() => setLogoError(true)}
          />
        );

      case 'compact':
        return (
          <>
            <Logo
              size={config.logoSize}
              theme={currentTheme}
              variant={variant}
              onError={() => setLogoError(true)}
            />
            <span style={textStyles}>
              {logoError ? (fallbackText || brandingConfig.shortName) : brandingConfig.name}
            </span>
          </>
        );

      case 'full':
        return (
          <>
            <Logo
              size={config.logoSize}
              theme={currentTheme}
              variant={variant}
              onError={() => setLogoError(true)}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span style={textStyles}>
                {logoError ? (fallbackText || brandingConfig.shortName) : brandingConfig.name}
              </span>
              {showTagline && (
                <span style={taglineStyles}>
                  {taglineText}
                </span>
              )}
            </div>
          </>
        );

      default:
        return (
          <>
            <Logo
              size={config.logoSize}
              theme={currentTheme}
              variant={variant}
              onError={() => setLogoError(true)}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span style={textStyles}>
                {logoError ? (fallbackText || brandingConfig.shortName) : brandingConfig.name}
              </span>
              {showTagline && variant !== 'compact' && (
                <span style={taglineStyles}>
                  {taglineText}
                </span>
              )}
            </div>
          </>
        );
    }
  };

  // Renderizar com loading
  if (loading) {
    return (
      <div
        style={{
          ...baseStyles,
          opacity: 0.6
        }}
        className={`branding-loading ${className}`}
      >
        <div
          style={{
            width: config.logoSize,
            height: config.logoSize,
            borderRadius: '50%',
            backgroundColor: currentTheme === 'dark' ? colors.secondary[600] : colors.secondary[200],
            animation: 'pulse 1.5s ease-in-out infinite'
          }}
        />
        {variant !== 'icon-only' && (
          <div
            style={{
              width: '120px',
              height: '16px',
              backgroundColor: currentTheme === 'dark' ? colors.secondary[600] : colors.secondary[200],
              borderRadius: '4px',
              animation: 'pulse 1.5s ease-in-out infinite'
            }}
          />
        )}
      </div>
    );
  }

  // Renderizar com link
  if (href) {
    return (
      <a
        href={href}
        style={baseStyles}
        className={`branding-link ${className}`}
        onClick={onClick}
      >
        {renderContent()}
      </a>
    );
  }

  // Renderizar com onClick
  if (onClick) {
    return (
      <button
        type="button"
        style={{
          ...baseStyles,
          background: 'none',
          border: 'none',
          padding: 0
        }}
        className={`branding-button ${className}`}
        onClick={onClick}
      >
        {renderContent()}
      </button>
    );
  }

  // Renderizar padrão
  return (
    <div
      style={baseStyles}
      className={`branding ${className}`}
    >
      {renderContent()}
    </div>
  );
};

// Componente de Logo Simples (para uso em favicon, etc.)
export const SimpleLogo: React.FC<{
  size?: string;
  theme?: 'light' | 'dark' | 'auto';
}> = ({ size = '24px', theme = 'auto' }) => {
  const currentTheme = useTheme(theme);
  const { hasError } = useLogoLoading(brandingConfig.logo.icon);

  if (hasError) {
    return (
      <div
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          backgroundColor: currentTheme === 'dark' ? colors.secondary[700] : colors.primary[100],
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: `calc(${size} * 0.4)`,
          fontWeight: typography.weights.bold,
          color: currentTheme === 'dark' ? colors.secondary[100] : colors.primary[600]
        }}
      >
        {brandingConfig.shortName}
      </div>
    );
  }

  return (
    <img
      src={brandingConfig.logo.icon}
      alt={`${brandingConfig.name} Icon`}
      style={{
        width: size,
        height: size,
        filter: currentTheme === 'dark' ? 'invert(1)' : 'none'
      }}
    />
  );
};

// Componente de Favicon
export const Favicon: React.FC = () => {
  return (
    <link
      rel="icon"
      type="image/svg+xml"
      href={brandingConfig.logo.icon}
    />
  );
};

// Exportações
export default Branding;
export { brandingConfig }; 