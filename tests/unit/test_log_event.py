"""
Testes Unitários para Log Event
Sistema de Log de Eventos - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de log de eventos
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.app.utils.log_event import log_event
from backend.app.models import Log


class TestLogEvent:
    """Testes para Log Event"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock da sessão do banco de dados"""
        with patch('backend.app.utils.log_event.db') as mock_db:
            mock_db.session.add = Mock()
            mock_db.session.commit = Mock()
            yield mock_db
    
    @pytest.fixture
    def mock_g(self):
        """Mock do objeto g do Flask"""
        with patch('backend.app.utils.log_event.g') as mock_g:
            mock_g.current_user = "test_user"
            yield mock_g
    
    @pytest.fixture
    def mock_log_model(self):
        """Mock do modelo Log"""
        with patch('backend.app.utils.log_event.Log') as mock_log:
            mock_instance = Mock()
            mock_log.return_value = mock_instance
            yield mock_log
    
    def test_log_event_basic(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento básico"""
        result = log_event(
            tipo_operacao="criação",
            entidade="Nicho",
            id_referencia=123,
            usuario="admin",
            detalhes="Nicho criado com sucesso"
        )
        
        # Verificar se Log foi criado com parâmetros corretos
        mock_log_model.assert_called_once_with(
            tipo_operacao="criação",
            entidade="Nicho",
            id_referencia=123,
            usuario="admin",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes="Nicho criado com sucesso"
        )
        
        # Verificar se foi adicionado à sessão
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        
        # Verificar se commit foi executado
        mock_db_session.session.commit.assert_called_once()
        
        # Verificar se retornou o log criado
        assert result == mock_log_model.return_value
    
    def test_log_event_without_optional_params(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento sem parâmetros opcionais"""
        result = log_event(
            tipo_operacao="consulta",
            entidade="Categoria"
        )
        
        # Verificar se Log foi criado com valores padrão
        mock_log_model.assert_called_once_with(
            tipo_operacao="consulta",
            entidade="Categoria",
            id_referencia=None,
            usuario="test_user",  # Deve usar current_user do g
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=None
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_without_current_user(self, mock_db_session, mock_log_model):
        """Testa log de evento sem current_user no g"""
        with patch('backend.app.utils.log_event.g') as mock_g:
            # Remover current_user do g
            del mock_g.current_user
            
            result = log_event(
                tipo_operacao="erro",
                entidade="Sistema",
                detalhes="Erro interno"
            )
            
            # Verificar se usuario foi None
            mock_log_model.assert_called_once_with(
                tipo_operacao="erro",
                entidade="Sistema",
                id_referencia=None,
                usuario=None,
                timestamp=mock_log_model.return_value.timestamp,
                detalhes="Erro interno"
            )
            
            mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
            mock_db_session.session.commit.assert_called_once()
            assert result == mock_log_model.return_value
    
    def test_log_event_with_all_params(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com todos os parâmetros"""
        result = log_event(
            tipo_operacao="alteração",
            entidade="Execução",
            id_referencia=456,
            usuario="user123",
            detalhes="Execução alterada para status 'concluída'"
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="alteração",
            entidade="Execução",
            id_referencia=456,
            usuario="user123",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes="Execução alterada para status 'concluída'"
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_special_characters(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com caracteres especiais"""
        special_details = "Log com caracteres especiais: @#$%&*()_+-=[]{}|;':\",./<>?"
        
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            detalhes=special_details
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=None,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=special_details
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_unicode_characters(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com caracteres Unicode"""
        unicode_details = "Log com Unicode: 🚀✨🎉 #emoji #unicode #teste"
        
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            detalhes=unicode_details
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=None,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=unicode_details
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_long_details(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com detalhes muito longos"""
        long_details = "A" * 1000  # 1000 caracteres
        
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            detalhes=long_details
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=None,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=long_details
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_empty_strings(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com strings vazias"""
        result = log_event(
            tipo_operacao="",
            entidade="",
            detalhes=""
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="",
            entidade="",
            id_referencia=None,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=""
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_none_values(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com valores None"""
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=None,
            usuario=None,
            detalhes=None
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=None,
            usuario=None,
            timestamp=mock_log_model.return_value.timestamp,
            detalhes=None
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_zero_id(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com ID zero"""
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=0,
            detalhes="ID zero"
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=0,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes="ID zero"
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_negative_id(self, mock_db_session, mock_g, mock_log_model):
        """Testa log de evento com ID negativo"""
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=-123,
            detalhes="ID negativo"
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="teste",
            entidade="Sistema",
            id_referencia=-123,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes="ID negativo"
        )
        
        mock_db_session.session.add.assert_called_once_with(mock_log_model.return_value)
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value


class TestLogEventIntegration:
    """Testes de integração para Log Event"""
    
    def test_log_event_multiple_calls(self, mock_db_session, mock_g, mock_log_model):
        """Testa múltiplas chamadas de log_event"""
        # Primeira chamada
        result1 = log_event(
            tipo_operacao="criação",
            entidade="Nicho",
            id_referencia=1,
            usuario="admin",
            detalhes="Primeiro nicho"
        )
        
        # Segunda chamada
        result2 = log_event(
            tipo_operacao="alteração",
            entidade="Categoria",
            id_referencia=2,
            usuario="user1",
            detalhes="Categoria alterada"
        )
        
        # Terceira chamada
        result3 = log_event(
            tipo_operacao="deleção",
            entidade="Execução",
            id_referencia=3,
            detalhes="Execução removida"
        )
        
        # Verificar se foram criados 3 logs
        assert mock_log_model.call_count == 3
        
        # Verificar se foram feitos 3 commits
        assert mock_db_session.session.commit.call_count == 3
        
        # Verificar se foram adicionados 3 logs
        assert mock_db_session.session.add.call_count == 3
        
        # Verificar se retornaram instâncias diferentes
        assert result1 != result2
        assert result2 != result3
        assert result1 != result3
    
    def test_log_event_with_different_operation_types(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com diferentes tipos de operação"""
        operation_types = [
            "criação", "alteração", "deleção", "consulta", "execução",
            "erro", "warning", "info", "debug", "acesso_negado"
        ]
        
        results = []
        for op_type in operation_types:
            result = log_event(
                tipo_operacao=op_type,
                entidade="Sistema",
                detalhes=f"Operação do tipo: {op_type}"
            )
            results.append(result)
        
        # Verificar se foram criados logs para todos os tipos
        assert mock_log_model.call_count == len(operation_types)
        assert mock_db_session.session.commit.call_count == len(operation_types)
        assert len(results) == len(operation_types)
        
        # Verificar se todos os resultados são diferentes
        assert len(set(results)) == len(operation_types)
    
    def test_log_event_with_different_entities(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com diferentes entidades"""
        entities = [
            "Nicho", "Categoria", "Execução", "Usuário", "Sistema",
            "Pagamento", "Auditoria", "Segurança", "API", "Database"
        ]
        
        results = []
        for entity in entities:
            result = log_event(
                tipo_operacao="teste",
                entidade=entity,
                detalhes=f"Teste para entidade: {entity}"
            )
            results.append(result)
        
        # Verificar se foram criados logs para todas as entidades
        assert mock_log_model.call_count == len(entities)
        assert mock_db_session.session.commit.call_count == len(entities)
        assert len(results) == len(entities)
        
        # Verificar se todos os resultados são diferentes
        assert len(set(results)) == len(entities)


class TestLogEventErrorHandling:
    """Testes de tratamento de erros para Log Event"""
    
    def test_log_event_with_db_session_error(self, mock_g, mock_log_model):
        """Testa log_event com erro na sessão do banco"""
        with patch('backend.app.utils.log_event.db') as mock_db:
            mock_db.session.add = Mock()
            mock_db.session.commit = Mock(side_effect=Exception("Database error"))
            
            with pytest.raises(Exception, match="Database error"):
                log_event(
                    tipo_operacao="teste",
                    entidade="Sistema",
                    detalhes="Teste com erro"
                )
            
            # Verificar se add foi chamado mesmo com erro
            mock_db.session.add.assert_called_once()
    
    def test_log_event_with_log_creation_error(self, mock_db_session, mock_g):
        """Testa log_event com erro na criação do Log"""
        with patch('backend.app.utils.log_event.Log') as mock_log:
            mock_log.side_effect = Exception("Log creation error")
            
            with pytest.raises(Exception, match="Log creation error"):
                log_event(
                    tipo_operacao="teste",
                    entidade="Sistema",
                    detalhes="Teste com erro"
                )
            
            # Verificar se add e commit não foram chamados
            mock_db_session.session.add.assert_not_called()
            mock_db_session.session.commit.assert_not_called()
    
    def test_log_event_with_getattr_error(self, mock_db_session, mock_log_model):
        """Testa log_event com erro no getattr"""
        with patch('backend.app.utils.log_event.g') as mock_g:
            # Simular erro no getattr
            mock_g.__getattr__ = Mock(side_effect=AttributeError("current_user not found"))
            
            with pytest.raises(AttributeError, match="current_user not found"):
                log_event(
                    tipo_operacao="teste",
                    entidade="Sistema",
                    detalhes="Teste com erro"
                )
    
    def test_log_event_with_invalid_parameters(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com parâmetros inválidos"""
        # Teste com tipo_operacao None
        with pytest.raises(TypeError):
            log_event(
                tipo_operacao=None,
                entidade="Sistema"
            )
        
        # Teste com entidade None
        with pytest.raises(TypeError):
            log_event(
                tipo_operacao="teste",
                entidade=None
            )
        
        # Teste com parâmetros extras (não deve causar erro)
        result = log_event(
            tipo_operacao="teste",
            entidade="Sistema",
            extra_param="valor_extra"
        )
        
        # Deve funcionar normalmente
        assert result == mock_log_model.return_value


class TestLogEventPerformance:
    """Testes de performance para Log Event"""
    
    def test_log_event_large_scale(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event em grande escala"""
        import time
        
        start_time = time.time()
        
        results = []
        for i in range(1000):
            result = log_event(
                tipo_operacao=f"op_{i}",
                entidade=f"entity_{i}",
                id_referencia=i,
                usuario=f"user_{i}",
                detalhes=f"Detalhes do evento {i}"
            )
            results.append(result)
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Menos de 10 segundos para 1000 logs
        
        # Verificar se todos foram processados
        assert mock_log_model.call_count == 1000
        assert mock_db_session.session.commit.call_count == 1000
        assert len(results) == 1000
        
        # Verificar se todos os resultados são diferentes
        assert len(set(results)) == 1000
    
    def test_log_event_with_complex_details(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com detalhes complexos"""
        import time
        
        # Criar detalhes complexos
        complex_details = []
        for i in range(100):
            detail = f"Evento {i} com detalhes complexos: 🚀✨🎉 #teste{i} @user{i} https://example{i}.com"
            complex_details.append(detail)
        
        start_time = time.time()
        
        results = []
        for i, detail in enumerate(complex_details):
            result = log_event(
                tipo_operacao=f"complex_op_{i}",
                entidade=f"complex_entity_{i}",
                detalhes=detail
            )
            results.append(result)
        
        end_time = time.time()
        
        # Verificar performance
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Menos de 5 segundos para 100 logs complexos
        
        # Verificar se todos foram processados
        assert mock_log_model.call_count == 100
        assert mock_db_session.session.commit.call_count == 100
        assert len(results) == 100
        
        # Verificar se detalhes complexos foram preservados
        for i, result in enumerate(results):
            assert complex_details[i] in str(mock_log_model.call_args_list[i])


class TestLogEventEdgeCases:
    """Testes de casos extremos para Log Event"""
    
    def test_log_event_with_very_long_strings(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com strings muito longas"""
        very_long_string = "A" * 10000  # 10k caracteres
        
        result = log_event(
            tipo_operacao=very_long_string,
            entidade=very_long_string,
            detalhes=very_long_string
        )
        
        # Deve processar sem erro
        mock_log_model.assert_called_once()
        mock_db_session.session.add.assert_called_once()
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_special_json_characters(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com caracteres especiais do JSON"""
        json_chars = 'Log com "aspas" e \'apóstrofos\' e \\backslashes\\ e quebras\nlinha2'
        
        result = log_event(
            tipo_operacao="json_test",
            entidade="Sistema",
            detalhes=json_chars
        )
        
        # Deve preservar caracteres especiais
        mock_log_model.assert_called_once()
        call_args = mock_log_model.call_args
        assert json_chars in str(call_args)
        
        mock_db_session.session.add.assert_called_once()
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value
    
    def test_log_event_with_numeric_strings(self, mock_db_session, mock_g, mock_log_model):
        """Testa log_event com strings numéricas"""
        result = log_event(
            tipo_operacao="123",
            entidade="456",
            detalhes="789"
        )
        
        mock_log_model.assert_called_once_with(
            tipo_operacao="123",
            entidade="456",
            id_referencia=None,
            usuario="test_user",
            timestamp=mock_log_model.return_value.timestamp,
            detalhes="789"
        )
        
        mock_db_session.session.add.assert_called_once()
        mock_db_session.session.commit.assert_called_once()
        assert result == mock_log_model.return_value


if __name__ == "__main__":
    pytest.main([__file__]) 