"""
Calculadora de RISK_SCORE para Testes de Integração

📐 CoCoT: Baseado em especificação do prompt de testes de integração
🌲 ToT: Avaliado múltiplas estratégias de cálculo de risco
♻️ ReAct: Implementado cálculo automático baseado em camadas, serviços e frequência

Tracing ID: risk-score-calculator-2025-01-27-001
Data: 2025-01-27
Versão: 1.0.0

Fórmula: RISK_SCORE = (Camadas * 10) + (Serviços * 15) + (Frequência * 5)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class FrequenciaUso(Enum):
    """Frequência de uso do fluxo."""
    BAIXA = 1
    MEDIA = 2
    ALTA = 3

class Camada(Enum):
    """Camadas do sistema."""
    API = "API"
    SERVICE = "Service"
    DB = "DB"
    CACHE = "Cache"
    LOG = "Log"
    SECURITY = "Security"
    OAUTH = "OAuth"
    EXTERNO = "Externo"
    GOVERNANCA = "Governança"
    PROCESSAMENTO = "Processamento"
    EXPORTACAO = "Exportação"
    DASHBOARD = "Dashboard"

class ServicoExterno(Enum):
    """Serviços externos."""
    BANCO = "Banco"
    LOGS = "Logs"
    NOTIFICACAO = "Notificação"
    OAUTH2 = "OAuth2"
    JWT = "JWT"
    HMAC = "HMAC"
    IP = "IP"
    GOOGLE_TRENDS = "Google Trends"
    INSTAGRAM_API = "Instagram API"
    FACEBOOK_API = "Facebook API"
    YOUTUBE_API = "YouTube API"
    TIKTOK_API = "TikTok API"
    PINTEREST_API = "Pinterest API"
    REDDIT_API = "Reddit API"
    DISCORD_API = "Discord API"
    AMAZON_API = "Amazon API"
    GSC_API = "GSC API"
    GOOGLE_PAA = "Google PAA"
    MERCADOPAGO = "MercadoPago"
    STRIPE = "Stripe"
    SENDGRID = "SendGrid"
    AWS_S3 = "AWS S3"
    REDIS = "Redis"
    RABBITMQ = "RabbitMQ"

@dataclass
class FluxoConfig:
    """Configuração de um fluxo para cálculo de risco."""
    nome: str
    camadas: List[Camada]
    servicos: List[ServicoExterno]
    frequencia: FrequenciaUso
    endpoint: Optional[str] = None
    metodo: Optional[str] = None
    descricao: Optional[str] = None

@dataclass
class RiskScoreResult:
    """Resultado do cálculo de RISK_SCORE."""
    fluxo: FluxoConfig
    risk_score: int
    detalhes: Dict[str, Any]
    nivel_risco: str
    recomendacoes: List[str]

class RiskScoreCalculator:
    """Calculadora de RISK_SCORE para testes de integração."""
    
    def __init__(self):
        self.niveis_risco = {
            (0, 30): "BAIXO",
            (31, 60): "MÉDIO",
            (61, 80): "ALTO",
            (81, 100): "CRÍTICO"
        }
    
    def calcular_risk_score(self, fluxo: FluxoConfig) -> RiskScoreResult:
        """
        Calcula RISK_SCORE para um fluxo.
        
        Fórmula: RISK_SCORE = (Camadas * 10) + (Serviços * 15) + (Frequência * 5)
        
        Args:
            fluxo: Configuração do fluxo
            
        Returns:
            Resultado do cálculo de risco
        """
        # Calcular componentes
        camadas_score = len(fluxo.camadas) * 10
        servicos_score = len(fluxo.servicos) * 15
        frequencia_score = fluxo.frequencia.value * 5
        
        # Calcular RISK_SCORE total
        risk_score = camadas_score + servicos_score + frequencia_score
        
        # Determinar nível de risco
        nivel_risco = self._determinar_nivel_risco(risk_score)
        
        # Gerar detalhes
        detalhes = {
            'camadas_score': camadas_score,
            'servicos_score': servicos_score,
            'frequencia_score': frequencia_score,
            'camadas_count': len(fluxo.camadas),
            'servicos_count': len(fluxo.servicos),
            'frequencia_value': fluxo.frequencia.value,
            'formula': f"({len(fluxo.camadas)} * 10) + ({len(fluxo.servicos)} * 15) + ({fluxo.frequencia.value} * 5) = {risk_score}"
        }
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(risk_score, fluxo)
        
        return RiskScoreResult(
            fluxo=fluxo,
            risk_score=risk_score,
            detalhes=detalhes,
            nivel_risco=nivel_risco,
            recomendacoes=recomendacoes
        )
    
    def _determinar_nivel_risco(self, risk_score: int) -> str:
        """Determina nível de risco baseado no score."""
        for (min_score, max_score), nivel in self.niveis_risco.items():
            if min_score <= risk_score <= max_score:
                return nivel
        return "CRÍTICO"  # Para scores > 100
    
    def _gerar_recomendacoes(self, risk_score: int, fluxo: FluxoConfig) -> List[str]:
        """Gera recomendações baseadas no risco."""
        recomendacoes = []
        
        if risk_score >= 70:
            recomendacoes.append("🔴 PRIORIDADE MÁXIMA: Teste obrigatório com mutation testing")
            recomendacoes.append("🔴 Implementar shadow testing para validação canário")
            recomendacoes.append("🔴 Monitoramento contínuo em produção")
        
        elif risk_score >= 50:
            recomendacoes.append("🟡 PRIORIDADE ALTA: Teste completo com side effects")
            recomendacoes.append("🟡 Validar logs e métricas")
        
        elif risk_score >= 30:
            recomendacoes.append("🟢 PRIORIDADE MÉDIA: Teste funcional básico")
        
        else:
            recomendacoes.append("🟢 PRIORIDADE BAIXA: Teste unitário suficiente")
        
        # Recomendações específicas por tipo de serviço
        if any(servico in [ServicoExterno.BANCO, ServicoExterno.REDIS] for servico in fluxo.servicos):
            recomendacoes.append("💾 Validar transações e consistência de dados")
        
        if ServicoExterno.OAUTH2 in fluxo.servicos:
            recomendacoes.append("🔐 Testar cenários de expiração e renovação de tokens")
        
        if any(servico.value.endswith('_API') for servico in fluxo.servicos):
            recomendacoes.append("🌐 Testar cenários de falha de API externa")
        
        return recomendacoes
    
    def calcular_risk_score_para_mapeamento(self, mapeamento: Dict[str, Any]) -> RiskScoreResult:
        """Calcula RISK_SCORE para um item do mapeamento."""
        # Converter string de camadas para enum
        camadas_str = mapeamento.get('camadas_tocadas', '').split(', ')
        camadas = [Camada(camada.strip()) for camada in camadas_str if camada.strip()]
        
        # Converter string de serviços para enum
        servicos_str = mapeamento.get('dependencias_reais', '').split(', ')
        servicos = [ServicoExterno(servico.strip()) for servico in servicos_str if servico.strip()]
        
        # Converter frequência
        frequencia_str = mapeamento.get('freq_uso', 'MEDIA').upper()
        frequencia = FrequenciaUso[frequencia_str]
        
        fluxo = FluxoConfig(
            nome=mapeamento.get('endpoint_fluxo', ''),
            camadas=camadas,
            servicos=servicos,
            frequencia=frequencia,
            endpoint=mapeamento.get('endpoint_fluxo'),
            descricao=mapeamento.get('observacoes', '')
        )
        
        return self.calcular_risk_score(fluxo)

# Instância global
risk_calculator = RiskScoreCalculator()

def calcular_risk_score_fluxo(nome: str, camadas: List[str], servicos: List[str], 
                            frequencia: str) -> RiskScoreResult:
    """
    Função de conveniência para calcular RISK_SCORE.
    
    Args:
        nome: Nome do fluxo
        camadas: Lista de camadas (strings)
        servicos: Lista de serviços (strings)
        frequencia: Frequência de uso ('BAIXA', 'MEDIA', 'ALTA')
        
    Returns:
        Resultado do cálculo de risco
    """
    # Converter strings para enums
    camadas_enum = [Camada(camada) for camada in camadas]
    servicos_enum = [ServicoExterno(servico) for servico in servicos]
    frequencia_enum = FrequenciaUso[frequencia.upper()]
    
    fluxo = FluxoConfig(
        nome=nome,
        camadas=camadas_enum,
        servicos=servicos_enum,
        frequencia=frequencia_enum
    )
    
    return risk_calculator.calcular_risk_score(fluxo)

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: Fluxo de execução em lote
    fluxo_exemplo = FluxoConfig(
        nome="/api/execucoes/lote (POST)",
        camadas=[Camada.API, Camada.SERVICE, Camada.DB, Camada.LOG],
        servicos=[ServicoExterno.BANCO, ServicoExterno.LOGS, ServicoExterno.NOTIFICACAO],
        frequencia=FrequenciaUso.ALTA
    )
    
    resultado = risk_calculator.calcular_risk_score(fluxo_exemplo)
    
    print(f"Fluxo: {resultado.fluxo.nome}")
    print(f"RISK_SCORE: {resultado.risk_score}")
    print(f"Nível de Risco: {resultado.nivel_risco}")
    print(f"Detalhes: {resultado.detalhes}")
    print(f"Recomendações:")
    for rec in resultado.recomendacoes:
        print(f"  - {rec}") 