/**
 * TemplatesDashboard.tsx
 * 
 * Dashboard principal para gestão de templates
 * 
 * Tracing ID: UI_TEMPLATES_DASHBOARD_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 12.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { 
  Search, 
  Plus, 
  Filter, 
  Grid, 
  List, 
  Download, 
  Upload,
  Eye,
  Edit,
  Trash2,
  Copy,
  History,
  Star
} from 'lucide-react';
import { TemplatesTable } from './TemplatesTable';
import { TemplatePreview } from './TemplatePreview';
import { TemplateStats } from './TemplateStats';
import { useTemplates } from '@/hooks/useTemplates';
import { useNotifications } from '@/hooks/useNotifications';
import { usePermissions } from '@/hooks/usePermissions';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  status: 'active' | 'draft' | 'archived';
  usageCount: number;
  rating: number;
  lastModified: string;
  author: string;
  tags: string[];
  isPublic: boolean;
}

interface TemplatesDashboardProps {
  className?: string;
}

export const TemplatesDashboard: React.FC<TemplatesDashboardProps> = ({ 
  className = '' 
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showStats, setShowStats] = useState(false);

  const { 
    templates, 
    loading, 
    error, 
    createTemplate, 
    updateTemplate, 
    deleteTemplate,
    duplicateTemplate,
    exportTemplate,
    importTemplate
  } = useTemplates();

  const { showNotification } = useNotifications();
  const { hasPermission } = usePermissions();

  // Filtros disponíveis
  const categories = [
    'all',
    'blog-posts',
    'social-media',
    'email-marketing',
    'seo-content',
    'product-descriptions',
    'landing-pages',
    'newsletters'
  ];

  const statuses = [
    'all',
    'active',
    'draft',
    'archived'
  ];

  // Filtrar templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || template.status === selectedStatus;

    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Métricas do dashboard
  const dashboardStats = {
    total: templates.length,
    active: templates.filter(t => t.status === 'active').length,
    draft: templates.filter(t => t.status === 'draft').length,
    archived: templates.filter(t => t.status === 'archived').length,
    totalUsage: templates.reduce((sum, t) => sum + t.usageCount, 0),
    avgRating: templates.length > 0 
      ? templates.reduce((sum, t) => sum + t.rating, 0) / templates.length 
      : 0
  };

  // Handlers
  const handleCreateTemplate = () => {
    if (!hasPermission('templates:create')) {
      showNotification('error', 'Permissão negada para criar templates');
      return;
    }
    // Implementar criação de template
    showNotification('info', 'Funcionalidade de criação será implementada');
  };

  const handleImportTemplates = () => {
    if (!hasPermission('templates:import')) {
      showNotification('error', 'Permissão negada para importar templates');
      return;
    }
    // Implementar importação
    showNotification('info', 'Funcionalidade de importação será implementada');
  };

  const handleExportTemplates = () => {
    if (!hasPermission('templates:export')) {
      showNotification('error', 'Permissão negada para exportar templates');
      return;
    }
    // Implementar exportação
    showNotification('info', 'Funcionalidade de exportação será implementada');
  };

  const handleTemplateAction = (action: string, template: Template) => {
    switch (action) {
      case 'preview':
        setSelectedTemplate(template);
        setShowPreview(true);
        break;
      case 'edit':
        if (!hasPermission('templates:update')) {
          showNotification('error', 'Permissão negada para editar templates');
          return;
        }
        // Implementar edição
        showNotification('info', 'Funcionalidade de edição será implementada');
        break;
      case 'duplicate':
        if (!hasPermission('templates:create')) {
          showNotification('error', 'Permissão negada para duplicar templates');
          return;
        }
        duplicateTemplate(template.id);
        showNotification('success', 'Template duplicado com sucesso');
        break;
      case 'delete':
        if (!hasPermission('templates:delete')) {
          showNotification('error', 'Permissão negada para excluir templates');
          return;
        }
        // Implementar exclusão com confirmação
        showNotification('info', 'Funcionalidade de exclusão será implementada');
        break;
    }
  };

  if (error) {
    return (
      <div className={`p-6 ${className}`}>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Erro ao carregar templates
              </h3>
              <p className="text-red-600 mb-4">{error}</p>
              <Button 
                variant="outline" 
                onClick={() => window.location.reload()}
              >
                Tentar novamente
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header do Dashboard */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Templates
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gerencie seus templates de conteúdo e prompts
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {hasPermission('templates:import') && (
            <Button variant="outline" onClick={handleImportTemplates}>
              <Upload className="w-4 h-4 mr-2" />
              Importar
            </Button>
          )}
          
          {hasPermission('templates:export') && (
            <Button variant="outline" onClick={handleExportTemplates}>
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          )}
          
          {hasPermission('templates:create') && (
            <Button onClick={handleCreateTemplate}>
              <Plus className="w-4 h-4 mr-2" />
              Novo Template
            </Button>
          )}
        </div>
      </div>

      {/* Métricas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {dashboardStats.total}
                </p>
              </div>
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <Grid className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Ativos
                </p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {dashboardStats.active}
                </p>
              </div>
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <Star className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Uso Total
                </p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {dashboardStats.totalUsage}
                </p>
              </div>
              <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <History className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Avaliação Média
                </p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {dashboardStats.avgRating.toFixed(1)}
                </p>
              </div>
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                <Star className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros e Controles */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col lg:flex-row gap-4 items-center">
            {/* Busca */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Buscar templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filtros */}
            <div className="flex gap-2">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Categoria" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(category => (
                    <SelectItem key={category} value={category}>
                      {category === 'all' ? 'Todas' : category.replace('-', ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  {statuses.map(status => (
                    <SelectItem key={status} value={status}>
                      {status === 'all' ? 'Todos' : status}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Controles de Visualização */}
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Templates */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              Templates ({filteredTemplates.length})
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowStats(!showStats)}
            >
              <Filter className="w-4 h-4 mr-2" />
              Estatísticas
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Carregando templates...</span>
            </div>
          ) : filteredTemplates.length === 0 ? (
            <div className="text-center py-12">
              <Grid className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Nenhum template encontrado
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {searchTerm || selectedCategory !== 'all' || selectedStatus !== 'all'
                  ? 'Tente ajustar os filtros de busca'
                  : 'Crie seu primeiro template para começar'
                }
              </p>
              {hasPermission('templates:create') && (
                <Button onClick={handleCreateTemplate}>
                  <Plus className="w-4 h-4 mr-2" />
                  Criar Template
                </Button>
              )}
            </div>
          ) : (
            <TemplatesTable
              templates={filteredTemplates}
              viewMode={viewMode}
              onTemplateAction={handleTemplateAction}
              hasPermissions={{
                update: hasPermission('templates:update'),
                delete: hasPermission('templates:delete'),
                duplicate: hasPermission('templates:create')
              }}
            />
          )}
        </CardContent>
      </Card>

      {/* Preview Modal */}
      {showPreview && selectedTemplate && (
        <TemplatePreview
          template={selectedTemplate}
          isOpen={showPreview}
          onClose={() => {
            setShowPreview(false);
            setSelectedTemplate(null);
          }}
        />
      )}

      {/* Stats Modal */}
      {showStats && (
        <TemplateStats
          templates={templates}
          isOpen={showStats}
          onClose={() => setShowStats(false)}
        />
      )}
    </div>
  );
};

export default TemplatesDashboard; 