#!/usr/bin/env python3
"""
Sistema de Monitoramento de Documentação Enterprise
==================================================

Tracing ID: DOC_MONITOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação

Objetivo: Monitorar mudanças na documentação, detectar divergências semânticas
e gerar alertas automáticos para manutenção da qualidade.
"""

import os
import sys
import json
import logging
import hashlib
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
# Importações opcionais para monitoramento de arquivos
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
from collections import defaultdict, deque

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService
    from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
    from infrastructure.security.advanced_security_system import SensitiveDataDetector
    from shared.doc_generation_metrics import MetricsCollector, MetricsAnalyzer
    from shared.trigger_config_validator import TriggerConfigValidator
    from scripts.validate_doc_compliance import DocComplianceValidator
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que todos os módulos estão implementados")
    sys.exit(1)


@dataclass
class FileChange:
    """Representa uma mudança em arquivo"""
    timestamp: str
    file_path: str
    change_type: str  # 'created', 'modified', 'deleted'
    file_hash: str
    file_size: int
    quality_score: Optional[float] = None
    security_issues: List[Dict] = None
    semantic_similarity: Optional[float] = None


@dataclass
class MonitoringAlert:
    """Alerta de monitoramento"""
    timestamp: str
    alert_id: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str  # 'quality', 'security', 'compliance', 'performance'
    message: str
    file_path: Optional[str] = None
    details: Dict[str, Any] = None
    resolved: bool = False


@dataclass
class MonitoringReport:
    """Relatório de monitoramento"""
    timestamp: str
    monitoring_id: str
    duration: float
    files_monitored: int
    changes_detected: int
    alerts_generated: int
    quality_score: float
    security_score: float
    compliance_score: float
    changes: List[FileChange]
    alerts: List[MonitoringAlert]
    metrics: Dict[str, Any]


class DocumentChangeHandler(FileSystemEventHandler):
    """
    Handler para eventos de mudança de arquivos
    """
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.logger = logging.getLogger(f"DocumentChangeHandler_{monitor.tracing_id}")
    
    def on_created(self, event):
        """Arquivo criado"""
        if not event.is_directory and self._should_monitor_file(event.src_path):
            self.logger.info(f"[{self.monitor.tracing_id}] Arquivo criado: {event.src_path}")
            self.monitor.handle_file_change(event.src_path, 'created')
    
    def on_modified(self, event):
        """Arquivo modificado"""
        if not event.is_directory and self._should_monitor_file(event.src_path):
            self.logger.info(f"[{self.monitor.tracing_id}] Arquivo modificado: {event.src_path}")
            self.monitor.handle_file_change(event.src_path, 'modified')
    
    def on_deleted(self, event):
        """Arquivo deletado"""
        if not event.is_directory and self._should_monitor_file(event.src_path):
            self.logger.info(f"[{self.monitor.tracing_id}] Arquivo deletado: {event.src_path}")
            self.monitor.handle_file_change(event.src_path, 'deleted')
    
    def _should_monitor_file(self, file_path: str) -> bool:
        """Verificar se arquivo deve ser monitorado"""
        path = Path(file_path)
        
        # Verificar extensões
        if path.suffix.lower() not in ['.md', '.py', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml']:
            return False
        
        # Verificar padrões de exclusão
        exclude_patterns = [
            'node_modules',
            '__pycache__',
            '.git',
            '.vscode',
            'logs',
            'coverage',
            'htmlcov'
        ]
        
        for pattern in exclude_patterns:
            if pattern in str(path):
                return False
        
        return True


class DocumentationMonitor:
    """
    Monitor principal de documentação enterprise
    """
    
    def __init__(self, 
                 docs_path: str = "docs/",
                 config_path: str = "docs/trigger_config.json",
                 alert_threshold: float = 0.85,
                 check_interval: int = 300):  # 5 minutos
        
        self.docs_path = Path(docs_path)
        self.config_path = config_path
        self.alert_threshold = alert_threshold
        self.check_interval = check_interval
        
        self.tracing_id = f"DOC_MONITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.setup_logging()
        
        # Inicializar serviços
        self.initialize_services()
        
        # Estado do monitoramento
        self.is_monitoring = False
        self.observer = None
        self.change_handler = None
        
        # Histórico e cache
        self.file_hashes = {}  # Cache de hashes
        self.change_history = deque(maxlen=1000)  # Histórico de mudanças
        self.alert_history = deque(maxlen=500)  # Histórico de alertas
        
        # Métricas
        self.metrics_collector = MetricsCollector()
        self.metrics_analyzer = MetricsAnalyzer()
        
        # Threading
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        self.logger.info(f"[{self.tracing_id}] Inicializado monitor de documentação")
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        self.logger = logging.getLogger(f"DocumentationMonitor_{self.tracing_id}")
        self.logger.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Handler para arquivo
        log_dir = Path("logs/monitoring")
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"doc_monitor_{self.tracing_id}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter(
            '[%(levelname)string_data] [%(name)string_data] %(message)string_data - %(asctime)string_data'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def initialize_services(self):
        """Inicializar todos os serviços necessários"""
        try:
            self.logger.info(f"[{self.tracing_id}] Inicializando serviços...")
            
            # Serviços de análise
            self.semantic_service = SemanticEmbeddingService()
            self.quality_analyzer = DocQualityAnalyzer()
            self.security_detector = SensitiveDataDetector()
            
            # Validadores
            self.trigger_validator = TriggerConfigValidator()
            self.compliance_checker = DocComplianceValidator()
            
            self.logger.info(f"[{self.tracing_id}] Todos os serviços inicializados")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro na inicialização: {str(e)}")
            raise
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calcular hash do arquivo"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao calcular hash de {file_path}: {str(e)}")
            return ""
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Obter informações do arquivo"""
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': path.exists()
            }
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao obter info de {file_path}: {str(e)}")
            return {}
    
    def analyze_file_quality(self, file_path: str) -> float:
        """Analisar qualidade do arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            quality_score = self.quality_analyzer.calculate_doc_quality_score(content)
            return quality_score
            
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao analisar qualidade de {file_path}: {str(e)}")
            return 0.0
    
    def scan_file_security(self, file_path: str) -> List[Dict]:
        """Escanear arquivo em busca de dados sensíveis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            security_issues = self.security_detector.scan_documentation(content)
            return security_issues
            
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao escanear segurança de {file_path}: {str(e)}")
            return []
    
    def calculate_semantic_similarity(self, file_path: str) -> float:
        """Calcular similaridade semântica"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Comparar com versão anterior se existir
            if file_path in self.file_hashes:
                # Aqui seria implementada a comparação semântica
                # Por enquanto, retorna um valor padrão
                return 0.85
            
            return 1.0  # Novo arquivo
            
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao calcular similaridade de {file_path}: {str(e)}")
            return 0.0
    
    def handle_file_change(self, file_path: str, change_type: str):
        """Processar mudança de arquivo"""
        try:
            self.logger.info(f"[{self.tracing_id}] Processando mudança: {change_type} - {file_path}")
            
            # Obter informações do arquivo
            file_info = self.get_file_info(file_path)
            if not file_info:
                return
            
            # Calcular hash
            file_hash = self.calculate_file_hash(file_path) if change_type != 'deleted' else ""
            
            # Analisar qualidade (apenas para arquivos markdown)
            quality_score = None
            if change_type != 'deleted' and Path(file_path).suffix.lower() == '.md':
                quality_score = self.analyze_file_quality(file_path)
            
            # Escanear segurança
            security_issues = []
            if change_type != 'deleted':
                security_issues = self.scan_file_security(file_path)
            
            # Calcular similaridade semântica
            semantic_similarity = None
            if change_type != 'deleted':
                semantic_similarity = self.calculate_semantic_similarity(file_path)
            
            # Criar registro de mudança
            change = FileChange(
                timestamp=datetime.now().isoformat(),
                file_path=file_path,
                change_type=change_type,
                file_hash=file_hash,
                file_size=file_info.get('size', 0),
                quality_score=quality_score,
                security_issues=security_issues,
                semantic_similarity=semantic_similarity
            )
            
            # Adicionar ao histórico
            self.change_history.append(change)
            
            # Atualizar cache de hashes
            if change_type != 'deleted':
                self.file_hashes[file_path] = file_hash
            elif file_path in self.file_hashes:
                del self.file_hashes[file_path]
            
            # Gerar alertas se necessário
            self.generate_alerts_for_change(change)
            
            # Coletar métricas
            self.collect_change_metrics(change)
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao processar mudança: {str(e)}")
    
    def generate_alerts_for_change(self, change: FileChange):
        """Gerar alertas baseados na mudança"""
        alerts = []
        
        # Alerta de qualidade baixa
        if change.quality_score is not None and change.quality_score < self.alert_threshold:
            alert = MonitoringAlert(
                timestamp=datetime.now().isoformat(),
                alert_id=f"QUALITY_{change.file_path}_{int(time.time())}",
                severity='medium',
                category='quality',
                message=f"Qualidade baixa detectada: {change.quality_score:.2f}",
                file_path=change.file_path,
                details={'quality_score': change.quality_score, 'threshold': self.alert_threshold}
            )
            alerts.append(alert)
        
        # Alerta de dados sensíveis
        if change.security_issues:
            alert = MonitoringAlert(
                timestamp=datetime.now().isoformat(),
                alert_id=f"SECURITY_{change.file_path}_{int(time.time())}",
                severity='critical',
                category='security',
                message=f"Dados sensíveis detectados: {len(change.security_issues)} incidentes",
                file_path=change.file_path,
                details={'security_issues': change.security_issues}
            )
            alerts.append(alert)
        
        # Alerta de similaridade semântica baixa
        if change.semantic_similarity is not None and change.semantic_similarity < 0.8:
            alert = MonitoringAlert(
                timestamp=datetime.now().isoformat(),
                alert_id=f"SEMANTIC_{change.file_path}_{int(time.time())}",
                severity='low',
                category='quality',
                message=f"Similaridade semântica baixa: {change.semantic_similarity:.2f}",
                file_path=change.file_path,
                details={'semantic_similarity': change.semantic_similarity}
            )
            alerts.append(alert)
        
        # Adicionar alertas ao histórico
        for alert in alerts:
            self.alert_history.append(alert)
            self.logger.warning(f"[{self.tracing_id}] Alerta gerado: {alert.message}")
    
    def collect_change_metrics(self, change: FileChange):
        """Coletar métricas da mudança"""
        try:
            metrics = {
                'change_type': change.change_type,
                'file_size': change.file_size,
                'quality_score': change.quality_score,
                'security_issues_count': len(change.security_issues) if change.security_issues else 0,
                'semantic_similarity': change.semantic_similarity
            }
            
            self.metrics_collector.collect_metrics(
                operation="file_change_monitoring",
                duration=0.1,  # Tempo estimado
                success=True,
                data_size=len(json.dumps(metrics)),
                tokens_used=0,
                additional_metrics=metrics
            )
            
        except Exception as e:
            self.logger.warning(f"[{self.tracing_id}] Erro ao coletar métricas: {str(e)}")
    
    def detect_divergences(self) -> List[Dict[str, Any]]:
        """Detectar divergências na documentação"""
        try:
            self.logger.info(f"[{self.tracing_id}] Detectando divergências...")
            
            divergences = []
            
            # Verificar compliance
            compliance_report = self.compliance_checker.run_validation(str(self.docs_path))
            
            if compliance_report.status == "FAIL":
                divergences.append({
                    'type': 'compliance_failure',
                    'severity': 'critical',
                    'description': f'Falha de compliance: {compliance_report.status}',
                    'details': {
                        'quality_score': compliance_report.quality_score,
                        'security_score': compliance_report.security_score,
                        'compliance_score': compliance_report.compliance_score
                    }
                })
            
            # Verificar qualidade geral
            if compliance_report.quality_score < self.alert_threshold:
                divergences.append({
                    'type': 'quality_degradation',
                    'severity': 'medium',
                    'description': f'Degradação de qualidade: {compliance_report.quality_score:.2f}',
                    'details': {'quality_score': compliance_report.quality_score}
                })
            
            # Verificar mudanças frequentes
            recent_changes = [c for c in self.change_history 
                            if datetime.fromisoformat(c.timestamp) > datetime.now() - timedelta(hours=1)]
            
            if len(recent_changes) > 10:  # Mais de 10 mudanças por hora
                divergences.append({
                    'type': 'high_change_rate',
                    'severity': 'low',
                    'description': f'Alta taxa de mudanças: {len(recent_changes)} em 1 hora',
                    'details': {'change_count': len(recent_changes)}
                })
            
            # Verificar alertas não resolvidos
            unresolved_alerts = [a for a in self.alert_history if not a.resolved]
            critical_alerts = [a for a in unresolved_alerts if a.severity == 'critical']
            
            if critical_alerts:
                divergences.append({
                    'type': 'unresolved_critical_alerts',
                    'severity': 'critical',
                    'description': f'Alertas críticos não resolvidos: {len(critical_alerts)}',
                    'details': {'alert_count': len(critical_alerts)}
                })
            
            self.logger.info(f"[{self.tracing_id}] {len(divergences)} divergências detectadas")
            return divergences
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao detectar divergências: {str(e)}")
            return []
    
    def generate_monitoring_report(self, duration: float) -> MonitoringReport:
        """Gerar relatório de monitoramento"""
        try:
            # Calcular estatísticas
            files_monitored = len(self.file_hashes)
            changes_detected = len(self.change_history)
            alerts_generated = len(self.alert_history)
            
            # Obter scores atuais
            compliance_report = self.compliance_checker.run_validation(str(self.docs_path))
            
            # Coletar métricas
            metrics = self.metrics_collector.collect_all_metrics()
            
            # Criar relatório
            report = MonitoringReport(
                timestamp=datetime.now().isoformat(),
                monitoring_id=self.tracing_id,
                duration=duration,
                files_monitored=files_monitored,
                changes_detected=changes_detected,
                alerts_generated=alerts_generated,
                quality_score=compliance_report.quality_score,
                security_score=compliance_report.security_score,
                compliance_score=compliance_report.compliance_score,
                changes=list(self.change_history),
                alerts=list(self.alert_history),
                metrics=metrics
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao gerar relatório: {str(e)}")
            raise
    
    def save_report(self, report: MonitoringReport, output_path: str = "logs/monitoring_report.json"):
        """Salvar relatório de monitoramento"""
        try:
            # Criar diretório se não existir
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Converter para dict
            report_dict = asdict(report)
            
            # Salvar arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"[{self.tracing_id}] Relatório salvo em: {output_path}")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao salvar relatório: {str(e)}")
    
    def start_monitoring(self):
        """Iniciar monitoramento"""
        try:
            if self.is_monitoring:
                self.logger.warning(f"[{self.tracing_id}] Monitoramento já está ativo")
                return
            
            self.logger.info(f"[{self.tracing_id}] Iniciando monitoramento...")
            
            # Configurar observer
            self.observer = Observer()
            self.change_handler = DocumentChangeHandler(self)
            
            # Adicionar diretórios para monitorar
            self.observer.schedule(self.change_handler, str(self.docs_path), recursive=True)
            
            # Iniciar observer
            self.observer.start()
            self.is_monitoring = True
            
            # Iniciar thread de verificação periódica
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info(f"[{self.tracing_id}] Monitoramento iniciado com sucesso")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao iniciar monitoramento: {str(e)}")
            raise
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        try:
            if not self.is_monitoring:
                return
            
            self.logger.info(f"[{self.tracing_id}] Parando monitoramento...")
            
            # Sinalizar parada
            self.stop_event.set()
            
            # Parar observer
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            # Aguardar thread
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            self.is_monitoring = False
            self.logger.info(f"[{self.tracing_id}] Monitoramento parado")
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao parar monitoramento: {str(e)}")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        start_time = datetime.now()
        
        while not self.stop_event.is_set():
            try:
                # Verificar divergências periodicamente
                divergences = self.detect_divergences()
                
                # Gerar alertas para divergências
                for divergence in divergences:
                    alert = MonitoringAlert(
                        timestamp=datetime.now().isoformat(),
                        alert_id=f"DIVERGENCE_{divergence['type']}_{int(time.time())}",
                        severity=divergence['severity'],
                        category='compliance',
                        message=divergence['description'],
                        details=divergence['details']
                    )
                    self.alert_history.append(alert)
                    self.logger.warning(f"[{self.tracing_id}] Divergência detectada: {divergence['description']}")
                
                # Aguardar próximo ciclo
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"[{self.tracing_id}] Erro no loop de monitoramento: {str(e)}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
        
        # Gerar relatório final
        duration = (datetime.now() - start_time).total_seconds()
        try:
            final_report = self.generate_monitoring_report(duration)
            self.save_report(final_report)
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao gerar relatório final: {str(e)}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Obter status atual do monitoramento"""
        try:
            compliance_report = self.compliance_checker.run_validation(str(self.docs_path))
            
            return {
                'is_monitoring': self.is_monitoring,
                'files_monitored': len(self.file_hashes),
                'changes_detected': len(self.change_history),
                'alerts_generated': len(self.alert_history),
                'unresolved_alerts': len([a for a in self.alert_history if not a.resolved]),
                'quality_score': compliance_report.quality_score,
                'security_score': compliance_report.security_score,
                'compliance_score': compliance_report.compliance_score,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao obter status: {str(e)}")
            return {'error': str(e)}
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Marcar alerta como resolvido"""
        try:
            for alert in self.alert_history:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    self.logger.info(f"[{self.tracing_id}] Alerta resolvido: {alert_id}")
                    return True
            
            self.logger.warning(f"[{self.tracing_id}] Alerta não encontrado: {alert_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"[{self.tracing_id}] Erro ao resolver alerta: {str(e)}")
            return False


def main():
    """
    Função principal para execução standalone
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de Documentação Enterprise")
    parser.add_argument("--docs-path", default="docs/", help="Caminho para documentação")
    parser.add_argument("--config-path", default="docs/trigger_config.json", help="Caminho para configuração")
    parser.add_argument("--alert-threshold", type=float, default=0.85, help="Threshold de alerta")
    parser.add_argument("--check-interval", type=int, default=300, help="Intervalo de verificação (segundos)")
    parser.add_argument("--duration", type=int, default=3600, help="Duração do monitoramento (segundos)")
    parser.add_argument("--verbose", action="store_true", help="Modo verbose")
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Criar monitor
        monitor = DocumentationMonitor(
            docs_path=args.docs_path,
            config_path=args.config_path,
            alert_threshold=args.alert_threshold,
            check_interval=args.check_interval
        )
        
        # Iniciar monitoramento
        monitor.start_monitoring()
        
        print(f"🚀 Monitoramento iniciado (duração: {args.duration}string_data)")
        print(f"📁 Diretório: {args.docs_path}")
        print(f"🔔 Threshold: {args.alert_threshold}")
        print(f"⏱️ Intervalo: {args.check_interval}string_data")
        
        # Aguardar duração especificada
        time.sleep(args.duration)
        
        # Parar monitoramento
        monitor.stop_monitoring()
        
        # Mostrar status final
        status = monitor.get_current_status()
        print("\n📊 Status Final:")
        print(f"  Arquivos monitorados: {status['files_monitored']}")
        print(f"  Mudanças detectadas: {status['changes_detected']}")
        print(f"  Alertas gerados: {status['alerts_generated']}")
        print(f"  Alertas não resolvidos: {status['unresolved_alerts']}")
        print(f"  Score de qualidade: {status['quality_score']:.2f}")
        print(f"  Score de segurança: {status['security_score']:.2f}")
        print(f"  Score de compliance: {status['compliance_score']:.2f}")
        
        print("✅ Monitoramento concluído!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoramento interrompido pelo usuário")
        if 'monitor' in locals():
            monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        if args.verbose:
            traceback.print_exc()


if __name__ == "__main__":
    main() 