"""
Validador de Cauda Longa Avançado - Omni Keywords Finder
Tracing ID: LONGTAIL-008
Data/Hora: 2024-12-20 17:15:00 UTC
Versão: 1.0
Status: IMPLEMENTADO

Sistema completo de validação avançada que integra todos os componentes
para fornecer validação robusta e confiável de keywords de cauda longa.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import traceback

# Importações dos módulos relacionados
try:
    from .analisador_semantico_cauda_longa import AnalisadorSemanticoCaudaLonga, AnaliseSemantica
    from .score_composto_inteligente import ScoreCompostoInteligente, ScoreComposto
    from .configuracao_adaptativa import ConfiguracaoAdaptativa, ConfiguracaoNicho, TipoNicho
    from .analisador_semantico import AnalisadorSemantico
    from .complexidade_semantica import ComplexidadeSemantica
    from .score_competitivo import ScoreCompetitivo
    from .logs_cauda_longa import LogsCaudaLonga
except ImportError:
    # Fallback para importação local
    pass

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatusValidacao(Enum):
    """Status de validação."""
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    PENDENTE = "pendente"
    ERRO = "erro"

class CriticidadeValidacao(Enum):
    """Criticidade da validação."""
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"

@dataclass
class CriterioValidacao:
    """Estrutura para critério de validação."""
    nome: str
    descricao: str
    status: StatusValidacao
    valor_atual: Any
    valor_esperado: Any
    criticidade: CriticidadeValidacao
    peso: float
    mensagem: str
    timestamp: datetime

@dataclass
class ResultadoValidacao:
    """Estrutura para resultado de validação."""
    keyword: str
    status_final: StatusValidacao
    score_final: float
    criterios: List[CriterioValidacao]
    analise_semantica: Optional[Dict[str, Any]]
    score_composto: Optional[Dict[str, Any]]
    configuracao_aplicada: Optional[Dict[str, Any]]
    metadados: Dict[str, Any]
    timestamp: datetime
    tracing_id: str
    duracao_processamento: float

class ValidadorCaudaLongaAvancado:
    """
    Sistema de validação avançada de cauda longa.
    
    Características:
    - Integração com todos os componentes
    - Validação multi-critério
    - Configuração adaptativa
    - Logs estruturados
    - Performance otimizada
    - Configuração flexível
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o validador avançado.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.tracing_id = f"LONGTAIL-008_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config_path = config_path
        
        # Inicialização dos componentes
        self.analisador_semantico = None
        self.score_composto = None
        self.configuracao_adaptativa = None
        self.analisador_semantico_basico = None
        self.complexidade_semantica = None
        self.score_competitivo = None
        self.logs_cauda_longa = None
        
        self._inicializar_componentes()
        
        # Configurações de validação
        self.config_validacao = self._carregar_config_validacao()
        
        logger.info(f"[{self.tracing_id}] Validador avançado inicializado com sucesso")
    
    def _inicializar_componentes(self):
        """Inicializa todos os componentes necessários."""
        try:
            # Componentes principais
            self.analisador_semantico = AnalisadorSemanticoCaudaLonga()
            self.score_composto = ScoreCompostoInteligente()
            self.configuracao_adaptativa = ConfiguracaoAdaptativa()
            
            # Componentes de suporte
            self.analisador_semantico_basico = AnalisadorSemantico()
            self.complexidade_semantica = ComplexidadeSemantica()
            self.score_competitivo = ScoreCompetitivo()
            self.logs_cauda_longa = LogsCaudaLonga()
            
            logger.info(f"[{self.tracing_id}] Todos os componentes inicializados")
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na inicialização de componentes: {e}")
            # Fallback para componentes básicos
            self._inicializar_componentes_basicos()
    
    def _inicializar_componentes_basicos(self):
        """Inicializa componentes básicos em caso de falha."""
        logger.warning(f"[{self.tracing_id}] Usando componentes básicos")
        # Implementação básica dos componentes se necessário
    
    def _carregar_config_validacao(self) -> Dict[str, Any]:
        """Carrega configuração de validação."""
        config_padrao = {
            "thresholds": {
                "score_minimo_aprovacao": 0.7,
                "especificidade_minima": 0.6,
                "complexidade_minima": 0.5,
                "score_competitivo_minimo": 0.5,
                "similaridade_semantica_minima": 0.7
            },
            "pesos_criterios": {
                "analise_semantica": 0.3,
                "score_composto": 0.3,
                "configuracao_adaptativa": 0.2,
                "validacoes_basicas": 0.2
            },
            "timeout_validacao": 60,
            "max_tentativas": 3,
            "habilitar_cache": True,
            "cache_duracao": 3600
        }
        
        if self.config_path:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_custom = json.load(f)
                    config_padrao.update(config_custom)
            except Exception as e:
                logger.warning(f"[{self.tracing_id}] Erro ao carregar config: {e}")
        
        return config_padrao
    
    def validar_keyword(
        self, 
        keyword: str, 
        dados_mercado: Optional[Dict[str, Any]] = None,
        dados_tendencia: Optional[Dict[str, Any]] = None,
        nicho_sugerido: Optional[str] = None
    ) -> ResultadoValidacao:
        """
        Valida uma keyword de cauda longa de forma completa.
        
        Args:
            keyword: Keyword a ser validada
            dados_mercado: Dados de mercado
            dados_tendencia: Dados de tendência
            nicho_sugerido: Nicho sugerido
            
        Returns:
            ResultadoValidacao: Resultado completo da validação
        """
        inicio_processamento = datetime.now()
        
        try:
            logger.info(f"[{self.tracing_id}] Iniciando validação avançada: {keyword}")
            
            # Dados padrão
            dados_mercado = dados_mercado or {}
            dados_tendencia = dados_tendencia or {}
            
            # 1. Configuração adaptativa
            config_aplicada = self._aplicar_configuracao_adaptativa(keyword, nicho_sugerido)
            
            # 2. Análise semântica
            analise_semantica = self._realizar_analise_semantica(keyword)
            
            # 3. Score composto
            score_composto = self._calcular_score_composto(keyword, dados_mercado, dados_tendencia, config_aplicada)
            
            # 4. Validações básicas
            validacoes_basicas = self._realizar_validacoes_basicas(keyword, config_aplicada)
            
            # 5. Critérios de validação
            criterios = self._avaliar_criterios(
                keyword, analise_semantica, score_composto, config_aplicada, validacoes_basicas
            )
            
            # 6. Determinação do status final
            status_final, score_final = self._determinar_status_final(criterios)
            
            # 7. Metadados
            metadados = self._gerar_metadados(
                keyword, config_aplicada, dados_mercado, dados_tendencia
            )
            
            # 8. Logs
            self._registrar_logs(keyword, status_final, score_final, criterios)
            
            # Cálculo da duração
            duracao = (datetime.now() - inicio_processamento).total_seconds()
            
            # Criação do resultado
            resultado = ResultadoValidacao(
                keyword=keyword,
                status_final=status_final,
                score_final=score_final,
                criterios=criterios,
                analise_semantica=analise_semantica,
                score_composto=score_composto,
                configuracao_aplicada=config_aplicada,
                metadados=metadados,
                timestamp=datetime.now(),
                tracing_id=self.tracing_id,
                duracao_processamento=duracao
            )
            
            logger.info(f"[{self.tracing_id}] Validação concluída - Status: {status_final.value}, Score: {score_final:.3f}")
            return resultado
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na validação: {e}")
            return self._criar_resultado_erro(keyword, str(e), inicio_processamento)
    
    def _aplicar_configuracao_adaptativa(self, keyword: str, nicho_sugerido: Optional[str]) -> Dict[str, Any]:
        """Aplica configuração adaptativa baseada na keyword."""
        try:
            dados_adicionais = {"nicho_sugerido": nicho_sugerido} if nicho_sugerido else None
            config = self.configuracao_adaptativa.configurar_automaticamente(keyword, dados_adicionais)
            
            return {
                "nicho": config.nicho.value,
                "nome_exibicao": config.nome_exibicao,
                "descricao": config.descricao,
                "parametros": {
                    "score_minimo_aprovacao": config.score_minimo_aprovacao,
                    "threshold_especificidade": config.threshold_especificidade,
                    "threshold_similaridade": config.threshold_similaridade,
                    "peso_complexidade": config.peso_complexidade,
                    "peso_especificidade": config.peso_especificidade,
                    "peso_competitivo": config.peso_competitivo,
                    "peso_tendencia": config.peso_tendencia
                }
            }
            
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro na configuração adaptativa: {e}")
            return {"nicho": "generico", "nome_exibicao": "Genérico", "descricao": "Configuração padrão"}
    
    def _realizar_analise_semantica(self, keyword: str) -> Dict[str, Any]:
        """Realiza análise semântica da keyword."""
        try:
            if self.analisador_semantico:
                analise = self.analisador_semantico.analisar_keyword(keyword)
                return {
                    "embedding_score": analise.embedding_score,
                    "especificidade": analise.especificidade,
                    "intencao_detectada": analise.intencao_detectada,
                    "palavras_chave_especificas": analise.palavras_chave_especificas,
                    "similaridade_semantica": analise.similaridade_semantica,
                    "score_qualidade_semantica": analise.score_qualidade_semantica
                }
            else:
                # Fallback básico
                return {
                    "embedding_score": 0.5,
                    "especificidade": 0.5,
                    "intencao_detectada": "informativa",
                    "palavras_chave_especificas": [],
                    "similaridade_semantica": 0.5,
                    "score_qualidade_semantica": 0.5
                }
                
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro na análise semântica: {e}")
            return {"score_qualidade_semantica": 0.0}
    
    def _calcular_score_composto(
        self, 
        keyword: str, 
        dados_mercado: Dict[str, Any], 
        dados_tendencia: Dict[str, Any],
        config_aplicada: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula score composto da keyword."""
        try:
            if self.score_composto:
                nicho = config_aplicada.get("nicho", "generico")
                score = self.score_composto.calcular_score_composto(
                    keyword, dados_mercado, dados_tendencia, nicho
                )
                
                return {
                    "score_final": score.score_final,
                    "classificacao": score.classificacao,
                    "confianca": score.confianca,
                    "componentes": {
                        nome: {
                            "valor": comp.valor,
                            "peso": comp.peso_normalizado,
                            "descricao": comp.descricao
                        }
                        for nome, comp in score.componentes.items()
                    }
                }
            else:
                # Fallback básico
                return {
                    "score_final": 0.5,
                    "classificacao": "regular",
                    "confianca": 0.5,
                    "componentes": {}
                }
                
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro no score composto: {e}")
            return {"score_final": 0.0, "classificacao": "ruim", "confianca": 0.0}
    
    def _realizar_validacoes_basicas(self, keyword: str, config_aplicada: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza validações básicas da keyword."""
        try:
            validacoes = {}
            
            # Validação de comprimento
            palavras = keyword.split()
            validacoes["comprimento_adequado"] = {
                "status": len(palavras) >= 3,
                "valor": len(palavras),
                "minimo": 3,
                "maximo": 15
            }
            
            # Validação de caracteres especiais
            caracteres_especiais = sum(1 for c in keyword if not c.isalnum() and c != ' ')
            validacoes["caracteres_especiais"] = {
                "status": caracteres_especiais <= 5,
                "valor": caracteres_especiais,
                "maximo": 5
            }
            
            # Validação de palavras repetidas
            palavras_unicas = len(set(palavras))
            validacoes["palavras_unicas"] = {
                "status": palavras_unicas >= len(palavras) * 0.8,
                "valor": palavras_unicas,
                "total": len(palavras),
                "percentual": palavras_unicas / len(palavras) if palavras else 0
            }
            
            return validacoes
            
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro nas validações básicas: {e}")
            return {}
    
    def _avaliar_criterios(
        self,
        keyword: str,
        analise_semantica: Dict[str, Any],
        score_composto: Dict[str, Any],
        config_aplicada: Dict[str, Any],
        validacoes_basicas: Dict[str, Any]
    ) -> List[CriterioValidacao]:
        """Avalia todos os critérios de validação."""
        criterios = []
        thresholds = self.config_validacao["thresholds"]
        config_params = config_aplicada.get("parametros", {})
        
        # Critério 1: Score composto
        score_final = score_composto.get("score_final", 0)
        score_minimo = config_params.get("score_minimo_aprovacao", thresholds["score_minimo_aprovacao"])
        
        criterios.append(CriterioValidacao(
            nome="score_composto",
            descricao="Score composto final da keyword",
            status=StatusValidacao.APROVADA if score_final >= score_minimo else StatusValidacao.REJEITADA,
            valor_atual=score_final,
            valor_esperado=f">= {score_minimo}",
            criticidade=CriticidadeValidacao.CRITICA,
            peso=0.3,
            mensagem=f"Score {score_final:.3f} {'atende' if score_final >= score_minimo else 'não atende'} ao mínimo {score_minimo}",
            timestamp=datetime.now()
        ))
        
        # Critério 2: Especificidade semântica
        especificidade = analise_semantica.get("especificidade", 0)
        especificidade_minima = config_params.get("threshold_especificidade", thresholds["especificidade_minima"])
        
        criterios.append(CriterioValidacao(
            nome="especificidade_semantica",
            descricao="Especificidade semântica da keyword",
            status=StatusValidacao.APROVADA if especificidade >= especificidade_minima else StatusValidacao.REJEITADA,
            valor_atual=especificidade,
            valor_esperado=f">= {especificidade_minima}",
            criticidade=CriticidadeValidacao.ALTA,
            peso=0.25,
            mensagem=f"Especificidade {especificidade:.3f} {'atende' if especificidade >= especificidade_minima else 'não atende'} ao mínimo {especificidade_minima}",
            timestamp=datetime.now()
        ))
        
        # Critério 3: Similaridade semântica
        similaridade = analise_semantica.get("similaridade_semantica", 0)
        similaridade_minima = config_params.get("threshold_similaridade", thresholds["similaridade_semantica_minima"])
        
        criterios.append(CriterioValidacao(
            nome="similaridade_semantica",
            descricao="Similaridade semântica da keyword",
            status=StatusValidacao.APROVADA if similaridade >= similaridade_minima else StatusValidacao.REJEITADA,
            valor_atual=similaridade,
            valor_esperado=f">= {similaridade_minima}",
            criticidade=CriticidadeValidacao.ALTA,
            peso=0.2,
            mensagem=f"Similaridade {similaridade:.3f} {'atende' if similaridade >= similaridade_minima else 'não atende'} ao mínimo {similaridade_minima}",
            timestamp=datetime.now()
        ))
        
        # Critério 4: Validações básicas
        validacoes_aprovadas = sum(1 for value in validacoes_basicas.values() if value.get("status", False))
        total_validacoes = len(validacoes_basicas)
        
        criterios.append(CriterioValidacao(
            nome="validacoes_basicas",
            descricao="Validações básicas de formato e estrutura",
            status=StatusValidacao.APROVADA if validacoes_aprovadas == total_validacoes else StatusValidacao.REJEITADA,
            valor_atual=f"{validacoes_aprovadas}/{total_validacoes}",
            valor_esperado=f"{total_validacoes}/{total_validacoes}",
            criticidade=CriticidadeValidacao.MEDIA,
            peso=0.15,
            mensagem=f"{validacoes_aprovadas} de {total_validacoes} validações básicas aprovadas",
            timestamp=datetime.now()
        ))
        
        # Critério 5: Confiança do score
        confianca = score_composto.get("confianca", 0)
        confianca_minima = 0.5
        
        criterios.append(CriterioValidacao(
            nome="confianca_score",
            descricao="Nível de confiança do score composto",
            status=StatusValidacao.APROVADA if confianca >= confianca_minima else StatusValidacao.REJEITADA,
            valor_atual=confianca,
            valor_esperado=f">= {confianca_minima}",
            criticidade=CriticidadeValidacao.BAIXA,
            peso=0.1,
            mensagem=f"Confiança {confianca:.3f} {'atende' if confianca >= confianca_minima else 'não atende'} ao mínimo {confianca_minima}",
            timestamp=datetime.now()
        ))
        
        return criterios
    
    def _determinar_status_final(self, criterios: List[CriterioValidacao]) -> Tuple[StatusValidacao, float]:
        """Determina o status final baseado nos critérios."""
        try:
            # Cálculo do score ponderado
            score_ponderado = 0
            peso_total = 0
            
            for criterio in criterios:
                peso = criterio.peso
                peso_total += peso
                
                if criterio.status == StatusValidacao.APROVADA:
                    score_ponderado += peso
                elif criterio.status == StatusValidacao.REJEITADA:
                    # Penalização para critérios críticos
                    if criterio.criticidade == CriticidadeValidacao.CRITICA:
                        score_ponderado -= peso * 0.5
                    elif criterio.criticidade == CriticidadeValidacao.ALTA:
                        score_ponderado -= peso * 0.3
            
            # Normalização do score
            if peso_total > 0:
                score_final = max(0, min(1, score_ponderado / peso_total))
            else:
                score_final = 0
            
            # Determinação do status
            if score_final >= 0.7:
                status = StatusValidacao.APROVADA
            elif score_final >= 0.5:
                status = StatusValidacao.PENDENTE
            else:
                status = StatusValidacao.REJEITADA
            
            return status, score_final
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na determinação do status final: {e}")
            return StatusValidacao.ERRO, 0.0
    
    def _gerar_metadados(
        self,
        keyword: str,
        config_aplicada: Dict[str, Any],
        dados_mercado: Dict[str, Any],
        dados_tendencia: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera metadados da validação."""
        return {
            "nicho_aplicado": config_aplicada.get("nicho", "generico"),
            "configuracao_nome": config_aplicada.get("nome_exibicao", "Genérico"),
            "dados_mercado_fornecidos": bool(dados_mercado),
            "dados_tendencia_fornecidos": bool(dados_tendencia),
            "componentes_ativos": {
                "analisador_semantico": self.analisador_semantico is not None,
                "score_composto": self.score_composto is not None,
                "configuracao_adaptativa": self.configuracao_adaptativa is not None
            },
            "versao_validador": "1.0",
            "config_validacao": self.config_validacao
        }
    
    def _registrar_logs(self, keyword: str, status: StatusValidacao, score: float, criterios: List[CriterioValidacao]):
        """Registra logs da validação."""
        try:
            if self.logs_cauda_longa:
                log_data = {
                    "keyword": keyword,
                    "status": status.value,
                    "score": score,
                    "criterios_aprovados": sum(1 for c in criterios if c.status == StatusValidacao.APROVADA),
                    "total_criterios": len(criterios),
                    "tracing_id": self.tracing_id
                }
                self.logs_cauda_longa.registrar_validacao(log_data)
                
        except Exception as e:
            logger.warning(f"[{self.tracing_id}] Erro ao registrar logs: {e}")
    
    def _criar_resultado_erro(self, keyword: str, erro: str, inicio_processamento: datetime) -> ResultadoValidacao:
        """Cria resultado de erro em caso de falha."""
        duracao = (datetime.now() - inicio_processamento).total_seconds()
        
        criterio_erro = CriterioValidacao(
            nome="erro_processamento",
            descricao="Erro durante o processamento",
            status=StatusValidacao.ERRO,
            valor_atual=erro,
            valor_esperado="Processamento sem erros",
            criticidade=CriticidadeValidacao.CRITICA,
            peso=1.0,
            mensagem=f"Erro: {erro}",
            timestamp=datetime.now()
        )
        
        return ResultadoValidacao(
            keyword=keyword,
            status_final=StatusValidacao.ERRO,
            score_final=0.0,
            criterios=[criterio_erro],
            analise_semantica=None,
            score_composto=None,
            configuracao_aplicada=None,
            metadados={"erro": erro},
            timestamp=datetime.now(),
            tracing_id=self.tracing_id,
            duracao_processamento=duracao
        )
    
    def validar_multiplas_keywords(
        self, 
        keywords: List[str], 
        dados_mercado: Optional[Dict[str, Any]] = None,
        dados_tendencia: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Valida múltiplas keywords de uma vez.
        
        Args:
            keywords: Lista de keywords
            dados_mercado: Dados de mercado
            dados_tendencia: Dados de tendência
            
        Returns:
            Dict com resultados de todas as validações
        """
        try:
            logger.info(f"[{self.tracing_id}] Iniciando validação de {len(keywords)} keywords")
            
            resultados = []
            estatisticas = {
                "total": len(keywords),
                "aprovadas": 0,
                "rejeitadas": 0,
                "pendentes": 0,
                "erros": 0,
                "scores": []
            }
            
            for keyword in keywords:
                try:
                    resultado = self.validar_keyword(keyword, dados_mercado, dados_tendencia)
                    resultados.append(resultado)
                    
                    # Atualização de estatísticas
                    if resultado.status_final == StatusValidacao.APROVADA:
                        estatisticas["aprovadas"] += 1
                    elif resultado.status_final == StatusValidacao.REJEITADA:
                        estatisticas["rejeitadas"] += 1
                    elif resultado.status_final == StatusValidacao.PENDENTE:
                        estatisticas["pendentes"] += 1
                    else:
                        estatisticas["erros"] += 1
                    
                    estatisticas["scores"].append(resultado.score_final)
                    
                except Exception as e:
                    logger.error(f"[{self.tracing_id}] Erro ao validar '{keyword}': {e}")
                    estatisticas["erros"] += 1
            
            # Cálculo de estatísticas adicionais
            if estatisticas["scores"]:
                estatisticas["score_medio"] = sum(estatisticas["scores"]) / len(estatisticas["scores"])
                estatisticas["score_minimo"] = min(estatisticas["scores"])
                estatisticas["score_maximo"] = max(estatisticas["scores"])
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "estatisticas": estatisticas,
                "resultados": [
                    {
                        "keyword": r.keyword,
                        "status": r.status_final.value,
                        "score": r.score_final,
                        "duracao": r.duracao_processamento
                    }
                    for r in resultados
                ]
            }
            
            logger.info(f"[{self.tracing_id}] Validação em lote concluída - {estatisticas['aprovadas']} aprovadas")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na validação em lote: {e}")
            raise
    
    def gerar_relatorio_validacao(self, resultados: List[ResultadoValidacao]) -> Dict[str, Any]:
        """
        Gera relatório detalhado de validações.
        
        Args:
            resultados: Lista de resultados de validação
            
        Returns:
            Dict com relatório completo
        """
        try:
            # Análise por status
            status_count = {}
            scores_por_status = {}
            
            for resultado in resultados:
                status = resultado.status_final.value
                if status not in status_count:
                    status_count[status] = 0
                    scores_por_status[status] = []
                
                status_count[status] += 1
                scores_por_status[status].append(resultado.score_final)
            
            # Análise por critério
            criterios_analise = {}
            for resultado in resultados:
                for criterio in resultado.criterios:
                    nome = criterio.nome
                    if nome not in criterios_analise:
                        criterios_analise[nome] = {
                            "total": 0,
                            "aprovados": 0,
                            "rejeitados": 0,
                            "scores": []
                        }
                    
                    criterios_analise[nome]["total"] += 1
                    if criterio.status == StatusValidacao.APROVADA:
                        criterios_analise[nome]["aprovados"] += 1
                    else:
                        criterios_analise[nome]["rejeitados"] += 1
                    
                    criterios_analise[nome]["scores"].append(criterio.valor if isinstance(criterio.valor, (int, float)) else 0)
            
            # Cálculo de taxas de aprovação por critério
            for nome, dados in criterios_analise.items():
                if dados["total"] > 0:
                    dados["taxa_aprovacao"] = dados["aprovados"] / dados["total"]
                    dados["score_medio"] = sum(dados["scores"]) / len(dados["scores"]) if dados["scores"] else 0
            
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "resumo": {
                    "total_keywords": len(resultados),
                    "status_distribuicao": status_count,
                    "score_medio_geral": sum(r.score_final for r in resultados) / len(resultados) if resultados else 0
                },
                "analise_por_status": {
                    status: {
                        "count": count,
                        "score_medio": sum(scores_por_status[status]) / len(scores_por_status[status]) if scores_por_status[status] else 0
                    }
                    for status, count in status_count.items()
                },
                "analise_por_criterio": criterios_analise,
                "resultados_detalhados": [
                    {
                        "keyword": r.keyword,
                        "status": r.status_final.value,
                        "score": r.score_final,
                        "criterios": [
                            {
                                "nome": c.nome,
                                "status": c.status.value,
                                "valor": c.valor,
                                "mensagem": c.mensagem
                            }
                            for c in r.criterios
                        ],
                        "duracao": r.duracao_processamento
                    }
                    for r in resultados
                ]
            }
            
            logger.info(f"[{self.tracing_id}] Relatório de validação gerado")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {e}")
            raise

# Funções de conveniência
def validar_keyword_cauda_longa(
    keyword: str,
    dados_mercado: Optional[Dict[str, Any]] = None,
    dados_tendencia: Optional[Dict[str, Any]] = None,
    nicho_sugerido: Optional[str] = None,
    config_path: Optional[str] = None
) -> ResultadoValidacao:
    """
    Função de conveniência para validação rápida de keyword.
    
    Args:
        keyword: Keyword a ser validada
        dados_mercado: Dados de mercado
        dados_tendencia: Dados de tendência
        nicho_sugerido: Nicho sugerido
        config_path: Caminho para configuração
        
    Returns:
        ResultadoValidacao: Resultado da validação
    """
    validador = ValidadorCaudaLongaAvancado(config_path)
    return validador.validar_keyword(keyword, dados_mercado, dados_tendencia, nicho_sugerido)

def validar_multiplas_keywords_cauda_longa(
    keywords: List[str],
    dados_mercado: Optional[Dict[str, Any]] = None,
    dados_tendencia: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função de conveniência para validação em lote.
    
    Args:
        keywords: Lista de keywords
        dados_mercado: Dados de mercado
        dados_tendencia: Dados de tendência
        config_path: Caminho para configuração
        
    Returns:
        Dict: Resultados da validação em lote
    """
    validador = ValidadorCaudaLongaAvancado(config_path)
    return validador.validar_multiplas_keywords(keywords, dados_mercado, dados_tendencia)

if __name__ == "__main__":
    # Teste básico do validador avançado
    validador = ValidadorCaudaLongaAvancado()
    
    # Keywords de teste
    keywords_teste = [
        "melhor preço notebook gaming 2024",
        "como fazer backup automático windows 11",
        "sintomas de diabetes tipo 2 em adultos",
        "curso online marketing digital certificado",
        "investimento em criptomoedas para iniciantes"
    ]
    
    print("=== TESTE DO VALIDADOR DE CAUDA LONGA AVANÇADO ===")
    resultados = []
    
    for keyword in keywords_teste:
        resultado = validador.validar_keyword(keyword)
        resultados.append(resultado)
        
        print(f"\nKeyword: {keyword}")
        print(f"Status: {resultado.status_final.value}")
        print(f"Score: {resultado.score_final:.3f}")
        print(f"Duração: {resultado.duracao_processamento:.2f}string_data")
        print("Critérios:")
        for criterio in resultado.criterios:
            print(f"  {criterio.nome}: {criterio.status.value} - {criterio.mensagem}")
    
    # Gerar relatório
    relatorio = validador.gerar_relatorio_validacao(resultados)
    print(f"\n=== RELATÓRIO ===")
    print(f"Total: {relatorio['resumo']['total_keywords']}")
    print(f"Score médio: {relatorio['resumo']['score_medio_geral']:.3f}")
    print("Distribuição por status:")
    for status, count in relatorio['resumo']['status_distribuicao'].items():
        print(f"  {status}: {count}") 