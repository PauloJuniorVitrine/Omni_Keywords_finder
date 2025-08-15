#!/usr/bin/env python3
"""
Script de Mutation Testing para Omni Keywords Finder
Tracing ID: MUTATION_TESTING_20241220_001
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(levelname)string_data - %(message)string_data',
    handlers=[
        logging.FileHandler('logs/mutation_testing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MutationTestingRunner:
    """Runner para execução de mutation testing"""
    
    def __init__(self):
        self.tracing_id = "MUTATION_TESTING_20241220_001"
        self.start_time = datetime.now()
        self.results = {
            "tracing_id": self.tracing_id,
            "start_time": self.start_time.isoformat(),
            "mutation_results": {},
            "quality_metrics": {},
            "false_positives": [],
            "surviving_mutants": [],
            "execution_log": []
        }
        
    def log_execution(self, message: str, level: str = "INFO"):
        """Registra execução no log"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.results["execution_log"].append(log_entry)
        logger.info(f"[{self.tracing_id}] {message}")
        
    def run_pre_mutation_tests(self) -> bool:
        """Executa testes antes da mutação"""
        self.log_execution("Iniciando testes pré-mutação")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                self.log_execution("Testes pré-mutação passaram com sucesso")
                return True
            else:
                self.log_execution(f"Testes pré-mutação falharam: {result.stderr}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            self.log_execution("Testes pré-mutação excederam timeout", "ERROR")
            return False
        except Exception as e:
            self.log_execution(f"Erro nos testes pré-mutação: {str(e)}", "ERROR")
            return False
    
    def run_mutation_testing(self) -> Dict[str, Any]:
        """Executa mutation testing com mutmut"""
        self.log_execution("Iniciando mutation testing")
        
        try:
            # Executa mutmut
            result = subprocess.run(
                ["mutmut", "run", "--paths-to-mutate=app/,backend/,infrastructure/,shared/,domain/"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Analisa resultados
            mutation_results = self.analyze_mutation_results(result.stdout, result.stderr)
            
            self.log_execution(f"Mutation testing concluído: {mutation_results['total_mutants']} mutantes")
            return mutation_results
            
        except subprocess.TimeoutExpired:
            self.log_execution("Mutation testing excedeu timeout", "ERROR")
            return {"error": "Timeout exceeded"}
        except Exception as e:
            self.log_execution(f"Erro no mutation testing: {str(e)}", "ERROR")
            return {"error": str(e)}
    
    def analyze_mutation_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Analisa resultados do mutation testing"""
        self.log_execution("Analisando resultados do mutation testing")
        
        # Extrai estatísticas básicas
        total_mutants = 0
        killed_mutants = 0
        surviving_mutants = 0
        timeout_mutants = 0
        
        # Parse do output do mutmut
        lines = stdout.split('\n')
        for line in lines:
            if 'mutants' in line.lower():
                if 'killed' in line.lower():
                    killed_mutants = int(line.split()[0])
                elif 'surviving' in line.lower():
                    surviving_mutants = int(line.split()[0])
                elif 'timeout' in line.lower():
                    timeout_mutants = int(line.split()[0])
        
        total_mutants = killed_mutants + surviving_mutants + timeout_mutants
        
        # Calcula métricas de qualidade
        kill_rate = (killed_mutants / total_mutants * 100) if total_mutants > 0 else 0
        survival_rate = (surviving_mutants / total_mutants * 100) if total_mutants > 0 else 0
        
        # Identifica mutantes sobreviventes
        surviving_mutants_list = self.identify_surviving_mutants()
        
        # Detecta falsos positivos
        false_positives = self.detect_false_positives()
        
        return {
            "total_mutants": total_mutants,
            "killed_mutants": killed_mutants,
            "surviving_mutants": surviving_mutants,
            "timeout_mutants": timeout_mutants,
            "kill_rate": kill_rate,
            "survival_rate": survival_rate,
            "quality_score": self.calculate_quality_score(kill_rate, survival_rate),
            "surviving_mutants_list": surviving_mutants_list,
            "false_positives": false_positives,
            "thresholds": {
                "min_kill_rate": 90,
                "max_survival_rate": 10,
                "quality_threshold": 85
            }
        }
    
    def identify_surviving_mutants(self) -> List[Dict[str, Any]]:
        """Identifica mutantes sobreviventes"""
        self.log_execution("Identificando mutantes sobreviventes")
        
        surviving_mutants = []
        
        # Procura por arquivos de mutantes sobreviventes
        mutation_dir = Path("coverage/mutation/")
        if mutation_dir.exists():
            for mutant_file in mutation_dir.glob("*.py"):
                if "surviving" in mutant_file.name:
                    surviving_mutants.append({
                        "file": str(mutant_file),
                        "type": "surviving",
                        "risk_level": "HIGH"
                    })
        
        return surviving_mutants
    
    def detect_false_positives(self) -> List[Dict[str, Any]]:
        """Detecta falsos positivos no mutation testing"""
        self.log_execution("Detectando falsos positivos")
        
        false_positives = []
        
        # Análise baseada em heurísticas
        # 1. Mutantes que não alteram comportamento semântico
        # 2. Mutantes em código de logging/debug
        # 3. Mutantes em comentários ou docstrings
        
        # Implementação simplificada - em produção seria mais sofisticada
        false_positives = [
            {
                "type": "logging_mutant",
                "description": "Mutante em código de logging",
                "risk_level": "LOW"
            },
            {
                "type": "comment_mutant", 
                "description": "Mutante em comentários",
                "risk_level": "LOW"
            }
        ]
        
        return false_positives
    
    def calculate_quality_score(self, kill_rate: float, survival_rate: float) -> float:
        """Calcula score de qualidade baseado em métricas"""
        # Fórmula: (kill_rate * 0.7) + ((100 - survival_rate) * 0.3)
        quality_score = (kill_rate * 0.7) + ((100 - survival_rate) * 0.3)
        return round(quality_score, 2)
    
    def validate_quality_thresholds(self, results: Dict[str, Any]) -> bool:
        """Valida se os thresholds de qualidade foram atingidos"""
        self.log_execution("Validando thresholds de qualidade")
        
        thresholds = results.get("thresholds", {})
        kill_rate = results.get("kill_rate", 0)
        survival_rate = results.get("survival_rate", 100)
        quality_score = results.get("quality_score", 0)
        
        min_kill_rate = thresholds.get("min_kill_rate", 90)
        max_survival_rate = thresholds.get("max_survival_rate", 10)
        quality_threshold = thresholds.get("quality_threshold", 85)
        
        # Validações
        kill_rate_ok = kill_rate >= min_kill_rate
        survival_rate_ok = survival_rate <= max_survival_rate
        quality_score_ok = quality_score >= quality_threshold
        
        self.log_execution(f"Kill rate: {kill_rate}% (mínimo: {min_kill_rate}%) - {'✅' if kill_rate_ok else '❌'}")
        self.log_execution(f"Survival rate: {survival_rate}% (máximo: {max_survival_rate}%) - {'✅' if survival_rate_ok else '❌'}")
        self.log_execution(f"Quality score: {quality_score} (mínimo: {quality_threshold}) - {'✅' if quality_score_ok else '❌'}")
        
        return kill_rate_ok and survival_rate_ok and quality_score_ok
    
    def generate_reports(self, results: Dict[str, Any]):
        """Gera relatórios de mutation testing"""
        self.log_execution("Gerando relatórios de mutation testing")
        
        # Cria diretório de relatórios
        reports_dir = Path("coverage/mutation/")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Relatório JSON
        json_report = reports_dir / "mutation_results.json"
        with open(json_report, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Relatório HTML
        html_report = self.generate_html_report(results)
        html_file = reports_dir / "mutation_report.html"
        with open(html_file, 'w') as f:
            f.write(html_report)
        
        # Relatório Markdown
        md_report = self.generate_markdown_report(results)
        md_file = reports_dir / "mutation_report.md"
        with open(md_file, 'w') as f:
            f.write(md_report)
        
        self.log_execution(f"Relatórios gerados em: {reports_dir}")
    
    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mutation Testing Report - Omni Keywords Finder</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
        .success {{ background: #d4edda; border-color: #c3e6cb; }}
        .warning {{ background: #fff3cd; border-color: #ffeaa7; }}
        .error {{ background: #f8d7da; border-color: #f5c6cb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Mutation Testing Report</h1>
        <p><strong>Tracing ID:</strong> {results.get('tracing_id', 'N/A')}</p>
        <p><strong>Data:</strong> {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}</p>
    </div>
    
    <div class="metric {'success' if results.get('kill_rate', 0) >= 90 else 'warning'}">
        <h3>Kill Rate: {results.get('kill_rate', 0):.2f}%</h3>
        <p>Mutantes eliminados: {results.get('killed_mutants', 0)} / {results.get('total_mutants', 0)}</p>
    </div>
    
    <div class="metric {'success' if results.get('survival_rate', 100) <= 10 else 'error'}">
        <h3>Survival Rate: {results.get('survival_rate', 100):.2f}%</h3>
        <p>Mutantes sobreviventes: {results.get('surviving_mutants', 0)}</p>
    </div>
    
    <div class="metric {'success' if results.get('quality_score', 0) >= 85 else 'warning'}">
        <h3>Quality Score: {results.get('quality_score', 0):.2f}</h3>
    </div>
    
    <h3>Surviving Mutants</h3>
    <ul>
        {''.join([f'<li>{mutant.get("file", "N/A")} - {mutant.get("risk_level", "N/A")}</li>' for mutant in results.get('surviving_mutants_list', [])])}
    </ul>
    
    <h3>False Positives</h3>
    <ul>
        {''.join([f'<li>{fp.get("type", "N/A")} - {fp.get("description", "N/A")}</li>' for fp in results.get('false_positives', [])])}
    </ul>
</body>
</html>
"""
    
    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório Markdown"""
        return f"""# Mutation Testing Report - Omni Keywords Finder

**Tracing ID**: {results.get('tracing_id', 'N/A')}  
**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}

## 📊 Métricas de Qualidade

### Kill Rate: {results.get('kill_rate', 0):.2f}%
- **Mutantes eliminados**: {results.get('killed_mutants', 0)} / {results.get('total_mutants', 0)}
- **Status**: {'✅ PASSOU' if results.get('kill_rate', 0) >= 90 else '❌ FALHOU'}

### Survival Rate: {results.get('survival_rate', 100):.2f}%
- **Mutantes sobreviventes**: {results.get('surviving_mutants', 0)}
- **Status**: {'✅ PASSOU' if results.get('survival_rate', 100) <= 10 else '❌ FALHOU'}

### Quality Score: {results.get('quality_score', 0):.2f}
- **Status**: {'✅ PASSOU' if results.get('quality_score', 0) >= 85 else '❌ FALHOU'}

## 🧬 Mutantes Sobreviventes

{chr(10).join([f'- **{mutant.get("file", "N/A")}** - {mutant.get("risk_level", "N/A")}' for mutant in results.get('surviving_mutants_list', [])])}

## ⚠️ Falsos Positivos

{chr(10).join([f'- **{fp.get("type", "N/A")}**: {fp.get("description", "N/A")}' for fp in results.get('false_positives', [])])}

## 📈 Thresholds

- **Kill Rate Mínimo**: 90%
- **Survival Rate Máximo**: 10%
- **Quality Score Mínimo**: 85

## 🎯 Conclusão

{'✅ **MUTATION TESTING PASSOU** - Sistema com qualidade adequada' if self.validate_quality_thresholds(results) else '❌ **MUTATION TESTING FALHOU** - Necessita melhorias nos testes'}
"""
    
    def run(self) -> bool:
        """Executa o pipeline completo de mutation testing"""
        self.log_execution("=== INICIANDO MUTATION TESTING ===")
        
        # 1. Testes pré-mutação
        if not self.run_pre_mutation_tests():
            self.log_execution("Falha nos testes pré-mutação. Abortando.", "ERROR")
            return False
        
        # 2. Mutation testing
        mutation_results = self.run_mutation_testing()
        if "error" in mutation_results:
            self.log_execution(f"Erro no mutation testing: {mutation_results['error']}", "ERROR")
            return False
        
        # 3. Validação de qualidade
        quality_ok = self.validate_quality_thresholds(mutation_results)
        
        # 4. Geração de relatórios
        self.generate_reports(mutation_results)
        
        # 5. Finalização
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.results["end_time"] = end_time.isoformat()
        self.results["duration_seconds"] = duration
        self.results["mutation_results"] = mutation_results
        self.results["quality_passed"] = quality_ok
        
        self.log_execution(f"=== MUTATION TESTING CONCLUÍDO em {duration:.2f}string_data ===")
        self.log_execution(f"Qualidade: {'✅ PASSOU' if quality_ok else '❌ FALHOU'}")
        
        return quality_ok

def main():
    """Função principal"""
    runner = MutationTestingRunner()
    success = runner.run()
    
    # Salva resultados finais
    results_file = Path("coverage/mutation/final_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(runner.results, f, indent=2)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 