"""
Testes unitários para backend/app/services/
Tracing ID: BACKEND_TESTS_SERVICES_001_20250127
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from backend.app.services import (
    NichoService, CategoriaService, ExecucaoService, 
    KeywordService, ProcessamentoService, AnalyticsService
)

class TestNichoService:
    """Testes para o serviço de nichos."""
    
    def test_create_nicho_success(self, db_session):
        """Testa criação bem-sucedida de nicho."""
        service = NichoService(db_session)
        
        nicho_data = {
            "nome": "Novo Nicho",
            "descricao": "Descrição do novo nicho",
            "ativo": True
        }
        
        with patch('backend.app.services.nicho_service.validate_nicho_data') as mock_validate:
            mock_validate.return_value = True
            
            nicho = service.create_nicho(nicho_data)
            
            assert nicho is not None
            assert nicho.nome == "Novo Nicho"
            assert nicho.descricao == "Descrição do novo nicho"
            assert nicho.ativo is True
    
    def test_create_nicho_validation_error(self, db_session):
        """Testa criação de nicho com dados inválidos."""
        service = NichoService(db_session)
        
        invalid_data = {
            "nome": "",  # Nome vazio
            "descricao": "Descrição válida"
        }
        
        with patch('backend.app.services.nicho_service.validate_nicho_data') as mock_validate:
            mock_validate.side_effect = ValueError("Nome não pode ser vazio")
            
            with pytest.raises(ValueError, match="Nome não pode ser vazio"):
                service.create_nicho(invalid_data)
    
    def test_get_nicho_by_id_success(self, db_session):
        """Testa busca de nicho por ID com sucesso."""
        service = NichoService(db_session)
        
        # Criar nicho de teste
        nicho = service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        # Buscar por ID
        found_nicho = service.get_nicho_by_id(nicho.id)
        
        assert found_nicho is not None
        assert found_nicho.id == nicho.id
        assert found_nicho.nome == "Nicho Teste"
    
    def test_get_nicho_by_id_not_found(self, db_session):
        """Testa busca de nicho inexistente."""
        service = NichoService(db_session)
        
        nicho = service.get_nicho_by_id(999)
        assert nicho is None
    
    def test_update_nicho_success(self, db_session):
        """Testa atualização bem-sucedida de nicho."""
        service = NichoService(db_session)
        
        # Criar nicho
        nicho = service.create_nicho({
            "nome": "Nicho Original",
            "descricao": "Descrição original",
            "ativo": True
        })
        
        # Atualizar dados
        update_data = {
            "nome": "Nicho Atualizado",
            "descricao": "Descrição atualizada"
        }
        
        with patch('backend.app.services.nicho_service.validate_nicho_data') as mock_validate:
            mock_validate.return_value = True
            
            updated_nicho = service.update_nicho(nicho.id, update_data)
            
            assert updated_nicho.nome == "Nicho Atualizado"
            assert updated_nicho.descricao == "Descrição atualizada"
    
    def test_delete_nicho_success(self, db_session):
        """Testa exclusão bem-sucedida de nicho."""
        service = NichoService(db_session)
        
        # Criar nicho
        nicho = service.create_nicho({
            "nome": "Nicho para Deletar",
            "descricao": "Será deletado",
            "ativo": True
        })
        
        nicho_id = nicho.id
        
        # Deletar nicho
        result = service.delete_nicho(nicho_id)
        
        assert result is True
        
        # Verificar se foi deletado
        deleted_nicho = service.get_nicho_by_id(nicho_id)
        assert deleted_nicho is None
    
    def test_get_nichos_with_filters(self, db_session):
        """Testa busca de nichos com filtros."""
        service = NichoService(db_session)
        
        # Criar múltiplos nichos
        nichos_data = [
            {"nome": "Marketing Digital", "descricao": "Marketing online", "ativo": True},
            {"nome": "Tecnologia", "descricao": "Tecnologia", "ativo": True},
            {"nome": "Saúde", "descricao": "Saúde", "ativo": False}
        ]
        
        for nicho_data in nichos_data:
            service.create_nicho(nicho_data)
        
        # Buscar apenas ativos
        active_nichos = service.get_nichos(filtros={"ativo": True})
        assert len(active_nichos) == 2
        
        # Buscar por nome
        marketing_nichos = service.get_nichos(filtros={"nome": "Marketing"})
        assert len(marketing_nichos) == 1
        assert marketing_nichos[0].nome == "Marketing Digital"
    
    def test_nicho_statistics(self, db_session):
        """Testa estatísticas de nichos."""
        service = NichoService(db_session)
        
        # Criar nichos com diferentes status
        nichos_data = [
            {"nome": "Nicho 1", "descricao": "Desc 1", "ativo": True},
            {"nome": "Nicho 2", "descricao": "Desc 2", "ativo": True},
            {"nome": "Nicho 3", "descricao": "Desc 3", "ativo": False}
        ]
        
        for nicho_data in nichos_data:
            service.create_nicho(nicho_data)
        
        stats = service.get_nicho_statistics()
        
        assert stats['total'] == 3
        assert stats['ativos'] == 2
        assert stats['inativos'] == 1

class TestCategoriaService:
    """Testes para o serviço de categorias."""
    
    def test_create_categoria_success(self, db_session):
        """Testa criação bem-sucedida de categoria."""
        service = CategoriaService(db_session)
        
        categoria_data = {
            "nome": "Nova Categoria",
            "descricao": "Descrição da nova categoria",
            "ativo": True
        }
        
        with patch('backend.app.services.categoria_service.validate_categoria_data') as mock_validate:
            mock_validate.return_value = True
            
            categoria = service.create_categoria(categoria_data)
            
            assert categoria is not None
            assert categoria.nome == "Nova Categoria"
            assert categoria.descricao == "Descrição da nova categoria"
    
    def test_get_categorias_by_nicho(self, db_session):
        """Testa busca de categorias por nicho."""
        service = CategoriaService(db_session)
        
        # Criar nicho e categorias
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        categorias_data = [
            {"nome": "SEO", "descricao": "Otimização SEO"},
            {"nome": "PPC", "descricao": "Publicidade paga"}
        ]
        
        for cat_data in categorias_data:
            service.create_categoria(cat_data)
        
        # Buscar categorias do nicho
        nicho_categorias = service.get_categorias_by_nicho(nicho.id)
        assert len(nicho_categorias) == 2
    
    def test_update_categoria_success(self, db_session):
        """Testa atualização bem-sucedida de categoria."""
        service = CategoriaService(db_session)
        
        # Criar categoria
        categoria = service.create_categoria({
            "nome": "Categoria Original",
            "descricao": "Descrição original",
            "ativo": True
        })
        
        # Atualizar
        update_data = {
            "nome": "Categoria Atualizada",
            "descricao": "Descrição atualizada"
        }
        
        with patch('backend.app.services.categoria_service.validate_categoria_data') as mock_validate:
            mock_validate.return_value = True
            
            updated_categoria = service.update_categoria(categoria.id, update_data)
            
            assert updated_categoria.nome == "Categoria Atualizada"
            assert updated_categoria.descricao == "Descrição atualizada"

class TestExecucaoService:
    """Testes para o serviço de execuções."""
    
    def test_create_execucao_success(self, db_session):
        """Testa criação bem-sucedida de execução."""
        service = ExecucaoService(db_session)
        
        # Criar nicho primeiro
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao_data = {
            "nicho_id": nicho.id,
            "total_keywords": 100,
            "configuracao": {
                "max_concurrent": 5,
                "timeout": 30
            }
        }
        
        execucao = service.create_execucao(execucao_data)
        
        assert execucao is not None
        assert execucao.nicho_id == nicho.id
        assert execucao.total_keywords == 100
        assert execucao.status == "em_execucao"
        assert execucao.data_inicio is not None
    
    def test_update_execucao_status(self, db_session):
        """Testa atualização de status de execução."""
        service = ExecucaoService(db_session)
        
        # Criar execução
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao = service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Atualizar status
        service.update_execucao_status(execucao.id, "concluido", {
            "keywords_processadas": 100,
            "keywords_validas": 95,
            "data_fim": datetime.utcnow()
        })
        
        updated_execucao = service.get_execucao_by_id(execucao.id)
        assert updated_execucao.status == "concluido"
        assert updated_execucao.keywords_processadas == 100
        assert updated_execucao.keywords_validas == 95
    
    def test_get_execucao_progress(self, db_session):
        """Testa cálculo de progresso de execução."""
        service = ExecucaoService(db_session)
        
        # Criar execução
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao = service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Atualizar progresso
        service.update_execucao_status(execucao.id, "em_execucao", {
            "keywords_processadas": 50,
            "keywords_validas": 45
        })
        
        progress = service.get_execucao_progress(execucao.id)
        
        assert progress['progresso'] == 50.0
        assert progress['taxa_sucesso'] == 90.0
        assert progress['keywords_processadas'] == 50
        assert progress['total_keywords'] == 100
    
    def test_cancel_execucao(self, db_session):
        """Testa cancelamento de execução."""
        service = ExecucaoService(db_session)
        
        # Criar execução
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao = service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Cancelar execução
        result = service.cancel_execucao(execucao.id)
        
        assert result is True
        
        cancelled_execucao = service.get_execucao_by_id(execucao.id)
        assert cancelled_execucao.status == "cancelado"
        assert cancelled_execucao.data_fim is not None
    
    def test_get_execucao_history(self, db_session):
        """Testa histórico de execuções."""
        service = ExecucaoService(db_session)
        
        # Criar múltiplas execuções
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucoes_data = [
            {"nicho_id": nicho.id, "total_keywords": 100},
            {"nicho_id": nicho.id, "total_keywords": 200},
            {"nicho_id": nicho.id, "total_keywords": 150}
        ]
        
        for exec_data in execucoes_data:
            service.create_execucao(exec_data)
        
        # Buscar histórico
        history = service.get_execucao_history(nicho.id)
        assert len(history) == 3

class TestKeywordService:
    """Testes para o serviço de keywords."""
    
    def test_create_keyword_success(self, db_session):
        """Testa criação bem-sucedida de keyword."""
        service = KeywordService(db_session)
        
        # Criar nicho primeiro
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_data = {
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "cpc": 2.50,
            "nicho_id": nicho.id
        }
        
        keyword = service.create_keyword(keyword_data)
        
        assert keyword is not None
        assert keyword.palavra == "marketing digital"
        assert keyword.volume == 1000
        assert keyword.competicao == "baixa"
        assert keyword.cpc == 2.50
        assert keyword.nicho_id == nicho.id
    
    def test_search_keywords(self, db_session):
        """Testa busca de keywords."""
        service = KeywordService(db_session)
        
        # Criar nicho e keywords
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keywords_data = [
            {"palavra": "marketing digital", "volume": 1000, "competicao": "baixa", "nicho_id": nicho.id},
            {"palavra": "seo marketing", "volume": 800, "competicao": "média", "nicho_id": nicho.id},
            {"palavra": "email marketing", "volume": 600, "competicao": "alta", "nicho_id": nicho.id}
        ]
        
        for kw_data in keywords_data:
            service.create_keyword(kw_data)
        
        # Buscar por palavra
        search_results = service.search_keywords("marketing")
        assert len(search_results) == 3
        
        # Buscar por volume mínimo
        high_volume_results = service.search_keywords("", min_volume=800)
        assert len(high_volume_results) == 2
        
        # Buscar por competição
        low_competition_results = service.search_keywords("", competicao="baixa")
        assert len(low_competition_results) == 1
    
    def test_update_keyword_metrics(self, db_session):
        """Testa atualização de métricas de keyword."""
        service = KeywordService(db_session)
        
        # Criar keyword
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword = service.create_keyword({
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "nicho_id": nicho.id
        })
        
        # Atualizar métricas
        new_metrics = {
            "volume": 1200,
            "competicao": "média",
            "cpc": 2.80
        }
        
        service.update_keyword_metrics(keyword.id, new_metrics)
        
        updated_keyword = service.get_keyword_by_id(keyword.id)
        assert updated_keyword.volume == 1200
        assert updated_keyword.competicao == "média"
        assert updated_keyword.cpc == 2.80
    
    def test_get_keyword_analytics(self, db_session):
        """Testa analytics de keyword."""
        service = KeywordService(db_session)
        
        # Criar keyword com histórico
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword = service.create_keyword({
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "nicho_id": nicho.id
        })
        
        # Simular histórico de métricas
        with patch('backend.app.services.keyword_service.get_keyword_history') as mock_history:
            mock_history.return_value = [
                {"volume": 1000, "competicao": "baixa", "cpc": 2.50, "data": "2024-01-01"},
                {"volume": 1100, "competicao": "baixa", "cpc": 2.60, "data": "2024-01-02"},
                {"volume": 1200, "competicao": "média", "cpc": 2.70, "data": "2024-01-03"}
            ]
            
            analytics = service.get_keyword_analytics(keyword.id)
            
            assert 'volume_trend' in analytics
            assert 'competition_trend' in analytics
            assert 'cpc_trend' in analytics
            assert len(analytics['volume_trend']) == 3

class TestProcessamentoService:
    """Testes para o serviço de processamento."""
    
    def test_process_keyword_success(self, db_session):
        """Testa processamento bem-sucedido de keyword."""
        service = ProcessamentoService(db_session)
        
        # Criar keyword
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_service = KeywordService(db_session)
        keyword = keyword_service.create_keyword({
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "nicho_id": nicho.id
        })
        
        # Mock das APIs externas
        with patch('backend.app.services.processamento_service.GoogleSearchConsole') as mock_gsc:
            mock_gsc.return_value.get_keyword_data.return_value = {
                "volume": 1000,
                "competition": "low",
                "cpc": 2.50
            }
            
            with patch('backend.app.services.processamento_service.OpenAI') as mock_openai:
                mock_openai.return_value.generate_content.return_value = {
                    "content": "Conteúdo sobre marketing digital",
                    "quality": 0.85
                }
                
                result = service.process_keyword(keyword.id)
                
                assert result is not None
                assert result['status'] == "sucesso"
                assert result['conteudo_gerado'] == "Conteúdo sobre marketing digital"
                assert result['qualidade'] == 0.85
    
    def test_process_keyword_api_error(self, db_session):
        """Testa processamento com erro de API."""
        service = ProcessamentoService(db_session)
        
        # Criar keyword
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_service = KeywordService(db_session)
        keyword = keyword_service.create_keyword({
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "nicho_id": nicho.id
        })
        
        # Simular erro de API
        with patch('backend.app.services.processamento_service.GoogleSearchConsole') as mock_gsc:
            mock_gsc.return_value.get_keyword_data.side_effect = Exception("API Error")
            
            result = service.process_keyword(keyword.id)
            
            assert result['status'] == "erro"
            assert 'error' in result
    
    def test_batch_process_keywords(self, db_session):
        """Testa processamento em lote de keywords."""
        service = ProcessamentoService(db_session)
        
        # Criar múltiplas keywords
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_service = KeywordService(db_session)
        keywords = []
        for i in range(5):
            keyword = keyword_service.create_keyword({
                "palavra": f"keyword {i}",
                "volume": 1000,
                "competicao": "baixa",
                "nicho_id": nicho.id
            })
            keywords.append(keyword)
        
        # Mock do processamento
        with patch.object(service, 'process_keyword') as mock_process:
            mock_process.return_value = {
                "status": "sucesso",
                "conteudo_gerado": "Conteúdo teste",
                "qualidade": 0.80
            }
            
            results = service.batch_process_keywords([kw.id for kw in keywords])
            
            assert len(results) == 5
            assert all(r['status'] == "sucesso" for r in results)
    
    def test_validate_processing_result(self, db_session):
        """Testa validação de resultado de processamento."""
        service = ProcessamentoService(db_session)
        
        # Teste com resultado válido
        valid_result = {
            "conteudo_gerado": "Conteúdo válido com pelo menos 100 caracteres para passar na validação de qualidade",
            "qualidade": 0.85,
            "tempo_processamento": 2.5
        }
        
        is_valid = service.validate_processing_result(valid_result)
        assert is_valid is True
        
        # Teste com resultado inválido (conteúdo muito curto)
        invalid_result = {
            "conteudo_gerado": "Muito curto",
            "qualidade": 0.85,
            "tempo_processamento": 2.5
        }
        
        is_valid = service.validate_processing_result(invalid_result)
        assert is_valid is False
        
        # Teste com qualidade baixa
        low_quality_result = {
            "conteudo_gerado": "Conteúdo válido com pelo menos 100 caracteres para passar na validação de qualidade",
            "qualidade": 0.30,  # Abaixo do threshold
            "tempo_processamento": 2.5
        }
        
        is_valid = service.validate_processing_result(low_quality_result)
        assert is_valid is False

class TestAnalyticsService:
    """Testes para o serviço de analytics."""
    
    def test_generate_execucao_report(self, db_session):
        """Testa geração de relatório de execução."""
        service = AnalyticsService(db_session)
        
        # Criar execução com dados
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao_service = ExecucaoService(db_session)
        execucao = execucao_service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Atualizar status para concluído
        execucao_service.update_execucao_status(execucao.id, "concluido", {
            "keywords_processadas": 95,
            "keywords_validas": 90,
            "data_fim": datetime.utcnow()
        })
        
        # Gerar relatório
        report = service.generate_execucao_report(execucao.id)
        
        assert report is not None
        assert report['execucao_id'] == execucao.id
        assert report['total_keywords'] == 100
        assert report['keywords_processadas'] == 95
        assert report['keywords_validas'] == 90
        assert report['qualidade_media'] == 0.90
    
    def test_generate_nicho_report(self, db_session):
        """Testa geração de relatório de nicho."""
        service = AnalyticsService(db_session)
        
        # Criar nicho com execuções
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        execucao_service = ExecucaoService(db_session)
        for i in range(3):
            execucao = execucao_service.create_execucao({
                "nicho_id": nicho.id,
                "total_keywords": 100
            })
            
            # Marcar como concluído
            execucao_service.update_execucao_status(execucao.id, "concluido", {
                "keywords_processadas": 95,
                "keywords_validas": 90,
                "data_fim": datetime.utcnow()
            })
        
        # Gerar relatório do nicho
        report = service.generate_nicho_report(nicho.id)
        
        assert report is not None
        assert report['nicho_id'] == nicho.id
        assert report['total_keywords'] == 300
        assert report['execucoes_count'] == 3
        assert report['qualidade_media'] == 0.90
    
    def test_calculate_keyword_metrics(self, db_session):
        """Testa cálculo de métricas de keywords."""
        service = AnalyticsService(db_session)
        
        # Criar keywords com diferentes métricas
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_service = KeywordService(db_session)
        keywords_data = [
            {"palavra": "kw1", "volume": 1000, "competicao": "baixa", "cpc": 2.50, "nicho_id": nicho.id},
            {"palavra": "kw2", "volume": 800, "competicao": "média", "cpc": 3.00, "nicho_id": nicho.id},
            {"palavra": "kw3", "volume": 1200, "competicao": "alta", "cpc": 4.50, "nicho_id": nicho.id}
        ]
        
        for kw_data in keywords_data:
            keyword_service.create_keyword(kw_data)
        
        # Calcular métricas
        metrics = service.calculate_keyword_metrics(nicho.id)
        
        assert metrics['total_keywords'] == 3
        assert metrics['volume_medio'] == 1000
        assert metrics['cpc_medio'] == 3.33
        assert metrics['distribuicao_competicao']['baixa'] == 1
        assert metrics['distribuicao_competicao']['média'] == 1
        assert metrics['distribuicao_competicao']['alta'] == 1
    
    def test_export_report_csv(self, db_session):
        """Testa exportação de relatório em CSV."""
        service = AnalyticsService(db_session)
        
        # Criar dados de teste
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        keyword_service = KeywordService(db_session)
        keywords_data = [
            {"palavra": "marketing digital", "volume": 1000, "competicao": "baixa", "cpc": 2.50, "nicho_id": nicho.id},
            {"palavra": "seo marketing", "volume": 800, "competicao": "média", "cpc": 3.00, "nicho_id": nicho.id}
        ]
        
        for kw_data in keywords_data:
            keyword_service.create_keyword(kw_data)
        
        # Exportar CSV
        csv_data = service.export_report_csv(nicho.id)
        
        assert csv_data is not None
        assert 'keyword' in csv_data
        assert 'volume' in csv_data
        assert 'competicao' in csv_data
        assert 'cpc' in csv_data
        assert 'marketing digital' in csv_data
        assert 'seo marketing' in csv_data
    
    def test_export_report_pdf(self, db_session):
        """Testa exportação de relatório em PDF."""
        service = AnalyticsService(db_session)
        
        # Criar dados de teste
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Nicho Teste",
            "descricao": "Descrição teste",
            "ativo": True
        })
        
        # Mock da geração de PDF
        with patch('backend.app.services.analytics_service.generate_pdf') as mock_pdf:
            mock_pdf.return_value = b"%PDF-1.4\n%Test PDF content"
            
            pdf_data = service.export_report_pdf(nicho.id)
            
            assert pdf_data is not None
            assert pdf_data.startswith(b"%PDF-1.4")

class TestServiceIntegration:
    """Testes de integração entre serviços."""
    
    def test_nicho_categoria_integration(self, db_session):
        """Testa integração entre serviços de nicho e categoria."""
        nicho_service = NichoService(db_session)
        categoria_service = CategoriaService(db_session)
        
        # Criar nicho
        nicho = nicho_service.create_nicho({
            "nome": "Marketing Digital",
            "descricao": "Estratégias de marketing online",
            "ativo": True
        })
        
        # Criar categoria
        categoria = categoria_service.create_categoria({
            "nome": "SEO",
            "descricao": "Otimização para motores de busca",
            "ativo": True
        })
        
        # Associar categoria ao nicho
        nicho_service.add_categoria_to_nicho(nicho.id, categoria.id)
        
        # Verificar associação
        nicho_categorias = categoria_service.get_categorias_by_nicho(nicho.id)
        assert len(nicho_categorias) == 1
        assert nicho_categorias[0].nome == "SEO"
    
    def test_execucao_keyword_integration(self, db_session):
        """Testa integração entre serviços de execução e keyword."""
        nicho_service = NichoService(db_session)
        execucao_service = ExecucaoService(db_session)
        keyword_service = KeywordService(db_session)
        
        # Criar nicho
        nicho = nicho_service.create_nicho({
            "nome": "Marketing Digital",
            "descricao": "Estratégias de marketing online",
            "ativo": True
        })
        
        # Criar execução
        execucao = execucao_service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Criar keywords para a execução
        keywords_data = [
            {"palavra": "marketing digital", "volume": 1000, "competicao": "baixa", "nicho_id": nicho.id},
            {"palavra": "seo marketing", "volume": 800, "competicao": "média", "nicho_id": nicho.id}
        ]
        
        for kw_data in keywords_data:
            keyword_service.create_keyword(kw_data)
        
        # Verificar integração
        execucao_keywords = keyword_service.get_keywords_by_execucao(execucao.id)
        assert len(execucao_keywords) == 2
    
    def test_full_workflow_integration(self, db_session):
        """Testa workflow completo de criação e processamento."""
        # Criar nicho
        nicho_service = NichoService(db_session)
        nicho = nicho_service.create_nicho({
            "nome": "Marketing Digital",
            "descricao": "Estratégias de marketing online",
            "ativo": True
        })
        
        # Criar execução
        execucao_service = ExecucaoService(db_session)
        execucao = execucao_service.create_execucao({
            "nicho_id": nicho.id,
            "total_keywords": 100
        })
        
        # Criar keyword
        keyword_service = KeywordService(db_session)
        keyword = keyword_service.create_keyword({
            "palavra": "marketing digital",
            "volume": 1000,
            "competicao": "baixa",
            "nicho_id": nicho.id
        })
        
        # Processar keyword
        processamento_service = ProcessamentoService(db_session)
        
        with patch.object(processamento_service, 'process_keyword') as mock_process:
            mock_process.return_value = {
                "status": "sucesso",
                "conteudo_gerado": "Conteúdo sobre marketing digital",
                "qualidade": 0.85
            }
            
            result = processamento_service.process_keyword(keyword.id)
            
            # Verificar resultado
            assert result['status'] == "sucesso"
            
            # Atualizar execução
            execucao_service.update_execucao_status(execucao.id, "em_execucao", {
                "keywords_processadas": 1,
                "keywords_validas": 1
            })
            
            # Verificar progresso
            progress = execucao_service.get_execucao_progress(execucao.id)
            assert progress['progresso'] == 1.0
            assert progress['taxa_sucesso'] == 100.0
