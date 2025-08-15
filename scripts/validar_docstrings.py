#!/usr/bin/env python3
"""
Script para validar docstrings em funções críticas do projeto.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-004
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import os
import ast
import re
from typing import List, Dict, Set, Tuple
from pathlib import Path


class DocstringValidator:
    """Validador de docstrings para funções críticas."""
    
    def __init__(self, projeto_path: str = "."):
        """
        Inicializa o validador.
        
        Args:
            projeto_path: Caminho raiz do projeto
        """
        self.projeto_path = Path(projeto_path)
        self.funcoes_criticas = {
            "coletar_keywords": "Função principal de coleta de keywords",
            "extrair_sugestoes": "Função de extração de sugestões",
            "extrair_metricas_especificas": "Função de extração de métricas",
            "processar": "Função principal de processamento",
            "normalizar": "Função de normalização",
            "enriquecer": "Função de enriquecimento",
            "validar": "Função de validação",
            "limpar": "Função de limpeza"
        }
        
        self.arquivos_analisados = []
        self.funcoes_sem_docstring = []
        self.funcoes_com_docstring = []
        
    def analisar_arquivo(self, arquivo_path: Path) -> List[Dict]:
        """
        Analisa um arquivo Python em busca de funções críticas.
        
        Args:
            arquivo_path: Caminho do arquivo a analisar
            
        Returns:
            Lista de funções encontradas com informações
        """
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            tree = ast.parse(conteudo)
            funcoes_encontradas = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Verifica se é uma função crítica
                    for funcao_critica in self.funcoes_criticas.keys():
                        if funcao_critica in node.name:
                            funcoes_encontradas.append({
                                'arquivo': str(arquivo_path),
                                'nome': node.name,
                                'linha': node.lineno,
                                'tem_docstring': ast.get_docstring(node) is not None,
                                'docstring': ast.get_docstring(node),
                                'tipo': 'função crítica'
                            })
                            break
                    
                    # Verifica se é método de classe (tem self como primeiro parâmetro)
                    if (isinstance(node, ast.FunctionDef) and 
                        node.args.args and 
                        node.args.args[0].arg == 'self'):
                        
                        for funcao_critica in self.funcoes_criticas.keys():
                            if funcao_critica in node.name:
                                funcoes_encontradas.append({
                                    'arquivo': str(arquivo_path),
                                    'nome': node.name,
                                    'linha': node.lineno,
                                    'tem_docstring': ast.get_docstring(node) is not None,
                                    'docstring': ast.get_docstring(node),
                                    'tipo': 'método crítico'
                                })
                                break
            
            return funcoes_encontradas
            
        except Exception as e:
            print(f"Erro ao analisar {arquivo_path}: {e}")
            return []
    
    def analisar_projeto(self) -> Dict:
        """
        Analisa todo o projeto em busca de funções críticas.
        
        Returns:
            Dicionário com resultados da análise
        """
        diretorios_analisar = [
            'infrastructure/coleta',
            'infrastructure/processamento', 
            'backend/app/services',
            'shared/utils'
        ]
        
        total_funcoes = 0
        funcoes_sem_docstring = 0
        funcoes_com_docstring = 0
        
        for diretorio in diretorios_analisar:
            diretorio_path = self.projeto_path / diretorio
            if not diretorio_path.exists():
                continue
                
            for arquivo_path in diretorio_path.rglob("*.py"):
                if arquivo_path.name.startswith('__'):
                    continue
                    
                self.arquivos_analisados.append(str(arquivo_path))
                funcoes = self.analisar_arquivo(arquivo_path)
                
                for funcao in funcoes:
                    total_funcoes += 1
                    
                    if funcao['tem_docstring']:
                        funcoes_com_docstring += 1
                        self.funcoes_com_docstring.append(funcao)
                    else:
                        funcoes_sem_docstring += 1
                        self.funcoes_sem_docstring.append(funcao)
        
        return {
            'total_funcoes': total_funcoes,
            'funcoes_com_docstring': funcoes_com_docstring,
            'funcoes_sem_docstring': funcoes_sem_docstring,
            'cobertura': (funcoes_com_docstring / total_funcoes * 100) if total_funcoes > 0 else 0,
            'arquivos_analisados': len(self.arquivos_analisados)
        }
    
    def gerar_relatorio(self) -> str:
        """
        Gera relatório detalhado da análise.
        
        Returns:
            Relatório em formato texto
        """
        resultados = self.analisar_projeto()
        
        relatorio = f"""
# 📋 RELATÓRIO DE VALIDAÇÃO DE DOCSTRINGS

## 📊 Resumo Executivo
- **Total de Funções Críticas**: {resultados['total_funcoes']}
- **Com Docstring**: {resultados['funcoes_com_docstring']}
- **Sem Docstring**: {resultados['funcoes_sem_docstring']}
- **Cobertura**: {resultados['cobertura']:.1f}%
- **Arquivos Analisados**: {resultados['arquivos_analisados']}

## ✅ Funções com Docstring ({resultados['funcoes_com_docstring']})
"""
        
        for funcao in self.funcoes_com_docstring:
            relatorio += f"- **{funcao['nome']}** ({funcao['arquivo']}:{funcao['linha']})\n"
        
        relatorio += f"""
## ❌ Funções Sem Docstring ({resultados['funcoes_sem_docstring']})
"""
        
        for funcao in self.funcoes_sem_docstring:
            relatorio += f"- **{funcao['nome']}** ({funcao['arquivo']}:{funcao['linha']})\n"
        
        relatorio += f"""
## 📁 Arquivos Analisados
"""
        
        for arquivo in self.arquivos_analisados:
            relatorio += f"- {arquivo}\n"
        
        return relatorio
    
    def validar_qualidade_docstring(self, docstring: str) -> Dict:
        """
        Valida a qualidade de uma docstring.
        
        Args:
            docstring: Docstring a ser validada
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not docstring:
            return {
                'completa': False,
                'tem_args': False,
                'tem_returns': False,
                'tem_descricao': False,
                'pontuacao': 0
            }
        
        # Verifica se tem descrição
        tem_descricao = len(docstring.strip()) > 10
        
        # Verifica se tem Args
        tem_args = 'Args:' in docstring or 'args:' in docstring
        
        # Verifica se tem Returns
        tem_returns = 'Returns:' in docstring or 'returns:' in docstring
        
        # Calcula pontuação
        pontuacao = 0
        if tem_descricao:
            pontuacao += 30
        if tem_args:
            pontuacao += 35
        if tem_returns:
            pontuacao += 35
        
        return {
            'completa': pontuacao >= 80,
            'tem_args': tem_args,
            'tem_returns': tem_returns,
            'tem_descricao': tem_descricao,
            'pontuacao': pontuacao
        }


def main():
    """Função principal do script."""
    print("🔍 Iniciando validação de docstrings...")
    
    validator = DocstringValidator()
    relatorio = validator.gerar_relatorio()
    
    print(relatorio)
    
    # Salva relatório em arquivo
    with open('relatorio_docstrings.md', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("\n📄 Relatório salvo em 'relatorio_docstrings.md'")
    
    # Valida qualidade das docstrings existentes
    print("\n🔍 Validando qualidade das docstrings existentes...")
    
    total_qualidade = 0
    docstrings_analisadas = 0
    
    for funcao in validator.funcoes_com_docstring:
        qualidade = validator.validar_qualidade_docstring(funcao['docstring'])
        total_qualidade += qualidade['pontuacao']
        docstrings_analisadas += 1
        
        if not qualidade['completa']:
            print(f"⚠️  Docstring incompleta: {funcao['nome']} ({funcao['arquivo']})")
            print(f"   Pontuação: {qualidade['pontuacao']}/100")
    
    if docstrings_analisadas > 0:
        media_qualidade = total_qualidade / docstrings_analisadas
        print(f"\n📊 Qualidade média das docstrings: {media_qualidade:.1f}/100")
    
    print("\n✅ Validação concluída!")


if __name__ == "__main__":
    main() 