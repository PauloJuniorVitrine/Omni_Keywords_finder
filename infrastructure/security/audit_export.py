"""
audit_export.py

Exportação de Auditoria - Omni Keywords Finder

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 6
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Exportação de logs em múltiplos formatos
- Geração de relatórios de compliance
- Exportação de alertas de segurança
- Relatórios personalizados
- Compressão e criptografia
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import zipfile
import hashlib
import hmac
import base64
from pathlib import Path
import sqlite3
from dataclasses import asdict
import logging
from enum import Enum

from .advanced_audit import (
    AdvancedAuditSystem, AuditEvent, ComplianceReport, SecurityAlert,
    AuditCategory, AuditLevel, ComplianceFramework, audit_system
)

logger = logging.getLogger(__name__)

class ExportFormat(Enum):
    """Formatos de exportação suportados"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PDF = "pdf"
    EXCEL = "xlsx"
    ZIP = "zip"

class ReportType(Enum):
    """Tipos de relatório"""
    AUDIT_LOGS = "audit_logs"
    COMPLIANCE = "compliance"
    SECURITY_ALERTS = "security_alerts"
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    CUSTOM = "custom"

class AuditExporter:
    """
    Sistema de exportação de auditoria
    
    Fornece exportação em múltiplos formatos, relatórios de compliance
    e funcionalidades de compressão e criptografia.
    """
    
    def __init__(self, audit_system: AdvancedAuditSystem = None):
        self.audit_system = audit_system or audit_system
        self.export_path = Path("exports")
        self.export_path.mkdir(exist_ok=True)
        
        # Configurações de segurança
        self.encryption_key = None
        self.compression_enabled = True
        
        logger.info("Sistema de Exportação de Auditoria inicializado")
    
    def export_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        format: ExportFormat = ExportFormat.JSON,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        compress: bool = True
    ) -> str:
        """
        Exportar logs de auditoria
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            format: Formato de exportação
            filters: Filtros adicionais
            include_metadata: Incluir metadados
            compress: Comprimir arquivo
            
        Returns:
            Caminho do arquivo exportado
        """
        # Buscar eventos
        events = self._get_filtered_events(start_date, end_date, filters)
        
        # Gerar nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_logs_{start_date.strftime('%Y%m%data')}_{end_date.strftime('%Y%m%data')}_{timestamp}"
        
        # Exportar no formato solicitado
        if format == ExportFormat.JSON:
            file_path = self._export_json(events, filename, include_metadata)
        elif format == ExportFormat.CSV:
            file_path = self._export_csv(events, filename, include_metadata)
        elif format == ExportFormat.XML:
            file_path = self._export_xml(events, filename, include_metadata)
        elif format == ExportFormat.EXCEL:
            file_path = self._export_excel(events, filename, include_metadata)
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        # Comprimir se solicitado
        if compress and self.compression_enabled:
            file_path = self._compress_file(file_path)
        
        # Criptografar se configurado
        if self.encryption_key:
            file_path = self._encrypt_file(file_path)
        
        logger.info(f"Logs de auditoria exportados: {file_path}")
        return str(file_path)
    
    def _get_filtered_events(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AuditEvent]:
        """Buscar eventos com filtros"""
        # Usar o método do sistema de auditoria
        events = self.audit_system.get_events(start_date, end_date, limit=100000)
        
        # Aplicar filtros adicionais
        if filters:
            events = self._apply_filters(events, filters)
        
        return events
    
    def _apply_filters(self, events: List[AuditEvent], filters: Dict[str, Any]) -> List[AuditEvent]:
        """Aplicar filtros aos eventos"""
        filtered_events = []
        
        for event in events:
            include_event = True
            
            # Filtro por usuário
            if 'user_id' in filters and event.user_id != filters['user_id']:
                include_event = False
            
            # Filtro por categoria
            if 'category' in filters and event.category != filters['category']:
                include_event = False
            
            # Filtro por nível
            if 'level' in filters and event.level != filters['level']:
                include_event = False
            
            # Filtro por score de risco
            if 'min_risk_score' in filters and event.risk_score < filters['min_risk_score']:
                include_event = False
            
            if 'max_risk_score' in filters and event.risk_score > filters['max_risk_score']:
                include_event = False
            
            # Filtro por ação
            if 'action_contains' in filters and filters['action_contains'] not in event.action:
                include_event = False
            
            # Filtro por recurso
            if 'resource_contains' in filters and filters['resource_contains'] not in event.resource:
                include_event = False
            
            if include_event:
                filtered_events.append(event)
        
        return filtered_events
    
    def _export_json(
        self,
        events: List[AuditEvent],
        filename: str,
        include_metadata: bool
    ) -> Path:
        """Exportar eventos em formato JSON"""
        file_path = self.export_path / f"{filename}.json"
        
        # Preparar dados
        data = {
            'export_info': {
                'generated_at': datetime.now().isoformat(),
                'total_events': len(events),
                'format': 'json',
                'version': '1.0'
            }
        }
        
        if include_metadata:
            data['metadata'] = {
                'filters_applied': True,
                'compression_enabled': self.compression_enabled,
                'encryption_enabled': self.encryption_key is not None
            }
        
        # Converter eventos
        data['events'] = []
        for event in events:
            event_dict = asdict(event)
            event_dict['timestamp'] = event.timestamp.isoformat()
            event_dict['category'] = event.category.value
            event_dict['level'] = event.level.value
            data['events'].append(event_dict)
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def _export_csv(
        self,
        events: List[AuditEvent],
        filename: str,
        include_metadata: bool
    ) -> Path:
        """Exportar eventos em formato CSV"""
        file_path = self.export_path / f"{filename}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            headers = [
                'ID', 'Timestamp', 'User ID', 'Session ID', 'IP Address',
                'User Agent', 'Action', 'Resource', 'Category', 'Level',
                'Details', 'Metadata', 'Hash Signature', 'Compliance Tags',
                'Risk Score'
            ]
            writer.writerow(headers)
            
            # Dados
            for event in events:
                row = [
                    event.id,
                    event.timestamp.isoformat(),
                    event.user_id or '',
                    event.session_id or '',
                    event.ip_address or '',
                    event.user_agent or '',
                    event.action,
                    event.resource,
                    event.category.value,
                    event.level.value,
                    json.dumps(event.details),
                    json.dumps(event.metadata),
                    event.hash_signature,
                    json.dumps(event.compliance_tags),
                    event.risk_score
                ]
                writer.writerow(row)
        
        return file_path
    
    def _export_xml(
        self,
        events: List[AuditEvent],
        filename: str,
        include_metadata: bool
    ) -> Path:
        """Exportar eventos em formato XML"""
        file_path = self.export_path / f"{filename}.xml"
        
        # Criar estrutura XML
        root = ET.Element('audit_logs')
        
        # Informações de exportação
        export_info = ET.SubElement(root, 'export_info')
        ET.SubElement(export_info, 'generated_at').text = datetime.now().isoformat()
        ET.SubElement(export_info, 'total_events').text = str(len(events))
        ET.SubElement(export_info, 'format').text = 'xml'
        ET.SubElement(export_info, 'version').text = '1.0'
        
        if include_metadata:
            metadata = ET.SubElement(root, 'metadata')
            ET.SubElement(metadata, 'filters_applied').text = 'true'
            ET.SubElement(metadata, 'compression_enabled').text = str(self.compression_enabled).lower()
            ET.SubElement(metadata, 'encryption_enabled').text = str(self.encryption_key is not None).lower()
        
        # Eventos
        events_elem = ET.SubElement(root, 'events')
        for event in events:
            event_elem = ET.SubElement(events_elem, 'event')
            
            ET.SubElement(event_elem, 'id').text = event.id
            ET.SubElement(event_elem, 'timestamp').text = event.timestamp.isoformat()
            ET.SubElement(event_elem, 'user_id').text = event.user_id or ''
            ET.SubElement(event_elem, 'session_id').text = event.session_id or ''
            ET.SubElement(event_elem, 'ip_address').text = event.ip_address or ''
            ET.SubElement(event_elem, 'user_agent').text = event.user_agent or ''
            ET.SubElement(event_elem, 'action').text = event.action
            ET.SubElement(event_elem, 'resource').text = event.resource
            ET.SubElement(event_elem, 'category').text = event.category.value
            ET.SubElement(event_elem, 'level').text = event.level.value
            ET.SubElement(event_elem, 'details').text = json.dumps(event.details)
            ET.SubElement(event_elem, 'metadata').text = json.dumps(event.metadata)
            ET.SubElement(event_elem, 'hash_signature').text = event.hash_signature
            ET.SubElement(event_elem, 'compliance_tags').text = json.dumps(event.compliance_tags)
            ET.SubElement(event_elem, 'risk_score').text = str(event.risk_score)
        
        # Salvar arquivo
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
        return file_path
    
    def _export_excel(
        self,
        events: List[AuditEvent],
        filename: str,
        include_metadata: bool
    ) -> Path:
        """Exportar eventos em formato Excel"""
        try:
            import pandas as pd
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            raise ImportError("pandas e openpyxl são necessários para exportação Excel")
        
        file_path = self.export_path / f"{filename}.xlsx"
        
        # Criar DataFrame
        data = []
        for event in events:
            data.append({
                'ID': event.id,
                'Timestamp': event.timestamp,
                'User ID': event.user_id or '',
                'Session ID': event.session_id or '',
                'IP Address': event.ip_address or '',
                'User Agent': event.user_agent or '',
                'Action': event.action,
                'Resource': event.resource,
                'Category': event.category.value,
                'Level': event.level.value,
                'Details': json.dumps(event.details),
                'Metadata': json.dumps(event.metadata),
                'Hash Signature': event.hash_signature,
                'Compliance Tags': json.dumps(event.compliance_tags),
                'Risk Score': event.risk_score
            })
        
        df = pd.DataFrame(data)
        
        # Criar workbook
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Planilha principal
            df.to_excel(writer, sheet_name='Audit Logs', index=False)
            
            # Planilha de resumo
            summary_data = {
                'Metric': [
                    'Total Events',
                    'Unique Users',
                    'High Risk Events (>0.7)',
                    'Security Events',
                    'Average Risk Score',
                    'Date Range'
                ],
                'Value': [
                    len(events),
                    len(set(e.user_id for e in events if e.user_id)),
                    len([e for e in events if e.risk_score > 0.7]),
                    len([e for e in events if e.category == AuditCategory.SECURITY_EVENT]),
                    sum(e.risk_score for e in events) / len(events) if events else 0,
                    f"{events[0].timestamp.date()} to {events[-1].timestamp.date()}" if events else "N/A"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Planilha de categorias
            categories = {}
            for event in events:
                cat = event.category.value
                categories[cat] = categories.get(cat, 0) + 1
            
            cat_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            cat_df.to_excel(writer, sheet_name='Categories', index=False)
        
        return file_path
    
    def _compress_file(self, file_path: Path) -> Path:
        """Comprimir arquivo"""
        zip_path = file_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, file_path.name)
        
        # Remover arquivo original
        file_path.unlink()
        
        return zip_path
    
    def _encrypt_file(self, file_path: Path) -> Path:
        """Criptografar arquivo"""
        if not self.encryption_key:
            return file_path
        
        # Implementar criptografia simples (em produção usar biblioteca adequada)
        encrypted_path = file_path.with_suffix('.enc')
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Criptografar dados
        encrypted_data = self._simple_encrypt(data, self.encryption_key)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Remover arquivo original
        file_path.unlink()
        
        return encrypted_path
    
    def _simple_encrypt(self, data: bytes, key: str) -> bytes:
        """Criptografia simples (apenas para demonstração)"""
        # Em produção, usar bibliotecas como cryptography
        key_bytes = key.encode()
        encrypted = bytearray()
        
        for index, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[index % len(key_bytes)])
        
        return bytes(encrypted)
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime,
        format: ExportFormat = ExportFormat.PDF
    ) -> str:
        """
        Gerar relatório de compliance
        
        Args:
            framework: Framework de compliance
            start_date: Data de início
            end_date: Data de fim
            format: Formato de exportação
            
        Returns:
            Caminho do arquivo gerado
        """
        # Gerar relatório usando o sistema de auditoria
        report = self.audit_system.generate_compliance_report(framework, start_date, end_date)
        
        # Exportar no formato solicitado
        if format == ExportFormat.JSON:
            return self._export_compliance_json(report)
        elif format == ExportFormat.PDF:
            return self._export_compliance_pdf(report)
        elif format == ExportFormat.EXCEL:
            return self._export_compliance_excel(report)
        else:
            raise ValueError(f"Formato não suportado para compliance: {format}")
    
    def _export_compliance_json(self, report: ComplianceReport) -> str:
        """Exportar relatório de compliance em JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_{report.framework.value}_{timestamp}.json"
        file_path = self.export_path / filename
        
        data = {
            'report_id': report.id,
            'framework': report.framework.value,
            'period': {
                'start': report.period_start.isoformat(),
                'end': report.period_end.isoformat()
            },
            'generated_at': report.generated_at.isoformat(),
            'summary': report.summary,
            'violations': report.violations,
            'recommendations': report.recommendations,
            'status': report.status
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def _export_compliance_pdf(self, report: ComplianceReport) -> str:
        """Exportar relatório de compliance em PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError:
            raise ImportError("reportlab é necessário para exportação PDF")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_{report.framework.value}_{timestamp}.pdf"
        file_path = self.export_path / filename
        
        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        story.append(Paragraph(f"Relatório de Compliance - {report.framework.value.upper()}", title_style))
        story.append(Spacer(1, 12))
        
        # Informações do período
        story.append(Paragraph(f"Período: {report.period_start.strftime('%data/%m/%Y')} a {report.period_end.strftime('%data/%m/%Y')}", styles['Normal']))
        story.append(Paragraph(f"Gerado em: {report.generated_at.strftime('%data/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Resumo
        story.append(Paragraph("Resumo", styles['Heading2']))
        for key, value in report.summary.items():
            story.append(Paragraph(f"{key}: {value}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Violações
        if report.violations:
            story.append(Paragraph("Violações Detectadas", styles['Heading2']))
            for violation in report.violations:
                story.append(Paragraph(f"• {violation.get('description', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Recomendações
        if report.recommendations:
            story.append(Paragraph("Recomendações", styles['Heading2']))
            for recommendation in report.recommendations:
                story.append(Paragraph(f"• {recommendation}", styles['Normal']))
        
        doc.build(story)
        return str(file_path)
    
    def _export_compliance_excel(self, report: ComplianceReport) -> str:
        """Exportar relatório de compliance em Excel"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas é necessário para exportação Excel")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_{report.framework.value}_{timestamp}.xlsx"
        file_path = self.export_path / filename
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Planilha de resumo
            summary_df = pd.DataFrame(list(report.summary.items()), columns=['Métrica', 'Valor'])
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Planilha de violações
            if report.violations:
                violations_df = pd.DataFrame(report.violations)
                violations_df.to_excel(writer, sheet_name='Violações', index=False)
            
            # Planilha de recomendações
            if report.recommendations:
                recommendations_df = pd.DataFrame(report.recommendations, columns=['Recomendação'])
                recommendations_df.to_excel(writer, sheet_name='Recomendações', index=False)
        
        return str(file_path)
    
    def export_security_alerts(
        self,
        start_date: datetime,
        end_date: datetime,
        format: ExportFormat = ExportFormat.JSON,
        status: Optional[str] = None
    ) -> str:
        """
        Exportar alertas de segurança
        
        Args:
            start_date: Data de início
            end_date: Data de fim
            format: Formato de exportação
            status: Status dos alertas (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        # Buscar alertas
        alerts = self._get_security_alerts(start_date, end_date, status)
        
        # Gerar nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security_alerts_{start_date.strftime('%Y%m%data')}_{end_date.strftime('%Y%m%data')}_{timestamp}"
        
        # Exportar no formato solicitado
        if format == ExportFormat.JSON:
            file_path = self._export_alerts_json(alerts, filename)
        elif format == ExportFormat.CSV:
            file_path = self._export_alerts_csv(alerts, filename)
        elif format == ExportFormat.EXCEL:
            file_path = self._export_alerts_excel(alerts, filename)
        else:
            raise ValueError(f"Formato não suportado para alertas: {format}")
        
        return str(file_path)
    
    def _get_security_alerts(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> List[SecurityAlert]:
        """Buscar alertas de segurança"""
        # Implementar busca de alertas do banco de dados
        conn = sqlite3.connect(self.audit_system.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM security_alerts WHERE timestamp >= ? AND timestamp <= ?"
        params = [start_date.isoformat(), end_date.isoformat()]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alert = SecurityAlert(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                alert_type=row[2],
                severity=row[3],
                description=row[4],
                affected_user=row[5],
                affected_resource=row[6],
                evidence=json.loads(row[7]),
                status=row[8],
                resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
            )
            alerts.append(alert)
        
        return alerts
    
    def _export_alerts_json(self, alerts: List[SecurityAlert], filename: str) -> Path:
        """Exportar alertas em JSON"""
        file_path = self.export_path / f"{filename}.json"
        
        data = {
            'export_info': {
                'generated_at': datetime.now().isoformat(),
                'total_alerts': len(alerts),
                'format': 'json',
                'version': '1.0'
            },
            'alerts': []
        }
        
        for alert in alerts:
            alert_dict = asdict(alert)
            alert_dict['timestamp'] = alert.timestamp.isoformat()
            if alert.resolved_at:
                alert_dict['resolved_at'] = alert.resolved_at.isoformat()
            data['alerts'].append(alert_dict)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def _export_alerts_csv(self, alerts: List[SecurityAlert], filename: str) -> Path:
        """Exportar alertas em CSV"""
        file_path = self.export_path / f"{filename}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho
            headers = [
                'ID', 'Timestamp', 'Alert Type', 'Severity', 'Description',
                'Affected User', 'Affected Resource', 'Evidence', 'Status',
                'Resolved At'
            ]
            writer.writerow(headers)
            
            # Dados
            for alert in alerts:
                row = [
                    alert.id,
                    alert.timestamp.isoformat(),
                    alert.alert_type,
                    alert.severity,
                    alert.description,
                    alert.affected_user or '',
                    alert.affected_resource or '',
                    json.dumps(alert.evidence),
                    alert.status,
                    alert.resolved_at.isoformat() if alert.resolved_at else ''
                ]
                writer.writerow(row)
        
        return file_path
    
    def _export_alerts_excel(self, alerts: List[SecurityAlert], filename: str) -> Path:
        """Exportar alertas em Excel"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas é necessário para exportação Excel")
        
        file_path = self.export_path / f"{filename}.xlsx"
        
        data = []
        for alert in alerts:
            data.append({
                'ID': alert.id,
                'Timestamp': alert.timestamp,
                'Alert Type': alert.alert_type,
                'Severity': alert.severity,
                'Description': alert.description,
                'Affected User': alert.affected_user or '',
                'Affected Resource': alert.affected_resource or '',
                'Evidence': json.dumps(alert.evidence),
                'Status': alert.status,
                'Resolved At': alert.resolved_at
            })
        
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Security Alerts', index=False)
            
            # Planilha de resumo
            summary_data = {
                'Metric': [
                    'Total Alerts',
                    'Open Alerts',
                    'Resolved Alerts',
                    'Critical Alerts',
                    'High Severity Alerts',
                    'Medium Severity Alerts',
                    'Low Severity Alerts'
                ],
                'Count': [
                    len(alerts),
                    len([a for a in alerts if a.status == 'open']),
                    len([a for a in alerts if a.status == 'resolved']),
                    len([a for a in alerts if a.severity == 'critical']),
                    len([a for a in alerts if a.severity == 'high']),
                    len([a for a in alerts if a.severity == 'medium']),
                    len([a for a in alerts if a.severity == 'low'])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return file_path
    
    def create_custom_report(
        self,
        report_config: Dict[str, Any],
        format: ExportFormat = ExportFormat.JSON
    ) -> str:
        """
        Criar relatório personalizado
        
        Args:
            report_config: Configuração do relatório
            format: Formato de exportação
            
        Returns:
            Caminho do arquivo gerado
        """
        # Validar configuração
        required_fields = ['name', 'type', 'filters', 'start_date', 'end_date']
        for field in required_fields:
            if field not in report_config:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Gerar relatório baseado no tipo
        report_type = ReportType(report_config['type'])
        
        if report_type == ReportType.AUDIT_LOGS:
            return self.export_audit_logs(
                start_date=report_config['start_date'],
                end_date=report_config['end_date'],
                format=format,
                filters=report_config.get('filters')
            )
        
        elif report_type == ReportType.COMPLIANCE:
            return self.generate_compliance_report(
                framework=ComplianceFramework(report_config['framework']),
                start_date=report_config['start_date'],
                end_date=report_config['end_date'],
                format=format
            )
        
        elif report_type == ReportType.SECURITY_ALERTS:
            return self.export_security_alerts(
                start_date=report_config['start_date'],
                end_date=report_config['end_date'],
                format=format,
                status=report_config.get('status')
            )
        
        else:
            raise ValueError(f"Tipo de relatório não suportado: {report_type}")


# Instância global do exportador
audit_exporter = AuditExporter() 