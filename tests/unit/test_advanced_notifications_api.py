"""
Testes unitários para Advanced Notifications API
Cobertura: Envio de notificações, templates, canais, métricas
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Advanced Notifications API
class AdvancedNotificationsAPI:
    """API para notificações avançadas"""
    
    def __init__(self, notification_config: Dict[str, Any] = None):
        self.notification_config = notification_config or {
            'max_retries': 3,
            'retry_delay': 60,
            'rate_limit': 1000,
            'enable_templates': True,
            'default_channels': ['email', 'sms']
        }
        self.notifications = {}
        self.templates = {}
        self.channels = {}
        self.notification_history = []
        self.system_metrics = {
            'notifications_sent': 0,
            'notifications_failed': 0,
            'templates_used': 0,
            'channels_used': 0,
            'total_delivery_time': 0
        }
    
    def send_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia uma notificação"""
        try:
            # Validar dados da notificação
            validation = self._validate_notification_data(notification_data)
            if not validation['valid']:
                self._log_operation('send_notification', 'validation', False, validation['error'])
                return validation
            
            # Gerar ID único
            notification_id = self._generate_notification_id()
            
            # Processar template se especificado
            if 'template_id' in notification_data:
                processed_content = self._process_template(
                    notification_data['template_id'], 
                    notification_data.get('variables', {})
                )
                if not processed_content['success']:
                    return processed_content
                notification_data['content'] = processed_content['content']
            
            # Preparar notificação
            notification = {
                'id': notification_id,
                'recipient': notification_data['recipient'],
                'subject': notification_data.get('subject', ''),
                'content': notification_data['content'],
                'channels': notification_data.get('channels', self.notification_config['default_channels']),
                'priority': notification_data.get('priority', 'normal'),
                'scheduled_at': notification_data.get('scheduled_at', datetime.now()),
                'created_at': datetime.now(),
                'status': 'pending',
                'retry_count': 0,
                'metadata': notification_data.get('metadata', {})
            }
            
            # Enviar através dos canais
            delivery_results = {}
            start_time = datetime.now()
            
            for channel in notification['channels']:
                if channel in self.channels:
                    channel_result = self._send_via_channel(channel, notification)
                    delivery_results[channel] = channel_result
                else:
                    delivery_results[channel] = {'success': False, 'error': 'Channel not available'}
            
            end_time = datetime.now()
            delivery_time = (end_time - start_time).total_seconds()
            
            # Determinar status geral
            successful_channels = [c for c, r in delivery_results.items() if r['success']]
            notification['status'] = 'sent' if successful_channels else 'failed'
            notification['delivery_results'] = delivery_results
            notification['delivery_time'] = delivery_time
            notification['sent_at'] = datetime.now() if successful_channels else None
            
            # Atualizar métricas
            if successful_channels:
                self.system_metrics['notifications_sent'] += 1
                self.system_metrics['total_delivery_time'] += delivery_time
            else:
                self.system_metrics['notifications_failed'] += 1
            
            self.system_metrics['channels_used'] += len(notification['channels'])
            
            # Registrar no histórico
            self.notification_history.append({
                'timestamp': datetime.now(),
                'notification_id': notification_id,
                'recipient': notification['recipient'],
                'status': notification['status'],
                'channels_used': notification['channels'],
                'delivery_time': delivery_time
            })
            
            self.notifications[notification_id] = notification
            
            self._log_operation('send_notification', notification_id, True, 
                              f'Notification sent via {len(successful_channels)} channels')
            
            return {
                'success': True,
                'notification_id': notification_id,
                'status': notification['status'],
                'delivery_results': delivery_results,
                'delivery_time': delivery_time,
                'successful_channels': successful_channels
            }
            
        except Exception as e:
            self._log_operation('send_notification', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def create_notification_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um template de notificação"""
        try:
            # Validar dados do template
            validation = self._validate_template_data(template_data)
            if not validation['valid']:
                self._log_operation('create_notification_template', 'validation', False, validation['error'])
                return validation
            
            # Gerar ID único
            template_id = self._generate_template_id()
            
            # Criar template
            template = {
                'id': template_id,
                'name': template_data['name'],
                'subject': template_data.get('subject', ''),
                'content': template_data['content'],
                'variables': template_data.get('variables', []),
                'channels': template_data.get('channels', self.notification_config['default_channels']),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'created_by': template_data.get('created_by', 'system'),
                'status': 'active',
                'version': 1,
                'metadata': template_data.get('metadata', {})
            }
            
            self.templates[template_id] = template
            
            self._log_operation('create_notification_template', template_id, True, 'Template created successfully')
            
            return {
                'success': True,
                'template_id': template_id,
                'template': template
            }
            
        except Exception as e:
            self._log_operation('create_notification_template', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def configure_notification_channel(self, channel_name: str, 
                                     channel_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configura um canal de notificação"""
        try:
            # Validar configuração do canal
            validation = self._validate_channel_config(channel_config)
            if not validation['valid']:
                self._log_operation('configure_notification_channel', channel_name, False, validation['error'])
                return validation
            
            # Configurar canal
            self.channels[channel_name] = {
                'name': channel_name,
                'config': channel_config,
                'status': 'active',
                'created_at': datetime.now(),
                'last_used': None,
                'success_count': 0,
                'failure_count': 0
            }
            
            self._log_operation('configure_notification_channel', channel_name, True, 'Channel configured successfully')
            
            return {
                'success': True,
                'channel_name': channel_name,
                'status': 'configured'
            }
            
        except Exception as e:
            self._log_operation('configure_notification_channel', channel_name, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de notificações"""
        try:
            total_notifications = len(self.notifications)
            successful_notifications = sum(1 for n in self.notifications.values() if n['status'] == 'sent')
            failed_notifications = total_notifications - successful_notifications
            
            success_rate = 0
            if total_notifications > 0:
                success_rate = successful_notifications / total_notifications
            
            avg_delivery_time = 0
            if self.system_metrics['notifications_sent'] > 0:
                avg_delivery_time = self.system_metrics['total_delivery_time'] / self.system_metrics['notifications_sent']
            
            return {
                'total_notifications': total_notifications,
                'successful_notifications': successful_notifications,
                'failed_notifications': failed_notifications,
                'success_rate': success_rate,
                'templates_used': self.system_metrics['templates_used'],
                'channels_used': self.system_metrics['channels_used'],
                'avg_delivery_time': avg_delivery_time,
                'total_delivery_time': self.system_metrics['total_delivery_time'],
                'active_channels': len([c for c in self.channels.values() if c['status'] == 'active']),
                'active_templates': len([t for t in self.templates.values() if t['status'] == 'active'])
            }
            
        except Exception as e:
            self._log_operation('get_notification_stats', 'system', False, str(e))
            return {}
    
    def _validate_notification_data(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados da notificação"""
        required_fields = ['recipient', 'content']
        
        for field in required_fields:
            if field not in notification_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not notification_data['recipient']:
            return {'valid': False, 'error': 'Recipient cannot be empty'}
        
        if not notification_data['content']:
            return {'valid': False, 'error': 'Content cannot be empty'}
        
        return {'valid': True}
    
    def _validate_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do template"""
        required_fields = ['name', 'content']
        
        for field in required_fields:
            if field not in template_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not template_data['name']:
            return {'valid': False, 'error': 'Template name cannot be empty'}
        
        if not template_data['content']:
            return {'valid': False, 'error': 'Template content cannot be empty'}
        
        return {'valid': True}
    
    def _validate_channel_config(self, channel_config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida configuração do canal"""
        if not isinstance(channel_config, dict):
            return {'valid': False, 'error': 'Channel config must be a dictionary'}
        
        if 'type' not in channel_config:
            return {'valid': False, 'error': 'Channel config must have type field'}
        
        return {'valid': True}
    
    def _process_template(self, template_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Processa template com variáveis"""
        if template_id not in self.templates:
            return {'success': False, 'error': 'Template not found'}
        
        template = self.templates[template_id]
        content = template['content']
        
        # Substituir variáveis
        for key, value in variables.items():
            placeholder = f'{{{{{key}}}}}'
            content = content.replace(placeholder, str(value))
        
        self.system_metrics['templates_used'] += 1
        
        return {
            'success': True,
            'content': content,
            'template_name': template['name']
        }
    
    def _send_via_channel(self, channel_name: str, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Envia notificação através de um canal específico"""
        try:
            channel = self.channels[channel_name]
            
            # Simular envio
            import time
            time.sleep(0.001)  # Simular processamento
            
            # Atualizar estatísticas do canal
            channel['last_used'] = datetime.now()
            channel['success_count'] += 1
            
            return {
                'success': True,
                'channel': channel_name,
                'delivery_time': notification['delivery_time'],
                'message_id': self._generate_message_id()
            }
            
        except Exception as e:
            if channel_name in self.channels:
                self.channels[channel_name]['failure_count'] += 1
            
            return {
                'success': False,
                'channel': channel_name,
                'error': str(e)
            }
    
    def _generate_notification_id(self) -> str:
        """Gera ID único para notificação"""
        import hashlib
        import uuid
        content = f"notification_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_template_id(self) -> str:
        """Gera ID único para template"""
        import hashlib
        import uuid
        content = f"template_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_message_id(self) -> str:
        """Gera ID único para mensagem"""
        import hashlib
        import uuid
        content = f"message_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] AdvancedNotificationsAPI.{operation}: {target} - {details}")


class TestAdvancedNotificationsAPI:
    """Testes para Advanced Notifications API"""
    
    @pytest.fixture
    def notification_api(self):
        """Fixture para instância da API de notificações"""
        return AdvancedNotificationsAPI()
    
    @pytest.fixture
    def sample_notification_data(self):
        """Dados de notificação de exemplo"""
        return {
            'recipient': 'user@example.com',
            'subject': 'Welcome to our platform',
            'content': 'Thank you for joining us!',
            'channels': ['email'],
            'priority': 'normal',
            'metadata': {'campaign': 'welcome'}
        }
    
    @pytest.fixture
    def sample_template_data(self):
        """Dados de template de exemplo"""
        return {
            'name': 'Welcome Template',
            'subject': 'Welcome {{user_name}}!',
            'content': 'Hello {{user_name}}, welcome to {{platform_name}}!',
            'variables': ['user_name', 'platform_name'],
            'channels': ['email', 'sms'],
            'created_by': 'system',
            'metadata': {'category': 'welcome'}
        }
    
    @pytest.fixture
    def sample_channel_config(self):
        """Configuração de canal de exemplo"""
        return {
            'type': 'email',
            'provider': 'smtp',
            'host': 'smtp.example.com',
            'port': 587,
            'username': 'noreply@example.com',
            'password': 'password123'
        }
    
    def test_send_notification_success(self, notification_api, sample_notification_data):
        """Teste de envio de notificação bem-sucedido"""
        # Arrange
        notification_data = sample_notification_data
        
        # Configurar canal primeiro
        channel_config = {
            'type': 'email',
            'provider': 'smtp'
        }
        notification_api.configure_notification_channel('email', channel_config)
        
        # Act
        result = notification_api.send_notification(notification_data)
        
        # Assert
        assert result['success'] is True
        assert 'notification_id' in result
        assert 'status' in result
        assert 'delivery_results' in result
        assert 'delivery_time' in result
        assert 'successful_channels' in result
        
        assert result['status'] == 'sent'
        assert 'email' in result['successful_channels']
        assert result['delivery_time'] > 0
    
    def test_create_notification_template(self, notification_api, sample_template_data):
        """Teste de criação de template de notificação"""
        # Arrange
        template_data = sample_template_data
        
        # Act
        result = notification_api.create_notification_template(template_data)
        
        # Assert
        assert result['success'] is True
        assert 'template_id' in result
        assert 'template' in result
        
        template = result['template']
        assert template['name'] == template_data['name']
        assert template['content'] == template_data['content']
        assert template['status'] == 'active'
        assert template['version'] == 1
        assert template['created_by'] == template_data['created_by']
    
    def test_configure_notification_channel(self, notification_api, sample_channel_config):
        """Teste de configuração de canal de notificação"""
        # Arrange
        channel_name = 'email'
        channel_config = sample_channel_config
        
        # Act
        result = notification_api.configure_notification_channel(channel_name, channel_config)
        
        # Assert
        assert result['success'] is True
        assert result['channel_name'] == channel_name
        assert result['status'] == 'configured'
        
        # Verificar se canal foi configurado
        assert channel_name in notification_api.channels
        assert notification_api.channels[channel_name]['status'] == 'active'
    
    def test_notification_edge_cases(self, notification_api):
        """Teste de casos edge do sistema de notificações"""
        # Teste com dados inválidos
        invalid_data = {'recipient': '', 'content': ''}
        result = notification_api.send_notification(invalid_data)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste com template inexistente
        notification_data = {
            'recipient': 'user@example.com',
            'content': 'Test content',
            'template_id': 'nonexistent_template'
        }
        result = notification_api.send_notification(notification_data)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste de template com dados inválidos
        invalid_template = {'name': '', 'content': ''}
        result = notification_api.create_notification_template(invalid_template)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste de canal com configuração inválida
        invalid_channel_config = {'invalid': 'config'}
        result = notification_api.configure_notification_channel('test', invalid_channel_config)
        assert result['success'] is False
        assert 'error' in result
    
    def test_notification_performance_multiple_sends(self, notification_api, sample_notification_data):
        """Teste de performance com múltiplos envios"""
        # Arrange
        notification_data = sample_notification_data
        
        # Configurar canal
        channel_config = {'type': 'email', 'provider': 'smtp'}
        notification_api.configure_notification_channel('email', channel_config)
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(20):
            notification_data['recipient'] = f'user{i}@example.com'
            result = notification_api.send_notification(notification_data)
            assert result['success'] is True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 2 segundos para 20 operações)
        assert duration < 2.0
    
    def test_notification_integration_with_templates(self, notification_api, sample_template_data, sample_channel_config):
        """Teste de integração com templates"""
        # Arrange
        # Criar template
        template_result = notification_api.create_notification_template(sample_template_data)
        template_id = template_result['template_id']
        
        # Configurar canal
        notification_api.configure_notification_channel('email', sample_channel_config)
        
        # Dados de notificação com template
        notification_data = {
            'recipient': 'user@example.com',
            'template_id': template_id,
            'variables': {
                'user_name': 'John Doe',
                'platform_name': 'Test Platform'
            },
            'channels': ['email']
        }
        
        # Act
        result = notification_api.send_notification(notification_data)
        
        # Assert
        assert result['success'] is True
        assert result['status'] == 'sent'
        
        # Verificar se template foi processado
        notification = notification_api.notifications[result['notification_id']]
        assert 'John Doe' in notification['content']
        assert 'Test Platform' in notification['content']
    
    def test_notification_configuration_validation(self, notification_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert notification_api.notification_config['max_retries'] == 3
        assert notification_api.notification_config['retry_delay'] == 60
        assert notification_api.notification_config['rate_limit'] == 1000
        assert notification_api.notification_config['enable_templates'] is True
        assert 'email' in notification_api.notification_config['default_channels']
        
        # Teste de configuração customizada
        custom_config = {
            'max_retries': 5,
            'retry_delay': 120,
            'rate_limit': 500,
            'enable_templates': False,
            'default_channels': ['sms']
        }
        custom_api = AdvancedNotificationsAPI(custom_config)
        
        assert custom_api.notification_config['max_retries'] == 5
        assert custom_api.notification_config['retry_delay'] == 120
        assert custom_api.notification_config['rate_limit'] == 500
        assert custom_api.notification_config['enable_templates'] is False
        assert custom_api.notification_config['default_channels'] == ['sms']
    
    def test_notification_logs_operation_tracking(self, notification_api, sample_notification_data, capsys):
        """Teste de logs de operações do sistema"""
        # Arrange
        channel_config = {'type': 'email', 'provider': 'smtp'}
        notification_api.configure_notification_channel('email', channel_config)
        
        # Act
        notification_api.send_notification(sample_notification_data)
        notification_api.create_notification_template({'name': 'Test', 'content': 'Test content'})
        notification_api.get_notification_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "AdvancedNotificationsAPI.send_notification" in log_output
        assert "AdvancedNotificationsAPI.create_notification_template" in log_output
        assert "AdvancedNotificationsAPI.get_notification_stats" in log_output
        assert "INFO" in log_output
    
    def test_notification_metrics_collection(self, notification_api, sample_notification_data):
        """Teste de coleta de métricas do sistema"""
        # Arrange
        initial_stats = notification_api.get_notification_stats()
        
        # Configurar canal
        channel_config = {'type': 'email', 'provider': 'smtp'}
        notification_api.configure_notification_channel('email', channel_config)
        
        # Act - Simular uso do sistema
        notification_api.send_notification(sample_notification_data)
        notification_api.create_notification_template({'name': 'Test', 'content': 'Test content'})
        
        # Enviar mais algumas notificações
        for i in range(3):
            notification_data = sample_notification_data.copy()
            notification_data['recipient'] = f'user{i}@example.com'
            notification_api.send_notification(notification_data)
        
        # Assert
        final_stats = notification_api.get_notification_stats()
        
        assert final_stats['total_notifications'] == 4
        assert final_stats['successful_notifications'] == 4
        assert final_stats['failed_notifications'] == 0
        assert final_stats['success_rate'] == 1.0
        assert final_stats['templates_used'] == 0  # Não usamos templates
        assert final_stats['channels_used'] == 4  # 4 notificações via email
        assert final_stats['avg_delivery_time'] > 0
        assert final_stats['active_channels'] == 1
        assert final_stats['active_templates'] == 1
    
    def test_notification_reports_generation(self, notification_api, sample_notification_data):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        # Configurar canais
        channels = ['email', 'sms']
        for channel in channels:
            config = {'type': channel, 'provider': 'test'}
            notification_api.configure_notification_channel(channel, config)
        
        # Criar templates
        for i in range(3):
            template_data = {
                'name': f'Template {i}',
                'content': f'Content for template {i} with {{variable}}',
                'variables': ['variable']
            }
            notification_api.create_notification_template(template_data)
        
        # Enviar notificações
        for i in range(10):
            notification_data = sample_notification_data.copy()
            notification_data['recipient'] = f'user{i}@example.com'
            notification_data['channels'] = ['email'] if i % 2 == 0 else ['sms']
            notification_api.send_notification(notification_data)
        
        # Act
        report = notification_api.get_notification_stats()
        
        # Assert
        assert 'total_notifications' in report
        assert 'successful_notifications' in report
        assert 'failed_notifications' in report
        assert 'success_rate' in report
        assert 'templates_used' in report
        assert 'channels_used' in report
        assert 'avg_delivery_time' in report
        assert 'total_delivery_time' in report
        assert 'active_channels' in report
        assert 'active_templates' in report
        
        # Verificar valores específicos
        assert report['total_notifications'] == 10
        assert report['successful_notifications'] == 10
        assert report['failed_notifications'] == 0
        assert report['success_rate'] == 1.0
        assert report['channels_used'] == 10
        assert report['active_channels'] == 2
        assert report['active_templates'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 