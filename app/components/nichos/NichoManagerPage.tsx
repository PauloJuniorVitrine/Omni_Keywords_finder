import React, { useState, useEffect } from 'react';
import NichoTree, { Nicho, Categoria, Prompt } from './NichoTree';
import NichoForm from './NichoForm';
import CategoriaForm from './CategoriaForm';
import PromptUpload from './PromptUpload';
import PromptList from './PromptList';
import ExecucaoAutomaticaButton from './ExecucaoAutomaticaButton';
import ResultadosPainel from './ResultadosPainel';
import Tooltip from '../shared/Tooltip_v1';
import ExportButton from '../shared/ExportButton';
import Toast from '../shared/Toast';

// Placeholder de dados iniciais
const nichosExemplo: Nicho[] = [
  {
    id: 'n1', nome: 'Saúde', categorias: [
      { id: 'c1', nome: 'Emagrecimento', prompts: [ { id: 'p1', nome: 'Prompt1.txt' } ] },
      { id: 'c2', nome: 'Bem-estar', prompts: [] },
    ]
  },
  {
    id: 'n2', nome: 'Finanças', categorias: [
      { id: 'c3', nome: 'Investimentos', prompts: [] }
    ]
  }
];

const NichoManagerPage: React.FC = () => {
  const [nichos, setNichos] = useState<Nicho[]>([]);
  const [selectedNichoId, setSelectedNichoId] = useState<string | undefined>();
  const [selectedCategoriaId, setSelectedCategoriaId] = useState<string | undefined>();
  const [selectedPromptId, setSelectedPromptId] = useState<string | undefined>();

  // Modais
  const [showNichoForm, setShowNichoForm] = useState(false);
  const [showCategoriaForm, setShowCategoriaForm] = useState(false);

  // Execução
  const [executando, setExecutando] = useState(false);
  const [resultados, setResultados] = useState<any[]>([]); // Ajustar tipagem após integração

  // Fetch inicial
  const [loadingNichos, setLoadingNichos] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const fetchNichos = async () => {
      setLoadingNichos(true);
      try {
        const resp = await fetch('/api/nichos');
        if (!resp.ok) throw new Error('Erro ao buscar nichos');
        const data = await resp.json();
        setNichos(data);
      } catch (err) {
        setToast({ type: 'error', message: 'Erro ao carregar nichos: ' + (err as Error).message });
      } finally {
        setLoadingNichos(false);
      }
    };
    fetchNichos();
  }, []);

  // Handlers de seleção
  const handleSelectNicho = (id: string) => {
    setSelectedNichoId(id);
    setSelectedCategoriaId(undefined);
    setSelectedPromptId(undefined);
  };
  const handleSelectCategoria = (id: string) => {
    setSelectedCategoriaId(id);
    setSelectedPromptId(undefined);
  };
  const handleSelectPrompt = (id: string) => setSelectedPromptId(id);

  // Handlers de cadastro
  const handleAddNicho = async (nome: string) => {
    setShowNichoForm(false);
    try {
      const resp = await fetch('/api/nichos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });
      if (!resp.ok) throw new Error('Erro ao criar nicho');
      const novoNicho = await resp.json();
      setNichos((prev) => [...prev, { ...novoNicho, categorias: [] }]);
      setToast({ type: 'success', message: 'Nicho criado com sucesso!' });
    } catch (err) {
      setToast({ type: 'error', message: 'Erro ao criar nicho: ' + (err as Error).message });
    }
  };
  const handleAddCategoria = async (nome: string) => {
    setShowCategoriaForm(false);
    if (!selectedNichoId) return;
    try {
      const resp = await fetch(`/api/categorias`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, nicho_id: selectedNichoId }),
      });
      if (!resp.ok) throw new Error('Erro ao criar categoria');
      const novaCategoria = await resp.json();
      setNichos((prev) =>
        prev.map((nicho) =>
          nicho.id === selectedNichoId
            ? { ...nicho, categorias: [...nicho.categorias, { ...novaCategoria, prompts: [] }] }
            : nicho
        )
      );
      setToast({ type: 'success', message: 'Categoria criada com sucesso!' });
    } catch (err) {
      setToast({ type: 'error', message: 'Erro ao criar categoria: ' + (err as Error).message });
    }
  };
  const handleUploadPrompts = async (files: FileList) => {
    if (!selectedCategoriaId) return;
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('files', file));
    try {
      const resp = await fetch(`/api/prompts?categoria_id=${selectedCategoriaId}`, {
        method: 'POST',
        body: formData,
      });
      if (!resp.ok) throw new Error('Erro ao fazer upload');
      const novosPrompts = await resp.json();
      setNichos((prev) =>
        prev.map((nicho) => ({
          ...nicho,
          categorias: nicho.categorias.map((cat) =>
            cat.id === selectedCategoriaId
              ? { ...cat, prompts: [...cat.prompts, ...novosPrompts] }
              : cat
          ),
        }))
      );
      setToast({ type: 'success', message: 'Prompts enviados com sucesso!' });
    } catch (err) {
      setToast({ type: 'error', message: 'Erro ao fazer upload: ' + (err as Error).message });
    }
  };
  const handleRemovePrompt = async (promptId: string) => {
    if (!selectedCategoriaId) return;
    try {
      const resp = await fetch(`/api/prompts/${promptId}`, { method: 'DELETE' });
      if (!resp.ok) throw new Error('Erro ao remover prompt');
      setNichos((prev) =>
        prev.map((nicho) => ({
          ...nicho,
          categorias: nicho.categorias.map((cat) =>
            cat.id === selectedCategoriaId
              ? { ...cat, prompts: cat.prompts.filter((p) => p.id !== promptId) }
              : cat
          ),
        }))
      );
      setToast({ type: 'success', message: 'Prompt removido com sucesso!' });
    } catch (err) {
      setToast({ type: 'error', message: 'Erro ao remover prompt: ' + (err as Error).message });
    }
  };

  // Execução automática
  const handleExecutar = async () => {
    setExecutando(true);
    try {
      const resp = await fetch('/api/execucao/busca_automatica', { method: 'POST' });
      if (!resp.ok) throw new Error('Erro ao iniciar execução');
      setToast({ type: 'success', message: 'Execução iniciada!' });
      setTimeout(() => setExecutando(false), 2000);
    } catch (err) {
      setExecutando(false);
      setToast({ type: 'error', message: 'Erro ao iniciar execução: ' + (err as Error).message });
    }
  };

  // Exportação de resultados
  const handleExport = (format: 'csv' | 'json') => {
    setExportLoading(true);
    setTimeout(() => {
      setExportLoading(false);
      setToast({ type: 'success', message: `Exportação ${format.toUpperCase()} concluída com sucesso!` });
    }, 1500);
  };

  // Dados selecionados
  const nichoSel = nichos.find(n => n.id === selectedNichoId);
  const categoriaSel = nichoSel?.categorias.find(c => c.id === selectedCategoriaId);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <NichoTree
        nichos={loadingNichos ? [{ id: 'skeleton', nome: '', categorias: [{ id: 'skeleton-cat', nome: '', prompts: [{ id: 'skeleton-p', nome: '' }] }] }] : nichos}
        onSelectNicho={handleSelectNicho}
        onSelectCategoria={handleSelectCategoria}
        onSelectPrompt={handleSelectPrompt}
        selectedNichoId={selectedNichoId}
        selectedCategoriaId={selectedCategoriaId}
        selectedPromptId={selectedPromptId}
        renderSkeleton={loadingNichos}
      />
      <main style={{ flex: 1, padding: 32, overflowY: 'auto' }}>
        <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
          <Tooltip content="Criar um novo nicho">
            <button onClick={() => setShowNichoForm(true)} title="Criar um novo nicho">+ Novo Nicho</button>
          </Tooltip>
          {selectedNichoId && (
            <Tooltip content="Criar uma nova categoria">
              <button onClick={() => setShowCategoriaForm(true)} title="Criar uma nova categoria">+ Nova Categoria</button>
            </Tooltip>
          )}
        </div>
        {showNichoForm && <NichoForm onSubmit={handleAddNicho} onCancel={() => setShowNichoForm(false)} />}
        {showCategoriaForm && <CategoriaForm onSubmit={handleAddCategoria} onCancel={() => setShowCategoriaForm(false)} />}
        {categoriaSel && (
          <>
            <h3>Prompts da Categoria: {categoriaSel.nome}</h3>
            <PromptUpload onUpload={handleUploadPrompts} />
            <PromptList prompts={categoriaSel.prompts} onRemove={handleRemovePrompt} renderSkeleton={loadingNichos} />
          </>
        )}
        <Tooltip content="Executar busca automática de palavras-chave">
          <ExecucaoAutomaticaButton onClick={handleExecutar} loading={executando} disabled={executando} />
        </Tooltip>
        <Tooltip content="Exportar resultados em CSV" position="top">
          <ExportButton format="csv" onExport={() => handleExport('csv')} loading={exportLoading} disabled={exportLoading || !resultados.length} />
        </Tooltip>
        <Tooltip content="Exportar resultados em JSON" position="top">
          <ExportButton format="json" onExport={() => handleExport('json')} loading={exportLoading} disabled={exportLoading || !resultados.length} />
        </Tooltip>
        <Tooltip content="Exportar resultados do nicho">
          <ResultadosPainel resultados={resultados} nichoNome={nichoSel?.nome || ''} onExport={handleExport} />
        </Tooltip>
      </main>
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}
    </div>
  );
};

export default NichoManagerPage; 