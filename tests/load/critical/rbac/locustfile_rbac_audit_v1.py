"""
Teste de Carga - RBAC Auditoria
Endpoint: /api/audit/logs (GET)
Baseado em: backend/app/api/auditoria.py linha 40-200
Tracing ID: RBAC_AUDIT_LOAD_TEST_20250127_001
Data: 2025-01-27
"""

from locust import HttpUser, task, between
import json
import logging
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RBACAuditLoadTest(HttpUser):
    """
    Teste de carga para endpoint de auditoria
    Baseado no código real: backend/app/api/auditoria.py
    """
    
    wait_time = between(2, 4)  # Intervalo para operações de auditoria
    
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
    def consultar_logs_basico(self):
        """
        Teste básico de consulta de logs de auditoria
        Baseado em: backend/app/api/auditoria.py linha 40-200
        """
        try:
            response = self.client.get(
                "/api/audit/logs",
                headers=self.headers,
                name="Audit - Consultar Logs (Básico)"
            )
            
            # Validações baseadas no código real
            if response.status_code == 200:
                logs = response.json()
                # Validar estrutura da resposta baseada no código
                for log in logs:
                    assert "timestamp" in log, "Campo 'timestamp' ausente na resposta"
                    assert "event_type" in log, "Campo 'event_type' ausente na resposta"
                    assert "message" in log, "Campo 'message' ausente na resposta"
                    assert "user_id" in log, "Campo 'user_id' ausente na resposta"
                
                logger.info(f"Consulta de logs bem-sucedida: {len(logs)} logs")
                
            elif response.status_code == 401:
                logger.warning("Acesso não autorizado - token pode ter expirado")
                self.on_start()
                
            elif response.status_code == 403:
                logger.warning("Acesso negado - usuário sem permissão audit:read")
                
            else:
                logger.error(f"Erro inesperado: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante consulta de logs: {str(e)}")

    @task(2)
    def consultar_logs_com_filtros(self):
        """
        Teste de consulta com filtros
        Baseado em: backend/app/api/auditoria.py linha 40-200
        """
        try:
            # Filtros baseados em dados reais do sistema
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            filtros = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "event_types": "login,logout,data_access",
                "severities": "info,warning,error",
                "limit": 50
            }
            
            response = self.client.get(
                "/api/audit/logs",
                headers=self.headers,
                params=filtros,
                name="Audit - Consultar Logs (Com Filtros)"
            )
            
            if response.status_code == 200:
                logs = response.json()
                logger.info(f"Consulta com filtros bem-sucedida: {len(logs)} logs")
                
            elif response.status_code == 400:
                logger.warning(f"Filtros inválidos: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante consulta com filtros: {str(e)}")

    @task(2)
    def consultar_estatisticas(self):
        """
        Teste de consulta de estatísticas
        Baseado em: backend/app/api/auditoria.py linha 201-224
        """
        try:
            # Período baseado em dados reais
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = self.client.get(
                "/api/audit/statistics",
                headers=self.headers,
                params=params,
                name="Audit - Consultar Estatísticas"
            )
            
            if response.status_code == 200:
                stats = response.json()
                # Validar estrutura das estatísticas
                assert "total_events" in stats, "Campo 'total_events' ausente"
                assert "events_by_type" in stats, "Campo 'events_by_type' ausente"
                assert "events_by_severity" in stats, "Campo 'events_by_severity' ausente"
                
                logger.info(f"Estatísticas obtidas com sucesso: {stats['total_events']} eventos")
                
            elif response.status_code == 400:
                logger.warning(f"Período inválido: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante consulta de estatísticas: {str(e)}")

    @task(1)
    def gerar_relatorio(self):
        """
        Teste de geração de relatório
        Baseado em: backend/app/api/auditoria.py linha 225-281
        """
        try:
            # Dados baseados em relatórios reais do sistema
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            relatorio_data = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "filters": {
                    "event_types": ["login", "logout", "data_access"],
                    "severities": ["info", "warning", "error"]
                }
            }
            
            response = self.client.post(
                "/api/audit/reports",
                headers=self.headers,
                json=relatorio_data,
                name="Audit - Gerar Relatório"
            )
            
            if response.status_code == 200:
                relatorio = response.json()
                assert "report_id" in relatorio, "ID do relatório não retornado"
                assert "status" in relatorio, "Status do relatório não retornado"
                
                logger.info(f"Relatório gerado com sucesso: {relatorio['report_id']}")
                
            elif response.status_code == 400:
                logger.warning(f"Dados inválidos para relatório: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante geração de relatório: {str(e)}")

    @task(1)
    def exportar_logs(self):
        """
        Teste de exportação de logs
        Baseado em: backend/app/api/auditoria.py linha 282-344
        """
        try:
            # Configuração de exportação baseada no código real
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            export_config = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": "json",
                "filters": {
                    "event_types": ["login", "logout"],
                    "severities": ["info", "warning"]
                }
            }
            
            response = self.client.post(
                "/api/audit/export",
                headers=self.headers,
                json=export_config,
                name="Audit - Exportar Logs"
            )
            
            if response.status_code == 200:
                export_result = response.json()
                assert "export_id" in export_result, "ID da exportação não retornado"
                assert "status" in export_result, "Status da exportação não retornado"
                
                logger.info(f"Exportação iniciada com sucesso: {export_result['export_id']}")
                
            elif response.status_code == 400:
                logger.warning(f"Configuração inválida para exportação: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro durante exportação: {str(e)}")

    def on_stop(self):
        """Cleanup ao finalizar"""
        logger.info("Teste de carga RBAC Auditoria finalizado") 