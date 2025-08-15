import React, { useState } from 'react';

export interface ExpandableCardProps {
  title: string;
  summary?: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  className?: string;
}

export const ExpandableCard: React.FC<ExpandableCardProps> = ({ title, summary, children, defaultExpanded = false, className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={`expandable-card ${className}`} style={{ border: '1px solid #ccc', borderRadius: 8, margin: '8px 0' }}>
      <div onClick={() => setIsExpanded(!isExpanded)} style={{ padding: '16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3>{title}</h3>
          {summary && <p>{summary}</p>}
        </div>
        <span>{isExpanded ? '−' : '+'}</span>
      </div>
      {isExpanded && <div className="expandable-content" style={{ padding: '0 16px 16px' }}>{children}</div>}
    </div>
  );
}; 