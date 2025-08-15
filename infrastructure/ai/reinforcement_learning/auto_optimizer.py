"""
Sistema de Auto-Otimização com Reinforcement Learning
===================================================

Este módulo implementa um sistema de auto-otimização usando Reinforcement Learning
para ajustar automaticamente parâmetros de cauda longa baseado em feedback e resultados.

Tracing ID: RL_OPT_001
Data: 2024-12-20
Autor: Sistema de IA Generativa
"""

import numpy as np
import pandas as pd
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import random
import pickle
from pathlib import Path

# ML Libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch não disponível. Usando implementação simplificada.")

# Observability
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationAction(Enum):
    """Ações de otimização disponíveis"""
    INCREASE_VOLUME_WEIGHT = "increase_volume_weight"
    DECREASE_VOLUME_WEIGHT = "decrease_volume_weight"
    INCREASE_CPC_WEIGHT = "increase_cpc_weight"
    DECREASE_CPC_WEIGHT = "decrease_cpc_weight"
    INCREASE_COMPETITION_WEIGHT = "increase_competition_weight"
    DECREASE_COMPETITION_WEIGHT = "decrease_competition_weight"
    ADJUST_SEMANTIC_THRESHOLD = "adjust_semantic_threshold"
    ADJUST_COMPLEXITY_THRESHOLD = "adjust_complexity_threshold"
    MAINTAIN_CURRENT = "maintain_current"


class OptimizationState(Enum):
    """Estados do sistema de otimização"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    CONVERGED = "converged"
    STAGNANT = "stagnant"


@dataclass
class OptimizationConfig:
    """Configuração de otimização"""
    # Pesos iniciais
    volume_weight: float = 0.3
    cpc_weight: float = 0.25
    competition_weight: float = 0.15
    intent_weight: float = 0.2
    trend_weight: float = 0.1
    
    # Thresholds
    semantic_threshold: float = 0.7
    complexity_threshold: float = 0.6
    
    # Parâmetros de otimização
    learning_rate: float = 0.01
    exploration_rate: float = 0.1
    discount_factor: float = 0.95
    
    # Limites
    min_weight: float = 0.05
    max_weight: float = 0.5
    min_threshold: float = 0.3
    max_threshold: float = 0.9


@dataclass
class OptimizationResult:
    """Resultado de uma otimização"""
    config: OptimizationConfig
    performance_score: float
    improvement: float
    action_taken: OptimizationAction
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QLearningAgent:
    """Agente Q-Learning para otimização"""
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = 0.95
        self.epsilon = 0.1
        
        # Q-table (estado -> ação -> valor)
        self.q_table = np.zeros((state_size, action_size))
        
        # Histórico de experiências
        self.experiences = []
        
        logger.info(f"Agente Q-Learning inicializado: {state_size} estados, {action_size} ações")
    
    def get_state_index(self, config: OptimizationConfig) -> int:
        """Converte configuração em índice de estado"""
        # Discretizar os parâmetros em bins
        volume_bin = int(config.volume_weight * 10)  # 0-5 bins
        cpc_bin = int(config.cpc_weight * 10)
        semantic_bin = int(config.semantic_threshold * 10)
        
        # Combinar bins em um índice único
        state_index = volume_bin * 100 + cpc_bin * 10 + semantic_bin
        return min(state_index, self.state_size - 1)
    
    def choose_action(self, state_index: int, exploration: bool = True) -> int:
        """Escolhe ação baseada no estado atual"""
        if exploration and random.random() < self.epsilon:
            # Exploração: ação aleatória
            return random.randint(0, self.action_size - 1)
        else:
            # Exploitação: melhor ação conhecida
            return np.argmax(self.q_table[state_index])
    
    def update_q_value(self, state: int, action: int, reward: float, next_state: int):
        """Atualiza valor Q baseado na experiência"""
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        
        # Equação de Bellman
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state, action] = new_q
    
    def save_model(self, filepath: str):
        """Salva o modelo Q-Learning"""
        model_data = {
            'q_table': self.q_table,
            'experiences': self.experiences,
            'state_size': self.state_size,
            'action_size': self.action_size
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"Modelo Q-Learning salvo: {filepath}")
    
    def load_model(self, filepath: str):
        """Carrega o modelo Q-Learning"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_table = model_data['q_table']
            self.experiences = model_data['experiences']
            self.state_size = model_data['state_size']
            self.action_size = model_data['action_size']
            
            logger.info(f"Modelo Q-Learning carregado: {filepath}")
        except Exception as e:
            logger.warning(f"Erro ao carregar modelo: {e}")


class KeywordEnvironment:
    """Ambiente de simulação para keywords"""
    
    def __init__(self, historical_data: Optional[pd.DataFrame] = None):
        self.historical_data = historical_data or self._generate_mock_data()
        self.current_step = 0
        self.max_steps = 1000
        
        logger.info("Ambiente de keywords inicializado")
    
    def _generate_mock_data(self) -> pd.DataFrame:
        """Gera dados mock para simulação"""
        np.random.seed(42)
        
        data = []
        for index in range(1000):
            data.append({
                'keyword': f'keyword_{index}',
                'volume': np.random.randint(100, 10000),
                'cpc': np.random.uniform(0.5, 5.0),
                'competition': np.random.uniform(0.1, 0.9),
                'intent_score': np.random.uniform(0.3, 0.9),
                'trend_score': np.random.uniform(0.2, 0.8),
                'semantic_score': np.random.uniform(0.4, 0.9),
                'complexity_score': np.random.uniform(0.3, 0.8),
                'performance': np.random.uniform(0.1, 1.0)
            })
        
        return pd.DataFrame(data)
    
    def reset(self) -> OptimizationConfig:
        """Reseta o ambiente"""
        self.current_step = 0
        return OptimizationConfig()
    
    def step(self, config: OptimizationConfig, action: OptimizationAction) -> Tuple[OptimizationConfig, float, bool]:
        """Executa um passo no ambiente"""
        self.current_step += 1
        
        # Aplicar ação
        new_config = self._apply_action(config, action)
        
        # Calcular recompensa
        reward = self._calculate_reward(new_config)
        
        # Verificar se terminou
        done = self.current_step >= self.max_steps
        
        return new_config, reward, done
    
    def _apply_action(self, config: OptimizationConfig, action: OptimizationAction) -> OptimizationConfig:
        """Aplica ação na configuração"""
        new_config = OptimizationConfig(
            volume_weight=config.volume_weight,
            cpc_weight=config.cpc_weight,
            competition_weight=config.competition_weight,
            intent_weight=config.intent_weight,
            trend_weight=config.trend_weight,
            semantic_threshold=config.semantic_threshold,
            complexity_threshold=config.complexity_threshold
        )
        
        step_size = 0.05
        
        if action == OptimizationAction.INCREASE_VOLUME_WEIGHT:
            new_config.volume_weight = min(config.volume_weight + step_size, self.max_weight)
        elif action == OptimizationAction.DECREASE_VOLUME_WEIGHT:
            new_config.volume_weight = max(config.volume_weight - step_size, self.min_weight)
        elif action == OptimizationAction.INCREASE_CPC_WEIGHT:
            new_config.cpc_weight = min(config.cpc_weight + step_size, self.max_weight)
        elif action == OptimizationAction.DECREASE_CPC_WEIGHT:
            new_config.cpc_weight = max(config.cpc_weight - step_size, self.min_weight)
        elif action == OptimizationAction.INCREASE_COMPETITION_WEIGHT:
            new_config.competition_weight = min(config.competition_weight + step_size, self.max_weight)
        elif action == OptimizationAction.DECREASE_COMPETITION_WEIGHT:
            new_config.competition_weight = max(config.competition_weight - step_size, self.min_weight)
        elif action == OptimizationAction.ADJUST_SEMANTIC_THRESHOLD:
            new_config.semantic_threshold = np.clip(
                config.semantic_threshold + random.uniform(-0.1, 0.1),
                self.min_threshold, self.max_threshold
            )
        elif action == OptimizationAction.ADJUST_COMPLEXITY_THRESHOLD:
            new_config.complexity_threshold = np.clip(
                config.complexity_threshold + random.uniform(-0.1, 0.1),
                self.min_threshold, self.max_threshold
            )
        
        # Normalizar pesos para somar 1.0
        total_weight = (new_config.volume_weight + new_config.cpc_weight + 
                       new_config.competition_weight + new_config.intent_weight + 
                       new_config.trend_weight)
        
        new_config.volume_weight /= total_weight
        new_config.cpc_weight /= total_weight
        new_config.competition_weight /= total_weight
        new_config.intent_weight /= total_weight
        new_config.trend_weight /= total_weight
        
        return new_config
    
    def _calculate_reward(self, config: OptimizationConfig) -> float:
        """Calcula recompensa baseada na configuração"""
        # Simular performance com dados históricos
        sample_data = self.historical_data.sample(min(100, len(self.historical_data)))
        
        # Calcular score composto
        scores = []
        for _, row in sample_data.iterrows():
            score = (
                row['volume'] * config.volume_weight +
                row['cpc'] * config.cpc_weight +
                (1 - row['competition']) * config.competition_weight +
                row['intent_score'] * config.intent_weight +
                row['trend_score'] * config.trend_weight
            )
            
            # Aplicar thresholds
            if row['semantic_score'] >= config.semantic_threshold and \
               row['complexity_score'] >= config.complexity_threshold:
                scores.append(score)
        
        if not scores:
            return 0.0
        
        avg_score = np.mean(scores)
        return avg_score


class RewardFunction:
    """Função de recompensa para otimização"""
    
    def __init__(self):
        self.performance_history = []
        self.improvement_threshold = 0.01
        
    def calculate_reward(self, 
                        current_performance: float, 
                        previous_performance: float,
                        config: OptimizationConfig) -> float:
        """Calcula recompensa baseada na melhoria de performance"""
        
        # Recompensa baseada na melhoria
        improvement = current_performance - previous_performance
        
        if improvement > self.improvement_threshold:
            reward = improvement * 10  # Recompensa positiva para melhorias
        elif improvement > 0:
            reward = improvement * 5   # Recompensa menor para melhorias pequenas
        elif improvement < -self.improvement_threshold:
            reward = improvement * 2   # Penalidade para pioras
        else:
            reward = 0  # Recompensa neutra para mudanças pequenas
        
        # Penalidade por configurações extremas
        extreme_penalty = 0
        if config.volume_weight > 0.8 or config.volume_weight < 0.1:
            extreme_penalty -= 0.1
        if config.cpc_weight > 0.8 or config.cpc_weight < 0.1:
            extreme_penalty -= 0.1
        if config.semantic_threshold > 0.9 or config.semantic_threshold < 0.3:
            extreme_penalty -= 0.1
        
        reward += extreme_penalty
        
        # Armazenar histórico
        self.performance_history.append(current_performance)
        
        return reward


class AutoOptimizer:
    """
    Sistema de Auto-Otimização com Reinforcement Learning
    
    Características:
    - Q-Learning para otimização de parâmetros
    - Ambiente de simulação de keywords
    - Função de recompensa baseada em performance
    - Exploração vs. exploração balanceada
    - Persistência de modelos treinados
    - Integração com observabilidade
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 enable_observability: bool = True):
        """
        Inicializa o auto-otimizador
        
        Args:
            model_path: Caminho para carregar modelo salvo
            enable_observability: Habilita integração com observabilidade
        """
        # Configurações
        self.state_size = 1000  # Estados discretizados
        self.action_size = len(OptimizationAction)
        
        # Componentes RL
        self.agent = QLearningAgent(self.state_size, self.action_size)
        self.environment = KeywordEnvironment()
        self.reward_function = RewardFunction()
        
        # Estado atual
        self.current_config = OptimizationConfig()
        self.best_config = OptimizationConfig()
        self.best_performance = 0.0
        
        # Histórico
        self.optimization_history: List[OptimizationResult] = []
        self.performance_history: List[float] = []
        
        # Observabilidade
        self.telemetry = None
        self.tracing = None
        self.metrics = None
        
        if enable_observability:
            try:
                self.telemetry = TelemetryManager()
                self.tracing = TracingManager()
                self.metrics = MetricsManager()
                logger.info("Observabilidade integrada ao Auto-Optimizer")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Carregar modelo se existir
        if model_path and Path(model_path).exists():
            self.agent.load_model(model_path)
            logger.info(f"Modelo carregado: {model_path}")
        
        logger.info("Auto-Optimizer inicializado com RL")
    
    async def optimize_parameters(self, 
                                iterations: int = 100,
                                exploration_rate: float = 0.1) -> OptimizationConfig:
        """
        Otimiza parâmetros usando RL
        
        Args:
            iterations: Número de iterações de treinamento
            exploration_rate: Taxa de exploração
            
        Returns:
            Configuração otimizada
        """
        with self.tracing.start_span("optimize_parameters") if self.tracing else nullcontext():
            logger.info(f"Iniciando otimização com {iterations} iterações")
            
            # Resetar ambiente
            current_config = self.environment.reset()
            self.agent.epsilon = exploration_rate
            
            best_reward = float('-inf')
            
            for episode in range(iterations):
                # Estado atual
                state_index = self.agent.get_state_index(current_config)
                
                # Escolher ação
                action_index = self.agent.choose_action(state_index, exploration=True)
                action = list(OptimizationAction)[action_index]
                
                # Executar ação no ambiente
                new_config, reward, done = self.environment.step(current_config, action)
                
                # Próximo estado
                next_state_index = self.agent.get_state_index(new_config)
                
                # Atualizar Q-table
                self.agent.update_q_value(state_index, action_index, reward, next_state_index)
                
                # Armazenar experiência
                self.agent.experiences.append({
                    'state': state_index,
                    'action': action_index,
                    'reward': reward,
                    'next_state': next_state_index,
                    'config': current_config,
                    'episode': episode
                })
                
                # Atualizar melhor configuração
                if reward > best_reward:
                    best_reward = reward
                    self.best_config = new_config
                    self.best_performance = reward
                
                # Registrar resultado
                result = OptimizationResult(
                    config=new_config,
                    performance_score=reward,
                    improvement=reward - (self.performance_history[-1] if self.performance_history else 0),
                    action_taken=action,
                    metadata={'episode': episode, 'exploration_rate': exploration_rate}
                )
                
                self.optimization_history.append(result)
                self.performance_history.append(reward)
                
                # Métricas
                if self.metrics:
                    self.metrics.record_gauge("rl_optimization_reward", reward)
                    self.metrics.record_gauge("rl_optimization_episode", episode)
                
                # Log periódico
                if episode % 10 == 0:
                    logger.info(f"Episódio {episode}: Reward={reward:.4f}, Best={best_reward:.4f}")
                
                current_config = new_config
                
                if done:
                    break
            
            # Salvar modelo
            self._save_model()
            
            logger.info(f"Otimização concluída. Melhor performance: {best_reward:.4f}")
            
            if self.metrics:
                self.metrics.increment_counter("rl_optimization_completed")
            
            return self.best_config
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da otimização"""
        if not self.optimization_history:
            return {"error": "Nenhuma otimização realizada"}
        
        recent_results = self.optimization_history[-50:]  # Últimos 50 resultados
        
        stats = {
            "total_optimizations": len(self.optimization_history),
            "best_performance": self.best_performance,
            "current_performance": self.performance_history[-1] if self.performance_history else 0,
            "average_improvement": np.mean([r.improvement for r in recent_results]),
            "performance_trend": self._calculate_trend(self.performance_history),
            "most_used_actions": self._get_most_used_actions(),
            "convergence_status": self._check_convergence(),
            "best_config": {
                "volume_weight": self.best_config.volume_weight,
                "cpc_weight": self.best_config.cpc_weight,
                "competition_weight": self.best_config.competition_weight,
                "semantic_threshold": self.best_config.semantic_threshold,
                "complexity_threshold": self.best_config.complexity_threshold
            }
        }
        
        return stats
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendência dos valores"""
        if len(values) < 10:
            return "insufficient_data"
        
        recent_values = values[-10:]
        slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _get_most_used_actions(self) -> Dict[str, int]:
        """Obtém ações mais utilizadas"""
        action_counts = {}
        for result in self.optimization_history[-100:]:  # Últimos 100
            action = result.action_taken.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return dict(sorted(action_counts.items(), key=lambda value: value[1], reverse=True))
    
    def _check_convergence(self) -> str:
        """Verifica se a otimização convergiu"""
        if len(self.performance_history) < 20:
            return "insufficient_data"
        
        recent_performance = self.performance_history[-20:]
        std_dev = np.std(recent_performance)
        
        if std_dev < 0.01:
            return "converged"
        elif std_dev < 0.05:
            return "stabilizing"
        else:
            return "exploring"
    
    def _save_model(self, filepath: Optional[str] = None):
        """Salva modelo treinado"""
        if filepath is None:
            filepath = f"models/auto_optimizer_rl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        # Criar diretório se não existir
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        self.agent.save_model(filepath)
        logger.info(f"Modelo salvo: {filepath}")
    
    def get_recommendations(self) -> List[str]:
        """Obtém recomendações baseadas na otimização"""
        recommendations = []
        
        if not self.optimization_history:
            return ["Execute otimização primeiro"]
        
        stats = self.get_optimization_stats()
        
        # Recomendações baseadas em performance
        if stats["performance_trend"] == "improving":
            recommendations.append("Otimização está melhorando. Continue o processo.")
        elif stats["performance_trend"] == "declining":
            recommendations.append("Performance em declínio. Considere ajustar parâmetros de exploração.")
        
        # Recomendações baseadas em convergência
        if stats["convergence_status"] == "converged":
            recommendations.append("Sistema convergiu. Considere reduzir taxa de exploração.")
        elif stats["convergence_status"] == "exploring":
            recommendations.append("Sistema ainda explorando. Mantenha taxa de exploração atual.")
        
        # Recomendações baseadas em ações
        most_used = stats["most_used_actions"]
        if most_used:
            top_action = list(most_used.keys())[0]
            recommendations.append(f"Ação mais efetiva: {top_action}")
        
        return recommendations


# Context manager para compatibilidade
class nullcontext:
    def __enter__(self): return None
    def __exit__(self, *args): return None


# Função de conveniência para uso rápido
async def auto_optimize_keyword_parameters(iterations: int = 100) -> OptimizationConfig:
    """
    Função de conveniência para auto-otimização rápida
    
    Args:
        iterations: Número de iterações
        
    Returns:
        Configuração otimizada
    """
    optimizer = AutoOptimizer()
    return await optimizer.optimize_parameters(iterations=iterations) 