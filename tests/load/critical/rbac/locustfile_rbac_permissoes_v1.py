"""
Teste de Carga - RBAC Permissões
Endpoint: /api/rbac/permissoes (GET, POST, PUT, DELETE)
Baseado em: backend/app/api/rbac.py linha 731-876
Tracing ID: RBAC_PERMISSOES_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging
import random

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RBACPermissoesLoadTest(HttpUser):
    """
    Teste de carga para endpoint de permissões RBAC
    Baseado no código real: backend/app/api/rbac.py
    """
    
    wait_time = between(2, 5)  # Intervalo maior para operações críticas
    
    def on_start(self):
        """Setup inicial - autenticação"""
        # Dados reais baseados no sistema
        login_data = {
            "email": "admin@omnikeywords.com",
            "password": "admin_password_2025"
        }
        
        try:
            # Login para obter token
            response = self.client.post("/api/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                logger.info("Autenticação realizada com sucesso")
            else:
                logger.error(f"Falha na autenticação: {response.status_code}")
                self.token = None
                self.headers = {}
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            self.token = None
            self.headers = {}

    @task(4)
    def listar_permissoes(self):
        """
        Teste de listagem de permissões
        Baseado em: backend/app/api/rbac.py linha 731-742
        """
        try:
            response = self.client.get(
                "/api/rbac/permissoes",
                headers=self.headers,
                name="RBAC - Listar Permissões"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                permissoes = response.json()
                # Validar estrutura da resposta baseada no código
                for permissao in permissoes:
                    assert "id" in permissao, "Campo 'id' ausente na resposta"
                    assert "nome" in permissao, "Campo 'nome' ausente na resposta"
                    assert "descricao" in permissao, "Campo 'descricao' ausente na resposta"
                
                logger.info(f"Listagem de permissões bem-sucedida: {len(permissoes)} permissões")
                
            elif response.status_code == 401:
                logger.warning("Acesso não autorizado - token pode ter expirado")
                self.on_start()
                
            elif response.status_code == 403:
                logger.warning("Acesso negado - usuário sem permissão de admin/gestor")
                
            else:
                logger.error(f"Erro inesperado: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante listagem de permissões: {str(e)}")

    @task(2)
    def criar_permissao(self):
        """
        Teste de criação de permissão
        Baseado em: backend/app/api/rbac.py linha 743-787
        """
        try:
            # Dados baseados em permissões reais do sistema
            permissoes_teste = [
                {
                    "nome": "analytics_export",
                    "descricao": "Permissão para exportar dados de analytics"
                },
                {
                    "nome": "reports_generate",
                    "descricao": "Permissão para gerar relatórios"
                },
                {
                    "nome": "users_manage",
                    "descricao": "Permissão para gerenciar usuários"
                }
            ]
            
            # Selecionar permissão aleatória
            permissao_data = random.choice(permissoes_teste)
            
            response = self.client.post(
                "/api/rbac/permissoes",
                headers=self.headers,
                json=permissao_data,
                name="RBAC - Criar Permissão"
            )
            
            if response.status_code == 201:
                permissao_criada = response.json()
                assert "id" in permissao_criada, "ID não retornado na criação"
                assert permissao_criada["nome"] == permissao_data["nome"], "Nome não confere"
                logger.info(f"Permissão criada com sucesso: {permissao_criada['nome']}")
                
            elif response.status_code == 409:
                logger.info(f"Permissão já existe: {permissao_data['nome']}")
                
            elif response.status_code == 400:
                logger.warning(f"Dados inválidos para criação: {response.text}")
                
            else:
                logger.error(f"Erro na criação: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante criação de permissão: {str(e)}")

    @task(1)
    def editar_permissao(self):
        """
        Teste de edição de permissão
        Baseado em: backend/app/api/rbac.py linha 788-831
        """
        try:
            # Primeiro, listar permissões para obter um ID válido
            list_response = self.client.get("/api/rbac/permissoes", headers=self.headers)
            
            if list_response.status_code == 200:
                permissoes = list_response.json()
                if permissoes:
                    # Selecionar primeira permissão para edição
                    permissao_id = permissoes[0]["id"]
                    
                    # Dados de edição baseados no código real
                    dados_edicao = {
                        "descricao": "Descrição atualizada via teste de carga"
                    }
                    
                    response = self.client.put(
                        f"/api/rbac/permissoes/{permissao_id}",
                        headers=self.headers,
                        json=dados_edicao,
                        name="RBAC - Editar Permissão"
                    )
                    
                    if response.status_code == 200:
                        permissao_editada = response.json()
                        assert permissao_editada["descricao"] == dados_edicao["descricao"]
                        logger.info(f"Permissão editada com sucesso: {permissao_editada['nome']}")
                        
                    elif response.status_code == 404:
                        logger.warning(f"Permissão não encontrada: {permissao_id}")
                        
                    else:
                        logger.error(f"Erro na edição: {response.status_code} - {response.text}")
                        
        except Exception as e:
            logger.error(f"Erro durante edição de permissão: {str(e)}")

    @task(1)
    def remover_permissao(self):
        """
        Teste de remoção de permissão (apenas para permissões de teste)
        Baseado em: backend/app/api/rbac.py linha 832-876
        """
        try:
            # Primeiro, listar permissões para obter um ID válido
            list_response = self.client.get("/api/rbac/permissoes", headers=self.headers)
            
            if list_response.status_code == 200:
                permissoes = list_response.json()
                # Filtrar apenas permissões de teste (que podem ser removidas)
                permissoes_teste = [p for p in permissoes if p["nome"].startswith("test_")]
                
                if permissoes_teste:
                    # Selecionar primeira permissão de teste
                    permissao_id = permissoes_teste[0]["id"]
                    
                    response = self.client.delete(
                        f"/api/rbac/permissoes/{permissao_id}",
                        headers=self.headers,
                        name="RBAC - Remover Permissão"
                    )
                    
                    if response.status_code == 200:
                        resultado = response.json()
                        logger.info(f"Permissão removida com sucesso: {resultado['nome']}")
                        
                    elif response.status_code == 409:
                        logger.info("Permissão não pode ser removida devido a dependências")
                        
                    elif response.status_code == 404:
                        logger.warning(f"Permissão não encontrada: {permissao_id}")
                        
                    else:
                        logger.error(f"Erro na remoção: {response.status_code} - {response.text}")
                        
        except Exception as e:
            logger.error(f"Erro durante remoção de permissão: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga RBAC Permissões finalizado") 