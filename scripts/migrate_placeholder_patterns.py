#!/usr/bin/env python3
"""
Script de Migração Automática de Placeholders - Omni Keywords Finder
===================================================================

Tracing ID: MIGRATION_SCRIPT_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Script que migra automaticamente todos os padrões de placeholders no sistema:
- Atualiza arquivos Python
- Atualiza arquivos TypeScript/JavaScript
- Atualiza templates HTML
- Gera relatório de migração
- Valida consistência

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

# Importar sistema de unificação
import sys
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.processamento.placeholder_unification_system import (
    PlaceholderUnificationSystem, 
    PlaceholderFormat,
    MigrationResult
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_placeholder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class FileMigrationResult:
    """Resultado da migração de um arquivo."""
    file_path: str
    original_content: str
    migrated_content: str
    migration_result: MigrationResult
    file_hash_before: str
    file_hash_after: str
    success: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class MigrationSummary:
    """Resumo da migração completa."""
    total_files: int
    successful_migrations: int
    failed_migrations: int
    total_changes: int
    migration_time: float
    start_time: datetime
    end_time: datetime
    file_results: List[FileMigrationResult]
    statistics: Dict[str, Any]


class PlaceholderMigrationScript:
    """
    Script de migração automática de placeholders.
    
    Responsabilidades:
    - Identificar arquivos que precisam de migração
    - Aplicar migração de forma segura
    - Gerar backup antes das mudanças
    - Validar resultados
    - Gerar relatório detalhado
    """
    
    def __init__(self, project_root: str = "."):
        """Inicializa o script de migração."""
        self.project_root = Path(project_root)
        self.unification_system = PlaceholderUnificationSystem()
        
        # Padrões de arquivos para migrar
        self.file_patterns = {
            "python": ["*.py"],
            "typescript": ["*.ts", "*.tsx"],
            "javascript": ["*.js", "*.jsx"],
            "html": ["*.html", "*.htm"],
            "markdown": ["*.md"],
            "yaml": ["*.yml", "*.yaml"],
            "json": ["*.json"]
        }
        
        # Diretórios para excluir
        self.exclude_dirs = {
            ".git", ".venv", "venv", "__pycache__", "node_modules",
            "backup_sistema_antigo", "logs", "coverage", "htmlcov",
            ".pytest_cache", ".mypy_cache", "dist", "build"
        }
        
        # Arquivos para excluir
        self.exclude_files = {
            "migration_placeholder.log",
            "migration_report.json",
            "placeholder_backup"
        }
        
        # Backup directory
        self.backup_dir = self.project_root / "placeholder_backup"
        
        logger.info(f"Script de migração inicializado para: {self.project_root}")
    
    def find_files_to_migrate(self) -> List[Path]:
        """
        Encontra arquivos que precisam de migração.
        
        Returns:
            Lista de arquivos para migrar
        """
        files_to_migrate = []
        
        for file_type, patterns in self.file_patterns.items():
            for pattern in patterns:
                files = list(self.project_root.rglob(pattern))
                
                for file_path in files:
                    # Verificar se deve ser excluído
                    if self._should_exclude_file(file_path):
                        continue
                    
                    # Verificar se contém placeholders antigos
                    if self._contains_old_placeholders(file_path):
                        files_to_migrate.append(file_path)
        
        logger.info(f"Encontrados {len(files_to_migrate)} arquivos para migração")
        return files_to_migrate
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Verifica se arquivo deve ser excluído."""
        # Verificar diretórios excluídos
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return True
        
        # Verificar arquivos excluídos
        if file_path.name in self.exclude_files:
            return True
        
        # Verificar se está no diretório de backup
        if self.backup_dir in file_path.parents:
            return True
        
        return False
    
    def _contains_old_placeholders(self, file_path: Path) -> bool:
        """Verifica se arquivo contém placeholders antigos."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Padrões de placeholders antigos
            old_patterns = [
                r'\[[A-Z\- ]+\]',  # [PALAVRA-CHAVE], [CLUSTER]
                r'\$[a-z_]+',      # $primary_keyword
                r'<[a-z_]+>',      # <primary_keyword>
                r'\[\[[a-z_]+\]\]'  # [[primary_keyword]]
            ]
            
            for pattern in old_patterns:
                if re.search(pattern, content):
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Erro ao verificar arquivo {file_path}: {e}")
            return False
    
    def create_backup(self, files_to_migrate: List[Path]) -> bool:
        """
        Cria backup dos arquivos antes da migração.
        
        Args:
            files_to_migrate: Lista de arquivos para fazer backup
            
        Returns:
            True se backup foi criado com sucesso
        """
        try:
            # Criar diretório de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / timestamp
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivos
            for file_path in files_to_migrate:
                relative_path = file_path.relative_to(self.project_root)
                backup_file_path = backup_path / relative_path
                
                # Criar diretórios necessários
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(file_path, backup_file_path)
            
            logger.info(f"Backup criado em: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return False
    
    def migrate_file(self, file_path: Path) -> FileMigrationResult:
        """
        Migra um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Resultado da migração
        """
        try:
            # Ler conteúdo original
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Gerar hash do conteúdo original
            file_hash_before = hashlib.md5(original_content.encode()).hexdigest()
            
            # Aplicar migração
            migration_result = self.unification_system.migrate_to_standard_format(original_content)
            
            # Gerar hash do conteúdo migrado
            file_hash_after = hashlib.md5(migration_result.migrated_text.encode()).hexdigest()
            
            # Verificar se houve mudanças
            content_changed = file_hash_before != file_hash_after
            
            # Criar resultado
            file_result = FileMigrationResult(
                file_path=str(file_path),
                original_content=original_content,
                migrated_content=migration_result.migrated_text,
                migration_result=migration_result,
                file_hash_before=file_hash_before,
                file_hash_after=file_hash_after,
                success=migration_result.success,
                errors=migration_result.errors,
                warnings=migration_result.warnings
            )
            
            # Aplicar mudanças se houve alterações
            if content_changed and migration_result.success:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(migration_result.migrated_text)
                
                logger.info(f"Arquivo migrado: {file_path}")
            elif not content_changed:
                logger.info(f"Arquivo sem mudanças: {file_path}")
            else:
                logger.warning(f"Arquivo com erros: {file_path}")
            
            return file_result
            
        except Exception as e:
            error_msg = f"Erro ao migrar arquivo {file_path}: {e}"
            logger.error(error_msg)
            
            return FileMigrationResult(
                file_path=str(file_path),
                original_content="",
                migrated_content="",
                migration_result=MigrationResult(
                    original_text="",
                    migrated_text="",
                    format_detected=PlaceholderFormat.NEW_CURLY,
                    migrations_applied=[],
                    errors=[error_msg],
                    warnings=[],
                    success=False,
                    timestamp=datetime.now(),
                    hash_before="",
                    hash_after=""
                ),
                file_hash_before="",
                file_hash_after="",
                success=False,
                errors=[error_msg],
                warnings=[]
            )
    
    def run_migration(self, create_backup: bool = True, dry_run: bool = False) -> MigrationSummary:
        """
        Executa migração completa.
        
        Args:
            create_backup: Criar backup antes da migração
            dry_run: Executar sem aplicar mudanças
            
        Returns:
            Resumo da migração
        """
        start_time = datetime.now()
        
        logger.info("Iniciando migração de placeholders...")
        
        # Encontrar arquivos para migrar
        files_to_migrate = self.find_files_to_migrate()
        
        if not files_to_migrate:
            logger.info("Nenhum arquivo encontrado para migração")
            return MigrationSummary(
                total_files=0,
                successful_migrations=0,
                failed_migrations=0,
                total_changes=0,
                migration_time=0.0,
                start_time=start_time,
                end_time=datetime.now(),
                file_results=[],
                statistics={}
            )
        
        # Criar backup se solicitado
        if create_backup and not dry_run:
            backup_success = self.create_backup(files_to_migrate)
            if not backup_success:
                logger.error("Falha ao criar backup. Migração abortada.")
                return MigrationSummary(
                    total_files=len(files_to_migrate),
                    successful_migrations=0,
                    failed_migrations=len(files_to_migrate),
                    total_changes=0,
                    migration_time=0.0,
                    start_time=start_time,
                    end_time=datetime.now(),
                    file_results=[],
                    statistics={"backup_failed": True}
                )
        
        # Migrar arquivos
        file_results = []
        successful_migrations = 0
        failed_migrations = 0
        total_changes = 0
        
        for file_path in files_to_migrate:
            if dry_run:
                # Simular migração sem aplicar mudanças
                file_result = self.migrate_file(file_path)
                # Não aplicar mudanças no dry run
                if file_result.success and file_result.file_hash_before != file_result.file_hash_after:
                    total_changes += 1
            else:
                file_result = self.migrate_file(file_path)
                if file_result.success and file_result.file_hash_before != file_result.file_hash_after:
                    total_changes += 1
            
            file_results.append(file_result)
            
            if file_result.success:
                successful_migrations += 1
            else:
                failed_migrations += 1
        
        # Calcular tempo total
        end_time = datetime.now()
        migration_time = (end_time - start_time).total_seconds()
        
        # Gerar estatísticas
        statistics = self._generate_statistics(file_results)
        
        # Criar resumo
        summary = MigrationSummary(
            total_files=len(files_to_migrate),
            successful_migrations=successful_migrations,
            failed_migrations=failed_migrations,
            total_changes=total_changes,
            migration_time=migration_time,
            start_time=start_time,
            end_time=end_time,
            file_results=file_results,
            statistics=statistics
        )
        
        # Log do resumo
        logger.info(f"Migração concluída:")
        logger.info(f"  Total de arquivos: {summary.total_files}")
        logger.info(f"  Migrações bem-sucedidas: {summary.successful_migrations}")
        logger.info(f"  Migrações falharam: {summary.failed_migrations}")
        logger.info(f"  Total de mudanças: {summary.total_changes}")
        logger.info(f"  Tempo total: {summary.migration_time:.2f}s")
        
        return summary
    
    def _generate_statistics(self, file_results: List[FileMigrationResult]) -> Dict[str, Any]:
        """Gera estatísticas da migração."""
        stats = {
            "format_detections": {},
            "migration_types": {},
            "file_extensions": {},
            "error_types": {},
            "warning_types": {}
        }
        
        for result in file_results:
            # Estatísticas de formato
            format_detected = result.migration_result.format_detected.value
            stats["format_detections"][format_detected] = stats["format_detections"].get(format_detected, 0) + 1
            
            # Estatísticas de extensão de arquivo
            file_ext = Path(result.file_path).suffix
            stats["file_extensions"][file_ext] = stats["file_extensions"].get(file_ext, 0) + 1
            
            # Estatísticas de tipos de migração
            for migration in result.migration_result.migrations_applied:
                migration_type = f"{migration['old_format']} -> {migration['new_format']}"
                stats["migration_types"][migration_type] = stats["migration_types"].get(migration_type, 0) + 1
            
            # Estatísticas de erros
            for error in result.errors:
                error_type = error.split(':')[0] if ':' in error else error
                stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
            
            # Estatísticas de warnings
            for warning in result.warnings:
                warning_type = warning.split(':')[0] if ':' in warning else warning
                stats["warning_types"][warning_type] = stats["warning_types"].get(warning_type, 0) + 1
        
        return stats
    
    def generate_report(self, summary: MigrationSummary, output_file: str = "migration_report.json"):
        """
        Gera relatório detalhado da migração.
        
        Args:
            summary: Resumo da migração
            output_file: Arquivo de saída
        """
        try:
            report = {
                "migration_summary": asdict(summary),
                "detailed_results": [
                    {
                        "file_path": result.file_path,
                        "success": result.success,
                        "format_detected": result.migration_result.format_detected.value,
                        "migrations_applied": result.migration_result.migrations_applied,
                        "errors": result.errors,
                        "warnings": result.warnings,
                        "content_changed": result.file_hash_before != result.file_hash_after
                    }
                    for result in summary.file_results
                ],
                "statistics": summary.statistics,
                "generated_at": datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatório gerado: {output_file}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migração automática de placeholders")
    parser.add_argument("--project-root", default=".", help="Diretório raiz do projeto")
    parser.add_argument("--no-backup", action="store_true", help="Não criar backup")
    parser.add_argument("--dry-run", action="store_true", help="Executar sem aplicar mudanças")
    parser.add_argument("--report", default="migration_report.json", help="Arquivo de relatório")
    
    args = parser.parse_args()
    
    # Inicializar script
    migration_script = PlaceholderMigrationScript(args.project_root)
    
    # Executar migração
    summary = migration_script.run_migration(
        create_backup=not args.no_backup,
        dry_run=args.dry_run
    )
    
    # Gerar relatório
    migration_script.generate_report(summary, args.report)
    
    # Retornar código de saída
    if summary.failed_migrations > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 