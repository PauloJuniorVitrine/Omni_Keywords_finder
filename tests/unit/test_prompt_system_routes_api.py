"""
Testes unitários para Prompt System Routes API
Cobertura: Criação de prompts, execução, validação, métricas
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Prompt System Routes API
class PromptSystemRoutesAPI:
    """API para rotas do sistema de prompts"""
    
    def __init__(self, system_config: Dict[str, Any] = None):
        self.system_config = system_config or {
            'max_prompt_length': 10000,
            'max_execution_time': 300,
            'enable_caching': True,
            'rate_limit': 100
        }
        self.prompts = {}
        self.execution_history = []
        self.system_metrics = {
            'prompts_created': 0,
            'prompts_executed': 0,
            'executions_successful': 0,
            'executions_failed': 0,
            'total_execution_time': 0
        }
    
    def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo prompt"""
        try:
            # Validação dos dados do prompt
            validation = self._validate_prompt_data(prompt_data)
            if not validation['valid']:
                self._log_operation('create_prompt', prompt_data.get('name', 'unknown'), False, validation['error'])
                return validation
            
            # Gerar ID único
            prompt_id = self._generate_prompt_id()
            
            # Criar prompt
            prompt = {
                'id': prompt_id,
                'name': prompt_data['name'],
                'content': prompt_data['content'],
                'template': prompt_data.get('template', ''),
                'variables': prompt_data.get('variables', {}),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'created_by': prompt_data.get('created_by', 'system'),
                'status': 'active',
                'version': 1,
                'tags': prompt_data.get('tags', []),
                'metadata': prompt_data.get('metadata', {})
            }
            
            self.prompts[prompt_id] = prompt
            self.system_metrics['prompts_created'] += 1
            
            self._log_operation('create_prompt', prompt['name'], True, f'Prompt created with ID: {prompt_id}')
            return {
                'success': True,
                'prompt_id': prompt_id,
                'prompt': prompt
            }
            
        except Exception as e:
            self._log_operation('create_prompt', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def execute_prompt(self, prompt_id: str, variables: Dict[str, Any] = None, 
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executa um prompt"""
        try:
            # Verificar se prompt existe
            if prompt_id not in self.prompts:
                self._log_operation('execute_prompt', prompt_id, False, 'Prompt not found')
                return {'success': False, 'error': 'Prompt not found'}
            
            prompt = self.prompts[prompt_id]
            
            # Verificar se prompt está ativo
            if prompt['status'] != 'active':
                self._log_operation('execute_prompt', prompt['name'], False, 'Prompt is not active')
                return {'success': False, 'error': 'Prompt is not active'}
            
            # Preparar variáveis
            execution_variables = {**prompt['variables'], **(variables or {})}
            
            # Executar prompt
            start_time = datetime.now()
            execution_result = self._execute_prompt_content(prompt, execution_variables, context)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            # Verificar timeout
            if execution_time > self.system_config['max_execution_time']:
                self._log_operation('execute_prompt', prompt['name'], False, 'Execution timeout')
                return {'success': False, 'error': 'Execution timeout'}
            
            # Registrar execução
            execution_record = {
                'prompt_id': prompt_id,
                'prompt_name': prompt['name'],
                'variables': execution_variables,
                'context': context,
                'result': execution_result,
                'execution_time': execution_time,
                'timestamp': datetime.now(),
                'success': execution_result.get('success', False)
            }
            
            self.execution_history.append(execution_record)
            self.system_metrics['prompts_executed'] += 1
            self.system_metrics['total_execution_time'] += execution_time
            
            if execution_result.get('success', False):
                self.system_metrics['executions_successful'] += 1
            else:
                self.system_metrics['executions_failed'] += 1
            
            self._log_operation('execute_prompt', prompt['name'], True, f'Execution completed in {execution_time}s')
            
            return {
                'success': True,
                'prompt_id': prompt_id,
                'prompt_name': prompt['name'],
                'result': execution_result,
                'execution_time': execution_time,
                'variables_used': execution_variables
            }
            
        except Exception as e:
            self._log_operation('execute_prompt', prompt_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def validate_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados de um prompt"""
        try:
            validation_result = self._validate_prompt_data(prompt_data)
            
            if validation_result['valid']:
                # Análise adicional
                analysis = self._analyze_prompt(prompt_data)
                validation_result['analysis'] = analysis
            
            self._log_operation('validate_prompt', prompt_data.get('name', 'unknown'), 
                              validation_result['valid'], 'Validation completed')
            return validation_result
            
        except Exception as e:
            self._log_operation('validate_prompt', 'unknown', False, str(e))
            return {'valid': False, 'error': str(e)}
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de prompts"""
        try:
            total_prompts = len(self.prompts)
            active_prompts = sum(1 for p in self.prompts.values() if p['status'] == 'active')
            
            avg_execution_time = 0
            if self.system_metrics['prompts_executed'] > 0:
                avg_execution_time = self.system_metrics['total_execution_time'] / self.system_metrics['prompts_executed']
            
            success_rate = 0
            if self.system_metrics['prompts_executed'] > 0:
                success_rate = self.system_metrics['executions_successful'] / self.system_metrics['prompts_executed']
            
            return {
                'total_prompts': total_prompts,
                'active_prompts': active_prompts,
                'prompts_created': self.system_metrics['prompts_created'],
                'prompts_executed': self.system_metrics['prompts_executed'],
                'executions_successful': self.system_metrics['executions_successful'],
                'executions_failed': self.system_metrics['executions_failed'],
                'avg_execution_time': avg_execution_time,
                'success_rate': success_rate,
                'total_execution_time': self.system_metrics['total_execution_time']
            }
            
        except Exception as e:
            self._log_operation('get_prompt_stats', 'system', False, str(e))
            return {}
    
    def _validate_prompt_data(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do prompt"""
        required_fields = ['name', 'content']
        
        for field in required_fields:
            if field not in prompt_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not prompt_data['name'] or len(prompt_data['name']) < 3:
            return {'valid': False, 'error': 'Name must be at least 3 characters long'}
        
        if not prompt_data['content'] or len(prompt_data['content']) > self.system_config['max_prompt_length']:
            return {'valid': False, 'error': f'Content too long (max {self.system_config["max_prompt_length"]} chars)'}
        
        return {'valid': True}
    
    def _analyze_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa prompt para insights"""
        content = prompt_data['content']
        
        return {
            'length': len(content),
            'word_count': len(content.split()),
            'has_variables': '{{' in content and '}}' in content,
            'complexity_score': self._calculate_complexity_score(content),
            'estimated_execution_time': len(content) * 0.001,  # ms por caractere
            'suggestions': self._generate_suggestions(content)
        }
    
    def _calculate_complexity_score(self, content: str) -> int:
        """Calcula score de complexidade do prompt"""
        score = 0
        score += len(content) // 100  # Pontos por 100 caracteres
        score += content.count('{{') * 5  # Pontos por variável
        score += content.count('\n') * 2  # Pontos por linha
        return min(100, score)
    
    def _generate_suggestions(self, content: str) -> List[str]:
        """Gera sugestões para o prompt"""
        suggestions = []
        
        if len(content) > 5000:
            suggestions.append("Consider breaking down into smaller prompts")
        
        if content.count('{{') > 10:
            suggestions.append("Too many variables, consider simplifying")
        
        if len(content.split('\n')) > 50:
            suggestions.append("Prompt is very long, consider condensing")
        
        return suggestions
    
    def _execute_prompt_content(self, prompt: Dict[str, Any], variables: Dict[str, Any], 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executa o conteúdo do prompt"""
        try:
            content = prompt['content']
            
            # Substituir variáveis
            for key, value in variables.items():
                placeholder = f'{{{{{key}}}}}'
                content = content.replace(placeholder, str(value))
            
            # Simular execução
            result = {
                'success': True,
                'output': f"Executed prompt: {prompt['name']}",
                'processed_content': content,
                'variables_used': variables,
                'context': context
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'variables_used': variables
            }
    
    def _generate_prompt_id(self) -> str:
        """Gera ID único para prompt"""
        import hashlib
        import uuid
        content = f"{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] PromptSystemRoutesAPI.{operation}: {target} - {details}")


class TestPromptSystemRoutesAPI:
    """Testes para Prompt System Routes API"""
    
    @pytest.fixture
    def prompt_api(self):
        """Fixture para instância da API de prompts"""
        return PromptSystemRoutesAPI()
    
    @pytest.fixture
    def sample_prompt_data(self):
        """Dados de prompt de exemplo"""
        return {
            'name': 'Test Prompt',
            'content': 'Hello {{name}}, welcome to {{platform}}!',
            'template': 'greeting',
            'variables': {'name': 'User', 'platform': 'System'},
            'created_by': 'test_user',
            'tags': ['greeting', 'welcome'],
            'metadata': {'category': 'communication'}
        }
    
    @pytest.fixture
    def complex_prompt_data(self):
        """Dados de prompt complexo de exemplo"""
        return {
            'name': 'Complex Analysis Prompt',
            'content': '''
            Analyze the following data:
            - User: {{user_name}}
            - Age: {{user_age}}
            - Preferences: {{preferences}}
            
            Please provide:
            1. Summary of user profile
            2. Recommended actions
            3. Risk assessment
            
            Use the following criteria:
            - Age group analysis
            - Preference matching
            - Historical data comparison
            ''',
            'variables': {
                'user_name': 'John Doe',
                'user_age': 30,
                'preferences': ['tech', 'sports']
            },
            'tags': ['analysis', 'complex'],
            'metadata': {'complexity': 'high'}
        }
    
    def test_create_prompt_success(self, prompt_api, sample_prompt_data):
        """Teste de criação de prompt bem-sucedido"""
        # Arrange
        prompt_data = sample_prompt_data
        
        # Act
        result = prompt_api.create_prompt(prompt_data)
        
        # Assert
        assert result['success'] is True
        assert 'prompt_id' in result
        assert 'prompt' in result
        
        prompt = result['prompt']
        assert prompt['name'] == prompt_data['name']
        assert prompt['content'] == prompt_data['content']
        assert prompt['status'] == 'active'
        assert prompt['version'] == 1
        assert prompt['created_by'] == prompt_data['created_by']
    
    def test_execute_prompt_success(self, prompt_api, sample_prompt_data):
        """Teste de execução de prompt bem-sucedido"""
        # Arrange
        create_result = prompt_api.create_prompt(sample_prompt_data)
        prompt_id = create_result['prompt_id']
        variables = {'name': 'Alice', 'platform': 'Test Platform'}
        
        # Act
        result = prompt_api.execute_prompt(prompt_id, variables)
        
        # Assert
        assert result['success'] is True
        assert result['prompt_id'] == prompt_id
        assert result['prompt_name'] == sample_prompt_data['name']
        assert 'result' in result
        assert 'execution_time' in result
        assert 'variables_used' in result
        
        execution_result = result['result']
        assert execution_result['success'] is True
        assert 'Hello Alice, welcome to Test Platform!' in execution_result['processed_content']
    
    def test_validate_prompt(self, prompt_api, sample_prompt_data):
        """Teste de validação de prompt"""
        # Arrange
        prompt_data = sample_prompt_data
        
        # Act
        validation = prompt_api.validate_prompt(prompt_data)
        
        # Assert
        assert validation['valid'] is True
        assert 'analysis' in validation
        
        analysis = validation['analysis']
        assert 'length' in analysis
        assert 'word_count' in analysis
        assert 'has_variables' in analysis
        assert 'complexity_score' in analysis
        assert 'estimated_execution_time' in analysis
        assert 'suggestions' in analysis
        
        assert analysis['has_variables'] is True
        assert analysis['length'] > 0
        assert analysis['word_count'] > 0
    
    def test_prompt_edge_cases(self, prompt_api):
        """Teste de casos edge do sistema de prompts"""
        # Teste com dados inválidos
        invalid_data = {'name': 'ab', 'content': ''}  # Nome muito curto, conteúdo vazio
        result = prompt_api.create_prompt(invalid_data)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste com conteúdo muito longo
        long_content = 'x' * 15000  # Excede limite de 10000
        long_prompt_data = {'name': 'Long Prompt', 'content': long_content}
        result = prompt_api.create_prompt(long_prompt_data)
        assert result['success'] is False
        assert 'too long' in result['error']
        
        # Teste de execução de prompt inexistente
        result = prompt_api.execute_prompt('nonexistent_id')
        assert result['success'] is False
        assert result['error'] == 'Prompt not found'
        
        # Teste de validação com dados mínimos
        minimal_data = {'name': 'Minimal', 'content': 'Simple content'}
        validation = prompt_api.validate_prompt(minimal_data)
        assert validation['valid'] is True
    
    def test_prompt_performance_large_scale(self, prompt_api):
        """Teste de performance em larga escala"""
        # Arrange
        prompts_created = []
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(50):
            prompt_data = {
                'name': f'Performance Test Prompt {i}',
                'content': f'This is test content for prompt {i} with variable {{var_{i}}}',
                'variables': {f'var_{i}': f'value_{i}'}
            }
            
            result = prompt_api.create_prompt(prompt_data)
            assert result['success'] is True
            prompts_created.append(result['prompt_id'])
        
        # Executar alguns prompts
        for i in range(10):
            prompt_id = prompts_created[i]
            result = prompt_api.execute_prompt(prompt_id, {f'var_{i}': f'exec_value_{i}'})
            assert result['success'] is True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 5 segundos para 60 operações)
        assert duration < 5.0
    
    def test_prompt_integration_with_variables(self, prompt_api, complex_prompt_data):
        """Teste de integração com variáveis complexas"""
        # Arrange
        create_result = prompt_api.create_prompt(complex_prompt_data)
        prompt_id = create_result['prompt_id']
        
        execution_variables = {
            'user_name': 'Jane Smith',
            'user_age': 25,
            'preferences': ['music', 'travel', 'food']
        }
        
        context = {
            'session_id': 'session_123',
            'user_agent': 'Test Browser',
            'timestamp': datetime.now().isoformat()
        }
        
        # Act
        result = prompt_api.execute_prompt(prompt_id, execution_variables, context)
        
        # Assert
        assert result['success'] is True
        assert result['prompt_name'] == complex_prompt_data['name']
        
        execution_result = result['result']
        assert execution_result['success'] is True
        assert 'Jane Smith' in execution_result['processed_content']
        assert '25' in execution_result['processed_content']
        assert 'music' in execution_result['processed_content']
        assert execution_result['context'] == context
    
    def test_prompt_configuration_validation(self, prompt_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert prompt_api.system_config['max_prompt_length'] == 10000
        assert prompt_api.system_config['max_execution_time'] == 300
        assert prompt_api.system_config['enable_caching'] is True
        assert prompt_api.system_config['rate_limit'] == 100
        
        # Teste de configuração customizada
        custom_config = {
            'max_prompt_length': 5000,
            'max_execution_time': 150,
            'enable_caching': False,
            'rate_limit': 50
        }
        custom_api = PromptSystemRoutesAPI(custom_config)
        
        assert custom_api.system_config['max_prompt_length'] == 5000
        assert custom_api.system_config['max_execution_time'] == 150
        assert custom_api.system_config['enable_caching'] is False
        assert custom_api.system_config['rate_limit'] == 50
    
    def test_prompt_logs_operation_tracking(self, prompt_api, sample_prompt_data, capsys):
        """Teste de logs de operações do sistema"""
        # Act
        prompt_api.create_prompt(sample_prompt_data)
        prompt_api.validate_prompt(sample_prompt_data)
        prompt_api.get_prompt_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "PromptSystemRoutesAPI.create_prompt" in log_output
        assert "PromptSystemRoutesAPI.validate_prompt" in log_output
        assert "PromptSystemRoutesAPI.get_prompt_stats" in log_output
        assert "INFO" in log_output
    
    def test_prompt_metrics_collection(self, prompt_api, sample_prompt_data, complex_prompt_data):
        """Teste de coleta de métricas do sistema"""
        # Arrange
        initial_stats = prompt_api.get_prompt_stats()
        
        # Act - Simular uso do sistema
        prompt_api.create_prompt(sample_prompt_data)
        prompt_api.create_prompt(complex_prompt_data)
        
        create_result = prompt_api.create_prompt(sample_prompt_data)
        prompt_id = create_result['prompt_id']
        
        prompt_api.execute_prompt(prompt_id, {'name': 'Test', 'platform': 'System'})
        prompt_api.execute_prompt(prompt_id, {'name': 'Another', 'platform': 'Test'})
        
        # Assert
        final_stats = prompt_api.get_prompt_stats()
        
        assert final_stats['total_prompts'] == 3
        assert final_stats['active_prompts'] == 3
        assert final_stats['prompts_created'] == 3
        assert final_stats['prompts_executed'] == 2
        assert final_stats['executions_successful'] == 2
        assert final_stats['executions_failed'] == 0
        assert final_stats['success_rate'] == 1.0
        assert final_stats['avg_execution_time'] > 0
        assert final_stats['total_execution_time'] > 0
    
    def test_prompt_reports_generation(self, prompt_api, sample_prompt_data, complex_prompt_data):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        for i in range(5):
            prompt_data = {
                'name': f'Report Test Prompt {i}',
                'content': f'Content for prompt {i} with {{variable_{i}}}',
                'variables': {f'variable_{i}': f'value_{i}'}
            }
            prompt_api.create_prompt(prompt_data)
        
        prompt_api.create_prompt(sample_prompt_data)
        prompt_api.create_prompt(complex_prompt_data)
        
        # Executar alguns prompts
        create_result = prompt_api.create_prompt(sample_prompt_data)
        prompt_id = create_result['prompt_id']
        
        for i in range(3):
            prompt_api.execute_prompt(prompt_id, {'name': f'User{i}', 'platform': 'Platform{i}'})
        
        # Act
        report = prompt_api.get_prompt_stats()
        
        # Assert
        assert 'total_prompts' in report
        assert 'active_prompts' in report
        assert 'prompts_created' in report
        assert 'prompts_executed' in report
        assert 'executions_successful' in report
        assert 'executions_failed' in report
        assert 'avg_execution_time' in report
        assert 'success_rate' in report
        assert 'total_execution_time' in report
        
        # Verificar valores específicos
        assert report['total_prompts'] == 8  # 5 + 1 + 1 + 1
        assert report['active_prompts'] == 8
        assert report['prompts_created'] == 8
        assert report['prompts_executed'] == 3
        assert report['executions_successful'] == 3
        assert report['success_rate'] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 