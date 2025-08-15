"""
Testes unitários para Surveys API
Cobertura: Criação de pesquisas, coleta de respostas, análise de resultados
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulação do módulo Surveys API
class SurveysAPI:
    """API para gerenciamento de pesquisas"""
    
    def __init__(self, survey_config: Dict[str, Any] = None):
        self.survey_config = survey_config or {
            'max_questions': 50,
            'max_responses': 10000,
            'enable_anonymous': True,
            'require_authentication': False,
            'auto_close_days': 30
        }
        self.surveys = {}
        self.responses = {}
        self.survey_history = []
        self.system_metrics = {
            'surveys_created': 0,
            'responses_collected': 0,
            'surveys_completed': 0,
            'analysis_generated': 0,
            'total_participants': 0
        }
    
    def create_survey(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova pesquisa"""
        try:
            # Validar dados da pesquisa
            validation = self._validate_survey_data(survey_data)
            if not validation['valid']:
                self._log_operation('create_survey', 'validation', False, validation['error'])
                return validation
            
            # Gerar ID único
            survey_id = self._generate_survey_id()
            
            # Criar pesquisa
            survey = {
                'id': survey_id,
                'title': survey_data['title'],
                'description': survey_data.get('description', ''),
                'questions': survey_data['questions'],
                'created_by': survey_data.get('created_by', 'system'),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'status': 'active',
                'settings': survey_data.get('settings', {}),
                'target_audience': survey_data.get('target_audience', []),
                'expires_at': self._calculate_expiry_date(survey_data.get('duration_days', 30)),
                'response_count': 0,
                'completion_rate': 0.0,
                'metadata': survey_data.get('metadata', {})
            }
            
            self.surveys[survey_id] = survey
            
            # Registrar no histórico
            self.survey_history.append({
                'timestamp': datetime.now(),
                'survey_id': survey_id,
                'operation': 'create',
                'created_by': survey['created_by']
            })
            
            self.system_metrics['surveys_created'] += 1
            
            self._log_operation('create_survey', survey_id, True, 'Survey created successfully')
            
            return {
                'success': True,
                'survey_id': survey_id,
                'survey': survey
            }
            
        except Exception as e:
            self._log_operation('create_survey', 'unknown', False, str(e))
            return {'success': False, 'error': str(e)}
    
    def collect_response(self, survey_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coleta resposta de uma pesquisa"""
        try:
            # Verificar se pesquisa existe e está ativa
            if survey_id not in self.surveys:
                self._log_operation('collect_response', survey_id, False, 'Survey not found')
                return {'success': False, 'error': 'Survey not found'}
            
            survey = self.surveys[survey_id]
            
            if survey['status'] != 'active':
                self._log_operation('collect_response', survey_id, False, 'Survey is not active')
                return {'success': False, 'error': 'Survey is not active'}
            
            if datetime.now() > survey['expires_at']:
                self._log_operation('collect_response', survey_id, False, 'Survey has expired')
                return {'success': False, 'error': 'Survey has expired'}
            
            # Validar resposta
            response_validation = self._validate_response_data(survey, response_data)
            if not response_validation['valid']:
                self._log_operation('collect_response', survey_id, False, response_validation['error'])
                return response_validation
            
            # Gerar ID único para resposta
            response_id = self._generate_response_id()
            
            # Criar resposta
            response = {
                'id': response_id,
                'survey_id': survey_id,
                'answers': response_data['answers'],
                'respondent_id': response_data.get('respondent_id'),
                'submitted_at': datetime.now(),
                'completion_time': response_data.get('completion_time', 0),
                'device_info': response_data.get('device_info', {}),
                'ip_address': response_data.get('ip_address'),
                'user_agent': response_data.get('user_agent'),
                'metadata': response_data.get('metadata', {})
            }
            
            # Armazenar resposta
            if survey_id not in self.responses:
                self.responses[survey_id] = []
            self.responses[survey_id].append(response)
            
            # Atualizar estatísticas da pesquisa
            survey['response_count'] += 1
            survey['completion_rate'] = self._calculate_completion_rate(survey_id)
            survey['updated_at'] = datetime.now()
            
            # Atualizar métricas
            self.system_metrics['responses_collected'] += 1
            if response_data.get('respondent_id'):
                self.system_metrics['total_participants'] += 1
            
            self._log_operation('collect_response', survey_id, True, f'Response collected: {response_id}')
            
            return {
                'success': True,
                'response_id': response_id,
                'survey_id': survey_id,
                'submitted_at': response['submitted_at'].isoformat()
            }
            
        except Exception as e:
            self._log_operation('collect_response', survey_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def analyze_survey_results(self, survey_id: str, analysis_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analisa resultados de uma pesquisa"""
        try:
            # Verificar se pesquisa existe
            if survey_id not in self.surveys:
                self._log_operation('analyze_survey_results', survey_id, False, 'Survey not found')
                return {'success': False, 'error': 'Survey not found'}
            
            survey = self.surveys[survey_id]
            responses = self.responses.get(survey_id, [])
            
            if not responses:
                self._log_operation('analyze_survey_results', survey_id, False, 'No responses found')
                return {'success': False, 'error': 'No responses found'}
            
            # Configuração de análise
            config = analysis_config or {}
            
            # Realizar análises
            analysis_results = {
                'survey_id': survey_id,
                'survey_title': survey['title'],
                'total_responses': len(responses),
                'completion_rate': survey['completion_rate'],
                'average_completion_time': self._calculate_average_completion_time(responses),
                'question_analysis': self._analyze_questions(survey['questions'], responses),
                'demographics': self._analyze_demographics(responses),
                'trends': self._analyze_trends(responses),
                'insights': self._generate_insights(survey, responses),
                'generated_at': datetime.now().isoformat()
            }
            
            # Adicionar análises específicas se configurado
            if config.get('include_sentiment_analysis'):
                analysis_results['sentiment_analysis'] = self._analyze_sentiment(responses)
            
            if config.get('include_correlation_analysis'):
                analysis_results['correlation_analysis'] = self._analyze_correlations(survey, responses)
            
            self.system_metrics['analysis_generated'] += 1
            
            self._log_operation('analyze_survey_results', survey_id, True, 'Analysis completed successfully')
            
            return {
                'success': True,
                'analysis': analysis_results
            }
            
        except Exception as e:
            self._log_operation('analyze_survey_results', survey_id, False, str(e))
            return {'success': False, 'error': str(e)}
    
    def get_survey_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de pesquisas"""
        try:
            total_surveys = len(self.surveys)
            active_surveys = sum(1 for s in self.surveys.values() if s['status'] == 'active')
            completed_surveys = sum(1 for s in self.surveys.values() if s['status'] == 'completed')
            
            total_responses = sum(s['response_count'] for s in self.surveys.values())
            avg_completion_rate = 0
            if total_surveys > 0:
                avg_completion_rate = sum(s['completion_rate'] for s in self.surveys.values()) / total_surveys
            
            return {
                'total_surveys': total_surveys,
                'active_surveys': active_surveys,
                'completed_surveys': completed_surveys,
                'total_responses': total_responses,
                'avg_completion_rate': avg_completion_rate,
                'surveys_created': self.system_metrics['surveys_created'],
                'responses_collected': self.system_metrics['responses_collected'],
                'analysis_generated': self.system_metrics['analysis_generated'],
                'total_participants': self.system_metrics['total_participants'],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_operation('get_survey_stats', 'system', False, str(e))
            return {}
    
    def _validate_survey_data(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados da pesquisa"""
        required_fields = ['title', 'questions']
        
        for field in required_fields:
            if field not in survey_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        if not survey_data['title']:
            return {'valid': False, 'error': 'Title cannot be empty'}
        
        if not survey_data['questions'] or len(survey_data['questions']) == 0:
            return {'valid': False, 'error': 'Survey must have at least one question'}
        
        if len(survey_data['questions']) > self.survey_config['max_questions']:
            return {'valid': False, 'error': f'Too many questions (max {self.survey_config["max_questions"]})'}
        
        # Validar cada questão
        for i, question in enumerate(survey_data['questions']):
            question_validation = self._validate_question(question)
            if not question_validation['valid']:
                return {'valid': False, 'error': f'Question {i+1}: {question_validation["error"]}'}
        
        return {'valid': True}
    
    def _validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma questão"""
        if 'text' not in question:
            return {'valid': False, 'error': 'Question must have text'}
        
        if 'type' not in question:
            return {'valid': False, 'error': 'Question must have type'}
        
        valid_types = ['text', 'multiple_choice', 'rating', 'yes_no', 'scale']
        if question['type'] not in valid_types:
            return {'valid': False, 'error': f'Invalid question type: {question["type"]}'}
        
        return {'valid': True}
    
    def _validate_response_data(self, survey: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados da resposta"""
        if 'answers' not in response_data:
            return {'valid': False, 'error': 'Response must have answers'}
        
        answers = response_data['answers']
        questions = survey['questions']
        
        if len(answers) != len(questions):
            return {'valid': False, 'error': 'Number of answers must match number of questions'}
        
        # Validar cada resposta
        for i, (question, answer) in enumerate(zip(questions, answers)):
            answer_validation = self._validate_answer(question, answer)
            if not answer_validation['valid']:
                return {'valid': False, 'error': f'Answer {i+1}: {answer_validation["error"]}'}
        
        return {'valid': True}
    
    def _validate_answer(self, question: Dict[str, Any], answer: Any) -> Dict[str, Any]:
        """Valida uma resposta"""
        question_type = question['type']
        
        if question_type == 'text':
            if not isinstance(answer, str):
                return {'valid': False, 'error': 'Text question requires string answer'}
        
        elif question_type == 'multiple_choice':
            if not isinstance(answer, (str, int)):
                return {'valid': False, 'error': 'Multiple choice question requires string or integer answer'}
        
        elif question_type == 'rating':
            if not isinstance(answer, (int, float)) or answer < 1 or answer > 5:
                return {'valid': False, 'error': 'Rating must be between 1 and 5'}
        
        elif question_type == 'yes_no':
            if not isinstance(answer, bool):
                return {'valid': False, 'error': 'Yes/No question requires boolean answer'}
        
        elif question_type == 'scale':
            if not isinstance(answer, int) or answer < 1 or answer > 10:
                return {'valid': False, 'error': 'Scale must be between 1 and 10'}
        
        return {'valid': True}
    
    def _calculate_expiry_date(self, duration_days: int) -> datetime:
        """Calcula data de expiração"""
        return datetime.now() + timedelta(days=duration_days)
    
    def _calculate_completion_rate(self, survey_id: str) -> float:
        """Calcula taxa de conclusão da pesquisa"""
        responses = self.responses.get(survey_id, [])
        if not responses:
            return 0.0
        
        completed_responses = sum(1 for r in responses if len(r['answers']) == len(self.surveys[survey_id]['questions']))
        return completed_responses / len(responses)
    
    def _calculate_average_completion_time(self, responses: List[Dict[str, Any]]) -> float:
        """Calcula tempo médio de conclusão"""
        if not responses:
            return 0.0
        
        completion_times = [r.get('completion_time', 0) for r in responses]
        return sum(completion_times) / len(completion_times)
    
    def _analyze_questions(self, questions: List[Dict[str, Any]], 
                          responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa respostas por questão"""
        analysis = []
        
        for i, question in enumerate(questions):
            question_analysis = {
                'question_index': i,
                'question_text': question['text'],
                'question_type': question['type'],
                'response_count': len(responses),
                'statistics': self._calculate_question_statistics(question, responses, i)
            }
            analysis.append(question_analysis)
        
        return analysis
    
    def _calculate_question_statistics(self, question: Dict[str, Any], 
                                     responses: List[Dict[str, Any]], 
                                     question_index: int) -> Dict[str, Any]:
        """Calcula estatísticas de uma questão"""
        answers = [r['answers'][question_index] for r in responses if len(r['answers']) > question_index]
        
        if question['type'] == 'rating':
            return {
                'average': sum(answers) / len(answers) if answers else 0,
                'min': min(answers) if answers else 0,
                'max': max(answers) if answers else 0,
                'distribution': self._calculate_rating_distribution(answers)
            }
        
        elif question['type'] == 'multiple_choice':
            return {
                'options': self._calculate_choice_distribution(answers)
            }
        
        elif question['type'] == 'yes_no':
            yes_count = sum(1 for a in answers if a)
            return {
                'yes_percentage': (yes_count / len(answers)) * 100 if answers else 0,
                'no_percentage': ((len(answers) - yes_count) / len(answers)) * 100 if answers else 0
            }
        
        else:
            return {
                'total_answers': len(answers)
            }
    
    def _calculate_rating_distribution(self, ratings: List[int]) -> Dict[int, int]:
        """Calcula distribuição de avaliações"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            if rating in distribution:
                distribution[rating] += 1
        return distribution
    
    def _calculate_choice_distribution(self, choices: List[Any]) -> Dict[str, int]:
        """Calcula distribuição de escolhas"""
        distribution = {}
        for choice in choices:
            choice_str = str(choice)
            distribution[choice_str] = distribution.get(choice_str, 0) + 1
        return distribution
    
    def _analyze_demographics(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa demografia dos respondentes"""
        # Simulação de análise demográfica
        return {
            'total_respondents': len(responses),
            'anonymous_responses': sum(1 for r in responses if not r.get('respondent_id')),
            'identified_responses': sum(1 for r in responses if r.get('respondent_id')),
            'device_distribution': self._analyze_device_distribution(responses)
        }
    
    def _analyze_device_distribution(self, responses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analisa distribuição de dispositivos"""
        devices = {}
        for response in responses:
            device_info = response.get('device_info', {})
            device_type = device_info.get('type', 'unknown')
            devices[device_type] = devices.get(device_type, 0) + 1
        return devices
    
    def _analyze_trends(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa tendências temporais"""
        if not responses:
            return {}
        
        # Agrupar por data
        daily_responses = {}
        for response in responses:
            date = response['submitted_at'].date()
            daily_responses[date] = daily_responses.get(date, 0) + 1
        
        return {
            'daily_submissions': daily_responses,
            'peak_day': max(daily_responses.items(), key=lambda x: x[1])[0] if daily_responses else None,
            'total_days': len(daily_responses)
        }
    
    def _generate_insights(self, survey: Dict[str, Any], responses: List[Dict[str, Any]]) -> List[str]:
        """Gera insights da pesquisa"""
        insights = []
        
        if survey['completion_rate'] < 0.5:
            insights.append("Low completion rate - consider simplifying the survey")
        
        if len(responses) < 10:
            insights.append("Limited responses - consider extending the survey period")
        
        avg_time = self._calculate_average_completion_time(responses)
        if avg_time > 300:  # 5 minutes
            insights.append("Long completion time - consider reducing survey length")
        
        return insights
    
    def _analyze_sentiment(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa sentimento das respostas"""
        # Simulação de análise de sentimento
        return {
            'positive': 0.6,
            'neutral': 0.3,
            'negative': 0.1,
            'overall_sentiment': 'positive'
        }
    
    def _analyze_correlations(self, survey: Dict[str, Any], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa correlações entre questões"""
        # Simulação de análise de correlação
        return {
            'strong_correlations': [],
            'moderate_correlations': [],
            'weak_correlations': []
        }
    
    def _generate_survey_id(self) -> str:
        """Gera ID único para pesquisa"""
        import hashlib
        import uuid
        content = f"survey_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_response_id(self) -> str:
        """Gera ID único para resposta"""
        import hashlib
        import uuid
        content = f"response_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _log_operation(self, operation: str, target: str, success: bool, details: str):
        """Log de operações do sistema"""
        level = 'INFO' if success else 'ERROR'
        timestamp = datetime.now().isoformat()
        print(f"[{level}] [{timestamp}] SurveysAPI.{operation}: {target} - {details}")


class TestSurveysAPI:
    """Testes para Surveys API"""
    
    @pytest.fixture
    def surveys_api(self):
        """Fixture para instância da API de pesquisas"""
        return SurveysAPI()
    
    @pytest.fixture
    def sample_survey_data(self):
        """Dados de pesquisa de exemplo"""
        return {
            'title': 'Customer Satisfaction Survey',
            'description': 'Help us improve our services',
            'questions': [
                {
                    'text': 'How satisfied are you with our service?',
                    'type': 'rating'
                },
                {
                    'text': 'What is your favorite feature?',
                    'type': 'multiple_choice'
                },
                {
                    'text': 'Would you recommend us to others?',
                    'type': 'yes_no'
                },
                {
                    'text': 'Any additional comments?',
                    'type': 'text'
                }
            ],
            'created_by': 'admin',
            'settings': {
                'allow_anonymous': True,
                'require_completion': False
            },
            'target_audience': ['customers', 'users'],
            'duration_days': 30,
            'metadata': {'category': 'feedback'}
        }
    
    @pytest.fixture
    def sample_response_data(self):
        """Dados de resposta de exemplo"""
        return {
            'answers': [4, 'Feature A', True, 'Great service overall!'],
            'respondent_id': 'user_123',
            'completion_time': 120,
            'device_info': {'type': 'desktop', 'browser': 'chrome'},
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0...',
            'metadata': {'source': 'web'}
        }
    
    def test_create_survey_success(self, surveys_api, sample_survey_data):
        """Teste de criação de pesquisa bem-sucedido"""
        # Arrange
        survey_data = sample_survey_data
        
        # Act
        result = surveys_api.create_survey(survey_data)
        
        # Assert
        assert result['success'] is True
        assert 'survey_id' in result
        assert 'survey' in result
        
        survey = result['survey']
        assert survey['title'] == survey_data['title']
        assert survey['description'] == survey_data['description']
        assert len(survey['questions']) == len(survey_data['questions'])
        assert survey['status'] == 'active'
        assert survey['created_by'] == survey_data['created_by']
        assert survey['response_count'] == 0
        assert survey['completion_rate'] == 0.0
    
    def test_collect_response_success(self, surveys_api, sample_survey_data, sample_response_data):
        """Teste de coleta de resposta bem-sucedido"""
        # Arrange
        create_result = surveys_api.create_survey(sample_survey_data)
        survey_id = create_result['survey_id']
        response_data = sample_response_data
        
        # Act
        result = surveys_api.collect_response(survey_id, response_data)
        
        # Assert
        assert result['success'] is True
        assert 'response_id' in result
        assert result['survey_id'] == survey_id
        assert 'submitted_at' in result
        
        # Verificar se resposta foi armazenada
        assert survey_id in surveys_api.responses
        assert len(surveys_api.responses[survey_id]) == 1
        
        # Verificar se estatísticas foram atualizadas
        survey = surveys_api.surveys[survey_id]
        assert survey['response_count'] == 1
        assert survey['completion_rate'] > 0
    
    def test_analyze_survey_results(self, surveys_api, sample_survey_data, sample_response_data):
        """Teste de análise de resultados"""
        # Arrange
        create_result = surveys_api.create_survey(sample_survey_data)
        survey_id = create_result['survey_id']
        
        # Coletar algumas respostas
        for i in range(5):
            response_data = sample_response_data.copy()
            response_data['answers'] = [4, f'Feature {chr(65+i)}', True, f'Comment {i}']
            response_data['respondent_id'] = f'user_{i}'
            surveys_api.collect_response(survey_id, response_data)
        
        # Act
        result = surveys_api.analyze_survey_results(survey_id)
        
        # Assert
        assert result['success'] is True
        assert 'analysis' in result
        
        analysis = result['analysis']
        assert analysis['survey_id'] == survey_id
        assert analysis['total_responses'] == 5
        assert analysis['completion_rate'] > 0
        assert 'question_analysis' in analysis
        assert 'demographics' in analysis
        assert 'trends' in analysis
        assert 'insights' in analysis
        
        # Verificar análise de questões
        question_analysis = analysis['question_analysis']
        assert len(question_analysis) == 4  # 4 questões
        
        # Verificar estatísticas da primeira questão (rating)
        first_question = question_analysis[0]
        assert first_question['question_type'] == 'rating'
        assert 'average' in first_question['statistics']
        assert first_question['statistics']['average'] == 4.0
    
    def test_surveys_edge_cases(self, surveys_api):
        """Teste de casos edge do sistema de pesquisas"""
        # Teste com dados inválidos
        invalid_survey = {'title': '', 'questions': []}
        result = surveys_api.create_survey(invalid_survey)
        assert result['success'] is False
        assert 'error' in result
        
        # Teste com muitas questões
        many_questions = [{'text': f'Question {i}', 'type': 'text'} for i in range(60)]
        large_survey = {'title': 'Large Survey', 'questions': many_questions}
        result = surveys_api.create_survey(large_survey)
        assert result['success'] is False
        assert 'Too many questions' in result['error']
        
        # Teste de resposta para pesquisa inexistente
        result = surveys_api.collect_response('nonexistent_id', {'answers': [1]})
        assert result['success'] is False
        assert result['error'] == 'Survey not found'
        
        # Teste de análise sem respostas
        create_result = surveys_api.create_survey({'title': 'Test', 'questions': [{'text': 'Q1', 'type': 'text'}]})
        survey_id = create_result['survey_id']
        
        result = surveys_api.analyze_survey_results(survey_id)
        assert result['success'] is False
        assert result['error'] == 'No responses found'
    
    def test_surveys_performance_large_scale(self, surveys_api):
        """Teste de performance em larga escala"""
        # Arrange
        survey_data = {
            'title': 'Performance Test Survey',
            'questions': [{'text': f'Question {i}', 'type': 'text'} for i in range(10)]
        }
        
        create_result = surveys_api.create_survey(survey_data)
        survey_id = create_result['survey_id']
        
        # Act & Assert
        start_time = datetime.now()
        
        for i in range(100):
            response_data = {
                'answers': [f'Answer {i}'] * 10,
                'respondent_id': f'user_{i}',
                'completion_time': 60 + i
            }
            result = surveys_api.collect_response(survey_id, response_data)
            assert result['success'] is True
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Performance deve ser aceitável (< 5 segundos para 100 respostas)
        assert duration < 5.0
        
        # Verificar se todas as respostas foram coletadas
        survey = surveys_api.surveys[survey_id]
        assert survey['response_count'] == 100
    
    def test_surveys_integration_with_analysis(self, surveys_api, sample_survey_data):
        """Teste de integração com análise"""
        # Arrange
        create_result = surveys_api.create_survey(sample_survey_data)
        survey_id = create_result['survey_id']
        
        # Coletar respostas variadas
        responses = [
            {'answers': [5, 'Feature A', True, 'Excellent!'], 'respondent_id': 'user_1'},
            {'answers': [3, 'Feature B', False, 'Could be better'], 'respondent_id': 'user_2'},
            {'answers': [4, 'Feature A', True, 'Good service'], 'respondent_id': 'user_3'},
            {'answers': [2, 'Feature C', False, 'Needs improvement'], 'respondent_id': 'user_4'},
            {'answers': [5, 'Feature B', True, 'Amazing!'], 'respondent_id': 'user_5'}
        ]
        
        for response_data in responses:
            surveys_api.collect_response(survey_id, response_data)
        
        # Act - Análise com configurações específicas
        analysis_config = {
            'include_sentiment_analysis': True,
            'include_correlation_analysis': True
        }
        result = surveys_api.analyze_survey_results(survey_id, analysis_config)
        
        # Assert
        assert result['success'] is True
        
        analysis = result['analysis']
        assert 'sentiment_analysis' in analysis
        assert 'correlation_analysis' in analysis
        
        # Verificar análise de sentimento
        sentiment = analysis['sentiment_analysis']
        assert 'positive' in sentiment
        assert 'negative' in sentiment
        assert 'overall_sentiment' in sentiment
    
    def test_surveys_configuration_validation(self, surveys_api):
        """Teste de configuração e validação do sistema"""
        # Teste de configuração padrão
        assert surveys_api.survey_config['max_questions'] == 50
        assert surveys_api.survey_config['max_responses'] == 10000
        assert surveys_api.survey_config['enable_anonymous'] is True
        assert surveys_api.survey_config['require_authentication'] is False
        assert surveys_api.survey_config['auto_close_days'] == 30
        
        # Teste de configuração customizada
        custom_config = {
            'max_questions': 20,
            'max_responses': 5000,
            'enable_anonymous': False,
            'require_authentication': True,
            'auto_close_days': 15
        }
        custom_api = SurveysAPI(custom_config)
        
        assert custom_api.survey_config['max_questions'] == 20
        assert custom_api.survey_config['max_responses'] == 5000
        assert custom_api.survey_config['enable_anonymous'] is False
        assert custom_api.survey_config['require_authentication'] is True
        assert custom_api.survey_config['auto_close_days'] == 15
    
    def test_surveys_logs_operation_tracking(self, surveys_api, sample_survey_data, capsys):
        """Teste de logs de operações do sistema"""
        # Act
        surveys_api.create_survey(sample_survey_data)
        surveys_api.get_survey_stats()
        
        # Assert
        captured = capsys.readouterr()
        log_output = captured.out
        
        # Verificar se logs foram gerados
        assert "SurveysAPI.create_survey" in log_output
        assert "SurveysAPI.get_survey_stats" in log_output
        assert "INFO" in log_output
    
    def test_surveys_metrics_collection(self, surveys_api, sample_survey_data, sample_response_data):
        """Teste de coleta de métricas do sistema"""
        # Arrange
        initial_stats = surveys_api.get_survey_stats()
        
        # Act - Simular uso do sistema
        create_result = surveys_api.create_survey(sample_survey_data)
        survey_id = create_result['survey_id']
        
        for i in range(3):
            response_data = sample_response_data.copy()
            response_data['respondent_id'] = f'user_{i}'
            surveys_api.collect_response(survey_id, response_data)
        
        surveys_api.analyze_survey_results(survey_id)
        
        # Assert
        final_stats = surveys_api.get_survey_stats()
        
        assert final_stats['total_surveys'] == 1
        assert final_stats['active_surveys'] == 1
        assert final_stats['total_responses'] == 3
        assert final_stats['surveys_created'] == 1
        assert final_stats['responses_collected'] == 3
        assert final_stats['analysis_generated'] == 1
        assert final_stats['total_participants'] == 3
        assert final_stats['avg_completion_rate'] > 0
    
    def test_surveys_reports_generation(self, surveys_api, sample_survey_data):
        """Teste de geração de relatórios do sistema"""
        # Arrange - Popular sistema com dados
        for i in range(3):
            survey_data = sample_survey_data.copy()
            survey_data['title'] = f'Survey {i+1}'
            create_result = surveys_api.create_survey(survey_data)
            survey_id = create_result['survey_id']
            
            # Adicionar algumas respostas
            for j in range(5):
                response_data = {
                    'answers': [4, f'Feature {j}', True, f'Comment {j}'],
                    'respondent_id': f'user_{i}_{j}'
                }
                surveys_api.collect_response(survey_id, response_data)
        
        # Act
        report = surveys_api.get_survey_stats()
        
        # Assert
        assert 'total_surveys' in report
        assert 'active_surveys' in report
        assert 'completed_surveys' in report
        assert 'total_responses' in report
        assert 'avg_completion_rate' in report
        assert 'surveys_created' in report
        assert 'responses_collected' in report
        assert 'analysis_generated' in report
        assert 'total_participants' in report
        assert 'last_updated' in report
        
        # Verificar valores específicos
        assert report['total_surveys'] == 3
        assert report['active_surveys'] == 3
        assert report['total_responses'] == 15  # 3 surveys * 5 responses
        assert report['surveys_created'] == 3
        assert report['responses_collected'] == 15
        assert report['total_participants'] == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 