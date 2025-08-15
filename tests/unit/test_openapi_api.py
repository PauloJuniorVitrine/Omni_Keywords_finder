import pytest
from unittest.mock import MagicMock, patch
from myapp.api.openapi import OpenAPIAPI, DocumentationGenerator, SchemaValidator, ComplianceChecker

@pytest.fixture
def openapi_api():
    return OpenAPIAPI()

@pytest.fixture
def sample_api_spec():
    return {
        'openapi': '3.0.0',
        'info': {
            'title': 'Omni Keywords Finder API',
            'version': '1.0.0',
            'description': 'API for keyword analysis and management'
        },
        'paths': {
            '/api/v1/keywords': {
                'get': {
                    'summary': 'Get keywords',
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/Keyword'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        'components': {
            'schemas': {
                'Keyword': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'term': {'type': 'string'},
                        'volume': {'type': 'integer'}
                    }
                }
            }
        }
    }

# 1. Teste de geração de documentação
def test_documentation_generation(openapi_api, sample_api_spec):
    doc_generator = DocumentationGenerator()
    
    # Gerar documentação HTML
    html_docs = doc_generator.generate_html_documentation(sample_api_spec)
    assert html_docs['format'] == 'html'
    assert 'content' in html_docs
    assert '<html>' in html_docs['content']
    assert 'Omni Keywords Finder API' in html_docs['content']
    
    # Gerar documentação JSON
    json_docs = doc_generator.generate_json_documentation(sample_api_spec)
    assert json_docs['format'] == 'json'
    assert isinstance(json_docs['content'], dict)
    assert json_docs['content']['openapi'] == '3.0.0'
    
    # Gerar documentação YAML
    yaml_docs = doc_generator.generate_yaml_documentation(sample_api_spec)
    assert yaml_docs['format'] == 'yaml'
    assert 'content' in yaml_docs
    assert 'openapi: 3.0.0' in yaml_docs['content']

# 2. Teste de validação de schemas
def test_schema_validation(openapi_api, sample_api_spec):
    schema_validator = SchemaValidator()
    
    # Validar schema OpenAPI
    validation_result = schema_validator.validate_openapi_schema(sample_api_spec)
    assert validation_result['valid'] is True
    assert validation_result['errors'] == []
    assert 'warnings' in validation_result
    
    # Validar schemas individuais
    schema_validation = schema_validator.validate_component_schemas(sample_api_spec)
    assert 'Keyword' in schema_validation
    assert schema_validation['Keyword']['valid'] is True
    
    # Testar schema inválido
    invalid_spec = sample_api_spec.copy()
    invalid_spec['openapi'] = 'invalid_version'
    invalid_validation = schema_validator.validate_openapi_schema(invalid_spec)
    assert invalid_validation['valid'] is False
    assert len(invalid_validation['errors']) > 0

# 3. Teste de casos edge
def test_edge_cases(openapi_api):
    doc_generator = DocumentationGenerator()
    
    # Teste com especificação vazia
    empty_spec = {}
    with pytest.raises(ValueError):
        doc_generator.generate_html_documentation(empty_spec)
    
    # Teste com especificação inválida
    invalid_spec = {'invalid': 'structure'}
    with pytest.raises(ValueError):
        doc_generator.generate_html_documentation(invalid_spec)
    
    # Teste com schema circular
    circular_spec = {
        'openapi': '3.0.0',
        'components': {
            'schemas': {
                'A': {'$ref': '#/components/schemas/B'},
                'B': {'$ref': '#/components/schemas/A'}
            }
        }
    }
    with pytest.raises(ValueError):
        doc_generator.generate_html_documentation(circular_spec)

# 4. Teste de performance
def test_openapi_performance(openapi_api, sample_api_spec, benchmark):
    doc_generator = DocumentationGenerator()
    
    def generate_docs_operation():
        return doc_generator.generate_html_documentation(sample_api_spec)
    
    benchmark(generate_docs_operation)

# 5. Teste de integração
def test_integration_with_api_framework(openapi_api, sample_api_spec):
    doc_generator = DocumentationGenerator()
    
    # Integração com framework de API
    with patch('myapp.framework.APIFramework') as mock_framework:
        mock_framework.return_value.get_api_spec.return_value = sample_api_spec
        
        result = doc_generator.generate_from_framework()
        assert result['format'] == 'html'
        assert 'content' in result

# 6. Teste de configuração
def test_configuration_management(openapi_api):
    # Configurar opções de documentação
    doc_config = openapi_api.configure_documentation_options({
        'include_examples': True,
        'include_deprecated': False,
        'theme': 'dark',
        'show_curl_examples': True
    })
    assert doc_config['include_examples'] is True
    assert doc_config['theme'] == 'dark'
    
    # Configurar validação
    validation_config = openapi_api.configure_validation_options({
        'strict_mode': True,
        'check_deprecated': True,
        'validate_examples': True
    })
    assert validation_config['strict_mode'] is True

# 7. Teste de logs
def test_logging_functionality(openapi_api, sample_api_spec, caplog):
    doc_generator = DocumentationGenerator()
    
    with caplog.at_level('INFO'):
        doc_generator.generate_html_documentation(sample_api_spec)
    
    assert any('Documentation generated' in m for m in caplog.messages)
    assert any('HTML' in m for m in caplog.messages)
    
    # Verificar logs de erro
    with caplog.at_level('ERROR'):
        try:
            doc_generator.generate_html_documentation({})
        except:
            pass
    
    assert any('Failed to generate documentation' in m for m in caplog.messages)

# 8. Teste de métricas
def test_metrics_monitoring(openapi_api, sample_api_spec):
    doc_generator = DocumentationGenerator()
    
    # Monitorar métricas de documentação
    doc_metrics = doc_generator.monitor_documentation_metrics('2024-01-01', '2024-01-31')
    assert 'total_generations' in doc_metrics
    assert 'format_distribution' in doc_metrics
    assert 'avg_generation_time' in doc_metrics
    assert 'error_rate' in doc_metrics
    
    # Monitorar performance do sistema
    system_metrics = doc_generator.monitor_system_performance()
    assert 'active_generations' in system_metrics
    assert 'cache_hit_rate' in system_metrics
    assert 'validation_performance' in system_metrics

# 9. Teste de relatórios
def test_report_generation(openapi_api, sample_api_spec):
    doc_generator = DocumentationGenerator()
    
    # Gerar relatório de documentação
    doc_report = doc_generator.generate_documentation_report('2024-01-01', '2024-01-31')
    assert 'summary' in doc_report
    assert 'generation_stats' in doc_report
    assert 'popular_endpoints' in doc_report
    assert 'quality_metrics' in doc_report
    
    # Gerar relatório de API
    api_report = doc_generator.generate_api_report(sample_api_spec)
    assert 'endpoint_count' in api_report
    assert 'schema_count' in api_report
    assert 'coverage_analysis' in api_report
    assert 'compliance_status' in api_report

# 10. Teste de compliance
def test_compliance_checks(openapi_api, sample_api_spec):
    compliance_checker = ComplianceChecker()
    
    # Verificar compliance OpenAPI
    openapi_compliance = compliance_checker.check_openapi_compliance(sample_api_spec)
    assert openapi_compliance['compliant'] in [True, False]
    assert 'version_compliance' in openapi_compliance
    assert 'schema_compliance' in openapi_compliance
    
    # Verificar compliance de documentação
    doc_compliance = compliance_checker.check_documentation_compliance(sample_api_spec)
    assert doc_compliance['compliant'] in [True, False]
    assert 'completeness' in doc_compliance
    assert 'accuracy' in doc_compliance
    assert 'accessibility' in doc_compliance 