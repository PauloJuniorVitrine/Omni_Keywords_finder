"""
Testes unitários para Feature Requests API
Cobertura: Criação de solicitações, acompanhamento, votação, métricas
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Feature Requests API
class FeatureRequestsAPI:
    """API para gerenciamento de solicitações de features"""
    
    def __init__(self, requests_config: Dict[str, Any] = None):
        self.requests_config = requests_config or {
            'max_title_length': 200,
            'max_description_length': 2000,
            'enable_voting': True,
            'max_votes_per_user': 10,
            'auto_archive_days': 365,
            'require_authentication': True
        }
        self.feature_requests = {}
        self.votes = {}
        self.comments = {}
        self.request_history = []
        self.system_metrics = {
            'requests_created': 0,
            'requests_approved': 0,
            'requests_rejected': 0,
            'total_votes': 0,
            'total_comments': 0,
            'unique_voters': 0
        }
    
    def create_feature_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova solicitação de feature"""
        try:
            # Validar dados da solicitação
            validation = self._validate_request_data(request_data)
            if not validation['valid']:
                self._log_operation('create_feature_request', 'validation', False, validation['error'])
                return validation
            
            # Gerar ID único
            request_id = self._generate_request_id()
            
            # Criar solicitação
            feature_request = {
                'id': request_id,
                'title': request_data['title'],
                'description': request_data['description'],
                'category': request_data.get('category', 'general'),
                'priority': request_data.get('priority', 'medium'),
                'created_by': request_data['created_by'],
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'status': 'open',
                'votes_count': 0,
                'comments_count': 0,
                'tags': request_data.get('tags', []),
                'attachments': request_data.get('attachments', []),
                'estimated_effort': request_data.get('estimated_effort'),
                'business_value': request_data.get('business_value'),
                'metadata': request_data.get('metadata', {})
            }
            
            self.feature_requests[request_id] = feature_request
            
            # Inicializar estruturas de dados relacionadas
            self.votes[request_id] = []
            self.comments[request_id] = []
            
            # Registrar no histórico
            self.request_history.append({
                'timestamp': datetime.now(),
                'request_id': request_id,
                'operation': 'create',
                'user_id': request_data['created_by']
            })
            
            self.system_metrics['requests_created'] += 1
            
            self._log_operation('create_feature_request', request_id, True, 'Feature request created successfully')
            
            return {
                'success': True,
                'request_id': request_id,
                'feature_request': feature_request
            }
            
        except Exception as e:
            self._log_operation('create_feature_request', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def vote_feature_request(self, request_id: str, user_id: str, 
                           vote_type: str = 'upvote', context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Vota em uma solicitação de feature"""
        try:
            # Verificar se solicitação existe
            if request_id not in self.feature_requests:
                self._log_operation('vote_feature_request', request_id, False, 'Feature request not found')
                return {'success': False, 'error': 'Feature request not found'}
            
            feature_request = self.feature_requests[request_id]
            
            # Verificar se solicitação está aberta
            if feature_request['status'] != 'open':
                self._log_operation('vote_feature_request', request_id, False, 'Feature request is not open for voting')
                return {'success': False, 'error': 'Feature request is not open for voting'}
            
            # Verificar limite de votos por usuário
            user_votes = [v for v in self.votes[request_id] if v['user_id'] == user_id]
            if len(user_votes) >= self.requests_config['max_votes_per_user']:
                self._log_operation('vote_feature_request', request_id, False, 'User has reached vote limit')
                return {'success': False, 'error': 'User has reached vote limit'}
            
            # Validar tipo de voto
            valid_vote_types = ['upvote', 'downvote']
            if vote_type not in valid_vote_types:
                self._log_operation('vote_feature_request', request_id, False, 'Invalid vote type')
                return {'success': False, 'error': 'Invalid vote type'}
            
            # Criar voto
            vote = {
                'id': self._generate_vote_id(),
                'request_id': request_id,
                'user_id': user_id,
                'vote_type': vote_type,
                'created_at': datetime.now(),
                'context': context or {}
            }
            
            self.votes[request_id].append(vote)
            
            # Atualizar contadores
            feature_request['votes_count'] += 1
            feature_request['updated_at'] = datetime.now()
            
            # Atualizar métricas
            self.system_metrics['total_votes'] += 1
            
            # Verificar se é um novo votante
            unique_voters = set(v['user_id'] for v in self.votes[request_id])
            if len(unique_voters) > self.system_metrics['unique_voters']:
                self.system_metrics['unique_voters'] = len(unique_voters)
            
            self._log_operation('vote_feature_request', request_id, True, f'Vote recorded: {vote_type}')
            
            return {
                'success': True,
                'vote_id': vote['id'],
                'request_id': request_id,
                'vote_type': vote_type,
                'votes_count': feature_request['votes_count']
            }
            
        except Exception as e:
            self._log_operation('vote_feature_request', request_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def update_feature_request_status(self, request_id: str, new_status: str, 
                                    reason: str = None, updated_by: str = None) -> Dict[str, Any]:
        """Atualiza status de uma solicitação de feature"""
        try:
            # Verificar se solicitação existe
            if request_id not in self.feature_requests:
                self._log_operation('update_feature_request_status', request_id, False, 'Feature request not found')
                return {'success': False, 'error': 'Feature request not found'}
            
            feature_request = self.feature_requests[request_id]
            old_status = feature_request['status']
            
            # Validar novo status
            valid_statuses = ['open', 'in_progress', 'approved', 'rejected', 'completed', 'archived']
            if new_status not in valid_statuses:
                self._log_operation('update_feature_request_status', request_id, False, 'Invalid status')
                return {'success': False, 'error': 'Invalid status'}
            
            # Atualizar status
            feature_request['status'] = new_status
            feature_request['updated_at'] = datetime.now()
            
            # Registrar mudança no histórico
            self.request_history.append({
                'timestamp': datetime.now(),
                'request_id': request_id,
                'operation': 'status_update',
                'user_id': updated_by or 'system',
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason
            })
            
            # Atualizar métricas
            if new_status == 'approved':
                self.system_metrics['requests_approved'] += 1
            elif new_status == 'rejected':
                self.system_metrics['requests_rejected'] += 1
            
            self._log_operation('update_feature_request_status', request_id, True, f'Status updated: {old_status} -> {new_status}')
            
            return {
                'success': True,
                'request_id': request_id,
                'old_status': old_status,
                'new_status': new_status,
                'updated_at': feature_request['updated_at'].isoformat(),
                'reason': reason
            }
            
        except Exception as e:
            self._log_operation('update_feature_request_status', request_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_feature_requests_summary(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retorna resumo das solicitações de features"""
        try:
            filters = filters or {}
            
            # Aplicar filtros
            filtered_requests = self._apply_filters(self.feature_requests, filters)
            
            # Calcular estatísticas
            total_requests = len(filtered_requests)
            status_counts = {}
            category_counts = {}
            priority_counts = {}
            
            total_votes = 0
            total_comments = 0
            
            for request in filtered_requests.values():
                status = request['status']
                category = request['category']
                priority = request['priority']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                total_votes += request['votes_count']
                total_comments += request['comments_count']
            
            # Calcular métricas de engajamento
            engagement_metrics = self._calculate_engagement_metrics(filtered_requests)
            
            summary = {
                'total_requests': total_requests,
                'status_distribution': status_counts,
                'category_distribution': category_counts,
                'priority_distribution': priority_counts,
                'total_votes': total_votes,
                'total_comments': total_comments,
                'engagement_metrics': engagement_metrics,
                'last_updated': datetime.now().isoformat(),
                'filters_applied': filters
            }
            
            self._log_operation('get_feature_requests_summary', 'system', True, f'Summary generated for {total_requests} requests')
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            self._log_operation('get_feature_requests_summary', 'system', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_feature_request_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das solicitações de features"""
        try:
            total_requests = len(self.feature_requests)
            open_requests = sum(1 for r in self.feature_requests.values() if r['status'] == 'open')
            approved_requests = sum(1 for r in self.feature_requests.values() if r['status'] == 'approved')
            
            # Calcular métricas de tempo
            avg_processing_time = self._calculate_avg_processing_time()
            
            # Calcular métricas de engajamento
            avg_votes_per_request = 0
            if total_requests > 0:
                total_votes = sum(r['votes_count'] for r in self.feature_requests.values())
                avg_votes_per_request = total_votes / total_requests
            
            return {
                'total_requests': total_requests,
                'open_requests': open_requests,
                'approved_requests': approved_requests,
                'requests_created': self.system_metrics['requests_created'],
                'requests_approved': self.system_metrics['requests_approved'],
                'requests_rejected': self.system_metrics['requests_rejected'],
                'total_votes': self.system_metrics['total_votes'],
                'total_comments': self.system_metrics['total_comments'],
                'unique_voters': self.system_metrics['unique_voters'],
                'avg_votes_per_request': avg_votes_per_request,
                'avg_processing_time': avg_processing_time,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_operation('get_feature_request_stats', 'system', False, str(e))
            return {}
    
    def _validate_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados da solicitação"""
        required_fields = ['title', 'description', 'created_by']
        
        for field in required_fields:
            if field not in request_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not request_data['title']:
            return {'valid': False, 'error': 'Title cannot be empty'}
        
        if len(request_data['title']) > self.requests_config['max_title_length']:
            return {'valid': False, 'error': f'Title too long (max {self.requests_config["max_title_length"]} chars)'}
        
        if not request_data['description']:
            return {'valid': False, 'error': 'Description cannot be empty'}
        
        if len(request_data['description']) > self.requests_config['max_description_length']:
            return {'valid': False, 'error': f'Description too long (max {self.requests_config["max_description_length"]} chars)'}
        
        if not request_data['created_by']:
            return {'valid': False, 'error': 'Created by cannot be empty'}
        
        return {'valid': True}
    
    def _apply_filters(self, requests: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica filtros às solicitações"""
        filtered = requests.copy()
        
        if 'status' in filters:
            filtered = {k: v for k, v in filtered.items() if v['status'] == filters['status']}
        
        if 'category' in filters:
            filtered = {k: v for k, v in filtered.items() if v['category'] == filters['category']}
        
        if 'priority' in filters:
            filtered = {k: v for k, v in filtered.items() if v['priority'] == filters['priority']}
        
        if 'created_by' in filters:
            filtered = {k: v for k, v in filtered.items() if v['created_by'] == filters['created_by']}
        
        return filtered
    
    def _calculate_engagement_metrics(self, requests: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de engajamento"""
        if not requests:
            return {
                'avg_votes_per_request': 0,
                'avg_comments_per_request': 0,
                'most_voted_request': None,
                'engagement_rate': 0
            }
        
        total_votes = sum(r['votes_count'] for r in requests.values())
        total_comments = sum(r['comments_count'] for r in requests.values())
        
        avg_votes = total_votes / len(requests)
        avg_comments = total_comments / len(requests)
        
        # Encontrar solicitação mais votada
        most_voted = max(requests.values(), key=lambda x: x['votes_count'])
        
        # Calcular taxa de engajamento (solicitações com pelo menos 1 voto)
        engaged_requests = sum(1 for r in requests.values() if r['votes_count'] > 0)
        engagement_rate = engaged_requests / len(requests)
        
        return {
            'avg_votes_per_request': avg_votes,
            'avg_comments_per_request': avg_comments,
            'most_voted_request': {
                'id': most_voted['id'],
                'title': most_voted['title'],
                'votes_count': most_voted['votes_count']
            },
            'engagement_rate': engagement_rate
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calcula tempo médio de processamento"""
        completed_requests = [r for r in self.feature_requests.values() 
                            if r['status'] in ['approved', 'rejected', 'completed']]
        
        if not completed_requests:
            return 0.0
        
        total_time = 0
        for request in completed_requests:
            # Encontrar quando o status foi alterado pela última vez
            status_changes = [h for h in self.request_history 
                            if h['request_id'] == request['id'] and h['operation'] == 'status_update']
            
            if status_changes:
                last_change = max(status_changes, key=lambda x: x['timestamp'])
                processing_time = (last_change['timestamp'] - request['created_at']).total_seconds()
                total_time += processing_time
        
        return total_time / len(completed_requests)
    
    def _generate_request_id(self) -> str:
        """Gera ID único para solicitação"""
        import hashlib
        import uuid
        content = f"request_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_vote_id(self) -> str:
        """Gera ID único para voto"""
        import hashlib
        import uuid
        content = f"vote_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] FeatureRequestsAPI.{operation}: {target} - {details}")


class TestFeatureRequestsAPI:
    """Testes para Feature Requests API"""
    
    @pytest.fixture
    def requests_api(self):
        """Fixture para instância da API de solicitações"""
        return FeatureRequestsAPI()
    
    @pytest.fixture
    def sample_request_data(self):
        """Dados de solicitação de exemplo"""
        return {
            'title': 'Dark Mode Support',
            'description': 'Add dark mode theme option to improve user experience in low-light environments',
            'category': 'ui_ux',
            'priority': 'high',
            'created_by': 'user_123',
            'tags': ['ui', 'theme', 'accessibility'],
            'estimated_effort': 'medium',
            'business_value': 'high',
            'metadata': {'platform': 'web', 'browser_support': 'all'}
        }
    
    @pytest.fixture
    def sample_vote_data(self):
        """Dados de voto de exemplo"""
        return {
            'user_id': 'voter_456',
            'vote_type': 'upvote',
            'context': {'source': 'web', 'session_id': 'session_789'}
        }
    
    def test_create_feature_request_success(self, requests_api, sample_request_data):
        """Teste de criação de solicitação bem-sucedido"""
        # Arrange
        request_data = sample_request_data
        
        # Act
        result = requests_api.create_feature_request(request_data)
        
        # Assert
        assert result['success'] is True
        assert 'request_id' in result
        assert 'feature_request' in result
        
        feature_request = result['feature_request']
        assert feature_request['title'] == request_data['title']
        assert feature_request['description'] == request_data['description']
        assert feature_request['category'] == request_data['category']
        assert feature_request['priority'] == request_data['priority']
        assert feature_request['created_by'] == request_data['created_by']
        assert feature_request['status'] == 'open'
        assert feature_request['votes_count'] == 0
        assert feature_request['comments_count'] == 0
    
    def test_vote_feature_request_success(self, requests_api, sample_request_data, sample_vote_data):
        """Teste de votação bem-sucedido"""
        # Arrange
        create_result = requests_api.create_feature_request(sample_request_data)
        request_id = create_result['request_id']
        vote_data = sample_vote_data
        
        # Act
        result = requests_api.vote_feature_request(request_id, vote_data['user_id'], vote_data['vote_type'])
        
        # Assert
        assert result['success'] is True
        assert 'vote_id' in result
        assert result['request_id'] == request_id
        assert result['vote_type'] == vote_data['vote_type']
        assert result['votes_count'] == 1
        
        # Verificar se voto foi registrado
        assert request_id in requests_api.votes
        assert len(requests_api.votes[request_id]) == 1
        
        # Verificar se contadores foram atualizados
        feature_request = requests_api.feature_requests[request_id]
        assert feature_request['votes_count'] == 1
    
    def test_update_feature_request_status(self, requests_api, sample_request_data):
        """Teste de atualização de status"""
        # Arrange
        create_result = requests_api.create_feature_request(sample_request_data)
        request_id = create_result['request_id']
        new_status = 'approved'
        reason = 'High user demand and business value'
        
        # Act
        result = requests_api.update_feature_request_status(request_id, new_status, reason, 'admin_001')
        
        # Assert
        assert result['success'] is True
        assert result['request_id'] == request_id
        assert result['old_status'] == 'open'
        assert result['new_status'] == new_status
        assert result['reason'] == reason
        
        # Verificar se status foi atualizado
        feature_request = requests_api.feature_requests[request_id]
        assert feature_request['status'] == new_status
        
        # Verificar se métricas foram atualizadas
        assert requests_api.system_metrics['requests_approved'] == 1
    
    def test_requests_edge_cases(self, requests_api):
        """Teste de casos edge do sistema de solicitações"""
        # Teste com dados inválidos
        invalid_request = {'title': '', 'description': '', 'created_by': ''}
        result = requests_api.create_feature_request(invalid_request)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste com título muito longo
        long_title = 'x' * 250  # Excede limite de 200
        long_request = {
            'title': long_title,
            'description': 'Valid description',
            'created_by': 'user_123'
        }
        result = requests_api.create_feature_request(long_request)
        assert result['success'] is False
        assert 'too long' in result['error']
        
        # Teste de voto em solicitação inexistente
        result = requests_api.vote_feature_request('nonexistent_id', 'user_123')
        assert result['success'] is False
        assert result['error'] == 'Feature request not found'
        
        # Teste de voto inválido
        create_result = requests_api.create_feature_request({
            'title': 'Test Request',
            'description': 'Test description',
            'created_by': 'user_123'
        })
        request_id = create_result['request_id']
        
        result = requests_api.vote_feature_request(request_id, 'user_123', 'invalid_vote')
        assert result['success'] is False
        assert result['error'] == 'Invalid vote type'
    
    def test_requests_performance_large_scale(self, requests_api):
        """Teste de performance em larga escala"""
        # Arrange
        request_data = {
            'title': 'Performance Test Request',
            'description': 'Test description for performance',
            'created_by': 'test_user'
        }
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(50):
            request_data['title'] = f'Request {i}'
            request_data['created_by'] = f'user_{i}'
            
            result = requests_api.create_feature_request(request_data)
            assert result['success'] is True
            
            request_id = result['request_id']
            
            # Adicionar alguns votos
            for j in range(3):
                requests_api.vote_feature_request(request_id, f'voter_{i}_{j}')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 3 segundos para 200 operações)
        assert duration < 3.0
        
        # Verificar se todas as solicitações foram criadas
        assert len(requests_api.feature_requests) == 50
        assert requests_api.system_metrics['requests_created'] == 50
        assert requests_api.system_metrics['total_votes'] == 150  # 50 * 3
    
    def test_requests_integration_with_voting(self, requests_api, sample_request_data):
        """Teste de integração com sistema de votação"""
        # Arrange
        create_result = requests_api.create_feature_request(sample_request_data)
        request_id = create_result['request_id']
        
        # Adicionar múltiplos votos
        voters = ['user_1', 'user_2', 'user_3', 'user_4', 'user_5']
        for voter in voters:
            result = requests_api.vote_feature_request(request_id, voter, 'upvote')
            assert result['success'] is True
        
        # Tentar votar novamente (deve falhar por limite)
        result = requests_api.vote_feature_request(request_id, 'user_1', 'upvote')
        assert result['success'] is False
        assert 'vote limit' in result['error']
        
        # Verificar estatísticas
        feature_request = requests_api.feature_requests[request_id]
        assert feature_request['votes_count'] == 5
        
        # Verificar votantes únicos
        assert requests_api.system_metrics['unique_voters'] == 5
    
    def test_requests_configuration_validation(self, requests_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert requests_api.requests_config['max_title_length'] == 200
        assert requests_api.requests_config['max_description_length'] == 2000
        assert requests_api.requests_config['enable_voting'] is True
        assert requests_api.requests_config['max_votes_per_user'] == 10
        assert requests_api.requests_config['auto_archive_days'] == 365
        assert requests_api.requests_config['require_authentication'] is True
        
        # Teste de configuração customizada
        custom_config = {
            'max_title_length': 100,
            'max_description_length': 1000,
            'enable_voting': False,
            'max_votes_per_user': 5,
            'auto_archive_days': 180,
            'require_authentication': False
        }
        custom_api = FeatureRequestsAPI(custom_config)
        
        assert custom_api.requests_config['max_title_length'] == 100
        assert custom_api.requests_config['max_description_length'] == 1000
        assert custom_api.requests_config['enable_voting'] is False
        assert custom_api.requests_config['max_votes_per_user'] == 5
        assert custom_api.requests_config['auto_archive_days'] == 180
        assert custom_api.requests_config['require_authentication'] is False
    
    def test_requests_logs_operation_tracking(self, requests_api, sample_request_data, capsys):
        """Teste de logs de operações do sistema"""
        # Act
        requests_api.create_feature_request(sample_request_data)
        requests_api.get_feature_requests_summary()
        requests_api.get_feature_request_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "FeatureRequestsAPI.create_feature_request" in log_output
        assert "FeatureRequestsAPI.get_feature_requests_summary" in log_output
        assert "FeatureRequestsAPI.get_feature_request_stats" in log_output
        assert "INFO" in log_output
    
    def test_requests_metrics_collection(self, requests_api, sample_request_data):
        """Teste de coleta de métricas do sistema"""
        # Arrange
        initial_stats = requests_api.get_feature_request_stats()
        
        # Act - Simular uso do sistema
        create_result = requests_api.create_feature_request(sample_request_data)
        request_id = create_result['request_id']
        
        # Adicionar votos
        for i in range(3):
            requests_api.vote_feature_request(request_id, f'voter_{i}')
        
        # Atualizar status
        requests_api.update_feature_request_status(request_id, 'approved', 'High priority')
        
        # Assert
        final_stats = requests_api.get_feature_request_stats()
        
        assert final_stats['total_requests'] == 1
        assert final_stats['open_requests'] == 0
        assert final_stats['approved_requests'] == 1
        assert final_stats['requests_created'] == 1
        assert final_stats['requests_approved'] == 1
        assert final_stats['total_votes'] == 3
        assert final_stats['unique_voters'] == 3
        assert final_stats['avg_votes_per_request'] == 3.0
    
    def test_requests_reports_generation(self, requests_api, sample_request_data):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        categories = ['ui_ux', 'backend', 'mobile', 'security']
        priorities = ['low', 'medium', 'high']
        statuses = ['open', 'in_progress', 'approved', 'rejected']
        
        for i in range(10):
            request_data = sample_request_data.copy()
            request_data['title'] = f'Feature Request {i+1}'
            request_data['category'] = categories[i % len(categories)]
            request_data['priority'] = priorities[i % len(priorities)]
            request_data['created_by'] = f'user_{i}'
            
            create_result = requests_api.create_feature_request(request_data)
            request_id = create_result['request_id']
            
            # Adicionar votos
            for j in range(i + 1):  # Variação no número de votos
                requests_api.vote_feature_request(request_id, f'voter_{i}_{j}')
            
            # Atualizar alguns statuses
            if i % 3 == 0:
                requests_api.update_feature_request_status(request_id, 'approved', 'Approved')
            elif i % 3 == 1:
                requests_api.update_feature_request_status(request_id, 'rejected', 'Rejected')
        
        # Act
        summary_result = requests_api.get_feature_requests_summary()
        stats_result = requests_api.get_feature_request_stats()
        
        # Assert
        assert summary_result['success'] is True
        assert stats_result['total_requests'] == 10
        
        summary = summary_result['summary']
        assert 'total_requests' in summary
        assert 'status_distribution' in summary
        assert 'category_distribution' in summary
        assert 'priority_distribution' in summary
        assert 'total_votes' in summary
        assert 'engagement_metrics' in summary
        
        # Verificar valores específicos
        assert summary['total_requests'] == 10
        assert summary['status_distribution']['open'] == 4  # 10 - 3 approved - 3 rejected
        assert summary['status_distribution']['approved'] == 3
        assert summary['status_distribution']['rejected'] == 3
        assert summary['total_votes'] == 55  # Soma de 1+2+3+...+10
        assert summary['engagement_metrics']['avg_votes_per_request'] == 5.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 