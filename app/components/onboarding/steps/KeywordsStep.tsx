/**
 * Componente KeywordsStep - Omni Keywords Finder
 * Quarto passo do onboarding: configuração inicial de palavras-chave
 * 
 * Tracing ID: ONBOARDING_KEYWORDS_STEP_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Search, Plus, X, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

interface KeywordsStepProps {
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
  updateData: (updates: any) => void;
  onNext: () => void;
  onBack: () => void;
  isActive: boolean;
  errors: string[];
}

interface ValidationErrors {
  initial?: string;
  competitors?: string;
}

const KeywordsStep: React.FC<KeywordsStepProps> = ({ 
  data, 
  updateData, 
  onNext, 
  onBack,
  isActive,
  errors 
}) => {
  const [initialKeywords, setInitialKeywords] = useState<string[]>(data.keywords?.initial || []);
  const [competitorKeywords, setCompetitorKeywords] = useState<string[]>(data.keywords?.competitors || []);
  const [newKeyword, setNewKeyword] = useState('');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState(false);

  // Sugestões baseadas na indústria e objetivos
  const getIndustrySuggestions = () => {
    const industry = data.company?.industry;
    const goals = data.goals?.primary || [];
    
    const suggestions: { [key: string]: string[] } = {
      'Tecnologia': [
        'software desenvolvimento',
        'sistema gestão',
        'tecnologia inovação',
        'startup tecnologia',
        'solução digital'
      ],
      'E-commerce': [
        'loja online',
        'ecommerce plataforma',
        'venda internet',
        'marketplace digital',
        'compras online'
      ],
      'Saúde': [
        'clínica médica',
        'consulta online',
        'exame laboratório',
        'plano saúde',
        'telemedicina'
      ],
      'Educação': [
        'curso online',
        'treinamento profissional',
        'educação digital',
        'certificação',
        'aprendizado online'
      ],
      'Finanças': [
        'investimento financeiro',
        'consultoria financeira',
        'planejamento financeiro',
        'gestão patrimonial',
        'financiamento'
      ],
      'Marketing Digital': [
        'agência marketing',
        'publicidade digital',
        'seo otimização',
        'tráfego orgânico',
        'conversão leads'
      ]
    };

    return suggestions[industry] || [
      'palavra-chave principal',
      'termo busca',
      'otimização seo',
      'marketing digital',
      'solução problema'
    ];
  };

  const industrySuggestions = getIndustrySuggestions();

  // Validação em tempo real
  useEffect(() => {
    const errors: ValidationErrors = {};
    
    // Validar palavras-chave iniciais
    if (initialKeywords.length === 0) {
      errors.initial = 'Adicione pelo menos uma palavra-chave inicial';
    }
    
    setValidationErrors(errors);
    setIsValid(Object.keys(errors).length === 0 && initialKeywords.length > 0);
  }, [initialKeywords]);

  const addInitialKeyword = (keyword: string) => {
    const trimmedKeyword = keyword.trim().toLowerCase();
    if (trimmedKeyword && !initialKeywords.includes(trimmedKeyword)) {
      setInitialKeywords(prev => [...prev, trimmedKeyword]);
    }
  };

  const removeInitialKeyword = (keyword: string) => {
    setInitialKeywords(prev => prev.filter(k => k !== keyword));
  };

  const addCompetitorKeyword = (keyword: string) => {
    const trimmedKeyword = keyword.trim().toLowerCase();
    if (trimmedKeyword && !competitorKeywords.includes(trimmedKeyword)) {
      setCompetitorKeywords(prev => [...prev, trimmedKeyword]);
    }
  };

  const removeCompetitorKeyword = (keyword: string) => {
    setCompetitorKeywords(prev => prev.filter(k => k !== keyword));
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim()) {
      addInitialKeyword(newKeyword);
      setNewKeyword('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddKeyword();
    }
  };

  const handleNext = () => {
    if (isValid) {
      updateData({
        keywords: {
          initial: initialKeywords,
          competitors: competitorKeywords,
          suggestions: industrySuggestions
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
          className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 rounded-full flex items-center justify-center mx-auto"
        >
          <Search className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.h2
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900"
        >
          Suas palavras-chave
        </motion.h2>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 max-w-md mx-auto"
        >
          Adicione as palavras-chave principais que você gostaria de otimizar.
        </motion.p>
      </div>

      {/* Formulário */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="space-y-6"
      >
        {/* Palavras-chave Iniciais */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Palavras-chave Principais <span className="text-red-500">*</span>
          </label>
          
          {/* Input para adicionar */}
          <div className="flex space-x-2 mb-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Digite uma palavra-chave..."
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-5 h-5 text-gray-400" />
              </div>
            </div>
            <button
              onClick={handleAddKeyword}
              disabled={!newKeyword.trim()}
              className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          {/* Lista de palavras-chave */}
          <div className="space-y-2">
            {initialKeywords.map((keyword, index) => (
              <motion.div
                key={keyword}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">{keyword}</span>
                </div>
                <button
                  onClick={() => removeInitialKeyword(keyword)}
                  className="p-1 text-red-500 hover:bg-red-100 rounded-full transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </div>

          {validationErrors.initial && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.initial}
            </motion.p>
          )}
        </div>

        {/* Sugestões baseadas na indústria */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Sugestões para {data.company?.industry || 'seu setor'}
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {industrySuggestions.map((suggestion) => (
              <motion.button
                key={suggestion}
                onClick={() => addInitialKeyword(suggestion)}
                disabled={initialKeywords.includes(suggestion)}
                className={`p-3 border rounded-lg text-left transition-all duration-200 ${
                  initialKeywords.includes(suggestion)
                    ? 'border-green-500 bg-green-50 cursor-not-allowed'
                    : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                }`}
                whileHover={!initialKeywords.includes(suggestion) ? { scale: 1.02 } : {}}
                whileTap={!initialKeywords.includes(suggestion) ? { scale: 0.98 } : {}}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-900">{suggestion}</span>
                  {initialKeywords.includes(suggestion) ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <Plus className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Palavras-chave de Concorrentes (Opcional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Palavras-chave de Concorrentes <span className="text-gray-500">(opcional)</span>
          </label>
          <p className="text-sm text-gray-600 mb-3">
            Adicione palavras-chave que seus concorrentes estão usando para análise competitiva.
          </p>
          
          <div className="space-y-2">
            {competitorKeywords.map((keyword, index) => (
              <motion.div
                key={keyword}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-900">{keyword}</span>
                </div>
                <button
                  onClick={() => removeCompetitorKeyword(keyword)}
                  className="p-1 text-red-500 hover:bg-red-100 rounded-full transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </div>

          {/* Input rápido para concorrentes */}
          <div className="flex space-x-2 mt-3">
            <input
              type="text"
              placeholder="Palavra-chave do concorrente..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                  addCompetitorKeyword(e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <button
              onClick={() => {
                const input = document.querySelector('input[placeholder="Palavra-chave do concorrente..."]') as HTMLInputElement;
                if (input?.value.trim()) {
                  addCompetitorKeyword(input.value);
                  input.value = '';
                }
              }}
              className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
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
            'Adicione pelo menos uma palavra-chave'
          )}
        </button>
      </motion.div>

      {/* Dicas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="bg-orange-50 border border-orange-200 rounded-lg p-4"
      >
        <h4 className="text-sm font-medium text-orange-900 mb-2">
          💡 Dica rápida
        </h4>
        <p className="text-sm text-orange-700">
          Foque em palavras-chave específicas e relevantes para seu negócio. Palavras-chave long-tail geralmente têm menos concorrência e melhor conversão.
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
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
      </motion.div>
    </motion.div>
  );
};

export default KeywordsStep; 