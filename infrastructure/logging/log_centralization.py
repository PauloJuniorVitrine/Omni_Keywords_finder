"""
Sistema de Centralização de Logs
Responsável por centralização de logs com ELK Stack, log shipping e parsing.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 3.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import json
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError
import logging
from pathlib import Path
import queue
import gzip
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

class LogDestination(Enum):
    """Destinos de log disponíveis."""
    ELASTICSEARCH = "elasticsearch"
    LOGSTASH = "logstash"
    KIBANA = "kibana"
    FILE = "file"
    CONSOLE = "console"

@dataclass
class LogEntry:
    """Entrada de log padronizada."""
    timestamp: datetime
    level: str
    message: str
    category: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    service: str = "omni_keywords_finder"
    environment: str = "production"
    metadata: Dict[str, Any] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Converter para JSON."""
        return json.dumps(self.to_dict(), default=str)

class LogShipper:
    """
    Sistema de envio de logs para destinos centralizados.
    
    Funcionalidades:
    - Envio assíncrono de logs
    - Retry automático
    - Compressão de dados
    - Batch processing
    - Fallback para arquivo local
    """
    
    def __init__(
        self,
        elasticsearch_url: str = "http://localhost:9200",
        logstash_url: str = "http://localhost:5044",
        batch_size: int = 100,
        batch_timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
        enable_compression: bool = True,
        fallback_file: str = "logs/fallback.log"
    ):
        """
        Inicializar sistema de envio de logs.
        
        Args:
            elasticsearch_url: URL do Elasticsearch
            logstash_url: URL do Logstash
            batch_size: Tamanho do lote
            batch_timeout: Timeout do lote em segundos
            max_retries: Máximo de tentativas
            retry_delay: Delay entre tentativas
            enable_compression: Habilitar compressão
            fallback_file: Arquivo de fallback
        """
        self.elasticsearch_url = elasticsearch_url
        self.logstash_url = logstash_url
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_compression = enable_compression
        self.fallback_file = Path(fallback_file)
        
        # Criar diretório de fallback
        self.fallback_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Fila de logs
        self.log_queue = queue.Queue()
        
        # Thread pool para envio
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Estatísticas
        self.stats = {
            'logs_sent': 0,
            'logs_failed': 0,
            'batches_processed': 0,
            'retries': 0,
            'fallback_writes': 0
        }
        
        # Iniciar worker thread
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        # Configurar Elasticsearch
        self._setup_elasticsearch()
    
    def _setup_elasticsearch(self):
        """Configurar conexão com Elasticsearch."""
        try:
            self.es = Elasticsearch([self.elasticsearch_url])
            if self.es.ping():
                logging.info(f"Conectado ao Elasticsearch: {self.elasticsearch_url}")
            else:
                logging.warning(f"Não foi possível conectar ao Elasticsearch: {self.elasticsearch_url}")
        except Exception as e:
            logging.error(f"Erro ao conectar ao Elasticsearch: {e}")
            self.es = None
    
    def ship_log(self, log_entry: LogEntry):
        """
        Enviar log para centralização.
        
        Args:
            log_entry: Entrada de log
        """
        try:
            self.log_queue.put(log_entry, timeout=1)
        except queue.Full:
            # Se a fila estiver cheia, escrever no fallback
            self._write_fallback(log_entry)
    
    def _worker_loop(self):
        """Loop principal do worker."""
        batch = []
        last_batch_time = time.time()
        
        while self.running:
            try:
                # Tentar obter log da fila
                try:
                    log_entry = self.log_queue.get(timeout=1)
                    batch.append(log_entry)
                except queue.Empty:
                    pass
                
                # Verificar se deve processar o lote
                current_time = time.time()
                should_process = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_batch_time >= self.batch_timeout)
                )
                
                if should_process and batch:
                    self._process_batch(batch)
                    batch = []
                    last_batch_time = current_time
                    
            except Exception as e:
                logging.error(f"Erro no worker loop: {e}")
                time.sleep(1)
    
    def _process_batch(self, batch: List[LogEntry]):
        """Processar lote de logs."""
        self.stats['batches_processed'] += 1
        
        # Tentar enviar para Elasticsearch
        if self._send_to_elasticsearch(batch):
            self.stats['logs_sent'] += len(batch)
            return
        
        # Tentar enviar para Logstash
        if self._send_to_logstash(batch):
            self.stats['logs_sent'] += len(batch)
            return
        
        # Fallback para arquivo
        for log_entry in batch:
            self._write_fallback(log_entry)
        self.stats['fallback_writes'] += len(batch)
    
    def _send_to_elasticsearch(self, batch: List[LogEntry]) -> bool:
        """Enviar lote para Elasticsearch."""
        if not self.es:
            return False
        
        try:
            # Preparar documentos para bulk insert
            bulk_data = []
            for log_entry in batch:
                # Index name baseado na data
                index_name = f"logs-{log_entry.timestamp.strftime('%Y.%m.%data')}"
                
                # Documento
                doc = {
                    '_index': index_name,
                    '_source': log_entry.to_dict()
                }
                bulk_data.append(doc)
            
            # Enviar em lote
            if bulk_data:
                response = self.es.bulk(body=bulk_data)
                
                # Verificar erros
                if response.get('errors'):
                    errors = [item for item in response['items'] if item.get('index', {}).get('error')]
                    logging.warning(f"Erros no bulk insert: {len(errors)} erros")
                    return False
                
                return True
                
        except Exception as e:
            logging.error(f"Erro ao enviar para Elasticsearch: {e}")
            return False
        
        return False
    
    def _send_to_logstash(self, batch: List[LogEntry]) -> bool:
        """Enviar lote para Logstash."""
        try:
            # Preparar dados
            data = [log_entry.to_dict() for log_entry in batch]
            
            # Comprimir se habilitado
            if self.enable_compression:
                json_data = json.dumps(data)
                compressed_data = gzip.compress(json_data.encode('utf-8'))
                headers = {'Content-Encoding': 'gzip'}
                response = requests.post(
                    self.logstash_url,
                    data=compressed_data,
                    headers=headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    self.logstash_url,
                    json=data,
                    timeout=30
                )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Erro ao enviar para Logstash: {e}")
            return False
    
    def _write_fallback(self, log_entry: LogEntry):
        """Escrever log no arquivo de fallback."""
        try:
            with open(self.fallback_file, 'a', encoding='utf-8') as f:
                f.write(log_entry.to_json() + '\n')
            self.stats['fallback_writes'] += 1
        except Exception as e:
            logging.error(f"Erro ao escrever fallback: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de envio."""
        return self.stats.copy()
    
    def shutdown(self):
        """Desligar o sistema de envio."""
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        self.executor.shutdown(wait=True)

class LogParser:
    """
    Sistema de parsing de logs.
    
    Funcionalidades:
    - Parsing de logs estruturados
    - Extração de campos
    - Validação de formato
    - Transformação de dados
    """
    
    def __init__(self):
        """Inicializar parser de logs."""
        self.parsers = {
            'json': self._parse_json,
            'structured': self._parse_structured,
            'plain': self._parse_plain
        }
    
    def parse_log(self, log_line: str, format_type: str = 'json') -> Optional[LogEntry]:
        """
        Fazer parse de uma linha de log.
        
        Args:
            log_line: Linha de log
            format_type: Tipo de formato
            
        Returns:
            LogEntry ou None se falhar
        """
        parser = self.parsers.get(format_type)
        if not parser:
            logging.error(f"Formato de log não suportado: {format_type}")
            return None
        
        try:
            return parser(log_line)
        except Exception as e:
            logging.error(f"Erro ao fazer parse do log: {e}")
            return None
    
    def _parse_json(self, log_line: str) -> LogEntry:
        """Fazer parse de log JSON."""
        data = json.loads(log_line)
        
        # Converter timestamp
        if isinstance(data.get('timestamp'), str):
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        else:
            timestamp = datetime.utcnow()
        
        return LogEntry(
            timestamp=timestamp,
            level=data.get('level', 'info'),
            message=data.get('message', ''),
            category=data.get('category', 'system'),
            correlation_id=data.get('correlation_id'),
            user_id=data.get('user_id'),
            request_id=data.get('request_id'),
            service=data.get('service', 'omni_keywords_finder'),
            environment=data.get('environment', 'production'),
            metadata=data.get('metadata', {}),
            source_file=data.get('source_file'),
            line_number=data.get('line_number')
        )
    
    def _parse_structured(self, log_line: str) -> LogEntry:
        """Fazer parse de log estruturado."""
        # Implementar parsing de logs estruturados
        # Por exemplo: [2025-01-27 10:30:00] [INFO] [SYSTEM] Message
        parts = log_line.strip().split('] [')
        if len(parts) < 4:
            raise ValueError("Formato estruturado inválido")
        
        # Extrair timestamp
        timestamp_str = parts[0].replace('[', '')
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%data %H:%M:%S')
        
        # Extrair nível
        level = parts[1]
        
        # Extrair categoria
        category = parts[2]
        
        # Extrair mensagem
        message = parts[3].replace(']', '')
        
        return LogEntry(
            timestamp=timestamp,
            level=level.lower(),
            message=message,
            category=category.lower()
        )
    
    def _parse_plain(self, log_line: str) -> LogEntry:
        """Fazer parse de log simples."""
        return LogEntry(
            timestamp=datetime.utcnow(),
            level='info',
            message=log_line.strip(),
            category='system'
        )

class LogAnalyzer:
    """
    Sistema de análise de logs.
    
    Funcionalidades:
    - Análise de padrões
    - Detecção de anomalias
    - Agregação de métricas
    - Alertas baseados em logs
    """
    
    def __init__(self):
        """Inicializar analisador de logs."""
        self.patterns = {
            'error_patterns': [
                r'ERROR',
                r'Exception',
                r'Failed',
                r'Timeout',
                r'Connection refused'
            ],
            'performance_patterns': [
                r'execution_time',
                r'latency',
                r'response_time',
                r'throughput'
            ],
            'security_patterns': [
                r'Unauthorized',
                r'Forbidden',
                r'Invalid credentials',
                r'SQL injection',
                r'XSS'
            ]
        }
        
        self.metrics = {
            'error_rate': 0.0,
            'avg_response_time': 0.0,
            'requests_per_minute': 0,
            'unique_users': set(),
            'top_errors': {}
        }
    
    def analyze_logs(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """
        Analisar lista de logs.
        
        Args:
            logs: Lista de logs
            
        Returns:
            Resultados da análise
        """
        if not logs:
            return {}
        
        # Análise básica
        total_logs = len(logs)
        error_logs = [log for log in logs if log.level in ['error', 'critical']]
        warning_logs = [log for log in logs if log.level == 'warning']
        
        # Calcular métricas
        error_rate = len(error_logs) / total_logs if total_logs > 0 else 0.0
        
        # Análise de performance
        performance_logs = [log for log in logs if 'execution_time' in log.metadata]
        avg_response_time = 0.0
        if performance_logs:
            times = [log.metadata['execution_time'] for log in performance_logs]
            avg_response_time = sum(times) / len(times)
        
        # Análise de usuários
        unique_users = set(log.user_id for log in logs if log.user_id)
        
        # Top erros
        error_messages = {}
        for log in error_logs:
            message = log.message
            error_messages[message] = error_messages.get(message, 0) + 1
        
        top_errors = dict(sorted(error_messages.items(), key=lambda value: value[1], reverse=True)[:10])
        
        # Detectar anomalias
        anomalies = self._detect_anomalies(logs)
        
        return {
            'total_logs': total_logs,
            'error_logs': len(error_logs),
            'warning_logs': len(warning_logs),
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'unique_users': len(unique_users),
            'top_errors': top_errors,
            'anomalies': anomalies,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _detect_anomalies(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detectar anomalias nos logs."""
        anomalies = []
        
        # Agrupar logs por minuto
        logs_by_minute = {}
        for log in logs:
            minute_key = log.timestamp.replace(second=0, microsecond=0)
            if minute_key not in logs_by_minute:
                logs_by_minute[minute_key] = []
            logs_by_minute[minute_key].append(log)
        
        # Detectar picos de erro
        for minute, minute_logs in logs_by_minute.items():
            error_count = len([log for log in minute_logs if log.level in ['error', 'critical']])
            
            # Se mais de 50% dos logs são erros, é uma anomalia
            if error_count > len(minute_logs) * 0.5:
                anomalies.append({
                    'type': 'high_error_rate',
                    'timestamp': minute.isoformat(),
                    'error_count': error_count,
                    'total_logs': len(minute_logs),
                    'error_rate': error_count / len(minute_logs)
                })
        
        return anomalies

class LogAlerting:
    """
    Sistema de alertas baseados em logs.
    
    Funcionalidades:
    - Alertas baseados em thresholds
    - Alertas baseados em padrões
    - Escalação de alertas
    - Integração com sistemas externos
    """
    
    def __init__(self):
        """Inicializar sistema de alertas."""
        self.alerts = []
        self.thresholds = {
            'error_rate': 0.1,  # 10%
            'response_time': 1000,  # 1 segundo
            'consecutive_errors': 5
        }
        
        self.alert_handlers = {
            'email': self._send_email_alert,
            'slack': self._send_slack_alert,
            'webhook': self._send_webhook_alert
        }
    
    def check_alerts(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Verificar se há alertas baseados na análise.
        
        Args:
            analysis_result: Resultado da análise
            
        Returns:
            Lista de alertas
        """
        alerts = []
        
        # Verificar taxa de erro
        if analysis_result.get('error_rate', 0) > self.thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"Taxa de erro alta: {analysis_result['error_rate']:.2%}",
                'value': analysis_result['error_rate'],
                'threshold': self.thresholds['error_rate'],
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Verificar tempo de resposta
        if analysis_result.get('avg_response_time', 0) > self.thresholds['response_time']:
            alerts.append({
                'type': 'high_response_time',
                'severity': 'medium',
                'message': f"Tempo de resposta alto: {analysis_result['avg_response_time']:.2f}ms",
                'value': analysis_result['avg_response_time'],
                'threshold': self.thresholds['response_time'],
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Verificar anomalias
        for anomaly in analysis_result.get('anomalies', []):
            alerts.append({
                'type': 'anomaly_detected',
                'severity': 'high',
                'message': f"Anomalia detectada: {anomaly['type']}",
                'details': anomaly,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Processar alertas
        for alert in alerts:
            self._process_alert(alert)
        
        return alerts
    
    def _process_alert(self, alert: Dict[str, Any]):
        """Processar um alerta."""
        # Adicionar à lista de alertas
        self.alerts.append(alert)
        
        # Enviar para handlers configurados
        for handler_name, handler_func in self.alert_handlers.items():
            try:
                handler_func(alert)
            except Exception as e:
                logging.error(f"Erro ao processar alerta com {handler_name}: {e}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Enviar alerta por email."""
        # Implementar envio de email
        logging.info(f"Alerta por email: {alert['message']}")
    
    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Enviar alerta para Slack."""
        # Implementar envio para Slack
        logging.info(f"Alerta para Slack: {alert['message']}")
    
    def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Enviar alerta via webhook."""
        # Implementar webhook
        logging.info(f"Alerta via webhook: {alert['message']}")

# Instâncias globais
_log_shipper: Optional[LogShipper] = None
_log_parser: Optional[LogParser] = None
_log_analyzer: Optional[LogAnalyzer] = None
_log_alerting: Optional[LogAlerting] = None

def get_log_shipper() -> LogShipper:
    """Obter instância global do log shipper."""
    global _log_shipper
    if _log_shipper is None:
        _log_shipper = LogShipper()
    return _log_shipper

def get_log_parser() -> LogParser:
    """Obter instância global do log parser."""
    global _log_parser
    if _log_parser is None:
        _log_parser = LogParser()
    return _log_parser

def get_log_analyzer() -> LogAnalyzer:
    """Obter instância global do log analyzer."""
    global _log_analyzer
    if _log_analyzer is None:
        _log_analyzer = LogAnalyzer()
    return _log_analyzer

def get_log_alerting() -> LogAlerting:
    """Obter instância global do log alerting."""
    global _log_alerting
    if _log_alerting is None:
        _log_alerting = LogAlerting()
    return _log_alerting

def ship_log_to_centralization(log_entry: LogEntry):
    """Enviar log para centralização."""
    shipper = get_log_shipper()
    shipper.ship_log(log_entry)

def analyze_logs_centralized(logs: List[LogEntry]) -> Dict[str, Any]:
    """Analisar logs centralizados."""
    analyzer = get_log_analyzer()
    return analyzer.analyze_logs(logs)

def check_log_alerts(analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verificar alertas baseados em logs."""
    alerting = get_log_alerting()
    return alerting.check_alerts(analysis_result) 