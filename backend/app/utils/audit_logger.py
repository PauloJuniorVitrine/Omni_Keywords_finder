"""
Logger Especializado para Auditoria - Omni Keywords Finder
Logs estruturados de auditoria com análise de segurança
Prompt: Implementação de sistema de auditoria
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import uuid
import csv
import gzip
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import sqlite3
import os

from ..schemas.audit_schemas import (
    AuditLogEntry,
    AuditFilterSchema,
    AuditReportSchema,
    AuditExportSchema,
    AuditEventType,
    AuditSeverity,
    AuditCategory
)

@dataclass
class AuditStatistics:
    """Estatísticas de auditoria"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_category: Dict[str, int]
    events_by_user: Dict[str, int]
    events_by_hour: Dict[str, int]
    security_events: int
    unauthorized_access: int
    suspicious_activity: int
    rate_limit_violations: int

class AuditLogger:
    """Logger especializado para auditoria com análise de segurança"""
    
    def __init__(self, db_path: str = "audit.db", log_file: str = "logs/audit.log"):
        """Inicializa o logger de auditoria"""
        self.db_path = db_path
        self.log_file = log_file
        self.logger = self._setup_logger()
        self.db = self._setup_database()
        
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger"""
        logger = logging.getLogger("audit_logger")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if not logger.handlers:
            # Criar diretório de logs se não existir
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            # Handler para arquivo
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            
            # Formato estruturado
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            
            # Handler para console (apenas em desenvolvimento)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _setup_database(self) -> sqlite3.Connection:
        """Configura banco de dados SQLite para auditoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de logs de auditoria
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                request_id TEXT,
                message TEXT NOT NULL,
                details TEXT,
                resource_type TEXT,
                resource_id TEXT,
                source TEXT NOT NULL,
                version TEXT NOT NULL,
                environment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Criar índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON audit_logs(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON audit_logs(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_address ON audit_logs(ip_address)')
        
        conn.commit()
        return conn
    
    def log_event(
        self,
        event_type: str,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        severity: str = "info",
        category: str = "system"
    ) -> str:
        """
        Registra um evento de auditoria
        
        Args:
            event_type: Tipo do evento
            message: Mensagem do evento
            user_id: ID do usuário
            session_id: ID da sessão
            ip_address: Endereço IP
            user_agent: User-Agent
            request_id: ID da requisição
            details: Detalhes do evento
            resource_type: Tipo do recurso
            resource_id: ID do recurso
            severity: Nível de severidade
            category: Categoria do evento
            
        Returns:
            ID do log criado
        """
        try:
            # Criar entrada de log
            log_entry = AuditLogEntry(
                log_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                severity=severity,
                category=category,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                message=message,
                details=details or {},
                resource_type=resource_type,
                resource_id=resource_id,
                source="api",
                version="1.0",
                environment="production"
            )
            
            # Salvar no banco de dados
            self._save_to_database(log_entry)
            
            # Log estruturado
            self._log_structured(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar evento de auditoria: {str(e)}")
            return ""
    
    def _save_to_database(self, log_entry: AuditLogEntry):
        """Salva entrada no banco de dados"""
        cursor = self.db.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs (
                log_id, timestamp, event_type, severity, category,
                user_id, session_id, ip_address, user_agent, request_id,
                message, details, resource_type, resource_id,
                source, version, environment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_entry.log_id,
            log_entry.timestamp.isoformat(),
            log_entry.event_type,
            log_entry.severity,
            log_entry.category,
            log_entry.user_id,
            log_entry.session_id,
            log_entry.ip_address,
            log_entry.user_agent,
            log_entry.request_id,
            log_entry.message,
            json.dumps(log_entry.details),
            log_entry.resource_type,
            log_entry.resource_id,
            log_entry.source,
            log_entry.version,
            log_entry.environment,
            datetime.now(timezone.utc).isoformat()
        ))
        
        self.db.commit()
    
    def _log_structured(self, log_entry: AuditLogEntry):
        """Registra log estruturado"""
        try:
            log_data = asdict(log_entry)
            log_json = json.dumps(log_data, ensure_ascii=False, default=str)
            
            # Log baseado na severidade
            if log_entry.severity == "critical":
                self.logger.critical(f"[AUDIT] {log_json}")
            elif log_entry.severity == "error":
                self.logger.error(f"[AUDIT] {log_json}")
            elif log_entry.severity == "warning":
                self.logger.warning(f"[AUDIT] {log_json}")
            elif log_entry.severity == "security":
                self.logger.warning(f"[SECURITY] {log_json}")
            else:
                self.logger.info(f"[AUDIT] {log_json}")
                
        except Exception as e:
            self.logger.error(f"Erro ao registrar log estruturado: {str(e)}")
            self.logger.info(f"Log simples: {log_entry.message}")
    
    def get_audit_logs(self, filters: AuditFilterSchema) -> List[Dict[str, Any]]:
        """
        Obtém logs de auditoria com filtros
        
        Args:
            filters: Filtros para consulta
            
        Returns:
            Lista de logs de auditoria
        """
        try:
            cursor = self.db.cursor()
            
            # Construir query
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            # Filtros de tempo
            if filters.start_date:
                query += " AND timestamp >= ?"
                params.append(filters.start_date.isoformat())
            
            if filters.end_date:
                query += " AND timestamp <= ?"
                params.append(filters.end_date.isoformat())
            
            # Filtros de evento
            if filters.event_types:
                placeholders = ','.join(['?' for _ in filters.event_types])
                query += f" AND event_type IN ({placeholders})"
                params.extend(filters.event_types)
            
            # Filtros de severidade
            if filters.severities:
                placeholders = ','.join(['?' for _ in filters.severities])
                query += f" AND severity IN ({placeholders})"
                params.extend(filters.severities)
            
            # Filtros de categoria
            if filters.categories:
                placeholders = ','.join(['?' for _ in filters.categories])
                query += f" AND category IN ({placeholders})"
                params.extend(filters.categories)
            
            # Filtros de usuário
            if filters.user_id:
                query += " AND user_id = ?"
                params.append(filters.user_id)
            
            if filters.ip_address:
                query += " AND ip_address = ?"
                params.append(filters.ip_address)
            
            # Filtros de recurso
            if filters.resource_type:
                query += " AND resource_type = ?"
                params.append(filters.resource_type)
            
            if filters.resource_id:
                query += " AND resource_id = ?"
                params.append(filters.resource_id)
            
            # Ordenação
            query += f" ORDER BY {filters.sort_by} {filters.sort_order.upper()}"
            
            # Paginação
            if filters.limit:
                query += f" LIMIT {filters.limit}"
            
            if filters.offset:
                query += f" OFFSET {filters.offset}"
            
            # Executar query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Converter para dicionários
            logs = []
            for row in rows:
                log = {
                    'log_id': row[0],
                    'timestamp': row[1],
                    'event_type': row[2],
                    'severity': row[3],
                    'category': row[4],
                    'user_id': row[5],
                    'session_id': row[6],
                    'ip_address': row[7],
                    'user_agent': row[8],
                    'request_id': row[9],
                    'message': row[10],
                    'details': json.loads(row[11]) if row[11] else {},
                    'resource_type': row[12],
                    'resource_id': row[13],
                    'source': row[14],
                    'version': row[15],
                    'environment': row[16],
                    'created_at': row[17]
                }
                logs.append(log)
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Erro ao obter logs de auditoria: {str(e)}")
            return []
    
    def get_statistics(self, start_date: datetime, end_date: datetime) -> AuditStatistics:
        """
        Obtém estatísticas de auditoria
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Estatísticas de auditoria
        """
        try:
            cursor = self.db.cursor()
            
            # Query base
            base_query = "SELECT * FROM audit_logs WHERE timestamp BETWEEN ? AND ?"
            params = [start_date.isoformat(), end_date.isoformat()]
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            # Contadores
            events_by_type = Counter()
            events_by_severity = Counter()
            events_by_category = Counter()
            events_by_user = Counter()
            events_by_hour = Counter()
            
            security_events = 0
            unauthorized_access = 0
            suspicious_activity = 0
            rate_limit_violations = 0
            
            for row in rows:
                event_type = row[2]
                severity = row[3]
                category = row[4]
                user_id = row[5]
                timestamp = row[1]
                
                # Contadores básicos
                events_by_type[event_type] += 1
                events_by_severity[severity] += 1
                events_by_category[category] += 1
                
                if user_id:
                    events_by_user[user_id] += 1
                
                # Contador por hora
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour_key = dt.strftime("%Y-%m-%d %H:00")
                    events_by_hour[hour_key] += 1
                except:
                    pass
                
                # Contadores de segurança
                if category == "security":
                    security_events += 1
                
                if event_type == "unauthorized_access":
                    unauthorized_access += 1
                
                if event_type == "suspicious_activity":
                    suspicious_activity += 1
                
                if event_type == "rate_limit_exceeded":
                    rate_limit_violations += 1
            
            return AuditStatistics(
                total_events=len(rows),
                events_by_type=dict(events_by_type),
                events_by_severity=dict(events_by_severity),
                events_by_category=dict(events_by_category),
                events_by_user=dict(events_by_user),
                events_by_hour=dict(events_by_hour),
                security_events=security_events,
                unauthorized_access=unauthorized_access,
                suspicious_activity=suspicious_activity,
                rate_limit_violations=rate_limit_violations
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return AuditStatistics(
                total_events=0,
                events_by_type={},
                events_by_severity={},
                events_by_category={},
                events_by_user={},
                events_by_hour={},
                security_events=0,
                unauthorized_access=0,
                suspicious_activity=0,
                rate_limit_violations=0
            )
    
    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[AuditFilterSchema] = None
    ) -> AuditReportSchema:
        """
        Gera relatório de auditoria
        
        Args:
            start_date: Data inicial
            end_date: Data final
            filters: Filtros opcionais
            
        Returns:
            Relatório de auditoria
        """
        try:
            # Obter estatísticas
            stats = self.get_statistics(start_date, end_date)
            
            # Calcular métricas de performance
            total_hours = (end_date - start_date).total_seconds() / 3600
            average_events_per_hour = stats.total_events / total_hours if total_hours > 0 else 0
            
            # Encontrar hora de pico
            peak_hour = ""
            peak_events = 0
            if stats.events_by_hour:
                peak_hour = max(stats.events_by_hour, key=stats.events_by_hour.get)
                peak_events = stats.events_by_hour[peak_hour]
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(stats)
            
            return AuditReportSchema(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.now(timezone.utc),
                period_start=start_date,
                period_end=end_date,
                filters=filters or AuditFilterSchema(),
                total_events=stats.total_events,
                events_by_type=stats.events_by_type,
                events_by_severity=stats.events_by_severity,
                events_by_category=stats.events_by_category,
                events_by_user=stats.events_by_user,
                security_events=stats.security_events,
                unauthorized_access=stats.unauthorized_access,
                suspicious_activity=stats.suspicious_activity,
                rate_limit_violations=stats.rate_limit_violations,
                average_events_per_hour=average_events_per_hour,
                peak_hour=peak_hour,
                peak_events=peak_events,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {str(e)}")
            raise
    
    def _generate_recommendations(self, stats: AuditStatistics) -> List[str]:
        """Gera recomendações baseadas nas estatísticas"""
        recommendations = []
        
        # Análise de segurança
        if stats.unauthorized_access > 10:
            recommendations.append("Alto número de tentativas de acesso não autorizado. Revisar políticas de autenticação.")
        
        if stats.suspicious_activity > 5:
            recommendations.append("Atividades suspeitas detectadas. Implementar monitoramento adicional.")
        
        if stats.rate_limit_violations > 20:
            recommendations.append("Muitas violações de rate limiting. Ajustar limites ou investigar ataques.")
        
        # Análise de performance
        if stats.total_events > 10000:
            recommendations.append("Volume alto de eventos. Considerar otimização de logs.")
        
        # Análise de usuários
        if len(stats.events_by_user) > 100:
            recommendations.append("Muitos usuários ativos. Revisar políticas de acesso.")
        
        return recommendations
    
    def export_logs(self, export_config: AuditExportSchema) -> str:
        """
        Exporta logs de auditoria
        
        Args:
            export_config: Configuração de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        try:
            # Obter logs
            logs = self.get_audit_logs(export_config.filters)
            
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_config.filename or f"audit_logs_{timestamp}"
            
            if export_config.format == "json":
                filepath = self._export_json(logs, filename, export_config)
            elif export_config.format == "csv":
                filepath = self._export_csv(logs, filename, export_config)
            elif export_config.format == "xml":
                filepath = self._export_xml(logs, filename, export_config)
            else:
                raise ValueError(f"Formato não suportado: {export_config.format}")
            
            # Comprimir se solicitado
            if export_config.compression:
                filepath = self._compress_file(filepath)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar logs: {str(e)}")
            raise
    
    def _export_json(self, logs: List[Dict], filename: str, config: AuditExportSchema) -> str:
        """Exporta logs em formato JSON"""
        filepath = f"exports/{filename}.json"
        os.makedirs("exports", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath
    
    def _export_csv(self, logs: List[Dict], filename: str, config: AuditExportSchema) -> str:
        """Exporta logs em formato CSV"""
        filepath = f"exports/{filename}.csv"
        os.makedirs("exports", exist_ok=True)
        
        if not logs:
            return filepath
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=logs[0].keys())
            writer.writeheader()
            writer.writerows(logs)
        
        return filepath
    
    def _export_xml(self, logs: List[Dict], filename: str, config: AuditExportSchema) -> str:
        """Exporta logs em formato XML"""
        filepath = f"exports/{filename}.xml"
        os.makedirs("exports", exist_ok=True)
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<audit_logs>\n'
        
        for log in logs:
            xml_content += '  <log>\n'
            for key, value in log.items():
                xml_content += f'    <{key}>{value}</{key}>\n'
            xml_content += '  </log>\n'
        
        xml_content += '</audit_logs>'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filepath
    
    def _compress_file(self, filepath: str) -> str:
        """Comprime arquivo com gzip"""
        compressed_path = filepath + '.gz'
        
        with open(filepath, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remover arquivo original
        os.remove(filepath)
        
        return compressed_path
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Remove logs antigos"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            cursor = self.db.cursor()
            cursor.execute(
                "DELETE FROM audit_logs WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            
            deleted_count = cursor.rowcount
            self.db.commit()
            
            self.logger.info(f"Removidos {deleted_count} logs antigos (mais de {days_to_keep} dias)")
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar logs antigos: {str(e)}")
    
    def close(self):
        """Fecha conexões"""
        if self.db:
            self.db.close() 