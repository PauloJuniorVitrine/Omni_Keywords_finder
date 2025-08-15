"""
Testes Unitários para Instagram Media Parser
Parser de Mídia do Instagram - Omni Keywords Finder

Prompt: Implementação de testes unitários para parser de mídia do Instagram
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from infrastructure.coleta.instagram_media_parser import parse_post


class TestInstagramMediaParser:
    """Testes para Instagram Media Parser"""
    
    @pytest.fixture
    def sample_post_data(self):
        """Dados de exemplo de post do Instagram"""
        return {
            "id": "post_123456789",
            "media_url": "https://instagram.com/p/post_123456789/media.jpg",
            "caption": "Este é um post de teste #teste #instagram #omni",
            "timestamp": "2024-01-15T10:30:00Z",
            "media_type": "IMAGE",
            "permalink": "https://www.instagram.com/p/post_123456789/",
            "like_count": 150,
            "comment_count": 25,
            "owner": {
                "id": "user_123",
                "username": "test_user"
            }
        }
    
    @pytest.fixture
    def sample_video_post_data(self):
        """Dados de exemplo de post de vídeo do Instagram"""
        return {
            "id": "video_987654321",
            "media_url": "https://instagram.com/p/video_987654321/media.mp4",
            "caption": "Vídeo de teste #video #teste",
            "timestamp": "2024-01-16T15:45:00Z",
            "media_type": "VIDEO",
            "permalink": "https://www.instagram.com/p/video_987654321/",
            "like_count": 300,
            "comment_count": 50,
            "video_duration": 30.5,
            "owner": {
                "id": "user_456",
                "username": "video_user"
            }
        }
    
    @pytest.fixture
    def sample_carousel_post_data(self):
        """Dados de exemplo de post carrossel do Instagram"""
        return {
            "id": "carousel_555666777",
            "media_url": "https://instagram.com/p/carousel_555666777/media1.jpg",
            "caption": "Carrossel de teste #carrossel #multiple",
            "timestamp": "2024-01-17T12:20:00Z",
            "media_type": "CAROUSEL_ALBUM",
            "permalink": "https://www.instagram.com/p/carousel_555666777/",
            "like_count": 200,
            "comment_count": 35,
            "children": [
                {
                    "id": "child_1",
                    "media_url": "https://instagram.com/p/carousel_555666777/media1.jpg",
                    "media_type": "IMAGE"
                },
                {
                    "id": "child_2",
                    "media_url": "https://instagram.com/p/carousel_555666777/media2.jpg",
                    "media_type": "IMAGE"
                }
            ],
            "owner": {
                "id": "user_789",
                "username": "carousel_user"
            }
        }
    
    def test_parse_post_basic(self, sample_post_data):
        """Testa parsing básico de post"""
        result = parse_post(sample_post_data)
        
        assert isinstance(result, dict)
        assert result["id"] == "post_123456789"
        assert result["media_url"] == "https://instagram.com/p/post_123456789/media.jpg"
        assert result["caption"] == "Este é um post de teste #teste #instagram #omni"
        assert result["timestamp"] == "2024-01-15T10:30:00Z"
    
    def test_parse_post_with_missing_fields(self):
        """Testa parsing de post com campos faltantes"""
        incomplete_data = {
            "id": "incomplete_post"
        }
        
        result = parse_post(incomplete_data)
        
        assert isinstance(result, dict)
        assert result["id"] == "incomplete_post"
        assert result["media_url"] == "mock_url"
        assert result["caption"] == ""
        assert result["timestamp"] == "2024-01-01T00:00:00Z"
    
    def test_parse_post_with_empty_data(self):
        """Testa parsing de post com dados vazios"""
        empty_data = {}
        
        result = parse_post(empty_data)
        
        assert isinstance(result, dict)
        assert result["id"] == "mock_id"
        assert result["media_url"] == "mock_url"
        assert result["caption"] == ""
        assert result["timestamp"] == "2024-01-01T00:00:00Z"
    
    def test_parse_post_with_none_values(self):
        """Testa parsing de post com valores None"""
        data_with_none = {
            "id": None,
            "media_url": None,
            "caption": None,
            "timestamp": None
        }
        
        result = parse_post(data_with_none)
        
        assert isinstance(result, dict)
        assert result["id"] == "mock_id"
        assert result["media_url"] == "mock_url"
        assert result["caption"] == ""
        assert result["timestamp"] == "2024-01-01T00:00:00Z"
    
    def test_parse_post_with_extra_fields(self, sample_post_data):
        """Testa parsing de post com campos extras"""
        # Adicionar campos extras que não são processados
        sample_post_data["extra_field"] = "valor_extra"
        sample_post_data["another_field"] = 123
        
        result = parse_post(sample_post_data)
        
        # Campos extras devem ser ignorados
        assert "extra_field" not in result
        assert "another_field" not in result
        assert result["id"] == "post_123456789"
        assert result["media_url"] == "https://instagram.com/p/post_123456789/media.jpg"
    
    def test_parse_post_with_different_data_types(self):
        """Testa parsing de post com diferentes tipos de dados"""
        data_with_different_types = {
            "id": 12345,  # int em vez de string
            "media_url": ["url1", "url2"],  # list em vez de string
            "caption": 123,  # int em vez de string
            "timestamp": datetime.now()  # datetime em vez de string
        }
        
        result = parse_post(data_with_different_types)
        
        assert isinstance(result, dict)
        assert result["id"] == "mock_id"  # Deve usar valor padrão
        assert result["media_url"] == "mock_url"  # Deve usar valor padrão
        assert result["caption"] == ""  # Deve usar valor padrão
        assert result["timestamp"] == "2024-01-01T00:00:00Z"  # Deve usar valor padrão
    
    def test_parse_post_with_special_characters(self):
        """Testa parsing de post com caracteres especiais"""
        data_with_special_chars = {
            "id": "post_123",
            "media_url": "https://instagram.com/p/post_123/media.jpg",
            "caption": "Post com caracteres especiais: @#$%&*()_+-=[]{}|;':\",./<>?",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_special_chars)
        
        assert result["caption"] == "Post com caracteres especiais: @#$%&*()_+-=[]{}|;':\",./<>?"
    
    def test_parse_post_with_unicode_characters(self):
        """Testa parsing de post com caracteres Unicode"""
        data_with_unicode = {
            "id": "post_unicode",
            "media_url": "https://instagram.com/p/post_unicode/media.jpg",
            "caption": "Post com Unicode: 🚀✨🎉 #emoji #unicode #teste",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_unicode)
        
        assert result["caption"] == "Post com Unicode: 🚀✨🎉 #emoji #unicode #teste"
    
    def test_parse_post_with_long_caption(self):
        """Testa parsing de post com caption muito longo"""
        long_caption = "A" * 1000  # Caption de 1000 caracteres
        data_with_long_caption = {
            "id": "post_long",
            "media_url": "https://instagram.com/p/post_long/media.jpg",
            "caption": long_caption,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_long_caption)
        
        assert result["caption"] == long_caption
        assert len(result["caption"]) == 1000
    
    def test_parse_post_with_hashtags(self):
        """Testa parsing de post com hashtags"""
        data_with_hashtags = {
            "id": "post_hashtags",
            "media_url": "https://instagram.com/p/post_hashtags/media.jpg",
            "caption": "Post com #hashtag1 #hashtag2 #hashtag3 #teste #instagram",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_hashtags)
        
        assert "#hashtag1" in result["caption"]
        assert "#hashtag2" in result["caption"]
        assert "#hashtag3" in result["caption"]
        assert "#teste" in result["caption"]
        assert "#instagram" in result["caption"]
    
    def test_parse_post_with_mentions(self):
        """Testa parsing de post com menções"""
        data_with_mentions = {
            "id": "post_mentions",
            "media_url": "https://instagram.com/p/post_mentions/media.jpg",
            "caption": "Post com @usuario1 e @usuario2 #teste",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_mentions)
        
        assert "@usuario1" in result["caption"]
        assert "@usuario2" in result["caption"]
        assert "#teste" in result["caption"]
    
    def test_parse_post_with_urls(self):
        """Testa parsing de post com URLs"""
        data_with_urls = {
            "id": "post_urls",
            "media_url": "https://instagram.com/p/post_urls/media.jpg",
            "caption": "Post com link: https://example.com e outro: http://test.com #link",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_urls)
        
        assert "https://example.com" in result["caption"]
        assert "http://test.com" in result["caption"]
        assert "#link" in result["caption"]
    
    def test_parse_post_with_line_breaks(self):
        """Testa parsing de post com quebras de linha"""
        data_with_line_breaks = {
            "id": "post_line_breaks",
            "media_url": "https://instagram.com/p/post_line_breaks/media.jpg",
            "caption": "Primeira linha\nSegunda linha\nTerceira linha\n#teste",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_line_breaks)
        
        assert "Primeira linha" in result["caption"]
        assert "Segunda linha" in result["caption"]
        assert "Terceira linha" in result["caption"]
        assert "\n" in result["caption"]
        assert "#teste" in result["caption"]
    
    def test_parse_post_with_different_timestamp_formats(self):
        """Testa parsing de post com diferentes formatos de timestamp"""
        # Formato ISO
        data_iso = {
            "id": "post_iso",
            "media_url": "https://instagram.com/p/post_iso/media.jpg",
            "caption": "Post com timestamp ISO",
            "timestamp": "2024-01-15T10:30:00.000Z"
        }
        
        result_iso = parse_post(data_iso)
        assert result_iso["timestamp"] == "2024-01-15T10:30:00.000Z"
        
        # Formato sem timezone
        data_no_tz = {
            "id": "post_no_tz",
            "media_url": "https://instagram.com/p/post_no_tz/media.jpg",
            "caption": "Post sem timezone",
            "timestamp": "2024-01-15T10:30:00"
        }
        
        result_no_tz = parse_post(data_no_tz)
        assert result_no_tz["timestamp"] == "2024-01-15T10:30:00"
    
    def test_parse_post_with_invalid_data_type(self):
        """Testa parsing com tipo de dados inválido"""
        with pytest.raises(AssertionError, match="data deve ser um dicionário"):
            parse_post("string_invalida")
        
        with pytest.raises(AssertionError, match="data deve ser um dicionário"):
            parse_post(123)
        
        with pytest.raises(AssertionError, match="data deve ser um dicionário"):
            parse_post(None)
        
        with pytest.raises(AssertionError, match="data deve ser um dicionário"):
            parse_post([])
    
    def test_parse_post_with_nested_structures(self):
        """Testa parsing de post com estruturas aninhadas"""
        data_with_nested = {
            "id": "post_nested",
            "media_url": "https://instagram.com/p/post_nested/media.jpg",
            "caption": "Post com estruturas aninhadas",
            "timestamp": "2024-01-15T10:30:00Z",
            "owner": {
                "id": "user_123",
                "username": "test_user",
                "profile_picture": "https://example.com/pic.jpg"
            },
            "location": {
                "id": "location_123",
                "name": "São Paulo, Brasil",
                "coordinates": {
                    "latitude": -23.5505,
                    "longitude": -46.6333
                }
            }
        }
        
        result = parse_post(data_with_nested)
        
        # Estruturas aninhadas devem ser ignoradas pelo parser atual
        assert "owner" not in result
        assert "location" not in result
        assert result["id"] == "post_nested"
        assert result["caption"] == "Post com estruturas aninhadas"


class TestInstagramMediaParserIntegration:
    """Testes de integração para Instagram Media Parser"""
    
    def test_parse_multiple_posts(self):
        """Testa parsing de múltiplos posts"""
        posts_data = [
            {
                "id": f"post_{i}",
                "media_url": f"https://instagram.com/p/post_{i}/media.jpg",
                "caption": f"Post {i} de teste #post{i}",
                "timestamp": f"2024-01-{15+i:02d}T10:30:00Z"
            }
            for i in range(1, 6)
        ]
        
        results = [parse_post(post_data) for post_data in posts_data]
        
        assert len(results) == 5
        
        for i, result in enumerate(results, 1):
            assert result["id"] == f"post_{i}"
            assert result["media_url"] == f"https://instagram.com/p/post_{i}/media.jpg"
            assert result["caption"] == f"Post {i} de teste #post{i}"
            assert result["timestamp"] == f"2024-01-{15+i:02d}T10:30:00Z"
    
    def test_parse_posts_with_different_media_types(self):
        """Testa parsing de posts com diferentes tipos de mídia"""
        posts_data = [
            {
                "id": "image_post",
                "media_url": "https://instagram.com/p/image_post/media.jpg",
                "caption": "Post de imagem #image",
                "timestamp": "2024-01-15T10:30:00Z",
                "media_type": "IMAGE"
            },
            {
                "id": "video_post",
                "media_url": "https://instagram.com/p/video_post/media.mp4",
                "caption": "Post de vídeo #video",
                "timestamp": "2024-01-15T11:30:00Z",
                "media_type": "VIDEO"
            },
            {
                "id": "carousel_post",
                "media_url": "https://instagram.com/p/carousel_post/media1.jpg",
                "caption": "Post carrossel #carousel",
                "timestamp": "2024-01-15T12:30:00Z",
                "media_type": "CAROUSEL_ALBUM"
            }
        ]
        
        results = [parse_post(post_data) for post_data in posts_data]
        
        assert len(results) == 3
        
        # Verificar se todos os posts foram parseados corretamente
        assert results[0]["id"] == "image_post"
        assert results[1]["id"] == "video_post"
        assert results[2]["id"] == "carousel_post"
        
        # Verificar se os tipos de mídia não afetam o parsing básico
        for result in results:
            assert "id" in result
            assert "media_url" in result
            assert "caption" in result
            assert "timestamp" in result


class TestInstagramMediaParserErrorHandling:
    """Testes de tratamento de erros para Instagram Media Parser"""
    
    def test_parse_post_with_malformed_data(self):
        """Testa parsing de post com dados malformados"""
        malformed_data = {
            "id": "",  # ID vazio
            "media_url": "invalid_url",  # URL inválida
            "caption": None,  # Caption None
            "timestamp": "invalid_timestamp"  # Timestamp inválido
        }
        
        result = parse_post(malformed_data)
        
        # Deve retornar valores padrão para campos inválidos
        assert result["id"] == "mock_id"
        assert result["media_url"] == "mock_url"
        assert result["caption"] == ""
        assert result["timestamp"] == "2024-01-01T00:00:00Z"
    
    def test_parse_post_with_very_large_data(self):
        """Testa parsing de post com dados muito grandes"""
        large_caption = "A" * 10000  # Caption de 10k caracteres
        large_data = {
            "id": "large_post",
            "media_url": "https://instagram.com/p/large_post/media.jpg",
            "caption": large_caption,
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(large_data)
        
        # Deve processar sem erro
        assert result["caption"] == large_caption
        assert len(result["caption"]) == 10000
    
    def test_parse_post_with_special_json_characters(self):
        """Testa parsing de post com caracteres especiais do JSON"""
        data_with_json_chars = {
            "id": "json_post",
            "media_url": "https://instagram.com/p/json_post/media.jpg",
            "caption": 'Post com "aspas" e \'apóstrofos\' e \\backslashes\\',
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = parse_post(data_with_json_chars)
        
        # Deve preservar caracteres especiais
        assert '"aspas"' in result["caption"]
        assert "'apóstrofos'" in result["caption"]
        assert "\\backslashes\\" in result["caption"]


class TestInstagramMediaParserPerformance:
    """Testes de performance para Instagram Media Parser"""
    
    def test_parse_large_number_of_posts(self):
        """Testa parsing de grande número de posts"""
        import time
        
        # Criar dados de 1000 posts
        posts_data = [
            {
                "id": f"post_{i:06d}",
                "media_url": f"https://instagram.com/p/post_{i:06d}/media.jpg",
                "caption": f"Post {i} de teste com hashtag #post{i} e menção @user{i}",
                "timestamp": f"2024-01-{15+(i%30):02d}T10:30:00Z"
            }
            for i in range(1000)
        ]
        
        start_time = time.time()
        
        results = [parse_post(post_data) for post_data in posts_data]
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        parsing_time = end_time - start_time
        assert parsing_time < 5.0  # Menos de 5 segundos para 1000 posts
        
        # Verificar se todos foram parseados
        assert len(results) == 1000
        assert all(isinstance(result, dict) for result in results)
        assert all("id" in result for result in results)
        assert all("media_url" in result for result in results)
        assert all("caption" in result for result in results)
        assert all("timestamp" in result for result in results)
    
    def test_parse_posts_with_complex_captions(self):
        """Testa parsing de posts com captions complexas"""
        import time
        
        # Criar posts com captions complexas
        complex_captions = [
            f"Post {i} com #hashtag{i} e @user{i} e link https://example{i}.com e emoji 🚀✨🎉 e quebras de linha\nlinha2\nlinha3" * 10
            for i in range(100)
        ]
        
        posts_data = [
            {
                "id": f"complex_post_{i}",
                "media_url": f"https://instagram.com/p/complex_post_{i}/media.jpg",
                "caption": caption,
                "timestamp": f"2024-01-{15+(i%30):02d}T10:30:00Z"
            }
            for i, caption in enumerate(complex_captions)
        ]
        
        start_time = time.time()
        
        results = [parse_post(post_data) for post_data in posts_data]
        
        end_time = time.time()
        
        # Verificar performance
        parsing_time = end_time - start_time
        assert parsing_time < 2.0  # Menos de 2 segundos para 100 posts complexos
        
        # Verificar se captions complexas foram preservadas
        for i, result in enumerate(results):
            assert complex_captions[i] in result["caption"]


if __name__ == "__main__":
    pytest.main([__file__]) 