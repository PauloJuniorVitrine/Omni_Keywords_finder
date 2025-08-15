#!/usr/bin/env python3
"""
Testes Unitários - Detector Híbrido de Lacunas
==============================================

Tracing ID: TEST_HYBRID_LACUNA_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para o sistema híbrido de detecção de lacunas:
- RegexLacunaDetector
- BasicValidator  
- HybridLacunaDetector
- Sistema de fallback

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import re
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Importar classes do sistema
from infrastructure.processamento.hybrid_lacuna_detector import (
    RegexLacunaDetector,
    BasicValidator,
    HybridLacunaDetector,
    FallbackSystem,
    DetectedGap,
    DetectionResult,
    DetectionMethod,
    ValidationLevel,
    PlaceholderType
)
from infrastructure.processamento.placeholder_unification_system import (
    PlaceholderUnificationSystem,
    MigrationResult
)


class TestRegexLacunaDetector:
    """Testes para o detector de lacunas baseado em regex."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.detector = RegexLacunaDetector()
        self.sample_text = """
        Crie um artigo sobre {primary_keyword} que inclua {secondary_keywords}.
        O cluster {cluster_id} contém informações sobre {categoria}.
        Use um tom {tone} e comprimento {length} palavras.
        """
    
    def test_initialization(self):
        """Testa inicialização do detector."""
        assert self.detector.placeholder_patterns is not None
        assert self.detector.compiled_patterns is not None
        assert len(self.detector.placeholder_patterns) > 0
        
        # Verificar se todos os tipos de placeholder estão mapeados
        expected_types = [
            PlaceholderType.PRIMARY_KEYWORD,
            PlaceholderType.SECONDARY_KEYWORDS,
            PlaceholderType.CLUSTER_CONTENT,
            PlaceholderType.CLUSTER_ID,
            PlaceholderType.CATEGORIA,
            PlaceholderType.CUSTOM
        ]
        
        for placeholder_type in expected_types:
            assert placeholder_type in self.detector.placeholder_patterns
    
    def test_detect_primary_keyword(self):
        """Testa detecção de palavra-chave principal."""
        text = "Artigo sobre {primary_keyword} para SEO"
        gaps = self.detector.detect_gaps(text)
        
        assert len(gaps) == 1
        gap = gaps[0]
        
        assert gap.placeholder_type == PlaceholderType.PRIMARY_KEYWORD
        assert gap.placeholder_name == "primary_keyword"
        assert gap.confidence > 0.9
        assert gap.detection_method == DetectionMethod.REGEX
        assert gap.validation_level == ValidationLevel.BASIC
    
    def test_detect_multiple_placeholders(self):
        """Testa detecção de múltiplos placeholders."""
        gaps = self.detector.detect_gaps(self.sample_text)
        
        # Deve detectar pelo menos 6 placeholders
        assert len(gaps) >= 6
        
        # Verificar tipos específicos
        placeholder_types = [gap.placeholder_type for gap in gaps]
        assert PlaceholderType.PRIMARY_KEYWORD in placeholder_types
        assert PlaceholderType.SECONDARY_KEYWORDS in placeholder_types
        assert PlaceholderType.CLUSTER_ID in placeholder_types
        assert PlaceholderType.CATEGORIA in placeholder_types
        assert PlaceholderType.TONE in placeholder_types
        assert PlaceholderType.LENGTH in placeholder_types
    
    def test_detect_custom_placeholder(self):
        """Testa detecção de placeholders customizados."""
        text = "Use {custom_field} e {another_custom} no conteúdo"
        gaps = self.detector.detect_gaps(text)
        
        assert len(gaps) == 2
        
        custom_gaps = [g for g in gaps if g.placeholder_type == PlaceholderType.CUSTOM]
        assert len(custom_gaps) == 2
        
        custom_names = [g.placeholder_name for g in custom_gaps]
        assert "custom_field" in custom_names
        assert "another_custom" in custom_names
    
    def test_extract_context(self):
        """Testa extração de contexto."""
        text = "Texto anterior. {primary_keyword} Texto posterior."
        gaps = self.detector.detect_gaps(text)
        
        assert len(gaps) == 1
        gap = gaps[0]
        
        # Verificar se o contexto foi extraído
        assert "Texto anterior" in gap.context
        assert "Texto posterior" in gap.context
        assert "{primary_keyword}" in gap.context
    
    def test_confidence_calculation(self):
        """Testa cálculo de confiança."""
        text = "{primary_keyword} {cluster_id} {custom_field}"
        gaps = self.detector.detect_gaps(text)
        
        for gap in gaps:
            assert 0.0 <= gap.confidence <= 1.0
            
            # Placeholders principais devem ter alta confiança
            if gap.placeholder_type in [PlaceholderType.PRIMARY_KEYWORD, PlaceholderType.CLUSTER_ID]:
                assert gap.confidence >= 0.95
    
    def test_case_insensitive_detection(self):
        """Testa detecção case-insensitive."""
        text = "{PRIMARY_KEYWORD} {Primary_Keyword} {primary_keyword}"
        gaps = self.detector.detect_gaps(text)
        
        # Deve detectar todas as variações
        assert len(gaps) == 3
    
    def test_no_placeholders(self):
        """Testa texto sem placeholders."""
        text = "Texto simples sem placeholders"
        gaps = self.detector.detect_gaps(text)
        
        assert len(gaps) == 0
    
    def test_empty_text(self):
        """Testa texto vazio."""
        gaps = self.detector.detect_gaps("")
        
        assert len(gaps) == 0
    
    def test_metadata_inclusion(self):
        """Testa inclusão de metadados."""
        text = "{primary_keyword}"
        gaps = self.detector.detect_gaps(text)
        
        assert len(gaps) == 1
        gap = gaps[0]
        
        assert "pattern_used" in gap.metadata
        assert "match_length" in gap.metadata
        assert gap.metadata["match_length"] == len("{primary_keyword}")


class TestBasicValidator:
    """Testes para o validador básico de lacunas."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.validator = BasicValidator()
        self.sample_gap = DetectedGap(
            placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
            placeholder_name="primary_keyword",
            start_pos=0,
            end_pos=20,
            context="Artigo sobre {primary_keyword}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
    
    def test_initialization(self):
        """Testa inicialização do validador."""
        assert self.validator.validation_rules is not None
        assert len(self.validator.validation_rules) > 0
        
        # Verificar se regras existem para tipos principais
        assert PlaceholderType.PRIMARY_KEYWORD in self.validator.validation_rules
        assert PlaceholderType.SECONDARY_KEYWORDS in self.validator.validation_rules
        assert PlaceholderType.CLUSTER_ID in self.validator.validation_rules
    
    def test_validate_primary_keyword_valid(self):
        """Testa validação de palavra-chave principal válida."""
        value = "marketing digital"
        result = self.validator.validate_gap(self.sample_gap, value)
        
        assert result["is_valid"] is True
        assert result["confidence"] > 0.9
        assert len(result["issues"]) == 0
        assert result["validation_score"] > 0.9
    
    def test_validate_primary_keyword_invalid_length(self):
        """Testa validação de palavra-chave com comprimento inválido."""
        # Muito curta
        value = "a"
        result = self.validator.validate_gap(self.sample_gap, value)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
        assert result["confidence"] < 1.0
        
        # Muito longa
        value = "a" * 150
        result = self.validator.validate_gap(self.sample_gap, value)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
    
    def test_validate_primary_keyword_invalid_format(self):
        """Testa validação de palavra-chave com formato inválido."""
        value = "marketing@digital#$%"
        result = self.validator.validate_gap(self.sample_gap, value)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
        assert result["confidence"] < 1.0
    
    def test_validate_required_field_empty(self):
        """Testa validação de campo obrigatório vazio."""
        value = ""
        result = self.validator.validate_gap(self.sample_gap, value)
        
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
        assert "obrigatória" in result["issues"][0].lower()
    
    def test_validate_content_type_enum(self):
        """Testa validação de enum para tipo de conteúdo."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.CONTENT_TYPE,
            placeholder_name="content_type",
            start_pos=0,
            end_pos=20,
            context="Tipo: {content_type}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        # Valor válido
        value = "artigo"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is True
        
        # Valor inválido
        value = "invalid_type"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is False
        assert len(result["suggestions"]) > 0
    
    def test_validate_tone_enum(self):
        """Testa validação de enum para tom."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.TONE,
            placeholder_name="tone",
            start_pos=0,
            end_pos=20,
            context="Tom: {tone}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        # Valor válido
        value = "formal"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is True
        
        # Valor inválido
        value = "invalid_tone"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is False
    
    def test_validate_length_numeric(self):
        """Testa validação de comprimento numérico."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.LENGTH,
            placeholder_name="length",
            start_pos=0,
            end_pos=20,
            context="Comprimento: {length}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        # Valor válido
        value = "1000"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is True
        
        # Valor inválido (não numérico)
        value = "abc"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is False
        
        # Valor inválido (fora do range)
        value = "50"
        result = self.validator.validate_gap(gap, value)
        assert result["is_valid"] is False
    
    def test_validate_unknown_type(self):
        """Testa validação de tipo desconhecido."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.CUSTOM,
            placeholder_name="unknown_type",
            start_pos=0,
            end_pos=20,
            context="Campo: {unknown_type}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = "test_value"
        result = self.validator.validate_gap(gap, value)
        
        # Deve retornar válido para tipos desconhecidos
        assert result["is_valid"] is True
        assert result["confidence"] == 1.0


class TestFallbackSystem:
    """Testes para o sistema de fallback."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.fallback_system = FallbackSystem()
        self.sample_gap = DetectedGap(
            placeholder_type=PlaceholderType.PRIMARY_KEYWORD,
            placeholder_name="primary_keyword",
            start_pos=0,
            end_pos=20,
            context="Artigo sobre {primary_keyword}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
    
    def test_initialization(self):
        """Testa inicialização do sistema de fallback."""
        assert self.fallback_system.fallback_values is not None
        assert len(self.fallback_system.fallback_values) > 0
    
    def test_get_fallback_value_primary_keyword(self):
        """Testa obtenção de valor de fallback para palavra-chave principal."""
        value = self.fallback_system.get_fallback_value(self.sample_gap, self.sample_gap.context)
        
        assert value is not None
        assert len(value) > 0
        assert isinstance(value, str)
    
    def test_get_fallback_value_secondary_keywords(self):
        """Testa obtenção de valor de fallback para palavras-chave secundárias."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.SECONDARY_KEYWORDS,
            placeholder_name="secondary_keywords",
            start_pos=0,
            end_pos=20,
            context="Incluir {secondary_keywords}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = self.fallback_system.get_fallback_value(gap, gap.context)
        
        assert value is not None
        assert len(value) > 0
        assert "," in value  # Deve ser uma lista separada por vírgulas
    
    def test_get_fallback_value_cluster_id(self):
        """Testa obtenção de valor de fallback para ID do cluster."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.CLUSTER_ID,
            placeholder_name="cluster_id",
            start_pos=0,
            end_pos=20,
            context="Cluster {cluster_id}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = self.fallback_system.get_fallback_value(gap, gap.context)
        
        assert value is not None
        assert len(value) > 0
        # Deve ser um ID válido (sem espaços, caracteres especiais)
        assert " " not in value
        assert re.match(r'^[a-zA-Z0-9\-_]+$', value)
    
    def test_get_fallback_value_content_type(self):
        """Testa obtenção de valor de fallback para tipo de conteúdo."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.CONTENT_TYPE,
            placeholder_name="content_type",
            start_pos=0,
            end_pos=20,
            context="Tipo: {content_type}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = self.fallback_system.get_fallback_value(gap, gap.context)
        
        assert value is not None
        assert value in ["artigo", "post", "vídeo", "infográfico", "e-book", "newsletter"]
    
    def test_get_fallback_value_tone(self):
        """Testa obtenção de valor de fallback para tom."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.TONE,
            placeholder_name="tone",
            start_pos=0,
            end_pos=20,
            context="Tom: {tone}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = self.fallback_system.get_fallback_value(gap, gap.context)
        
        assert value is not None
        assert value in ["formal", "informal", "profissional", "casual", "técnico", "amigável"]
    
    def test_get_fallback_value_custom(self):
        """Testa obtenção de valor de fallback para placeholder customizado."""
        gap = DetectedGap(
            placeholder_type=PlaceholderType.CUSTOM,
            placeholder_name="custom_field",
            start_pos=0,
            end_pos=20,
            context="Campo: {custom_field}",
            confidence=0.95,
            detection_method=DetectionMethod.REGEX,
            validation_level=ValidationLevel.BASIC
        )
        
        value = self.fallback_system.get_fallback_value(gap, gap.context)
        
        assert value is not None
        assert len(value) > 0
        assert isinstance(value, str)


class TestHybridLacunaDetector:
    """Testes para o detector híbrido de lacunas."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.detector = HybridLacunaDetector()
        self.sample_text = """
        Crie um artigo sobre {primary_keyword} que inclua {secondary_keywords}.
        O cluster {cluster_id} contém informações sobre {categoria}.
        Use um tom {tone} e comprimento {length} palavras.
        """
    
    def test_initialization(self):
        """Testa inicialização do detector híbrido."""
        assert self.detector.regex_detector is not None
        assert self.detector.validator is not None
        assert self.detector.fallback_system is not None
        assert self.detector.unification_system is not None
        assert self.detector.metrics is not None
    
    @patch('infrastructure.processamento.hybrid_lacuna_detector.PlaceholderUnificationSystem')
    def test_detect_gaps_with_migration(self, mock_unification_system):
        """Testa detecção com migração de placeholders."""
        # Mock do sistema de unificação
        mock_unification = Mock()
        mock_unification.migrate_to_standard_format.return_value = MigrationResult(
            original_text=self.sample_text,
            migrated_text=self.sample_text,
            format_detected=None,
            migrations_applied=[],
            errors=[],
            warnings=[],
            success=True,
            timestamp=None,
            hash_before="",
            hash_after=""
        )
        mock_unification_system.return_value = mock_unification
        
        # Criar detector com mock
        detector = HybridLacunaDetector()
        detector.unification_system = mock_unification
        
        result = detector.detect_gaps(self.sample_text)
        
        assert result.success is True
        assert result.total_gaps > 0
        assert result.method_used == DetectionMethod.HYBRID
        assert result.validation_level == ValidationLevel.BASIC
    
    @patch('infrastructure.processamento.hybrid_lacuna_detector.PlaceholderUnificationSystem')
    def test_detect_gaps_migration_failure(self, mock_unification_system):
        """Testa detecção com falha na migração."""
        # Mock do sistema de unificação com falha
        mock_unification = Mock()
        mock_unification.migrate_to_standard_format.return_value = MigrationResult(
            original_text=self.sample_text,
            migrated_text="",
            format_detected=None,
            migrations_applied=[],
            errors=["Erro de migração"],
            warnings=[],
            success=False,
            timestamp=None,
            hash_before="",
            hash_after=""
        )
        mock_unification_system.return_value = mock_unification
        
        # Criar detector com mock
        detector = HybridLacunaDetector()
        detector.unification_system = mock_unification
        
        result = detector.detect_gaps(self.sample_text)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert result.method_used == DetectionMethod.FALLBACK
    
    def test_detect_gaps_without_validation(self):
        """Testa detecção sem validação."""
        result = self.detector.detect_gaps(self.sample_text, enable_validation=False)
        
        assert result.success is True
        assert result.total_gaps > 0
        assert result.method_used == DetectionMethod.REGEX
        
        # Verificar se os gaps não têm valores sugeridos
        for gap in result.gaps:
            assert gap.suggested_value is None
            assert gap.validation_score is None
    
    def test_detect_gaps_with_validation(self):
        """Testa detecção com validação."""
        result = self.detector.detect_gaps(self.sample_text, enable_validation=True)
        
        assert result.success is True
        assert result.total_gaps > 0
        assert result.method_used == DetectionMethod.HYBRID
        
        # Verificar se os gaps têm valores sugeridos
        for gap in result.gaps:
            assert gap.suggested_value is not None
            assert gap.validation_score is not None
            assert "validation_result" in gap.metadata
    
    def test_metrics_update(self):
        """Testa atualização de métricas."""
        initial_metrics = dict(self.detector.metrics)
        
        result = self.detector.detect_gaps(self.sample_text)
        
        # Verificar se as métricas foram atualizadas
        assert self.detector.metrics["total_detections"] > initial_metrics["total_detections"]
        assert self.detector.metrics["method_usage"]["regex"] > 0
        assert len(self.detector.metrics["detection_times"]) > 0
    
    def test_error_handling(self):
        """Testa tratamento de erros."""
        # Forçar erro passando None
        result = self.detector.detect_gaps(None)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert result.method_used == DetectionMethod.FALLBACK
    
    def test_empty_text(self):
        """Testa texto vazio."""
        result = self.detector.detect_gaps("")
        
        assert result.success is True
        assert result.total_gaps == 0
        assert result.confidence_avg == 0.0
    
    def test_detection_time_tracking(self):
        """Testa rastreamento de tempo de detecção."""
        start_time = time.time()
        result = self.detector.detect_gaps(self.sample_text)
        end_time = time.time()
        
        # Verificar se o tempo foi registrado
        assert result.detection_time > 0
        assert result.detection_time <= (end_time - start_time) + 0.1  # Margem de erro
    
    def test_confidence_calculation(self):
        """Testa cálculo de confiança média."""
        result = self.detector.detect_gaps(self.sample_text)
        
        if result.total_gaps > 0:
            assert 0.0 <= result.confidence_avg <= 1.0
            
            # Verificar se a confiança média corresponde aos gaps
            calculated_avg = sum(g.confidence for g in result.gaps) / len(result.gaps)
            assert abs(result.confidence_avg - calculated_avg) < 0.01


class TestIntegration:
    """Testes de integração do sistema completo."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.detector = HybridLacunaDetector()
        self.complex_text = """
        [PALAVRA-CHAVE PRINCIPAL DO CLUSTER] é um tópico importante.
        Inclua [PALAVRAS-CHAVE SECUNDÁRIAS] no conteúdo.
        O [CLUSTER] {cluster_id} pertence à categoria {categoria}.
        Use tom {tone} e comprimento {length} palavras.
        """
    
    def test_mixed_format_migration_and_detection(self):
        """Testa migração e detecção de formato misto."""
        result = self.detector.detect_gaps(self.complex_text)
        
        assert result.success is True
        assert result.total_gaps > 0
        
        # Verificar se placeholders antigos foram migrados
        if result.metadata and result.metadata.get("migration_applied"):
            assert len(result.metadata["migration_details"]) > 0
    
    def test_full_workflow(self):
        """Testa workflow completo: migração -> detecção -> validação -> fallback."""
        result = self.detector.detect_gaps(self.complex_text, enable_validation=True)
        
        assert result.success is True
        assert result.total_gaps > 0
        
        for gap in result.gaps:
            # Verificar se cada gap tem todas as informações necessárias
            assert gap.placeholder_type is not None
            assert gap.placeholder_name is not None
            assert gap.confidence > 0
            assert gap.suggested_value is not None
            assert gap.validation_score is not None
            assert gap.metadata is not None
    
    def test_performance_benchmark(self):
        """Testa performance do sistema."""
        large_text = self.complex_text * 100  # Texto grande
        
        start_time = time.time()
        result = self.detector.detect_gaps(large_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verificar se a execução foi rápida (< 1 segundo)
        assert execution_time < 1.0
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 