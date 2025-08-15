#!/usr/bin/env python3
"""
Testes Unitários - Sistema de Unificação de Placeholders
=======================================================

Tracing ID: TEST_PLACEHOLDER_UNIFICATION_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para o sistema de unificação de placeholders:
- Testes de detecção de formato
- Testes de migração
- Testes de validação
- Testes de performance

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.processamento.placeholder_unification_system import (
    PlaceholderUnificationSystem,
    PlaceholderFormat,
    PlaceholderType,
    MigrationResult,
    migrate_placeholders,
    detect_placeholder_format,
    get_migration_stats
)


class TestPlaceholderUnificationSystem:
    """Testes para o sistema de unificação de placeholders."""
    
    @pytest.fixture
    def unification_system(self):
        """Fixture para o sistema de unificação."""
        return PlaceholderUnificationSystem()
    
    def test_initialization(self, unification_system):
        """Testa inicialização do sistema."""
        assert unification_system is not None
        assert len(unification_system.placeholder_mappings) > 0
        assert len(unification_system.required_placeholders) > 0
        assert len(unification_system.optional_placeholders) > 0
    
    def test_detect_format_old_brackets(self, unification_system):
        """Testa detecção de formato antigo com colchetes."""
        text = "Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE]"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.OLD_BRACKETS
    
    def test_detect_format_new_curly(self, unification_system):
        """Testa detecção de formato novo com chaves."""
        text = "Crie um {content_type} sobre {primary_keyword}"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.NEW_CURLY
    
    def test_detect_format_template_dollar(self, unification_system):
        """Testa detecção de formato template com dólar."""
        text = "Crie um $content_type sobre $primary_keyword"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.TEMPLATE_DOLLAR
    
    def test_detect_format_angular_brackets(self, unification_system):
        """Testa detecção de formato com colchetes angulares."""
        text = "Crie um <content_type> sobre <primary_keyword>"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.ANGULAR_BRACKETS
    
    def test_detect_format_double_brackets(self, unification_system):
        """Testa detecção de formato com colchetes duplos."""
        text = "Crie um [[content_type]] sobre [[primary_keyword]]"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.DOUBLE_BRACKETS
    
    def test_detect_format_no_placeholders(self, unification_system):
        """Testa detecção quando não há placeholders."""
        text = "Texto simples sem placeholders"
        detected_format = unification_system.detect_format(text)
        assert detected_format == PlaceholderFormat.NEW_CURLY  # Padrão
    
    def test_migrate_old_brackets_to_new_curly(self, unification_system):
        """Testa migração de formato antigo para novo."""
        original_text = "Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE]"
        result = unification_system.migrate_to_standard_format(original_text)
        
        assert result.success
        assert result.migrated_text == "Crie um {content_type} sobre {primary_keyword}"
        assert result.format_detected == PlaceholderFormat.OLD_BRACKETS
        assert len(result.migrations_applied) > 0
    
    def test_migrate_template_dollar_to_new_curly(self, unification_system):
        """Testa migração de template dollar para novo formato."""
        original_text = "Crie um $content_type sobre $primary_keyword"
        result = unification_system.migrate_to_standard_format(original_text)
        
        assert result.success
        assert result.migrated_text == "Crie um {content_type} sobre {primary_keyword}"
        assert result.format_detected == PlaceholderFormat.TEMPLATE_DOLLAR
    
    def test_migrate_already_standard_format(self, unification_system):
        """Testa migração quando já está no formato padrão."""
        original_text = "Crie um {content_type} sobre {primary_keyword}"
        result = unification_system.migrate_to_standard_format(original_text)
        
        assert result.success
        assert result.migrated_text == original_text
        assert result.format_detected == PlaceholderFormat.NEW_CURLY
        assert len(result.migrations_applied) == 0
    
    def test_migrate_with_force(self, unification_system):
        """Testa migração forçada."""
        original_text = "Crie um {content_type} sobre {primary_keyword}"
        result = unification_system.migrate_to_standard_format(original_text, force_migration=True)
        
        assert result.success
        assert result.migrated_text == original_text
        assert len(result.warnings) > 0  # Deve ter warning sobre já estar no formato padrão
    
    def test_migrate_complex_text(self, unification_system):
        """Testa migração de texto complexo."""
        original_text = """
        Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE] para [PUBLICO-ALVO].
        O conteúdo deve ter [COMPRIMENTO] palavras e usar tom [TOM].
        Inclua [PALAVRAS-SECUNDARIAS] e [CLUSTER DE CONTEÚDO].
        """
        
        result = unification_system.migrate_to_standard_format(original_text)
        
        assert result.success
        assert "{content_type}" in result.migrated_text
        assert "{primary_keyword}" in result.migrated_text
        assert "{target_audience}" in result.migrated_text
        assert "{length}" in result.migrated_text
        assert "{tone}" in result.migrated_text
        assert "{secondary_keywords}" in result.migrated_text
        assert "{cluster_content}" in result.migrated_text
    
    def test_validate_migrated_text_success(self, unification_system):
        """Testa validação de texto migrado com sucesso."""
        text = "Crie um {content_type} sobre {primary_keyword} para {target_audience}"
        validation_result = unification_system._validate_migrated_text(text)
        
        assert len(validation_result["errors"]) == 0
        assert validation_result["errors"] == []
    
    def test_validate_migrated_text_missing_required(self, unification_system):
        """Testa validação com placeholders obrigatórios ausentes."""
        text = "Crie um {content_type} sobre {target_audience}"  # Falta primary_keyword
        validation_result = unification_system._validate_migrated_text(text)
        
        assert len(validation_result["errors"]) > 0
        assert any("obrigatórios ausentes" in error for error in validation_result["errors"])
    
    def test_validate_migrated_text_unmapped_placeholders(self, unification_system):
        """Testa validação com placeholders não mapeados."""
        text = "Crie um {content_type} sobre {unknown_placeholder}"
        validation_result = unification_system._validate_migrated_text(text)
        
        assert len(validation_result["warnings"]) > 0
        assert any("não mapeados" in warning for warning in validation_result["warnings"])
    
    def test_validate_migrated_text_syntax_errors(self, unification_system):
        """Testa validação com erros de sintaxe."""
        text = "Crie um {content_type} sobre { primary_keyword }"  # Espaços extras
        validation_result = unification_system._validate_migrated_text(text)
        
        assert len(validation_result["errors"]) > 0
        assert any("malformados" in error for error in validation_result["errors"])
    
    def test_check_missing_required_placeholders(self, unification_system):
        """Testa verificação de placeholders obrigatórios ausentes."""
        text = "Crie um {content_type} sobre {target_audience}"  # Falta primary_keyword
        missing = unification_system._check_missing_required_placeholders(text)
        
        assert "primary_keyword" in missing
        assert "cluster_id" in missing
        assert "categoria" in missing
    
    def test_detect_unmapped_placeholders(self, unification_system):
        """Testa detecção de placeholders não mapeados."""
        text = "Crie um {content_type} sobre {unknown_placeholder} e {another_unknown}"
        unmapped = unification_system._detect_unmapped_placeholders(text)
        
        assert "unknown_placeholder" in unmapped
        assert "another_unknown" in unmapped
        assert "content_type" not in unmapped  # Deve estar mapeado
    
    def test_check_placeholder_syntax(self, unification_system):
        """Testa verificação de sintaxe de placeholders."""
        # Placeholder malformado
        text = "Crie um {content_type} sobre { primary_keyword }"
        errors = unification_system._check_placeholder_syntax(text)
        
        assert len(errors) > 0
        assert any("malformados" in error for error in errors)
    
    def test_get_migration_statistics(self, unification_system):
        """Testa obtenção de estatísticas de migração."""
        # Executar algumas migrações
        unification_system.migrate_to_standard_format("Crie um [TIPO-CONTEUDO]")
        unification_system.migrate_to_standard_format("Faça $content_type")
        
        stats = unification_system.get_migration_statistics()
        
        assert "total_migrations" in stats
        assert "successful_migrations" in stats
        assert "failed_migrations" in stats
        assert "success_rate" in stats
        assert "format_detections" in stats
        assert "avg_migration_time" in stats
        assert "cache_size" in stats
    
    def test_clear_cache(self, unification_system):
        """Testa limpeza do cache."""
        # Adicionar alguns itens ao cache
        unification_system.migration_cache["test1"] = {"result": "test", "timestamp": 123}
        unification_system.migration_cache["test2"] = {"result": "test", "timestamp": 456}
        
        assert len(unification_system.migration_cache) == 2
        
        # Limpar cache
        unification_system.clear_cache()
        
        assert len(unification_system.migration_cache) == 0
    
    def test_migration_with_errors(self, unification_system):
        """Testa migração com erros."""
        # Simular erro durante migração
        with patch.object(unification_system, '_validate_migrated_text', side_effect=Exception("Erro de validação")):
            result = unification_system.migrate_to_standard_format("Texto de teste")
            
            assert not result.success
            assert "Erro durante migração" in result.errors[0]
    
    def test_migration_cache_functionality(self, unification_system):
        """Testa funcionalidade do cache de migração."""
        text = "Crie um [TIPO-CONTEUDO]"
        
        # Primeira migração
        result1 = unification_system.migrate_to_standard_format(text)
        
        # Segunda migração (deve usar cache)
        result2 = unification_system.migrate_to_standard_format(text)
        
        assert result1.migrated_text == result2.migrated_text
        assert result1.success == result2.success


class TestPlaceholderUnificationFunctions:
    """Testes para funções de conveniência."""
    
    def test_migrate_placeholders_function(self):
        """Testa função de conveniência migrate_placeholders."""
        text = "Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE]"
        result = migrate_placeholders(text)
        
        assert result.success
        assert "{content_type}" in result.migrated_text
        assert "{primary_keyword}" in result.migrated_text
    
    def test_detect_placeholder_format_function(self):
        """Testa função de conveniência detect_placeholder_format."""
        text = "Crie um [TIPO-CONTEUDO]"
        detected_format = detect_placeholder_format(text)
        
        assert detected_format == PlaceholderFormat.OLD_BRACKETS
    
    def test_get_migration_stats_function(self):
        """Testa função de conveniência get_migration_stats."""
        stats = get_migration_stats()
        
        assert "total_migrations" in stats
        assert "successful_migrations" in stats
        assert "failed_migrations" in stats
        assert "success_rate" in stats


class TestPlaceholderUnificationPerformance:
    """Testes de performance do sistema de unificação."""
    
    @pytest.fixture
    def large_text(self):
        """Fixture para texto grande."""
        return """
        Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE] para [PUBLICO-ALVO].
        O conteúdo deve ter [COMPRIMENTO] palavras e usar tom [TOM].
        Inclua [PALAVRAS-SECUNDARIAS] e [CLUSTER DE CONTEÚDO].
        """ * 100  # Repetir 100 vezes
    
    def test_migration_performance(self, large_text):
        """Testa performance da migração."""
        import time
        
        start_time = time.time()
        result = migrate_placeholders(large_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result.success
        assert execution_time < 1.0  # Deve executar em menos de 1 segundo
        assert result.migrated_text != large_text  # Deve ter mudanças
    
    def test_cache_performance(self):
        """Testa performance do cache."""
        import time
        
        text = "Crie um [TIPO-CONTEUDO] sobre [PALAVRA-CHAVE]"
        
        # Primeira execução (sem cache)
        start_time = time.time()
        result1 = migrate_placeholders(text)
        time1 = time.time() - start_time
        
        # Segunda execução (com cache)
        start_time = time.time()
        result2 = migrate_placeholders(text)
        time2 = time.time() - start_time
        
        assert result1.success == result2.success
        assert result1.migrated_text == result2.migrated_text
        assert time2 < time1  # Com cache deve ser mais rápido


class TestPlaceholderUnificationEdgeCases:
    """Testes para casos extremos."""
    
    def test_empty_text(self):
        """Testa migração de texto vazio."""
        result = migrate_placeholders("")
        
        assert result.success
        assert result.migrated_text == ""
    
    def test_text_without_placeholders(self):
        """Testa migração de texto sem placeholders."""
        text = "Texto simples sem placeholders"
        result = migrate_placeholders(text)
        
        assert result.success
        assert result.migrated_text == text
    
    def test_text_with_special_characters(self):
        """Testa migração de texto com caracteres especiais."""
        text = "Crie um [TIPO-CONTEUDO] com caracteres especiais: áéíóú çãõ"
        result = migrate_placeholders(text)
        
        assert result.success
        assert "áéíóú" in result.migrated_text
        assert "çãõ" in result.migrated_text
    
    def test_text_with_html_tags(self):
        """Testa migração de texto com tags HTML."""
        text = "Crie um <strong>[TIPO-CONTEUDO]</strong> sobre [PALAVRA-CHAVE]"
        result = migrate_placeholders(text)
        
        assert result.success
        assert "<strong>" in result.migrated_text
        assert "</strong>" in result.migrated_text
        assert "{content_type}" in result.migrated_text
    
    def test_text_with_multiple_formats(self):
        """Testa migração de texto com múltiplos formatos."""
        text = "Crie um [TIPO-CONTEUDO] sobre $primary_keyword e <target_audience>"
        result = migrate_placeholders(text)
        
        assert result.success
        assert "{content_type}" in result.migrated_text
        assert "{primary_keyword}" in result.migrated_text
        assert "{target_audience}" in result.migrated_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 