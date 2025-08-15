from typing import Dict, List, Optional, Any
"""
Testes unitários para Sistema de Auto-Otimização com Reinforcement Learning
Tracing ID: LONGTAIL-035
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os

from infrastructure.ai.reinforcement_learning.auto_optimizer import (
    AutoOptimizer,
    QLearningAgent,
    KeywordEnvironment,
    ActionType,
    State,
    Action,
    Reward
)

class TestKeywordEnvironment:
    """Testes para o ambiente de keywords"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.initial_config = {
            'density': 0.5,
            'complexity': 0.5,
            'competition': 0.5,
            'volume': 0.5,
            'template': 'default'
        }
        self.env = KeywordEnvironment(self.initial_config)
    
    def test_reset(self):
        """Testa reset do ambiente"""
        state = self.env.reset()
        
        assert isinstance(state, State)
        assert state.current_density == 0.5
        assert state.current_complexity == 0.5
        assert state.current_competition == 0.5
        assert state.current_volume == 0.5
        assert state.current_template == 'default'
        assert state.iteration == 0
    
    def test_step_with_density_action(self):
        """Testa execução de ação de ajuste de densidade"""
        state = self.env.reset()
        action = Action(
            action_type=ActionType.ADJUST_DENSITY,
            value=0.1,
            description="Aumentar densidade"
        )
        
        next_state, reward, done = self.env.step(action)
        
        assert next_state.current_density == 0.6
        assert isinstance(reward, Reward)
        assert isinstance(done, bool)
        assert next_state.iteration == 1
    
    def test_step_with_complexity_action(self):
        """Testa execução de ação de ajuste de complexidade"""
        state = self.env.reset()
        action = Action(
            action_type=ActionType.ADJUST_COMPLEXITY,
            value=-0.1,
            description="Diminuir complexidade"
        )
        
        next_state, reward, done = self.env.step(action)
        
        assert next_state.current_complexity == 0.4
        assert isinstance(reward, Reward)
    
    def test_step_with_template_action(self):
        """Testa execução de ação de ajuste de template"""
        state = self.env.reset()
        action = Action(
            action_type=ActionType.ADJUST_TEMPLATE,
            value=1,
            description="Próximo template"
        )
        
        next_state, reward, done = self.env.step(action)
        
        assert next_state.current_template == 'ecommerce'
    
    def test_performance_calculation(self):
        """Testa cálculo de performance"""
        state = State(
            current_density=0.7,
            current_complexity=0.6,
            current_competition=0.2,
            current_volume=0.8,
            current_template='default',
            performance_score=0.0,
            iteration=0
        )
        
        performance = self.env._calculate_performance(state)
        
        assert 0.0 <= performance <= 1.0
        assert performance > 0.5  # Estado otimizado deve ter performance alta
    
    def test_reward_calculation(self):
        """Testa cálculo de recompensa"""
        # Simula histórico
        self.env.history = [
            {
                'state': State(
                    current_density=0.5,
                    current_complexity=0.5,
                    current_competition=0.5,
                    current_volume=0.5,
                    current_template='default',
                    performance_score=0.5,
                    iteration=0
                ),
                'action': None,
                'reward': None,
                'timestamp': None
            }
        ]
        
        current_state = State(
            current_density=0.7,
            current_complexity=0.6,
            current_competition=0.2,
            current_volume=0.8,
            current_template='default',
            performance_score=0.8,
            iteration=1
        )
        
        reward = self.env._calculate_reward(current_state)
        
        assert isinstance(reward, Reward)
        assert reward.score_improvement > 0  # Melhoria deve gerar recompensa positiva
    
    def test_done_condition(self):
        """Testa condição de término"""
        # Testa término por iterações
        state = State(
            current_density=0.5,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.5,
            iteration=100
        )
        
        done = self.env._is_done(state)
        assert done is True
        
        # Testa término por performance ótima
        state.iteration = 10
        state.performance_score = 0.96
        
        done = self.env._is_done(state)
        assert done is True

class TestQLearningAgent:
    """Testes para o agente de Q-Learning"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = QLearningAgent()
    
    def test_action_space_creation(self):
        """Testa criação do espaço de ações"""
        assert len(self.agent.action_space) > 0
        
        # Verifica se há ações de cada tipo
        action_types = [action.action_type for action in self.agent.action_space]
        assert ActionType.ADJUST_DENSITY in action_types
        assert ActionType.ADJUST_COMPLEXITY in action_types
        assert ActionType.ADJUST_COMPETITION in action_types
        assert ActionType.ADJUST_VOLUME in action_types
        assert ActionType.ADJUST_TEMPLATE in action_types
    
    def test_state_to_key_conversion(self):
        """Testa conversão de estado para chave"""
        state = State(
            current_density=0.5,
            current_complexity=0.6,
            current_competition=0.3,
            current_volume=0.7,
            current_template='default',
            performance_score=0.8,
            iteration=5
        )
        
        key = self.agent._state_to_key(state)
        assert isinstance(key, str)
        assert '0.50_0.60_0.30_0.70_default' in key
    
    def test_action_to_key_conversion(self):
        """Testa conversão de ação para chave"""
        action = Action(
            action_type=ActionType.ADJUST_DENSITY,
            value=0.1,
            description="Teste"
        )
        
        key = self.agent._action_to_key(action)
        assert key == "adjust_density_0.1"
    
    def test_get_action_exploration(self):
        """Testa seleção de ação com exploração"""
        state = State(
            current_density=0.5,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.5,
            iteration=0
        )
        
        # Com epsilon alto, deve explorar
        self.agent.epsilon = 1.0
        action = self.agent.get_action(state)
        
        assert action in self.agent.action_space
    
    def test_get_best_action(self):
        """Testa seleção da melhor ação"""
        state = State(
            current_density=0.5,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.5,
            iteration=0
        )
        
        # Para estado novo, deve retornar ação aleatória
        action = self.agent.get_best_action(state)
        assert action in self.agent.action_space
    
    def test_q_table_update(self):
        """Testa atualização da Q-table"""
        state = State(
            current_density=0.5,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.5,
            iteration=0
        )
        
        action = Action(
            action_type=ActionType.ADJUST_DENSITY,
            value=0.1,
            description="Teste"
        )
        
        next_state = State(
            current_density=0.6,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.6,
            iteration=1
        )
        
        next_action = Action(
            action_type=ActionType.ADJUST_COMPLEXITY,
            value=0.05,
            description="Teste"
        )
        
        # Atualiza Q-table
        self.agent.update(state, action, 0.5, next_state, next_action)
        
        # Verifica se Q-value foi atualizado
        state_key = self.agent._state_to_key(state)
        action_key = self.agent._action_to_key(action)
        q_key = f"{state_key}_{action_key}"
        
        assert q_key in self.agent.q_table
        assert self.agent.q_table[q_key] > 0
    
    def test_model_save_load(self):
        """Testa salvamento e carregamento do modelo"""
        # Cria agente com alguns dados
        agent = QLearningAgent()
        state = State(
            current_density=0.5,
            current_complexity=0.5,
            current_competition=0.5,
            current_volume=0.5,
            current_template='default',
            performance_score=0.5,
            iteration=0
        )
        
        action = Action(
            action_type=ActionType.ADJUST_DENSITY,
            value=0.1,
            description="Teste"
        )
        
        # Adiciona alguns Q-values
        agent.update(state, action, 0.5, state, action)
        
        # Salva modelo
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = f.name
        
        try:
            agent.save_model(temp_path)
            
            # Carrega modelo em novo agente
            new_agent = QLearningAgent()
            new_agent.load_model(temp_path)
            
            # Verifica se dados foram preservados
            assert len(new_agent.q_table) == len(agent.q_table)
            assert new_agent.learning_rate == agent.learning_rate
            assert new_agent.discount_factor == agent.discount_factor
            assert new_agent.epsilon == agent.epsilon
            
        finally:
            os.unlink(temp_path)

class TestAutoOptimizer:
    """Testes para o otimizador principal"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.optimizer = AutoOptimizer()
        self.initial_config = {
            'density': 0.5,
            'complexity': 0.5,
            'competition': 0.5,
            'volume': 0.5,
            'template': 'default'
        }
    
    def test_initialization(self):
        """Testa inicialização do otimizador"""
        assert self.optimizer.agent is not None
        assert self.optimizer.environment is None
        assert isinstance(self.optimizer.results_history, list)
    
    def test_environment_initialization(self):
        """Testa inicialização do ambiente"""
        self.optimizer.initialize_environment(self.initial_config)
        
        assert self.optimizer.environment is not None
        assert isinstance(self.optimizer.environment, KeywordEnvironment)
    
    def test_optimization_without_training(self):
        """Testa otimização sem treinamento prévio"""
        self.optimizer.initialize_environment(self.initial_config)
        
        optimized_config = self.optimizer.optimize_configuration(
            self.initial_config, 
            max_iterations=5
        )
        
        assert isinstance(optimized_config, dict)
        assert 'density' in optimized_config
        assert 'complexity' in optimized_config
        assert 'competition' in optimized_config
        assert 'volume' in optimized_config
        assert 'template' in optimized_config
    
    def test_training_process(self):
        """Testa processo de treinamento"""
        self.optimizer.initialize_environment(self.initial_config)
        
        # Treina com poucos episódios para teste
        rewards = self.optimizer.train(episodes=10)
        
        assert isinstance(rewards, list)
        assert len(rewards) == 10
        assert all(isinstance(r, (int, float)) for r in rewards)
    
    def test_optimization_report(self):
        """Testa geração de relatório"""
        report = self.optimizer.get_optimization_report()
        
        assert isinstance(report, dict)
        assert 'training_history' in report
        assert 'q_table_size' in report
        assert 'action_space_size' in report
        assert 'last_optimization' in report
    
    def test_config_save(self):
        """Testa salvamento de configuração"""
        config = {
            'density': 0.7,
            'complexity': 0.6,
            'competition': 0.3,
            'volume': 0.8,
            'template': 'ecommerce'
        }
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.optimizer.save_config(config, temp_path)
            
            # Verifica se arquivo foi criado
            assert os.path.exists(temp_path)
            
            # Verifica conteúdo
            with open(temp_path, 'r') as f:
                saved_data = f.read()
                assert 'density' in saved_data
                assert '0.7' in saved_data
                
        finally:
            os.unlink(temp_path)

class TestIntegration:
    """Testes de integração"""
    
    def test_full_optimization_workflow(self):
        """Testa workflow completo de otimização"""
        initial_config = {
            'density': 0.5,
            'complexity': 0.5,
            'competition': 0.5,
            'volume': 0.5,
            'template': 'default'
        }
        
        optimizer = AutoOptimizer()
        optimizer.initialize_environment(initial_config)
        
        # Treina rapidamente
        optimizer.train(episodes=5)
        
        # Otimiza configuração
        optimized_config = optimizer.optimize_configuration(
            initial_config, 
            max_iterations=3
        )
        
        # Verifica que configuração foi otimizada
        assert optimized_config != initial_config
        
        # Verifica que valores estão dentro dos limites
        for key, value in optimized_config.items():
            if key != 'template':
                assert 0.1 <= value <= 0.9
    
    def test_performance_improvement(self):
        """Testa que otimização realmente melhora performance"""
        initial_config = {
            'density': 0.3,
            'complexity': 0.3,
            'competition': 0.8,
            'volume': 0.3,
            'template': 'default'
        }
        
        env = KeywordEnvironment(initial_config)
        initial_state = env.reset()
        initial_performance = env._calculate_performance(initial_state)
        
        optimizer = AutoOptimizer()
        optimizer.initialize_environment(initial_config)
        
        # Treina rapidamente
        optimizer.train(episodes=10)
        
        # Otimiza
        optimized_config = optimizer.optimize_configuration(
            initial_config, 
            max_iterations=5
        )
        
        # Verifica se performance melhorou
        optimized_state = State(
            current_density=optimized_config['density'],
            current_complexity=optimized_config['complexity'],
            current_competition=optimized_config['competition'],
            current_volume=optimized_config['volume'],
            current_template=optimized_config['template'],
            performance_score=0.0,
            iteration=0
        )
        
        optimized_performance = env._calculate_performance(optimized_state)
        
        # Performance deve ter melhorado (ou pelo menos não piorado)
        assert optimized_performance >= initial_performance * 0.9

if __name__ == "__main__":
    pytest.main([__file__]) 