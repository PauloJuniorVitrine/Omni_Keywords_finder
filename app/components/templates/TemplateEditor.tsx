/**
 * TemplateEditor.tsx
 * 
 * Editor avançado de templates com syntax highlighting e validação
 * 
 * Tracing ID: UI_TEMPLATE_EDITOR_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 12.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { 
  Save, 
  Eye, 
  Code, 
  Settings, 
  Play, 
  Download, 
  Upload,
  Copy,
  Undo,
  Redo,
  Search,
  Replace,
  Zap,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { useTemplates } from '@/hooks/useTemplates';
import { useNotifications } from '@/hooks/useNotifications';
import { usePermissions } from '@/hooks/usePermissions';

interface Template {
  id?: string;
  name: string;
  description: string;
  category: string;
  content: string;
  variables: string[];
  version: string;
  status: 'active' | 'draft' | 'archived';
  tags: string[];
  isPublic: boolean;
  metadata?: Record<string, any>;
}

interface TemplateEditorProps {
  template?: Template;
  onSave?: (template: Template) => void;
  onCancel?: () => void;
  className?: string;
}

interface ValidationError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

interface Variable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  defaultValue?: any;
  description?: string;
}

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  template,
  onSave,
  onCancel,
  className = ''
}) => {
  const [formData, setFormData] = useState<Template>({
    name: template?.name || '',
    description: template?.description || '',
    category: template?.category || 'blog-posts',
    content: template?.content || '',
    variables: template?.variables || [],
    version: template?.version || '1.0.0',
    status: template?.status || 'draft',
    tags: template?.tags || [],
    isPublic: template?.isPublic || false,
    metadata: template?.metadata || {}
  });

  const [activeTab, setActiveTab] = useState('editor');
  const [searchTerm, setSearchTerm] = useState('');
  const [replaceTerm, setReplaceTerm] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [previewData, setPreviewData] = useState<Record<string, any>>({});
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [undoStack, setUndoStack] = useState<string[]>([]);
  const [redoStack, setRedoStack] = useState<string[]>([]);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });

  const { createTemplate, updateTemplate } = useTemplates();
  const { showNotification } = useNotifications();
  const { hasPermission } = usePermissions();

  // Categorias disponíveis
  const categories = [
    'blog-posts',
    'social-media',
    'email-marketing',
    'seo-content',
    'product-descriptions',
    'landing-pages',
    'newsletters',
    'prompts',
    'custom'
  ];

  // Variáveis detectadas automaticamente
  const detectedVariables = useCallback((content: string): string[] => {
    const variableRegex = /\{\{([^}]+)\}\}/g;
    const variables = new Set<string>();
    let match;

    while ((match = variableRegex.exec(content)) !== null) {
      const variableName = match[1].trim();
      if (variableName && !variableName.includes(' ')) {
        variables.add(variableName);
      }
    }

    return Array.from(variables);
  }, []);

  // Validação de sintaxe
  const validateTemplate = useCallback((content: string): ValidationError[] => {
    const errors: ValidationError[] = [];
    const lines = content.split('\n');

    lines.forEach((line, index) => {
      const lineNumber = index + 1;

      // Verificar variáveis não fechadas
      const openBraces = (line.match(/\{\{/g) || []).length;
      const closeBraces = (line.match(/\}\}/g) || []).length;
      
      if (openBraces > closeBraces) {
        errors.push({
          line: lineNumber,
          column: line.length + 1,
          message: 'Variável não fechada',
          severity: 'error'
        });
      }

      // Verificar variáveis vazias
      const emptyVariables = line.match(/\{\{\s*\}\}/g);
      if (emptyVariables) {
        errors.push({
          line: lineNumber,
          column: line.indexOf('{{') + 1,
          message: 'Variável vazia',
          severity: 'warning'
        });
      }

      // Verificar variáveis com espaços
      const invalidVariables = line.match(/\{\{[^}]*\s+[^}]*\}\}/g);
      if (invalidVariables) {
        errors.push({
          line: lineNumber,
          column: line.indexOf('{{') + 1,
          message: 'Variável contém espaços inválidos',
          severity: 'error'
        });
      }
    });

    return errors;
  }, []);

  // Atualizar variáveis detectadas
  useEffect(() => {
    const variables = detectedVariables(formData.content);
    setFormData(prev => ({
      ...prev,
      variables: variables
    }));
  }, [formData.content, detectedVariables]);

  // Validar template
  useEffect(() => {
    const errors = validateTemplate(formData.content);
    setValidationErrors(errors);
  }, [formData.content, validateTemplate]);

  // Handlers
  const handleContentChange = (content: string) => {
    // Salvar estado para undo/redo
    setUndoStack(prev => [...prev, formData.content]);
    setRedoStack([]);

    setFormData(prev => ({
      ...prev,
      content
    }));
  };

  const handleUndo = () => {
    if (undoStack.length > 0) {
      const previousContent = undoStack[undoStack.length - 1];
      setRedoStack(prev => [...prev, formData.content]);
      setUndoStack(prev => prev.slice(0, -1));
      
      setFormData(prev => ({
        ...prev,
        content: previousContent
      }));
    }
  };

  const handleRedo = () => {
    if (redoStack.length > 0) {
      const nextContent = redoStack[redoStack.length - 1];
      setUndoStack(prev => [...prev, formData.content]);
      setRedoStack(prev => prev.slice(0, -1));
      
      setFormData(prev => ({
        ...prev,
        content: nextContent
      }));
    }
  };

  const handleSearch = () => {
    if (!searchTerm) return;
    
    const content = formData.content;
    const index = content.toLowerCase().indexOf(searchTerm.toLowerCase());
    
    if (index !== -1) {
      const lines = content.substring(0, index).split('\n');
      const line = lines.length;
      const column = lines[lines.length - 1].length + 1;
      
      setCursorPosition({ line, column });
      // Aqui você implementaria o foco no editor
    }
  };

  const handleReplace = () => {
    if (!searchTerm || !replaceTerm) return;
    
    const newContent = formData.content.replace(
      new RegExp(searchTerm, 'gi'),
      replaceTerm
    );
    
    handleContentChange(newContent);
    showNotification('success', 'Substituição realizada com sucesso');
  };

  const handleSave = async () => {
    if (!hasPermission('templates:create') && !hasPermission('templates:update')) {
      showNotification('error', 'Permissão negada para salvar template');
      return;
    }

    if (validationErrors.some(error => error.severity === 'error')) {
      showNotification('error', 'Corrija os erros de validação antes de salvar');
      return;
    }

    try {
      if (template?.id) {
        await updateTemplate(template.id, formData);
        showNotification('success', 'Template atualizado com sucesso');
      } else {
        await createTemplate(formData);
        showNotification('success', 'Template criado com sucesso');
      }
      
      onSave?.(formData);
    } catch (error) {
      showNotification('error', 'Erro ao salvar template');
    }
  };

  const handlePreview = () => {
    setIsPreviewMode(!isPreviewMode);
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(formData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${formData.name.replace(/\s+/g, '_')}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    showNotification('success', 'Template exportado com sucesso');
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedTemplate = JSON.parse(e.target?.result as string);
        setFormData(importedTemplate);
        showNotification('success', 'Template importado com sucesso');
      } catch (error) {
        showNotification('error', 'Erro ao importar template');
      }
    };
    reader.readAsText(file);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(formData.content);
    showNotification('success', 'Conteúdo copiado para a área de transferência');
  };

  // Gerar preview com dados de exemplo
  const generatePreview = () => {
    const previewData: Record<string, any> = {};
    
    formData.variables.forEach(variable => {
      switch (variable) {
        case 'title':
          previewData[variable] = 'Título do Artigo';
          break;
        case 'author':
          previewData[variable] = 'João Silva';
          break;
        case 'date':
          previewData[variable] = new Date().toLocaleDateString('pt-BR');
          break;
        case 'content':
          previewData[variable] = 'Conteúdo do artigo...';
          break;
        case 'keywords':
          previewData[variable] = 'palavra-chave1, palavra-chave2';
          break;
        default:
          previewData[variable] = `[${variable}]`;
      }
    });

    setPreviewData(previewData);
  };

  // Renderizar preview
  const renderPreview = () => {
    let previewContent = formData.content;
    
    Object.entries(previewData).forEach(([key, value]) => {
      const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
      previewContent = previewContent.replace(regex, String(value));
    });

    return previewContent;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {template?.id ? 'Editar Template' : 'Novo Template'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {template?.id ? 'Modifique o template existente' : 'Crie um novo template'}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={validationErrors.some(e => e.severity === 'error')}>
            <Save className="w-4 h-4 mr-2" />
            Salvar
          </Button>
        </div>
      </div>

      {/* Formulário Principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configurações */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Configurações
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nome
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Nome do template"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Descrição
                </label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Descrição do template"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Categoria
                </label>
                <Select value={formData.category} onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(category => (
                      <SelectItem key={category} value={category}>
                        {category.replace('-', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Versão
                </label>
                <Input
                  value={formData.version}
                  onChange={(e) => setFormData(prev => ({ ...prev, version: e.target.value }))}
                  placeholder="1.0.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Status
                </label>
                <Select value={formData.status} onValueChange={(value) => setFormData(prev => ({ ...prev, status: value as any }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Rascunho</SelectItem>
                    <SelectItem value="active">Ativo</SelectItem>
                    <SelectItem value="archived">Arquivado</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={formData.isPublic}
                  onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <label htmlFor="isPublic" className="text-sm text-gray-700 dark:text-gray-300">
                  Template público
                </label>
              </div>
            </CardContent>
          </Card>

          {/* Variáveis Detectadas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="w-5 h-5" />
                Variáveis Detectadas
              </CardTitle>
            </CardHeader>
            <CardContent>
              {formData.variables.length > 0 ? (
                <div className="space-y-2">
                  {formData.variables.map((variable, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <span className="text-sm font-mono text-gray-700 dark:text-gray-300">
                        {variable}
                      </span>
                      <Badge variant="secondary" className="text-xs">
                        {{variable}}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Nenhuma variável detectada
                </p>
              )}
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardHeader>
              <CardTitle>Tags</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="cursor-pointer">
                    {tag}
                    <button
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        tags: prev.tags.filter((_, i) => i !== index)
                      }))}
                      className="ml-1 text-gray-400 hover:text-gray-600"
                    >
                      ×
                    </button>
                  </Badge>
                ))}
              </div>
              <Input
                placeholder="Adicionar tag..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                    setFormData(prev => ({
                      ...prev,
                      tags: [...prev.tags, e.currentTarget.value.trim()]
                    }));
                    e.currentTarget.value = '';
                  }
                }}
                className="mt-2"
              />
            </CardContent>
          </Card>
        </div>

        {/* Editor */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Editor
                </CardTitle>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowSearch(!showSearch)}
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Buscar
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleUndo}
                    disabled={undoStack.length === 0}
                  >
                    <Undo className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRedo}
                    disabled={redoStack.length === 0}
                  >
                    <Redo className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopy}
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePreview}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Preview
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="editor">Editor</TabsTrigger>
                  <TabsTrigger value="preview">Preview</TabsTrigger>
                </TabsList>
                
                <TabsContent value="editor" className="space-y-4">
                  {/* Busca e Substituição */}
                  {showSearch && (
                    <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                      <Input
                        placeholder="Buscar..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="flex-1"
                      />
                      <Input
                        placeholder="Substituir por..."
                        value={replaceTerm}
                        onChange={(e) => setReplaceTerm(e.target.value)}
                        className="flex-1"
                      />
                      <Button size="sm" onClick={handleSearch}>
                        Buscar
                      </Button>
                      <Button size="sm" onClick={handleReplace}>
                        Substituir
                      </Button>
                    </div>
                  )}

                  {/* Editor de Código */}
                  <div className="relative">
                    <Textarea
                      value={formData.content}
                      onChange={(e) => handleContentChange(e.target.value)}
                      placeholder="Digite seu template aqui... Use {{variável}} para inserir variáveis"
                      className="font-mono text-sm min-h-[400px] resize-none"
                      rows={20}
                    />
                    
                    {/* Indicador de posição do cursor */}
                    <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white dark:bg-gray-800 px-2 py-1 rounded">
                      Linha {cursorPosition.line}, Col {cursorPosition.column}
                    </div>
                  </div>

                  {/* Erros de Validação */}
                  {validationErrors.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Validação
                      </h4>
                      {validationErrors.map((error, index) => (
                        <div
                          key={index}
                          className={`flex items-center gap-2 p-2 rounded text-sm ${
                            error.severity === 'error'
                              ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
                              : error.severity === 'warning'
                              ? 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300'
                              : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                          }`}
                        >
                          {error.severity === 'error' ? (
                            <AlertCircle className="w-4 h-4" />
                          ) : error.severity === 'warning' ? (
                            <AlertCircle className="w-4 h-4" />
                          ) : (
                            <Info className="w-4 h-4" />
                          )}
                          <span>
                            Linha {error.line}: {error.message}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
                
                <TabsContent value="preview" className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Preview com Dados de Exemplo
                    </h4>
                    <Button size="sm" onClick={generatePreview}>
                      <Zap className="w-4 h-4 mr-2" />
                      Gerar Preview
                    </Button>
                  </div>
                  
                  <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded border">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                      {renderPreview()}
                    </pre>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Ações */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600 dark:text-gray-400">
                    Importar template:
                  </label>
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImport}
                    className="text-sm"
                  />
                </div>
                
                <div className="flex items-center gap-2">
                  <Button variant="outline" onClick={handleExport}>
                    <Download className="w-4 h-4 mr-2" />
                    Exportar
                  </Button>
                  
                  <Button variant="outline" onClick={handlePreview}>
                    <Play className="w-4 h-4 mr-2" />
                    Testar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor; 