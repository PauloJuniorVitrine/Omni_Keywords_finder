#!/usr/bin/env python3
"""
📋 COMPLIANCE REPORT GENERATOR - OMNİ KEYWORDS FINDER

Tracing ID: COMPLIANCE_REPORT_2025_001
Data/Hora: 2025-01-27 16:45:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Gerador de relatórios de compliance em múltiplos formatos.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import csv
import yaml
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [COMPLIANCE_REPORT] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/compliance_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReportFormat(Enum):
    """Formatos de relatório suportados"""
    JSON = "json"
    CSV = "csv"
    YAML = "yaml"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"

class ReportType(Enum):
    """Tipos de relatório"""
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    INCIDENT = "incident"

@dataclass
class ComplianceRequirement:
    """Requisito de compliance"""
    id: str
    name: str
    description: str
    framework: str
    status: str
    priority: str
    score: float
    last_audit: Optional[datetime] = None
    next_audit: Optional[datetime] = None
    notes: str = ""

@dataclass
class ComplianceReport:
    """Relatório de compliance"""
    report_id: str
    report_type: ReportType
    framework: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    overall_score: float
    requirements: List[ComplianceRequirement]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]
    metrics: Dict[str, Any]

class ComplianceReportGenerator:
    """Gerador de relatórios de compliance"""
    
    def __init__(self):
        self.tracing_id = f"COMPLIANCE_REPORT_GEN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.reports_dir = Path("reports/compliance")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def load_compliance_data(self) -> Dict[str, Any]:
        """Carrega dados de compliance"""
        try:
            data = {}
            
            # Carregar métricas
            metrics_file = Path("data/compliance/metrics_history.json")
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    data["metrics"] = [json.loads(line) for line in f]
            
            # Carregar alertas
            alerts_file = Path("data/compliance/alerts.json")
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    data["alerts"] = [json.loads(line) for line in f]
            
            # Carregar dashboard
            dashboard_file = Path("data/compliance/dashboard.json")
            if dashboard_file.exists():
                with open(dashboard_file, 'r') as f:
                    data["dashboard"] = json.load(f)
            
            # Carregar requirements
            requirements_file = Path("config/compliance/requirements.json")
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    data["requirements"] = json.load(f)
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return {}
    
    def generate_executive_report(self, data: Dict[str, Any]) -> ComplianceReport:
        """Gera relatório executivo"""
        dashboard = data.get("dashboard", {})
        
        # Calcular métricas executivas
        overall_score = dashboard.get("overall_score", 0.0)
        framework_scores = dashboard.get("framework_scores", {})
        active_alerts = dashboard.get("active_alerts", 0)
        
        # Gerar recomendações executivas
        recommendations = []
        if overall_score < 90:
            recommendations.append("Implementar melhorias urgentes nos controles de compliance")
        if active_alerts > 0:
            recommendations.append("Resolver alertas ativos de compliance")
        if any(score < 85 for score in framework_scores.values()):
            recommendations.append("Focar em frameworks com score baixo")
        
        report = ComplianceReport(
            report_id=f"EXEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.EXECUTIVE,
            framework="ALL",
            generated_at=datetime.now(),
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now(),
            overall_score=overall_score,
            requirements=[],
            recommendations=recommendations,
            alerts=data.get("alerts", [])[-10:],  # Últimos 10 alertas
            metrics=dashboard
        )
        
        return report
    
    def generate_technical_report(self, data: Dict[str, Any], framework: str) -> ComplianceReport:
        """Gera relatório técnico"""
        requirements_data = data.get("requirements", {}).get(framework, [])
        
        requirements = []
        for req_data in requirements_data:
            req = ComplianceRequirement(
                id=req_data.get("id", ""),
                name=req_data.get("name", ""),
                description=req_data.get("description", ""),
                framework=framework,
                status=req_data.get("status", ""),
                priority=req_data.get("priority", ""),
                score=req_data.get("score", 0.0),
                notes=req_data.get("notes", "")
            )
            requirements.append(req)
        
        # Calcular score geral
        if requirements:
            overall_score = sum(req.score for req in requirements) / len(requirements)
        else:
            overall_score = 0.0
        
        # Gerar recomendações técnicas
        recommendations = []
        low_score_reqs = [req for req in requirements if req.score < 80]
        for req in low_score_reqs:
            recommendations.append(f"Melhorar implementação de {req.name} (score: {req.score})")
        
        report = ComplianceReport(
            report_id=f"TECH_{framework}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.TECHNICAL,
            framework=framework,
            generated_at=datetime.now(),
            period_start=datetime.now() - timedelta(days=30),
            period_end=datetime.now(),
            overall_score=overall_score,
            requirements=requirements,
            recommendations=recommendations,
            alerts=[],
            metrics={}
        )
        
        return report
    
    def generate_audit_report(self, data: Dict[str, Any]) -> ComplianceReport:
        """Gera relatório de auditoria"""
        # Simular dados de auditoria
        audit_requirements = [
            ComplianceRequirement(
                id="AUDIT-001",
                name="Data Protection Policy Review",
                description="Revisão da política de proteção de dados",
                framework="GDPR",
                status="completed",
                priority="high",
                score=95.0,
                last_audit=datetime.now() - timedelta(days=7),
                next_audit=datetime.now() + timedelta(days=90)
            ),
            ComplianceRequirement(
                id="AUDIT-002",
                name="Access Control Audit",
                description="Auditoria de controles de acesso",
                framework="ISO27001",
                status="in_progress",
                priority="high",
                score=87.0,
                last_audit=datetime.now() - timedelta(days=3),
                next_audit=datetime.now() + timedelta(days=30)
            )
        ]
        
        overall_score = sum(req.score for req in audit_requirements) / len(audit_requirements)
        
        recommendations = [
            "Completar auditoria de controles de acesso",
            "Implementar melhorias identificadas na revisão de políticas"
        ]
        
        report = ComplianceReport(
            report_id=f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.AUDIT,
            framework="ALL",
            generated_at=datetime.now(),
            period_start=datetime.now() - timedelta(days=90),
            period_end=datetime.now(),
            overall_score=overall_score,
            requirements=audit_requirements,
            recommendations=recommendations,
            alerts=[],
            metrics={}
        )
        
        return report
    
    def export_report_json(self, report: ComplianceReport) -> str:
        """Exporta relatório em JSON"""
        report_data = asdict(report)
        report_data["generated_at"] = report.generated_at.isoformat()
        report_data["period_start"] = report.period_start.isoformat()
        report_data["period_end"] = report.period_end.isoformat()
        
        filename = f"{report.report_id}.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def export_report_csv(self, report: ComplianceReport) -> str:
        """Exporta relatório em CSV"""
        filename = f"{report.report_id}.csv"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Report ID", "Type", "Framework", "Generated At",
                "Overall Score", "Requirements Count", "Recommendations Count"
            ])
            
            # Data
            writer.writerow([
                report.report_id,
                report.report_type.value,
                report.framework,
                report.generated_at.isoformat(),
                report.overall_score,
                len(report.requirements),
                len(report.recommendations)
            ])
            
            # Requirements
            if report.requirements:
                writer.writerow([])
                writer.writerow([
                    "Requirement ID", "Name", "Description", "Status",
                    "Priority", "Score", "Notes"
                ])
                
                for req in report.requirements:
                    writer.writerow([
                        req.id, req.name, req.description, req.status,
                        req.priority, req.score, req.notes
                    ])
        
        return str(filepath)
    
    def export_report_yaml(self, report: ComplianceReport) -> str:
        """Exporta relatório em YAML"""
        report_data = asdict(report)
        report_data["generated_at"] = report.generated_at.isoformat()
        report_data["period_start"] = report.period_start.isoformat()
        report_data["period_end"] = report.period_end.isoformat()
        
        filename = f"{report.report_id}.yaml"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(report_data, f, default_flow_style=False, allow_unicode=True)
        
        return str(filepath)
    
    def export_report_markdown(self, report: ComplianceReport) -> str:
        """Exporta relatório em Markdown"""
        filename = f"{report.report_id}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 📋 Relatório de Compliance - {report.report_type.value.upper()}\n\n")
            f.write(f"**ID do Relatório**: {report.report_id}\n")
            f.write(f"**Framework**: {report.framework}\n")
            f.write(f"**Gerado em**: {report.generated_at.strftime('%Y-%m-%data %H:%M:%S')}\n")
            f.write(f"**Período**: {report.period_start.strftime('%Y-%m-%data')} a {report.period_end.strftime('%Y-%m-%data')}\n\n")
            
            f.write(f"## 📊 Resumo Executivo\n\n")
            f.write(f"**Score Geral**: {report.overall_score:.1f}%\n")
            f.write(f"**Requisitos**: {len(report.requirements)}\n")
            f.write(f"**Recomendações**: {len(report.recommendations)}\n")
            f.write(f"**Alertas**: {len(report.alerts)}\n\n")
            
            if report.requirements:
                f.write(f"## 📋 Requisitos\n\n")
                f.write("| ID | Nome | Status | Prioridade | Score |\n")
                f.write("|----|------|--------|------------|-------|\n")
                
                for req in report.requirements:
                    f.write(f"| {req.id} | {req.name} | {req.status} | {req.priority} | {req.score:.1f}% |\n")
                f.write("\n")
            
            if report.recommendations:
                f.write(f"## 💡 Recomendações\n\n")
                for index, rec in enumerate(report.recommendations, 1):
                    f.write(f"{index}. {rec}\n")
                f.write("\n")
            
            if report.alerts:
                f.write(f"## 🚨 Alertas\n\n")
                for alert in report.alerts:
                    f.write(f"- **{alert.get('level', 'INFO')}**: {alert.get('message', '')}\n")
                f.write("\n")
        
        return str(filepath)
    
    def export_report_html(self, report: ComplianceReport) -> str:
        """Exporta relatório em HTML"""
        filename = f"{report.report_id}.html"
        filepath = self.reports_dir / filename
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Compliance - {report.report_type.value.upper()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 2em; color: #007bff; font-weight: bold; }}
        .requirements {{ margin: 20px 0; }}
        .requirement {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .recommendations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; }}
        .alerts {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Relatório de Compliance - {report.report_type.value.upper()}</h1>
        <p><strong>ID:</strong> {report.report_id}</p>
        <p><strong>Framework:</strong> {report.framework}</p>
        <p><strong>Gerado em:</strong> {report.generated_at.strftime('%Y-%m-%data %H:%M:%S')}</p>
        <p class="score">Score Geral: {report.overall_score:.1f}%</p>
    </div>
    
    <div class="requirements">
        <h2>📋 Requisitos ({len(report.requirements)})</h2>
        {''.join(f'<div class="requirement"><strong>{req.id}:</strong> {req.name} - {req.status} ({req.score:.1f}%)</div>' for req in report.requirements)}
    </div>
    
    <div class="recommendations">
        <h2>💡 Recomendações ({len(report.recommendations)})</h2>
        <ul>
        {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
        </ul>
    </div>
    
    <div class="alerts">
        <h2>🚨 Alertas ({len(report.alerts)})</h2>
        <ul>
        {''.join(f'<li>{alert.get("message", "")}</li>' for alert in report.alerts)}
        </ul>
    </div>
</body>
</html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_all_reports(self, formats: List[ReportFormat] = None) -> Dict[str, List[str]]:
        """Gera todos os tipos de relatório"""
        if formats is None:
            formats = [ReportFormat.JSON, ReportFormat.CSV, ReportFormat.MARKDOWN, ReportFormat.HTML]
        
        data = self.load_compliance_data()
        results = {}
        
        # Relatório Executivo
        executive_report = self.generate_executive_report(data)
        results["executive"] = self.export_report(executive_report, formats)
        
        # Relatórios Técnicos por Framework
        frameworks = ["GDPR", "LGPD", "SOC2", "ISO27001", "PCI_DSS"]
        for framework in frameworks:
            tech_report = self.generate_technical_report(data, framework)
            results[f"technical_{framework.lower()}"] = self.export_report(tech_report, formats)
        
        # Relatório de Auditoria
        audit_report = self.generate_audit_report(data)
        results["audit"] = self.export_report(audit_report, formats)
        
        return results
    
    def export_report(self, report: ComplianceReport, formats: List[ReportFormat]) -> List[str]:
        """Exporta relatório em múltiplos formatos"""
        exported_files = []
        
        for format_type in formats:
            try:
                if format_type == ReportFormat.JSON:
                    filepath = self.export_report_json(report)
                elif format_type == ReportFormat.CSV:
                    filepath = self.export_report_csv(report)
                elif format_type == ReportFormat.YAML:
                    filepath = self.export_report_yaml(report)
                elif format_type == ReportFormat.MARKDOWN:
                    filepath = self.export_report_markdown(report)
                elif format_type == ReportFormat.HTML:
                    filepath = self.export_report_html(report)
                else:
                    logger.warning(f"Formato não suportado: {format_type}")
                    continue
                
                exported_files.append(filepath)
                logger.info(f"✅ Relatório exportado: {filepath}")
                
            except Exception as e:
                logger.error(f"Erro ao exportar {format_type.value}: {e}")
        
        return exported_files

def main():
    """Função principal"""
    logger.info("🚀 Iniciando geração de relatórios de compliance")
    
    generator = ComplianceReportGenerator()
    
    # Gerar todos os relatórios
    results = generator.generate_all_reports()
    
    # Resumo
    logger.info("📊 Resumo da geração de relatórios:")
    for report_type, files in results.items():
        logger.info(f"  {report_type}: {len(files)} arquivos gerados")
        for filepath in files:
            logger.info(f"    - {filepath}")
    
    logger.info("✅ Geração de relatórios concluída")

if __name__ == "__main__":
    main() 