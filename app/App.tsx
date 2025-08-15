/**
 * App.tsx
 * 
 * Componente principal da aplicação
 * 
 * Tracing ID: APP_MAIN_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Integração do AppRouter
 * - Layout base (Header, Sidebar, Footer)
 * - Sistema de autenticação
 * - Estado global
 * - Tema global
 */

import React, { useState } from 'react';
import { AppRouter } from './routes/AppRouter';
import { AppStoreProvider } from './store/AppStore';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './theme/ThemeProvider';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';
import { ErrorBoundary } from './components/error/ErrorBoundary';
import { LoadingSpinner } from './components/shared/LoadingSpinner';

const App: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <ErrorBoundary>
      <AppStoreProvider>
        <ThemeProvider>
          <AuthProvider>
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
              {/* Layout principal */}
              <div className="flex h-screen">
                {/* Sidebar */}
                <Sidebar 
                  collapsed={sidebarCollapsed}
                  onToggle={handleToggleSidebar}
                />
                
                {/* Conteúdo principal */}
                <div className="flex-1 flex flex-col overflow-hidden">
                  {/* Header */}
                  <Header 
                    onToggleSidebar={handleToggleSidebar}
                    sidebarCollapsed={sidebarCollapsed}
                  />
                  
                  {/* Conteúdo da aplicação */}
                  <main className="flex-1 overflow-auto">
                    <div className="p-6">
                      <AppRouter />
                    </div>
                  </main>
                  
                  {/* Footer */}
                  <Footer />
                </div>
              </div>
            </div>
          </AuthProvider>
        </ThemeProvider>
      </AppStoreProvider>
    </ErrorBoundary>
  );
};

export default App; 