import React from 'react';
import Skeleton from '../shared/Skeleton_v1';

// Tipos básicos
export interface Prompt {
  id: string;
  nome: string;
}
export interface Categoria {
  id: string;
  nome: string;
  prompts: Prompt[];
}
export interface Nicho {
  id: string;
  nome: string;
  categorias: Categoria[];
}

interface NichoTreeProps {
  nichos: Nicho[];
  onSelectNicho: (id: string) => void;
  onSelectCategoria: (id: string) => void;
  onSelectPrompt: (id: string) => void;
  selectedNichoId?: string;
  selectedCategoriaId?: string;
  selectedPromptId?: string;
  renderSkeleton?: boolean;
}

const NichoTree: React.FC<NichoTreeProps> = ({ nichos, onSelectNicho, onSelectCategoria, onSelectPrompt, selectedNichoId, selectedCategoriaId, selectedPromptId, renderSkeleton }) => (
  <nav aria-label="Navegação de nichos" style={{ width: 280, borderRight: '1px solid #eee', padding: 16, overflowY: 'auto', height: '100%' }}>
    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
      {renderSkeleton ? (
        <>
          {[1,2,3].map(i => (
            <li key={i} style={{ marginBottom: 12 }}>
              <Skeleton width={180} height={20} style={{ marginBottom: 8 }} />
              <ul style={{ listStyle: 'none', paddingLeft: 16 }}>
                {[1,2].map(j => (
                  <li key={j}>
                    <Skeleton width={140} height={16} style={{ marginBottom: 6 }} />
                    <ul style={{ listStyle: 'none', paddingLeft: 16 }}>
                      {[1,2].map(k => (
                        <li key={k}>
                          <Skeleton width={100} height={14} style={{ marginBottom: 4 }} />
                        </li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </>
      ) : (
        nichos.map((nicho) => (
          <li key={nicho.id}>
            <button style={{ fontWeight: nicho.id === selectedNichoId ? 700 : 400, background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'left', padding: 8 }} onClick={() => onSelectNicho(nicho.id)} aria-label={`Selecionar nicho ${nicho.nome}`}>{nicho.nome}</button>
            {nicho.id === selectedNichoId && (
              <ul style={{ listStyle: 'none', paddingLeft: 16 }}>
                {nicho.categorias.map((cat) => (
                  <li key={cat.id}>
                    <button style={{ fontWeight: cat.id === selectedCategoriaId ? 700 : 400, background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'left', padding: 6 }} onClick={() => onSelectCategoria(cat.id)} aria-label={`Selecionar categoria ${cat.nome}`}>{cat.nome}</button>
                    {cat.id === selectedCategoriaId && (
                      <ul style={{ listStyle: 'none', paddingLeft: 16 }}>
                        {cat.prompts.map((prompt) => (
                          <li key={prompt.id}>
                            <button style={{ fontWeight: prompt.id === selectedPromptId ? 700 : 400, background: 'none', border: 'none', cursor: 'pointer', width: '100%', textAlign: 'left', padding: 4 }} onClick={() => onSelectPrompt(prompt.id)} aria-label={`Selecionar prompt ${prompt.nome}`}>{prompt.nome}</button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))
      )}
    </ul>
  </nav>
);

export default NichoTree; 