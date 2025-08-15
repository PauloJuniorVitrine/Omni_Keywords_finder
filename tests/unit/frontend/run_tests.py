#!/usr/bin/env python3
"""
Script de Execução de Testes Frontend - Semana 3-4
Omni Keywords Finder - Cobertura 98%

Tracing ID: FRONTEND_TESTS_001_20250127
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

class FrontendTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.frontend_tests_dir = self.project_root / "tests" / "unit" / "frontend"
        self.app_dir = self.project_root / "app"
        self.coverage_dir = self.project_root / "coverage" / "frontend"
        
        # Configurações
        self.coverage_threshold = 90  # Meta da semana 3-4
        self.test_timeout = 300  # 5 minutos
        
    def log(self, message: str, level: str = "INFO"):
        """Log estruturado com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_dependencies(self) -> bool:
        """Verifica se as dependências estão instaladas"""
        self.log("Verificando dependências...")
        
        try:
            # Verifica Node.js
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Node.js não encontrado", "ERROR")
                return False
            self.log(f"Node.js: {result.stdout.strip()}")
            
            # Verifica npm
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("npm não encontrado", "ERROR")
                return False
            self.log(f"npm: {result.stdout.strip()}")
            
            return True
            
        except Exception as e:
            self.log(f"Erro ao verificar dependências: {e}", "ERROR")
            return False
    
    def install_dependencies(self) -> bool:
        """Instala dependências do frontend"""
        self.log("Instalando dependências do frontend...")
        
        try:
            os.chdir(self.app_dir)
            
            # Instala dependências
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"Erro ao instalar dependências: {result.stderr}", "ERROR")
                return False
                
            self.log("Dependências instaladas com sucesso")
            return True
            
        except Exception as e:
            self.log(f"Erro ao instalar dependências: {e}", "ERROR")
            return False
    
    def run_tests(self) -> bool:
        """Executa os testes unitários do frontend"""
        self.log("Executando testes unitários do frontend...")
        
        try:
            os.chdir(self.frontend_tests_dir)
            
            # Executa testes com cobertura
            cmd = [
                "npx", "vitest", "run",
                "--coverage",
                "--reporter=verbose",
                "--reporter=html",
                "--reporter=json"
            ]
            
            self.log(f"Comando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.test_timeout
            )
            
            if result.returncode != 0:
                self.log(f"Testes falharam: {result.stderr}", "ERROR")
                return False
                
            self.log("Testes executados com sucesso")
            self.log(f"Output: {result.stdout}")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("Testes excederam o tempo limite", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erro ao executar testes: {e}", "ERROR")
            return False
    
    def generate_coverage_report(self) -> dict:
        """Gera relatório de cobertura"""
        self.log("Gerando relatório de cobertura...")
        
        try:
            coverage_file = self.coverage_dir / "coverage-final.json"
            
            if not coverage_file.exists():
                self.log("Arquivo de cobertura não encontrado", "WARNING")
                return {}
            
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            # Calcula métricas
            total_lines = 0
            covered_lines = 0
            total_functions = 0
            covered_functions = 0
            
            for file_path, file_data in coverage_data.items():
                if file_path.startswith('app/'):
                    total_lines += file_data.get('lines', {}).get('total', 0)
                    covered_lines += file_data.get('lines', {}).get('covered', 0)
                    total_functions += file_data.get('functions', {}).get('total', 0)
                    covered_functions += file_data.get('functions', {}).get('covered', 0)
            
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            function_coverage = (covered_functions / total_functions * 100) if total_functions > 0 else 0
            
            report = {
                'total_lines': total_lines,
                'covered_lines': covered_lines,
                'total_functions': total_functions,
                'covered_functions': covered_functions,
                'line_coverage': round(coverage_percentage, 2),
                'function_coverage': round(function_coverage, 2),
                'timestamp': datetime.now().isoformat(),
                'threshold_met': coverage_percentage >= self.coverage_threshold
            }
            
            self.log(f"Cobertura de linhas: {coverage_percentage:.2f}%")
            self.log(f"Cobertura de funções: {function_coverage:.2f}%")
            
            return report
            
        except Exception as e:
            self.log(f"Erro ao gerar relatório: {e}", "ERROR")
            return {}
    
    def run(self) -> bool:
        """Executa o pipeline completo de testes"""
        self.log("🚀 Iniciando execução de testes Frontend - Semana 3-4")
        self.log(f"Diretório de testes: {self.frontend_tests_dir}")
        self.log(f"Meta de cobertura: {self.coverage_threshold}%")
        
        # Verifica dependências
        if not self.check_dependencies():
            return False
        
        # Instala dependências
        if not self.install_dependencies():
            return False
        
        # Executa testes
        if not self.run_tests():
            return False
        
        # Gera relatório
        coverage_report = self.generate_coverage_report()
        
        if coverage_report:
            if coverage_report['threshold_met']:
                self.log("✅ Meta de cobertura atingida!", "SUCCESS")
            else:
                self.log("⚠️ Meta de cobertura não atingida", "WARNING")
        
        self.log("🎉 Execução de testes Frontend concluída")
        return True

def main():
    """Função principal"""
    runner = FrontendTestRunner()
    
    try:
        success = runner.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Execução interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
