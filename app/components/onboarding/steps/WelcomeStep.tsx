/**
 * Componente WelcomeStep - Omni Keywords Finder
 * Primeiro passo do onboarding: boas-vindas e dados básicos
 * 
 * Tracing ID: ONBOARDING_WELCOME_STEP_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, User, Mail, CheckCircle, AlertCircle } from 'lucide-react';

interface WelcomeStepProps {
  data: {
    user: {
      name: string;
      email: string;
      company: string;
      role: string;
    };
  };
  updateData: (updates: any) => void;
  onNext: () => void;
  isActive: boolean;
  errors: string[];
}

interface ValidationErrors {
  name?: string;
  email?: string;
}

const WelcomeStep: React.FC<WelcomeStepProps> = ({ 
  data, 
  updateData, 
  onNext, 
  isActive,
  errors 
}) => {
  const [name, setName] = useState(data.user.name || '');
  const [email, setEmail] = useState(data.user.email || '');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState(false);

  // Validação em tempo real
  useEffect(() => {
    const errors: ValidationErrors = {};
    
    // Validar nome
    if (!name.trim()) {
      errors.name = 'Nome é obrigatório';
    } else if (name.trim().length < 2) {
      errors.name = 'Nome deve ter pelo menos 2 caracteres';
    }
    
    // Validar email
    if (!email.trim()) {
      errors.email = 'E-mail é obrigatório';
    } else if (!isValidEmail(email)) {
      errors.email = 'E-mail deve ter um formato válido';
    }
    
    setValidationErrors(errors);
    setIsValid(Object.keys(errors).length === 0 && name.trim() && email.trim());
  }, [name, email]);

  const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleNext = () => {
    if (isValid) {
      updateData({
        user: {
          ...data.user,
          name: name.trim(),
          email: email.trim()
        }
      });
      onNext();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && isValid) {
      handleNext();
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
          className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto"
        >
          <User className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.h2
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900"
        >
          Bem-vindo ao Omni Keywords Finder
        </motion.h2>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 max-w-md mx-auto"
        >
          Vamos configurar sua conta em menos de 5 minutos para começar a otimizar suas palavras-chave.
        </motion.p>
      </div>

      {/* Formulário */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="space-y-4"
      >
        {/* Campo Nome */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nome Completo
          </label>
          <div className="relative">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyPress={handleKeyPress}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                validationErrors.name 
                  ? 'border-red-300 bg-red-50' 
                  : name.trim() 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
              placeholder="Digite seu nome completo"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User className={`w-5 h-5 ${
                validationErrors.name 
                  ? 'text-red-400' 
                  : name.trim() 
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {name.trim() && !validationErrors.name && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
          </div>
          {validationErrors.name && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.name}
            </motion.p>
          )}
        </div>

        {/* Campo Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            E-mail
          </label>
          <div className="relative">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={handleKeyPress}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                validationErrors.email 
                  ? 'border-red-300 bg-red-50' 
                  : email.trim() && isValidEmail(email)
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
              placeholder="seu@email.com"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className={`w-5 h-5 ${
                validationErrors.email 
                  ? 'text-red-400' 
                  : email.trim() && isValidEmail(email)
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {email.trim() && isValidEmail(email) && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
          </div>
          {validationErrors.email && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.email}
            </motion.p>
          )}
        </div>
      </motion.div>

      {/* Botão de ação */}
      <motion.button
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.6 }}
        onClick={handleNext}
        disabled={!isValid}
        className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-200 flex items-center justify-center ${
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
          'Preencha os campos obrigatórios'
        )}
      </motion.button>

      {/* Dicas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="bg-blue-50 border border-blue-200 rounded-lg p-4"
      >
        <h4 className="text-sm font-medium text-blue-900 mb-2">
          💡 Dica rápida
        </h4>
        <p className="text-sm text-blue-700">
          Use o e-mail que você utiliza para acessar o sistema. Isso facilitará o processo de recuperação de conta.
        </p>
      </motion.div>

      {/* Indicador de progresso */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex items-center justify-center space-x-2 text-sm text-gray-500"
      >
        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
      </motion.div>
    </motion.div>
  );
};

export default WelcomeStep; 