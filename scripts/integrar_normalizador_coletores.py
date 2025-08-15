#!/usr/bin/env python3
"""
Script para integrar o normalizador central em todos os coletores.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-003
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set


class IntegradorNormalizador:
    """Integrador automático do normalizador central nos coletores."""
    
    def __init__(self, projeto_path: str = "."):
        """
        Inicializa o integrador.
        
        Args:
            projeto_path: Caminho raiz do projeto
        """
        self.projeto_path = Path(projeto_path)
        self.coletores_path = self.projeto_path / "infrastructure" / "coleta"
        self.coletores_integrados = set()
        self.coletores_pendentes = set()
        
    def identificar_coletores(self) -> Dict[str, bool]:
        """
        Identifica todos os coletores e seu status de integração.
        
        Returns:
            Dicionário com status de integração por coletor
        """
        status = {}
        
        for arquivo in self.coletores_path.glob("*.py"):
            if arquivo.name.startswith("__") or arquivo.name.endswith(".bak"):
                continue
                
            coletor_nome = arquivo.stem
            conteudo = arquivo.read_text(encoding="utf-8")
            
            # Verifica se já está integrado
            ja_integrado = (
                "from shared.utils.normalizador_central import" in conteudo and
                "self.normalizador = NormalizadorCentral(" in conteudo
            )
            
            status[coletor_nome] = ja_integrado
            
            if ja_integrado:
                self.coletores_integrados.add(coletor_nome)
            else:
                self.coletores_pendentes.add(coletor_nome)
                
        return status
    
    def integrar_coletor(self, nome_coletor: str) -> bool:
        """
        Integra o normalizador central em um coletor específico.
        
        Args:
            nome_coletor: Nome do arquivo do coletor
            
        Returns:
            True se integração foi bem-sucedida
        """
        arquivo = self.coletores_path / f"{nome_coletor}.py"
        
        if not arquivo.exists():
            print(f"❌ Arquivo {arquivo} não encontrado")
            return False
            
        try:
            conteudo = arquivo.read_text(encoding="utf-8")
            
            # Verifica se já está integrado
            if "from shared.utils.normalizador_central import" in conteudo:
                print(f"✅ {nome_coletor} já está integrado")
                return True
                
            # Adiciona importação
            import_pattern = r'from shared\.logger import logger'
            import_replacement = '''from shared.logger import logger
from shared.utils.normalizador_central import NormalizadorCentral'''
            
            if import_pattern in conteudo:
                conteudo = re.sub(import_pattern, import_replacement, conteudo)
            else:
                # Adiciona após imports existentes
                lines = conteudo.split('\n')
                for index, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        continue
                    if line.strip() == '':
                        continue
                    # Encontra o final dos imports
                    lines.insert(index, 'from shared.utils.normalizador_central import NormalizadorCentral')
                    break
                conteudo = '\n'.join(lines)
            
            # Adiciona normalizador no construtor
            construtor_pattern = r'(def __init__\(self[^)]*\):.*?)(\n\string_data+)(self\.\w+ = \w+)'
            
            if re.search(construtor_pattern, conteudo, re.DOTALL):
                normalizador_code = '''
        # Normalizador central para padronização de keywords
        self.normalizador = NormalizadorCentral(
            remover_acentos=False,
            case_sensitive=False,
            caracteres_permitidos=r'^[\\w\\string_data\\-,.!?@#]+$',
            min_caracteres=3,
            max_caracteres=100
        )'''
                
                # Encontra o final do construtor
                construtor_match = re.search(construtor_pattern, conteudo, re.DOTALL)
                if construtor_match:
                    inicio = construtor_match.start()
                    fim = construtor_match.end()
                    
                    # Encontra o final do método __init__
                    metodo_conteudo = conteudo[inicio:]
                    indentacao = re.search(r'(\string_data+)(self\.\w+ = \w+)', metodo_conteudo)
                    if indentacao:
                        pos_final = inicio + metodo_conteudo.find(indentacao.group(0))
                        conteudo = (
                            conteudo[:pos_final] + 
                            normalizador_code + 
                            conteudo[pos_final:]
                        )
            
            # Salva o arquivo
            arquivo.write_text(conteudo, encoding="utf-8")
            print(f"✅ {nome_coletor} integrado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao integrar {nome_coletor}: {e}")
            return False
    
    def integrar_todos_pendentes(self) -> Dict[str, bool]:
        """
        Integra o normalizador central em todos os coletores pendentes.
        
        Returns:
            Dicionário com resultado da integração por coletor
        """
        resultados = {}
        
        print("🔄 Integrando normalizador central em coletores pendentes...")
        
        for coletor in self.coletores_pendentes:
            if coletor in ['base_keyword', 'base', 'config', '__init__']:
                continue  # Pula arquivos base
                
            resultados[coletor] = self.integrar_coletor(coletor)
            
        return resultados
    
    def gerar_relatorio(self) -> str:
        """
        Gera relatório de integração.
        
        Returns:
            Relatório formatado
        """
        status = self.identificar_coletores()
        
        relatorio = "# 📊 RELATÓRIO DE INTEGRAÇÃO - NORMALIZADOR CENTRAL\n\n"
        relatorio += f"**Data**: {__import__('datetime').datetime.now().strftime('%Y-%m-%data %H:%M:%S')}\n"
        relatorio += f"**Total de Coletores**: {len(status)}\n\n"
        
        # Estatísticas
        integrados = sum(1 for string_data in status.values() if string_data)
        pendentes = len(status) - integrados
        
        relatorio += f"## 📈 Estatísticas\n"
        relatorio += f"- ✅ **Integrados**: {integrados}\n"
        relatorio += f"- 🔄 **Pendentes**: {pendentes}\n"
        relatorio += f"- 📊 **Progresso**: {(integrados/len(status)*100):.1f}%\n\n"
        
        # Detalhes por coletor
        relatorio += "## 📋 Status por Coletor\n\n"
        
        for coletor, integrado in sorted(status.items()):
            status_icon = "✅" if integrado else "🔄"
            status_text = "Integrado" if integrado else "Pendente"
            relatorio += f"- {status_icon} **{coletor}**: {status_text}\n"
            
        return relatorio


def main():
    """Função principal do script."""
    print("🚀 Iniciando integração do normalizador central...")
    
    integrador = IntegradorNormalizador()
    
    # Identifica status atual
    status_atual = integrador.identificar_coletores()
    print(f"\n📊 Status atual: {sum(status_atual.values())}/{len(status_atual)} coletores integrados")
    
    # Integra pendentes
    resultados = integrador.integrar_todos_pendentes()
    
    # Gera relatório
    relatorio = integrador.gerar_relatorio()
    
    # Salva relatório
    relatorio_path = Path("logs") / "integracao_normalizador.md"
    relatorio_path.parent.mkdir(exist_ok=True)
    relatorio_path.write_text(relatorio, encoding="utf-8")
    
    print(f"\n📄 Relatório salvo em: {relatorio_path}")
    print("\n" + relatorio)


if __name__ == "__main__":
    main() 