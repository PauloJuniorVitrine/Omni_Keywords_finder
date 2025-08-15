/**
 * ProgressIndicator.tsx
 * 
 * Sistema de indicadores de progresso para Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_CHECKLIST_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 9.2
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect } from 'react';
import { cn } from '../../utils/cn';

// Types
export type ProgressType = 'linear' | 'circular' | 'dots' | 'spinner' | 'steps';
export type ProgressStatus = 'idle' | 'loading' | 'success' | 'error' | 'warning' | 'paused';

export interface ProgressIndicatorProps {
  type?: ProgressType;
  status?: ProgressStatus;
  progress?: number; // 0-100
  total?: number;
  current?: number;
  label?: string;
  description?: string;
  showPercentage?: boolean;
  showLabel?: boolean;
  showDescription?: boolean;
  animated?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  onCancel?: () => void;
  onRetry?: () => void;
  onPause?: () => void;
  onResume?: () => void;
}

export interface StepProgressProps {
  steps: Array<{
    id: string;
    label: string;
    status: 'pending' | 'active' | 'completed' | 'error';
    description?: string;
  }>;
  currentStep?: number;
  className?: string;
  onStepClick?: (stepIndex: number) => void;
}

// Linear Progress Bar
const LinearProgress: React.FC<ProgressIndicatorProps> = ({
  progress = 0,
  status = 'loading',
  size = 'md',
  showPercentage = true,
  className = '',
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'paused':
        return 'bg-gray-400';
      default:
        return 'bg-blue-500';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-1';
      case 'lg':
        return 'h-3';
      case 'xl':
        return 'h-4';
      default:
        return 'h-2';
    }
  };

  return (
    <div className={cn('w-full', className)}>
      <div className={cn('bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden', getSizeClasses())}>
        <div
          className={cn(
            'transition-all duration-300 ease-out',
            getStatusColor(),
            getSizeClasses()
          )}
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>
      {showPercentage && (
        <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

// Circular Progress
const CircularProgress: React.FC<ProgressIndicatorProps> = ({
  progress = 0,
  status = 'loading',
  size = 'md',
  showPercentage = true,
  className = '',
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-8 h-8';
      case 'lg':
        return 'w-16 h-16';
      case 'xl':
        return 'w-24 h-24';
      default:
        return 'w-12 h-12';
    }
  };

  const getStrokeWidth = () => {
    switch (size) {
      case 'sm':
        return 2;
      case 'lg':
        return 4;
      case 'xl':
        return 6;
      default:
        return 3;
    }
  };

  const radius = size === 'sm' ? 14 : size === 'lg' ? 28 : size === 'xl' ? 42 : 21;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg className={cn('transform -rotate-90', getSizeClasses())}>
        <circle
          cx="50%"
          cy="50%"
          r={radius}
          stroke="currentColor"
          strokeWidth={getStrokeWidth()}
          fill="transparent"
          className="text-gray-200 dark:text-gray-700"
        />
        <circle
          cx="50%"
          cy="50%"
          r={radius}
          stroke="currentColor"
          strokeWidth={getStrokeWidth()}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          className="text-blue-500 transition-all duration-300 ease-out"
          strokeLinecap="round"
        />
      </svg>
      {showPercentage && (
        <div className="absolute text-sm font-medium text-gray-900 dark:text-white">
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

// Dots Progress
const DotsProgress: React.FC<ProgressIndicatorProps> = ({
  status = 'loading',
  size = 'md',
  className = '',
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-1 h-1';
      case 'lg':
        return 'w-3 h-3';
      case 'xl':
        return 'w-4 h-4';
      default:
        return 'w-2 h-2';
    }
  };

  return (
    <div className={cn('flex space-x-1', className)}>
      {[0, 1, 2].map((index) => (
        <div
          key={index}
          className={cn(
            'bg-gray-400 dark:bg-gray-600 rounded-full animate-pulse',
            getSizeClasses()
          )}
          style={{
            animationDelay: `${index * 0.2}s`,
            animationDuration: '1s',
          }}
        />
      ))}
    </div>
  );
};

// Spinner Progress
const SpinnerProgress: React.FC<ProgressIndicatorProps> = ({
  status = 'loading',
  size = 'md',
  className = '',
}) => {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'lg':
        return 'w-8 h-8';
      case 'xl':
        return 'w-12 h-12';
      default:
        return 'w-6 h-6';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <div className={cn('text-green-500 text-center', getSizeClasses())}>✓</div>;
      case 'error':
        return <div className={cn('text-red-500 text-center', getSizeClasses())}>✗</div>;
      case 'warning':
        return <div className={cn('text-yellow-500 text-center', getSizeClasses())}>⚠</div>;
      case 'paused':
        return <div className={cn('text-gray-500 text-center', getSizeClasses())}>⏸</div>;
      default:
        return <div className={cn('text-blue-500 animate-spin text-center', getSizeClasses())}>⟳</div>;
    }
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      {getStatusIcon()}
    </div>
  );
};

// Steps Progress
const StepsProgress: React.FC<StepProgressProps> = ({
  steps,
  currentStep = 0,
  className = '',
  onStepClick,
}) => {
  return (
    <div className={cn('space-y-4', className)}>
      {steps.map((step, index) => (
        <div
          key={step.id}
          className={cn(
            'flex items-center space-x-3 p-3 rounded-lg border transition-colors',
            step.status === 'completed' && 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700',
            step.status === 'active' && 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700',
            step.status === 'error' && 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700',
            step.status === 'pending' && 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700',
            onStepClick && 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700'
          )}
          onClick={() => onStepClick?.(index)}
        >
          <div className="flex-shrink-0">
            {step.status === 'completed' && (
              <div className="w-5 h-5 text-green-500 text-center">✓</div>
            )}
            {step.status === 'active' && (
              <div className="w-5 h-5 bg-blue-500 rounded-full animate-pulse" />
            )}
            {step.status === 'error' && (
              <div className="w-5 h-5 text-red-500 text-center">✗</div>
            )}
            {step.status === 'pending' && (
              <div className="w-5 h-5 bg-gray-300 dark:bg-gray-600 rounded-full" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {step.label}
            </div>
            {step.description && (
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {step.description}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

// Main Progress Indicator Component
export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  type = 'linear',
  status = 'loading',
  progress = 0,
  total,
  current,
  label,
  description,
  showPercentage = true,
  showLabel = true,
  showDescription = true,
  animated = true,
  size = 'md',
  className = '',
  onCancel,
  onRetry,
  onPause,
  onResume,
}) => {
  // Calculate progress from current/total if provided
  const calculatedProgress = total && current !== undefined 
    ? (current / total) * 100 
    : progress;

  const renderProgress = () => {
    switch (type) {
      case 'circular':
        return (
          <CircularProgress
            progress={calculatedProgress}
            status={status}
            size={size}
            showPercentage={showPercentage}
            className={className}
          />
        );
      case 'dots':
        return (
          <DotsProgress
            status={status}
            size={size}
            className={className}
          />
        );
      case 'spinner':
        return (
          <SpinnerProgress
            status={status}
            size={size}
            className={className}
          />
        );
      default:
        return (
          <LinearProgress
            progress={calculatedProgress}
            status={status}
            size={size}
            showPercentage={showPercentage}
            className={className}
          />
        );
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'success':
        return 'Concluído';
      case 'error':
        return 'Erro';
      case 'warning':
        return 'Atenção';
      case 'paused':
        return 'Pausado';
      case 'idle':
        return 'Aguardando';
      default:
        return 'Processando...';
    }
  };

  return (
    <div className="space-y-3">
      {/* Label and Description */}
      {(showLabel || showDescription) && (
        <div className="space-y-1">
          {showLabel && label && (
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {label}
            </div>
          )}
          {showDescription && description && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {description}
            </div>
          )}
        </div>
      )}

      {/* Progress Component */}
      <div className="flex items-center space-x-3">
        {renderProgress()}
        
        {/* Status Text */}
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {getStatusText()}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-2">
        {status === 'loading' && onPause && (
          <button
            onClick={onPause}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Pausar"
          >
            <span className="w-4 h-4 text-center">⏸</span>
          </button>
        )}
        
        {status === 'paused' && onResume && (
          <button
            onClick={onResume}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Retomar"
          >
            <span className="w-4 h-4 text-center">▶</span>
          </button>
        )}
        
        {status === 'error' && onRetry && (
          <button
            onClick={onRetry}
            className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            title="Tentar novamente"
          >
            <span className="w-4 h-4 text-center">⟳</span>
          </button>
        )}
        
        {(status === 'loading' || status === 'paused') && onCancel && (
          <button
            onClick={onCancel}
            className="p-1 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400"
            title="Cancelar"
          >
            <span className="w-4 h-4 text-center">✗</span>
          </button>
        )}
      </div>
    </div>
  );
};

// Export Steps Progress as separate component
export { StepsProgress };

// Hooks
export const useProgress = (initialProgress = 0) => {
  const [progress, setProgress] = useState(initialProgress);
  const [status, setStatus] = useState<ProgressStatus>('idle');

  const start = () => setStatus('loading');
  const complete = () => {
    setProgress(100);
    setStatus('success');
  };
  const error = () => setStatus('error');
  const pause = () => setStatus('paused');
  const resume = () => setStatus('loading');
  const reset = () => {
    setProgress(0);
    setStatus('idle');
  };

  return {
    progress,
    setProgress,
    status,
    setStatus,
    start,
    complete,
    error,
    pause,
    resume,
    reset,
  };
};

export default ProgressIndicator; 