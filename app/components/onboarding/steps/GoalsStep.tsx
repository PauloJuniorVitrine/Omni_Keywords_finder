/**
 * Componente GoalsStep - Omni Keywords Finder
 * Terceiro passo do onboarding: definição de objetivos
 * 
 * Tracing ID: ONBOARDING_GOALS_STEP_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Target, TrendingUp, CheckCircle, AlertCircle, Star } from 'lucide-react';

interface GoalsStepProps {
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
  };
  updateData: (updates: any) => void;
  onNext: () => void;
  onBack: () => void;
  isActive: boolean;
  errors: string[];
}

interface ValidationErrors {
  primary?: string;
  timeframe?: string;
  priority?: string;
}

const GoalsStep: React.FC<GoalsStepProps> = ({ 
  data, 
  updateData, 
  onNext, 
  onBack,
  isActive,
  errors 
}) => {
  const [selectedPrimary, setSelectedPrimary] = useState<string[]>(data.goals?.primary || []);
  const [selectedSecondary, setSelectedSecondary] = useState<string[]>(data.goals?.secondary || []);
  const [timeframe, setTimeframe] = useState(data.goals?.timeframe || '');
  const [budget, setBudget] = useState(data.goals?.budget || '');
  const [priority, setPriority] = useState(data.goals?.priority || '');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState(false);

  const primaryGoals = [
    { id: 'increase-traffic', label: 'Aumentar tráfego orgânico', icon: '📈' },
    { id: 'improve-rankings', label: 'Melhorar posicionamento', icon: '🏆' },
    { id: 'generate-leads', label: 'Gerar mais leads', icon: '🎯' },
    { id: 'increase-sales', label: 'Aumentar vendas', icon: '💰' },
    { id: 'brand-awareness', label: 'Aumentar reconhecimento da marca', icon: '🌟' },
    { id: 'competitor-analysis', label: 'Análise de concorrência', icon: '🔍' }
  ];

  const secondaryGoals = [
    { id: 'content-optimization', label: 'Otimização de conteúdo', icon: '📝' },
    { id: 'local-seo', label: 'SEO Local', icon: '📍' },
    { id: 'technical-seo', label: 'SEO Técnico', icon: '⚙️' },
    { id: 'link-building', label: 'Link Building', icon: '🔗' },
    { id: 'keyword-research', label: 'Pesquisa de palavras-chave', icon: '🔎' },
    { id: 'performance-monitoring', label: 'Monitoramento de performance', icon: '📊' }
  ];

  const timeframeOptions = [
    { value: '1-3-months', label: '1-3 meses' },
    { value: '3-6-months', label: '3-6 meses' },
    { value: '6-12-months', label: '6-12 meses' },
    { value: '12+months', label: 'Mais de 12 meses' }
  ];

  const budgetOptions = [
    { value: 'low', label: 'Baixo (até R$ 500/mês)', icon: '💰' },
    { value: 'medium', label: 'Médio (R$ 500-2000/mês)', icon: '💰💰' },
    { value: 'high', label: 'Alto (acima de R$ 2000/mês)', icon: '💰💰💰' },
    { value: 'enterprise', label: 'Enterprise (sob consulta)', icon: '🏢' }
  ];

  const priorityOptions = [
    { value: 'high', label: 'Alta prioridade', color: 'text-red-600' },
    { value: 'medium', label: 'Média prioridade', color: 'text-yellow-600' },
    { value: 'low', label: 'Baixa prioridade', color: 'text-green-600' }
  ];

  // Validação em tempo real
  useEffect(() => {
    const errors: ValidationErrors = {};
    
    // Validar objetivos primários
    if (selectedPrimary.length === 0) {
      errors.primary = 'Selecione pelo menos um objetivo principal';
    }
    
    // Validar prazo
    if (!timeframe) {
      errors.timeframe = 'Selecione um prazo';
    }
    
    // Validar prioridade
    if (!priority) {
      errors.priority = 'Selecione uma prioridade';
    }
    
    setValidationErrors(errors);
    setIsValid(Object.keys(errors).length === 0 && selectedPrimary.length > 0 && timeframe && priority);
  }, [selectedPrimary, timeframe, priority]);

  const togglePrimaryGoal = (goalId: string) => {
    setSelectedPrimary(prev => 
      prev.includes(goalId) 
        ? prev.filter(id => id !== goalId)
        : [...prev, goalId]
    );
  };

  const toggleSecondaryGoal = (goalId: string) => {
    setSelectedSecondary(prev => 
      prev.includes(goalId) 
        ? prev.filter(id => id !== goalId)
        : [...prev, goalId]
    );
  };

  const handleNext = () => {
    if (isValid) {
      updateData({
        goals: {
          primary: selectedPrimary,
          secondary: selectedSecondary,
          timeframe,
          budget,
          priority
        }
      });
      onNext();
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
          className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto"
        >
          <Target className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.h2
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900"
        >
          Seus objetivos
        </motion.h2>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 max-w-md mx-auto"
        >
          Defina seus objetivos principais para otimizarmos as recomendações de palavras-chave.
        </motion.p>
      </div>

      {/* Formulário */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="space-y-6"
      >
        {/* Objetivos Primários */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Objetivos Principais <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {primaryGoals.map((goal) => (
              <motion.button
                key={goal.id}
                onClick={() => togglePrimaryGoal(goal.id)}
                className={`p-4 border rounded-lg text-left transition-all duration-200 ${
                  selectedPrimary.includes(goal.id)
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{goal.icon}</span>
                  <span className="text-sm font-medium text-gray-900">
                    {goal.label}
                  </span>
                  {selectedPrimary.includes(goal.id) && (
                    <CheckCircle className="w-5 h-5 text-blue-500 ml-auto" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
          {validationErrors.primary && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.primary}
            </motion.p>
          )}
        </div>

        {/* Objetivos Secundários */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Objetivos Secundários <span className="text-gray-500">(opcional)</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {secondaryGoals.map((goal) => (
              <motion.button
                key={goal.id}
                onClick={() => toggleSecondaryGoal(goal.id)}
                className={`p-4 border rounded-lg text-left transition-all duration-200 ${
                  selectedSecondary.includes(goal.id)
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{goal.icon}</span>
                  <span className="text-sm font-medium text-gray-900">
                    {goal.label}
                  </span>
                  {selectedSecondary.includes(goal.id) && (
                    <CheckCircle className="w-5 h-5 text-green-500 ml-auto" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Prazo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Prazo para resultados <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {timeframeOptions.map((option) => (
              <motion.button
                key={option.value}
                onClick={() => setTimeframe(option.value)}
                className={`p-3 border rounded-lg text-center transition-all duration-200 ${
                  timeframe === option.value
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-sm font-medium text-gray-900">
                  {option.label}
                </span>
                {timeframe === option.value && (
                  <CheckCircle className="w-4 h-4 text-blue-500 mx-auto mt-1" />
                )}
              </motion.button>
            ))}
          </div>
          {validationErrors.timeframe && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.timeframe}
            </motion.p>
          )}
        </div>

        {/* Orçamento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Orçamento mensal <span className="text-gray-500">(opcional)</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {budgetOptions.map((option) => (
              <motion.button
                key={option.value}
                onClick={() => setBudget(option.value)}
                className={`p-4 border rounded-lg text-left transition-all duration-200 ${
                  budget === option.value
                    ? 'border-purple-500 bg-purple-50 shadow-md'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{option.icon}</span>
                  <span className="text-sm font-medium text-gray-900">
                    {option.label}
                  </span>
                  {budget === option.value && (
                    <CheckCircle className="w-5 h-5 text-purple-500 ml-auto" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Prioridade */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Prioridade <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {priorityOptions.map((option) => (
              <motion.button
                key={option.value}
                onClick={() => setPriority(option.value)}
                className={`p-4 border rounded-lg text-center transition-all duration-200 ${
                  priority === option.value
                    ? 'border-orange-500 bg-orange-50 shadow-md'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center justify-center space-x-2">
                  <Star className={`w-5 h-5 ${option.color}`} />
                  <span className="text-sm font-medium text-gray-900">
                    {option.label}
                  </span>
                  {priority === option.value && (
                    <CheckCircle className="w-5 h-5 text-orange-500" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
          {validationErrors.priority && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.priority}
            </motion.p>
          )}
        </div>
      </motion.div>

      {/* Botões de navegação */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
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
          onClick={handleNext}
          disabled={!isValid}
          className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all duration-200 flex items-center justify-center ${
            isValid
              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl transform hover:scale-105'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isValid ? (
            <>
              Continuar
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          ) : (
            'Selecione os campos obrigatórios'
          )}
        </button>
      </motion.div>

      {/* Dicas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="bg-purple-50 border border-purple-200 rounded-lg p-4"
      >
        <h4 className="text-sm font-medium text-purple-900 mb-2">
          💡 Dica rápida
        </h4>
        <p className="text-sm text-purple-700">
          Selecione objetivos realistas baseados no seu prazo e orçamento. Podemos ajustar as estratégias conforme necessário.
        </p>
      </motion.div>

      {/* Indicador de progresso */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex items-center justify-center space-x-2 text-sm text-gray-500"
      >
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
      </motion.div>
    </motion.div>
  );
};

export default GoalsStep; 