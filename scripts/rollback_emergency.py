#!/usr/bin/env python3
"""
🚨 SCRIPT DE ROLLBACK DE EMERGÊNCIA - OMNİ KEYWORDS FINDER

Tracing ID: ROLLBACK_EMERGENCY_001_20241227
Versão: 1.0
Data: 2024-12-27
Autor: IA-Cursor

Este script permite rollback rápido e seguro em caso de falha durante a migração.
"""

import os
import sys
import shutil
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/rollback_emergency.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EmergencyRollback:
    """Sistema de rollback de emergência para migração sistêmica."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_branch = "backup-sistema-antigo"
        self.rollback_log = self.project_root / "logs" / "rollback_history.json"
        self.critical_files = [
            "infrastructure/processamento/processador_keywords.py",
            "infrastructure/processamento/processador_keywords_core.py",
            "infrastructure/validacao/google_keyword_planner_validator.py",
            "infrastructure/cache/cache_inteligente_cauda_longa.py",
            "infrastructure/monitoring/performance_cauda_longa.py"
        ]
        
    def log_rollback_action(self, action: str, details: Dict) -> None:
        """Registra ação de rollback no histórico."""
        if not self.rollback_log.parent.exists():
            self.rollback_log.parent.mkdir(parents=True)
            
        history = []
        if self.rollback_log.exists():
            with open(self.rollback_log, 'r') as f:
                history = json.load(f)
                
        rollback_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": "executed"
        }
        
        history.append(rollback_entry)
        
        with open(self.rollback_log, 'w') as f:
            json.dump(history, f, indent=2)
            
        logger.info(f"Rollback action logged: {action}")
    
    def check_git_status(self) -> bool:
        """Verifica se o Git está disponível e configurado."""
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("Git não encontrado no sistema")
            return False
    
    def check_backup_branch(self) -> bool:
        """Verifica se o branch de backup existe."""
        try:
            result = subprocess.run(
                ["git", "branch", "--list", self.backup_branch],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return self.backup_branch in result.stdout
        except Exception as e:
            logger.error(f"Erro ao verificar branch de backup: {e}")
            return False
    
    def rollback_complete_system(self) -> bool:
        """Rollback completo do sistema para o estado anterior."""
        logger.warning("🚨 INICIANDO ROLLBACK COMPLETO DO SISTEMA")
        
        if not self.check_git_status():
            logger.error("Git não disponível. Rollback manual necessário.")
            return False
            
        if not self.check_backup_branch():
            logger.error(f"Branch de backup '{self.backup_branch}' não encontrado.")
            return False
        
        try:
            # Salvar estado atual antes do rollback
            subprocess.run(
                ["git", "stash", "push", "-m", f"Estado antes do rollback - {datetime.now()}"],
                cwd=self.project_root,
                check=True
            )
            
            # Fazer checkout para o branch de backup
            subprocess.run(
                ["git", "checkout", self.backup_branch],
                cwd=self.project_root,
                check=True
            )
            
            # Criar branch de rollback
            rollback_branch = f"rollback-emergency-{datetime.now().strftime('%Y%m%data-%H%M%S')}"
            subprocess.run(
                ["git", "checkout", "-b", rollback_branch],
                cwd=self.project_root,
                check=True
            )
            
            logger.info(f"✅ Rollback completo executado. Branch: {rollback_branch}")
            
            self.log_rollback_action("complete_system_rollback", {
                "backup_branch": self.backup_branch,
                "rollback_branch": rollback_branch,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro durante rollback completo: {e}")
            return False
    
    def rollback_specific_files(self, files: List[str]) -> bool:
        """Rollback de arquivos específicos."""
        logger.warning(f"🚨 INICIANDO ROLLBACK DE ARQUIVOS ESPECÍFICOS: {files}")
        
        if not self.check_git_status():
            logger.error("Git não disponível. Rollback manual necessário.")
            return False
        
        try:
            # Restaurar arquivos específicos do branch de backup
            for file_path in files:
                if Path(self.project_root / file_path).exists():
                    subprocess.run(
                        ["git", "checkout", self.backup_branch, "--", file_path],
                        cwd=self.project_root,
                        check=True
                    )
                    logger.info(f"✅ Arquivo restaurado: {file_path}")
                else:
                    logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
            
            self.log_rollback_action("specific_files_rollback", {
                "files": files,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro durante rollback de arquivos: {e}")
            return False
    
    def rollback_critical_components(self) -> bool:
        """Rollback dos componentes críticos do sistema."""
        logger.warning("🚨 INICIANDO ROLLBACK DE COMPONENTES CRÍTICOS")
        
        return self.rollback_specific_files(self.critical_files)
    
    def validate_rollback(self) -> Dict[str, bool]:
        """Valida se o rollback foi bem-sucedido."""
        logger.info("🔍 VALIDANDO ROLLBACK")
        
        validation_results = {
            "git_status": self.check_git_status(),
            "backup_branch_exists": self.check_backup_branch(),
            "critical_files_restored": True
        }
        
        # Verificar se arquivos críticos foram restaurados
        for file_path in self.critical_files:
            if not Path(self.project_root / file_path).exists():
                validation_results["critical_files_restored"] = False
                logger.error(f"❌ Arquivo crítico não restaurado: {file_path}")
        
        # Verificar se há mudanças não commitadas
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            validation_results["clean_working_directory"] = len(result.stdout.strip()) == 0
        except Exception:
            validation_results["clean_working_directory"] = False
        
        return validation_results
    
    def emergency_communication(self, rollback_type: str, success: bool) -> None:
        """Comunicação de emergência sobre o rollback."""
        message = f"""
🚨 COMUNICAÇÃO DE EMERGÊNCIA - ROLLBACK EXECUTADO

Tipo de Rollback: {rollback_type}
Status: {'✅ SUCESSO' if success else '❌ FALHA'}
Timestamp: {datetime.now().isoformat()}
Tracing ID: ROLLBACK_EMERGENCY_001_20241227

AÇÕES NECESSÁRIAS:
1. Verificar integridade do sistema
2. Executar testes de validação
3. Investigar causa da falha
4. Documentar incidente
5. Revisar plano de migração

CONTATO DE EMERGÊNCIA:
- Equipe de Desenvolvimento
- DevOps
- QA
        """
        
        logger.warning(message)
        
        # Salvar comunicação em arquivo
        comm_file = self.project_root / "logs" / f"emergency_communication_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        comm_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(comm_file, 'w') as f:
            f.write(message)
        
        logger.info(f"Comunicação de emergência salva em: {comm_file}")

def main():
    """Função principal do script de rollback."""
    print("🚨 SCRIPT DE ROLLBACK DE EMERGÊNCIA - OMNİ KEYWORDS FINDER")
    print("=" * 60)
    
    rollback = EmergencyRollback()
    
    if len(sys.argv) < 2:
        print("""
Uso: python scripts/rollback_emergency.py [OPÇÃO]

OPÇÕES:
  complete    - Rollback completo do sistema
  critical    - Rollback apenas de componentes críticos
  files       - Rollback de arquivos específicos
  validate    - Validar estado atual do sistema
  help        - Mostrar esta ajuda

EXEMPLOS:
  python scripts/rollback_emergency.py complete
  python scripts/rollback_emergency.py critical
  python scripts/rollback_emergency.py files file1.py file2.py
  python scripts/rollback_emergency.py validate
        """)
        return
    
    option = sys.argv[1].lower()
    
    if option == "complete":
        success = rollback.rollback_complete_system()
        rollback.emergency_communication("COMPLETO", success)
        
    elif option == "critical":
        success = rollback.rollback_critical_components()
        rollback.emergency_communication("COMPONENTES CRÍTICOS", success)
        
    elif option == "files":
        if len(sys.argv) < 3:
            print("❌ Erro: Especifique os arquivos para rollback")
            return
        files = sys.argv[2:]
        success = rollback.rollback_specific_files(files)
        rollback.emergency_communication(f"ARQUIVOS ESPECÍFICOS: {files}", success)
        
    elif option == "validate":
        results = rollback.validate_rollback()
        print("🔍 RESULTADOS DA VALIDAÇÃO:")
        for check, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
            
    elif option == "help":
        print("""
📋 AJUDA - ROLLBACK DE EMERGÊNCIA

Este script permite rollback rápido e seguro em caso de falha durante a migração.

CRITÉRIOS DE DECISÃO PARA ROLLBACK:
1. Quebra total do sistema
2. Perda de dados críticos
3. Performance degradada > 50%
4. Falhas em testes críticos
5. Problemas de segurança

PROCEDIMENTOS DE EMERGÊNCIA:
1. Executar rollback apropriado
2. Validar integridade do sistema
3. Comunicar à equipe
4. Investigar causa raiz
5. Documentar incidente

CONTATOS DE EMERGÊNCIA:
- Equipe de Desenvolvimento
- DevOps
- QA
        """)
        
    else:
        print(f"❌ Opção inválida: {option}")
        print("Use 'python scripts/rollback_emergency.py help' para ver as opções")

if __name__ == "__main__":
    main() 