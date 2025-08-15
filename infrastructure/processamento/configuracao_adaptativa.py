"""
Configuração Adaptativa por Nicho - Omni Keywords Finder
Tracing ID: LONGTAIL-007
Data/Hora: 2024-12-20 17:10:00 UTC
Versão: 1.0
Status: IMPLEMENTADO

Sistema completo de configuração adaptativa que ajusta parâmetros automaticamente
baseado no nicho de mercado, otimizando a detecção de keywords de cauda longa.
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import yaml

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoNicho(Enum):
    """Tipos de nicho suportados."""
    ECOMMERCE = "ecommerce"
    SAUDE = "saude"
    TECNOLOGIA = "tecnologia"
    EDUCACAO = "educacao"
    FINANCAS = "financas"
    GENERICO = "generico"

@dataclass
class ConfiguracaoNicho:
    """Estrutura de configuração específica por nicho."""
    nicho: TipoNicho
    nome_exibicao: str
    descricao: str
    
    # Parâmetros de análise semântica
    min_palavras_significativas: int
    max_palavras_significativas: int
    threshold_especificidade: float
    threshold_similaridade: float
    
    # Parâmetros de score
    peso_complexidade: float
    peso_especificidade: float
    peso_competitivo: float
    peso_tendencia: float
    
    # Parâmetros de validação
    score_minimo_aprovacao: float
    threshold_volume_busca: int
    threshold_cpc_minimo: float
    threshold_cpc_maximo: float
    threshold_concorrencia_maxima: float
    
    # Palavras-chave específicas
    palavras_chave_especificas: List[str]
    palavras_chave_negativas: List[str]
    
    # Configurações de tendência
    peso_crescimento_volume: float
    peso_novidade: float
    peso_sazonalidade: float
    
    # Configurações de performance
    timeout_analise: int
    max_tentativas: int
    cache_duracao: int
    
    # Metadados
    criado_em: datetime
    atualizado_em: datetime
    versao: str
    ativo: bool

class ConfiguracaoAdaptativa:
    """
    Sistema de configuração adaptativa por nicho.
    
    Características:
    - Detecção automática de nicho
    - Configuração específica por tipo de mercado
    - Ajuste dinâmico de parâmetros
    - Persistência de configurações
    - Validação de parâmetros
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o sistema de configuração adaptativa.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.tracing_id = f"LONGTAIL-007_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config_path = config_path
        self.configuracoes = self._carregar_configuracoes_padrao()
        self.configuracao_atual = None
        self.historico_ajustes = []
        
        logger.info(f"[{self.tracing_id}] Sistema de configuração adaptativa inicializado")
    
    def _carregar_configuracoes_padrao(self) -> Dict[TipoNicho, ConfiguracaoNicho]:
        """Carrega configurações padrão para todos os nichos."""
        agora = datetime.now()
        
        return {
            TipoNicho.ECOMMERCE: ConfiguracaoNicho(
                nicho=TipoNicho.ECOMMERCE,
                nome_exibicao="E-commerce",
                descricao="Configuração otimizada para lojas online e vendas",
                min_palavras_significativas=3,
                max_palavras_significativas=8,
                threshold_especificidade=0.6,
                threshold_similaridade=0.7,
                peso_complexidade=0.25,
                peso_especificidade=0.30,
                peso_competitivo=0.30,
                peso_tendencia=0.15,
                score_minimo_aprovacao=0.65,
                threshold_volume_busca=50,
                threshold_cpc_minimo=0.5,
                threshold_cpc_maximo=8.0,
                threshold_concorrencia_maxima=0.8,
                palavras_chave_especificas=[
                    "preço", "barato", "promoção", "desconto", "oferta", "comprar",
                    "vender", "frete", "entrega", "garantia", "devolução", "pagamento"
                ],
                palavras_chave_negativas=[
                    "gratuito", "free", "sem custo", "não pago"
                ],
                peso_crescimento_volume=0.4,
                peso_novidade=0.3,
                peso_sazonalidade=0.3,
                timeout_analise=30,
                max_tentativas=3,
                cache_duracao=3600,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            ),
            
            TipoNicho.SAUDE: ConfiguracaoNicho(
                nicho=TipoNicho.SAUDE,
                nome_exibicao="Saúde",
                descricao="Configuração otimizada para saúde e bem-estar",
                min_palavras_significativas=4,
                max_palavras_significativas=10,
                threshold_especificidade=0.75,
                threshold_similaridade=0.8,
                peso_complexidade=0.35,
                peso_especificidade=0.30,
                peso_competitivo=0.20,
                peso_tendencia=0.15,
                score_minimo_aprovacao=0.75,
                threshold_volume_busca=30,
                threshold_cpc_minimo=1.0,
                threshold_cpc_maximo=15.0,
                threshold_concorrencia_maxima=0.7,
                palavras_chave_especificas=[
                    "sintomas", "tratamento", "medicamento", "consulta", "exame",
                    "diagnóstico", "prevenção", "cura", "alívio", "especialista",
                    "clínica", "hospital", "médico", "terapia"
                ],
                palavras_chave_negativas=[
                    "milagre", "cura definitiva", "100% eficaz"
                ],
                peso_crescimento_volume=0.3,
                peso_novidade=0.4,
                peso_sazonalidade=0.3,
                timeout_analise=45,
                max_tentativas=2,
                cache_duracao=7200,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            ),
            
            TipoNicho.TECNOLOGIA: ConfiguracaoNicho(
                nicho=TipoNicho.TECNOLOGIA,
                nome_exibicao="Tecnologia",
                descricao="Configuração otimizada para tecnologia e inovação",
                min_palavras_significativas=3,
                max_palavras_significativas=9,
                threshold_especificidade=0.7,
                threshold_similaridade=0.75,
                peso_complexidade=0.30,
                peso_especificidade=0.25,
                peso_competitivo=0.25,
                peso_tendencia=0.20,
                score_minimo_aprovacao=0.7,
                threshold_volume_busca=40,
                threshold_cpc_minimo=0.8,
                threshold_cpc_maximo=12.0,
                threshold_concorrencia_maxima=0.75,
                palavras_chave_especificas=[
                    "tutorial", "como fazer", "passo a passo", "dica", "truque",
                    "otimização", "configuração", "resolução", "problema", "solução",
                    "software", "hardware", "programação", "desenvolvimento"
                ],
                palavras_chave_negativas=[
                    "hack", "crack", "pirata", "ilegal"
                ],
                peso_crescimento_volume=0.35,
                peso_novidade=0.35,
                peso_sazonalidade=0.30,
                timeout_analise=35,
                max_tentativas=3,
                cache_duracao=5400,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            ),
            
            TipoNicho.EDUCACAO: ConfiguracaoNicho(
                nicho=TipoNicho.EDUCACAO,
                nome_exibicao="Educação",
                descricao="Configuração otimizada para educação e aprendizado",
                min_palavras_significativas=4,
                max_palavras_significativas=10,
                threshold_especificidade=0.8,
                threshold_similaridade=0.8,
                peso_complexidade=0.25,
                peso_especificidade=0.35,
                peso_competitivo=0.25,
                peso_tendencia=0.15,
                score_minimo_aprovacao=0.75,
                threshold_volume_busca=25,
                threshold_cpc_minimo=0.6,
                threshold_cpc_maximo=10.0,
                threshold_concorrencia_maxima=0.7,
                palavras_chave_especificas=[
                    "curso", "aprendizado", "estudo", "material", "exercício",
                    "prática", "revisão", "preparação", "técnica", "método",
                    "professor", "aula", "conteúdo", "certificação"
                ],
                palavras_chave_negativas=[
                    "diploma falso", "certificado falso"
                ],
                peso_crescimento_volume=0.25,
                peso_novidade=0.35,
                peso_sazonalidade=0.40,
                timeout_analise=40,
                max_tentativas=2,
                cache_duracao=7200,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            ),
            
            TipoNicho.FINANCAS: ConfiguracaoNicho(
                nicho=TipoNicho.FINANCAS,
                nome_exibicao="Finanças",
                descricao="Configuração otimizada para finanças e investimentos",
                min_palavras_significativas=4,
                max_palavras_significativas=9,
                threshold_especificidade=0.75,
                threshold_similaridade=0.8,
                peso_complexidade=0.30,
                peso_especificidade=0.25,
                peso_competitivo=0.30,
                peso_tendencia=0.15,
                score_minimo_aprovacao=0.75,
                threshold_volume_busca=35,
                threshold_cpc_minimo=1.2,
                threshold_cpc_maximo=20.0,
                threshold_concorrencia_maxima=0.75,
                palavras_chave_especificas=[
                    "investimento", "economia", "poupança", "rendimento", "risco",
                    "retorno", "planejamento", "orçamento", "dívida", "crédito",
                    "ações", "fundos", "seguros", "aposentadoria"
                ],
                palavras_chave_negativas=[
                    "get rich quick", "fique rico rápido", "garantia 100%"
                ],
                peso_crescimento_volume=0.30,
                peso_novidade=0.25,
                peso_sazonalidade=0.45,
                timeout_analise=50,
                max_tentativas=2,
                cache_duracao=9000,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            ),
            
            TipoNicho.GENERICO: ConfiguracaoNicho(
                nicho=TipoNicho.GENERICO,
                nome_exibicao="Genérico",
                descricao="Configuração padrão para nichos não identificados",
                min_palavras_significativas=3,
                max_palavras_significativas=8,
                threshold_especificidade=0.65,
                threshold_similaridade=0.7,
                peso_complexidade=0.30,
                peso_especificidade=0.25,
                peso_competitivo=0.25,
                peso_tendencia=0.20,
                score_minimo_aprovacao=0.7,
                threshold_volume_busca=50,
                threshold_cpc_minimo=0.5,
                threshold_cpc_maximo=10.0,
                threshold_concorrencia_maxima=0.8,
                palavras_chave_especificas=[],
                palavras_chave_negativas=[],
                peso_crescimento_volume=0.33,
                peso_novidade=0.33,
                peso_sazonalidade=0.34,
                timeout_analise=30,
                max_tentativas=3,
                cache_duracao=3600,
                criado_em=agora,
                atualizado_em=agora,
                versao="1.0",
                ativo=True
            )
        }
    
    def detectar_nicho(self, keyword: str, dados_adicionais: Optional[Dict[str, Any]] = None) -> TipoNicho:
        """
        Detecta automaticamente o nicho baseado na keyword e dados adicionais.
        
        Args:
            keyword: Keyword a ser analisada
            dados_adicionais: Dados adicionais para análise
            
        Returns:
            TipoNicho: Nicho detectado
        """
        try:
            keyword_lower = keyword.lower()
            scores_nicho = {}
            
            # Análise por palavras-chave específicas
            for nicho, config in self.configuracoes.items():
                if nicho == TipoNicho.GENERICO:
                    continue
                
                score = 0
                palavras_especificas = config.palavras_chave_especificas
                
                for palavra in palavras_especificas:
                    if palavra in keyword_lower:
                        score += 1
                
                # Normalização do score
                if palavras_especificas:
                    score_normalizado = score / len(palavras_especificas)
                    scores_nicho[nicho] = score_normalizado
            
            # Análise de dados adicionais se fornecidos
            if dados_adicionais:
                nicho_sugerido = dados_adicionais.get('nicho_sugerido')
                if nicho_sugerido:
                    try:
                        nicho_enum = TipoNicho(nicho_sugerido)
                        if nicho_enum in scores_nicho:
                            scores_nicho[nicho_enum] += 0.3  # Bônus
                    except ValueError:
                        pass
            
            # Seleção do nicho com maior score
            if scores_nicho:
                nicho_detectado = max(scores_nicho, key=scores_nicho.get)
                if scores_nicho[nicho_detectado] >= 0.2:  # Threshold mínimo
                    logger.info(f"[{self.tracing_id}] Nicho detectado: {nicho_detectado.value}")
                    return nicho_detectado
            
            # Fallback para genérico
            logger.info(f"[{self.tracing_id}] Nicho não detectado, usando genérico")
            return TipoNicho.GENERICO
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na detecção de nicho: {e}")
            return TipoNicho.GENERICO
    
    def obter_configuracao(self, nicho: Union[TipoNicho, str]) -> ConfiguracaoNicho:
        """
        Obtém configuração para um nicho específico.
        
        Args:
            nicho: Nicho ou string do nicho
            
        Returns:
            ConfiguracaoNicho: Configuração do nicho
        """
        try:
            if isinstance(nicho, str):
                nicho = TipoNicho(nicho)
            
            if nicho not in self.configuracoes:
                logger.warning(f"[{self.tracing_id}] Nicho {nicho.value} não encontrado, usando genérico")
                nicho = TipoNicho.GENERICO
            
            config = self.configuracoes[nicho]
            self.configuracao_atual = config
            
            logger.info(f"[{self.tracing_id}] Configuração carregada para nicho: {nicho.value}")
            return config
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao obter configuração: {e}")
            return self.configuracoes[TipoNicho.GENERICO]
    
    def configurar_automaticamente(self, keyword: str, dados_adicionais: Optional[Dict[str, Any]] = None) -> ConfiguracaoNicho:
        """
        Configura automaticamente baseado na detecção de nicho.
        
        Args:
            keyword: Keyword para análise
            dados_adicionais: Dados adicionais
            
        Returns:
            ConfiguracaoNicho: Configuração aplicada
        """
        try:
            nicho_detectado = self.detectar_nicho(keyword, dados_adicionais)
            configuracao = self.obter_configuracao(nicho_detectado)
            
            # Registro do ajuste
            ajuste = {
                "timestamp": datetime.now().isoformat(),
                "keyword": keyword,
                "nicho_detectado": nicho_detectado.value,
                "configuracao_aplicada": configuracao.nome_exibicao,
                "dados_adicionais": dados_adicionais
            }
            self.historico_ajustes.append(ajuste)
            
            logger.info(f"[{self.tracing_id}] Configuração automática aplicada: {configuracao.nome_exibicao}")
            return configuracao
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na configuração automática: {e}")
            return self.configuracoes[TipoNicho.GENERICO]
    
    def ajustar_parametros(self, nicho: TipoNicho, parametros: Dict[str, Any]) -> bool:
        """
        Ajusta parâmetros de um nicho específico.
        
        Args:
            nicho: Nicho a ser ajustado
            parametros: Novos parâmetros
            
        Returns:
            bool: True se ajustado com sucesso
        """
        try:
            if nicho not in self.configuracoes:
                logger.error(f"[{self.tracing_id}] Nicho {nicho.value} não encontrado")
                return False
            
            config_atual = self.configuracoes[nicho]
            
            # Validação dos parâmetros
            parametros_validos = self._validar_parametros(parametros)
            if not parametros_validos:
                return False
            
            # Aplicação dos ajustes
            for campo, valor in parametros_validos.items():
                if hasattr(config_atual, campo):
                    setattr(config_atual, campo, valor)
            
            # Atualização de metadados
            config_atual.atualizado_em = datetime.now()
            
            # Registro do ajuste
            ajuste = {
                "timestamp": datetime.now().isoformat(),
                "nicho": nicho.value,
                "parametros_ajustados": parametros_validos,
                "configuracao_anterior": asdict(self.configuracoes[nicho])
            }
            self.historico_ajustes.append(ajuste)
            
            logger.info(f"[{self.tracing_id}] Parâmetros ajustados para nicho {nicho.value}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao ajustar parâmetros: {e}")
            return False
    
    def _validar_parametros(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """Valida parâmetros antes da aplicação."""
        parametros_validos = {}
        
        # Validações específicas
        validacoes = {
            "min_palavras_significativas": lambda value: isinstance(value, int) and 1 <= value <= 10,
            "max_palavras_significativas": lambda value: isinstance(value, int) and 5 <= value <= 15,
            "threshold_especificidade": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "threshold_similaridade": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "peso_complexidade": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "peso_especificidade": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "peso_competitivo": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "peso_tendencia": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "score_minimo_aprovacao": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0,
            "threshold_volume_busca": lambda value: isinstance(value, int) and value >= 0,
            "threshold_cpc_minimo": lambda value: isinstance(value, float) and value >= 0,
            "threshold_cpc_maximo": lambda value: isinstance(value, float) and value >= 0,
            "threshold_concorrencia_maxima": lambda value: isinstance(value, float) and 0.0 <= value <= 1.0
        }
        
        for campo, valor in parametros.items():
            if campo in validacoes and validacoes[campo](valor):
                parametros_validos[campo] = valor
            else:
                logger.warning(f"[{self.tracing_id}] Parâmetro inválido ignorado: {campo}={valor}")
        
        return parametros_validos
    
    def salvar_configuracoes(self, arquivo_saida: str) -> bool:
        """
        Salva configurações em arquivo.
        
        Args:
            arquivo_saida: Caminho do arquivo de saída
            
        Returns:
            bool: True se salvo com sucesso
        """
        try:
            dados_para_salvar = {}
            
            for nicho, config in self.configuracoes.items():
                dados_config = asdict(config)
                # Converter datetime para string
                dados_config["criado_em"] = dados_config["criado_em"].isoformat()
                dados_config["atualizado_em"] = dados_config["atualizado_em"].isoformat()
                dados_para_salvar[nicho.value] = dados_config
            
            # Salvar como JSON
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[{self.tracing_id}] Configurações salvas em: {arquivo_saida}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao salvar configurações: {e}")
            return False
    
    def carregar_configuracoes(self, arquivo_entrada: str) -> bool:
        """
        Carrega configurações de arquivo.
        
        Args:
            arquivo_entrada: Caminho do arquivo de entrada
            
        Returns:
            bool: True se carregado com sucesso
        """
        try:
            with open(arquivo_entrada, 'r', encoding='utf-8') as f:
                dados_carregados = json.load(f)
            
            for nicho_str, dados_config in dados_carregados.items():
                try:
                    nicho = TipoNicho(nicho_str)
                    
                    # Converter strings de data para datetime
                    dados_config["criado_em"] = datetime.fromisoformat(dados_config["criado_em"])
                    dados_config["atualizado_em"] = datetime.fromisoformat(dados_config["atualizado_em"])
                    dados_config["nicho"] = nicho
                    
                    # Criar objeto de configuração
                    config = ConfiguracaoNicho(**dados_config)
                    self.configuracoes[nicho] = config
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"[{self.tracing_id}] Erro ao carregar nicho {nicho_str}: {e}")
            
            logger.info(f"[{self.tracing_id}] Configurações carregadas de: {arquivo_entrada}")
            return True
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao carregar configurações: {e}")
            return False
    
    def gerar_relatorio_configuracao(self) -> Dict[str, Any]:
        """
        Gera relatório das configurações atuais.
        
        Returns:
            Dict com relatório completo
        """
        try:
            relatorio = {
                "tracing_id": self.tracing_id,
                "timestamp": datetime.now().isoformat(),
                "configuracao_atual": None,
                "nichos_disponiveis": {},
                "historico_ajustes": self.historico_ajustes[-10:],  # Últimos 10 ajustes
                "estatisticas": {
                    "total_nichos": len(self.configuracoes),
                    "nichos_ativos": sum(1 for c in self.configuracoes.values() if c.ativo),
                    "total_ajustes": len(self.historico_ajustes)
                }
            }
            
            # Configuração atual
            if self.configuracao_atual:
                relatorio["configuracao_atual"] = {
                    "nicho": self.configuracao_atual.nicho.value,
                    "nome": self.configuracao_atual.nome_exibicao,
                    "descricao": self.configuracao_atual.descricao,
                    "versao": self.configuracao_atual.versao,
                    "ativo": self.configuracao_atual.ativo
                }
            
            # Nichos disponíveis
            for nicho, config in self.configuracoes.items():
                relatorio["nichos_disponiveis"][nicho.value] = {
                    "nome": config.nome_exibicao,
                    "descricao": config.descricao,
                    "ativo": config.ativo,
                    "versao": config.versao,
                    "parametros_principais": {
                        "score_minimo": config.score_minimo_aprovacao,
                        "threshold_especificidade": config.threshold_especificidade,
                        "peso_complexidade": config.peso_complexidade,
                        "peso_especificidade": config.peso_especificidade
                    }
                }
            
            logger.info(f"[{self.tracing_id}] Relatório de configuração gerado")
            return relatorio
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {e}")
            raise

# Funções de conveniência
def configurar_automaticamente(
    keyword: str, 
    dados_adicionais: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None
) -> ConfiguracaoNicho:
    """
    Função de conveniência para configuração automática.
    
    Args:
        keyword: Keyword para análise
        dados_adicionais: Dados adicionais
        config_path: Caminho para configuração
        
    Returns:
        ConfiguracaoNicho: Configuração aplicada
    """
    sistema = ConfiguracaoAdaptativa(config_path)
    return sistema.configurar_automaticamente(keyword, dados_adicionais)

def obter_configuracao_nicho(
    nicho: Union[TipoNicho, str],
    config_path: Optional[str] = None
) -> ConfiguracaoNicho:
    """
    Função de conveniência para obter configuração de nicho.
    
    Args:
        nicho: Nicho desejado
        config_path: Caminho para configuração
        
    Returns:
        ConfiguracaoNicho: Configuração do nicho
    """
    sistema = ConfiguracaoAdaptativa(config_path)
    return sistema.obter_configuracao(nicho)

if __name__ == "__main__":
    # Teste básico do sistema de configuração adaptativa
    sistema = ConfiguracaoAdaptativa()
    
    # Keywords de teste
    keywords_teste = [
        "melhor preço notebook gaming 2024",
        "sintomas de diabetes tipo 2 em adultos",
        "tutorial python para iniciantes",
        "curso online marketing digital certificado",
        "investimento em criptomoedas para iniciantes"
    ]
    
    print("=== TESTE DO SISTEMA DE CONFIGURAÇÃO ADAPTATIVA ===")
    for keyword in keywords_teste:
        config = sistema.configurar_automaticamente(keyword)
        print(f"\nKeyword: {keyword}")
        print(f"Nicho detectado: {config.nicho.value}")
        print(f"Configuração: {config.nome_exibicao}")
        print(f"Score mínimo: {config.score_minimo_aprovacao}")
        print(f"Threshold especificidade: {config.threshold_especificidade}")
        print(f"Pesos - Complexidade: {config.peso_complexidade}, Especificidade: {config.peso_especificidade}")
    
    # Gerar relatório
    relatorio = sistema.gerar_relatorio_configuracao()
    print(f"\n=== RELATÓRIO ===")
    print(f"Total de nichos: {relatorio['estatisticas']['total_nichos']}")
    print(f"Nichos ativos: {relatorio['estatisticas']['nichos_ativos']}")
    print(f"Total de ajustes: {relatorio['estatisticas']['total_ajustes']}") 