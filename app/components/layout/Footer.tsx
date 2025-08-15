/**
 * Footer.tsx
 * 
 * Componente de rodapé principal
 * 
 * Tracing ID: FOOTER_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Informações de copyright
 * - Links úteis
 * - Status do sistema
 * - Versão da aplicação
 */

import React from 'react';
import { useAppStore } from '../../store/AppStore';

interface FooterProps {
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({ className = '' }) => {
  const { state } = useAppStore();
  const currentYear = new Date().getFullYear();

  return (
    <footer className={`bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          {/* Lado esquerdo - Copyright e versão */}
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-xs">OK</span>
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                © {currentYear} Omni Keywords Finder
              </span>
            </div>
            
            <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
              <span>v{state.config.version}</span>
              <span className="hidden md:inline">•</span>
              <span className="capitalize">{state.config.environment}</span>
              <span className="hidden md:inline">•</span>
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Online</span>
              </span>
            </div>
          </div>

          {/* Centro - Links úteis */}
          <div className="hidden md:flex items-center space-x-6 text-sm">
            <a 
              href="/docs" 
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Documentação
            </a>
            <a 
              href="/support" 
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Suporte
            </a>
            <a 
              href="/privacy" 
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Privacidade
            </a>
            <a 
              href="/terms" 
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Termos
            </a>
          </div>

          {/* Lado direito - Status e métricas */}
          <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
            <div className="hidden lg:flex items-center space-x-4">
              <span className="flex items-center space-x-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
                <span>{state.data.nichos.length} nichos</span>
              </span>
              
              <span className="flex items-center space-x-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{state.data.execucoes.filter(e => e.status === 'concluida').length} execuções</span>
              </span>
              
              <span className="flex items-center space-x-1">
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                <span>{state.data.analytics.tempoMedioExecucao}s média</span>
              </span>
            </div>
            
            <button
              onClick={() => {
                // Abrir modal de status do sistema
                console.log('Status do sistema');
              }}
              className="flex items-center space-x-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              title="Status do sistema"
            >
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="hidden sm:inline">Status</span>
            </button>
          </div>
        </div>

        {/* Linha inferior - Informações adicionais */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-2 md:space-y-0 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-4">
              <span>API: {state.config.apiBaseUrl}</span>
              <span>•</span>
              <span>Última atualização: {new Date().toLocaleTimeString()}</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span>Desenvolvido com ❤️</span>
              <span>•</span>
              <span>React + TypeScript</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 