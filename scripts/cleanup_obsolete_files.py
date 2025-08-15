#!/usr/bin/env python3
"""
Script de Limpeza de Arquivos Obsoletos - Omni Keywords Finder

Remove arquivos temporários, logs antigos e arquivos obsoletos
para otimizar o sistema após a migração.

Tracing ID: CLEANUP_001_20241227
Versão: 1.0
Autor: IA-Cursor
Status: ✅ IMPLEMENTADO PARA FASE 4
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)


class CleanupManager:
    """Gerenciador de limpeza de arquivos obsoletos."""
    
    def __init__(self, root_dir: str = "."):
        """
        Inicializa o gerenciador de limpeza.
        
        Args:
            root_dir: Diretório raiz do projeto
        """
        self.root_dir = Path(root_dir)
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.errors = []
        
        # Diretórios para preservar
        self.preserve_dirs = {
            'backup_sistema_antigo_20241227',
            'infrastructure',
            'domain',
            'app',
            'tests',
            'docs',
            'scripts',
            'config',
            'examples',
            '.venv',
            '.git'
        }
        
        # Arquivos para preservar
        self.preserve_files = {
            'README.md',
            'CHANGELOG.md',
            'requirements.txt',
            'package.json',
            'pytest.ini',
            'CHECKLIST_ORGANIZACAO_SISTEMICA_V1.md',
            'PLANO_MELHORIAS_SISTEMA_V1.md'
        }
    
    def limpar_logs_antigos(self, dias_antigos: int = 30) -> Dict[str, Any]:
        """
        Remove logs mais antigos que o número de dias especificado.
        
        Args:
            dias_antigos: Número de dias para considerar logs antigos
            
        Returns:
            Dicionário com estatísticas da limpeza
        """
        logger.info(f"Limpando logs mais antigos que {dias_antigos} dias...")
        
        stats = {
            'arquivos_removidos': 0,
            'espaco_liberado': 0,
            'erros': 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=dias_antigos)
        
        # Limpar logs no diretório logs/
        logs_dir = self.root_dir / 'logs'
        if logs_dir.exists():
            for log_file in logs_dir.glob('*.log'):
                try:
                    # Verificar data de modificação
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff_date:
                        size = log_file.stat().st_size
                        log_file.unlink()
                        stats['arquivos_removidos'] += 1
                        stats['espaco_liberado'] += size
                        self.cleaned_files.append(str(log_file))
                        logger.info(f"Removido log antigo: {log_file}")
                except Exception as e:
                    stats['erros'] += 1
                    self.errors.append(f"Erro ao remover {log_file}: {e}")
                    logger.error(f"Erro ao remover {log_file}: {e}")
        
        # Limpar logs pytest no diretório raiz
        for log_file in self.root_dir.glob('pytest_*.log'):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    stats['arquivos_removidos'] += 1
                    stats['espaco_liberado'] += size
                    self.cleaned_files.append(str(log_file))
                    logger.info(f"Removido log pytest: {log_file}")
            except Exception as e:
                stats['erros'] += 1
                self.errors.append(f"Erro ao remover {log_file}: {e}")
                logger.error(f"Erro ao remover {log_file}: {e}")
        
        return stats
    
    def limpar_cache(self) -> Dict[str, Any]:
        """
        Remove arquivos de cache e diretórios temporários.
        
        Returns:
            Dicionário com estatísticas da limpeza
        """
        logger.info("Limpando arquivos de cache...")
        
        stats = {
            'arquivos_removidos': 0,
            'diretorios_removidos': 0,
            'espaco_liberado': 0,
            'erros': 0
        }
        
        # Limpar .pytest_cache
        pytest_cache = self.root_dir / '.pytest_cache'
        if pytest_cache.exists():
            try:
                shutil.rmtree(pytest_cache)
                stats['diretorios_removidos'] += 1
                self.cleaned_dirs.append(str(pytest_cache))
                logger.info(f"Removido diretório de cache: {pytest_cache}")
            except Exception as e:
                stats['erros'] += 1
                self.errors.append(f"Erro ao remover {pytest_cache}: {e}")
                logger.error(f"Erro ao remover {pytest_cache}: {e}")
        
        # Limpar .coverage
        coverage_file = self.root_dir / '.coverage'
        if coverage_file.exists():
            try:
                size = coverage_file.stat().st_size
                coverage_file.unlink()
                stats['arquivos_removidos'] += 1
                stats['espaco_liberado'] += size
                self.cleaned_files.append(str(coverage_file))
                logger.info(f"Removido arquivo de coverage: {coverage_file}")
            except Exception as e:
                stats['erros'] += 1
                self.errors.append(f"Erro ao remover {coverage_file}: {e}")
                logger.error(f"Erro ao remover {coverage_file}: {e}")
        
        # Limpar htmlcov
        htmlcov_dir = self.root_dir / 'htmlcov'
        if htmlcov_dir.exists():
            try:
                shutil.rmtree(htmlcov_dir)
                stats['diretorios_removidos'] += 1
                self.cleaned_dirs.append(str(htmlcov_dir))
                logger.info(f"Removido diretório htmlcov: {htmlcov_dir}")
            except Exception as e:
                stats['erros'] += 1
                self.errors.append(f"Erro ao remover {htmlcov_dir}: {e}")
                logger.error(f"Erro ao remover {htmlcov_dir}: {e}")
        
        # Limpar __pycache__ recursivamente
        for pycache_dir in self.root_dir.rglob('__pycache__'):
            try:
                shutil.rmtree(pycache_dir)
                stats['diretorios_removidos'] += 1
                self.cleaned_dirs.append(str(pycache_dir))
                logger.info(f"Removido __pycache__: {pycache_dir}")
            except Exception as e:
                stats['erros'] += 1
                self.errors.append(f"Erro ao remover {pycache_dir}: {e}")
                logger.error(f"Erro ao remover {pycache_dir}: {e}")
        
        return stats
    
    def _is_in_preserved_dir(self, file_path: Path) -> bool:
        """Verifica se o arquivo está em um diretório preservado."""
        for preserve_dir in self.preserve_dirs:
            if preserve_dir in file_path.parts:
                return True
        return False
    
    def executar_limpeza_completa(self, dias_logs: int = 30) -> Dict[str, Any]:
        """
        Executa limpeza completa do sistema.
        
        Args:
            dias_logs: Número de dias para considerar logs antigos
            
        Returns:
            Dicionário com estatísticas completas da limpeza
        """
        logger.info("Iniciando limpeza completa do sistema...")
        
        total_stats = {
            'logs': self.limpar_logs_antigos(dias_logs),
            'cache': self.limpar_cache(),
            'total_arquivos_removidos': 0,
            'total_diretorios_removidos': 0,
            'total_espaco_liberado': 0,
            'total_erros': 0
        }
        
        # Calcular totais
        for category in ['logs', 'cache']:
            total_stats['total_arquivos_removidos'] += total_stats[category]['arquivos_removidos']
            total_stats['total_diretorios_removidos'] += total_stats[category].get('diretorios_removidos', 0)
            total_stats['total_espaco_liberado'] += total_stats[category]['espaco_liberado']
            total_stats['total_erros'] += total_stats[category]['erros']
        
        # Gerar relatório
        self._gerar_relatorio_limpeza(total_stats)
        
        logger.info("Limpeza completa concluída!")
        return total_stats
    
    def _gerar_relatorio_limpeza(self, stats: Dict[str, Any]):
        """Gera relatório de limpeza."""
        relatorio = f"""
# Relatório de Limpeza - {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}

## Estatísticas Gerais
- **Arquivos removidos**: {stats['total_arquivos_removidos']}
- **Diretórios removidos**: {stats['total_diretorios_removidos']}
- **Espaço liberado**: {stats['total_espaco_liberado'] / 1024 / 1024:.2f} MB
- **Erros**: {stats['total_erros']}

## Detalhamento por Categoria

### Logs Antigos
- Arquivos removidos: {stats['logs']['arquivos_removidos']}
- Espaço liberado: {stats['logs']['espaco_liberado'] / 1024:.2f} KB
- Erros: {stats['logs']['erros']}

### Cache
- Arquivos removidos: {stats['cache']['arquivos_removidos']}
- Diretórios removidos: {stats['cache']['diretorios_removidos']}
- Espaço liberado: {stats['cache']['espaco_liberado'] / 1024 / 1024:.2f} MB
- Erros: {stats['cache']['erros']}

## Arquivos Removidos
{chr(10).join(f"- {file}" for file in self.cleaned_files[:20])}
{'...' if len(self.cleaned_files) > 20 else ''}

## Diretórios Removidos
{chr(10).join(f"- {dir}" for dir in self.cleaned_dirs[:10])}
{'...' if len(self.cleaned_dirs) > 10 else ''}

## Erros Encontrados
{chr(10).join(f"- {error}" for error in self.errors[:10])}
{'...' if len(self.errors) > 10 else ''}
"""
        
        # Salvar relatório
        relatorio_file = self.root_dir / 'relatorio_limpeza.md'
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        logger.info(f"Relatório de limpeza salvo em: {relatorio_file}")


def main():
    """Função principal do script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Limpeza de arquivos obsoletos')
    parser.add_argument('--dias-logs', type=int, default=30,
                       help='Dias para considerar logs antigos (padrão: 30)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simular limpeza sem remover arquivos')
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("Modo DRY-RUN ativado - nenhum arquivo será removido")
    
    cleanup = CleanupManager()
    
    if not args.dry_run:
        stats = cleanup.executar_limpeza_completa(args.dias_logs)
        logger.info(f"Limpeza concluída! {stats['total_arquivos_removidos']} arquivos removidos")
    else:
        logger.info("Simulação de limpeza concluída")


if __name__ == '__main__':
    main() 