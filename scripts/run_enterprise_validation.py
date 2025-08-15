#!/usr/bin/env python3
"""
Enterprise Validation Execution Script
Tracing ID: RUN_VALIDATION_ENTERPRISE_20250127_001

Script de execução automatizada da validação enterprise com:
- Execução programada
- Relatórios detalhados
- Notificações de status
- Integração com CI/CD
- Métricas de tendência
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Importações do sistema enterprise
from scripts.validate_enterprise_compliance import EnterpriseComplianceValidator
from shared.doc_generation_metrics import MetricsAnalyzer
from infrastructure.monitoring.doc_monitor import DocumentationMonitor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [%(name)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/enterprise_validation_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnterpriseValidationRunner:
    """
    Executor principal da validação enterprise.
    
    Gerencia execução, relatórios e notificações.
    """
    
    def __init__(self, config: Dict = None):
        self.tracing_id = f"RUN_VALIDATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config = config or self._load_default_config()
        self.start_time = time.time()
        self.results_history = []
        
        # Inicializar componentes
        self.metrics_analyzer = MetricsAnalyzer()
        self.doc_monitor = DocumentationMonitor()
        
        logger.info(f"[{self.tracing_id}] Iniciando executor de validação enterprise")
    
    def _load_default_config(self) -> Dict:
        """
        Carrega configuração padrão.
        
        Returns:
            Configuração padrão
        """
        return {
            "validation": {
                "timeout_seconds": 600,  # 10 minutos
                "retry_attempts": 3,
                "parallel_execution": True
            },
            "reporting": {
                "save_detailed_reports": True,
                "generate_trend_analysis": True,
                "notify_on_failure": True,
                "notify_on_success": False
            },
            "thresholds": {
                "min_quality_score": 0.85,
                "min_semantic_similarity": 0.85,
                "max_generation_time": 300,
                "max_tokens_consumed": 10000,
                "min_documentation_coverage": 0.95
            },
            "notifications": {
                "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),
                "email_recipients": os.getenv("VALIDATION_EMAIL_RECIPIENTS", "").split(","),
                "teams_webhook": os.getenv("TEAMS_WEBHOOK_URL")
            }
        }
    
    async def run_validation(self, validation_type: str = "full") -> Dict:
        """
        Executa validação enterprise.
        
        Args:
            validation_type: Tipo de validação ("full", "quick", "security_only")
            
        Returns:
            Resultados da validação
        """
        logger.info(f"[{self.tracing_id}] Executando validação tipo: {validation_type}")
        
        try:
            # Criar validador
            validator = EnterpriseComplianceValidator()
            
            # Executar validação com timeout
            if self.config["validation"]["parallel_execution"]:
                result = await asyncio.wait_for(
                    validator.run_complete_validation(),
                    timeout=self.config["validation"]["timeout_seconds"]
                )
            else:
                result = await validator.run_complete_validation()
            
            # Adicionar metadados
            result["validation_type"] = validation_type
            result["execution_timestamp"] = datetime.now().isoformat()
            result["config_used"] = self.config
            
            # Salvar resultados
            self._save_validation_results(result)
            
            # Analisar tendências
            if self.config["reporting"]["generate_trend_analysis"]:
                trend_analysis = await self._analyze_trends(result)
                result["trend_analysis"] = trend_analysis
            
            # Gerar relatórios
            if self.config["reporting"]["save_detailed_reports"]:
                await self._generate_detailed_reports(result)
            
            # Notificações
            await self._handle_notifications(result)
            
            logger.info(f"[{self.tracing_id}] Validação concluída com status: {result['status']}")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"[{self.tracing_id}] Timeout na validação após {self.config['validation']['timeout_seconds']}string_data")
            return {
                "status": "timeout",
                "error": f"Timeout após {self.config['validation']['timeout_seconds']} segundos",
                "validation_type": validation_type,
                "execution_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na validação: {e}")
            return {
                "status": "error",
                "error": str(e),
                "validation_type": validation_type,
                "execution_timestamp": datetime.now().isoformat()
            }
    
    def _save_validation_results(self, result: Dict):
        """
        Salva resultados da validação.
        
        Args:
            result: Resultados da validação
        """
        try:
            # Salvar resultado individual
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_results_{timestamp}.json"
            
            with open(f"logs/{filename}", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Adicionar ao histórico
            self.results_history.append(result)
            
            # Manter apenas os últimos 50 resultados
            if len(self.results_history) > 50:
                self.results_history = self.results_history[-50:]
            
            # Salvar histórico
            with open("logs/validation_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.results_history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[{self.tracing_id}] Resultados salvos em logs/{filename}")
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao salvar resultados: {e}")
    
    async def _analyze_trends(self, current_result: Dict) -> Dict:
        """
        Analisa tendências baseadas no histórico.
        
        Args:
            current_result: Resultado atual
            
        Returns:
            Análise de tendências
        """
        if len(self.results_history) < 2:
            return {"message": "Histórico insuficiente para análise de tendências"}
        
        try:
            # Carregar histórico se necessário
            if not self.results_history:
                history_file = Path("logs/validation_history.json")
                if history_file.exists():
                    with open(history_file, 'r', encoding='utf-8') as f:
                        self.results_history = json.load(f)
            
            # Analisar tendências
            trend_analysis = {
                "total_validations": len(self.results_history) + 1,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "common_violations": {},
                "quality_trend": "stable",
                "performance_trend": "stable",
                "security_trend": "stable"
            }
            
            # Calcular taxa de sucesso
            successful_runs = sum(1 for r in self.results_history if r.get("status") == "passed")
            trend_analysis["success_rate"] = successful_runs / len(self.results_history)
            
            # Calcular tempo médio de execução
            execution_times = [r.get("total_execution_time", 0) for r in self.results_history]
            if execution_times:
                trend_analysis["avg_execution_time"] = sum(execution_times) / len(execution_times)
            
            # Analisar violações comuns
            all_violations = []
            for result in self.results_history:
                all_violations.extend(result.get("violations", []))
            
            violation_counts = {}
            for violation in all_violations:
                violation_type = violation.get("type", "unknown")
                violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
            
            trend_analysis["common_violations"] = dict(
                sorted(violation_counts.items(), key=lambda value: value[1], reverse=True)[:5]
            )
            
            # Analisar tendências de qualidade
            quality_scores = []
            for result in self.results_history[-10:]:  # Últimos 10 resultados
                if "metrics" in result and "doc_quality" in result["metrics"]:
                    quality_data = result["metrics"]["doc_quality"]
                    if "doc_quality_scores" in quality_data:
                        scores = list(quality_data["doc_quality_scores"].values())
                        if scores:
                            quality_scores.append(sum(scores) / len(scores))
            
            if len(quality_scores) >= 2:
                if quality_scores[-1] > quality_scores[0] * 1.05:
                    trend_analysis["quality_trend"] = "improving"
                elif quality_scores[-1] < quality_scores[0] * 0.95:
                    trend_analysis["quality_trend"] = "declining"
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro na análise de tendências: {e}")
            return {"error": str(e)}
    
    async def _generate_detailed_reports(self, result: Dict):
        """
        Gera relatórios detalhados.
        
        Args:
            result: Resultados da validação
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Relatório executivo
            executive_report = self._generate_executive_report(result)
            with open(f"reports/executive_report_{timestamp}.md", 'w', encoding='utf-8') as f:
                f.write(executive_report)
            
            # Relatório técnico
            technical_report = self._generate_technical_report(result)
            with open(f"reports/technical_report_{timestamp}.md", 'w', encoding='utf-8') as f:
                f.write(technical_report)
            
            # Relatório de compliance
            compliance_report = self._generate_compliance_report(result)
            with open(f"reports/compliance_report_{timestamp}.md", 'w', encoding='utf-8') as f:
                f.write(compliance_report)
            
            logger.info(f"[{self.tracing_id}] Relatórios detalhados gerados")
            
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao gerar relatórios: {e}")
    
    def _generate_executive_report(self, result: Dict) -> str:
        """
        Gera relatório executivo.
        
        Args:
            result: Resultados da validação
            
        Returns:
            Relatório executivo em Markdown
        """
        status_emoji = "✅" if result["status"] == "passed" else "❌"
        
        report = f"""# Relatório Executivo - Validação Enterprise

**Tracing ID**: {result.get('validation_id', 'N/A')}  
**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}  
**Status**: {status_emoji} {result['status'].upper()}

## Resumo Executivo

- **Status Geral**: {result['status'].upper()}
- **Tempo de Execução**: {result.get('total_execution_time', 0):.2f} segundos
- **Violações Encontradas**: {len(result.get('violations', []))}
- **Recomendações**: {len(result.get('recommendations', []))}

## Métricas Principais

### Qualidade da Documentação
- **Score Médio**: {self._calculate_avg_quality_score(result):.2f}/1.0
- **Threshold**: {self.config['thresholds']['min_quality_score']}

### Performance
- **Tempo de Geração**: {result.get('metrics', {}).get('performance', {}).get('generation_time', 0):.2f}string_data
- **Tokens Consumidos**: {result.get('metrics', {}).get('performance', {}).get('tokens_consumed', 0):,}

### Segurança
- **Score de Segurança**: {result.get('metrics', {}).get('security', {}).get('security_score', 0):.2f}/1.0
- **Dados Sensíveis Encontrados**: {len(result.get('metrics', {}).get('security', {}).get('sensitive_data_found', []))}

### Compliance
- **PCI-DSS**: {'✅' if result.get('metrics', {}).get('compliance', {}).get('pci_dss_compliance') else '❌'}
- **LGPD**: {'✅' if result.get('metrics', {}).get('compliance', {}).get('lgpd_compliance') else '❌'}

## Principais Violações

"""
        
        violations = result.get('violations', [])
        if violations:
            for index, violation in enumerate(violations[:5], 1):
                report += f"{index}. **{violation.get('type', 'Unknown')}**: {violation}\n"
        else:
            report += "Nenhuma violação encontrada. ✅\n"
        
        report += f"""
## Recomendações

"""
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            for index, rec in enumerate(recommendations, 1):
                report += f"{index}. {rec}\n"
        else:
            report += "Nenhuma recomendação necessária. ✅\n"
        
        return report
    
    def _generate_technical_report(self, result: Dict) -> str:
        """
        Gera relatório técnico detalhado.
        
        Args:
            result: Resultados da validação
            
        Returns:
            Relatório técnico em Markdown
        """
        report = f"""# Relatório Técnico - Validação Enterprise

**Tracing ID**: {result.get('validation_id', 'N/A')}  
**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}  
**Status**: {result['status'].upper()}

## Detalhes Técnicos

### Configuração Utilizada
```json
{json.dumps(self.config, indent=2)}
```

### Métricas Detalhadas

#### Qualidade da Documentação
"""
        
        doc_quality = result.get('metrics', {}).get('doc_quality', {})
        if doc_quality:
            report += f"- **Scores por Arquivo**:\n"
            for file_path, score in list(doc_quality.get('doc_quality_scores', {}).items())[:10]:
                report += f"  - {file_path}: {score:.3f}\n"
        
        report += f"""
#### Similaridade Semântica
"""
        
        semantic = result.get('metrics', {}).get('semantic_similarity', {})
        if semantic:
            report += f"- **Similaridades por Função**:\n"
            for func_path, similarity in list(semantic.get('function_similarities', {}).items())[:10]:
                report += f"  - {func_path}: {similarity:.3f}\n"
        
        report += f"""
#### Segurança
"""
        
        security = result.get('metrics', {}).get('security', {})
        if security:
            report += f"- **Score de Segurança**: {security.get('security_score', 0):.3f}\n"
            report += f"- **Arquivos Sanitizados**: {len(security.get('sanitized_content', {}))}\n"
            
            sensitive_data = security.get('sensitive_data_found', [])
            if sensitive_data:
                report += f"- **Dados Sensíveis Encontrados**:\n"
                for data in sensitive_data[:5]:
                    report += f"  - {data['file']}: {data['sensitive_data']}\n"
        
        report += f"""
#### Sistema de Rollback
"""
        
        rollback = result.get('metrics', {}).get('rollback_system', {})
        if rollback:
            report += f"- **Criação de Snapshot**: {'✅' if rollback.get('snapshot_creation') else '❌'}\n"
            report += f"- **Restauração de Snapshot**: {'✅' if rollback.get('snapshot_restoration') else '❌'}\n"
            report += f"- **Detecção de Divergência**: {'✅' if rollback.get('divergence_detection') else '❌'}\n"
        
        return report
    
    def _generate_compliance_report(self, result: Dict) -> str:
        """
        Gera relatório de compliance.
        
        Args:
            result: Resultados da validação
            
        Returns:
            Relatório de compliance em Markdown
        """
        compliance = result.get('metrics', {}).get('compliance', {})
        
        report = f"""# Relatório de Compliance - Validação Enterprise

**Tracing ID**: {result.get('validation_id', 'N/A')}  
**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}

## Status de Compliance

### PCI-DSS
- **Status**: {'✅ Conforme' if compliance.get('pci_dss_compliance') else '❌ Não Conforme'}
- **Violações**: {len(compliance.get('violations', []))}

### LGPD
- **Status**: {'✅ Conforme' if compliance.get('lgpd_compliance') else '❌ Não Conforme'}
- **Violações**: {len(compliance.get('violations', []))}

### Auditoria de Segurança
- **Status**: {'✅ Aprovada' if compliance.get('security_audit') else '❌ Reprovada'}

## Violações Detalhadas

"""
        
        violations = compliance.get('violations', [])
        if violations:
            for index, violation in enumerate(violations, 1):
                report += f"{index}. {violation}\n"
        else:
            report += "Nenhuma violação de compliance encontrada. ✅\n"
        
        return report
    
    def _calculate_avg_quality_score(self, result: Dict) -> float:
        """
        Calcula score médio de qualidade.
        
        Args:
            result: Resultados da validação
            
        Returns:
            Score médio
        """
        doc_quality = result.get('metrics', {}).get('doc_quality', {})
        scores = list(doc_quality.get('doc_quality_scores', {}).values())
        
        if scores:
            return sum(scores) / len(scores)
        return 0.0
    
    async def _handle_notifications(self, result: Dict):
        """
        Gerencia notificações baseadas no resultado.
        
        Args:
            result: Resultados da validação
        """
        try:
            should_notify = (
                (result['status'] == 'failed' and self.config['reporting']['notify_on_failure']) or
                (result['status'] == 'passed' and self.config['reporting']['notify_on_success'])
            )
            
            if should_notify:
                await self._send_notifications(result)
                
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao enviar notificações: {e}")
    
    async def _send_notifications(self, result: Dict):
        """
        Envia notificações para canais configurados.
        
        Args:
            result: Resultados da validação
        """
        # Slack
        if self.config['notifications']['slack_webhook']:
            await self._send_slack_notification(result)
        
        # Email
        if self.config['notifications']['email_recipients']:
            await self._send_email_notification(result)
        
        # Teams
        if self.config['notifications']['teams_webhook']:
            await self._send_teams_notification(result)
    
    async def _send_slack_notification(self, result: Dict):
        """Envia notificação para Slack."""
        try:
            import aiohttp
            
            status_emoji = "✅" if result['status'] == 'passed' else "❌"
            
            message = {
                "text": f"Enterprise Validation {status_emoji}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Enterprise Validation {status_emoji}*\n"
                                   f"Status: {result['status'].upper()}\n"
                                   f"Violations: {len(result.get('violations', []))}\n"
                                   f"Execution Time: {result.get('total_execution_time', 0):.2f}string_data"
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config['notifications']['slack_webhook'],
                    json=message
                ) as response:
                    if response.status == 200:
                        logger.info(f"[{self.tracing_id}] Notificação Slack enviada")
                    else:
                        logger.error(f"[{self.tracing_id}] Erro ao enviar notificação Slack: {response.status}")
                        
        except Exception as e:
            logger.error(f"[{self.tracing_id}] Erro ao enviar notificação Slack: {e}")
    
    async def _send_email_notification(self, result: Dict):
        """Envia notificação por email."""
        # Implementação de email seria adicionada aqui
        logger.info(f"[{self.tracing_id}] Notificação por email seria enviada")
    
    async def _send_teams_notification(self, result: Dict):
        """Envia notificação para Microsoft Teams."""
        # Implementação do Teams seria adicionada aqui
        logger.info(f"[{self.tracing_id}] Notificação Teams seria enviada")


async def main():
    """
    Função principal de execução.
    """
    parser = argparse.ArgumentParser(description="Enterprise Validation Runner")
    parser.add_argument(
        "--type", 
        choices=["full", "quick", "security_only"],
        default="full",
        help="Tipo de validação a executar"
    )
    parser.add_argument(
        "--config",
        help="Arquivo de configuração JSON"
    )
    parser.add_argument(
        "--retry",
        type=int,
        default=3,
        help="Número de tentativas em caso de falha"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout em segundos"
    )
    
    args = parser.parse_args()
    
    # Carregar configuração
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return 1
    
    # Criar executor
    runner = EnterpriseValidationRunner(config)
    
    # Ajustar configuração baseada em argumentos
    if args.timeout:
        runner.config["validation"]["timeout_seconds"] = args.timeout
    if args.retry:
        runner.config["validation"]["retry_attempts"] = args.retry
    
    # Executar validação com retry
    for attempt in range(runner.config["validation"]["retry_attempts"]):
        try:
            result = await runner.run_validation(args.type)
            
            if result["status"] in ["passed", "failed"]:
                return 0 if result["status"] == "passed" else 1
            else:
                logger.warning(f"Tentativa {attempt + 1} falhou: {result['status']}")
                if attempt < runner.config["validation"]["retry_attempts"] - 1:
                    await asyncio.sleep(5)  # Aguardar 5 segundos antes de tentar novamente
                    
        except Exception as e:
            logger.error(f"Erro na tentativa {attempt + 1}: {e}")
            if attempt < runner.config["validation"]["retry_attempts"] - 1:
                await asyncio.sleep(5)
    
    logger.error("Todas as tentativas falharam")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 