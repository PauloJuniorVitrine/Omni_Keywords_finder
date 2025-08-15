"""
Serviço de Agendamento - Omni Keywords Finder
Agendamento de execuções automáticas e recorrentes

Prompt: Implementação de serviço de agendamento
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from croniter import croniter
import sqlite3
import os

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

logger = logging.getLogger(__name__)

class AgendamentoStatus(Enum):
    """Status do agendamento"""
    ATIVO = "ativo"
    PAUSADO = "pausado"
    CANCELADO = "cancelado"
    EXECUTANDO = "executando"

class TipoRecorrencia(Enum):
    """Tipos de recorrência"""
    UMA_VEZ = "uma_vez"
    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    CRON = "cron"

@dataclass
class AgendamentoConfig:
    """Configuração do agendamento"""
    nome: str
    descricao: str
    tipo_recorrencia: TipoRecorrencia
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    hora_execucao: str = "09:00"  # HH:MM
    dias_semana: List[int] = None  # 0=Segunda, 6=Domingo
    dia_mes: Optional[int] = None  # 1-31
    cron_expression: Optional[str] = None
    max_execucoes: Optional[int] = None
    timeout_minutos: int = 30
    retry_on_failure: bool = True
    max_retries: int = 3
    notificar_erro: bool = True

@dataclass
class ExecucaoAgendada:
    """Execução agendada"""
    id: str
    agendamento_id: str
    categoria_id: int
    palavras_chave: List[str]
    cluster: Optional[str] = None
    parametros_extras: Dict[str, Any] = None

@dataclass
class Agendamento:
    """Agendamento"""
    id: str
    config: AgendamentoConfig
    execucoes: List[ExecucaoAgendada]
    status: AgendamentoStatus
    user_id: str
    criado_em: datetime
    proxima_execucao: Optional[datetime] = None
    ultima_execucao: Optional[datetime] = None
    total_execucoes: int = 0
    execucoes_sucesso: int = 0
    execucoes_falha: int = 0

class AgendamentoService:
    """Serviço de agendamento"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agendamentos = {}  # agendamento_id -> Agendamento
        self.db_path = self.config.get('db_path', 'agendamentos.db')
        self.scheduler_thread = None
        self.running = False
        
        # Callbacks
        self.on_execucao_agendada: Optional[Callable] = None
        self.on_agendamento_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Inicializar banco de dados
        self._init_database()
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para agendamentos
        self.scheduler_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="scheduler_service",
                fallback_function=self._fallback_scheduler_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=10,
            max_wait_duration=10.0,
            max_failure_count=3,
            name="scheduler_service"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=60.0,
            name="scheduler_service"
        )

    def _fallback_scheduler_error(self, *args, **kwargs):
        """Fallback quando agendamento falha"""
        logger.warning("Agendamento falhou, usando fallback")
        return {"error": "Agendamento indisponível", "fallback": True}
        
        # Carregar agendamentos salvos
        self._load_agendamentos()
        
        # Iniciar scheduler
        self.start_scheduler()
    
    def _init_database(self):
        """Inicializa banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de agendamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                tipo_recorrencia TEXT NOT NULL,
                data_inicio TEXT NOT NULL,
                data_fim TEXT,
                hora_execucao TEXT NOT NULL,
                dias_semana TEXT,
                dia_mes INTEGER,
                cron_expression TEXT,
                max_execucoes INTEGER,
                timeout_minutos INTEGER DEFAULT 30,
                retry_on_failure BOOLEAN DEFAULT 1,
                max_retries INTEGER DEFAULT 3,
                notificar_erro BOOLEAN DEFAULT 1,
                status TEXT NOT NULL,
                user_id TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                proxima_execucao TEXT,
                ultima_execucao TEXT,
                total_execucoes INTEGER DEFAULT 0,
                execucoes_sucesso INTEGER DEFAULT 0,
                execucoes_falha INTEGER DEFAULT 0
            )
        ''')
        
        # Tabela de execuções agendadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execucoes_agendadas (
                id TEXT PRIMARY KEY,
                agendamento_id TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                palavras_chave TEXT NOT NULL,
                cluster TEXT,
                parametros_extras TEXT,
                FOREIGN KEY (agendamento_id) REFERENCES agendamentos (id)
            )
        ''')
        
        # Tabela de histórico de execuções
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_execucoes (
                id TEXT PRIMARY KEY,
                agendamento_id TEXT NOT NULL,
                data_execucao TEXT NOT NULL,
                status TEXT NOT NULL,
                resultado TEXT,
                erro TEXT,
                tempo_execucao REAL,
                FOREIGN KEY (agendamento_id) REFERENCES agendamentos (id)
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proxima_execucao ON agendamentos(proxima_execucao)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON agendamentos(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON agendamentos(user_id)')
        
        conn.commit()
        conn.close()
    
    def _load_agendamentos(self):
        """Carrega agendamentos do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Carregar agendamentos
        cursor.execute('SELECT * FROM agendamentos WHERE status != ?', ('cancelado',))
        agendamentos_data = cursor.fetchall()
        
        for row in agendamentos_data:
            agendamento = self._row_to_agendamento(row)
            if agendamento:
                self.agendamentos[agendamento.id] = agendamento
        
        # Carregar execuções agendadas
        for agendamento in self.agendamentos.values():
            cursor.execute('SELECT * FROM execucoes_agendadas WHERE agendamento_id = ?', (agendamento.id,))
            execucoes_data = cursor.fetchall()
            
            for row in execucoes_data:
                execucao = self._row_to_execucao_agendada(row)
                if execucao:
                    agendamento.execucoes.append(execucao)
        
        conn.close()
        logger.info(f"Carregados {len(self.agendamentos)} agendamentos")
    
    def _row_to_agendamento(self, row) -> Optional[Agendamento]:
        """Converte linha do banco para objeto Agendamento"""
        try:
            config = AgendamentoConfig(
                nome=row[1],
                descricao=row[2] or '',
                tipo_recorrencia=TipoRecorrencia(row[3]),
                data_inicio=datetime.fromisoformat(row[4]),
                data_fim=datetime.fromisoformat(row[5]) if row[5] else None,
                hora_execucao=row[6],
                dias_semana=json.loads(row[7]) if row[7] else None,
                dia_mes=row[8],
                cron_expression=row[9],
                max_execucoes=row[10],
                timeout_minutos=row[11] or 30,
                retry_on_failure=bool(row[12]),
                max_retries=row[13] or 3,
                notificar_erro=bool(row[14])
            )
            
            return Agendamento(
                id=row[0],
                config=config,
                execucoes=[],
                status=AgendamentoStatus(row[15]),
                user_id=row[16],
                criado_em=datetime.fromisoformat(row[17]),
                proxima_execucao=datetime.fromisoformat(row[18]) if row[18] else None,
                ultima_execucao=datetime.fromisoformat(row[19]) if row[19] else None,
                total_execucoes=row[20] or 0,
                execucoes_sucesso=row[21] or 0,
                execucoes_falha=row[22] or 0
            )
        except Exception as e:
            logger.error(f"Erro ao converter linha para agendamento: {str(e)}")
            return None
    
    def _row_to_execucao_agendada(self, row) -> Optional[ExecucaoAgendada]:
        """Converte linha do banco para objeto ExecucaoAgendada"""
        try:
            return ExecucaoAgendada(
                id=row[0],
                agendamento_id=row[1],
                categoria_id=row[2],
                palavras_chave=json.loads(row[3]),
                cluster=row[4],
                parametros_extras=json.loads(row[5]) if row[5] else {}
            )
        except Exception as e:
            logger.error(f"Erro ao converter linha para execução agendada: {str(e)}")
            return None
    
    def start_scheduler(self):
        """Inicia thread do scheduler"""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self.scheduler_thread.start()
            logger.info("Scheduler de agendamentos iniciado")
    
    def stop_scheduler(self):
        """Para o scheduler"""
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler de agendamentos parado")
    
    def _scheduler_loop(self):
        """Loop principal do scheduler"""
        while self.running:
            try:
                now = datetime.now(timezone.utc)
                
                # Verificar agendamentos para execução
                for agendamento in self.agendamentos.values():
                    if (agendamento.status == AgendamentoStatus.ATIVO and
                        agendamento.proxima_execucao and
                        agendamento.proxima_execucao <= now):
                        
                        # Executar agendamento
                        self._executar_agendamento(agendamento)
                
                # Aguardar próximo check
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no scheduler: {str(e)}")
                if self.on_error:
                    self.on_error(e)
    
    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=10, max_wait_duration=10.0)
    @timeout(timeout_seconds=60.0)
    def _executar_agendamento(self, agendamento: Agendamento):
        """Executa um agendamento com padrões de resiliência"""
        try:
            logger.info(f"Executando agendamento: {agendamento.id}")
            
            # Atualizar status
            agendamento.status = AgendamentoStatus.EXECUTANDO
            agendamento.ultima_execucao = datetime.now(timezone.utc)
            agendamento.total_execucoes += 1
            
            # Executar todas as execuções do agendamento
            sucessos = 0
            falhas = 0
            
            for execucao in agendamento.execucoes:
                try:
                    # Chamar callback de execução
                    if self.on_execucao_agendada:
                        resultado = self.on_execucao_agendada(execucao)
                        if resultado:
                            sucessos += 1
                        else:
                            falhas += 1
                    else:
                        # Execução simulada
                        time.sleep(2)
                        sucessos += 1
                    
                except Exception as e:
                    falhas += 1
                    logger.error(f"Erro na execução {execucao.id}: {str(e)}")
                    
                    # Registrar no histórico
                    self._registrar_execucao_historico(agendamento.id, False, None, str(e))
            
            # Atualizar estatísticas
            agendamento.execucoes_sucesso += sucessos
            agendamento.execucoes_falha += falhas
            
            # Verificar se deve continuar
            if self._deve_continuar_agendamento(agendamento):
                # Calcular próxima execução
                proxima = self._calcular_proxima_execucao(agendamento)
                agendamento.proxima_execucao = proxima
                agendamento.status = AgendamentoStatus.ATIVO
            else:
                # Finalizar agendamento
                agendamento.status = AgendamentoStatus.CANCELADO
                agendamento.proxima_execucao = None
            
            # Salvar no banco
            self._save_agendamento(agendamento)
            
            # Callback de conclusão
            if self.on_agendamento_complete:
                self.on_agendamento_complete(agendamento, sucessos, falhas)
            
            logger.info(f"Agendamento concluído: {agendamento.id} - Sucessos: {sucessos}, Falhas: {falhas}")
            
        except Exception as e:
            logger.error(f"Erro na execução do agendamento {agendamento.id}: {str(e)}")
            agendamento.status = AgendamentoStatus.ATIVO
            self._save_agendamento(agendamento)
            
            if self.on_error:
                self.on_error(e)
    
    def _deve_continuar_agendamento(self, agendamento: Agendamento) -> bool:
        """Verifica se agendamento deve continuar"""
        config = agendamento.config
        
        # Verificar data fim
        if config.data_fim and datetime.now(timezone.utc) >= config.data_fim:
            return False
        
        # Verificar máximo de execuções
        if config.max_execucoes and agendamento.total_execucoes >= config.max_execucoes:
            return False
        
        # Verificar tipo de recorrência
        if config.tipo_recorrencia == TipoRecorrencia.UMA_VEZ:
            return False
        
        return True
    
    def _calcular_proxima_execucao(self, agendamento: Agendamento) -> Optional[datetime]:
        """Calcula próxima execução baseada na configuração"""
        config = agendamento.config
        now = datetime.now(timezone.utc)
        
        if config.tipo_recorrencia == TipoRecorrencia.UMA_VEZ:
            return None
        
        elif config.tipo_recorrencia == TipoRecorrencia.DIARIA:
            # Próximo dia na hora especificada
            hora, minuto = map(int, config.hora_execucao.split(':'))
            proxima = now.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            if proxima <= now:
                proxima += timedelta(days=1)
            return proxima
        
        elif config.tipo_recorrencia == TipoRecorrencia.SEMANAL:
            # Próximo dia da semana na hora especificada
            if not config.dias_semana:
                return None
            
            hora, minuto = map(int, config.hora_execucao.split(':'))
            proxima = None
            
            for dia_semana in config.dias_semana:
                # Calcular próximo dia da semana
                dias_ate_proximo = (dia_semana - now.weekday()) % 7
                if dias_ate_proximo == 0 and now.hour >= hora and now.minute >= minuto:
                    dias_ate_proximo = 7
                
                candidato = now.replace(hour=hora, minute=minuto, second=0, microsecond=0) + timedelta(days=dias_ate_proximo)
                
                if proxima is None or candidato < proxima:
                    proxima = candidato
            
            return proxima
        
        elif config.tipo_recorrencia == TipoRecorrencia.MENSAL:
            # Próximo dia do mês na hora especificada
            if not config.dia_mes:
                return None
            
            hora, minuto = map(int, config.hora_execucao.split(':'))
            
            # Próximo mês
            if now.day >= config.dia_mes:
                # Próximo mês
                if now.month == 12:
                    proxima = now.replace(year=now.year + 1, month=1, day=config.dia_mes, hour=hora, minute=minuto, second=0, microsecond=0)
                else:
                    proxima = now.replace(month=now.month + 1, day=config.dia_mes, hour=hora, minute=minuto, second=0, microsecond=0)
            else:
                # Mesmo mês
                proxima = now.replace(day=config.dia_mes, hour=hora, minute=minuto, second=0, microsecond=0)
            
            return proxima
        
        elif config.tipo_recorrencia == TipoRecorrencia.CRON:
            # Usar expressão cron
            if not config.cron_expression:
                return None
            
            cron = croniter(config.cron_expression, now)
            return cron.get_next(datetime)
        
        return None
    
    def criar_agendamento(
        self,
        config: AgendamentoConfig,
        execucoes: List[Dict[str, Any]],
        user_id: str
    ) -> str:
        """Cria um novo agendamento"""
        agendamento_id = str(uuid.uuid4())
        
        # Criar execuções agendadas
        execucoes_agendadas = []
        for exec_data in execucoes:
            execucao = ExecucaoAgendada(
                id=str(uuid.uuid4()),
                agendamento_id=agendamento_id,
                categoria_id=exec_data['categoria_id'],
                palavras_chave=exec_data['palavras_chave'],
                cluster=exec_data.get('cluster'),
                parametros_extras=exec_data.get('parametros_extras', {})
            )
            execucoes_agendadas.append(execucao)
        
        # Calcular primeira execução
        proxima_execucao = self._calcular_proxima_execucao_para_config(config)
        
        # Criar agendamento
        agendamento = Agendamento(
            id=agendamento_id,
            config=config,
            execucoes=execucoes_agendadas,
            status=AgendamentoStatus.ATIVO,
            user_id=user_id,
            criado_em=datetime.now(timezone.utc),
            proxima_execucao=proxima_execucao
        )
        
        # Salvar no banco
        self._save_agendamento(agendamento)
        
        # Adicionar à memória
        self.agendamentos[agendamento_id] = agendamento
        
        logger.info(f"Agendamento criado: {agendamento_id} - Próxima execução: {proxima_execucao}")
        return agendamento_id
    
    def _calcular_proxima_execucao_para_config(self, config: AgendamentoConfig) -> Optional[datetime]:
        """Calcula próxima execução para uma configuração"""
        now = datetime.now(timezone.utc)
        
        if config.data_inicio > now:
            # Primeira execução no futuro
            return self._calcular_proxima_execucao_apos_data(config, config.data_inicio)
        else:
            # Primeira execução já passou, calcular próxima
            return self._calcular_proxima_execucao_apos_data(config, now)
    
    def _calcular_proxima_execucao_apos_data(self, config: AgendamentoConfig, data_base: datetime) -> Optional[datetime]:
        """Calcula próxima execução após uma data específica"""
        if config.tipo_recorrencia == TipoRecorrencia.UMA_VEZ:
            return config.data_inicio if config.data_inicio > data_base else None
        
        # Usar lógica similar ao _calcular_proxima_execucao mas com data_base
        hora, minuto = map(int, config.hora_execucao.split(':'))
        
        if config.tipo_recorrencia == TipoRecorrencia.DIARIA:
            proxima = data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            if proxima <= data_base:
                proxima += timedelta(days=1)
            return proxima
        
        # Implementar outros tipos conforme necessário
        return data_base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    
    def _save_agendamento(self, agendamento: Agendamento):
        """Salva agendamento no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Salvar agendamento
            cursor.execute('''
                INSERT OR REPLACE INTO agendamentos (
                    id, nome, descricao, tipo_recorrencia, data_inicio, data_fim,
                    hora_execucao, dias_semana, dia_mes, cron_expression,
                    max_execucoes, timeout_minutos, retry_on_failure, max_retries,
                    notificar_erro, status, user_id, criado_em, proxima_execucao,
                    ultima_execucao, total_execucoes, execucoes_sucesso, execucoes_falha
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agendamento.id,
                agendamento.config.nome,
                agendamento.config.descricao,
                agendamento.config.tipo_recorrencia.value,
                agendamento.config.data_inicio.isoformat(),
                agendamento.config.data_fim.isoformat() if agendamento.config.data_fim else None,
                agendamento.config.hora_execucao,
                json.dumps(agendamento.config.dias_semana) if agendamento.config.dias_semana else None,
                agendamento.config.dia_mes,
                agendamento.config.cron_expression,
                agendamento.config.max_execucoes,
                agendamento.config.timeout_minutos,
                agendamento.config.retry_on_failure,
                agendamento.config.max_retries,
                agendamento.config.notificar_erro,
                agendamento.status.value,
                agendamento.user_id,
                agendamento.criado_em.isoformat(),
                agendamento.proxima_execucao.isoformat() if agendamento.proxima_execucao else None,
                agendamento.ultima_execucao.isoformat() if agendamento.ultima_execucao else None,
                agendamento.total_execucoes,
                agendamento.execucoes_sucesso,
                agendamento.execucoes_falha
            ))
            
            # Salvar execuções agendadas
            cursor.execute('DELETE FROM execucoes_agendadas WHERE agendamento_id = ?', (agendamento.id,))
            
            for execucao in agendamento.execucoes:
                cursor.execute('''
                    INSERT INTO execucoes_agendadas (
                        id, agendamento_id, categoria_id, palavras_chave, cluster, parametros_extras
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    execucao.id,
                    execucao.agendamento_id,
                    execucao.categoria_id,
                    json.dumps(execucao.palavras_chave),
                    execucao.cluster,
                    json.dumps(execucao.parametros_extras)
                ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao salvar agendamento: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _registrar_execucao_historico(self, agendamento_id: str, sucesso: bool, resultado: Optional[str], erro: Optional[str]):
        """Registra execução no histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO historico_execucoes (
                    id, agendamento_id, data_execucao, status, resultado, erro, tempo_execucao
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                agendamento_id,
                datetime.now(timezone.utc).isoformat(),
                'sucesso' if sucesso else 'falha',
                resultado,
                erro,
                0.0  # Tempo de execução (implementar se necessário)
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Erro ao registrar histórico: {str(e)}")
        finally:
            conn.close()
    
    def obter_agendamento(self, agendamento_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de um agendamento"""
        if agendamento_id not in self.agendamentos:
            return None
        
        agendamento = self.agendamentos[agendamento_id]
        
        return {
            'id': agendamento.id,
            'nome': agendamento.config.nome,
            'descricao': agendamento.config.descricao,
            'tipo_recorrencia': agendamento.config.tipo_recorrencia.value,
            'status': agendamento.status.value,
            'user_id': agendamento.user_id,
            'criado_em': agendamento.criado_em.isoformat(),
            'proxima_execucao': agendamento.proxima_execucao.isoformat() if agendamento.proxima_execucao else None,
            'ultima_execucao': agendamento.ultima_execucao.isoformat() if agendamento.ultima_execucao else None,
            'total_execucoes': agendamento.total_execucoes,
            'execucoes_sucesso': agendamento.execucoes_sucesso,
            'execucoes_falha': agendamento.execucoes_falha,
            'execucoes': [
                {
                    'id': e.id,
                    'categoria_id': e.categoria_id,
                    'palavras_chave': e.palavras_chave,
                    'cluster': e.cluster,
                    'parametros_extras': e.parametros_extras
                }
                for e in agendamento.execucoes
            ]
        }
    
    def listar_agendamentos(self, user_id: Optional[str] = None, status: Optional[AgendamentoStatus] = None) -> List[Dict[str, Any]]:
        """Lista agendamentos"""
        agendamentos = []
        
        for agendamento in self.agendamentos.values():
            # Filtrar por usuário
            if user_id and agendamento.user_id != user_id:
                continue
            
            # Filtrar por status
            if status and agendamento.status != status:
                continue
            
            agendamentos.append(self.obter_agendamento(agendamento.id))
        
        # Ordenar por próxima execução
        agendamentos.sort(key=lambda x: x['proxima_execucao'] or '9999-12-31')
        return agendamentos
    
    def cancelar_agendamento(self, agendamento_id: str) -> bool:
        """Cancela um agendamento"""
        if agendamento_id not in self.agendamentos:
            return False
        
        agendamento = self.agendamentos[agendamento_id]
        agendamento.status = AgendamentoStatus.CANCELADO
        agendamento.proxima_execucao = None
        
        self._save_agendamento(agendamento)
        logger.info(f"Agendamento cancelado: {agendamento_id}")
        return True
    
    def pausar_agendamento(self, agendamento_id: str) -> bool:
        """Pausa um agendamento"""
        if agendamento_id not in self.agendamentos:
            return False
        
        agendamento = self.agendamentos[agendamento_id]
        if agendamento.status != AgendamentoStatus.ATIVO:
            return False
        
        agendamento.status = AgendamentoStatus.PAUSADO
        self._save_agendamento(agendamento)
        logger.info(f"Agendamento pausado: {agendamento_id}")
        return True
    
    def retomar_agendamento(self, agendamento_id: str) -> bool:
        """Retoma um agendamento pausado"""
        if agendamento_id not in self.agendamentos:
            return False
        
        agendamento = self.agendamentos[agendamento_id]
        if agendamento.status != AgendamentoStatus.PAUSADO:
            return False
        
        agendamento.status = AgendamentoStatus.ATIVO
        if not agendamento.proxima_execucao:
            agendamento.proxima_execucao = self._calcular_proxima_execucao(agendamento)
        
        self._save_agendamento(agendamento)
        logger.info(f"Agendamento retomado: {agendamento_id}")
        return True
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do serviço"""
        total_agendamentos = len(self.agendamentos)
        agendamentos_ativos = sum(1 for a in self.agendamentos.values() if a.status == AgendamentoStatus.ATIVO)
        agendamentos_pausados = sum(1 for a in self.agendamentos.values() if a.status == AgendamentoStatus.PAUSADO)
        
        total_execucoes = sum(a.total_execucoes for a in self.agendamentos.values())
        total_sucessos = sum(a.execucoes_sucesso for a in self.agendamentos.values())
        total_falhas = sum(a.execucoes_falha for a in self.agendamentos.values())
        
        return {
            'total_agendamentos': total_agendamentos,
            'agendamentos_ativos': agendamentos_ativos,
            'agendamentos_pausados': agendamentos_pausados,
            'total_execucoes': total_execucoes,
            'execucoes_sucesso': total_sucessos,
            'execucoes_falha': total_falhas,
            'taxa_sucesso': total_sucessos / total_execucoes if total_execucoes > 0 else 0
        }

# Instância global
agendamento_service = None

def init_agendamento_service(config: Dict[str, Any] = None):
    """Inicializa serviço de agendamento global"""
    global agendamento_service
    agendamento_service = AgendamentoService(config)
    return agendamento_service

def get_agendamento_service() -> AgendamentoService:
    """Obtém instância do serviço de agendamento"""
    return agendamento_service 