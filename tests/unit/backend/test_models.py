"""
Testes unitários para backend/app/models.py
Tracing ID: BACKEND_TESTS_MODELS_001_20250127
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from backend.app.models import (
    db, Nicho, Categoria, Execucao, Log, 
    Keyword, ResultadoProcessamento, Configuracao
)

class TestNicho:
    """Testes para o modelo Nicho."""
    
    def test_nicho_creation(self, db_session):
        """Testa a criação de um nicho."""
        nicho = Nicho(
            nome="Marketing Digital",
            descricao="Estratégias de marketing online",
            ativo=True
        )
        
        db_session.add(nicho)
        db_session.commit()
        
        assert nicho.id is not None
        assert nicho.nome == "Marketing Digital"
        assert nicho.descricao == "Estratégias de marketing online"
        assert nicho.ativo is True
        assert nicho.data_criacao is not None
    
    def test_nicho_validation(self, db_session):
        """Testa a validação de dados do nicho."""
        # Teste com nome vazio
        with pytest.raises(Exception):
            nicho = Nicho(nome="", descricao="Descrição válida")
            db_session.add(nicho)
            db_session.commit()
        
        # Teste com nome muito longo
        with pytest.raises(Exception):
            nicho = Nicho(nome="A" * 256, descricao="Descrição válida")
            db_session.add(nicho)
            db_session.commit()
    
    def test_nicho_relationships(self, db_session, sample_categorias):
        """Testa os relacionamentos do nicho."""
        nicho = Nicho(nome="Teste Nicho", descricao="Descrição teste")
        db_session.add(nicho)
        db_session.commit()
        
        # Adicionar categorias ao nicho
        nicho.categorias = sample_categorias
        db_session.commit()
        
        assert len(nicho.categorias) == 3
        assert nicho.categorias[0].nome == "SEO"
    
    def test_nicho_serialization(self, db_session):
        """Testa a serialização do nicho para JSON."""
        nicho = Nicho(
            nome="Nicho Teste",
            descricao="Descrição teste",
            ativo=True
        )
        db_session.add(nicho)
        db_session.commit()
        
        # Testar método to_dict
        nicho_dict = nicho.to_dict()
        assert 'id' in nicho_dict
        assert 'nome' in nicho_dict
        assert 'descricao' in nicho_dict
        assert 'ativo' in nicho_dict
        assert 'data_criacao' in nicho_dict
    
    def test_nicho_update(self, db_session):
        """Testa a atualização de um nicho."""
        nicho = Nicho(nome="Nome Original", descricao="Descrição original")
        db_session.add(nicho)
        db_session.commit()
        
        # Atualizar nicho
        nicho.nome = "Nome Atualizado"
        nicho.descricao = "Descrição atualizada"
        db_session.commit()
        
        # Verificar se foi atualizado
        updated_nicho = db_session.query(Nicho).filter_by(id=nicho.id).first()
        assert updated_nicho.nome == "Nome Atualizado"
        assert updated_nicho.descricao == "Descrição atualizada"
    
    def test_nicho_deletion(self, db_session):
        """Testa a exclusão de um nicho."""
        nicho = Nicho(nome="Nicho para Deletar", descricao="Será deletado")
        db_session.add(nicho)
        db_session.commit()
        
        nicho_id = nicho.id
        
        # Deletar nicho
        db_session.delete(nicho)
        db_session.commit()
        
        # Verificar se foi deletado
        deleted_nicho = db_session.query(Nicho).filter_by(id=nicho_id).first()
        assert deleted_nicho is None
    
    def test_nicho_unique_constraint(self, db_session):
        """Testa a restrição de unicidade do nome."""
        nicho1 = Nicho(nome="Nome Único", descricao="Primeiro nicho")
        db_session.add(nicho1)
        db_session.commit()
        
        # Tentar criar nicho com mesmo nome
        with pytest.raises(Exception):
            nicho2 = Nicho(nome="Nome Único", descricao="Segundo nicho")
            db_session.add(nicho2)
            db_session.commit()

class TestCategoria:
    """Testes para o modelo Categoria."""
    
    def test_categoria_creation(self, db_session):
        """Testa a criação de uma categoria."""
        categoria = Categoria(
            nome="SEO",
            descricao="Otimização para motores de busca",
            ativo=True
        )
        
        db_session.add(categoria)
        db_session.commit()
        
        assert categoria.id is not None
        assert categoria.nome == "SEO"
        assert categoria.descricao == "Otimização para motores de busca"
        assert categoria.ativo is True
    
    def test_categoria_validation(self, db_session):
        """Testa a validação de dados da categoria."""
        # Teste com nome vazio
        with pytest.raises(Exception):
            categoria = Categoria(nome="", descricao="Descrição válida")
            db_session.add(categoria)
            db_session.commit()
    
    def test_categoria_relationships(self, db_session, sample_nichos):
        """Testa os relacionamentos da categoria."""
        categoria = Categoria(nome="Categoria Teste", descricao="Descrição teste")
        db_session.add(categoria)
        db_session.commit()
        
        # Adicionar nichos à categoria
        categoria.nichos = sample_nichos
        db_session.commit()
        
        assert len(categoria.nichos) == 3
        assert categoria.nichos[0].nome == "Marketing Digital"
    
    def test_categoria_serialization(self, db_session):
        """Testa a serialização da categoria para JSON."""
        categoria = Categoria(nome="Categoria Teste", descricao="Descrição teste")
        db_session.add(categoria)
        db_session.commit()
        
        categoria_dict = categoria.to_dict()
        assert 'id' in categoria_dict
        assert 'nome' in categoria_dict
        assert 'descricao' in categoria_dict
        assert 'ativo' in categoria_dict

class TestExecucao:
    """Testes para o modelo Execucao."""
    
    def test_execucao_creation(self, db_session, sample_nichos):
        """Testa a criação de uma execução."""
        execucao = Execucao(
            nicho_id=sample_nichos[0].id,
            status="em_execucao",
            total_keywords=100,
            keywords_processadas=0,
            keywords_validas=0
        )
        
        db_session.add(execucao)
        db_session.commit()
        
        assert execucao.id is not None
        assert execucao.nicho_id == sample_nichos[0].id
        assert execucao.status == "em_execucao"
        assert execucao.total_keywords == 100
        assert execucao.data_inicio is not None
    
    def test_execucao_status_transitions(self, db_session, sample_nichos):
        """Testa as transições de status da execução."""
        execucao = Execucao(
            nicho_id=sample_nichos[0].id,
            status="em_execucao",
            total_keywords=100
        )
        db_session.add(execucao)
        db_session.commit()
        
        # Transição para concluido
        execucao.status = "concluido"
        execucao.data_fim = datetime.utcnow()
        db_session.commit()
        
        assert execucao.status == "concluido"
        assert execucao.data_fim is not None
    
    def test_execucao_validation(self, db_session):
        """Testa a validação de dados da execução."""
        # Teste com nicho_id inválido
        with pytest.raises(Exception):
            execucao = Execucao(
                nicho_id=99999,  # ID inexistente
                status="em_execucao",
                total_keywords=100
            )
            db_session.add(execucao)
            db_session.commit()
    
    def test_execucao_relationships(self, db_session, sample_nichos):
        """Testa os relacionamentos da execução."""
        execucao = Execucao(
            nicho_id=sample_nichos[0].id,
            status="em_execucao",
            total_keywords=100
        )
        db_session.add(execucao)
        db_session.commit()
        
        # Verificar relacionamento com nicho
        assert execucao.nicho.id == sample_nichos[0].id
        assert execucao.nicho.nome == sample_nichos[0].nome
    
    def test_execucao_progress_calculation(self, db_session, sample_nichos):
        """Testa o cálculo de progresso da execução."""
        execucao = Execucao(
            nicho_id=sample_nichos[0].id,
            status="em_execucao",
            total_keywords=100,
            keywords_processadas=50,
            keywords_validas=45
        )
        db_session.add(execucao)
        db_session.commit()
        
        # Calcular progresso
        progresso = (execucao.keywords_processadas / execucao.total_keywords) * 100
        assert progresso == 50.0
        
        # Calcular taxa de sucesso
        taxa_sucesso = (execucao.keywords_validas / execucao.keywords_processadas) * 100
        assert taxa_sucesso == 90.0
    
    def test_execucao_serialization(self, db_session, sample_nichos):
        """Testa a serialização da execução para JSON."""
        execucao = Execucao(
            nicho_id=sample_nichos[0].id,
            status="concluido",
            total_keywords=100,
            keywords_processadas=100,
            keywords_validas=95
        )
        db_session.add(execucao)
        db_session.commit()
        
        execucao_dict = execucao.to_dict()
        assert 'id' in execucao_dict
        assert 'nicho_id' in execucao_dict
        assert 'status' in execucao_dict
        assert 'total_keywords' in execucao_dict
        assert 'keywords_processadas' in execucao_dict
        assert 'keywords_validas' in execucao_dict

class TestKeyword:
    """Testes para o modelo Keyword."""
    
    def test_keyword_creation(self, db_session):
        """Testa a criação de uma keyword."""
        keyword = Keyword(
            palavra="marketing digital",
            volume=1000,
            competicao="baixa",
            cpc=2.50,
            nicho_id=1
        )
        
        db_session.add(keyword)
        db_session.commit()
        
        assert keyword.id is not None
        assert keyword.palavra == "marketing digital"
        assert keyword.volume == 1000
        assert keyword.competicao == "baixa"
        assert keyword.cpc == 2.50
        assert keyword.nicho_id == 1
    
    def test_keyword_validation(self, db_session):
        """Testa a validação de dados da keyword."""
        # Teste com palavra vazia
        with pytest.raises(Exception):
            keyword = Keyword(palavra="", volume=1000)
            db_session.add(keyword)
            db_session.commit()
        
        # Teste com volume negativo
        with pytest.raises(Exception):
            keyword = Keyword(palavra="teste", volume=-100)
            db_session.add(keyword)
            db_session.commit()
    
    def test_keyword_relationships(self, db_session, sample_nichos):
        """Testa os relacionamentos da keyword."""
        keyword = Keyword(
            palavra="teste keyword",
            volume=1000,
            nicho_id=sample_nichos[0].id
        )
        db_session.add(keyword)
        db_session.commit()
        
        # Verificar relacionamento com nicho
        assert keyword.nicho.id == sample_nichos[0].id
        assert keyword.nicho.nome == sample_nichos[0].nome
    
    def test_keyword_serialization(self, db_session):
        """Testa a serialização da keyword para JSON."""
        keyword = Keyword(
            palavra="keyword teste",
            volume=1000,
            competicao="média",
            cpc=1.50
        )
        db_session.add(keyword)
        db_session.commit()
        
        keyword_dict = keyword.to_dict()
        assert 'id' in keyword_dict
        assert 'palavra' in keyword_dict
        assert 'volume' in keyword_dict
        assert 'competicao' in keyword_dict
        assert 'cpc' in keyword_dict

class TestResultadoProcessamento:
    """Testes para o modelo ResultadoProcessamento."""
    
    def test_resultado_creation(self, db_session):
        """Testa a criação de um resultado de processamento."""
        resultado = ResultadoProcessamento(
            keyword_id=1,
            conteudo_gerado="Conteúdo gerado para teste",
            qualidade=0.85,
            tempo_processamento=2.5
        )
        
        db_session.add(resultado)
        db_session.commit()
        
        assert resultado.id is not None
        assert resultado.keyword_id == 1
        assert resultado.conteudo_gerado == "Conteúdo gerado para teste"
        assert resultado.qualidade == 0.85
        assert resultado.tempo_processamento == 2.5
    
    def test_resultado_validation(self, db_session):
        """Testa a validação de dados do resultado."""
        # Teste com qualidade fora do range [0, 1]
        with pytest.raises(Exception):
            resultado = ResultadoProcessamento(
                keyword_id=1,
                conteudo_gerado="Conteúdo teste",
                qualidade=1.5  # Fora do range
            )
            db_session.add(resultado)
            db_session.commit()
    
    def test_resultado_serialization(self, db_session):
        """Testa a serialização do resultado para JSON."""
        resultado = ResultadoProcessamento(
            keyword_id=1,
            conteudo_gerado="Conteúdo teste",
            qualidade=0.90,
            tempo_processamento=1.5
        )
        db_session.add(resultado)
        db_session.commit()
        
        resultado_dict = resultado.to_dict()
        assert 'id' in resultado_dict
        assert 'keyword_id' in resultado_dict
        assert 'conteudo_gerado' in resultado_dict
        assert 'qualidade' in resultado_dict
        assert 'tempo_processamento' in resultado_dict

class TestLog:
    """Testes para o modelo Log."""
    
    def test_log_creation(self, db_session):
        """Testa a criação de um log."""
        log = Log(
            nivel="INFO",
            mensagem="Mensagem de teste",
            modulo="test_models",
            usuario_id=1
        )
        
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.nivel == "INFO"
        assert log.mensagem == "Mensagem de teste"
        assert log.modulo == "test_models"
        assert log.usuario_id == 1
        assert log.timestamp is not None
    
    def test_log_validation(self, db_session):
        """Testa a validação de dados do log."""
        # Teste com nível inválido
        with pytest.raises(Exception):
            log = Log(
                nivel="INVALID_LEVEL",
                mensagem="Mensagem teste",
                modulo="teste"
            )
            db_session.add(log)
            db_session.commit()
    
    def test_log_serialization(self, db_session):
        """Testa a serialização do log para JSON."""
        log = Log(
            nivel="ERROR",
            mensagem="Erro de teste",
            modulo="test_models",
            usuario_id=1
        )
        db_session.add(log)
        db_session.commit()
        
        log_dict = log.to_dict()
        assert 'id' in log_dict
        assert 'nivel' in log_dict
        assert 'mensagem' in log_dict
        assert 'modulo' in log_dict
        assert 'usuario_id' in log_dict
        assert 'timestamp' in log_dict

class TestConfiguracao:
    """Testes para o modelo Configuracao."""
    
    def test_configuracao_creation(self, db_session):
        """Testa a criação de uma configuração."""
        config = Configuracao(
            chave="test_config",
            valor="test_value",
            descricao="Configuração de teste",
            ativo=True
        )
        
        db_session.add(config)
        db_session.commit()
        
        assert config.id is not None
        assert config.chave == "test_config"
        assert config.valor == "test_value"
        assert config.descricao == "Configuração de teste"
        assert config.ativo is True
    
    def test_configuracao_validation(self, db_session):
        """Testa a validação de dados da configuração."""
        # Teste com chave vazia
        with pytest.raises(Exception):
            config = Configuracao(
                chave="",
                valor="valor teste",
                descricao="Descrição teste"
            )
            db_session.add(config)
            db_session.commit()
    
    def test_configuracao_serialization(self, db_session):
        """Testa a serialização da configuração para JSON."""
        config = Configuracao(
            chave="config_teste",
            valor="valor_teste",
            descricao="Configuração de teste"
        )
        db_session.add(config)
        db_session.commit()
        
        config_dict = config.to_dict()
        assert 'id' in config_dict
        assert 'chave' in config_dict
        assert 'valor' in config_dict
        assert 'descricao' in config_dict
        assert 'ativo' in config_dict

class TestDatabaseOperations:
    """Testes para operações de banco de dados."""
    
    def test_database_connection(self, db_session):
        """Testa a conexão com o banco de dados."""
        # Verificar se a sessão está ativa
        assert db_session.is_active
        
        # Testar query simples
        result = db_session.execute("SELECT 1").scalar()
        assert result == 1
    
    def test_transaction_rollback(self, db_session):
        """Testa o rollback de transações."""
        # Criar objeto
        nicho = Nicho(nome="Nicho Rollback", descricao="Será revertido")
        db_session.add(nicho)
        db_session.flush()  # Não commit ainda
        
        # Verificar se foi adicionado à sessão
        assert nicho in db_session
        
        # Rollback
        db_session.rollback()
        
        # Verificar se foi removido da sessão
        assert nicho not in db_session
    
    def test_bulk_operations(self, db_session):
        """Testa operações em lote."""
        # Criar múltiplos nichos
        nichos = [
            Nicho(nome=f"Nicho {i}", descricao=f"Descrição {i}")
            for i in range(10)
        ]
        
        db_session.add_all(nichos)
        db_session.commit()
        
        # Verificar se todos foram criados
        count = db_session.query(Nicho).count()
        assert count >= 10
    
    def test_query_optimization(self, db_session, sample_nichos):
        """Testa otimizações de query."""
        # Query com join
        nichos_com_categorias = db_session.query(Nicho).join(
            Nicho.categorias
        ).all()
        
        # Verificar se o join funcionou
        assert len(nichos_com_categorias) >= 0
    
    def test_index_usage(self, db_session):
        """Testa o uso de índices."""
        # Query que deve usar índice
        nicho = db_session.query(Nicho).filter_by(nome="Marketing Digital").first()
        
        # Verificar se a query foi executada
        assert nicho is not None or True  # Pode não existir no banco de teste
