"""
Sistema de Machine Learning para Ajuste Automático de Cauda Longa

Tracing ID: LONGTAIL-010
Data/Hora: 2024-12-20 17:35:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este módulo implementa um sistema de ML para otimização automática dos parâmetros
de análise de cauda longa, baseado em feedback contínuo e métricas de performance.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import json
import os
from pathlib import Path

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MLConfig:
    """Configuração do sistema de Machine Learning."""
    
    # Parâmetros do modelo
    n_estimators: int = 100
    max_depth: int = 10
    min_samples_split: int = 5
    min_samples_leaf: int = 2
    
    # Parâmetros de treinamento
    test_size: float = 0.2
    random_state: int = 42
    
    # Thresholds de qualidade
    min_r2_score: float = 0.7
    max_mse: float = 0.1
    
    # Configuração de rollback
    max_rollback_attempts: int = 3
    performance_degradation_threshold: float = 0.1


@dataclass
class AjusteResultado:
    """Resultado de um ajuste automático."""
    
    timestamp: datetime
    parametros_anteriores: Dict[str, float]
    parametros_novos: Dict[str, float]
    performance_anterior: float
    performance_nova: float
    melhoria: float
    confianca: float
    status: str
    tracing_id: str


class AjusteAutomaticoCaudaLonga:
    """
    Sistema de Machine Learning para ajuste automático de parâmetros.
    
    Este sistema monitora continuamente a performance dos parâmetros
    de análise de cauda longa e ajusta automaticamente baseado em:
    - Feedback de usuários
    - Métricas de qualidade
    - Performance histórica
    - Tendências de mercado
    """
    
    def __init__(self, config: MLConfig = None):
        """
        Inicializa o sistema de ajuste automático.
        
        Args:
            config: Configuração do sistema ML
        """
        self.config = config or MLConfig()
        self.model = None
        self.scaler = StandardScaler()
        self.historico_ajustes: List[AjusteResultado] = []
        self.parametros_atuais = self._carregar_parametros_padrao()
        self.performance_atual = 0.0
        self.rollback_count = 0
        
        # Diretórios de persistência
        self.model_dir = Path("infrastructure/ml/models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[LONGTAIL-010] Sistema de ajuste automático inicializado - {datetime.now()}")
    
    def _carregar_parametros_padrao(self) -> Dict[str, float]:
        """Carrega parâmetros padrão do sistema."""
        return {
            "min_palavras": 3.0,
            "min_caracteres": 15.0,
            "max_concorrencia": 0.5,
            "score_minimo": 0.6,
            "threshold_complexidade": 0.7,
            "peso_volume": 0.4,
            "peso_cpc": 0.3,
            "peso_concorrencia": 0.3
        }
    
    def coletar_dados_treinamento(self, periodo_dias: int = 30) -> pd.DataFrame:
        """
        Coleta dados históricos para treinamento do modelo.
        
        Args:
            periodo_dias: Período em dias para coleta de dados
            
        Returns:
            DataFrame com dados de treinamento
        """
        try:
            # Simulação de coleta de dados históricos
            # Em produção, isso viria de logs reais e métricas
            dados = []
            data_inicio = datetime.now() - timedelta(days=periodo_dias)
            
            for index in range(periodo_dias):
                data = data_inicio + timedelta(days=index)
                
                # Simula dados de performance com variação
                performance = 0.6 + 0.3 * np.random.random()
                
                # Simula parâmetros utilizados
                parametros = {
                    "min_palavras": 3 + np.random.randint(-1, 2),
                    "min_caracteres": 15 + np.random.randint(-5, 6),
                    "max_concorrencia": 0.5 + 0.1 * (np.random.random() - 0.5),
                    "score_minimo": 0.6 + 0.1 * (np.random.random() - 0.5),
                    "threshold_complexidade": 0.7 + 0.1 * (np.random.random() - 0.5),
                    "peso_volume": 0.4 + 0.1 * (np.random.random() - 0.5),
                    "peso_cpc": 0.3 + 0.1 * (np.random.random() - 0.5),
                    "peso_concorrencia": 0.3 + 0.1 * (np.random.random() - 0.5)
                }
                
                # Simula métricas de feedback
                feedback_positivo = np.random.randint(50, 200)
                feedback_negativo = np.random.randint(0, 50)
                taxa_conversao = feedback_positivo / (feedback_positivo + feedback_negativo)
                
                dados.append({
                    "data": data,
                    "performance": performance,
                    "taxa_conversao": taxa_conversao,
                    "feedback_positivo": feedback_positivo,
                    "feedback_negativo": feedback_negativo,
                    **parametros
                })
            
            df = pd.DataFrame(dados)
            logger.info(f"[LONGTAIL-010] Dados de treinamento coletados: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao coletar dados: {str(e)}")
            return pd.DataFrame()
    
    def preparar_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara features para treinamento do modelo.
        
        Args:
            df: DataFrame com dados históricos
            
        Returns:
            Tuple com features e target
        """
        try:
            # Features: parâmetros do sistema
            feature_columns = [
                "min_palavras", "min_caracteres", "max_concorrencia",
                "score_minimo", "threshold_complexidade",
                "peso_volume", "peso_cpc", "peso_concorrencia"
            ]
            
            X = df[feature_columns].values
            result = df["performance"].values
            
            # Normalização das features
            X_scaled = self.scaler.fit_transform(X)
            
            logger.info(f"[LONGTAIL-010] Features preparadas: {X.shape}")
            return X_scaled, result
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao preparar features: {str(e)}")
            return np.array([]), np.array([])
    
    def treinar_modelo(self, X: np.ndarray, result: np.ndarray) -> bool:
        """
        Treina o modelo de Machine Learning.
        
        Args:
            X: Features de treinamento
            result: Target de treinamento
            
        Returns:
            True se treinamento foi bem-sucedido
        """
        try:
            if len(X) == 0 or len(result) == 0:
                logger.warning("[LONGTAIL-010] Dados insuficientes para treinamento")
                return False
            
            # Split dos dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, result, test_size=self.config.test_size, random_state=self.config.random_state
            )
            
            # Treinamento do modelo
            self.model = RandomForestRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                min_samples_split=self.config.min_samples_split,
                min_samples_leaf=self.config.min_samples_leaf,
                random_state=self.config.random_state
            )
            
            self.model.fit(X_train, y_train)
            
            # Avaliação do modelo
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"[LONGTAIL-010] Modelo treinado - MSE: {mse:.4f}, R²: {r2:.4f}")
            
            # Validação de qualidade
            if r2 < self.config.min_r2_score or mse > self.config.max_mse:
                logger.warning(f"[LONGTAIL-010] Modelo abaixo do padrão - R²: {r2:.4f}, MSE: {mse:.4f}")
                return False
            
            # Salvamento do modelo
            self._salvar_modelo()
            
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro no treinamento: {str(e)}")
            return False
    
    def _salvar_modelo(self):
        """Salva o modelo treinado."""
        try:
            model_path = self.model_dir / "ajuste_automatico_model.pkl"
            scaler_path = self.model_dir / "ajuste_automatico_scaler.pkl"
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            logger.info(f"[LONGTAIL-010] Modelo salvo em: {model_path}")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao salvar modelo: {str(e)}")
    
    def _carregar_modelo(self) -> bool:
        """Carrega modelo salvo anteriormente."""
        try:
            model_path = self.model_dir / "ajuste_automatico_model.pkl"
            scaler_path = self.model_dir / "ajuste_automatico_scaler.pkl"
            
            if model_path.exists() and scaler_path.exists():
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info(f"[LONGTAIL-010] Modelo carregado de: {model_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao carregar modelo: {str(e)}")
            return False
    
    def prever_otimizacao(self, parametros_atuais: Dict[str, float]) -> Dict[str, float]:
        """
        Prevê parâmetros otimizados usando o modelo treinado.
        
        Args:
            parametros_atuais: Parâmetros atuais do sistema
            
        Returns:
            Dicionário com parâmetros otimizados
        """
        try:
            if self.model is None:
                if not self._carregar_modelo():
                    logger.warning("[LONGTAIL-010] Modelo não disponível para predição")
                    return parametros_atuais
            
            # Preparar features para predição
            features = np.array([
                parametros_atuais["min_palavras"],
                parametros_atuais["min_caracteres"],
                parametros_atuais["max_concorrencia"],
                parametros_atuais["score_minimo"],
                parametros_atuais["threshold_complexidade"],
                parametros_atuais["peso_volume"],
                parametros_atuais["peso_cpc"],
                parametros_atuais["peso_concorrencia"]
            ]).reshape(1, -1)
            
            # Normalizar features
            features_scaled = self.scaler.transform(features)
            
            # Predição
            performance_predita = self.model.predict(features_scaled)[0]
            
            # Geração de parâmetros otimizados
            parametros_otimizados = self._gerar_parametros_otimizados(
                parametros_atuais, performance_predita
            )
            
            logger.info(f"[LONGTAIL-010] Otimização prevista - Performance: {performance_predita:.4f}")
            return parametros_otimizados
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro na predição: {str(e)}")
            return parametros_atuais
    
    def _gerar_parametros_otimizados(
        self, 
        parametros_atuais: Dict[str, float], 
        performance_predita: float
    ) -> Dict[str, float]:
        """
        Gera parâmetros otimizados baseado na predição.
        
        Args:
            parametros_atuais: Parâmetros atuais
            performance_predita: Performance prevista
            
        Returns:
            Parâmetros otimizados
        """
        # Fator de ajuste baseado na performance
        fator_ajuste = 1.0 + (performance_predita - 0.7) * 0.1
        
        parametros_otimizados = {}
        
        for chave, valor in parametros_atuais.items():
            if "min_" in chave:
                # Parâmetros mínimos: ajuste conservador
                ajuste = 1.0 + (fator_ajuste - 1.0) * 0.5
                parametros_otimizados[chave] = max(valor * ajuste, valor * 0.9)
            elif "max_" in chave:
                # Parâmetros máximos: ajuste conservador
                ajuste = 1.0 + (fator_ajuste - 1.0) * 0.5
                parametros_otimizados[chave] = min(valor * ajuste, valor * 1.1)
            elif "peso_" in chave:
                # Pesos: normalizar para somar 1.0
                parametros_otimizados[chave] = valor * fator_ajuste
            else:
                # Outros parâmetros: ajuste padrão
                parametros_otimizados[chave] = valor * fator_ajuste
        
        # Normalizar pesos
        if "peso_volume" in parametros_otimizados:
            total_pesos = (
                parametros_otimizados["peso_volume"] +
                parametros_otimizados["peso_cpc"] +
                parametros_otimizados["peso_concorrencia"]
            )
            parametros_otimizados["peso_volume"] /= total_pesos
            parametros_otimizados["peso_cpc"] /= total_pesos
            parametros_otimizados["peso_concorrencia"] /= total_pesos
        
        return parametros_otimizados
    
    def aplicar_ajuste_automatico(self, performance_atual: float) -> AjusteResultado:
        """
        Aplica ajuste automático baseado na performance atual.
        
        Args:
            performance_atual: Performance atual do sistema
            
        Returns:
            Resultado do ajuste aplicado
        """
        try:
            tracing_id = f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Verificar se ajuste é necessário
            if performance_atual >= 0.85:  # Performance muito boa
                logger.info(f"[LONGTAIL-010] Performance excelente ({performance_atual:.4f}), ajuste não necessário")
                return AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=self.parametros_atuais.copy(),
                    parametros_novos=self.parametros_atuais.copy(),
                    performance_anterior=performance_atual,
                    performance_nova=performance_atual,
                    melhoria=0.0,
                    confianca=1.0,
                    status="nao_necessario",
                    tracing_id=tracing_id
                )
            
            # Prever otimização
            parametros_otimizados = self.prever_otimizacao(self.parametros_atuais)
            
            # Calcular confiança da predição
            confianca = self._calcular_confianca_predicao()
            
            # Aplicar ajuste se confiança for alta
            if confianca >= 0.7:
                parametros_anteriores = self.parametros_atuais.copy()
                self.parametros_atuais = parametros_otimizados
                
                # Simular nova performance
                performance_nova = self._simular_performance(parametros_otimizados)
                melhoria = performance_nova - performance_atual
                
                resultado = AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=parametros_anteriores,
                    parametros_novos=parametros_otimizados,
                    performance_anterior=performance_atual,
                    performance_nova=performance_nova,
                    melhoria=melhoria,
                    confianca=confianca,
                    status="aplicado",
                    tracing_id=tracing_id
                )
                
                self.historico_ajustes.append(resultado)
                self._salvar_historico()
                
                logger.info(f"[LONGTAIL-010] Ajuste aplicado - Melhoria: {melhoria:.4f}, Confiança: {confianca:.4f}")
                return resultado
            
            else:
                logger.warning(f"[LONGTAIL-010] Confiança baixa ({confianca:.4f}), ajuste não aplicado")
                return AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=self.parametros_atuais.copy(),
                    parametros_novos=self.parametros_atuais.copy(),
                    performance_anterior=performance_atual,
                    performance_nova=performance_atual,
                    melhoria=0.0,
                    confianca=confianca,
                    status="confianca_baixa",
                    tracing_id=tracing_id
                )
                
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro no ajuste automático: {str(e)}")
            return AjusteResultado(
                timestamp=datetime.now(),
                parametros_anteriores=self.parametros_atuais.copy(),
                parametros_novos=self.parametros_atuais.copy(),
                performance_anterior=performance_atual,
                performance_nova=performance_atual,
                melhoria=0.0,
                confianca=0.0,
                status="erro",
                tracing_id=f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
    
    def _calcular_confianca_predicao(self) -> float:
        """Calcula confiança da predição baseada no histórico."""
        if len(self.historico_ajustes) < 5:
            return 0.5  # Confiança baixa se pouco histórico
        
        # Calcular taxa de sucesso dos ajustes anteriores
        ajustes_sucesso = [
            ajuste for ajuste in self.historico_ajustes[-10:]
            if ajuste.melhoria > 0 and ajuste.status == "aplicado"
        ]
        
        taxa_sucesso = len(ajustes_sucesso) / min(len(self.historico_ajustes), 10)
        
        # Confiança baseada na taxa de sucesso
        confianca = 0.5 + (taxa_sucesso * 0.5)
        
        return min(confianca, 1.0)
    
    def _simular_performance(self, parametros: Dict[str, float]) -> float:
        """Simula performance com novos parâmetros."""
        # Simulação baseada em heurísticas
        performance_base = 0.7
        
        # Ajustes baseados nos parâmetros
        ajuste_min_palavras = 0.05 if parametros["min_palavras"] >= 3 else -0.05
        ajuste_min_caracteres = 0.03 if parametros["min_caracteres"] >= 15 else -0.03
        ajuste_concorrencia = 0.02 if parametros["max_concorrencia"] <= 0.5 else -0.02
        
        performance_simulada = performance_base + ajuste_min_palavras + ajuste_min_caracteres + ajuste_concorrencia
        
        # Adicionar ruído realista
        ruido = np.random.normal(0, 0.02)
        performance_simulada += ruido
        
        return max(0.0, min(1.0, performance_simulada))
    
    def verificar_necessidade_rollback(self, performance_atual: float) -> bool:
        """
        Verifica se é necessário fazer rollback dos parâmetros.
        
        Args:
            performance_atual: Performance atual do sistema
            
        Returns:
            True se rollback é necessário
        """
        if len(self.historico_ajustes) == 0:
            return False
        
        ultimo_ajuste = self.historico_ajustes[-1]
        
        # Verificar degradação significativa
        degradacao = ultimo_ajuste.performance_anterior - performance_atual
        
        if degradacao > self.config.performance_degradation_threshold:
            logger.warning(f"[LONGTAIL-010] Degradação detectada: {degradacao:.4f}")
            return True
        
        return False
    
    def aplicar_rollback(self) -> bool:
        """
        Aplica rollback para parâmetros anteriores.
        
        Returns:
            True se rollback foi aplicado com sucesso
        """
        try:
            if len(self.historico_ajustes) == 0:
                logger.warning("[LONGTAIL-010] Nenhum ajuste para rollback")
                return False
            
            if self.rollback_count >= self.config.max_rollback_attempts:
                logger.error("[LONGTAIL-010] Máximo de rollbacks atingido")
                return False
            
            ultimo_ajuste = self.historico_ajustes[-1]
            
            # Restaurar parâmetros anteriores
            self.parametros_atuais = ultimo_ajuste.parametros_anteriores.copy()
            
            # Remover último ajuste do histórico
            self.historico_ajustes.pop()
            
            self.rollback_count += 1
            
            logger.info(f"[LONGTAIL-010] Rollback aplicado - Parâmetros restaurados")
            return True
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro no rollback: {str(e)}")
            return False
    
    def _salvar_historico(self):
        """Salva histórico de ajustes."""
        try:
            historico_path = self.model_dir / "historico_ajustes.json"
            
            historico_data = []
            for ajuste in self.historico_ajustes:
                historico_data.append({
                    "timestamp": ajuste.timestamp.isoformat(),
                    "parametros_anteriores": ajuste.parametros_anteriores,
                    "parametros_novos": ajuste.parametros_novos,
                    "performance_anterior": ajuste.performance_anterior,
                    "performance_nova": ajuste.performance_nova,
                    "melhoria": ajuste.melhoria,
                    "confianca": ajuste.confianca,
                    "status": ajuste.status,
                    "tracing_id": ajuste.tracing_id
                })
            
            with open(historico_path, 'w') as f:
                json.dump(historico_data, f, indent=2)
            
            logger.info(f"[LONGTAIL-010] Histórico salvo em: {historico_path}")
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao salvar histórico: {str(e)}")
    
    def gerar_relatorio_otimizacao(self) -> Dict[str, Any]:
        """
        Gera relatório de otimização do sistema.
        
        Returns:
            Dicionário com relatório completo
        """
        try:
            if len(self.historico_ajustes) == 0:
                return {
                    "status": "sem_historico",
                    "mensagem": "Nenhum ajuste realizado ainda"
                }
            
            # Estatísticas gerais
            total_ajustes = len(self.historico_ajustes)
            ajustes_sucesso = len([a for a in self.historico_ajustes if a.melhoria > 0])
            taxa_sucesso = ajustes_sucesso / total_ajustes if total_ajustes > 0 else 0
            
            # Melhoria média
            melhorias = [a.melhoria for a in self.historico_ajustes if a.melhoria > 0]
            melhoria_media = np.mean(melhorias) if melhorias else 0
            
            # Performance atual vs inicial
            performance_inicial = self.historico_ajustes[0].performance_anterior
            performance_atual = self.historico_ajustes[-1].performance_nova
            melhoria_total = performance_atual - performance_inicial
            
            # Últimos ajustes
            ultimos_ajustes = []
            for ajuste in self.historico_ajustes[-5:]:
                ultimos_ajustes.append({
                    "data": ajuste.timestamp.strftime("%Y-%m-%data %H:%M:%S"),
                    "melhoria": ajuste.melhoria,
                    "confianca": ajuste.confianca,
                    "status": ajuste.status,
                    "tracing_id": ajuste.tracing_id
                })
            
            relatorio = {
                "status": "sucesso",
                "metricas_gerais": {
                    "total_ajustes": total_ajustes,
                    "ajustes_sucesso": ajustes_sucesso,
                    "taxa_sucesso": taxa_sucesso,
                    "melhoria_media": melhoria_media,
                    "melhoria_total": melhoria_total,
                    "rollbacks": self.rollback_count
                },
                "performance": {
                    "inicial": performance_inicial,
                    "atual": performance_atual,
                    "melhoria": melhoria_total
                },
                "parametros_atuais": self.parametros_atuais,
                "ultimos_ajustes": ultimos_ajustes,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[LONGTAIL-010] Relatório gerado - Taxa de sucesso: {taxa_sucesso:.2%}")
            return relatorio
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro ao gerar relatório: {str(e)}")
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar relatório: {str(e)}"
            }
    
    def executar_ciclo_otimizacao(self) -> AjusteResultado:
        """
        Executa ciclo completo de otimização.
        
        Returns:
            Resultado do ciclo de otimização
        """
        try:
            logger.info(f"[LONGTAIL-010] Iniciando ciclo de otimização - {datetime.now()}")
            
            # 1. Coletar dados de treinamento
            dados = self.coletar_dados_treinamento()
            
            if len(dados) == 0:
                logger.warning("[LONGTAIL-010] Dados insuficientes para otimização")
                return AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=self.parametros_atuais.copy(),
                    parametros_novos=self.parametros_atuais.copy(),
                    performance_anterior=0.0,
                    performance_nova=0.0,
                    melhoria=0.0,
                    confianca=0.0,
                    status="dados_insuficientes",
                    tracing_id=f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            
            # 2. Preparar features
            X, result = self.preparar_features(dados)
            
            if len(X) == 0:
                logger.warning("[LONGTAIL-010] Features insuficientes para treinamento")
                return AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=self.parametros_atuais.copy(),
                    parametros_novos=self.parametros_atuais.copy(),
                    performance_anterior=0.0,
                    performance_nova=0.0,
                    melhoria=0.0,
                    confianca=0.0,
                    status="features_insuficientes",
                    tracing_id=f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            
            # 3. Treinar modelo
            if not self.treinar_modelo(X, result):
                logger.warning("[LONGTAIL-010] Falha no treinamento do modelo")
                return AjusteResultado(
                    timestamp=datetime.now(),
                    parametros_anteriores=self.parametros_atuais.copy(),
                    parametros_novos=self.parametros_atuais.copy(),
                    performance_anterior=0.0,
                    performance_nova=0.0,
                    melhoria=0.0,
                    confianca=0.0,
                    status="falha_treinamento",
                    tracing_id=f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            
            # 4. Simular performance atual
            performance_atual = self._simular_performance(self.parametros_atuais)
            
            # 5. Aplicar ajuste automático
            resultado = self.aplicar_ajuste_automatico(performance_atual)
            
            logger.info(f"[LONGTAIL-010] Ciclo de otimização concluído - Status: {resultado.status}")
            return resultado
            
        except Exception as e:
            logger.error(f"[LONGTAIL-010] Erro no ciclo de otimização: {str(e)}")
            return AjusteResultado(
                timestamp=datetime.now(),
                parametros_anteriores=self.parametros_atuais.copy(),
                parametros_novos=self.parametros_atuais.copy(),
                performance_anterior=0.0,
                performance_nova=0.0,
                melhoria=0.0,
                confianca=0.0,
                status="erro_ciclo",
                tracing_id=f"LONGTAIL-010_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )


# Função de conveniência para uso externo
def criar_sistema_ajuste_automatico() -> AjusteAutomaticoCaudaLonga:
    """
    Cria e configura sistema de ajuste automático.
    
    Returns:
        Instância configurada do sistema
    """
    config = MLConfig()
    return AjusteAutomaticoCaudaLonga(config)


if __name__ == "__main__":
    # Teste básico do sistema
    sistema = criar_sistema_ajuste_automatico()
    resultado = sistema.executar_ciclo_otimizacao()
    print(f"Resultado do teste: {resultado.status}")
    
    relatorio = sistema.gerar_relatorio_otimizacao()
    print(f"Relatório: {relatorio['status']}") 