import pytest
from unittest.mock import MagicMock, patch
from myapp.api.template_export import TemplateExportAPI, ExportManager, FormatConverter, ValidationEngine

@pytest.fixture
def export_api():
    return TemplateExportAPI()

@pytest.fixture
def sample_template():
    return {
        'id': 'template123',
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
        'metadata': {
            'created_by': 'user123',
            'created_at': '2024-01-01T10:00:00Z',
            'version': '1.0.0'
        }
    }

# 1. Teste de exportação de templates
def test_template_export(export_api, sample_template):
    export_manager = ExportManager()
    
    # Exportar template
    export_result = export_manager.export_template(sample_template['id'])
    assert export_result['exported'] is True
    assert export_result['export_id'] is not None
    assert export_result['template_id'] == 'template123'
    assert export_result['export_date'] is not None
    
    # Verificar exportação
    export_status = export_manager.get_export_status(export_result['export_id'])
    assert export_status['status'] in ['completed', 'processing', 'failed']
    assert 'download_url' in export_status

# 2. Teste de formatos de exportação
def test_export_formats(export_api, sample_template):
    format_converter = FormatConverter()
    
    # Exportar para PDF
    pdf_export = format_converter.export_to_pdf(sample_template)
    assert pdf_export['format'] == 'pdf'
    assert pdf_export['file_size'] > 0
    assert pdf_export['pages'] > 0
    assert 'download_url' in pdf_export
    
    # Exportar para Word
    word_export = format_converter.export_to_word(sample_template)
    assert word_export['format'] == 'docx'
    assert word_export['file_size'] > 0
    assert 'download_url' in word_export
    
    # Exportar para HTML
    html_export = format_converter.export_to_html(sample_template)
    assert html_export['format'] == 'html'
    assert 'content' in html_export
    assert '<html>' in html_export['content']
    
    # Exportar para JSON
    json_export = format_converter.export_to_json(sample_template)
    assert json_export['format'] == 'json'
    assert isinstance(json_export['content'], dict)
    assert json_export['content']['name'] == 'keyword_analysis_template'

# 3. Teste de validação
def test_export_validation(export_api, sample_template):
    validator = ValidationEngine()
    
    # Validar template antes da exportação
    validation_result = validator.validate_template_for_export(sample_template)
    assert validation_result['valid'] is True
    assert validation_result['errors'] == []
    assert 'warnings' in validation_result
    
    # Validar formato de exportação
    format_validation = validator.validate_export_format(sample_template, 'pdf')
    assert format_validation['supported'] is True
    assert format_validation['compatibility_score'] > 0
    
    # Testar validação com template inválido
    invalid_template = sample_template.copy()
    invalid_template['content'] = None
    invalid_validation = validator.validate_template_for_export(invalid_template)
    assert invalid_validation['valid'] is False
    assert len(invalid_validation['errors']) > 0

# 4. Teste de casos edge
def test_edge_cases(export_api):
    export_manager = ExportManager()
    
    # Teste com template inexistente
    with pytest.raises(Exception):
        export_manager.export_template('nonexistent_id')
    
    # Teste com formato não suportado
    format_converter = FormatConverter()
    with pytest.raises(ValueError):
        format_converter.export_to_format({}, 'unsupported_format')
    
    # Teste com template muito grande
    large_template = {
        'id': 'large_template',
        'content': {'sections': [{'content': 'x' * 1000000}]}  # 1MB de conteúdo
    }
    with pytest.raises(ValueError):
        export_manager.export_template(large_template['id'])

# 5. Teste de performance
def test_export_performance(export_api, sample_template, benchmark):
    format_converter = FormatConverter()
    
    def export_pdf_operation():
        return format_converter.export_to_pdf(sample_template)
    
    benchmark(export_pdf_operation)

# 6. Teste de integração
def test_integration_with_storage_system(export_api, sample_template):
    export_manager = ExportManager()
    
    # Integração com sistema de armazenamento
    with patch('myapp.storage.StorageSystem') as mock_storage:
        mock_storage.return_value.upload_file.return_value = {
            'uploaded': True, 
            'url': 's3://exports/template123.pdf'
        }
        
        result = export_manager.export_and_store(sample_template['id'], 'pdf')
        assert result['uploaded'] is True
        assert 's3://exports/template123.pdf' in result['url']

# 7. Teste de configuração
def test_configuration_management(export_api):
    # Configurar formatos suportados
    formats_config = export_api.configure_supported_formats([
        'pdf', 'docx', 'html', 'json', 'csv'
    ])
    assert 'pdf' in formats_config['formats']
    assert 'csv' in formats_config['formats']
    
    # Configurar limites de exportação
    limits_config = export_api.configure_export_limits({
        'max_file_size_mb': 50,
        'max_concurrent_exports': 10,
        'export_timeout_seconds': 300
    })
    assert limits_config['max_file_size_mb'] == 50

# 8. Teste de logs
def test_logging_functionality(export_api, sample_template, caplog):
    export_manager = ExportManager()
    
    with caplog.at_level('INFO'):
        export_manager.export_template(sample_template['id'])
    
    assert any('Template exported' in m for m in caplog.messages)
    assert any('template123' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            export_manager.export_template('invalid_id')
        except:
            pass
    
    assert any('Export failed' in m for m in caplog.messages)

# 9. Teste de métricas
def test_metrics_monitoring(export_api, sample_template):
    export_manager = ExportManager()
    
    # Monitorar métricas de exportação
    export_metrics = export_manager.monitor_export_metrics('2024-01-01', '2024-01-31')
    assert 'total_exports' in export_metrics
    assert 'format_distribution' in export_metrics
    assert 'avg_export_time' in export_metrics
    assert 'success_rate' in export_metrics
    
    # Monitorar performance do sistema
    system_metrics = export_manager.monitor_system_performance()
    assert 'active_exports' in system_metrics
    assert 'queue_size' in system_metrics
    assert 'storage_usage' in system_metrics

# 10. Teste de relatórios
def test_report_generation(export_api, sample_template):
    export_manager = ExportManager()
    
    # Gerar relatório de exportações
    export_report = export_manager.generate_export_report('2024-01-01', '2024-01-31')
    assert 'summary' in export_report
    assert 'format_breakdown' in export_report
    assert 'user_activity' in export_report
    assert 'performance_analysis' in export_report
    
    # Gerar relatório de uso
    usage_report = export_manager.generate_usage_report('2024-01-01', '2024-01-31')
    assert 'most_exported_templates' in usage_report
    assert 'export_trends' in usage_report
    assert 'storage_analysis' in usage_report 