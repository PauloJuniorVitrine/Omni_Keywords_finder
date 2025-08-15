/**
 * Componente CompanyStep - Omni Keywords Finder
 * Segundo passo do onboarding: configuração da empresa
 * 
 * Tracing ID: ONBOARDING_COMPANY_STEP_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Componente de Onboarding
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Building, Users, CheckCircle, AlertCircle, Globe } from 'lucide-react';

interface CompanyStepProps {
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
  };
  updateData: (updates: any) => void;
  onNext: () => void;
  onBack: () => void;
  isActive: boolean;
  errors: string[];
}

interface ValidationErrors {
  companyName?: string;
  industry?: string;
  size?: string;
  website?: string;
}

const CompanyStep: React.FC<CompanyStepProps> = ({ 
  data, 
  updateData, 
  onNext, 
  onBack,
  isActive,
  errors 
}) => {
  const [companyName, setCompanyName] = useState(data.company?.name || '');
  const [industry, setIndustry] = useState(data.company?.industry || '');
  const [size, setSize] = useState(data.company?.size || '');
  const [website, setWebsite] = useState(data.company?.website || '');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState(false);

  const industryOptions = [
    'Tecnologia',
    'E-commerce',
    'Saúde',
    'Educação',
    'Finanças',
    'Marketing Digital',
    'Consultoria',
    'Varejo',
    'Serviços',
    'Manufatura',
    'Outro'
  ];

  const sizeOptions = [
    { value: '1-10', label: '1-10 funcionários' },
    { value: '11-50', label: '11-50 funcionários' },
    { value: '51-200', label: '51-200 funcionários' },
    { value: '201-1000', label: '201-1000 funcionários' },
    { value: '1000+', label: 'Mais de 1000 funcionários' }
  ];

  // Validação em tempo real
  useEffect(() => {
    const errors: ValidationErrors = {};
    
    // Validar nome da empresa
    if (!companyName.trim()) {
      errors.companyName = 'Nome da empresa é obrigatório';
    } else if (companyName.trim().length < 2) {
      errors.companyName = 'Nome deve ter pelo menos 2 caracteres';
    }
    
    // Validar indústria
    if (!industry) {
      errors.industry = 'Selecione uma indústria';
    }
    
    // Validar tamanho
    if (!size) {
      errors.size = 'Selecione o tamanho da empresa';
    }
    
    // Validar website (opcional, mas se preenchido deve ser válido)
    if (website.trim() && !isValidUrl(website)) {
      errors.website = 'Website deve ter um formato válido';
    }
    
    setValidationErrors(errors);
    setIsValid(Object.keys(errors).length === 0 && companyName.trim() && industry && size);
  }, [companyName, industry, size, website]);

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url.startsWith('http') ? url : `https://${url}`);
      return true;
    } catch {
      return false;
    }
  };

  const handleNext = () => {
    if (isValid) {
      updateData({
        company: {
          name: companyName.trim(),
          industry,
          size,
          website: website.trim(),
          country: 'Brasil' // Default para o contexto brasileiro
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
          className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto"
        >
          <Building className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.h2
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-gray-900"
        >
          Sobre sua empresa
        </motion.h2>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 max-w-md mx-auto"
        >
          Conte-nos sobre sua empresa para personalizarmos as recomendações de palavras-chave.
        </motion.p>
      </div>

      {/* Formulário */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="space-y-4"
      >
        {/* Nome da Empresa */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nome da Empresa
          </label>
          <div className="relative">
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              onKeyPress={handleKeyPress}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                validationErrors.companyName 
                  ? 'border-red-300 bg-red-50' 
                  : companyName.trim() 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
              placeholder="Digite o nome da sua empresa"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Building className={`w-5 h-5 ${
                validationErrors.companyName 
                  ? 'text-red-400' 
                  : companyName.trim() 
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {companyName.trim() && !validationErrors.companyName && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
          </div>
          {validationErrors.companyName && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.companyName}
            </motion.p>
          )}
        </div>

        {/* Indústria */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Setor/Indústria
          </label>
          <div className="relative">
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors appearance-none ${
                validationErrors.industry 
                  ? 'border-red-300 bg-red-50' 
                  : industry 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
            >
              <option value="">Selecione uma indústria</option>
              {industryOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Globe className={`w-5 h-5 ${
                validationErrors.industry 
                  ? 'text-red-400' 
                  : industry 
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {industry && !validationErrors.industry && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          {validationErrors.industry && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.industry}
            </motion.p>
          )}
        </div>

        {/* Tamanho da Empresa */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tamanho da Empresa
          </label>
          <div className="relative">
            <select
              value={size}
              onChange={(e) => setSize(e.target.value)}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors appearance-none ${
                validationErrors.size 
                  ? 'border-red-300 bg-red-50' 
                  : size 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
            >
              <option value="">Selecione o tamanho</option>
              {sizeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Users className={`w-5 h-5 ${
                validationErrors.size 
                  ? 'text-red-400' 
                  : size 
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {size && !validationErrors.size && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
          {validationErrors.size && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.size}
            </motion.p>
          )}
        </div>

        {/* Website (Opcional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Website da Empresa <span className="text-gray-500">(opcional)</span>
          </label>
          <div className="relative">
            <input
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              onKeyPress={handleKeyPress}
              className={`w-full px-4 py-3 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                validationErrors.website 
                  ? 'border-red-300 bg-red-50' 
                  : website.trim() && isValidUrl(website)
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300'
              }`}
              placeholder="exemplo.com"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Globe className={`w-5 h-5 ${
                validationErrors.website 
                  ? 'text-red-400' 
                  : website.trim() && isValidUrl(website)
                    ? 'text-green-500' 
                    : 'text-gray-400'
              }`} />
            </div>
            {website.trim() && isValidUrl(website) && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            )}
          </div>
          {validationErrors.website && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-1 text-sm text-red-600 flex items-center"
            >
              <AlertCircle className="w-4 h-4 mr-1" />
              {validationErrors.website}
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
            'Preencha os campos obrigatórios'
          )}
        </button>
      </motion.div>

      {/* Dicas */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="bg-green-50 border border-green-200 rounded-lg p-4"
      >
        <h4 className="text-sm font-medium text-green-900 mb-2">
          💡 Dica rápida
        </h4>
        <p className="text-sm text-green-700">
          Essas informações nos ajudam a sugerir palavras-chave mais relevantes para o seu setor e tamanho de empresa.
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
        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
      </motion.div>
    </motion.div>
  );
};

export default CompanyStep; 