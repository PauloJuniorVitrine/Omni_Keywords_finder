/**
 * Componente FinishStep - Omni Keywords Finder
 * Quinto e último passo do onboarding: resumo e finalização
 * 
 * Tracing ID: ONBOARDING_FINISH_STEP_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle, User, Building, Target, Search, Rocket, Mail, Calendar, Star } from 'lucide-react';

interface FinishStepProps {
  data: {
    user: {
      name: string;
      email: string;
      company: string;
      role: string;
    };
    company: {
      name: string;
      industry: string;
      size: string;
      website: string;
      country: string;
    };
    goals: {
      primary: string[];
      secondary: string[];
      timeframe: string;
      budget: string;
      priority: string;
    };
    keywords: {
      initial: string[];
      competitors: string[];
      suggestions: string[];
    };
  };
  onBack: () => void;
  onFinish: () => void;
  isActive: boolean;
  errors: string[];
}

const FinishStep: React.FC<FinishStepProps> = ({ 
  data, 
  onBack, 
  onFinish,
  isActive,
  errors 
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getTimeframeLabel = (timeframe: string) => {
    const labels: { [key: string]: string } = {
      '1-3-months': '1-3 meses',
      '3-6-months': '3-6 meses',
      '6-12-months': '6-12 meses',
      '12+months': 'Mais de 12 meses'
    };
    return labels[timeframe] || timeframe;
  };

  const getBudgetLabel = (budget: string) => {
    const labels: { [key: string]: string } = {
      'low': 'Baixo (até R$ 500/mês)',
      'medium': 'Médio (R$ 500-2000/mês)',
      'high': 'Alto (acima de R$ 2000/mês)',
      'enterprise': 'Enterprise (sob consulta)'
    };
    return labels[budget] || budget;
  };

  const getPriorityLabel = (priority: string) => {
    const labels: { [key: string]: string } = {
      'high': 'Alta prioridade',
      'medium': 'Média prioridade',
      'low': 'Baixa prioridade'
    };
    return labels[priority] || priority;
  };

  const getPriorityColor = (priority: string) => {
    const colors: { [key: string]: string } = {
      'high': 'text-red-600',
      'medium': 'text-yellow-600',
      'low': 'text-green-600'
    };
    return colors[priority] || 'text-gray-600';
  };

  const handleFinish = async () => {
    setIsSubmitting(true);
    try {
      // Simular envio dos dados
      await new Promise(resolve => setTimeout(resolve, 2000));
      onFinish();
    } catch (error) {
      console.error('Erro ao finalizar onboarding:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: isActive ? 1 : 0.5, x: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto"
        >
          <Rocket className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.h2
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900"
        >
          Tudo pronto!
        </motion.h2>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 max-w-md mx-auto"
        >
          Revise suas informações e vamos começar a otimizar suas palavras-chave.
        </motion.p>
      </div>

      {/* Resumo dos dados */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="space-y-4"
      >
        {/* Informações do Usuário */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <User className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium text-blue-900">Informações Pessoais</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-600">Nome:</span>
              <span className="ml-2 font-medium text-gray-900">{data.user.name}</span>
            </div>
            <div>
              <span className="text-gray-600">E-mail:</span>
              <span className="ml-2 font-medium text-gray-900">{data.user.email}</span>
            </div>
          </div>
        </div>

        {/* Informações da Empresa */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Building className="w-5 h-5 text-green-600" />
            <h3 className="font-medium text-green-900">Empresa</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-600">Nome:</span>
              <span className="ml-2 font-medium text-gray-900">{data.company.name}</span>
            </div>
            <div>
              <span className="text-gray-600">Setor:</span>
              <span className="ml-2 font-medium text-gray-900">{data.company.industry}</span>
            </div>
            <div>
              <span className="text-gray-600">Tamanho:</span>
              <span className="ml-2 font-medium text-gray-900">{data.company.size}</span>
            </div>
            {data.company.website && (
              <div>
                <span className="text-gray-600">Website:</span>
                <span className="ml-2 font-medium text-gray-900">{data.company.website}</span>
              </div>
            )}
          </div>
        </div>

        {/* Objetivos */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Target className="w-5 h-5 text-purple-600" />
            <h3 className="font-medium text-purple-900">Objetivos</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Principais:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {data.goals.primary.map((goal, index) => (
                  <span
                    key={goal}
                    className="inline-block px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs"
                  >
                    {goal}
                  </span>
                ))}
              </div>
            </div>
            {data.goals.secondary.length > 0 && (
              <div>
                <span className="text-gray-600">Secundários:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {data.goals.secondary.map((goal) => (
                    <span
                      key={goal}
                      className="inline-block px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs"
                    >
                      {goal}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <div>
                <span className="text-gray-600">Prazo:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {getTimeframeLabel(data.goals.timeframe)}
                </span>
              </div>
              <div>
                <span className="text-gray-600">Orçamento:</span>
                <span className="ml-2 font-medium text-gray-900">
                  {getBudgetLabel(data.goals.budget)}
                </span>
              </div>
              <div>
                <span className="text-gray-600">Prioridade:</span>
                <span className={`ml-2 font-medium ${getPriorityColor(data.goals.priority)}`}>
                  {getPriorityLabel(data.goals.priority)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Palavras-chave */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Search className="w-5 h-5 text-orange-600" />
            <h3 className="font-medium text-orange-900">Palavras-chave</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Principais ({data.keywords.initial.length}):</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {data.keywords.initial.map((keyword) => (
                  <span
                    key={keyword}
                    className="inline-block px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
            {data.keywords.competitors.length > 0 && (
              <div>
                <span className="text-gray-600">Concorrentes ({data.keywords.competitors.length}):</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {data.keywords.competitors.map((keyword) => (
                    <span
                      key={keyword}
                      className="inline-block px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Próximos passos */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4"
      >
        <h4 className="font-medium text-gray-900 mb-3">🎯 O que acontece agora?</h4>
        <div className="space-y-2 text-sm text-gray-700">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Análise completa das suas palavras-chave</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Relatório personalizado de oportunidades</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Estratégia de otimização customizada</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Dashboard completo em até 24 horas</span>
          </div>
        </div>
      </motion.div>

      {/* Botões de navegação */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="flex space-x-4"
      >
        <button
          onClick={onBack}
          className="flex-1 py-3 px-6 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar
        </button>
        
        <button
          onClick={handleFinish}
          disabled={isSubmitting}
          className="flex-1 py-3 px-6 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Finalizando...
            </>
          ) : (
            <>
              <Rocket className="w-4 h-4 mr-2" />
              Começar Otimização
            </>
          )}
        </button>
      </motion.div>

      {/* Informações adicionais */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center space-y-2 text-sm text-gray-500"
      >
        <p>Você receberá um e-mail de confirmação em {data.user.email}</p>
        <p>Nossa equipe entrará em contato em até 2 horas úteis</p>
      </motion.div>

      {/* Indicador de progresso */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="flex items-center justify-center space-x-2 text-sm text-gray-500"
      >
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-green-600 rounded-full"></div>
      </motion.div>
    </motion.div>
  );
};

export default FinishStep; 