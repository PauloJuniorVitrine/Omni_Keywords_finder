import React, { useState, useRef, useEffect } from 'react';

/**
 * Barra de busca global com autocomplete e debounce.
 * @param placeholder Placeholder do input
 * @param onSearch Função chamada ao buscar (debounced)
 * @param suggestions Sugestões para autocomplete
 * @param ariaLabel Label acessível
 * @param minLength Mínimo de caracteres para buscar
 * @param debounceMs Delay do debounce em ms
 */
export interface GlobalSearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  suggestions?: string[];
  ariaLabel?: string;
  minLength?: number;
  debounceMs?: number;
}

const GlobalSearchBar: React.FC<GlobalSearchBarProps> = ({
  placeholder = 'Buscar...',
  onSearch,
  suggestions = [],
  ariaLabel = 'Busca global',
  minLength = 2,
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filtered, setFiltered] = useState<string[]>([]);
  const [highlight, setHighlight] = useState(-1);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (query.length < minLength) {
      setFiltered([]);
      setShowSuggestions(false);
      return;
    }
    setFiltered(suggestions.filter(s => s.toLowerCase().includes(query.toLowerCase())));
    setShowSuggestions(true);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => onSearch(query), debounceMs);
    // eslint-disable-next-line
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || filtered.length === 0) return;
    if (e.key === 'ArrowDown') {
      setHighlight(h => Math.min(h + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      setHighlight(h => Math.max(h - 1, 0));
    } else if (e.key === 'Enter' && highlight >= 0) {
      setQuery(filtered[highlight]);
      setShowSuggestions(false);
      onSearch(filtered[highlight]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: 320, maxWidth: '100%' }}>
      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={e => { setQuery(e.target.value); setHighlight(-1); }}
        onFocus={() => setShowSuggestions(query.length >= minLength && filtered.length > 0)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 120)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        aria-label={ariaLabel}
        style={{ width: '100%', padding: '10px 16px', borderRadius: 8, border: '1px solid #d1d5db', fontSize: 16, outline: 'none', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}
        autoComplete="off"
      />
      {showSuggestions && filtered.length > 0 && (
        <ul style={{ position: 'absolute', top: 44, left: 0, right: 0, background: '#fff', border: '1px solid #eee', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', zIndex: 10, margin: 0, padding: 0, listStyle: 'none', maxHeight: 180, overflowY: 'auto' }} role="listbox">
          {filtered.map((s, i) => (
            <li
              key={s}
              role="option"
              aria-selected={highlight === i}
              onMouseDown={() => { setQuery(s); setShowSuggestions(false); onSearch(s); }}
              style={{ padding: '10px 16px', background: highlight === i ? '#f3f4f6' : '#fff', cursor: 'pointer', fontWeight: highlight === i ? 600 : 400 }}
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default GlobalSearchBar; 