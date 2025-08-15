/**
 * Unauthorized.tsx
 * 
 * Componente para página de acesso negado (401/403)
 * 
 * Tracing ID: UNAUTHORIZED_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.1.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Página de acesso negado
 * - Redirecionamento para login
 * - Contato com suporte
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

export const Unauthorized: React.FC = () => {
  const navigate = useNavigate();

  const handleGoLogin = () => {
    navigate('/login');
  };

  const handleGoHome = () => {
    navigate('/dashboard');
  };

  const handleContactSupport = () => {
    // Abrir modal de contato ou redirecionar para página de suporte
    window.open('mailto:suporte@omni.com?subject=Acesso Negado', '_blank');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full text-center">
        {/* Ícone de acesso negado */}
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>

        {/* Título e descrição */}
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Acesso Negado</h1>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Você não tem permissão para acessar esta página
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Entre em contato com o administrador do sistema se você acredita que deveria ter acesso a esta funcionalidade.
        </p>

        {/* Ações */}
        <div className="space-y-4">
          <button
            onClick={handleGoHome}
            className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Ir para o Dashboard
          </button>
          
          <button
            onClick={handleGoLogin}
            className="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            Fazer Login
          </button>
        </div>

        {/* Contato com suporte */}
        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Precisa de ajuda?
          </p>
          <button
            onClick={handleContactSupport}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Contatar Suporte
          </button>
        </div>

        {/* Informações adicionais */}
        <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="text-sm text-yellow-800 dark:text-yellow-200">
              <p className="font-medium">Dica:</p>
              <p>Verifique se você está logado com a conta correta e se possui as permissões necessárias para acessar esta funcionalidade.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized; 