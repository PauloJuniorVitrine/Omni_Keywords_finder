"""
Sistema de Logs Estruturados para Cauda Longa
LONGTAIL-004: Sistema completo de logs estruturados específico

Tracing ID: LONGTAIL-004
Data/Hora: 2024-12-20 16:50:00 UTC
Versão: 1.0
Status: EM IMPLEMENTAÇÃO

Responsável: Sistema de Cauda Longa
"""

import json
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from shared.logger import logger


class TipoLog(Enum):
    """Tipos de log para cauda longa."""
    ANALISE_PALAVRAS = "analise_palavras"
    COMPLEXIDADE_SEMANTICA = "complexidade_semantica"
    SCORE_COMPETITIVO = "score_competitivo"
    VALIDACAO = "validacao"
    REJEICAO = "rejeicao"
    APROVACAO = "aprovacao"
    PROCESSAMENTO = "processamento"
    ERRO = "erro"
    PERFORMANCE = "performance"
    TENDENCIA = "tendencia"


class NivelLog(Enum):
    """Níveis de log."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogCaudaLonga:
    """Estrutura de log para cauda longa."""
    timestamp: str
    tracing_id: str
    tipo: TipoLog
    nivel: NivelLog
    keyword: str
    metadados: Dict[str, Any]
    analise_palavras: Optional[Dict] = None
    complexidade_semantica: Optional[Dict] = None
    score_competitivo: Optional[Dict] = None
    resultado_final: Optional[str] = None
    tempo_processamento: Optional[float] = None
    erro: Optional[str] = None


class SistemaLogsCaudaLonga:
    """
    Sistema completo de logs estruturados para cauda longa.
    
    Funcionalidades:
    - Análise de palavras significativas
    - Complexidade semântica calculada
    - Score competitivo e adaptativo
    - Metadados obrigatórios de cauda longa
    - Formato estruturado específico
    - Rastreabilidade completa
    - Integração com processamento
    - Logs de rejeições detalhadas
    - Relatórios de qualidade
    - Análise de tendências
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o sistema de logs para cauda longa.
        
        Args:
            config: Configuração opcional do sistema
        """
        self.config = config or {}
        
        # Configurações de diretório
        self._diretorio_logs = self.config.get("diretorio_logs", "logs/cauda_longa")
        self._max_logs_por_arquivo = self.config.get("max_logs_por_arquivo", 1000)
        self._retencao_dias = self.config.get("retencao_dias", 30)
        
        # Configurações de formato
        self._formato_timestamp = self.config.get("formato_timestamp", "%Y-%m-%dT%H:%M:%S.%fZ")
        self._incluir_metadados_completos = self.config.get("incluir_metadados_completos", True)
        self._compactar_logs_antigos = self.config.get("compactar_logs_antigos", True)
        
        # Contadores de logs
        self.contadores = {
            "total_logs": 0,
            "logs_por_tipo": {tipo.value: 0 for tipo in TipoLog},
            "logs_por_nivel": {nivel.value: 0 for nivel in NivelLog},
            "ultimo_log": None
        }
        
        # Criação do diretório de logs
        self._criar_diretorio_logs()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "sistema_logs_cauda_longa_inicializado",
            "status": "success",
            "source": "SistemaLogsCaudaLonga.__init__",
            "details": {
                "diretorio_logs": self._diretorio_logs,
                "max_logs_por_arquivo": self._max_logs_por_arquivo,
                "retencao_dias": self._retencao_dias,
                "incluir_metadados_completos": self._incluir_metadados_completos
            }
        })
    
    def _criar_diretorio_logs(self):
        """Cria diretório de logs se não existir."""
        Path(self._diretorio_logs).mkdir(parents=True, exist_ok=True)
    
    def _gerar_tracing_id(self, keyword: str) -> str:
        """
        Gera tracing ID único para a keyword.
        
        Args:
            keyword: Keyword para geração do ID
            
        Returns:
            Tracing ID único
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        keyword_hash = hash(keyword) % 10000
        return f"LONGTAIL_{timestamp}_{keyword_hash:04d}"
    
    def _obter_arquivo_log(self, data: datetime) -> str:
        """
        Obtém nome do arquivo de log para a data.
        
        Args:
            data: Data para o arquivo
            
        Returns:
            Nome do arquivo de log
        """
        data_str = data.strftime("%Y-%m-%data")
        return os.path.join(self._diretorio_logs, f"cauda_longa_{data_str}.jsonl")
    
    def _escrever_log(self, log: LogCaudaLonga):
        """
        Escreve log no arquivo apropriado.
        
        Args:
            log: Log a ser escrito
        """
        try:
            arquivo_log = self._obter_arquivo_log(datetime.utcnow())
            
            # Converte log para dicionário
            log_dict = asdict(log)
            
            # Converte enums para strings
            log_dict["tipo"] = log_dict["tipo"].value
            log_dict["nivel"] = log_dict["nivel"].value
            
            # Escreve no arquivo
            with open(arquivo_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_dict, ensure_ascii=False) + "\n")
            
            # Atualiza contadores
            self.contadores["total_logs"] += 1
            self.contadores["logs_por_tipo"][log.tipo.value] += 1
            self.contadores["logs_por_nivel"][log.nivel.value] += 1
            self.contadores["ultimo_log"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_escrever_log_cauda_longa",
                "status": "error",
                "source": "SistemaLogsCaudaLonga._escrever_log",
                "details": {
                    "erro": str(e),
                    "keyword": log.keyword,
                    "tipo": log.tipo.value
                }
            })
    
    def log_analise_palavras(
        self, 
        keyword: str, 
        analise_palavras: Dict, 
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de análise de palavras significativas.
        
        Args:
            keyword: Keyword analisada
            analise_palavras: Resultado da análise de palavras
            metadados: Metadados adicionais
        """
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.ANALISE_PALAVRAS,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados or {},
            analise_palavras=analise_palavras
        )
        
        self._escrever_log(log)
    
    def log_complexidade_semantica(
        self, 
        keyword: str, 
        complexidade_semantica: Dict, 
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de complexidade semântica.
        
        Args:
            keyword: Keyword analisada
            complexidade_semantica: Resultado da análise de complexidade
            metadados: Metadados adicionais
        """
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.COMPLEXIDADE_SEMANTICA,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados or {},
            complexidade_semantica=complexidade_semantica
        )
        
        self._escrever_log(log)
    
    def log_score_competitivo(
        self, 
        keyword: str, 
        score_competitivo: Dict, 
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de score competitivo.
        
        Args:
            keyword: Keyword analisada
            score_competitivo: Resultado do score competitivo
            metadados: Metadados adicionais
        """
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.SCORE_COMPETITIVO,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados or {},
            score_competitivo=score_competitivo
        )
        
        self._escrever_log(log)
    
    def log_validacao(
        self, 
        keyword: str, 
        resultado: str, 
        metadados: Optional[Dict] = None,
        tempo_processamento: Optional[float] = None
    ):
        """
        Registra log de validação.
        
        Args:
            keyword: Keyword validada
            resultado: Resultado da validação
            metadados: Metadados adicionais
            tempo_processamento: Tempo de processamento
        """
        nivel = NivelLog.INFO if resultado == "aprovada" else NivelLog.WARNING
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.VALIDACAO,
            nivel=nivel,
            keyword=keyword,
            metadados=metadados or {},
            resultado_final=resultado,
            tempo_processamento=tempo_processamento
        )
        
        self._escrever_log(log)
    
    def log_rejeicao(
        self, 
        keyword: str, 
        motivo: str, 
        detalhes: Optional[Dict] = None,
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de rejeição detalhada.
        
        Args:
            keyword: Keyword rejeitada
            motivo: Motivo da rejeição
            detalhes: Detalhes da rejeição
            metadados: Metadados adicionais
        """
        metadados_completos = metadados or {}
        if detalhes:
            metadados_completos["detalhes_rejeicao"] = detalhes
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.REJEICAO,
            nivel=NivelLog.WARNING,
            keyword=keyword,
            metadados=metadados_completos,
            resultado_final=f"rejeitada: {motivo}"
        )
        
        self._escrever_log(log)
    
    def log_aprovacao(
        self, 
        keyword: str, 
        score_final: float, 
        metadados: Optional[Dict] = None,
        tempo_processamento: Optional[float] = None
    ):
        """
        Registra log de aprovação.
        
        Args:
            keyword: Keyword aprovada
            score_final: Score final da keyword
            metadados: Metadados adicionais
            tempo_processamento: Tempo de processamento
        """
        metadados_completos = metadados or {}
        metadados_completos["score_final"] = score_final
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.APROVACAO,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados_completos,
            resultado_final="aprovada",
            tempo_processamento=tempo_processamento
        )
        
        self._escrever_log(log)
    
    def log_processamento(
        self, 
        keyword: str, 
        etapa: str, 
        metadados: Optional[Dict] = None,
        tempo_processamento: Optional[float] = None
    ):
        """
        Registra log de processamento.
        
        Args:
            keyword: Keyword processada
            etapa: Etapa do processamento
            metadados: Metadados adicionais
            tempo_processamento: Tempo de processamento
        """
        metadados_completos = metadados or {}
        metadados_completos["etapa"] = etapa
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.PROCESSAMENTO,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados_completos,
            tempo_processamento=tempo_processamento
        )
        
        self._escrever_log(log)
    
    def log_erro(
        self, 
        keyword: str, 
        erro: str, 
        contexto: Optional[Dict] = None,
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de erro.
        
        Args:
            keyword: Keyword com erro
            erro: Descrição do erro
            contexto: Contexto do erro
            metadados: Metadados adicionais
        """
        metadados_completos = metadados or {}
        if contexto:
            metadados_completos["contexto_erro"] = contexto
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.ERRO,
            nivel=NivelLog.ERROR,
            keyword=keyword,
            metadados=metadados_completos,
            erro=erro
        )
        
        self._escrever_log(log)
    
    def log_performance(
        self, 
        keyword: str, 
        metricas: Dict, 
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de performance.
        
        Args:
            keyword: Keyword analisada
            metricas: Métricas de performance
            metadados: Metadados adicionais
        """
        metadados_completos = metadados or {}
        metadados_completos["metricas_performance"] = metricas
        
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.PERFORMANCE,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados_completos
        )
        
        self._escrever_log(log)
    
    def log_tendencia(
        self, 
        keyword: str, 
        tendencia: Dict, 
        metadados: Optional[Dict] = None
    ):
        """
        Registra log de tendência.
        
        Args:
            keyword: Keyword analisada
            tendencia: Dados de tendência
            metadados: Metadados adicionais
        """
        log = LogCaudaLonga(
            timestamp=datetime.utcnow().isoformat(),
            tracing_id=self._gerar_tracing_id(keyword),
            tipo=TipoLog.TENDENCIA,
            nivel=NivelLog.INFO,
            keyword=keyword,
            metadados=metadados or {},
            resultado_final=f"tendencia: {tendencia.get('direcao', 'desconhecida')}"
        )
        
        self._escrever_log(log)
    
    def ler_logs_por_periodo(
        self, 
        data_inicio: datetime, 
        data_fim: datetime,
        tipos: Optional[List[TipoLog]] = None,
        niveis: Optional[List[NivelLog]] = None
    ) -> List[LogCaudaLonga]:
        """
        Lê logs por período com filtros opcionais.
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            tipos: Tipos de log para filtrar
            niveis: Níveis de log para filtrar
            
        Returns:
            Lista de logs filtrados
        """
        logs = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            arquivo_log = self._obter_arquivo_log(data_atual)
            
            if os.path.exists(arquivo_log):
                try:
                    with open(arquivo_log, "r", encoding="utf-8") as f:
                        for linha in f:
                            try:
                                log_dict = json.loads(linha.strip())
                                
                                # Converte strings de volta para enums
                                log_dict["tipo"] = TipoLog(log_dict["tipo"])
                                log_dict["nivel"] = NivelLog(log_dict["nivel"])
                                
                                # Aplica filtros
                                if tipos and log_dict["tipo"] not in tipos:
                                    continue
                                if niveis and log_dict["nivel"] not in niveis:
                                    continue
                                
                                # Cria objeto LogCaudaLonga
                                log = LogCaudaLonga(**log_dict)
                                logs.append(log)
                                
                            except json.JSONDecodeError:
                                continue  # Ignora linhas inválidas
                
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_ler_arquivo_log",
                        "status": "warning",
                        "source": "SistemaLogsCaudaLonga.ler_logs_por_periodo",
                        "details": {
                            "arquivo": arquivo_log,
                            "erro": str(e)
                        }
                    })
            
            data_atual += timedelta(days=1)
        
        return logs
    
    def gerar_relatorio_qualidade(self, periodo_dias: int = 7) -> Dict:
        """
        Gera relatório de qualidade baseado nos logs.
        
        Args:
            periodo_dias: Período em dias para análise
            
        Returns:
            Relatório de qualidade
        """
        data_fim = datetime.utcnow()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        logs = self.ler_logs_por_periodo(data_inicio, data_fim)
        
        if not logs:
            return {"erro": "Nenhum log encontrado no período"}
        
        # Estatísticas por tipo
        estatisticas_tipo = {}
        for tipo in TipoLog:
            logs_tipo = [log for log in logs if log.tipo == tipo]
            estatisticas_tipo[tipo.value] = {
                "total": len(logs_tipo),
                "percentual": (len(logs_tipo) / len(logs)) * 100
            }
        
        # Estatísticas por nível
        estatisticas_nivel = {}
        for nivel in NivelLog:
            logs_nivel = [log for log in logs if log.nivel == nivel]
            estatisticas_nivel[nivel.value] = {
                "total": len(logs_nivel),
                "percentual": (len(logs_nivel) / len(logs)) * 100
            }
        
        # Estatísticas de resultado
        aprovacoes = [log for log in logs if log.resultado_final == "aprovada"]
        rejeicoes = [log for log in logs if log.tipo == TipoLog.REJEICAO]
        erros = [log for log in logs if log.tipo == TipoLog.ERRO]
        
        # Performance média
        tempos_processamento = [
            log.tempo_processamento for log in logs 
            if log.tempo_processamento is not None
        ]
        tempo_medio = sum(tempos_processamento) / len(tempos_processamento) if tempos_processamento else 0
        
        relatorio = {
            "periodo_analise": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "total_dias": periodo_dias
            },
            "estatisticas_gerais": {
                "total_logs": len(logs),
                "keywords_unicas": len(set(log.keyword for log in logs)),
                "tempo_medio_processamento": tempo_medio
            },
            "estatisticas_tipo": estatisticas_tipo,
            "estatisticas_nivel": estatisticas_nivel,
            "resultados": {
                "aprovacoes": len(aprovacoes),
                "rejeicoes": len(rejeicoes),
                "erros": len(erros),
                "taxa_aprovacao": (len(aprovacoes) / (len(aprovacoes) + len(rejeicoes))) * 100 if (len(aprovacoes) + len(rejeicoes)) > 0 else 0
            },
            "top_keywords_processadas": [
                keyword for keyword, count in sorted(
                    [(log.keyword, sum(1 for list_data in logs if list_data.keyword == log.keyword)) 
                     for log in logs],
                    key=lambda value: value[1],
                    reverse=True
                )[:10]
            ]
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "relatorio_qualidade_gerado",
            "status": "success",
            "source": "SistemaLogsCaudaLonga.gerar_relatorio_qualidade",
            "details": {
                "periodo_dias": periodo_dias,
                "total_logs": len(logs),
                "taxa_aprovacao": relatorio["resultados"]["taxa_aprovacao"]
            }
        })
        
        return relatorio
    
    def analisar_tendencias(self, periodo_dias: int = 30) -> Dict:
        """
        Analisa tendências baseado nos logs.
        
        Args:
            periodo_dias: Período em dias para análise
            
        Returns:
            Análise de tendências
        """
        data_fim = datetime.utcnow()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        logs = self.ler_logs_por_periodo(data_inicio, data_fim)
        
        if not logs:
            return {"erro": "Nenhum log encontrado no período"}
        
        # Agrupa logs por dia
        logs_por_dia = {}
        for log in logs:
            data_log = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00')).date()
            if data_log not in logs_por_dia:
                logs_por_dia[data_log] = []
            logs_por_dia[data_log].append(log)
        
        # Calcula métricas diárias
        metricas_diarias = []
        for data, logs_dia in sorted(logs_por_dia.items()):
            aprovacoes = len([log for log in logs_dia if log.resultado_final == "aprovada"])
            rejeicoes = len([log for log in logs_dia if log.tipo == TipoLog.REJEICAO])
            erros = len([log for log in logs_dia if log.tipo == TipoLog.ERRO])
            
            metricas_diarias.append({
                "data": data.isoformat(),
                "total_logs": len(logs_dia),
                "aprovacoes": aprovacoes,
                "rejeicoes": rejeicoes,
                "erros": erros,
                "taxa_aprovacao": (aprovacoes / (aprovacoes + rejeicoes)) * 100 if (aprovacoes + rejeicoes) > 0 else 0
            })
        
        # Calcula tendências
        if len(metricas_diarias) > 1:
            primeira_semana = metricas_diarias[:7]
            ultima_semana = metricas_diarias[-7:]
            
            taxa_inicial = sum(m["taxa_aprovacao"] for m in primeira_semana) / len(primeira_semana)
            taxa_final = sum(m["taxa_aprovacao"] for m in ultima_semana) / len(ultima_semana)
            
            tendencia_taxa = "melhorando" if taxa_final > taxa_inicial else "piorando" if taxa_final < taxa_inicial else "estavel"
        else:
            tendencia_taxa = "insuficientes_dados"
        
        analise_tendencias = {
            "periodo_analise": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "total_dias": periodo_dias
            },
            "metricas_diarias": metricas_diarias,
            "tendencias": {
                "taxa_aprovacao": tendencia_taxa,
                "volume_processamento": "estavel" if len(metricas_diarias) > 0 else "sem_dados"
            },
            "resumo": {
                "total_logs_periodo": len(logs),
                "media_logs_dia": len(logs) / periodo_dias,
                "taxa_aprovacao_media": sum(m["taxa_aprovacao"] for m in metricas_diarias) / len(metricas_diarias) if metricas_diarias else 0
            }
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "analise_tendencias_gerada",
            "status": "success",
            "source": "SistemaLogsCaudaLonga.analisar_tendencias",
            "details": {
                "periodo_dias": periodo_dias,
                "tendencia_taxa": tendencia_taxa,
                "total_logs": len(logs)
            }
        })
        
        return analise_tendencias
    
    def limpar_logs_antigos(self):
        """Remove logs mais antigos que o período de retenção."""
        try:
            data_limite = datetime.utcnow() - timedelta(days=self._retencao_dias)
            
            for arquivo in Path(self._diretorio_logs).glob("cauda_longa_*.jsonl"):
                try:
                    # Extrai data do nome do arquivo
                    data_str = arquivo.stem.split("_")[-1]
                    data_arquivo = datetime.strptime(data_str, "%Y-%m-%data")
                    
                    if data_arquivo < data_limite:
                        arquivo.unlink()
                        logger.info({
                            "timestamp": datetime.utcnow().isoformat(),
                            "event": "log_antigo_removido",
                            "status": "info",
                            "source": "SistemaLogsCaudaLonga.limpar_logs_antigos",
                            "details": {"arquivo": str(arquivo)}
                        })
                
                except Exception as e:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "erro_remover_log_antigo",
                        "status": "warning",
                        "source": "SistemaLogsCaudaLonga.limpar_logs_antigos",
                        "details": {
                            "arquivo": str(arquivo),
                            "erro": str(e)
                        }
                    })
        
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_limpar_logs_antigos",
                "status": "error",
                "source": "SistemaLogsCaudaLonga.limpar_logs_antigos",
                "details": {"erro": str(e)}
            })
    
    def obter_metricas(self) -> Dict:
        """
        Obtém métricas do sistema de logs.
        
        Returns:
            Dicionário com métricas
        """
        return {
            **self.contadores,
            "configuracao": {
                "diretorio_logs": self._diretorio_logs,
                "max_logs_por_arquivo": self._max_logs_por_arquivo,
                "retencao_dias": self._retencao_dias,
                "incluir_metadados_completos": self._incluir_metadados_completos
            }
        }
    
    def resetar_contadores(self):
        """Reseta contadores de logs."""
        self.contadores = {
            "total_logs": 0,
            "logs_por_tipo": {tipo.value: 0 for tipo in TipoLog},
            "logs_por_nivel": {nivel.value: 0 for nivel in NivelLog},
            "ultimo_log": None
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "contadores_resetados",
            "status": "info",
            "source": "SistemaLogsCaudaLonga.resetar_contadores",
            "details": {"acao": "reset_contadores"}
        })


# Instância global para uso em outros módulos
sistema_logs_cauda_longa = SistemaLogsCaudaLonga() 