#!/usr/bin/env python3
"""
📝 Changelog Generator
📅 Criado: 2025-01-27
🔧 Tracing ID: CHANGELOG_GENERATOR_001_20250127
⚡ Status: ✅ ENTERPRISE-READY
🎯 Objetivo: Gerar changelog automático baseado em commits e patches
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import git
from git import Repo

class ChangelogGenerator:
    """
    Gerador de changelog automático
    """
    
    def __init__(self, repo_path: str = '.'):
        """
        Inicializa o gerador de changelog
        
        Args:
            repo_path: Caminho para o repositório
        """
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        
    def get_commits_since_last_tag(self) -> List[Dict[str, Any]]:
        """
        Obtém commits desde a última tag
        
        Returns:
            Lista de commits com informações
        """
        try:
            # Obter última tag
            tags = sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime)
            last_tag = tags[-1] if tags else None
            
            # Obter commits desde a última tag
            if last_tag:
                commits = list(self.repo.iter_commits(f'{last_tag.name}..HEAD'))
            else:
                commits = list(self.repo.iter_commits('HEAD'))
            
            # Processar commits
            processed_commits = []
            for commit in commits:
                processed_commits.append({
                    'hash': commit.hexsha,
                    'author': commit.author.name,
                    'email': commit.author.email,
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip(),
                    'type': self.categorize_commit(commit.message)
                })
            
            return processed_commits
            
        except Exception as e:
            print(f"Error getting commits: {e}")
            return []
    
    def categorize_commit(self, message: str) -> str:
        """
        Categoriza commit baseado na mensagem
        
        Args:
            message: Mensagem do commit
            
        Returns:
            Categoria do commit
        """
        message_lower = message.lower()
        
        # Padrões para categorização
        patterns = {
            'feature': [r'feat', r'feature', r'add', r'new'],
            'fix': [r'fix', r'bug', r'patch', r'resolve'],
            'docs': [r'doc', r'readme', r'comment'],
            'style': [r'style', r'format', r'indent'],
            'refactor': [r'refactor', r'restructure', r'clean'],
            'test': [r'test', r'spec', r'assert'],
            'chore': [r'chore', r'build', r'ci', r'cd'],
            'perf': [r'perf', r'performance', r'optimize'],
            'security': [r'security', r'vulnerability', r'secure'],
            'breaking': [r'breaking', r'!feat', r'!fix']
        }
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower):
                    return category
        
        return 'other'
    
    def get_auto_healing_patches(self) -> List[Dict[str, Any]]:
        """
        Obtém informações sobre patches de auto-healing
        
        Returns:
            Lista de patches com informações
        """
        patches = []
        patches_dir = Path('patches')
        
        if not patches_dir.exists():
            return patches
        
        # Procurar por patches em todos os subdiretórios
        for patch_file in patches_dir.rglob('*.diff'):
            try:
                with open(patch_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrair informações do patch
                patch_info = {
                    'file': str(patch_file),
                    'stage': patch_file.parent.name,
                    'attempt': self.extract_attempt_number(patch_file.name),
                    'timestamp': self.extract_timestamp(content),
                    'files_modified': self.extract_modified_files(content),
                    'lines_changed': self.count_lines_changed(content)
                }
                
                patches.append(patch_info)
                
            except Exception as e:
                print(f"Error reading patch {patch_file}: {e}")
        
        return patches
    
    def extract_attempt_number(self, filename: str) -> int:
        """Extrai número da tentativa do nome do arquivo"""
        match = re.search(r'patch_attempt_(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    def extract_timestamp(self, content: str) -> str:
        """Extrai timestamp do conteúdo do patch"""
        match = re.search(r'# Timestamp: (.+)', content)
        return match.group(1) if match else datetime.now().isoformat()
    
    def extract_modified_files(self, content: str) -> List[str]:
        """Extrai arquivos modificados do patch"""
        files = []
        for line in content.split('\n'):
            if line.startswith('--- a/') or line.startswith('+++ b/'):
                file_path = line[6:]  # Remove '--- a/' ou '+++ b/'
                if file_path not in files:
                    files.append(file_path)
        return files
    
    def count_lines_changed(self, content: str) -> Dict[str, int]:
        """Conta linhas adicionadas/removidas"""
        added = 0
        removed = 0
        
        for line in content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added += 1
            elif line.startswith('-') and not line.startswith('---'):
                removed += 1
        
        return {'added': added, 'removed': removed}
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Obtém informações de versão
        
        Returns:
            Dicionário com informações de versão
        """
        try:
            # Obter última tag
            tags = sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime)
            last_tag = tags[-1] if tags else None
            
            # Calcular nova versão
            if last_tag:
                version_parts = last_tag.name.lstrip('v').split('.')
                patch_version = int(version_parts[2]) + 1
                new_version = f"{version_parts[0]}.{version_parts[1]}.{patch_version}"
            else:
                new_version = "1.0.0"
            
            return {
                'current_version': last_tag.name if last_tag else 'v0.0.0',
                'new_version': f"v{new_version}",
                'release_date': datetime.now().strftime('%Y-%m-%d'),
                'release_time': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error getting version info: {e}")
            return {
                'current_version': 'v0.0.0',
                'new_version': 'v1.0.0',
                'release_date': datetime.now().strftime('%Y-%m-%d'),
                'release_time': datetime.now().strftime('%H:%M:%S')
            }
    
    def generate_changelog(self) -> str:
        """
        Gera changelog completo
        
        Returns:
            Changelog formatado
        """
        # Obter informações
        version_info = self.get_version_info()
        commits = self.get_commits_since_last_tag()
        patches = self.get_auto_healing_patches()
        
        # Agrupar commits por categoria
        categorized_commits = {}
        for commit in commits:
            category = commit['type']
            if category not in categorized_commits:
                categorized_commits[category] = []
            categorized_commits[category].append(commit)
        
        # Gerar changelog
        changelog = f"""# Changelog

## [{version_info['new_version']}] - {version_info['release_date']}

### 🚀 Auto-Healing Pipeline Release

**Release Date**: {version_info['release_date']} at {version_info['release_time']}  
**Previous Version**: {version_info['current_version']}  
**Generated by**: Auto-Healing Pipeline v3.0.0

### 📊 Auto-Healing Statistics

"""
        
        # Estatísticas de auto-healing
        if patches:
            total_patches = len(patches)
            total_attempts = sum(patch['attempt'] for patch in patches)
            stages = set(patch['stage'] for patch in patches)
            total_files = len(set(file for patch in patches for file in patch['files_modified']))
            
            changelog += f"""- **Total Patches**: {total_patches}
- **Total Healing Attempts**: {total_attempts}
- **Stages with Healing**: {', '.join(stages)}
- **Files Modified**: {total_files}

### 🔧 Auto-Healing Details

"""
            
            # Detalhes por estágio
            for stage in sorted(stages):
                stage_patches = [p for p in patches if p['stage'] == stage]
                changelog += f"#### {stage.replace('_', ' ').title()}\n"
                
                for patch in stage_patches:
                    changelog += f"- **Attempt {patch['attempt']}**: Modified {len(patch['files_modified'])} files"
                    if patch['lines_changed']['added'] > 0 or patch['lines_changed']['removed'] > 0:
                        changelog += f" (+{patch['lines_changed']['added']}/-{patch['lines_changed']['removed']} lines)"
                    changelog += f" at {patch['timestamp']}\n"
                
                changelog += "\n"
        
        # Commits por categoria
        if commits:
            changelog += "### 📝 Manual Changes\n\n"
            
            category_names = {
                'feature': '✨ Features',
                'fix': '🐛 Bug Fixes',
                'docs': '📚 Documentation',
                'style': '💄 Styles',
                'refactor': '♻️ Refactoring',
                'test': '🧪 Tests',
                'chore': '🔧 Chores',
                'perf': '⚡ Performance',
                'security': '🔒 Security',
                'breaking': '💥 Breaking Changes',
                'other': '📦 Other'
            }
            
            for category, commits_list in categorized_commits.items():
                if commits_list:
                    category_name = category_names.get(category, category.title())
                    changelog += f"#### {category_name}\n"
                    
                    for commit in commits_list:
                        # Limpar mensagem do commit
                        message = commit['message'].split('\n')[0]  # Primeira linha apenas
                        changelog += f"- {message} ({commit['hash'][:8]})\n"
                    
                    changelog += "\n"
        
        # Footer
        changelog += f"""
### 🔗 Links

- **GitHub Release**: [Release {version_info['new_version']}](https://github.com/your-repo/releases/tag/{version_info['new_version']})
- **Auto-Healing Pipeline**: [Pipeline Run](https://github.com/your-repo/actions)
- **Full Changelog**: [Compare {version_info['current_version']}...{version_info['new_version']}](https://github.com/your-repo/compare/{version_info['current_version']}...{version_info['new_version']})

---

**Generated by Auto-Healing Pipeline v3.0.0**  
**Tracing ID**: CHANGELOG_GENERATOR_001_20250127
"""
        
        return changelog
    
    def save_changelog(self, changelog: str, filename: str = 'CHANGELOG.md'):
        """
        Salva changelog em arquivo
        
        Args:
            changelog: Conteúdo do changelog
            filename: Nome do arquivo
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(changelog)
            
            print(f"✅ Changelog saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving changelog: {e}")

def main():
    """Função principal"""
    generator = ChangelogGenerator()
    
    print("🔄 Generating changelog...")
    
    # Gerar changelog
    changelog = generator.generate_changelog()
    
    # Salvar arquivo
    generator.save_changelog(changelog)
    
    # Salvar também como JSON para uso programático
    version_info = generator.get_version_info()
    commits = generator.get_commits_since_last_tag()
    patches = generator.get_auto_healing_patches()
    
    changelog_data = {
        'version_info': version_info,
        'commits': commits,
        'patches': patches,
        'generated_at': datetime.now().isoformat(),
        'tracing_id': 'CHANGELOG_GENERATOR_001_20250127'
    }
    
    with open('changelog_data.json', 'w', encoding='utf-8') as f:
        json.dump(changelog_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Changelog generation completed!")
    print(f"📊 Summary:")
    print(f"   - Commits: {len(commits)}")
    print(f"   - Patches: {len(patches)}")
    print(f"   - New Version: {version_info['new_version']}")

if __name__ == '__main__':
    main()

