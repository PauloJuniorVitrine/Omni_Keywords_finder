from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Ajuste Automático de Cauda Longa

Tracing ID: LONGTAIL-010-TEST
Data/Hora: 2024-12-20 17:40:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Testes para validar funcionalidades do sistema de Machine Learning
para ajuste automático de parâmetros de cauda longa.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

from infrastructure.ml.ajuste_automatico_cauda_longa import (
    AjusteAutomaticoCaudaLonga,
    MLConfig,
    AjusteResultado,
    criar_sistema_ajuste_automatico
)


class TestMLConfig:
    """Testes para configuração do sistema ML."""
    
    def test_configuracao_padrao(self):
        """Testa configuração padrão do sistema."""
        config = MLConfig()
        
        assert config.n_estimators == 100
        assert config.max_depth == 10
        assert config.min_samples_split == 5
        assert config.min_samples_leaf == 2
        assert config.test_size == 0.2
        assert config.random_state == 42
        assert config.min_r2_score == 0.7
        assert config.max_mse == 0.1
        assert config.max_rollback_attempts == 3
        assert config.performance_degradation_threshold == 0.1
    
    def test_configuracao_customizada(self):
        """Testa configuração customizada do sistema."""
        config = MLConfig(
            n_estimators=50,
            max_depth=5,
            min_r2_score=0.8,
            max_mse=0.05
        )
        
        assert config.n_estimators == 50
        assert config.max_depth == 5
        assert config.min_r2_score == 0.8
        assert config.max_mse == 0.05


class TestAjusteResultado:
    """Testes para resultado de ajuste."""
    
    def test_criacao_ajuste_resultado(self):
        """Testa criação de resultado de ajuste."""
        timestamp = datetime.now()
        parametros_anteriores = {"min_palavras": 3, "max_concorrencia": 0.5}
        parametros_novos = {"min_palavras": 4, "max_concorrencia": 0.4}
        
        resultado = AjusteResultado(
            timestamp=timestamp,
            parametros_anteriores=parametros_anteriores,
            parametros_novos=parametros_novos,
            performance_anterior=0.7,
            performance_nova=0.8,
            melhoria=0.1,
            confianca=0.85,
            status="aplicado",
            tracing_id="TEST-001"
        )
        
        assert resultado.timestamp == timestamp
        assert resultado.parametros_anteriores == parametros_anteriores
        assert resultado.parametros_novos == parametros_novos
        assert resultado.performance_anterior == 0.7
        assert resultado.performance_nova == 0.8
        assert resultado.melhoria == 0.1
        assert resultado.confianca == 0.85
        assert resultado.status == "aplicado"
        assert resultado.tracing_id == "TEST-001"


class TestAjusteAutomaticoCaudaLonga:
    """Testes para sistema de ajuste automático."""
    
    @pytest.fixture
    def sistema(self):
        """Fixture para criar sistema de teste."""
        config = MLConfig(
            n_estimators=10,  # Reduzido para testes
            max_depth=3,
            min_r2_score=0.5,  # Reduzido para testes
            max_mse=0.2
        )
        return AjusteAutomaticoCaudaLonga(config)
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture para diretório temporário."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_inicializacao_sistema(self, sistema):
        """Testa inicialização do sistema."""
        assert sistema.config is not None
        assert sistema.model is None
        assert sistema.scaler is not None
        assert len(sistema.historico_ajustes) == 0
        assert sistema.rollback_count == 0
        assert sistema.parametros_atuais is not None
    
    def test_carregar_parametros_padrao(self, sistema):
        """Testa carregamento de parâmetros padrão."""
        parametros = sistema._carregar_parametros_padrao()
        
        assert "min_palavras" in parametros
        assert "min_caracteres" in parametros
        assert "max_concorrencia" in parametros
        assert "score_minimo" in parametros
        assert "threshold_complexidade" in parametros
        assert "peso_volume" in parametros
        assert "peso_cpc" in parametros
        assert "peso_concorrencia" in parametros
        
        assert parametros["min_palavras"] == 3.0
        assert parametros["min_caracteres"] == 15.0
        assert parametros["max_concorrencia"] == 0.5
    
    def test_coletar_dados_treinamento(self, sistema):
        """Testa coleta de dados de treinamento."""
        dados = sistema.coletar_dados_treinamento(periodo_dias=5)
        
        assert isinstance(dados, pd.DataFrame)
        assert len(dados) > 0
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = [
            "data", "performance", "taxa_conversao",
            "feedback_positivo", "feedback_negativo",
            "min_palavras", "min_caracteres", "max_concorrencia",
            "score_minimo", "threshold_complexidade",
            "peso_volume", "peso_cpc", "peso_concorrencia"
        ]
        
        for coluna in colunas_obrigatorias:
            assert coluna in dados.columns
    
    def test_preparar_features(self, sistema):
        """Testa preparação de features."""
        # Criar dados de teste
        dados = pd.DataFrame({
            "min_palavras": [3, 4, 3],
            "min_caracteres": [15, 16, 15],
            "max_concorrencia": [0.5, 0.4, 0.5],
            "score_minimo": [0.6, 0.7, 0.6],
            "threshold_complexidade": [0.7, 0.8, 0.7],
            "peso_volume": [0.4, 0.5, 0.4],
            "peso_cpc": [0.3, 0.2, 0.3],
            "peso_concorrencia": [0.3, 0.3, 0.3],
            "performance": [0.7, 0.8, 0.7]
        })
        
        X, result = sistema.preparar_features(dados)
        
        assert isinstance(X, np.ndarray)
        assert isinstance(result, np.ndarray)
        assert len(X) == len(result)
        assert X.shape[1] == 8  # 8 features
        assert len(result) == 3
    
    def test_preparar_features_dados_vazios(self, sistema):
        """Testa preparação de features com dados vazios."""
        dados = pd.DataFrame()
        X, result = sistema.preparar_features(dados)
        
        assert len(X) == 0
        assert len(result) == 0
    
    @patch('infrastructure.ml.ajuste_automatico_cauda_longa.train_test_split')
    @patch('infrastructure.ml.ajuste_automatico_cauda_longa.RandomForestRegressor')
    def test_treinar_modelo_sucesso(self, mock_rf, mock_split, sistema):
        """Testa treinamento bem-sucedido do modelo."""
        # Mock do modelo
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = np.array([0.7, 0.8, 0.7])
        mock_rf.return_value = mock_model
        
        # Mock do split
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        result = np.array([0.7, 0.8, 0.7])
        mock_split.return_value = (X[:2], X[2:], result[:2], result[2:])
        
        # Mock das métricas
        with patch('infrastructure.ml.ajuste_automatico_cauda_longa.mean_squared_error') as mock_mse:
            with patch('infrastructure.ml.ajuste_automatico_cauda_longa.r2_score') as mock_r2:
                mock_mse.return_value = 0.05
                mock_r2.return_value = 0.8
                
                # Mock do salvamento
                with patch.object(sistema, '_salvar_modelo'):
                    resultado = sistema.treinar_modelo(X, result)
                    
                    assert resultado is True
                    assert sistema.model is not None
    
    def test_treinar_modelo_dados_insuficientes(self, sistema):
        """Testa treinamento com dados insuficientes."""
        X = np.array([])
        result = np.array([])
        
        resultado = sistema.treinar_modelo(X, result)
        
        assert resultado is False
    
    @patch('infrastructure.ml.ajuste_automatico_cauda_longa.train_test_split')
    @patch('infrastructure.ml.ajuste_automatico_cauda_longa.RandomForestRegressor')
    def test_treinar_modelo_qualidade_baixa(self, mock_rf, mock_split, sistema):
        """Testa treinamento com qualidade abaixo do padrão."""
        # Mock do modelo
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.predict.return_value = np.array([0.7, 0.8, 0.7])
        mock_rf.return_value = mock_model
        
        # Mock do split
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        result = np.array([0.7, 0.8, 0.7])
        mock_split.return_value = (X[:2], X[2:], result[:2], result[2:])
        
        # Mock das métricas com qualidade baixa
        with patch('infrastructure.ml.ajuste_automatico_cauda_longa.mean_squared_error') as mock_mse:
            with patch('infrastructure.ml.ajuste_automatico_cauda_longa.r2_score') as mock_r2:
                mock_mse.return_value = 0.3  # Acima do threshold
                mock_r2.return_value = 0.5   # Abaixo do threshold
                
                resultado = sistema.treinar_modelo(X, result)
                
                assert resultado is False
    
    def test_salvar_carregar_modelo(self, sistema, temp_dir):
        """Testa salvamento e carregamento do modelo."""
        # Mock do modelo
        sistema.model = Mock()
        sistema.scaler = Mock()
        
        # Mock do joblib
        with patch('infrastructure.ml.ajuste_automatico_cauda_longa.joblib') as mock_joblib:
            with patch.object(sistema, 'model_dir', Path(temp_dir)):
                # Testar salvamento
                sistema._salvar_modelo()
                mock_joblib.dump.assert_called()
                
                # Testar carregamento
                mock_joblib.load.side_effect = [sistema.model, sistema.scaler]
                resultado = sistema._carregar_modelo()
                
                assert resultado is True
                mock_joblib.load.assert_called()
    
    def test_prever_otimizacao_sem_modelo(self, sistema):
        """Testa predição sem modelo disponível."""
        parametros = {"min_palavras": 3, "max_concorrencia": 0.5}
        
        with patch.object(sistema, '_carregar_modelo', return_value=False):
            resultado = sistema.prever_otimizacao(parametros)
            
            assert resultado == parametros
    
    @patch.object(AjusteAutomaticoCaudaLonga, '_carregar_modelo')
    def test_prever_otimizacao_com_modelo(self, mock_carregar, sistema):
        """Testa predição com modelo disponível."""
        # Mock do modelo
        sistema.model = Mock()
        sistema.scaler = Mock()
        sistema.scaler.transform.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]])
        sistema.model.predict.return_value = np.array([0.8])
        mock_carregar.return_value = True
        
        parametros = {
            "min_palavras": 3.0,
            "min_caracteres": 15.0,
            "max_concorrencia": 0.5,
            "score_minimo": 0.6,
            "threshold_complexidade": 0.7,
            "peso_volume": 0.4,
            "peso_cpc": 0.3,
            "peso_concorrencia": 0.3
        }
        
        with patch.object(sistema, '_gerar_parametros_otimizados') as mock_gerar:
            mock_gerar.return_value = parametros.copy()
            
            resultado = sistema.prever_otimizacao(parametros)
            
            assert resultado == parametros
            sistema.model.predict.assert_called_once()
    
    def test_gerar_parametros_otimizados(self, sistema):
        """Testa geração de parâmetros otimizados."""
        parametros_atuais = {
            "min_palavras": 3.0,
            "min_caracteres": 15.0,
            "max_concorrencia": 0.5,
            "score_minimo": 0.6,
            "threshold_complexidade": 0.7,
            "peso_volume": 0.4,
            "peso_cpc": 0.3,
            "peso_concorrencia": 0.3
        }
        
        performance_predita = 0.8
        
        resultado = sistema._gerar_parametros_otimizados(parametros_atuais, performance_predita)
        
        assert isinstance(resultado, dict)
        assert "min_palavras" in resultado
        assert "max_concorrencia" in resultado
        assert "peso_volume" in resultado
        
        # Verificar normalização dos pesos
        total_pesos = resultado["peso_volume"] + resultado["peso_cpc"] + resultado["peso_concorrencia"]
        assert abs(total_pesos - 1.0) < 0.001
    
    def test_aplicar_ajuste_automatico_performance_excelente(self, sistema):
        """Testa ajuste com performance excelente."""
        performance_atual = 0.9  # Performance muito boa
        
        resultado = sistema.aplicar_ajuste_automatico(performance_atual)
        
        assert resultado.status == "nao_necessario"
        assert resultado.melhoria == 0.0
        assert resultado.confianca == 1.0
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'prever_otimizacao')
    @patch.object(AjusteAutomaticoCaudaLonga, '_calcular_confianca_predicao')
    @patch.object(AjusteAutomaticoCaudaLonga, '_simular_performance')
    def test_aplicar_ajuste_automatico_confianca_alta(self, mock_simular, mock_confianca, mock_prever, sistema):
        """Testa ajuste com confiança alta."""
        # Mock das dependências
        mock_prever.return_value = {"min_palavras": 4.0, "max_concorrencia": 0.4}
        mock_confianca.return_value = 0.8
        mock_simular.return_value = 0.75
        
        performance_atual = 0.6
        
        resultado = sistema.aplicar_ajuste_automatico(performance_atual)
        
        assert resultado.status == "aplicado"
        assert resultado.confianca == 0.8
        assert resultado.performance_anterior == 0.6
        assert resultado.performance_nova == 0.75
        assert resultado.melhoria > 0
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'prever_otimizacao')
    @patch.object(AjusteAutomaticoCaudaLonga, '_calcular_confianca_predicao')
    def test_aplicar_ajuste_automatico_confianca_baixa(self, mock_confianca, mock_prever, sistema):
        """Testa ajuste com confiança baixa."""
        # Mock das dependências
        mock_prever.return_value = {"min_palavras": 4.0, "max_concorrencia": 0.4}
        mock_confianca.return_value = 0.5  # Confiança baixa
        
        performance_atual = 0.6
        
        resultado = sistema.aplicar_ajuste_automatico(performance_atual)
        
        assert resultado.status == "confianca_baixa"
        assert resultado.confianca == 0.5
        assert resultado.melhoria == 0.0
    
    def test_calcular_confianca_predicao_sem_historico(self, sistema):
        """Testa cálculo de confiança sem histórico."""
        confianca = sistema._calcular_confianca_predicao()
        
        assert confianca == 0.5
    
    def test_calcular_confianca_predicao_com_historico(self, sistema):
        """Testa cálculo de confiança com histórico."""
        # Criar histórico de ajustes
        for index in range(10):
            ajuste = AjusteResultado(
                timestamp=datetime.now(),
                parametros_anteriores={},
                parametros_novos={},
                performance_anterior=0.6,
                performance_nova=0.7,
                melhoria=0.1 if index < 7 else -0.1,  # 7 sucessos, 3 falhas
                confianca=0.8,
                status="aplicado",
                tracing_id=f"TEST-{index}"
            )
            sistema.historico_ajustes.append(ajuste)
        
        confianca = sistema._calcular_confianca_predicao()
        
        # Taxa de sucesso = 7/10 = 0.7
        # Confiança esperada = 0.5 + (0.7 * 0.5) = 0.85
        assert confianca == 0.85
    
    def test_simular_performance(self, sistema):
        """Testa simulação de performance."""
        parametros = {
            "min_palavras": 3,
            "min_caracteres": 15,
            "max_concorrencia": 0.5,
            "score_minimo": 0.6,
            "threshold_complexidade": 0.7,
            "peso_volume": 0.4,
            "peso_cpc": 0.3,
            "peso_concorrencia": 0.3
        }
        
        performance = sistema._simular_performance(parametros)
        
        assert 0.0 <= performance <= 1.0
    
    def test_verificar_necessidade_rollback_sem_degradacao(self, sistema):
        """Testa verificação de rollback sem degradação."""
        # Criar ajuste sem degradação
        ajuste = AjusteResultado(
            timestamp=datetime.now(),
            parametros_anteriores={},
            parametros_novos={},
            performance_anterior=0.7,
            performance_nova=0.8,
            melhoria=0.1,
            confianca=0.8,
            status="aplicado",
            tracing_id="TEST-001"
        )
        sistema.historico_ajustes.append(ajuste)
        
        performance_atual = 0.75  # Pouca degradação
        
        necessidade = sistema.verificar_necessidade_rollback(performance_atual)
        
        assert necessidade is False
    
    def test_verificar_necessidade_rollback_com_degradacao(self, sistema):
        """Testa verificação de rollback com degradação."""
        # Criar ajuste com degradação
        ajuste = AjusteResultado(
            timestamp=datetime.now(),
            parametros_anteriores={},
            parametros_novos={},
            performance_anterior=0.8,
            performance_nova=0.9,
            melhoria=0.1,
            confianca=0.8,
            status="aplicado",
            tracing_id="TEST-001"
        )
        sistema.historico_ajustes.append(ajuste)
        
        performance_atual = 0.6  # Degradação significativa
        
        necessidade = sistema.verificar_necessidade_rollback(performance_atual)
        
        assert necessidade is True
    
    def test_aplicar_rollback_sucesso(self, sistema):
        """Testa aplicação de rollback bem-sucedida."""
        # Criar ajuste para rollback
        parametros_anteriores = {"min_palavras": 3, "max_concorrencia": 0.5}
        parametros_novos = {"min_palavras": 4, "max_concorrencia": 0.4}
        
        ajuste = AjusteResultado(
            timestamp=datetime.now(),
            parametros_anteriores=parametros_anteriores,
            parametros_novos=parametros_novos,
            performance_anterior=0.7,
            performance_nova=0.8,
            melhoria=0.1,
            confianca=0.8,
            status="aplicado",
            tracing_id="TEST-001"
        )
        sistema.historico_ajustes.append(ajuste)
        sistema.parametros_atuais = parametros_novos.copy()
        
        resultado = sistema.aplicar_rollback()
        
        assert resultado is True
        assert sistema.parametros_atuais == parametros_anteriores
        assert len(sistema.historico_ajustes) == 0
        assert sistema.rollback_count == 1
    
    def test_aplicar_rollback_sem_historico(self, sistema):
        """Testa rollback sem histórico."""
        resultado = sistema.aplicar_rollback()
        
        assert resultado is False
    
    def test_aplicar_rollback_maximo_atingido(self, sistema):
        """Testa rollback com máximo atingido."""
        sistema.rollback_count = sistema.config.max_rollback_attempts
        
        resultado = sistema.aplicar_rollback()
        
        assert resultado is False
    
    def test_gerar_relatorio_sem_historico(self, sistema):
        """Testa geração de relatório sem histórico."""
        relatorio = sistema.gerar_relatorio_otimizacao()
        
        assert relatorio["status"] == "sem_historico"
        assert "mensagem" in relatorio
    
    def test_gerar_relatorio_com_historico(self, sistema):
        """Testa geração de relatório com histórico."""
        # Criar histórico de ajustes
        for index in range(5):
            ajuste = AjusteResultado(
                timestamp=datetime.now(),
                parametros_anteriores={},
                parametros_novos={},
                performance_anterior=0.6 + index * 0.02,
                performance_nova=0.7 + index * 0.02,
                melhoria=0.1,
                confianca=0.8,
                status="aplicado",
                tracing_id=f"TEST-{index}"
            )
            sistema.historico_ajustes.append(ajuste)
        
        relatorio = sistema.gerar_relatorio_otimizacao()
        
        assert relatorio["status"] == "sucesso"
        assert "metricas_gerais" in relatorio
        assert "performance" in relatorio
        assert "parametros_atuais" in relatorio
        assert "ultimos_ajustes" in relatorio
        
        metricas = relatorio["metricas_gerais"]
        assert metricas["total_ajustes"] == 5
        assert metricas["ajustes_sucesso"] == 5
        assert metricas["taxa_sucesso"] == 1.0
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'coletar_dados_treinamento')
    @patch.object(AjusteAutomaticoCaudaLonga, 'preparar_features')
    @patch.object(AjusteAutomaticoCaudaLonga, 'treinar_modelo')
    @patch.object(AjusteAutomaticoCaudaLonga, '_simular_performance')
    @patch.object(AjusteAutomaticoCaudaLonga, 'aplicar_ajuste_automatico')
    def test_executar_ciclo_otimizacao_sucesso(self, mock_ajuste, mock_simular, mock_treinar, mock_features, mock_coletar, sistema):
        """Testa execução bem-sucedida do ciclo de otimização."""
        # Mock das dependências
        mock_coletar.return_value = pd.DataFrame({"test": [1, 2, 3]})
        mock_features.return_value = (np.array([[1, 2, 3]]), np.array([0.7]))
        mock_treinar.return_value = True
        mock_simular.return_value = 0.7
        
        resultado_ajuste = AjusteResultado(
            timestamp=datetime.now(),
            parametros_anteriores={},
            parametros_novos={},
            performance_anterior=0.7,
            performance_nova=0.8,
            melhoria=0.1,
            confianca=0.8,
            status="aplicado",
            tracing_id="TEST-001"
        )
        mock_ajuste.return_value = resultado_ajuste
        
        resultado = sistema.executar_ciclo_otimizacao()
        
        assert resultado.status == "aplicado"
        assert resultado.melhoria == 0.1
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'coletar_dados_treinamento')
    def test_executar_ciclo_otimizacao_dados_insuficientes(self, mock_coletar, sistema):
        """Testa ciclo de otimização com dados insuficientes."""
        mock_coletar.return_value = pd.DataFrame()
        
        resultado = sistema.executar_ciclo_otimizacao()
        
        assert resultado.status == "dados_insuficientes"
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'coletar_dados_treinamento')
    @patch.object(AjusteAutomaticoCaudaLonga, 'preparar_features')
    def test_executar_ciclo_otimizacao_features_insuficientes(self, mock_features, mock_coletar, sistema):
        """Testa ciclo de otimização com features insuficientes."""
        mock_coletar.return_value = pd.DataFrame({"test": [1, 2, 3]})
        mock_features.return_value = (np.array([]), np.array([]))
        
        resultado = sistema.executar_ciclo_otimizacao()
        
        assert resultado.status == "features_insuficientes"
    
    @patch.object(AjusteAutomaticoCaudaLonga, 'coletar_dados_treinamento')
    @patch.object(AjusteAutomaticoCaudaLonga, 'preparar_features')
    @patch.object(AjusteAutomaticoCaudaLonga, 'treinar_modelo')
    def test_executar_ciclo_otimizacao_falha_treinamento(self, mock_treinar, mock_features, mock_coletar, sistema):
        """Testa ciclo de otimização com falha no treinamento."""
        mock_coletar.return_value = pd.DataFrame({"test": [1, 2, 3]})
        mock_features.return_value = (np.array([[1, 2, 3]]), np.array([0.7]))
        mock_treinar.return_value = False
        
        resultado = sistema.executar_ciclo_otimizacao()
        
        assert resultado.status == "falha_treinamento"


class TestFuncaoConveniencia:
    """Testes para função de conveniência."""
    
    def test_criar_sistema_ajuste_automatico(self):
        """Testa criação de sistema via função de conveniência."""
        sistema = criar_sistema_ajuste_automatico()
        
        assert isinstance(sistema, AjusteAutomaticoCaudaLonga)
        assert sistema.config is not None
        assert sistema.parametros_atuais is not None


# Testes de integração
class TestIntegracao:
    """Testes de integração do sistema."""
    
    @pytest.fixture
    def sistema_integracao(self):
        """Fixture para sistema de integração."""
        config = MLConfig(
            n_estimators=5,  # Muito reduzido para testes
            max_depth=2,
            min_r2_score=0.3,  # Muito reduzido para testes
            max_mse=0.5
        )
        return AjusteAutomaticoCaudaLonga(config)
    
    def test_fluxo_completo_otimizacao(self, sistema_integracao):
        """Testa fluxo completo de otimização."""
        # 1. Executar ciclo de otimização
        resultado = sistema_integracao.executar_ciclo_otimizacao()
        
        # 2. Verificar que resultado foi gerado
        assert resultado is not None
        assert hasattr(resultado, 'status')
        assert hasattr(resultado, 'tracing_id')
        
        # 3. Gerar relatório
        relatorio = sistema_integracao.gerar_relatorio_otimizacao()
        
        # 4. Verificar relatório
        assert relatorio is not None
        assert "status" in relatorio
    
    def test_persistencia_modelo(self, sistema_integracao, temp_dir):
        """Testa persistência do modelo."""
        with patch.object(sistema_integracao, 'model_dir', Path(temp_dir)):
            # Mock do modelo
            sistema_integracao.model = Mock()
            sistema_integracao.scaler = Mock()
            
            # Testar salvamento
            with patch('infrastructure.ml.ajuste_automatico_cauda_longa.joblib') as mock_joblib:
                sistema_integracao._salvar_modelo()
                mock_joblib.dump.assert_called()
                
                # Testar carregamento
                mock_joblib.load.side_effect = [sistema_integracao.model, sistema_integracao.scaler]
                resultado = sistema_integracao._carregar_modelo()
                
                assert resultado is True


# Testes de performance
class TestPerformance:
    """Testes de performance do sistema."""
    
    def test_performance_coleta_dados(self):
        """Testa performance da coleta de dados."""
        import time
        
        sistema = AjusteAutomaticoCaudaLonga()
        
        inicio = time.time()
        dados = sistema.coletar_dados_treinamento(periodo_dias=10)
        tempo = time.time() - inicio
        
        # Deve ser rápido (< 1 segundo)
        assert tempo < 1.0
        assert len(dados) > 0
    
    def test_performance_preparacao_features(self):
        """Testa performance da preparação de features."""
        import time
        
        sistema = AjusteAutomaticoCaudaLonga()
        
        # Criar dados de teste
        dados = pd.DataFrame({
            "min_palavras": np.random.randint(3, 6, 100),
            "min_caracteres": np.random.randint(15, 20, 100),
            "max_concorrencia": np.random.random(100) * 0.5,
            "score_minimo": np.random.random(100) * 0.3 + 0.5,
            "threshold_complexidade": np.random.random(100) * 0.3 + 0.6,
            "peso_volume": np.random.random(100) * 0.2 + 0.3,
            "peso_cpc": np.random.random(100) * 0.2 + 0.2,
            "peso_concorrencia": np.random.random(100) * 0.2 + 0.2,
            "performance": np.random.random(100) * 0.3 + 0.6
        })
        
        inicio = time.time()
        X, result = sistema.preparar_features(dados)
        tempo = time.time() - inicio
        
        # Deve ser rápido (< 0.1 segundo)
        assert tempo < 0.1
        assert len(X) == 100
        assert len(result) == 100


# Testes de edge cases
class TestEdgeCases:
    """Testes de casos extremos."""
    
    def test_parametros_extremos(self):
        """Testa comportamento com parâmetros extremos."""
        sistema = AjusteAutomaticoCaudaLonga()
        
        parametros_extremos = {
            "min_palavras": 1.0,
            "min_caracteres": 5.0,
            "max_concorrencia": 0.9,
            "score_minimo": 0.1,
            "threshold_complexidade": 0.1,
            "peso_volume": 0.1,
            "peso_cpc": 0.1,
            "peso_concorrencia": 0.1
        }
        
        resultado = sistema._gerar_parametros_otimizados(parametros_extremos, 0.9)
        
        # Deve normalizar os pesos
        total_pesos = resultado["peso_volume"] + resultado["peso_cpc"] + resultado["peso_concorrencia"]
        assert abs(total_pesos - 1.0) < 0.001
    
    def test_performance_extrema(self):
        """Testa comportamento com performance extrema."""
        sistema = AjusteAutomaticoCaudaLonga()
        
        # Performance muito baixa
        resultado_baixa = sistema.aplicar_ajuste_automatico(0.1)
        assert resultado_baixa is not None
        
        # Performance muito alta
        resultado_alta = sistema.aplicar_ajuste_automatico(0.99)
        assert resultado_alta.status == "nao_necessario"


if __name__ == "__main__":
    # Executar testes básicos
    pytest.main([__file__, "-value"]) 