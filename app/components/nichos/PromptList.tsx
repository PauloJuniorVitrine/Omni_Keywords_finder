import React, { useState } from 'react';
import Skeleton from '../shared/Skeleton_v1';

export interface Prompt {
  id: string;
  nome: string;
  conteudo?: string;
}

interface PromptListProps {
  prompts: Prompt[];
  onRemove: (promptId: string) => void;
  renderSkeleton?: boolean;
}

const PromptList: React.FC<PromptListProps> = ({ prompts, onRemove, renderSkeleton }) => {
  const [previewId, setPreviewId] = useState<string | null>(null);

  if (renderSkeleton) {
    return (
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {[1,2,3,4].map(i => (
          <li key={i} style={{ marginBottom: 8 }}>
            <Skeleton width={180} height={18} />
          </li>
        ))}
      </ul>
    );
  }

  return (
    <ul style={{ listStyle: 'none', padding: 0 }}>
      {prompts.map((prompt) => (
        <li key={prompt.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ flex: 1 }}>{prompt.nome}</span>
          <button onClick={() => onRemove(prompt.id)} aria-label={`Remover prompt ${prompt.nome}`}>Remover</button>
        </li>
      ))}
    </ul>
  );
};

export default PromptList; 