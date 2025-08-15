import React, { createContext, useContext, ReactNode } from 'react';

// Definição dos flags disponíveis
export type FeatureFlags = {
  exportCsv: boolean;
  adminCrud: boolean;
  simulateFailures: boolean;
  darkMode: boolean;
};

const defaultFlags: FeatureFlags = {
  exportCsv: true,
  adminCrud: false,
  simulateFailures: false,
  darkMode: false,
};

const FeatureFlagContext = createContext<FeatureFlags>(defaultFlags);

export const FeatureFlagProvider = ({ children, flags }: { children: ReactNode; flags?: Partial<FeatureFlags> }) => {
  const mergedFlags = { ...defaultFlags, ...flags };
  return <FeatureFlagContext.Provider value={mergedFlags}>{children}</FeatureFlagContext.Provider>;
};

export const useFeatureFlags = () => useContext(FeatureFlagContext);

// Fallback visual para recursos desativados
export const FeatureFlagFallback: React.FC<{ flag: keyof FeatureFlags; children: ReactNode }> = ({ flag, children }) => {
  const flags = useFeatureFlags();
  if (!flags[flag]) {
    return <span style={{ color: '#888', fontStyle: 'italic' }}>Recurso indisponível (flag: {flag})</span>;
  }
  return <>{children}</>;
}; 