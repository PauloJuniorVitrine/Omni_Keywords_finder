"""
Testes unitários para Bug Reports API
Cobertura: Criação de relatórios, acompanhamento, priorização, métricas
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Bug Reports API
class BugReportsAPI:
    """API para gerenciamento de relatórios de bugs"""
    
    def __init__(self, reports_config: Dict[str, Any] = None):
        self.reports_config = reports_config or {
            'max_title_length': 200,
            'max_description_length': 5000,
            'enable_attachments': True,
            'max_attachments': 5,
            'auto_assign': True,
            'require_screenshots': False
        }
        self.bug_reports = {}
        self.comments = {}
        self.assignments = {}
        self.report_history = []
        self.system_metrics = {
            'reports_created': 0,
            'reports_resolved': 0,
            'reports_closed': 0,
            'total_comments': 0,
            'avg_resolution_time': 0,
            'critical_bugs': 0
        }
    
    def create_bug_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo relatório de bug"""
        try:
            # Validar dados do relatório
            validation = self._validate_report_data(report_data)
            if not validation['valid']:
                self._log_operation('create_bug_report', 'validation', False, validation['error'])
                return validation
            
            # Gerar ID único
            report_id = self._generate_report_id()
            
            # Calcular prioridade baseada em critérios
            priority = self._calculate_priority(report_data)
            
            # Criar relatório
            bug_report = {
                'id': report_id,
                'title': report_data['title'],
                'description': report_data['description'],
                'severity': report_data.get('severity', 'medium'),
                'priority': priority,
                'category': report_data.get('category', 'general'),
                'reported_by': report_data['reported_by'],
                'reported_at': datetime.now(),
                'updated_at': datetime.now(),
                'status': 'open',
                'assigned_to': None,
                'comments_count': 0,
                'attachments': report_data.get('attachments', []),
                'environment': report_data.get('environment', {}),
                'steps_to_reproduce': report_data.get('steps_to_reproduce', []),
                'expected_behavior': report_data.get('expected_behavior', ''),
                'actual_behavior': report_data.get('actual_behavior', ''),
                'metadata': report_data.get('metadata', {})
            }
            
            self.bug_reports[report_id] = bug_report
            
            # Inicializar estruturas relacionadas
            self.comments[report_id] = []
            self.assignments[report_id] = []
            
            # Auto-assign se configurado
            if self.reports_config['auto_assign']:
                assigned_to = self._auto_assign_bug(report_id, priority)
                if assigned_to:
                    bug_report['assigned_to'] = assigned_to
                    self._record_assignment(report_id, assigned_to, 'auto')
            
            # Registrar no histórico
            self.report_history.append({
                'timestamp': datetime.now(),
                'report_id': report_id,
                'operation': 'create',
                'user_id': report_data['reported_by']
            })
            
            # Atualizar métricas
            self.system_metrics['reports_created'] += 1
            if priority == 'critical':
                self.system_metrics['critical_bugs'] += 1
            
            self._log_operation('create_bug_report', report_id, True, 'Bug report created successfully')
            
            return {
                'success': True,
                'report_id': report_id,
                'bug_report': bug_report
            }
            
        except Exception as e:
            self._log_operation('create_bug_report', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def update_bug_status(self, report_id: str, new_status: str, 
                         updated_by: str, notes: str = None) -> Dict[str, Any]:
        """Atualiza status de um relatório de bug"""
        try:
            # Verificar se relatório existe
            if report_id not in self.bug_reports:
                self._log_operation('update_bug_status', report_id, False, 'Bug report not found')
                return {'success': False, 'error': 'Bug report not found'}
            
            bug_report = self.bug_reports[report_id]
            old_status = bug_report['status']
            
            # Validar novo status
            valid_statuses = ['open', 'in_progress', 'testing', 'resolved', 'closed', 'duplicate']
            if new_status not in valid_statuses:
                self._log_operation('update_bug_status', report_id, False, 'Invalid status')
                return {'success': False, 'error': 'Invalid status'}
            
            # Atualizar status
            bug_report['status'] = new_status
            bug_report['updated_at'] = datetime.now()
            
            # Calcular tempo de resolução se aplicável
            if new_status in ['resolved', 'closed'] and old_status not in ['resolved', 'closed']:
                resolution_time = (bug_report['updated_at'] - bug_report['reported_at']).total_seconds()
                self._update_resolution_metrics(resolution_time)
            
            # Registrar mudança no histórico
            self.report_history.append({
                'timestamp': datetime.now(),
                'report_id': report_id,
                'operation': 'status_update',
                'user_id': updated_by,
                'old_status': old_status,
                'new_status': new_status,
                'notes': notes
            })
            
            # Atualizar métricas
            if new_status == 'resolved':
                self.system_metrics['reports_resolved'] += 1
            elif new_status == 'closed':
                self.system_metrics['reports_closed'] += 1
            
            self._log_operation('update_bug_status', report_id, True, f'Status updated: {old_status} -> {new_status}')
            
            return {
                'success': True,
                'report_id': report_id,
                'old_status': old_status,
                'new_status': new_status,
                'updated_at': bug_report['updated_at'].isoformat(),
                'notes': notes
            }
            
        except Exception as e:
            self._log_operation('update_bug_status', report_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def assign_bug_report(self, report_id: str, assignee: str, 
                         assigned_by: str, reason: str = None) -> Dict[str, Any]:
        """Atribui um relatório de bug a um desenvolvedor"""
        try:
            # Verificar se relatório existe
            if report_id not in self.bug_reports:
                self._log_operation('assign_bug_report', report_id, False, 'Bug report not found')
                return {'success': False, 'error': 'Bug report not found'}
            
            bug_report = self.bug_reports[report_id]
            old_assignee = bug_report['assigned_to']
            
            # Atualizar atribuição
            bug_report['assigned_to'] = assignee
            bug_report['updated_at'] = datetime.now()
            
            # Registrar atribuição
            self._record_assignment(report_id, assignee, 'manual', assigned_by, reason)
            
            self._log_operation('assign_bug_report', report_id, True, f'Assigned to: {assignee}')
            
            return {
                'success': True,
                'report_id': report_id,
                'old_assignee': old_assignee,
                'new_assignee': assignee,
                'assigned_by': assigned_by,
                'assigned_at': bug_report['updated_at'].isoformat(),
                'reason': reason
            }
            
        except Exception as e:
            self._log_operation('assign_bug_report', report_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def add_comment_to_bug(self, report_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona comentário a um relatório de bug"""
        try:
            # Verificar se relatório existe
            if report_id not in self.bug_reports:
                self._log_operation('add_comment_to_bug', report_id, False, 'Bug report not found')
                return {'success': False, 'error': 'Bug report not found'}
            
            # Validar dados do comentário
            if 'content' not in comment_data or not comment_data['content']:
                self._log_operation('add_comment_to_bug', report_id, False, 'Comment content is required')
                return {'success': False, 'error': 'Comment content is required'}
            
            # Criar comentário
            comment = {
                'id': self._generate_comment_id(),
                'report_id': report_id,
                'content': comment_data['content'],
                'author': comment_data['author'],
                'created_at': datetime.now(),
                'is_internal': comment_data.get('is_internal', False),
                'attachments': comment_data.get('attachments', [])
            }
            
            self.comments[report_id].append(comment)
            
            # Atualizar contador
            bug_report = self.bug_reports[report_id]
            bug_report['comments_count'] += 1
            bug_report['updated_at'] = datetime.now()
            
            # Atualizar métricas
            self.system_metrics['total_comments'] += 1
            
            self._log_operation('add_comment_to_bug', report_id, True, f'Comment added by {comment_data["author"]}')
            
            return {
                'success': True,
                'comment_id': comment['id'],
                'report_id': report_id,
                'created_at': comment['created_at'].isoformat()
            }
            
        except Exception as e:
            self._log_operation('add_comment_to_bug', report_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_bug_reports_summary(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retorna resumo dos relatórios de bugs"""
        try:
            filters = filters or {}
            
            # Aplicar filtros
            filtered_reports = self._apply_filters(self.bug_reports, filters)
            
            # Calcular estatísticas
            total_reports = len(filtered_reports)
            status_counts = {}
            severity_counts = {}
            priority_counts = {}
            
            total_comments = 0
            avg_resolution_time = 0
            
            for report in filtered_reports.values():
                status = report['status']
                severity = report['severity']
                priority = report['priority']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                total_comments += report['comments_count']
            
            # Calcular métricas de performance
            performance_metrics = self._calculate_performance_metrics(filtered_reports)
            
            summary = {
                'total_reports': total_reports,
                'status_distribution': status_counts,
                'severity_distribution': severity_counts,
                'priority_distribution': priority_counts,
                'total_comments': total_comments,
                'performance_metrics': performance_metrics,
                'last_updated': datetime.now().isoformat(),
                'filters_applied': filters
            }
            
            self._log_operation('get_bug_reports_summary', 'system', True, f'Summary generated for {total_reports} reports')
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            self._log_operation('get_bug_reports_summary', 'system', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_bug_report_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos relatórios de bugs"""
        try:
            total_reports = len(self.bug_reports)
            open_reports = sum(1 for r in self.bug_reports.values() if r['status'] == 'open')
            resolved_reports = sum(1 for r in self.bug_reports.values() if r['status'] == 'resolved')
            
            # Calcular métricas de tempo
            avg_resolution_time = self.system_metrics['avg_resolution_time']
            
            # Calcular métricas de qualidade
            resolution_rate = 0
            if total_reports > 0:
                resolution_rate = (resolved_reports + self.system_metrics['reports_closed']) / total_reports
            
            return {
                'total_reports': total_reports,
                'open_reports': open_reports,
                'resolved_reports': resolved_reports,
                'reports_created': self.system_metrics['reports_created'],
                'reports_resolved': self.system_metrics['reports_resolved'],
                'reports_closed': self.system_metrics['reports_closed'],
                'total_comments': self.system_metrics['total_comments'],
                'critical_bugs': self.system_metrics['critical_bugs'],
                'avg_resolution_time': avg_resolution_time,
                'resolution_rate': resolution_rate,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_operation('get_bug_report_stats', 'system', False, str(e))
            return {}
    
    def _validate_report_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do relatório"""
        required_fields = ['title', 'description', 'reported_by']
        
        for field in required_fields:
            if field not in report_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not report_data['title']:
            return {'valid': False, 'error': 'Title cannot be empty'}
        
        if len(report_data['title']) > self.reports_config['max_title_length']:
            return {'valid': False, 'error': f'Title too long (max {self.reports_config["max_title_length"]} chars)'}
        
        if not report_data['description']:
            return {'valid': False, 'error': 'Description cannot be empty'}
        
        if len(report_data['description']) > self.reports_config['max_description_length']:
            return {'valid': False, 'error': f'Description too long (max {self.reports_config["max_description_length"]} chars)'}
        
        if not report_data['reported_by']:
            return {'valid': False, 'error': 'Reported by cannot be empty'}
        
        # Validar severidade
        valid_severities = ['low', 'medium', 'high', 'critical']
        if 'severity' in report_data and report_data['severity'] not in valid_severities:
            return {'valid': False, 'error': 'Invalid severity level'}
        
        return {'valid': True}
    
    def _calculate_priority(self, report_data: Dict[str, Any]) -> str:
        """Calcula prioridade baseada em critérios"""
        severity = report_data.get('severity', 'medium')
        
        # Mapeamento de severidade para prioridade
        severity_priority = {
            'critical': 'high',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        
        base_priority = severity_priority.get(severity, 'medium')
        
        # Ajustar baseado em outros fatores
        if report_data.get('affects_production', False):
            if base_priority == 'medium':
                base_priority = 'high'
            elif base_priority == 'low':
                base_priority = 'medium'
        
        return base_priority
    
    def _auto_assign_bug(self, report_id: str, priority: str) -> str:
        """Atribui bug automaticamente baseado em prioridade"""
        # Simulação de auto-atribuição
        developers = {
            'high': ['dev_senior_1', 'dev_senior_2'],
            'medium': ['dev_mid_1', 'dev_mid_2'],
            'low': ['dev_junior_1', 'dev_junior_2']
        }
        
        available_devs = developers.get(priority, ['dev_general'])
        return available_devs[0]  # Retorna primeiro desenvolvedor disponível
    
    def _record_assignment(self, report_id: str, assignee: str, assignment_type: str, 
                          assigned_by: str = None, reason: str = None):
        """Registra atribuição de bug"""
        assignment = {
            'report_id': report_id,
            'assignee': assignee,
            'assignment_type': assignment_type,
            'assigned_by': assigned_by or 'system',
            'assigned_at': datetime.now(),
            'reason': reason
        }
        
        self.assignments[report_id].append(assignment)
    
    def _update_resolution_metrics(self, resolution_time: float):
        """Atualiza métricas de tempo de resolução"""
        current_avg = self.system_metrics['avg_resolution_time']
        total_resolved = self.system_metrics['reports_resolved'] + self.system_metrics['reports_closed']
        
        if total_resolved > 0:
            new_avg = ((current_avg * (total_resolved - 1)) + resolution_time) / total_resolved
            self.system_metrics['avg_resolution_time'] = new_avg
    
    def _apply_filters(self, reports: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica filtros aos relatórios"""
        filtered = reports.copy()
        
        if 'status' in filters:
            filtered = {k: v for k, v in filtered.items() if v['status'] == filters['status']}
        
        if 'severity' in filters:
            filtered = {k: v for k, v in filtered.items() if v['severity'] == filters['severity']}
        
        if 'priority' in filters:
            filtered = {k: v for k, v in filtered.items() if v['priority'] == filters['priority']}
        
        if 'assigned_to' in filters:
            filtered = {k: v for k, v in filtered.items() if v['assigned_to'] == filters['assigned_to']}
        
        return filtered
    
    def _calculate_performance_metrics(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de performance"""
        if not reports:
            return {
                'avg_resolution_time': 0,
                'resolution_rate': 0,
                'avg_comments_per_report': 0
            }
        
        resolved_reports = [r for r in reports.values() if r['status'] in ['resolved', 'closed']]
        total_comments = sum(r['comments_count'] for r in reports.values())
        
        resolution_rate = len(resolved_reports) / len(reports)
        avg_comments = total_comments / len(reports)
        
        return {
            'avg_resolution_time': self.system_metrics['avg_resolution_time'],
            'resolution_rate': resolution_rate,
            'avg_comments_per_report': avg_comments
        }
    
    def _generate_report_id(self) -> str:
        """Gera ID único para relatório"""
        import hashlib
        import uuid
        content = f"bug_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_comment_id(self) -> str:
        """Gera ID único para comentário"""
        import hashlib
        import uuid
        content = f"comment_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] BugReportsAPI.{operation}: {target} - {details}")


class TestBugReportsAPI:
    """Testes para Bug Reports API"""
    
    @pytest.fixture
    def reports_api(self):
        """Fixture para instância da API de relatórios"""
        return BugReportsAPI()
    
    @pytest.fixture
    def sample_report_data(self):
        """Dados de relatório de exemplo"""
        return {
            'title': 'Login page crashes on mobile devices',
            'description': 'When users try to login on mobile devices, the app crashes immediately after entering credentials',
            'severity': 'high',
            'category': 'authentication',
            'reported_by': 'user_123',
            'environment': {
                'platform': 'mobile',
                'os': 'iOS 15.0',
                'browser': 'Safari',
                'device': 'iPhone 13'
            },
            'steps_to_reproduce': [
                'Open the app on mobile device',
                'Navigate to login page',
                'Enter valid credentials',
                'Tap login button'
            ],
            'expected_behavior': 'User should be logged in successfully',
            'actual_behavior': 'App crashes immediately',
            'metadata': {'version': '2.1.0', 'build': '12345'}
        }
    
    @pytest.fixture
    def sample_comment_data(self):
        """Dados de comentário de exemplo"""
        return {
            'content': 'This issue has been reproduced in our testing environment. Working on a fix.',
            'author': 'dev_456',
            'is_internal': True,
            'attachments': []
        }
    
    def test_create_bug_report_success(self, reports_api, sample_report_data):
        """Teste de criação de relatório bem-sucedido"""
        # Arrange
        report_data = sample_report_data
        
        # Act
        result = reports_api.create_bug_report(report_data)
        
        # Assert
        assert result['success'] is True
        assert 'report_id' in result
        assert 'bug_report' in result
        
        bug_report = result['bug_report']
        assert bug_report['title'] == report_data['title']
        assert bug_report['description'] == report_data['description']
        assert bug_report['severity'] == report_data['severity']
        assert bug_report['category'] == report_data['category']
        assert bug_report['reported_by'] == report_data['reported_by']
        assert bug_report['status'] == 'open'
        assert bug_report['priority'] == 'high'  # Baseado na severidade
        assert bug_report['comments_count'] == 0
    
    def test_update_bug_status(self, reports_api, sample_report_data):
        """Teste de atualização de status"""
        # Arrange
        create_result = reports_api.create_bug_report(sample_report_data)
        report_id = create_result['report_id']
        new_status = 'in_progress'
        notes = 'Developer assigned and working on fix'
        
        # Act
        result = reports_api.update_bug_status(report_id, new_status, 'dev_456', notes)
        
        # Assert
        assert result['success'] is True
        assert result['report_id'] == report_id
        assert result['old_status'] == 'open'
        assert result['new_status'] == new_status
        assert result['notes'] == notes
        
        # Verificar se status foi atualizado
        bug_report = reports_api.bug_reports[report_id]
        assert bug_report['status'] == new_status
    
    def test_assign_bug_report(self, reports_api, sample_report_data):
        """Teste de atribuição de bug"""
        # Arrange
        create_result = reports_api.create_bug_report(sample_report_data)
        report_id = create_result['report_id']
        assignee = 'dev_senior_1'
        reason = 'High priority bug requiring senior developer'
        
        # Act
        result = reports_api.assign_bug_report(report_id, assignee, 'manager_001', reason)
        
        # Assert
        assert result['success'] is True
        assert result['report_id'] == report_id
        assert result['new_assignee'] == assignee
        assert result['assigned_by'] == 'manager_001'
        assert result['reason'] == reason
        
        # Verificar se atribuição foi registrada
        bug_report = reports_api.bug_reports[report_id]
        assert bug_report['assigned_to'] == assignee
        
        # Verificar histórico de atribuições
        assert len(reports_api.assignments[report_id]) == 2  # Auto-assign + manual assign
    
    def test_add_comment_to_bug(self, reports_api, sample_report_data, sample_comment_data):
        """Teste de adição de comentário"""
        # Arrange
        create_result = reports_api.create_bug_report(sample_report_data)
        report_id = create_result['report_id']
        comment_data = sample_comment_data
        
        # Act
        result = reports_api.add_comment_to_bug(report_id, comment_data)
        
        # Assert
        assert result['success'] is True
        assert 'comment_id' in result
        assert result['report_id'] == report_id
        assert 'created_at' in result
        
        # Verificar se comentário foi adicionado
        assert len(reports_api.comments[report_id]) == 1
        
        comment = reports_api.comments[report_id][0]
        assert comment['content'] == comment_data['content']
        assert comment['author'] == comment_data['author']
        assert comment['is_internal'] == comment_data['is_internal']
        
        # Verificar se contador foi atualizado
        bug_report = reports_api.bug_reports[report_id]
        assert bug_report['comments_count'] == 1
    
    def test_reports_edge_cases(self, reports_api):
        """Teste de casos edge do sistema de relatórios"""
        # Teste com dados inválidos
        invalid_report = {'title': '', 'description': '', 'reported_by': ''}
        result = reports_api.create_bug_report(invalid_report)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste com título muito longo
        long_title = 'x' * 250  # Excede limite de 200
        long_report = {
            'title': long_title,
            'description': 'Valid description',
            'reported_by': 'user_123'
        }
        result = reports_api.create_bug_report(long_report)
        assert result['success'] is False
        assert 'too long' in result['error']
        
        # Teste com severidade inválida
        invalid_severity_report = {
            'title': 'Test Bug',
            'description': 'Test description',
            'reported_by': 'user_123',
            'severity': 'invalid'
        }
        result = reports_api.create_bug_report(invalid_severity_report)
        assert result['success'] is False
        assert 'Invalid severity level' in result['error']
        
        # Teste de atualização de status em relatório inexistente
        result = reports_api.update_bug_status('nonexistent_id', 'resolved', 'dev_123')
        assert result['success'] is False
        assert result['error'] == 'Bug report not found'
        
        # Teste de comentário em relatório inexistente
        result = reports_api.add_comment_to_bug('nonexistent_id', {'content': 'Test', 'author': 'dev_123'})
        assert result['success'] is False
        assert result['error'] == 'Bug report not found'
    
    def test_reports_performance_large_scale(self, reports_api):
        """Teste de performance em larga escala"""
        # Arrange
        report_data = {
            'title': 'Performance Test Bug',
            'description': 'Test description for performance testing',
            'reported_by': 'test_user'
        }
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(50):
            report_data['title'] = f'Bug Report {i}'
            report_data['reported_by'] = f'user_{i}'
            report_data['severity'] = ['low', 'medium', 'high', 'critical'][i % 4]
            
            result = reports_api.create_bug_report(report_data)
            assert result['success'] is True
            
            report_id = result['report_id']
            
            # Adicionar alguns comentários
            for j in range(2):
                comment_data = {
                    'content': f'Comment {j} for bug {i}',
                    'author': f'dev_{i}_{j}'
                }
                reports_api.add_comment_to_bug(report_id, comment_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 3 segundos para 150 operações)
        assert duration < 3.0
        
        # Verificar se todos os relatórios foram criados
        assert len(reports_api.bug_reports) == 50
        assert reports_api.system_metrics['reports_created'] == 50
        assert reports_api.system_metrics['total_comments'] == 100  # 50 * 2
        assert reports_api.system_metrics['critical_bugs'] == 12  # 50 / 4 (critical severity)
    
    def test_reports_integration_with_workflow(self, reports_api, sample_report_data):
        """Teste de integração com fluxo de trabalho"""
        # Arrange
        create_result = reports_api.create_bug_report(sample_report_data)
        report_id = create_result['report_id']
        
        # Simular fluxo completo de trabalho
        workflow_steps = [
            ('in_progress', 'dev_456', 'Developer assigned and starting investigation'),
            ('testing', 'qa_789', 'Fix implemented, ready for testing'),
            ('resolved', 'dev_456', 'Bug fixed and tested successfully')
        ]
        
        # Act - Executar fluxo de trabalho
        for status, user, notes in workflow_steps:
            result = reports_api.update_bug_status(report_id, status, user, notes)
            assert result['success'] is True
        
        # Adicionar comentários durante o processo
        comments = [
            ('dev_456', 'Found the issue in the authentication module'),
            ('qa_789', 'Testing the fix on multiple devices'),
            ('dev_456', 'Fix deployed to production')
        ]
        
        for author, content in comments:
            comment_data = {'content': content, 'author': author}
            result = reports_api.add_comment_to_bug(report_id, comment_data)
            assert result['success'] is True
        
        # Assert
        bug_report = reports_api.bug_reports[report_id]
        assert bug_report['status'] == 'resolved'
        assert bug_report['comments_count'] == 3
        
        # Verificar métricas
        assert reports_api.system_metrics['reports_resolved'] == 1
        assert reports_api.system_metrics['total_comments'] == 3
    
    def test_reports_configuration_validation(self, reports_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert reports_api.reports_config['max_title_length'] == 200
        assert reports_api.reports_config['max_description_length'] == 5000
        assert reports_api.reports_config['enable_attachments'] is True
        assert reports_api.reports_config['max_attachments'] == 5
        assert reports_api.reports_config['auto_assign'] is True
        assert reports_api.reports_config['require_screenshots'] is False
        
        # Teste de configuração customizada
        custom_config = {
            'max_title_length': 100,
            'max_description_length': 2000,
            'enable_attachments': False,
            'max_attachments': 3,
            'auto_assign': False,
            'require_screenshots': True
        }
        custom_api = BugReportsAPI(custom_config)
        
        assert custom_api.reports_config['max_title_length'] == 100
        assert custom_api.reports_config['max_description_length'] == 2000
        assert custom_api.reports_config['enable_attachments'] is False
        assert custom_api.reports_config['max_attachments'] == 3
        assert custom_api.reports_config['auto_assign'] is False
        assert custom_api.reports_config['require_screenshots'] is True
    
    def test_reports_logs_operation_tracking(self, reports_api, sample_report_data, capsys):
        """Teste de logs de operações do sistema"""
        # Act
        reports_api.create_bug_report(sample_report_data)
        reports_api.get_bug_reports_summary()
        reports_api.get_bug_report_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "BugReportsAPI.create_bug_report" in log_output
        assert "BugReportsAPI.get_bug_reports_summary" in log_output
        assert "BugReportsAPI.get_bug_report_stats" in log_output
        assert "INFO" in log_output
    
    def test_reports_metrics_collection(self, reports_api, sample_report_data):
        """Teste de coleta de métricas do sistema"""
        # Arrange
        initial_stats = reports_api.get_bug_report_stats()
        
        # Act - Simular uso do sistema
        create_result = reports_api.create_bug_report(sample_report_data)
        report_id = create_result['report_id']
        
        # Adicionar comentários
        for i in range(3):
            comment_data = {
                'content': f'Comment {i}',
                'author': f'dev_{i}'
            }
            reports_api.add_comment_to_bug(report_id, comment_data)
        
        # Atualizar status
        reports_api.update_bug_status(report_id, 'resolved', 'dev_456', 'Bug fixed')
        
        # Assert
        final_stats = reports_api.get_bug_report_stats()
        
        assert final_stats['total_reports'] == 1
        assert final_stats['open_reports'] == 0
        assert final_stats['resolved_reports'] == 1
        assert final_stats['reports_created'] == 1
        assert final_stats['reports_resolved'] == 1
        assert final_stats['total_comments'] == 3
        assert final_stats['critical_bugs'] == 0  # Severidade 'high' não é 'critical'
        assert final_stats['resolution_rate'] == 1.0
        assert final_stats['avg_resolution_time'] > 0
    
    def test_reports_reports_generation(self, reports_api, sample_report_data):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        severities = ['low', 'medium', 'high', 'critical']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        
        for i in range(20):
            report_data = sample_report_data.copy()
            report_data['title'] = f'Bug Report {i+1}'
            report_data['severity'] = severities[i % len(severities)]
            report_data['reported_by'] = f'user_{i}'
            
            create_result = reports_api.create_bug_report(report_data)
            report_id = create_result['report_id']
            
            # Adicionar comentários
            for j in range(i % 3 + 1):  # Variação no número de comentários
                comment_data = {
                    'content': f'Comment {j} for bug {i}',
                    'author': f'dev_{i}_{j}'
                }
                reports_api.add_comment_to_bug(report_id, comment_data)
            
            # Atualizar alguns statuses
            if i % 4 == 0:
                reports_api.update_bug_status(report_id, 'resolved', 'dev_456')
            elif i % 4 == 1:
                reports_api.update_bug_status(report_id, 'closed', 'dev_456')
        
        # Act
        summary_result = reports_api.get_bug_reports_summary()
        stats_result = reports_api.get_bug_report_stats()
        
        # Assert
        assert summary_result['success'] is True
        assert stats_result['total_reports'] == 20
        
        summary = summary_result['summary']
        assert 'total_reports' in summary
        assert 'status_distribution' in summary
        assert 'severity_distribution' in summary
        assert 'priority_distribution' in summary
        assert 'total_comments' in summary
        assert 'performance_metrics' in summary
        
        # Verificar valores específicos
        assert summary['total_reports'] == 20
        assert summary['status_distribution']['open'] == 10  # 20 - 5 resolved - 5 closed
        assert summary['status_distribution']['resolved'] == 5
        assert summary['status_distribution']['closed'] == 5
        assert summary['severity_distribution']['critical'] == 5  # 20 / 4
        assert summary['total_comments'] == 30  # Soma de comentários variados
        assert summary['performance_metrics']['resolution_rate'] == 0.5  # 10/20


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 