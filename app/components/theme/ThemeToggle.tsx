/**
 * ThemeToggle.tsx
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Criticalidade 4.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Componente de toggle de tema
 * - Animações suaves
 * - Feedback visual
 * - Integração com ThemeProvider
 */

import React from 'react';
import { 
  IconButton, 
  Tooltip, 
  Box,
  styled,
  keyframes
} from '@mui/material';
import { 
  LightMode as LightModeIcon, 
  DarkMode as DarkModeIcon 
} from '@mui/icons-material';
import { useTheme } from '../../theme/ThemeProvider';

// ===== ANIMAÇÕES =====
const rotateAnimation = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const pulseAnimation = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
`;

// ===== COMPONENTES ESTILIZADOS =====
const StyledIconButton = styled(IconButton)(({ theme }) => ({
  position: 'relative',
  borderRadius: '50%',
  padding: theme.spacing(1),
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  backgroundColor: theme.palette.mode === 'light' 
    ? 'rgba(255, 193, 7, 0.1)' 
    : 'rgba(156, 39, 176, 0.1)',
  border: `2px solid ${theme.palette.mode === 'light' 
    ? theme.palette.warning.light 
    : theme.palette.secondary.light}`,
  
  '&:hover': {
    backgroundColor: theme.palette.mode === 'light' 
      ? 'rgba(255, 193, 7, 0.2)' 
      : 'rgba(156, 39, 176, 0.2)',
    transform: 'scale(1.05)',
    boxShadow: `0 4px 12px ${theme.palette.mode === 'light' 
      ? 'rgba(255, 193, 7, 0.3)' 
      : 'rgba(156, 39, 176, 0.3)'}`,
  },
  
  '&:active': {
    transform: 'scale(0.95)',
  },
  
  '& .MuiSvgIcon-root': {
    fontSize: '1.5rem',
    color: theme.palette.mode === 'light' 
      ? theme.palette.warning.main 
      : theme.palette.secondary.main,
    transition: 'all 0.3s ease',
  },
}));

const AnimatedIcon = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '100%',
  height: '100%',
  
  '&.rotating': {
    animation: `${rotateAnimation} 0.6s ease-in-out`,
  },
  
  '&.pulsing': {
    animation: `${pulseAnimation} 0.3s ease-in-out`,
  },
}));

const ThemeIndicator = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: -2,
  right: -2,
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: theme.palette.mode === 'light' 
    ? theme.palette.warning.main 
    : theme.palette.secondary.main,
  border: `2px solid ${theme.palette.background.paper}`,
  boxShadow: `0 2px 4px ${theme.palette.mode === 'light' 
    ? 'rgba(255, 193, 7, 0.4)' 
    : 'rgba(156, 39, 176, 0.4)'}`,
  transition: 'all 0.3s ease',
}));

// ===== INTERFACES =====
interface ThemeToggleProps {
  size?: 'small' | 'medium' | 'large';
  showTooltip?: boolean;
  showIndicator?: boolean;
  className?: string;
}

// ===== COMPONENTE PRINCIPAL =====
export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  size = 'medium',
  showTooltip = true,
  showIndicator = true,
  className
}) => {
  const { mode, toggleTheme } = useTheme();
  const [isAnimating, setIsAnimating] = React.useState(false);

  const handleToggle = () => {
    setIsAnimating(true);
    toggleTheme();
    
    // Reset animação após 600ms
    setTimeout(() => {
      setIsAnimating(false);
    }, 600);
  };

  const getIcon = () => {
    return mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />;
  };

  const getTooltipTitle = () => {
    return mode === 'light' 
      ? 'Alternar para modo escuro' 
      : 'Alternar para modo claro';
  };

  const getSizeProps = () => {
    switch (size) {
      case 'small':
        return { padding: 0.5, iconSize: '1.2rem' };
      case 'large':
        return { padding: 1.5, iconSize: '2rem' };
      default:
        return { padding: 1, iconSize: '1.5rem' };
    }
  };

  const sizeProps = getSizeProps();

  const buttonContent = (
    <StyledIconButton
      onClick={handleToggle}
      className={className}
      sx={{
        padding: (theme) => theme.spacing(sizeProps.padding),
        '& .MuiSvgIcon-root': {
          fontSize: sizeProps.iconSize,
        }
      }}
      disabled={isAnimating}
    >
      <AnimatedIcon className={isAnimating ? 'rotating' : ''}>
        {getIcon()}
      </AnimatedIcon>
      
      {showIndicator && (
        <ThemeIndicator />
      )}
    </StyledIconButton>
  );

  if (showTooltip) {
    return (
      <Tooltip 
        title={getTooltipTitle()}
        placement="bottom"
        arrow
      >
        {buttonContent}
      </Tooltip>
    );
  }

  return buttonContent;
};

// ===== COMPONENTE DE DEMONSTRAÇÃO =====
export const ThemeToggleDemo: React.FC = () => {
  return (
    <Box sx={{ 
      display: 'flex', 
      gap: 2, 
      alignItems: 'center',
      padding: 2,
      backgroundColor: 'background.paper',
      borderRadius: 2,
      boxShadow: 1
    }}>
      <Box>
        <ThemeToggle size="small" />
      </Box>
      
      <Box>
        <ThemeToggle size="medium" />
      </Box>
      
      <Box>
        <ThemeToggle size="large" />
      </Box>
      
      <Box>
        <ThemeToggle showIndicator={false} />
      </Box>
      
      <Box>
        <ThemeToggle showTooltip={false} />
      </Box>
    </Box>
  );
};

export default ThemeToggle; 