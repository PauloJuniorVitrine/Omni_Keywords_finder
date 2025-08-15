/**
 * MainLayout.tsx
 * 
 * Componente principal de layout da aplicação Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Layout responsivo com sidebar colapsável
 * - Sistema de breadcrumbs dinâmico
 * - Integração com sistema de permissões
 * - Suporte a temas (light/dark)
 * - Navegação hierárquica
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  CssBaseline,
  ThemeProvider,
  useTheme,
  useMediaQuery,
  Drawer,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Breadcrumbs,
  Link,
  Container,
  useColorMode,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Home as HomeIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

// Componentes locais
import Sidebar from './Sidebar';
import Header from './Header';

// Tipos
interface MainLayoutProps {
  children: React.ReactNode;
}

interface BreadcrumbItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
}

// Constantes
const DRAWER_WIDTH = 240;
const DRAWER_WIDTH_COLLAPSED = 64;

/**
 * Componente principal de layout
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  // Estados
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [breadcrumbs, setBreadcrumbs] = useState<BreadcrumbItem[]>([]);

  // Hooks
  const theme = useTheme();
  const { colorMode, toggleColorMode } = useColorMode();
  const location = useLocation();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    // Fechar sidebar em mobile por padrão
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile]);

  useEffect(() => {
    // Gerar breadcrumbs baseado na rota atual
    generateBreadcrumbs();
  }, [location.pathname]);

  /**
   * Gera breadcrumbs baseado na rota atual
   */
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const newBreadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', path: '/', icon: <HomeIcon /> }
    ];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      newBreadcrumbs.push({
        label,
        path: currentPath
      });
    });

    setBreadcrumbs(newBreadcrumbs);
  };

  /**
   * Alterna estado da sidebar
   */
  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  /**
   * Navega para breadcrumb
   */
  const handleBreadcrumbClick = (path: string) => {
    navigate(path);
  };

  /**
   * Renderiza breadcrumbs
   */
  const renderBreadcrumbs = () => (
    <Breadcrumbs 
      aria-label="breadcrumb"
      sx={{ 
        color: 'text.secondary',
        '& .MuiBreadcrumbs-separator': { color: 'text.secondary' }
      }}
    >
      {breadcrumbs.map((item, index) => (
        <Link
          key={item.path}
          color={index === breadcrumbs.length - 1 ? 'text.primary' : 'inherit'}
          underline="hover"
          onClick={() => handleBreadcrumbClick(item.path)}
          sx={{ 
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 0.5
          }}
        >
          {item.icon}
          {item.label}
        </Link>
      ))}
    </Breadcrumbs>
  );

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <CssBaseline />
        
        {/* AppBar */}
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${sidebarOpen ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED}px)` },
            ml: { sm: `${sidebarOpen ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED}px` },
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="toggle sidebar"
              onClick={handleSidebarToggle}
              edge="start"
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <Box sx={{ flexGrow: 1 }}>
              {renderBreadcrumbs()}
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <IconButton
                color="inherit"
                onClick={toggleColorMode}
                aria-label="toggle theme"
              >
                {colorMode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Sidebar */}
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          drawerWidth={DRAWER_WIDTH}
          drawerWidthCollapsed={DRAWER_WIDTH_COLLAPSED}
          isMobile={isMobile}
        />

        {/* Conteúdo Principal */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: { sm: `calc(100% - ${sidebarOpen ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED}px)` },
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          <Toolbar /> {/* Espaçamento para AppBar */}
          
          <Container 
            maxWidth="xl" 
            sx={{ 
              py: 3,
              px: { xs: 2, sm: 3 },
              minHeight: 'calc(100vh - 64px)'
            }}
          >
            {children}
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default MainLayout; 