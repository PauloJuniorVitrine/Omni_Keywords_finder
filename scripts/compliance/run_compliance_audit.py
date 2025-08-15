#!/usr/bin/env python3
"""
🔍 COMPLIANCE AUDIT SYSTEM - OMNİ KEYWORDS FINDER

Tracing ID: COMPLIANCE_AUDIT_2025_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de auditoria completa de compliance.
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
import subprocess
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [COMPLIANCE_AUDIT] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/compliance_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuditType(Enum):
    """Tipos de auditoria"""
    COMPLIANCE = "compliance"
    SECURITY = "security"
    PRIVACY = "privacy"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"

class AuditStatus(Enum):
    """Status de auditoria"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AuditSeverity(Enum):
    """Severidade de achados"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditFinding:
    """Achado de auditoria"""
    id: str
    title: str
    description: str
    severity: AuditSeverity
    framework: str
    requirement_id: str
    evidence: str
    recommendation: str
    status: str = "open"
    created_at: datetime = None
    resolved_at: Optional[datetime] = None

@dataclass
class AuditReport:
    """Relatório de auditoria"""
    audit_id: str
    audit_type: AuditType
    framework: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: AuditStatus = AuditStatus.PENDING
    findings: List[AuditFinding] = None
    overall_score: float = 0.0
    compliance_score: float = 0.0
    security_score: float = 0.0
    privacy_score: float = 0.0
    recommendations: List[str] = None

class ComplianceAuditor:
    """Auditor de compliance"""
    
    def __init__(self):
        self.tracing_id = f"COMPLIANCE_AUDITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.audit_reports: Dict[str, AuditReport] = {}
        self.audit_dir = Path("audits/compliance")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
    def create_audit(self, audit_type: AuditType, framework: str) -> str:
        """Cria nova auditoria"""
        audit_id = f"AUDIT_{audit_type.value.upper()}_{framework}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        audit_report = AuditReport(
            audit_id=audit_id,
            audit_type=audit_type,
            framework=framework,
            started_at=datetime.now(),
            findings=[],
            recommendations=[]
        )
        
        self.audit_reports[audit_id] = audit_report
        logger.info(f"✅ Auditoria criada: {audit_id}")
        
        return audit_id
    
    def audit_gdpr_compliance(self, audit_id: str) -> List[AuditFinding]:
        """Audita compliance GDPR"""
        findings = []
        
        # Verificar política de proteção de dados
        policy_file = Path("docs/compliance/gdpr/data_protection_policy.md")
        if not policy_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_GDPR_001",
                title="Política de Proteção de Dados Ausente",
                description="Documento de política de proteção de dados não encontrado",
                severity=AuditSeverity.CRITICAL,
                framework="GDPR",
                requirement_id="GDPR-001",
                evidence="Arquivo docs/compliance/gdpr/data_protection_policy.md não existe",
                recommendation="Criar política de proteção de dados completa"
            ))
        else:
            logger.info("✅ Política de proteção de dados encontrada")
        
        # Verificar registro de processamento
        register_file = Path("docs/compliance/gdpr/data_processing_register.md")
        if not register_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_GDPR_002",
                title="Registro de Processamento Ausente",
                description="Registro de atividades de processamento não encontrado",
                severity=AuditSeverity.HIGH,
                framework="GDPR",
                requirement_id="GDPR-002",
                evidence="Arquivo docs/compliance/gdpr/data_processing_register.md não existe",
                recommendation="Criar registro de processamento de dados"
            ))
        else:
            logger.info("✅ Registro de processamento encontrado")
        
        # Verificar sistema de direitos dos titulares
        rights_file = Path("scripts/compliance/data_subject_rights.py")
        if not rights_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_GDPR_003",
                title="Sistema de Direitos dos Titulares Ausente",
                description="Implementação dos direitos GDPR não encontrada",
                severity=AuditSeverity.CRITICAL,
                framework="GDPR",
                requirement_id="GDPR-003",
                evidence="Arquivo scripts/compliance/data_subject_rights.py não existe",
                recommendation="Implementar sistema de direitos dos titulares"
            ))
        else:
            logger.info("✅ Sistema de direitos dos titulares encontrado")
        
        # Verificar sistema de notificação de violações
        breach_file = Path("scripts/compliance/breach_notification.py")
        if not breach_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_GDPR_004",
                title="Sistema de Notificação de Violações Ausente",
                description="Sistema de notificação de violações não encontrado",
                severity=AuditSeverity.HIGH,
                framework="GDPR",
                requirement_id="GDPR-004",
                evidence="Arquivo scripts/compliance/breach_notification.py não existe",
                recommendation="Implementar sistema de notificação de violações"
            ))
        else:
            logger.info("✅ Sistema de notificação de violações encontrado")
        
        return findings
    
    def audit_lgpd_compliance(self, audit_id: str) -> List[AuditFinding]:
        """Audita compliance LGPD"""
        findings = []
        
        # Verificar base legal
        legal_file = Path("docs/compliance/lgpd/legal_basis.md")
        if not legal_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_LGPD_001",
                title="Base Legal Ausente",
                description="Documentação de base legal não encontrada",
                severity=AuditSeverity.CRITICAL,
                framework="LGPD",
                requirement_id="LGPD-001",
                evidence="Arquivo docs/compliance/lgpd/legal_basis.md não existe",
                recommendation="Documentar base legal para processamento de dados"
            ))
        else:
            logger.info("✅ Base legal encontrada")
        
        # Verificar política de retenção
        retention_file = Path("docs/compliance/lgpd/data_retention.md")
        if not retention_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_LGPD_002",
                title="Política de Retenção Ausente",
                description="Política de retenção de dados não encontrada",
                severity=AuditSeverity.HIGH,
                framework="LGPD",
                requirement_id="LGPD-002",
                evidence="Arquivo docs/compliance/lgpd/data_retention.md não existe",
                recommendation="Criar política de retenção de dados"
            ))
        else:
            logger.info("✅ Política de retenção encontrada")
        
        return findings
    
    def audit_soc2_compliance(self, audit_id: str) -> List[AuditFinding]:
        """Audita compliance SOC 2"""
        findings = []
        
        # Verificar objetivos de controle
        controls_file = Path("docs/compliance/soc2/control_objectives.md")
        if not controls_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_SOC2_001",
                title="Objetivos de Controle Ausentes",
                description="Documentação de objetivos de controle SOC 2 não encontrada",
                severity=AuditSeverity.HIGH,
                framework="SOC2",
                requirement_id="SOC2-001",
                evidence="Arquivo docs/compliance/soc2/control_objectives.md não existe",
                recommendation="Documentar objetivos de controle SOC 2"
            ))
        else:
            logger.info("✅ Objetivos de controle SOC 2 encontrados")
        
        # Verificar atividades de controle
        activities_file = Path("docs/compliance/soc2/control_activities.md")
        if not activities_file.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_SOC2_002",
                title="Atividades de Controle Ausentes",
                description="Documentação de atividades de controle não encontrada",
                severity=AuditSeverity.HIGH,
                framework="SOC2",
                requirement_id="SOC2-002",
                evidence="Arquivo docs/compliance/soc2/control_activities.md não existe",
                recommendation="Documentar atividades de controle"
            ))
        else:
            logger.info("✅ Atividades de controle encontradas")
        
        return findings
    
    def audit_security_controls(self, audit_id: str) -> List[AuditFinding]:
        """Audita controles de segurança"""
        findings = []
        
        # Verificar política de segurança
        security_policy = Path("docs/compliance/iso27001/information_security_policy.md")
        if not security_policy.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_SEC_001",
                title="Política de Segurança Ausente",
                description="Política de segurança da informação não encontrada",
                severity=AuditSeverity.CRITICAL,
                framework="ISO27001",
                requirement_id="ISO27001-001",
                evidence="Arquivo docs/compliance/iso27001/information_security_policy.md não existe",
                recommendation="Criar política de segurança da informação"
            ))
        else:
            logger.info("✅ Política de segurança encontrada")
        
        # Verificar avaliação de riscos
        risk_assessment = Path("docs/compliance/iso27001/risk_assessment.md")
        if not risk_assessment.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_SEC_002",
                title="Avaliação de Riscos Ausente",
                description="Documentação de avaliação de riscos não encontrada",
                severity=AuditSeverity.HIGH,
                framework="ISO27001",
                requirement_id="ISO27001-002",
                evidence="Arquivo docs/compliance/iso27001/risk_assessment.md não existe",
                recommendation="Realizar avaliação de riscos de segurança"
            ))
        else:
            logger.info("✅ Avaliação de riscos encontrada")
        
        return findings
    
    def audit_operational_controls(self, audit_id: str) -> List[AuditFinding]:
        """Audita controles operacionais"""
        findings = []
        
        # Verificar monitoramento
        monitoring_script = Path("scripts/compliance/monitor_compliance.py")
        if not monitoring_script.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_OPS_001",
                title="Sistema de Monitoramento Ausente",
                description="Sistema de monitoramento de compliance não encontrado",
                severity=AuditSeverity.HIGH,
                framework="OPERATIONAL",
                requirement_id="OPS-001",
                evidence="Arquivo scripts/compliance/monitor_compliance.py não existe",
                recommendation="Implementar sistema de monitoramento contínuo"
            ))
        else:
            logger.info("✅ Sistema de monitoramento encontrado")
        
        # Verificar relatórios
        report_script = Path("scripts/compliance/generate_compliance_report.py")
        if not report_script.exists():
            findings.append(AuditFinding(
                id=f"{audit_id}_OPS_002",
                title="Sistema de Relatórios Ausente",
                description="Sistema de geração de relatórios não encontrado",
                severity=AuditSeverity.MEDIUM,
                framework="OPERATIONAL",
                requirement_id="OPS-002",
                evidence="Arquivo scripts/compliance/generate_compliance_report.py não existe",
                recommendation="Implementar sistema de geração de relatórios"
            ))
        else:
            logger.info("✅ Sistema de relatórios encontrado")
        
        return findings
    
    def calculate_audit_scores(self, findings: List[AuditFinding]) -> Dict[str, float]:
        """Calcula scores de auditoria"""
        if not findings:
            return {
                "overall": 100.0,
                "compliance": 100.0,
                "security": 100.0,
                "privacy": 100.0
            }
        
        # Pesos por severidade
        severity_weights = {
            AuditSeverity.LOW: 1,
            AuditSeverity.MEDIUM: 3,
            AuditSeverity.HIGH: 5,
            AuditSeverity.CRITICAL: 10
        }
        
        total_weight = 0
        weighted_score = 0
        
        for finding in findings:
            weight = severity_weights[finding.severity]
            total_weight += weight
            weighted_score += weight * 0  # Cada finding reduz o score
        
        if total_weight == 0:
            overall_score = 100.0
        else:
            overall_score = max(0.0, 100.0 - (weighted_score / total_weight) * 100)
        
        # Scores por categoria
        compliance_findings = [f for f in findings if f.framework in ["GDPR", "LGPD", "SOC2"]]
        security_findings = [f for f in findings if f.framework in ["ISO27001", "PCI_DSS"]]
        privacy_findings = [f for f in findings if f.framework in ["GDPR", "LGPD"]]
        
        compliance_score = self._calculate_category_score(compliance_findings, severity_weights)
        security_score = self._calculate_category_score(security_findings, severity_weights)
        privacy_score = self._calculate_category_score(privacy_findings, severity_weights)
        
        return {
            "overall": overall_score,
            "compliance": compliance_score,
            "security": security_score,
            "privacy": privacy_score
        }
    
    def _calculate_category_score(self, findings: List[AuditFinding], severity_weights: Dict) -> float:
        """Calcula score para uma categoria específica"""
        if not findings:
            return 100.0
        
        total_weight = 0
        weighted_score = 0
        
        for finding in findings:
            weight = severity_weights[finding.severity]
            total_weight += weight
            weighted_score += weight * 0
        
        if total_weight == 0:
            return 100.0
        
        return max(0.0, 100.0 - (weighted_score / total_weight) * 100)
    
    def generate_recommendations(self, findings: List[AuditFinding]) -> List[str]:
        """Gera recomendações baseadas nos achados"""
        recommendations = []
        
        # Agrupar por severidade
        critical_findings = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
        high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]
        medium_findings = [f for f in findings if f.severity == AuditSeverity.MEDIUM]
        
        if critical_findings:
            recommendations.append(f"RESOLVER URGENTEMENTE {len(critical_findings)} achados críticos")
        
        if high_findings:
            recommendations.append(f"Priorizar resolução de {len(high_findings)} achados de alta severidade")
        
        if medium_findings:
            recommendations.append(f"Planejar correção de {len(medium_findings)} achados de média severidade")
        
        # Recomendações específicas
        for finding in findings[:5]:  # Top 5 achados
            recommendations.append(f"Corrigir: {finding.title}")
        
        return recommendations
    
    def run_complete_audit(self, audit_type: AuditType = AuditType.COMPLIANCE) -> str:
        """Executa auditoria completa"""
        audit_id = self.create_audit(audit_type, "ALL")
        audit_report = self.audit_reports[audit_id]
        
        logger.info(f"🔍 Iniciando auditoria completa: {audit_id}")
        audit_report.status = AuditStatus.IN_PROGRESS
        
        all_findings = []
        
        # Auditoria GDPR
        logger.info("📋 Auditando compliance GDPR...")
        gdpr_findings = self.audit_gdpr_compliance(audit_id)
        all_findings.extend(gdpr_findings)
        
        # Auditoria LGPD
        logger.info("📋 Auditando compliance LGPD...")
        lgpd_findings = self.audit_lgpd_compliance(audit_id)
        all_findings.extend(lgpd_findings)
        
        # Auditoria SOC 2
        logger.info("📋 Auditando compliance SOC 2...")
        soc2_findings = self.audit_soc2_compliance(audit_id)
        all_findings.extend(soc2_findings)
        
        # Auditoria de Segurança
        logger.info("🔒 Auditando controles de segurança...")
        security_findings = self.audit_security_controls(audit_id)
        all_findings.extend(security_findings)
        
        # Auditoria Operacional
        logger.info("⚙️ Auditando controles operacionais...")
        operational_findings = self.audit_operational_controls(audit_id)
        all_findings.extend(operational_findings)
        
        # Calcular scores
        scores = self.calculate_audit_scores(all_findings)
        
        # Atualizar relatório
        audit_report.findings = all_findings
        audit_report.overall_score = scores["overall"]
        audit_report.compliance_score = scores["compliance"]
        audit_report.security_score = scores["security"]
        audit_report.privacy_score = scores["privacy"]
        audit_report.recommendations = self.generate_recommendations(all_findings)
        audit_report.completed_at = datetime.now()
        audit_report.status = AuditStatus.COMPLETED
        
        # Salvar relatório
        self.save_audit_report(audit_report)
        
        logger.info(f"✅ Auditoria concluída: {audit_id}")
        logger.info(f"📊 Score geral: {audit_report.overall_score:.1f}%")
        logger.info(f"🔍 Achados: {len(all_findings)}")
        
        return audit_id
    
    def save_audit_report(self, audit_report: AuditReport):
        """Salva relatório de auditoria"""
        report_data = {
            "audit_id": audit_report.audit_id,
            "audit_type": audit_report.audit_type.value,
            "framework": audit_report.framework,
            "started_at": audit_report.started_at.isoformat(),
            "completed_at": audit_report.completed_at.isoformat() if audit_report.completed_at else None,
            "status": audit_report.status.value,
            "overall_score": audit_report.overall_score,
            "compliance_score": audit_report.compliance_score,
            "security_score": audit_report.security_score,
            "privacy_score": audit_report.privacy_score,
            "findings": [asdict(finding) for finding in audit_report.findings],
            "recommendations": audit_report.recommendations
        }
        
        # Salvar em JSON
        report_file = self.audit_dir / f"{audit_report.audit_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Salvar resumo em Markdown
        summary_file = self.audit_dir / f"{audit_report.audit_id}.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# 🔍 Relatório de Auditoria - {audit_report.audit_id}\n\n")
            f.write(f"**Tipo**: {audit_report.audit_type.value}\n")
            f.write(f"**Framework**: {audit_report.framework}\n")
            f.write(f"**Início**: {audit_report.started_at.strftime('%Y-%m-%data %H:%M:%S')}\n")
            f.write(f"**Conclusão**: {audit_report.completed_at.strftime('%Y-%m-%data %H:%M:%S') if audit_report.completed_at else 'Em andamento'}\n\n")
            
            f.write(f"## 📊 Scores\n\n")
            f.write(f"- **Score Geral**: {audit_report.overall_score:.1f}%\n")
            f.write(f"- **Compliance**: {audit_report.compliance_score:.1f}%\n")
            f.write(f"- **Segurança**: {audit_report.security_score:.1f}%\n")
            f.write(f"- **Privacidade**: {audit_report.privacy_score:.1f}%\n\n")
            
            f.write(f"## 🔍 Achados ({len(audit_report.findings)})\n\n")
            for finding in audit_report.findings:
                f.write(f"### {finding.title}\n")
                f.write(f"- **Severidade**: {finding.severity.value}\n")
                f.write(f"- **Framework**: {finding.framework}\n")
                f.write(f"- **Descrição**: {finding.description}\n")
                f.write(f"- **Recomendação**: {finding.recommendation}\n\n")
            
            f.write(f"## 💡 Recomendações\n\n")
            for rec in audit_report.recommendations:
                f.write(f"- {rec}\n")
        
        logger.info(f"📄 Relatório salvo: {report_file}")
        logger.info(f"📄 Resumo salvo: {summary_file}")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando auditoria completa de compliance")
    
    auditor = ComplianceAuditor()
    
    # Executar auditoria completa
    audit_id = auditor.run_complete_audit()
    
    # Resumo final
    audit_report = auditor.audit_reports[audit_id]
    logger.info("📊 RESUMO DA AUDITORIA:")
    logger.info(f"  Score Geral: {audit_report.overall_score:.1f}%")
    logger.info(f"  Achados: {len(audit_report.findings)}")
    logger.info(f"  Críticos: {len([f for f in audit_report.findings if f.severity == AuditSeverity.CRITICAL])}")
    logger.info(f"  Altos: {len([f for f in audit_report.findings if f.severity == AuditSeverity.HIGH])}")
    
    logger.info("✅ Auditoria concluída")

if __name__ == "__main__":
    main() 