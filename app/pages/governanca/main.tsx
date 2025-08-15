import React from 'react';
import ReactDOM from 'react-dom/client';
import GovernancaPage from './index';

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <GovernancaPage />
    </React.StrictMode>
  );
} 