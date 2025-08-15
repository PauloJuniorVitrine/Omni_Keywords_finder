import React from 'react';
import ThemeToggle from './ThemeToggle_v1';

const Header: React.FC = () => (
  <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 32px', background: 'var(--header-bg, #fff)', borderBottom: '1px solid #e5e7eb' }}>
    <div>
      {/* ...logo, navegação, etc... */}
    </div>
    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
      {/* ...outros botões/menus... */}
      <ThemeToggle />
    </div>
  </header>
);

export default Header; 