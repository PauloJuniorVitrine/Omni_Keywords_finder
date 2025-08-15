import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Integração Plausible Analytics
if (typeof window !== 'undefined' && !document.getElementById('plausible-script')) {
  const script = document.createElement('script');
  script.id = 'plausible-script';
  script.setAttribute('defer', 'true');
  script.setAttribute('data-domain', 'SEU_DOMINIO_AQUI'); // Substitua pelo domínio real
  script.src = 'https://plausible.io/js/plausible.js';
  document.head.appendChild(script);
} 