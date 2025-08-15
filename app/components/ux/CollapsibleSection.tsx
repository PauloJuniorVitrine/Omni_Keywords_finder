import React, { useState } from 'react';

export interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({ title, children, defaultOpen = false, className = '' }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`collapsible-section ${className}`}>
      <button onClick={() => setIsOpen(!isOpen)} style={{ width: '100%', textAlign: 'left', padding: '8px', border: 'none', background: 'none', cursor: 'pointer' }}>
        <span>{isOpen ? '▼' : '▶'}</span> {title}
      </button>
      {isOpen && <div className="collapsible-content" style={{ padding: '8px' }}>{children}</div>}
    </div>
  );
}; 