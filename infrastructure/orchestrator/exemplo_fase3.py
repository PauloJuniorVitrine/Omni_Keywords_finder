"""
Exemplo de Uso - Fase 3: Integração e Qualidade

Demonstra como usar os novos módulos da Fase 3:
- Integration: Conecta com sistema existente
- Notifications: Sistema de alertas e progresso
- Metrics: Coleta de métricas e performance
- Validation: Validação de dados

Tracing ID: EXEMPLO_FASE3_001_20241227
Versão: 1.0
Autor: IA-Cursor
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime

from .fluxo_completo_orchestrator import FluxoCompletoOrchestrator
from .integration import SystemIntegration, IntegrationConfig
from .notifications import NotificationManager, NotificationConfig, NotificationType
from .metrics import MetricsCollector, MetricConfig, MetricType
from .validation import DataValidator, ValidationConfig, ValidationResult

logger = logging.getLogger(__name__)


class FluxoCompletoComIntegracao:
    """Exemplo de orquestrador com integração da Fase 3."""
    
    def __init__(self):
        """Inicializa o orquestrador com todos os módulos da Fase 3."""
        # Configurações
        self.integration_config = IntegrationConfig(
            enable_real_integration=True,
            fallback_to_simulation=True
        )
        
        self.notification_config = NotificationConfig(
            enabled_channels=[
                NotificationType.LOG,
                NotificationType.FILE,
                NotificationType.CALLBACK
            ],
            log_level="INFO"
        )
        
        self.metrics_config = MetricConfig(
            enabled=True,
            enable_real_time=True,
            flush_interval=5.0
        )
        
        self.validation_config = ValidationConfig(
            enabled=True,
            min_quality_score=0.7,
            fail_fast=False
        )
        
        # Inicializar módulos
        self.orchestrator = FluxoCompletoOrchestrator()
        self.integration = SystemIntegration(self.integration_config)
        self.notifications = NotificationManager(self.notification_config)
        self.metrics = MetricsCollector(self.metrics_config)
        self.validator = DataValidator(self.validation_config)
        
        # Configurar callbacks
        self._setup_callbacks()
        
        logger.info("FluxoCompletoComIntegracao inicializado com sucesso")
    
    def _setup_callbacks(self):
        """Configura callbacks para notificações."""
        # Callback para progresso
        def on_progress(notification):
            logger.info(f"Progresso: {notification.title} - {notification.message}")
        
        # Callback para sucesso
        def on_success(notification):
            logger.info(f"Sucesso: {notification.title} - {notification.message}")
            self.metrics.record_counter("etapas_concluidas", 1, {
                "etapa": notification.etapa,
                "nicho": notification.nicho
            })
        
        # Callback para erro
        def on_error(notification):
            logger.error(f"Erro: {notification.title} - {notification.message}")
            self.metrics.record_counter("erros", 1, {
                "etapa": notification.etapa,
                "nicho": notification.nicho
            })
        
        # Callback para conclusão
        def on_complete(notification):
            logger.info(f"Concluído: {notification.title} - {notification.message}")
            self.metrics.record_counter("nichos_concluidos", 1, {
                "nicho": notification.nicho
            })
        
        # Registrar callbacks
        self.notifications.register_callback(NotificationType.PROGRESS, on_progress)
        self.notifications.register_callback(NotificationType.SUCCESS, on_success)
        self.notifications.register_callback(NotificationType.ERROR, on_error)
        self.notifications.register_callback(NotificationType.COMPLETE, on_complete)
    
    def executar_fluxo_completo(self, nichos: List[str]) -> str:
        """
        Executa o fluxo completo com integração da Fase 3.
        
        Args:
            nichos: Lista de nichos para processar
            
        Returns:
            ID da sessão
        """
        # Gerar sessão ID
        sessao_id = f"fluxo_integrado_{int(time.time())}"
        
        # Registrar início da execução
        self.integration.registrar_execucao(
            sessao_id=sessao_id,
            nicho="",  # Nicho geral
            status="iniciando",
            metadados={"nichos": nichos, "fase": "3"}
        )
        
        # Registrar log
        self.integration.registrar_log(
            sessao_id=sessao_id,
            nivel="INFO",
            mensagem=f"Iniciando fluxo completo para {len(nichos)} nichos",
            contexto={"nichos": nichos}
        )
        
        # Notificar início
        self.notifications.notify(
            NotificationType.INFO,
            "Fluxo Iniciado",
            f"Iniciando processamento de {len(nichos)} nichos",
            sessao_id=sessao_id
        )
        
        # Métricas de início
        self.metrics.record_counter("fluxos_iniciados", 1)
        self.metrics.record_gauge("nichos_em_processamento", len(nichos))
        
        # Processar cada nicho
        for index, nicho in enumerate(nichos):
            try:
                # Timer para o nicho
                with self.metrics.start_timer("nicho_duration", {"nicho": nicho}):
                    sucesso = self._processar_nicho_completo(sessao_id, nicho, index + 1, len(nichos))
                
                if sucesso:
                    self.notifications.notify_success(sessao_id, nicho, "processamento_completo")
                else:
                    self.notifications.notify_error(sessao_id, nicho, "processamento", "Falha no processamento")
                
            except Exception as e:
                self.notifications.notify_error(
                    sessao_id, nicho, "processamento", 
                    f"Erro inesperado: {str(e)}"
                )
        
        # Finalizar execução
        self.integration.atualizar_status_execucao(sessao_id, "concluido", 100.0)
        
        # Notificar conclusão
        self.notifications.notify(
            NotificationType.COMPLETE,
            "Fluxo Concluído",
            f"Processamento de {len(nichos)} nichos concluído",
            sessao_id=sessao_id
        )
        
        # Métricas finais
        self.metrics.record_counter("fluxos_concluidos", 1)
        self.metrics.record_gauge("nichos_em_processamento", 0)
        
        return sessao_id
    
    def _processar_nicho_completo(
        self, 
        sessao_id: str, 
        nicho: str, 
        posicao: int, 
        total: int
    ) -> bool:
        """
        Processa um nicho completo com todas as integrações.
        
        Args:
            sessao_id: ID da sessão
            nicho: Nome do nicho
            posicao: Posição atual
            total: Total de nichos
            
        Returns:
            True se processado com sucesso
        """
        try:
            # Registrar início do nicho
            self.integration.registrar_execucao(
                sessao_id=sessao_id,
                nicho=nicho,
                status="em_processamento"
            )
            
            # Obter configuração do nicho
            config_nicho = self.integration.obter_config_nicho(nicho)
            if not config_nicho:
                logger.warning(f"Configuração não encontrada para nicho: {nicho}")
                return False
            
            # Obter prompts do nicho
            prompts = self.integration.obter_prompts_nicho(nicho)
            if not prompts:
                logger.warning(f"Prompts não encontrados para nicho: {nicho}")
                return False
            
            # Notificar início do nicho
            progresso = (posicao / total) * 100
            self.notifications.notify_progress(
                sessao_id, nicho, "inicio", progresso,
                f"Processando nicho {posicao}/{total}"
            )
            
            # Simular coleta de dados
            dados_coletados = self._simular_coleta(nicho, config_nicho)
            
            # Validar dados coletados
            dados_validados = self._validar_dados_coletados(dados_coletados, nicho)
            
            # Processar dados
            dados_processados = self._processar_dados(dados_validados, nicho)
            
            # Gerar prompts
            prompts_gerados = self._gerar_prompts(dados_processados, prompts, nicho)
            
            # Exportar resultados
            arquivo_exportado = self._exportar_resultados(prompts_gerados, nicho)
            
            # Registrar sucesso
            self.integration.atualizar_status_execucao(
                sessao_id, "concluido", 100.0
            )
            
            # Métricas do nicho
            self.metrics.record_counter("keywords_processadas", len(dados_coletados), {"nicho": nicho})
            self.metrics.record_counter("keywords_validadas", len(dados_validados), {"nicho": nicho})
            self.metrics.record_counter("prompts_gerados", len(prompts_gerados), {"nicho": nicho})
            
            # Log de conclusão
            self.integration.registrar_log(
                sessao_id=sessao_id,
                nivel="INFO",
                mensagem=f"Nicho {nicho} processado com sucesso",
                contexto={
                    "keywords_coletadas": len(dados_coletados),
                    "keywords_validadas": len(dados_validados),
                    "prompts_gerados": len(prompts_gerados),
                    "arquivo_exportado": arquivo_exportado
                }
            )
            
            return True
            
        except Exception as e:
            # Registrar erro
            self.integration.registrar_log(
                sessao_id=sessao_id,
                nivel="ERROR",
                mensagem=f"Erro no processamento do nicho {nicho}: {str(e)}",
                contexto={"nicho": nicho, "erro": str(e)}
            )
            
            return False
    
    def _simular_coleta(self, nicho: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simula coleta de dados."""
        # Simular dados coletados
        dados_simulados = [
            {
                "keyword": f"melhor {nicho} 2024",
                "volume": 5000,
                "competition": 0.6,
                "cpc": 2.5
            },
            {
                "keyword": f"{nicho} online",
                "volume": 3000,
                "competition": 0.4,
                "cpc": 1.8
            },
            {
                "keyword": f"comprar {nicho}",
                "volume": 2000,
                "competition": 0.7,
                "cpc": 3.2
            }
        ]
        
        # Métricas de coleta
        self.metrics.record_counter("coletas_realizadas", 1, {"nicho": nicho})
        
        return dados_simulados
    
    def _validar_dados_coletados(
        self, 
        dados: List[Dict[str, Any]], 
        nicho: str
    ) -> List[Dict[str, Any]]:
        """Valida dados coletados."""
        # Contexto para validação
        context = {
            "niche": nicho,
            "min_volume": 100,
            "max_competition": 0.8
        }
        
        # Validar dados
        resultados_validacao = self.validator.validate_data(dados, context)
        
        # Filtrar dados válidos
        dados_validados, _ = self.validator.filter_valid_data(
            dados, context, min_score=0.7
        )
        
        # Métricas de validação
        self.metrics.record_counter("validacoes_realizadas", 1, {"nicho": nicho})
        self.metrics.record_gauge("taxa_validacao", len(dados_validados) / len(dados), {"nicho": nicho})
        
        return dados_validados
    
    def _processar_dados(
        self, 
        dados: List[Dict[str, Any]], 
        nicho: str
    ) -> List[Dict[str, Any]]:
        """Processa dados validados."""
        # Simular processamento
        dados_processados = []
        
        for dado in dados:
            # Adicionar score de qualidade
            dado_processado = {
                **dado,
                "score_qualidade": 0.85,
                "categoria": "long_tail",
                "intencao": "comercial"
            }
            dados_processados.append(dado_processado)
        
        # Métricas de processamento
        self.metrics.record_counter("processamentos_realizados", 1, {"nicho": nicho})
        
        return dados_processados
    
    def _gerar_prompts(
        self, 
        dados: List[Dict[str, Any]], 
        prompts: List[Dict[str, Any]], 
        nicho: str
    ) -> List[Dict[str, Any]]:
        """Gera prompts baseados nos dados."""
        prompts_gerados = []
        
        for dado in dados:
            for prompt in prompts:
                prompt_gerado = {
                    "keyword": dado["keyword"],
                    "prompt_template": prompt["template"],
                    "prompt_final": prompt["template"].replace("{keyword}", dado["keyword"]),
                    "nicho": nicho,
                    "timestamp": datetime.now().isoformat()
                }
                prompts_gerados.append(prompt_gerado)
        
        # Métricas de geração
        self.metrics.record_counter("prompts_gerados", len(prompts_gerados), {"nicho": nicho})
        
        return prompts_gerados
    
    def _exportar_resultados(
        self, 
        prompts: List[Dict[str, Any]], 
        nicho: str
    ) -> str:
        """Exporta resultados."""
        # Simular exportação
        arquivo_exportado = f"resultados_{nicho}_{int(time.time())}.json"
        
        # Métricas de exportação
        self.metrics.record_counter("exportacoes_realizadas", 1, {"nicho": nicho})
        
        return arquivo_exportado
    
    def obter_relatorio_execucao(self, sessao_id: str) -> Dict[str, Any]:
        """
        Obtém relatório completo da execução.
        
        Args:
            sessao_id: ID da sessão
            
        Returns:
            Relatório da execução
        """
        # Métricas
        metricas = self.metrics.get_all_summaries()
        
        # Status da integração
        status_integracao = {
            "sessao_id": sessao_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Relatório
        relatorio = {
            "sessao_id": sessao_id,
            "timestamp": datetime.now().isoformat(),
            "metricas": metricas,
            "status_integracao": status_integracao,
            "configuracoes": {
                "integration": self.integration_config.__dict__,
                "notifications": self.notification_config.__dict__,
                "metrics": self.metrics_config.__dict__,
                "validation": self.validation_config.__dict__
            }
        }
        
        return relatorio


def executar_exemplo_fase3():
    """Executa exemplo da Fase 3."""
    print("🚀 Iniciando exemplo da Fase 3: Integração e Qualidade")
    
    # Criar instância
    fluxo = FluxoCompletoComIntegracao()
    
    # Nichos para processar
    nichos = ["tecnologia", "saude", "financas"]
    
    # Executar fluxo
    sessao_id = fluxo.executar_fluxo_completo(nichos)
    
    # Obter relatório
    relatorio = fluxo.obter_relatorio_execucao(sessao_id)
    
    print(f"✅ Fluxo concluído - Sessão: {sessao_id}")
    print(f"📊 Métricas coletadas: {len(relatorio['metricas'])}")
    
    # Mostrar algumas métricas
    for nome, metrica in relatorio['metricas'].items():
        if metrica['total_labels'] > 0:
            print(f"  - {nome}: {metrica['total_labels']} valores")
    
    return sessao_id, relatorio


if __name__ == "__main__":
    executar_exemplo_fase3() 