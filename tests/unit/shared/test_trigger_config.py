from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de TriggerConfig
Tracing ID: TEST_TRIGGER_CONFIG_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de TriggerConfig, cobrindo todos os cenários de uso e
validações de configuração enterprise.
"""

import pytest
import tempfile
import shutil
import json
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from shared.trigger_config import TriggerConfig, ConfigValidator, ConfigManager

class TestTriggerConfig:
    """
    Testes para TriggerConfig.
    
    Cobre funcionalidades da estrutura de dados.
    """
    
    def test_config_creation(self):
        """Testa criação de configuração."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes unitários",
            enabled=True,
            triggers={
                "on_file_change": True,
                "on_quality_drop": True,
                "on_error": False,
                "on_schedule": "daily"
            },
            conditions={
                "min_quality_score": 0.85,
                "max_generation_time": 5.0,
                "max_cost_usd": 0.01,
                "file_extensions": [".py", ".ts", ".js"]
            },
            actions={
                "auto_rollback": True,
                "send_notification": True,
                "log_incident": True,
                "retry_count": 3
            },
            metadata={
                "created_by": "test_user",
                "environment": "test"
            }
        )
        
        assert config.config_id == "config_001"
        assert config.name == "Configuração de Teste"
        assert config.description == "Configuração para testes unitários"
        assert config.enabled == True
        assert config.triggers["on_file_change"] == True
        assert config.triggers["on_quality_drop"] == True
        assert config.triggers["on_error"] == False
        assert config.triggers["on_schedule"] == "daily"
        assert config.conditions["min_quality_score"] == 0.85
        assert config.conditions["max_generation_time"] == 5.0
        assert config.conditions["max_cost_usd"] == 0.01
        assert config.conditions["file_extensions"] == [".py", ".ts", ".js"]
        assert config.actions["auto_rollback"] == True
        assert config.actions["send_notification"] == True
        assert config.actions["log_incident"] == True
        assert config.actions["retry_count"] == 3
        assert config.metadata["created_by"] == "test_user"
        assert config.metadata["environment"] == "test"
    
    def test_config_creation_minimal(self):
        """Testa criação de configuração mínima."""
        config = TriggerConfig(
            config_id="config_minimal",
            name="Configuração Mínima",
            description="Configuração com valores mínimos"
        )
        
        assert config.config_id == "config_minimal"
        assert config.name == "Configuração Mínima"
        assert config.description == "Configuração com valores mínimos"
        assert config.enabled == True  # Valor padrão
        assert config.triggers == {}  # Valor padrão
        assert config.conditions == {}  # Valor padrão
        assert config.actions == {}  # Valor padrão
        assert config.metadata == {}  # Valor padrão
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            triggers={"on_file_change": True},
            conditions={"min_quality_score": 0.85},
            actions={"auto_rollback": True},
            metadata={"test": "data"}
        )
        
        data = config.to_dict()
        
        assert isinstance(data, dict)
        assert data["config_id"] == "config_001"
        assert data["name"] == "Configuração de Teste"
        assert data["description"] == "Configuração para testes"
        assert data["enabled"] == True
        assert data["triggers"] == {"on_file_change": True}
        assert data["conditions"] == {"min_quality_score": 0.85}
        assert data["actions"] == {"auto_rollback": True}
        assert data["metadata"] == {"test": "data"}
    
    def test_to_json(self):
        """Testa conversão para JSON."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            triggers={"on_file_change": True},
            conditions={"min_quality_score": 0.85},
            actions={"auto_rollback": True},
            metadata={"test": "data"}
        )
        
        json_str = config.to_json()
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["config_id"] == "config_001"
        assert data["name"] == "Configuração de Teste"
        assert data["enabled"] == True
    
    def test_to_yaml(self):
        """Testa conversão para YAML."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            triggers={"on_file_change": True},
            conditions={"min_quality_score": 0.85},
            actions={"auto_rollback": True},
            metadata={"test": "data"}
        )
        
        yaml_str = config.to_yaml()
        
        assert isinstance(yaml_str, str)
        data = yaml.safe_load(yaml_str)
        assert data["config_id"] == "config_001"
        assert data["name"] == "Configuração de Teste"
        assert data["enabled"] == True
    
    def test_is_trigger_enabled(self):
        """Testa verificação de trigger habilitado."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            triggers={
                "on_file_change": True,
                "on_quality_drop": False,
                "on_error": True
            }
        )
        
        assert config.is_trigger_enabled("on_file_change") == True
        assert config.is_trigger_enabled("on_quality_drop") == False
        assert config.is_trigger_enabled("on_error") == True
        assert config.is_trigger_enabled("non_existent") == False  # Trigger inexistente
    
    def test_get_condition_value(self):
        """Testa obtenção de valor de condição."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            conditions={
                "min_quality_score": 0.85,
                "max_generation_time": 5.0,
                "max_cost_usd": 0.01
            }
        )
        
        assert config.get_condition_value("min_quality_score") == 0.85
        assert config.get_condition_value("max_generation_time") == 5.0
        assert config.get_condition_value("max_cost_usd") == 0.01
        assert config.get_condition_value("non_existent") is None  # Condição inexistente
    
    def test_get_action_value(self):
        """Testa obtenção de valor de ação."""
        config = TriggerConfig(
            config_id="config_001",
            name="Configuração de Teste",
            description="Configuração para testes",
            enabled=True,
            actions={
                "auto_rollback": True,
                "send_notification": False,
                "retry_count": 3
            }
        )
        
        assert config.get_action_value("auto_rollback") == True
        assert config.get_action_value("send_notification") == False
        assert config.get_action_value("retry_count") == 3
        assert config.get_action_value("non_existent") is None  # Ação inexistente
    
    def test_validate_self(self):
        """Testa validação da própria configuração."""
        # Configuração válida
        valid_config = TriggerConfig(
            config_id="config_valid",
            name="Configuração Válida",
            description="Configuração válida para testes",
            enabled=True,
            triggers={"on_file_change": True},
            conditions={"min_quality_score": 0.85},
            actions={"auto_rollback": True}
        )
        
        assert valid_config.validate_self() == True
        
        # Configuração inválida (sem ID)
        invalid_config = TriggerConfig(
            config_id="",  # ID vazio
            name="Configuração Inválida",
            description="Configuração inválida para testes"
        )
        
        assert invalid_config.validate_self() == False

class TestConfigValidator:
    """
    Testes para ConfigValidator.
    
    Cobre funcionalidades de validação de configuração.
    """
    
    @pytest.fixture
    def config_validator(self):
        """Cria instância do validador de configuração para testes."""
        return ConfigValidator()
    
    @pytest.fixture
    def valid_config(self):
        """Cria configuração válida para testes."""
        return TriggerConfig(
            config_id="config_valid",
            name="Configuração Válida",
            description="Configuração válida para testes",
            enabled=True,
            triggers={
                "on_file_change": True,
                "on_quality_drop": True,
                "on_error": False,
                "on_schedule": "daily"
            },
            conditions={
                "min_quality_score": 0.85,
                "max_generation_time": 5.0,
                "max_cost_usd": 0.01,
                "file_extensions": [".py", ".ts", ".js"]
            },
            actions={
                "auto_rollback": True,
                "send_notification": True,
                "log_incident": True,
                "retry_count": 3
            }
        )
    
    def test_validate_config_structure(self, config_validator, valid_config):
        """Testa validação da estrutura da configuração."""
        result = config_validator.validate_config_structure(valid_config)
        
        assert result["valid"] == True
        assert result["errors"] == []
        assert "warnings" in result
    
    def test_validate_config_structure_invalid(self, config_validator):
        """Testa validação da estrutura com configuração inválida."""
        invalid_config = TriggerConfig(
            config_id="",  # ID vazio
            name="",  # Nome vazio
            description="Configuração inválida"
        )
        
        result = config_validator.validate_config_structure(invalid_config)
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert "config_id" in str(result["errors"]).lower()
        assert "name" in str(result["errors"]).lower()
    
    def test_validate_triggers(self, config_validator, valid_config):
        """Testa validação de triggers."""
        result = config_validator.validate_triggers(valid_config.triggers)
        
        assert result["valid"] == True
        assert result["errors"] == []
    
    def test_validate_triggers_invalid(self, config_validator):
        """Testa validação de triggers inválidos."""
        invalid_triggers = {
            "on_file_change": "invalid_value",  # Deveria ser boolean
            "on_schedule": "invalid_schedule",  # Schedule inválido
            "unknown_trigger": True  # Trigger desconhecido
        }
        
        result = config_validator.validate_triggers(invalid_triggers)
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0
    
    def test_validate_conditions(self, config_validator, valid_config):
        """Testa validação de condições."""
        result = config_validator.validate_conditions(valid_config.conditions)
        
        assert result["valid"] == True
        assert result["errors"] == []
    
    def test_validate_conditions_invalid(self, config_validator):
        """Testa validação de condições inválidas."""
        invalid_conditions = {
            "min_quality_score": 1.5,  # Valor fora do range [0, 1]
            "max_generation_time": -1.0,  # Valor negativo
            "max_cost_usd": "invalid_cost",  # Tipo inválido
            "file_extensions": "not_a_list"  # Deveria ser lista
        }
        
        result = config_validator.validate_conditions(invalid_conditions)
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0
    
    def test_validate_actions(self, config_validator, valid_config):
        """Testa validação de ações."""
        result = config_validator.validate_actions(valid_config.actions)
        
        assert result["valid"] == True
        assert result["errors"] == []
    
    def test_validate_actions_invalid(self, config_validator):
        """Testa validação de ações inválidas."""
        invalid_actions = {
            "auto_rollback": "invalid_value",  # Deveria ser boolean
            "retry_count": -1,  # Valor negativo
            "unknown_action": True  # Ação desconhecida
        }
        
        result = config_validator.validate_actions(invalid_actions)
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0
    
    def test_validate_complete_config(self, config_validator, valid_config):
        """Testa validação completa da configuração."""
        result = config_validator.validate_complete_config(valid_config)
        
        assert result["valid"] == True
        assert result["errors"] == []
        assert "warnings" in result
        assert "structure" in result
        assert "triggers" in result
        assert "conditions" in result
        assert "actions" in result
    
    def test_validate_complete_config_invalid(self, config_validator):
        """Testa validação completa com configuração inválida."""
        invalid_config = TriggerConfig(
            config_id="",
            name="",
            description="Configuração inválida",
            enabled=True,
            triggers={"invalid_trigger": "invalid_value"},
            conditions={"min_quality_score": 1.5},
            actions={"invalid_action": "invalid_value"}
        )
        
        result = config_validator.validate_complete_config(invalid_config)
        
        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert "structure" in result
        assert "triggers" in result
        assert "conditions" in result
        assert "actions" in result

class TestConfigManager:
    """
    Testes para ConfigManager.
    
    Cobre funcionalidades de gerenciamento de configuração.
    """
    
    @pytest.fixture
    def temp_config_dir(self):
        """Cria diretório temporário para configurações de testes."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Cria instância do gerenciador de configuração para testes."""
        return ConfigManager(
            config_dir=temp_config_dir,
            default_config_file="default_config.yaml",
            backup_enabled=True
        )
    
    @pytest.fixture
    def sample_configs(self):
        """Cria configurações de exemplo para testes."""
        return [
            TriggerConfig(
                config_id="config_001",
                name="Configuração 1",
                description="Primeira configuração de teste",
                enabled=True,
                triggers={"on_file_change": True},
                conditions={"min_quality_score": 0.85},
                actions={"auto_rollback": True}
            ),
            TriggerConfig(
                config_id="config_002",
                name="Configuração 2",
                description="Segunda configuração de teste",
                enabled=False,
                triggers={"on_quality_drop": True},
                conditions={"max_generation_time": 5.0},
                actions={"send_notification": True}
            )
        ]
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        manager = ConfigManager()
        
        assert "configs" in manager.config_dir
        assert manager.default_config_file == "default_config.yaml"
        assert manager.backup_enabled == True
        assert len(manager.configs) == 0
        assert len(manager.config_history) == 0
    
    def test_init_custom_values(self, temp_config_dir):
        """Testa inicialização com valores customizados."""
        manager = ConfigManager(
            config_dir=temp_config_dir,
            default_config_file="custom_config.json",
            backup_enabled=False
        )
        
        assert manager.config_dir == temp_config_dir
        assert manager.default_config_file == "custom_config.json"
        assert manager.backup_enabled == False
    
    def test_add_config(self, config_manager, sample_configs):
        """Testa adição de configuração."""
        config = sample_configs[0]
        
        result = config_manager.add_config(config)
        
        # Verificar que configuração foi adicionada
        assert result["success"] == True
        assert result["config_id"] == config.config_id
        assert result["message"] == "Configuração adicionada com sucesso"
        
        # Verificar que foi adicionada ao dicionário
        assert config.config_id in config_manager.configs
        assert config_manager.configs[config.config_id] == config
        
        # Verificar que foi adicionada ao histórico
        assert len(config_manager.config_history) == 1
        assert config_manager.config_history[0]["action"] == "add"
        assert config_manager.config_history[0]["config_id"] == config.config_id
    
    def test_add_config_duplicate(self, config_manager, sample_configs):
        """Testa adição de configuração duplicada."""
        config = sample_configs[0]
        
        # Adicionar primeira vez
        config_manager.add_config(config)
        
        # Tentar adicionar novamente
        result = config_manager.add_config(config)
        
        # Verificar que falhou
        assert result["success"] == False
        assert "já existe" in result["message"].lower()
    
    def test_update_config(self, config_manager, sample_configs):
        """Testa atualização de configuração."""
        config = sample_configs[0]
        
        # Adicionar configuração
        config_manager.add_config(config)
        
        # Atualizar configuração
        updated_config = TriggerConfig(
            config_id=config.config_id,
            name="Configuração Atualizada",
            description="Configuração atualizada para testes",
            enabled=False,
            triggers={"on_file_change": False},
            conditions={"min_quality_score": 0.9},
            actions={"auto_rollback": False}
        )
        
        result = config_manager.update_config(updated_config)
        
        # Verificar que configuração foi atualizada
        assert result["success"] == True
        assert result["config_id"] == config.config_id
        assert result["message"] == "Configuração atualizada com sucesso"
        
        # Verificar que configuração foi atualizada no dicionário
        stored_config = config_manager.configs[config.config_id]
        assert stored_config.name == "Configuração Atualizada"
        assert stored_config.enabled == False
        assert stored_config.triggers["on_file_change"] == False
    
    def test_update_config_not_found(self, config_manager, sample_configs):
        """Testa atualização de configuração inexistente."""
        config = sample_configs[0]
        
        result = config_manager.update_config(config)
        
        # Verificar que falhou
        assert result["success"] == False
        assert "não encontrada" in result["message"].lower()
    
    def test_remove_config(self, config_manager, sample_configs):
        """Testa remoção de configuração."""
        config = sample_configs[0]
        
        # Adicionar configuração
        config_manager.add_config(config)
        
        # Remover configuração
        result = config_manager.remove_config(config.config_id)
        
        # Verificar que configuração foi removida
        assert result["success"] == True
        assert result["config_id"] == config.config_id
        assert result["message"] == "Configuração removida com sucesso"
        
        # Verificar que foi removida do dicionário
        assert config.config_id not in config_manager.configs
        
        # Verificar que foi adicionada ao histórico
        assert len(config_manager.config_history) == 2  # add + remove
        assert config_manager.config_history[-1]["action"] == "remove"
    
    def test_remove_config_not_found(self, config_manager):
        """Testa remoção de configuração inexistente."""
        result = config_manager.remove_config("config_inexistente")
        
        # Verificar que falhou
        assert result["success"] == False
        assert "não encontrada" in result["message"].lower()
    
    def test_get_config(self, config_manager, sample_configs):
        """Testa obtenção de configuração."""
        config = sample_configs[0]
        
        # Adicionar configuração
        config_manager.add_config(config)
        
        # Obter configuração
        retrieved_config = config_manager.get_config(config.config_id)
        
        # Verificar que configuração foi retornada
        assert retrieved_config is not None
        assert retrieved_config.config_id == config.config_id
        assert retrieved_config.name == config.name
    
    def test_get_config_not_found(self, config_manager):
        """Testa obtenção de configuração inexistente."""
        config = config_manager.get_config("config_inexistente")
        
        # Verificar que None foi retornado
        assert config is None
    
    def test_list_configs(self, config_manager, sample_configs):
        """Testa listagem de configurações."""
        # Adicionar configurações
        for config in sample_configs:
            config_manager.add_config(config)
        
        # Listar configurações
        configs_list = config_manager.list_configs()
        
        # Verificar que lista foi retornada
        assert len(configs_list) == 2
        
        # Verificar estrutura dos dados
        for config_info in configs_list:
            assert "config_id" in config_info
            assert "name" in config_info
            assert "description" in config_info
            assert "enabled" in config_info
            assert "triggers_count" in config_info
            assert "conditions_count" in config_info
            assert "actions_count" in config_info
    
    def test_save_configs_to_file(self, config_manager, sample_configs):
        """Testa salvamento de configurações em arquivo."""
        # Adicionar configurações
        for config in sample_configs:
            config_manager.add_config(config)
        
        # Salvar configurações
        file_path = config_manager.save_configs_to_file("test_configs.yaml")
        
        # Verificar que arquivo foi criado
        assert Path(file_path).exists()
        assert file_path.endswith(".yaml")
        
        # Verificar conteúdo do arquivo
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            assert "configs" in data
            assert len(data["configs"]) == 2
            assert data["configs"][0]["config_id"] == "config_001"
            assert data["configs"][1]["config_id"] == "config_002"
    
    def test_load_configs_from_file(self, config_manager, temp_config_dir):
        """Testa carregamento de configurações de arquivo."""
        # Criar arquivo de configurações de teste
        test_file = os.path.join(temp_config_dir, "test_configs.yaml")
        
        test_data = {
            "configs": [
                {
                    "config_id": "config_001",
                    "name": "Configuração 1",
                    "description": "Primeira configuração",
                    "enabled": True,
                    "triggers": {"on_file_change": True},
                    "conditions": {"min_quality_score": 0.85},
                    "actions": {"auto_rollback": True},
                    "metadata": {}
                },
                {
                    "config_id": "config_002",
                    "name": "Configuração 2",
                    "description": "Segunda configuração",
                    "enabled": False,
                    "triggers": {"on_quality_drop": True},
                    "conditions": {"max_generation_time": 5.0},
                    "actions": {"send_notification": True},
                    "metadata": {}
                }
            ]
        }
        
        with open(test_file, 'w') as f:
            yaml.dump(test_data, f)
        
        # Carregar configurações
        result = config_manager.load_configs_from_file(test_file)
        
        # Verificar que configurações foram carregadas
        assert result["success"] == True
        assert result["loaded_count"] == 2
        assert result["errors"] == []
        
        # Verificar que foram adicionadas ao dicionário
        assert len(config_manager.configs) == 2
        assert "config_001" in config_manager.configs
        assert "config_002" in config_manager.configs
    
    def test_load_configs_from_file_not_found(self, config_manager):
        """Testa carregamento de configurações de arquivo inexistente."""
        non_existent_file = "/path/to/non/existent/file.yaml"
        
        result = config_manager.load_configs_from_file(non_existent_file)
        
        # Verificar que falhou
        assert result["success"] == False
        assert "não encontrado" in result["message"].lower()
    
    def test_get_config_history(self, config_manager, sample_configs):
        """Testa obtenção do histórico de configurações."""
        # Adicionar e remover configuração
        config = sample_configs[0]
        config_manager.add_config(config)
        config_manager.remove_config(config.config_id)
        
        # Obter histórico
        history = config_manager.get_config_history()
        
        # Verificar que histórico foi retornado
        assert len(history) == 2
        
        # Verificar estrutura dos dados
        for entry in history:
            assert "timestamp" in entry
            assert "action" in entry
            assert "config_id" in entry
            assert "user" in entry
            assert "details" in entry

class TestTriggerConfigIntegration:
    """
    Testes de integração para TriggerConfig.
    
    Testa cenários mais complexos e interações entre componentes.
    """
    
    @pytest.fixture
    def integration_setup(self, temp_config_dir):
        """Configuração para testes de integração."""
        validator = ConfigValidator()
        manager = ConfigManager(config_dir=temp_config_dir)
        return validator, manager
    
    def test_full_workflow_validation_and_management(self, integration_setup, sample_configs):
        """Testa workflow completo de validação e gerenciamento."""
        validator, manager = integration_setup
        
        # Validar e adicionar configurações
        for config in sample_configs:
            # Validar configuração
            validation_result = validator.validate_complete_config(config)
            assert validation_result["valid"] == True
            
            # Adicionar configuração
            add_result = manager.add_config(config)
            assert add_result["success"] == True
        
        # Verificar que configurações foram adicionadas
        assert len(manager.configs) == 2
        
        # Listar configurações
        configs_list = manager.list_configs()
        assert len(configs_list) == 2
        
        # Salvar configurações
        file_path = manager.save_configs_to_file("integration_test.yaml")
        assert Path(file_path).exists()
        
        # Carregar configurações
        load_result = manager.load_configs_from_file(file_path)
        assert load_result["success"] == True
    
    def test_error_handling_robustness(self, integration_setup):
        """Testa robustez no tratamento de erros."""
        validator, manager = integration_setup
        
        # Teste com configuração inválida
        invalid_config = TriggerConfig(
            config_id="",
            name="",
            description="Configuração inválida",
            enabled=True,
            triggers={"invalid_trigger": "invalid_value"},
            conditions={"min_quality_score": 1.5},
            actions={"invalid_action": "invalid_value"}
        )
        
        # Validar configuração inválida
        validation_result = validator.validate_complete_config(invalid_config)
        assert validation_result["valid"] == False
        assert len(validation_result["errors"]) > 0
        
        # Tentar adicionar configuração inválida
        add_result = manager.add_config(invalid_config)
        assert add_result["success"] == False

if __name__ == "__main__":
    pytest.main([__file__]) 