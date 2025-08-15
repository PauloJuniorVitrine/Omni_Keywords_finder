"""
Teste de Carga - RBAC Usuários
Endpoint: /api/rbac/usuarios (GET)
Baseado em: backend/app/api/rbac.py linha 364-377
Tracing ID: RBAC_USUARIOS_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RBACUsuariosLoadTest(HttpUser):
    """
    Teste de carga para endpoint de listagem de usuários RBAC
    Baseado no código real: backend/app/api/rbac.py
    """
    
    wait_time = between(1, 3)  # Intervalo entre requisições
    
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

    @task(3)
    def listar_usuarios_basico(self):
        """
        Teste básico de listagem de usuários
        Baseado em: backend/app/api/rbac.py linha 364-377
        """
        try:
            response = self.client.get(
                "/api/rbac/usuarios",
                headers=self.headers,
                name="RBAC - Listar Usuários (Básico)"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                usuarios = response.json()
                # Validar estrutura da resposta baseada no código
                for usuario in usuarios:
                    assert "id" in usuario, "Campo 'id' ausente na resposta"
                    assert "username" in usuario, "Campo 'username' ausente na resposta"
                    assert "email" in usuario, "Campo 'email' ausente na resposta"
                    assert "ativo" in usuario, "Campo 'ativo' ausente na resposta"
                
                logger.info(f"Listagem de usuários bem-sucedida: {len(usuarios)} usuários")
                
            elif response.status_code == 401:
                logger.warning("Acesso não autorizado - token pode ter expirado")
                # Reautenticar se necessário
                self.on_start()
                
            elif response.status_code == 403:
                logger.warning("Acesso negado - usuário sem permissão de gestor/admin")
                
            else:
                logger.error(f"Erro inesperado: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante listagem de usuários: {str(e)}")

    @task(2)
    def listar_usuarios_com_filtros(self):
        """
        Teste de listagem com filtros
        Baseado em funcionalidades de filtro do sistema
        """
        try:
            # Filtros baseados em dados reais do sistema
            filtros = {
                "ativo": "true",
                "role": "gestor"
            }
            
            response = self.client.get(
                "/api/rbac/usuarios",
                headers=self.headers,
                params=filtros,
                name="RBAC - Listar Usuários (Com Filtros)"
            )
            
            if response.status_code == 200:
                usuarios = response.json()
                logger.info(f"Listagem com filtros bem-sucedida: {len(usuarios)} usuários")
                
        except Exception as e:
            logger.error(f"Erro durante listagem com filtros: {str(e)}")

    @task(1)
    def listar_usuarios_paginacao(self):
        """
        Teste de paginação
        Baseado em padrões de paginação do sistema
        """
        try:
            # Parâmetros de paginação
            params = {
                "page": 1,
                "per_page": 10
            }
            
            response = self.client.get(
                "/api/rbac/usuarios",
                headers=self.headers,
                params=params,
                name="RBAC - Listar Usuários (Paginação)"
            )
            
            if response.status_code == 200:
                usuarios = response.json()
                logger.info(f"Paginação bem-sucedida: {len(usuarios)} usuários na página")
                
        except Exception as e:
            logger.error(f"Erro durante paginação: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga RBAC Usuários finalizado") 