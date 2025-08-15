import pytest
from unittest.mock import MagicMock, patch
from myapp.api.template_management import TemplateManagementAPI, TemplateCreator, VersionManager, SharingManager

@pytest.fixture
def template_api():
    return TemplateManagementAPI()

@pytest.fixture
def sample_template():
    return {
        'name': 'keyword_analysis_template',
        'description': 'Template for keyword analysis reports',
        'content': {
            'sections': [
                {'title': 'Overview', 'type': 'text', 'content': 'Analysis overview'},
                {'title': 'Keywords', 'type': 'table', 'content': 'keyword_data'},
                {'title': 'Recommendations', 'type': 'list', 'content': 'recommendations'}
            ],
            'styling': {
                'theme': 'professional',
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c'],
                'font': 'Arial'
            }
        },
        'tags': ['analysis', 'keywords', 'seo'],
        'category': 'reports'
    }

# 1. Teste de criação de templates
def test_template_creation(template_api, sample_template):
    creator = TemplateCreator()
    
    # Criar template
    created_template = creator.create_template(sample_template)
    assert created_template['name'] == 'keyword_analysis_template'
    assert created_template['id'] is not None
    assert created_template['version'] == '1.0.0'
    assert created_template['status'] == 'draft'
    assert len(created_template['content']['sections']) == 3
    
    # Verificar template criado
    template = creator.get_template(created_template['id'])
    assert template['description'] == 'Template for keyword analysis reports'
    assert template['category'] == 'reports'
    assert 'keyword_analysis_template' in template['tags']

# 2. Teste de edição de templates
def test_template_editing(template_api, sample_template):
    creator = TemplateCreator()
    
    # Criar template primeiro
    template = creator.create_template(sample_template)
    
    # Editar template
    edit_data = {
        'description': 'Updated description for keyword analysis',
        'content': {
            'sections': [
                {'title': 'Executive Summary', 'type': 'text', 'content': 'Updated overview'},
                {'title': 'Keywords', 'type': 'table', 'content': 'keyword_data'},
                {'title': 'Action Items', 'type': 'list', 'content': 'action_items'}
            ]
        }
    }
    
    updated_template = creator.edit_template(template['id'], edit_data)
    assert updated_template['description'] == 'Updated description for keyword analysis'
    assert updated_template['version'] == '1.1.0' # Corrected version to 1.1.0 for consistency
    assert updated_template['content']['sections'][0]['title'] == 'Executive Summary'

# 3. Teste de versionamento
def test_template_versioning(template_api, sample_template):
    version_manager = VersionManager()
    creator = TemplateCreator()
    
    # Criar template
    template = creator.create_template(sample_template)
    
    # Criar nova versão
    new_version_data = {
        'content': {
            'sections': [
                {'title': 'New Section', 'type': 'chart', 'content': 'chart_data'}
            ]
        },
        'version_notes': 'Added chart section'
    }
    
    new_version = version_manager.create_version(template['id'], new_version_data)
    assert new_version['version'] == '1.1.0'
    assert new_version['version_notes'] == 'Added chart section'
    
    # Listar versões
    versions = version_manager.list_versions(template['id'])
    assert len(versions) >= 2
    assert all('version' in v for v in versions)
    
    # Comparar versões
    comparison = version_manager.compare_versions(template['id'], '1.0.0', '1.1.0')
    assert 'differences' in comparison
    assert 'added_sections' in comparison
    assert 'modified_sections' in comparison

# 4. Teste de compartilhamento
def test_template_sharing(template_api, sample_template):
    sharing_manager = SharingManager()
    creator = TemplateCreator()
    
    # Criar template
    template = creator.create_template(sample_template)
    
    # Compartilhar template
    share_config = {
        'users': ['user1', 'user2'],
        'permissions': ['read', 'edit'],
        'expires_at': '2024-12-31T23:59:59Z'
    }
    
    sharing_result = sharing_manager.share_template(template['id'], share_config)
    assert sharing_result['shared'] is True
    assert sharing_result['share_id'] is not None
    assert len(sharing_result['shared_with']) == 2
    
    # Verificar permissões
    permissions = sharing_manager.get_template_permissions(template['id'], 'user1')
    assert 'read' in permissions
    assert 'edit' in permissions
    
    # Revogar acesso
    revoke_result = sharing_manager.revoke_access(template['id'], 'user1')
    assert revoke_result['revoked'] is True

# 5. Teste de casos edge
def test_edge_cases(template_api):
    creator = TemplateCreator()
    
    # Teste com template vazio
    empty_template = {}
    with pytest.raises(ValueError):
        creator.create_template(empty_template)
    
    # Teste com nome duplicado
    duplicate_template = {
        'name': 'duplicate_template',
        'description': 'Test',
        'content': {'sections': []}
    }
    creator.create_template(duplicate_template)
    with pytest.raises(Exception):
        creator.create_template(duplicate_template)
    
    # Teste com conteúdo inválido
    invalid_template = {
        'name': 'test',
        'description': 'Test',
        'content': {'invalid': 'structure'}
    }
    with pytest.raises(ValueError):
        creator.create_template(invalid_template)

# 6. Teste de performance
def test_template_performance(template_api, sample_template, benchmark):
    creator = TemplateCreator()
    
    def create_template_operation():
        return creator.create_template(sample_template)
    
    benchmark(create_template_operation)

# 7. Teste de integração
def test_integration_with_storage_system(template_api, sample_template):
    creator = TemplateCreator()
    
    # Integração com sistema de armazenamento
    with patch('myapp.storage.StorageSystem') as mock_storage:
        mock_storage.return_value.save_template.return_value = {'saved': True, 'url': 's3://templates/template1'}
        
        result = creator.save_template_to_storage(sample_template)
        assert result['saved'] is True
        assert 's3://templates/template1' in result['url']

# 8. Teste de configuração
def test_configuration_management(template_api):
    # Configurar limites de templates
    limits_config = template_api.configure_template_limits({
        'max_templates_per_user': 100,
        'max_template_size_mb': 10,
        'max_versions_per_template': 50
    })
    assert limits_config['max_templates_per_user'] == 100
    
    # Configurar categorias
    categories_config = template_api.configure_categories([
        'reports', 'dashboards', 'forms', 'presentations'
    ])
    assert 'reports' in categories_config['categories']
    assert 'presentations' in categories_config['categories']

# 9. Teste de logs
def test_logging_functionality(template_api, sample_template, caplog):
    creator = TemplateCreator()
    
    with caplog.at_level('INFO'):
        creator.create_template(sample_template)
    
    assert any('Template created' in m for m in caplog.messages)
    assert any('keyword_analysis_template' in m for m in caplog.messages)
    
    # Verificar logs de auditoria
    with caplog.at_level('AUDIT'):
        creator.edit_template('template_id', {'description': 'Updated'})
    
    assert any('Template edited' in m for m in caplog.messages)

# 10. Teste de métricas
def test_metrics_monitoring(template_api, sample_template):
    creator = TemplateCreator()
    
    # Monitorar uso de templates
    usage_metrics = creator.monitor_template_usage('2024-01-01', '2024-01-31')
    assert 'total_templates' in usage_metrics
    assert 'most_used_templates' in usage_metrics
    assert 'creation_rate' in usage_metrics
    assert 'edit_frequency' in usage_metrics
    
    # Monitorar performance do sistema
    system_metrics = creator.monitor_system_performance()
    assert 'storage_usage' in system_metrics
    assert 'template_processing_time' in system_metrics
    assert 'version_management_performance' in system_metrics 