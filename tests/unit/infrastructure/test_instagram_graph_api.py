#!/usr/bin/env python3
"""
Testes Unitários - Instagram Graph API
=====================================

Tracing ID: TEST_INSTAGRAM_GRAPH_API_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/instagram_graph_api.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 4.2
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json
import os
import asyncio

from infrastructure.coleta.instagram_graph_api import (
    InstagramGraphAPI, InstagramGraphScope, InstagramBusinessAccount,
    InstagramBusinessMedia, InstagramInsights, InstagramComment,
    InstagramGraphAPIError, create_instagram_graph_api
)


class TestInstagramGraphAPI:
    @pytest.fixture
    def page_access_token(self):
        return "test_page_access_token"

    @pytest.fixture
    def api_client(self, page_access_token):
        return InstagramGraphAPI(page_access_token)

    def test_instagram_graph_scope_enum(self):
        """Testa enum InstagramGraphScope."""
        assert InstagramGraphScope.INSTAGRAM_BASIC.value == "instagram_basic"
        assert InstagramGraphScope.INSTAGRAM_CONTENT_PUBLISH.value == "instagram_content_publish"
        assert InstagramGraphScope.INSTAGRAM_MANAGE_COMMENTS.value == "instagram_manage_comments"
        assert InstagramGraphScope.INSTAGRAM_MANAGE_INSIGHTS.value == "instagram_manage_insights"
        assert InstagramGraphScope.PAGES_READ_ENGAGEMENT.value == "pages_read_engagement"
        assert InstagramGraphScope.PAGES_SHOW_LIST.value == "pages_show_list"

    def test_instagram_business_account_dataclass(self):
        """Testa criação de objeto InstagramBusinessAccount."""
        account = InstagramBusinessAccount(
            id="business_id",
            username="business_user",
            name="Business Name",
            profile_picture_url="http://test.com/profile.jpg",
            website="http://test.com",
            biography="Test biography",
            follows_count=100,
            followers_count=1000,
            media_count=50,
            is_verified=True,
            is_private=False,
            business_category_name="Business",
            category_name="Category"
        )
        assert account.id == "business_id"
        assert account.username == "business_user"
        assert account.followers_count == 1000
        assert account.is_verified is True

    def test_instagram_business_media_dataclass(self):
        """Testa criação de objeto InstagramBusinessMedia."""
        owner = InstagramBusinessAccount(
            id="owner_id",
            username="owner",
            name="Owner Name",
            profile_picture_url=None,
            website=None,
            biography=None,
            follows_count=0,
            followers_count=0,
            media_count=0,
            is_verified=False,
            is_private=False
        )
        
        media = InstagramBusinessMedia(
            id="media_id",
            caption="Test caption",
            media_type="IMAGE",
            media_url="http://test.com/media.jpg",
            permalink="http://instagram.com/p/media_id",
            thumbnail_url="http://test.com/thumb.jpg",
            timestamp=datetime.now(),
            like_count=100,
            comments_count=10,
            owner=owner
        )
        assert media.id == "media_id"
        assert media.media_type == "IMAGE"
        assert media.like_count == 100
        assert media.owner.username == "owner"

    def test_instagram_insights_dataclass(self):
        """Testa criação de objeto InstagramInsights."""
        insights = InstagramInsights(
            impressions=1000,
            reach=800,
            engagement=200,
            saved=50,
            video_views=500,
            video_view_rate=0.75,
            profile_views=100,
            follows=25
        )
        assert insights.impressions == 1000
        assert insights.reach == 800
        assert insights.video_view_rate == 0.75
        assert insights.follows == 25

    def test_instagram_comment_dataclass(self):
        """Testa criação de objeto InstagramComment."""
        comment = InstagramComment(
            id="comment_id",
            text="Great post!",
            timestamp=datetime.now(),
            username="user123",
            like_count=5,
            is_hidden=False,
            is_reply=False
        )
        assert comment.id == "comment_id"
        assert comment.text == "Great post!"
        assert comment.username == "user123"
        assert comment.is_hidden is False

    def test_instagram_graph_api_error(self):
        """Testa criação de exceção customizada."""
        error = InstagramGraphAPIError(
            "Test error",
            error_code="190",
            error_subcode="100",
            http_status=400
        )
        assert str(error) == "Test error"
        assert error.error_code == "190"
        assert error.error_subcode == "100"
        assert error.http_status == 400

    def test_instagram_graph_api_initialization(self, page_access_token):
        """Testa inicialização do cliente Instagram Graph API."""
        client = InstagramGraphAPI(page_access_token)
        assert client.page_access_token == page_access_token
        assert client.api_version == "v18.0"
        assert "graph.facebook.com/v18.0" in client.base_url
        assert client.session is None

    @patch('infrastructure.coleta.instagram_graph_api.INSTAGRAM_CONFIG')
    def test_instagram_graph_api_initialization_with_config(self, mock_config):
        """Testa inicialização com configuração."""
        mock_config.get.return_value = "config_token"
        client = InstagramGraphAPI()
        assert client.page_access_token == "config_token"

    @pytest.mark.asyncio
    async def test_get_session_creation(self, api_client):
        """Testa criação de sessão HTTP."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value = AsyncMock()
            session = await api_client._get_session()
            assert session is not None
            mock_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_reuse(self, api_client):
        """Testa reutilização de sessão existente."""
        mock_session = AsyncMock()
        api_client.session = mock_session
        
        session = await api_client._get_session()
        assert session == mock_session

    @pytest.mark.asyncio
    async def test_make_request_success(self, api_client):
        """Testa requisição bem-sucedida."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            with patch.object(api_client.rate_limiter, 'acquire', return_value=True):
                with patch.object(api_client.rate_limiter, 'record_response'):
                    result = await api_client._make_request("test/endpoint")
                    assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_make_request_no_token(self):
        """Testa requisição sem token de acesso."""
        client = InstagramGraphAPI(None)
        with pytest.raises(InstagramGraphAPIError, match="Page Access Token não configurado"):
            await client._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_exceeded(self, api_client):
        """Testa requisição com rate limit excedido."""
        with patch.object(api_client.rate_limiter, 'acquire', return_value=False):
            with pytest.raises(InstagramGraphAPIError, match="Rate limit atingido"):
                await api_client._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, api_client):
        """Testa requisição com erro HTTP."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={
            "error": {
                "message": "Invalid token",
                "code": "190"
            }
        })
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            with patch.object(api_client.rate_limiter, 'acquire', return_value=True):
                with patch.object(api_client.rate_limiter, 'record_response'):
                    with pytest.raises(InstagramGraphAPIError, match="Invalid token"):
                        await api_client._make_request("test/endpoint")

    @pytest.mark.asyncio
    async def test_get_business_accounts_success(self, api_client):
        """Testa obtenção de contas de negócio."""
        mock_data = {
            "data": [{
                "instagram_business_account": {
                    "id": "business_id",
                    "username": "business_user",
                    "name": "Business Name",
                    "profile_picture_url": "http://test.com/profile.jpg",
                    "follows_count": 100,
                    "followers_count": 1000,
                    "media_count": 50,
                    "is_verified": True,
                    "is_private": False
                }
            }]
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    accounts = await api_client.get_business_accounts()
                    assert len(accounts) == 1
                    assert accounts[0].id == "business_id"
                    assert accounts[0].username == "business_user"

    @pytest.mark.asyncio
    async def test_get_business_accounts_from_cache(self, api_client):
        """Testa obtenção de contas de negócio do cache."""
        cached_data = [{
            "id": "business_id",
            "username": "business_user",
            "name": "Business Name",
            "profile_picture_url": None,
            "website": None,
            "biography": None,
            "follows_count": 100,
            "followers_count": 1000,
            "media_count": 50,
            "is_verified": True,
            "is_private": False,
            "business_category_name": None,
            "category_name": None
        }]
        
        with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=cached_data):
            accounts = await api_client.get_business_accounts()
            assert len(accounts) == 1
            assert accounts[0].id == "business_id"

    @pytest.mark.asyncio
    async def test_get_business_account_info_success(self, api_client):
        """Testa obtenção de informações de conta de negócio."""
        mock_data = {
            "id": "business_id",
            "username": "business_user",
            "name": "Business Name",
            "profile_picture_url": "http://test.com/profile.jpg",
            "follows_count": 100,
            "followers_count": 1000,
            "media_count": 50,
            "is_verified": True,
            "is_private": False
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    account = await api_client.get_business_account_info("business_id")
                    assert account.id == "business_id"
                    assert account.username == "business_user"
                    assert account.followers_count == 1000

    @pytest.mark.asyncio
    async def test_get_business_media_success(self, api_client):
        """Testa obtenção de mídia de negócio."""
        mock_data = {
            "data": [{
                "id": "media_id",
                "caption": "Test caption",
                "media_type": "IMAGE",
                "media_url": "http://test.com/media.jpg",
                "permalink": "http://instagram.com/p/media_id",
                "thumbnail_url": "http://test.com/thumb.jpg",
                "timestamp": "2023-01-01T00:00:00Z",
                "like_count": 100,
                "comments_count": 10,
                "owner": {
                    "id": "owner_id",
                    "username": "owner",
                    "name": "Owner Name"
                }
            }]
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    media_list = await api_client.get_business_media("business_id")
                    assert len(media_list) == 1
                    assert media_list[0].id == "media_id"
                    assert media_list[0].media_type == "IMAGE"
                    assert media_list[0].owner.username == "owner"

    @pytest.mark.asyncio
    async def test_get_media_insights_success(self, api_client):
        """Testa obtenção de insights de mídia."""
        mock_data = {
            "data": [
                {
                    "name": "impressions",
                    "values": [{"value": 1000}]
                },
                {
                    "name": "reach",
                    "values": [{"value": 800}]
                },
                {
                    "name": "engagement",
                    "values": [{"value": 200}]
                },
                {
                    "name": "saved",
                    "values": [{"value": 50}]
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    insights = await api_client.get_media_insights("media_id")
                    assert insights.impressions == 1000
                    assert insights.reach == 800
                    assert insights.engagement == 200
                    assert insights.saved == 50

    @pytest.mark.asyncio
    async def test_get_account_insights_success(self, api_client):
        """Testa obtenção de insights de conta."""
        mock_data = {
            "data": [
                {
                    "name": "profile_views",
                    "values": [{"value": 100}]
                },
                {
                    "name": "follows",
                    "values": [{"value": 25}]
                }
            ]
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    insights = await api_client.get_account_insights("business_id")
                    assert insights.profile_views == 100
                    assert insights.follows == 25

    @pytest.mark.asyncio
    async def test_get_media_comments_success(self, api_client):
        """Testa obtenção de comentários de mídia."""
        mock_data = {
            "data": [{
                "id": "comment_id",
                "text": "Great post!",
                "timestamp": "2023-01-01T00:00:00Z",
                "username": "user123",
                "like_count": 5,
                "is_hidden": False,
                "is_reply": False
            }]
        }
        
        with patch.object(api_client, '_make_request', return_value=mock_data):
            with patch.object(api_client.fallback_manager, 'get_cached_value', return_value=None):
                with patch.object(api_client.fallback_manager, 'set_cached_value'):
                    comments = await api_client.get_media_comments("media_id")
                    assert len(comments) == 1
                    assert comments[0].id == "comment_id"
                    assert comments[0].text == "Great post!"
                    assert comments[0].username == "user123"

    @pytest.mark.asyncio
    async def test_reply_to_comment_success(self, api_client):
        """Testa resposta a comentário."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            result = await api_client.reply_to_comment("comment_id", "Thank you!")
            assert result is True

    @pytest.mark.asyncio
    async def test_reply_to_comment_error(self, api_client):
        """Testa erro ao responder comentário."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={
            "error": {
                "message": "Invalid comment",
                "code": "100"
            }
        })
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            with pytest.raises(InstagramGraphAPIError, match="Invalid comment"):
                await api_client.reply_to_comment("comment_id", "Thank you!")

    @pytest.mark.asyncio
    async def test_hide_comment_success(self, api_client):
        """Testa ocultação de comentário."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            result = await api_client.hide_comment("comment_id", True)
            assert result is True

    @pytest.mark.asyncio
    async def test_hide_comment_show(self, api_client):
        """Testa exibição de comentário."""
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(api_client, '_get_session', return_value=mock_session):
            result = await api_client.hide_comment("comment_id", False)
            assert result is True

    @pytest.mark.asyncio
    async def test_close_session(self, api_client):
        """Testa fechamento de sessão."""
        mock_session = AsyncMock()
        api_client.session = mock_session
        
        await api_client.close()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, page_access_token):
        """Testa uso como context manager."""
        with patch('infrastructure.coleta.instagram_graph_api.InstagramGraphAPI') as mock_api_class:
            mock_api = AsyncMock()
            mock_api_class.return_value = mock_api
            
            async with InstagramGraphAPI(page_access_token) as api:
                assert api == mock_api
            
            mock_api.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_instagram_graph_api(self, page_access_token):
        """Testa função de conveniência."""
        with patch('infrastructure.coleta.instagram_graph_api.InstagramGraphAPI') as mock_api_class:
            mock_api = AsyncMock()
            mock_api_class.return_value = mock_api
            
            result = await create_instagram_graph_api(page_access_token)
            assert result == mock_api
            mock_api_class.assert_called_once_with(page_access_token)

    def test_edge_cases(self, api_client):
        """Testa casos edge."""
        # Teste de dataclass com valores opcionais
        insights = InstagramInsights(
            impressions=0,
            reach=0,
            engagement=0,
            saved=0
        )
        assert insights.video_views is None
        assert insights.profile_views is None
        
        # Teste de comentário com parent_id
        comment = InstagramComment(
            id="reply_id",
            text="Reply",
            timestamp=datetime.now(),
            username="user",
            like_count=0,
            is_hidden=False,
            is_reply=True,
            parent_comment_id="parent_id"
        )
        assert comment.parent_comment_id == "parent_id"
        assert comment.is_reply is True


if __name__ == "__main__":
    pytest.main([__file__]) 