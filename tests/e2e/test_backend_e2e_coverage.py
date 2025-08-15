"""
🧪 Testes E2E - Cobertura Completa Backend
🎯 Objetivo: Garantir cobertura E2E >90% para todos os workflows
📅 Data: 2025-01-27
🔗 Tracing ID: BACKEND_E2E_COVERAGE_001
📋 Ruleset: enterprise_control_layer.yaml

Testes end-to-end para workflows completos do sistema.
"""

import pytest
import json
import tempfile
import os
import asyncio
import requests
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any

# Importar módulos para testes E2E
from backend.app import create_app
from backend.app.services.lote_execucao_service import LoteExecucaoService
from backend.app.services.agendamento_service import AgendamentoService
from backend.app.services.payment_v1_service import PaymentV1Service
from backend.app.services.business_metrics_service import BusinessMetricsService
from backend.app.utils.audit_logger import AuditLogger
from backend.app.utils.alert_system import AlertSystem


class TestUserJourneyE2E:
    """Testes E2E para jornadas do usuário"""
    
    @pytest.fixture
    def test_app(self):
        """Cria aplicação de teste"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        return app
    
    @pytest.fixture
    def test_client(self, test_app):
        """Cria cliente de teste"""
        with test_app.test_client() as client:
            yield client
    
    def test_complete_user_registration_flow(self, test_client):
        """Testa fluxo completo de registro de usuário"""
        # 1. Registrar novo usuário
        registration_data = {
            'username': 'testuser_e2e',
            'email': 'test_e2e@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        }
        
        response = test_client.post('/api/auth/register', 
                                  json=registration_data,
                                  content_type='application/json')
        
        assert response.status_code == 201
        registration_result = response.get_json()
        assert registration_result['success'] == True
        assert 'user_id' in registration_result
        
        # 2. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'TestPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        login_result = response.get_json()
        assert 'access_token' in login_result
        assert 'refresh_token' in login_result
        
        access_token = login_result['access_token']
        
        # 3. Configurar credenciais de API
        credentials_data = {
            'provider': 'google_ads',
            'api_key': 'test_api_key_safe_12345',
            'api_secret': 'test_api_secret_safe_67890'
        }
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = test_client.post('/api/credentials/config',
                                  json=credentials_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        credentials_result = response.get_json()
        assert credentials_result['success'] == True
        
        # 4. Criar execução
        execution_data = {
            'categoria_id': 1,
            'palavras_chave': ['seo optimization', 'digital marketing'],
            'cluster': 'test_cluster_e2e'
        }
        
        response = test_client.post('/api/execucoes',
                                  json=execution_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        execution_result = response.get_json()
        assert 'execution_id' in execution_result
        
        # 5. Verificar status da execução
        execution_id = execution_result['execution_id']
        response = test_client.get(f'/api/execucoes/{execution_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        status_result = response.get_json()
        assert 'status' in status_result
        
        # 6. Obter resultados
        response = test_client.get(f'/api/execucoes/{execution_id}/results',
                                 headers=headers)
        
        assert response.status_code == 200
        results = response.get_json()
        assert isinstance(results, list)
        
        # 7. Exportar resultados
        export_data = {
            'format': 'csv',
            'execution_ids': [execution_id]
        }
        
        response = test_client.post('/api/execucoes/export',
                                  json=export_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 200
        export_result = response.get_json()
        assert 'download_url' in export_result
        
        # 8. Verificar métricas do usuário
        response = test_client.get('/api/metrics/user',
                                 headers=headers)
        
        assert response.status_code == 200
        metrics = response.get_json()
        assert 'total_executions' in metrics
        assert 'total_keywords' in metrics
        
        # 9. Fazer logout
        response = test_client.post('/api/auth/logout',
                                  headers=headers)
        
        assert response.status_code == 200
        logout_result = response.get_json()
        assert logout_result['success'] == True
    
    def test_batch_processing_workflow(self, test_client):
        """Testa workflow de processamento em lote"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Criar múltiplas execuções
        executions = []
        for i in range(5):
            execution_data = {
                'categoria_id': i + 1,
                'palavras_chave': [f'keyword_{i}_1', f'keyword_{i}_2'],
                'cluster': f'cluster_{i}'
            }
            
            response = test_client.post('/api/execucoes',
                                      json=execution_data,
                                      headers=headers,
                                      content_type='application/json')
            
            assert response.status_code == 201
            execution_id = response.get_json()['execution_id']
            executions.append(execution_id)
        
        # 3. Criar lote de processamento
        batch_data = {
            'execution_ids': executions,
            'config': {
                'max_concurrent': 3,
                'timeout_per_execution': 300
            }
        }
        
        response = test_client.post('/api/execucoes/batch',
                                  json=batch_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        batch_result = response.get_json()
        assert 'batch_id' in batch_result
        
        # 4. Monitorar progresso do lote
        batch_id = batch_result['batch_id']
        response = test_client.get(f'/api/execucoes/batch/{batch_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        batch_status = response.get_json()
        assert 'status' in batch_status
        assert 'progress' in batch_status
        
        # 5. Aguardar conclusão (simulado)
        # Em um teste real, aguardaríamos a conclusão real
        assert batch_status['total_executions'] == 5
    
    def test_scheduled_executions_workflow(self, test_client):
        """Testa workflow de execuções agendadas"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Criar agendamento
        schedule_data = {
            'nome': 'Teste Agendamento E2E',
            'descricao': 'Agendamento para testes E2E',
            'execucoes': [
                {
                    'categoria_id': 1,
                    'palavras_chave': ['scheduled_keyword_1', 'scheduled_keyword_2'],
                    'cluster': 'scheduled_cluster'
                }
            ],
            'tipo_recorrencia': 'diaria',
            'data_inicio': datetime.now(timezone.utc).isoformat(),
            'hora_execucao': '10:00'
        }
        
        response = test_client.post('/api/execucoes/schedule',
                                  json=schedule_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        schedule_result = response.get_json()
        assert 'schedule_id' in schedule_result
        
        # 3. Verificar agendamento
        schedule_id = schedule_result['schedule_id']
        response = test_client.get(f'/api/execucoes/schedule/{schedule_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        schedule_info = response.get_json()
        assert schedule_info['nome'] == 'Teste Agendamento E2E'
        assert schedule_info['tipo_recorrencia'] == 'diaria'
        
        # 4. Listar agendamentos ativos
        response = test_client.get('/api/execucoes/schedule',
                                 headers=headers)
        
        assert response.status_code == 200
        schedules = response.get_json()
        assert isinstance(schedules, list)
        assert len(schedules) > 0
        
        # 5. Cancelar agendamento
        response = test_client.delete(f'/api/execucoes/schedule/{schedule_id}',
                                    headers=headers)
        
        assert response.status_code == 200
        cancel_result = response.get_json()
        assert cancel_result['success'] == True


class TestPaymentWorkflowE2E:
    """Testes E2E para workflows de pagamento"""
    
    def test_complete_payment_flow(self, test_client):
        """Testa fluxo completo de pagamento"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Criar pagamento
        payment_data = {
            'amount': 99.99,
            'currency': 'BRL',
            'payment_method': 'credit_card',
            'description': 'Teste E2E - Plano Premium',
            'card_data': {
                'number': '4111111111111111',
                'expiry': '12/25',
                'cvv': '123'
            }
        }
        
        response = test_client.post('/api/payments',
                                  json=payment_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        payment_result = response.get_json()
        assert 'payment_id' in payment_result
        
        # 3. Processar pagamento
        payment_id = payment_result['payment_id']
        response = test_client.post(f'/api/payments/{payment_id}/process',
                                  headers=headers)
        
        assert response.status_code == 200
        process_result = response.get_json()
        assert 'status' in process_result
        
        # 4. Verificar status do pagamento
        response = test_client.get(f'/api/payments/{payment_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        payment_status = response.get_json()
        assert 'status' in payment_status
        assert 'amount' in payment_status
        
        # 5. Obter histórico de pagamentos
        response = test_client.get('/api/payments/history',
                                 headers=headers)
        
        assert response.status_code == 200
        history = response.get_json()
        assert isinstance(history, list)
        assert len(history) > 0
        
        # 6. Solicitar reembolso (se aplicável)
        if payment_status['status'] == 'completed':
            refund_data = {
                'reason': 'Teste E2E',
                'amount': payment_status['amount']
            }
            
            response = test_client.post(f'/api/payments/{payment_id}/refund',
                                      json=refund_data,
                                      headers=headers,
                                      content_type='application/json')
            
            assert response.status_code in [200, 201]
            refund_result = response.get_json()
            assert 'refund_id' in refund_result


class TestAnalyticsWorkflowE2E:
    """Testes E2E para workflows de analytics"""
    
    def test_complete_analytics_workflow(self, test_client):
        """Testa fluxo completo de analytics"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Obter métricas gerais
        response = test_client.get('/api/metrics/overview',
                                 headers=headers)
        
        assert response.status_code == 200
        overview = response.get_json()
        assert 'total_executions' in overview
        assert 'total_keywords' in overview
        assert 'success_rate' in overview
        
        # 3. Obter métricas por período
        period_data = {
            'start_date': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            'end_date': datetime.now(timezone.utc).isoformat(),
            'granularity': 'daily'
        }
        
        response = test_client.post('/api/metrics/period',
                                  json=period_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 200
        period_metrics = response.get_json()
        assert isinstance(period_metrics, list)
        
        # 4. Obter análise de performance
        response = test_client.get('/api/analytics/performance',
                                 headers=headers)
        
        assert response.status_code == 200
        performance = response.get_json()
        assert 'avg_response_time' in performance
        assert 'error_rate' in performance
        assert 'throughput' in performance
        
        # 5. Obter insights de keywords
        response = test_client.get('/api/analytics/keyword-insights',
                                 headers=headers)
        
        assert response.status_code == 200
        insights = response.get_json()
        assert isinstance(insights, list)
        
        # 6. Gerar relatório personalizado
        report_data = {
            'name': 'Relatório E2E',
            'metrics': ['executions', 'keywords', 'performance'],
            'filters': {
                'date_range': 'last_30_days',
                'categories': [1, 2, 3]
            },
            'format': 'pdf'
        }
        
        response = test_client.post('/api/analytics/reports',
                                  json=report_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        report_result = response.get_json()
        assert 'report_id' in report_result
        
        # 7. Verificar status do relatório
        report_id = report_result['report_id']
        response = test_client.get(f'/api/analytics/reports/{report_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        report_status = response.get_json()
        assert 'status' in report_status


class TestAdminWorkflowE2E:
    """Testes E2E para workflows administrativos"""
    
    def test_admin_dashboard_workflow(self, test_client):
        """Testa fluxo do dashboard administrativo"""
        # 1. Fazer login como admin
        login_data = {
            'username': 'admin_e2e',
            'password': 'AdminPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Obter visão geral do sistema
        response = test_client.get('/api/admin/overview',
                                 headers=headers)
        
        assert response.status_code == 200
        overview = response.get_json()
        assert 'total_users' in overview
        assert 'total_executions' in overview
        assert 'system_health' in overview
        
        # 3. Obter métricas de usuários
        response = test_client.get('/api/admin/users/metrics',
                                 headers=headers)
        
        assert response.status_code == 200
        user_metrics = response.get_json()
        assert 'active_users' in user_metrics
        assert 'new_users_today' in user_metrics
        assert 'user_growth_rate' in user_metrics
        
        # 4. Obter métricas de sistema
        response = test_client.get('/api/admin/system/metrics',
                                 headers=headers)
        
        assert response.status_code == 200
        system_metrics = response.get_json()
        assert 'cpu_usage' in system_metrics
        assert 'memory_usage' in system_metrics
        assert 'disk_usage' in system_metrics
        assert 'uptime' in system_metrics
        
        # 5. Obter alertas ativos
        response = test_client.get('/api/admin/alerts',
                                 headers=headers)
        
        assert response.status_code == 200
        alerts = response.get_json()
        assert isinstance(alerts, list)
        
        # 6. Obter logs do sistema
        response = test_client.get('/api/admin/logs',
                                 headers=headers)
        
        assert response.status_code == 200
        logs = response.get_json()
        assert isinstance(logs, list)
        
        # 7. Obter configurações do sistema
        response = test_client.get('/api/admin/config',
                                 headers=headers)
        
        assert response.status_code == 200
        config = response.get_json()
        assert 'system_settings' in config
        assert 'security_settings' in config
    
    def test_user_management_workflow(self, test_client):
        """Testa fluxo de gestão de usuários"""
        # 1. Fazer login como admin
        login_data = {
            'username': 'admin_e2e',
            'password': 'AdminPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Listar usuários
        response = test_client.get('/api/admin/users',
                                 headers=headers)
        
        assert response.status_code == 200
        users = response.get_json()
        assert isinstance(users, list)
        
        # 3. Obter detalhes de um usuário
        if users:
            user_id = users[0]['id']
            response = test_client.get(f'/api/admin/users/{user_id}',
                                     headers=headers)
            
            assert response.status_code == 200
            user_details = response.get_json()
            assert 'id' in user_details
            assert 'username' in user_details
            assert 'email' in user_details
        
        # 4. Atualizar status de usuário
        if users:
            user_id = users[0]['id']
            update_data = {
                'status': 'active',
                'role': 'user'
            }
            
            response = test_client.put(f'/api/admin/users/{user_id}',
                                     json=update_data,
                                     headers=headers,
                                     content_type='application/json')
            
            assert response.status_code == 200
            update_result = response.get_json()
            assert update_result['success'] == True


class TestSecurityWorkflowE2E:
    """Testes E2E para workflows de segurança"""
    
    def test_security_monitoring_workflow(self, test_client):
        """Testa fluxo de monitoramento de segurança"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Verificar logs de segurança
        response = test_client.get('/api/security/logs',
                                 headers=headers)
        
        assert response.status_code == 200
        security_logs = response.get_json()
        assert isinstance(security_logs, list)
        
        # 3. Verificar tentativas de login
        response = test_client.get('/api/security/login-attempts',
                                 headers=headers)
        
        assert response.status_code == 200
        login_attempts = response.get_json()
        assert isinstance(login_attempts, list)
        
        # 4. Verificar atividades suspeitas
        response = test_client.get('/api/security/suspicious-activities',
                                 headers=headers)
        
        assert response.status_code == 200
        suspicious_activities = response.get_json()
        assert isinstance(suspicious_activities, list)
        
        # 5. Verificar configurações de segurança
        response = test_client.get('/api/security/settings',
                                 headers=headers)
        
        assert response.status_code == 200
        security_settings = response.get_json()
        assert 'two_factor_enabled' in security_settings
        assert 'password_policy' in security_settings
        assert 'session_timeout' in security_settings
    
    def test_audit_trail_workflow(self, test_client):
        """Testa fluxo de trilha de auditoria"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Obter trilha de auditoria
        response = test_client.get('/api/audit/trail',
                                 headers=headers)
        
        assert response.status_code == 200
        audit_trail = response.get_json()
        assert isinstance(audit_trail, list)
        
        # 3. Filtrar eventos de auditoria
        filter_data = {
            'event_type': 'user_login',
            'start_date': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
            'end_date': datetime.now(timezone.utc).isoformat()
        }
        
        response = test_client.post('/api/audit/filter',
                                  json=filter_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 200
        filtered_events = response.get_json()
        assert isinstance(filtered_events, list)
        
        # 4. Exportar trilha de auditoria
        export_data = {
            'format': 'csv',
            'filters': filter_data
        }
        
        response = test_client.post('/api/audit/export',
                                  json=export_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 200
        export_result = response.get_json()
        assert 'download_url' in export_result


class TestIntegrationWorkflowE2E:
    """Testes E2E para workflows de integração"""
    
    def test_webhook_integration_workflow(self, test_client):
        """Testa fluxo de integração via webhooks"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Configurar webhook
        webhook_data = {
            'url': 'https://webhook.site/test-e2e',
            'events': ['execution_completed', 'payment_processed'],
            'secret': 'webhook_secret_123'
        }
        
        response = test_client.post('/api/webhooks',
                                  json=webhook_data,
                                  headers=headers,
                                  content_type='application/json')
        
        assert response.status_code == 201
        webhook_result = response.get_json()
        assert 'webhook_id' in webhook_result
        
        # 3. Verificar webhook
        webhook_id = webhook_result['webhook_id']
        response = test_client.get(f'/api/webhooks/{webhook_id}',
                                 headers=headers)
        
        assert response.status_code == 200
        webhook_info = response.get_json()
        assert webhook_info['url'] == 'https://webhook.site/test-e2e'
        
        # 4. Testar webhook
        response = test_client.post(f'/api/webhooks/{webhook_id}/test',
                                  headers=headers)
        
        assert response.status_code == 200
        test_result = response.get_json()
        assert 'success' in test_result
        
        # 5. Obter logs do webhook
        response = test_client.get(f'/api/webhooks/{webhook_id}/logs',
                                 headers=headers)
        
        assert response.status_code == 200
        webhook_logs = response.get_json()
        assert isinstance(webhook_logs, list)
    
    def test_api_integration_workflow(self, test_client):
        """Testa fluxo de integração via API"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Obter documentação da API
        response = test_client.get('/api/docs',
                                 headers=headers)
        
        assert response.status_code == 200
        api_docs = response.get_json()
        assert 'endpoints' in api_docs
        assert 'schemas' in api_docs
        
        # 3. Verificar status da API
        response = test_client.get('/api/health',
                                 headers=headers)
        
        assert response.status_code == 200
        health_status = response.get_json()
        assert 'status' in health_status
        assert health_status['status'] == 'healthy'
        
        # 4. Obter métricas da API
        response = test_client.get('/api/metrics',
                                 headers=headers)
        
        assert response.status_code == 200
        api_metrics = response.get_json()
        assert 'request_count' in api_metrics
        assert 'error_rate' in api_metrics
        assert 'response_time' in api_metrics


class TestPerformanceE2E:
    """Testes E2E de performance"""
    
    def test_load_testing_scenario(self, test_client):
        """Testa cenário de teste de carga"""
        # 1. Fazer login
        login_data = {
            'username': 'testuser_e2e',
            'password': 'StrongPassword123!'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=login_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        access_token = response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 2. Executar múltiplas requisições simultâneas
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(request_id):
            try:
                start_time = time.time()
                response = test_client.get('/api/metrics/overview',
                                         headers=headers)
                end_time = time.time()
                
                results.append({
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                errors.append({
                    'request_id': request_id,
                    'error': str(e)
                })
        
        # Executar 10 requisições simultâneas
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 10
        assert len(errors) == 0
        
        # Verificar tempos de resposta
        response_times = [r['response_time'] for r in results]
        avg_response_time = sum(response_times) / len(response_times)
        
        # Tempo médio deve ser menor que 1 segundo
        assert avg_response_time < 1.0
        
        # Verificar códigos de status
        status_codes = [r['status_code'] for r in results]
        assert all(code == 200 for code in status_codes)
    
    def test_concurrent_user_scenario(self, test_client):
        """Testa cenário de usuários concorrentes"""
        # Simular múltiplos usuários fazendo login simultaneamente
        users = [
            {'username': 'user1', 'password': 'Password123!'},
            {'username': 'user2', 'password': 'Password123!'},
            {'username': 'user3', 'password': 'Password123!'}
        ]
        
        import threading
        import time
        
        login_results = []
        
        def user_login(user_data):
            try:
                start_time = time.time()
                response = test_client.post('/api/auth/login',
                                          json=user_data,
                                          content_type='application/json')
                end_time = time.time()
                
                login_results.append({
                    'username': user_data['username'],
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                })
            except Exception as e:
                login_results.append({
                    'username': user_data['username'],
                    'error': str(e),
                    'success': False
                })
        
        # Executar logins simultâneos
        threads = []
        for user in users:
            thread = threading.Thread(target=user_login, args=(user,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        successful_logins = [r for r in login_results if r['success']]
        assert len(successful_logins) > 0
        
        # Verificar tempos de resposta
        response_times = [r['response_time'] for r in successful_logins]
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2.0  # Login pode ser mais lento


class TestErrorHandlingE2E:
    """Testes E2E de tratamento de erros"""
    
    def test_error_scenarios(self, test_client):
        """Testa cenários de erro"""
        # 1. Tentar acessar endpoint sem autenticação
        response = test_client.get('/api/metrics/overview')
        assert response.status_code == 401
        
        # 2. Tentar fazer login com credenciais inválidas
        invalid_login = {
            'username': 'invalid_user',
            'password': 'wrong_password'
        }
        
        response = test_client.post('/api/auth/login',
                                  json=invalid_login,
                                  content_type='application/json')
        assert response.status_code == 401
        
        # 3. Tentar acessar recurso inexistente
        response = test_client.get('/api/nonexistent/endpoint')
        assert response.status_code == 404
        
        # 4. Tentar enviar dados inválidos
        invalid_data = {
            'invalid_field': 'invalid_value'
        }
        
        response = test_client.post('/api/execucoes',
                                  json=invalid_data,
                                  content_type='application/json')
        assert response.status_code == 400
        
        # 5. Tentar acessar com token inválido
        invalid_headers = {'Authorization': 'Bearer invalid_token'}
        response = test_client.get('/api/metrics/overview',
                                 headers=invalid_headers)
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 