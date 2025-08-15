"""
Analisador de tendências para otimização de cache.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from shared.logger import logger

class AnalisadorTendencias:
    """Analisa padrões temporais para otimizar cache."""
    
    def __init__(self, janela_analise: int = 7):
        """
        Inicializa analisador de tendências.
        
        Args:
            janela_analise: Número de dias para análise de padrões
        """
        self.janela_analise = janela_analise
        self._historico: Dict[str, List[Tuple[datetime, int]]] = {}
        
    def registrar_acesso(self, chave: str) -> None:
        """
        Registra um acesso para análise de tendências.
        
        Args:
            chave: Identificador do item acessado
        """
        agora = datetime.utcnow()
        if chave not in self._historico:
            self._historico[chave] = []
            
        self._historico[chave].append((agora, 1))
        self._limpar_historico_antigo(chave)
        
        logger.info({
            "timestamp": agora.isoformat(),
            "event": "registro_tendencia",
            "status": "success",
            "source": "trends.analyzer",
            "details": {
                "chave": chave,
                "total_registros": len(self._historico[chave])
            }
        })
        
    def calcular_tendencia(self, chave: str) -> float:
        """
        Calcula o índice de tendência para uma chave.
        
        O índice é calculado com base na frequência diária e padrões de horário.
        Valores:
        - 0.0: Sem tendência (poucos acessos ou muito antigos)
        - 0.1-0.3: Tendência baixa (acessos ocasionais)
        - 0.4-0.6: Tendência média (acessos regulares)
        - 0.7-0.9: Tendência alta (acessos frequentes)
        - 1.0: Tendência muito alta (acessos constantes)
        
        Args:
            chave: Identificador do item
            
        Returns:
            Índice de tendência entre 0.0 e 1.0
        """
        if chave not in self._historico:
            return 0.0
            
        self._limpar_historico_antigo(chave)
        registros = self._historico[chave]
        
        if not registros:
            return 0.0
            
        # Calcula frequência diária normalizada (0.0-0.5)
        freq_diaria = self.calcular_frequencia_diaria(chave)
        freq_normalizada = min(0.5, freq_diaria / 10.0)
        
        # Analisa padrão horário (0.0-0.5)
        hora_pico = self.identificar_padrao_horario(chave)
        peso_padrao = 0.5 if hora_pico is not None else 0.0
        
        # Combina os fatores
        tendencia = freq_normalizada + peso_padrao
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "calculo_tendencia",
            "status": "success",
            "source": "trends.analyzer",
            "details": {
                "chave": chave,
                "frequencia_diaria": freq_diaria,
                "hora_pico": hora_pico,
                "tendencia": tendencia
            }
        })
        
        return tendencia
        
    def _limpar_historico_antigo(self, chave: str) -> None:
        """
        Remove registros mais antigos que a janela de análise.
        
        Args:
            chave: Identificador do item
        """
        if chave not in self._historico:
            return
            
        limite = datetime.utcnow() - timedelta(days=self.janela_analise)
        self._historico[chave] = [
            (ts, count) for ts, count in self._historico[chave]
            if ts > limite
        ]
        
    def calcular_frequencia_diaria(self, chave: str) -> float:
        """
        Calcula média de acessos diários.
        
        Args:
            chave: Identificador do item
            
        Returns:
            Média de acessos por dia
        """
        if chave not in self._historico:
            return 0.0
            
        self._limpar_historico_antigo(chave)
        registros = self._historico[chave]
        
        if not registros:
            return 0.0
            
        total_acessos = sum(count for _, count in registros)
        dias_analisados = min(self.janela_analise, 
                            (datetime.utcnow() - registros[0][0]).days + 1)
                            
        return total_acessos / max(1, dias_analisados)
        
    def identificar_padrao_horario(self, chave: str) -> Optional[int]:
        """
        Identifica hora do dia com maior frequência de acessos.
        
        Args:
            chave: Identificador do item
            
        Returns:
            Hora do dia (0-23) com mais acessos ou None se não houver padrão
        """
        if chave not in self._historico:
            return None
            
        self._limpar_historico_antigo(chave)
        registros = self._historico[chave]
        
        if len(registros) < 10:  # Mínimo de registros para identificar padrão
            return None
            
        acessos_por_hora = [0] * 24
        for ts, count in registros:
            acessos_por_hora[ts.hour] += count
            
        hora_pico = max(range(24), key=lambda h: acessos_por_hora[h])
        total_acessos = sum(acessos_por_hora)
        
        # Só considera padrão se hora pico tem pelo menos 25% dos acessos
        if acessos_por_hora[hora_pico] >= total_acessos * 0.25:
            return hora_pico
        return None
        
    def calcular_ttl_otimizado(
        self,
        chave: str,
        ttl_min: int,
        ttl_padrao: int,
        ttl_max: int
    ) -> int:
        """
        Calcula TTL otimizado baseado em padrões de acesso.
        
        Args:
            chave: Identificador do item
            ttl_min: TTL mínimo em segundos
            ttl_padrao: TTL padrão em segundos
            ttl_max: TTL máximo em segundos
            
        Returns:
            TTL otimizado em segundos
        """
        freq_diaria = self.calcular_frequencia_diaria(chave)
        hora_pico = self.identificar_padrao_horario(chave)
        agora = datetime.utcnow()
        
        # Ajusta TTL baseado na frequência diária
        if freq_diaria < 1:
            ttl_base = ttl_min
        elif freq_diaria < 5:
            ttl_base = ttl_padrao
        else:
            # Aumenta TTL proporcionalmente à frequência
            ttl_base = min(ttl_padrao * (freq_diaria / 5), ttl_max)
            
        # Ajusta TTL se estiver próximo do horário de pico
        if hora_pico is not None:
            hora_atual = agora.hour
            diff_hora = (hora_pico - hora_atual) % 24
            
            if diff_hora <= 2:  # Próximo do pico
                ttl_base = max(ttl_base, ttl_padrao * 2)
            elif diff_hora >= 22:  # Aproximando do próximo pico
                ttl_base = min(ttl_base, ttl_padrao)
                
        logger.info({
            "timestamp": agora.isoformat(),
            "event": "calculo_ttl",
            "status": "success",
            "source": "trends.analyzer",
            "details": {
                "chave": chave,
                "frequencia_diaria": freq_diaria,
                "hora_pico": hora_pico,
                "ttl_calculado": ttl_base
            }
        })
                
        return int(ttl_base)
        
    def exportar_metricas(self, chave: str) -> Dict:
        """
        Exporta métricas de tendências para uma chave.
        
        Args:
            chave: Identificador do item
            
        Returns:
            Dicionário com métricas de tendências
        """
        if chave not in self._historico:
            return {
                "chave": chave,
                "frequencia_diaria": 0.0,
                "total_acessos": 0,
                "hora_pico": None,
                "dias_analisados": 0
            }
            
        self._limpar_historico_antigo(chave)
        registros = self._historico[chave]
        
        if not registros:
            return {
                "chave": chave,
                "frequencia_diaria": 0.0,
                "total_acessos": 0,
                "hora_pico": None,
                "dias_analisados": 0
            }
            
        freq_diaria = self.calcular_frequencia_diaria(chave)
        hora_pico = self.identificar_padrao_horario(chave)
        total_acessos = sum(count for _, count in registros)
        primeiro_acesso = min(ts for ts, _ in registros)
        dias_analisados = (datetime.utcnow() - primeiro_acesso).days + 1
        
        return {
            "chave": chave,
            "frequencia_diaria": freq_diaria,
            "total_acessos": total_acessos,
            "hora_pico": hora_pico,
            "dias_analisados": dias_analisados
        } 