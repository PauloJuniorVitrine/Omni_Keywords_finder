"""
Exemplo Prático do Sistema de Colaboração em Tempo Real
=======================================================

Este exemplo demonstra como usar o sistema de colaboração em tempo real
incluindo edição colaborativa, comentários e versionamento.

Tracing ID: EXAMPLE_COLLAB_001
Data: 2024-12-19
Versão: 1.0
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any

from infrastructure.collaboration.realtime_editor import (
    RealtimeEditor, Operation, OperationType, Document, CursorPosition
)
from infrastructure.collaboration.comment_system import (
    CommentSystem, CommentType, CommentStatus
)
from infrastructure.collaboration.version_control import (
    VersionControl, VersionType, MergeStatus
)


class CollaborationExample:
    """Exemplo completo de sistema de colaboração"""
    
    def __init__(self):
        self.editor = RealtimeEditor()
        self.comment_system = CommentSystem()
        self.version_control = VersionControl()
        
        # Dados de exemplo
        self.document_id = "doc_exemplo_001"
        self.users = {
            "user1": {"name": "João Silva", "color": "#007ACC"},
            "user2": {"name": "Maria Santos", "color": "#FF6B6B"},
            "user3": {"name": "Pedro Costa", "color": "#4ECDC4"}
        }
    
    async def run_complete_example(self):
        """Executa exemplo completo do sistema de colaboração"""
        print("🚀 INICIANDO EXEMPLO DE COLABORAÇÃO EM TEMPO REAL")
        print("=" * 60)
        
        # 1. Simular entrada de usuários
        await self.simulate_users_joining()
        
        # 2. Simular edição colaborativa
        await self.simulate_collaborative_editing()
        
        # 3. Simular sistema de comentários
        await self.simulate_comment_system()
        
        # 4. Simular versionamento
        await self.simulate_version_control()
        
        # 5. Simular merge de branches
        await self.simulate_branch_merging()
        
        # 6. Mostrar estatísticas finais
        self.show_final_statistics()
        
        print("\n✅ EXEMPLO CONCLUÍDO COM SUCESSO!")
    
    async def simulate_users_joining(self):
        """Simula entrada de usuários no documento"""
        print("\n👥 1. SIMULAÇÃO DE ENTRADA DE USUÁRIOS")
        print("-" * 40)
        
        for user_id, user_info in self.users.items():
            # Simular entrada no documento
            document = Document(
                id=self.document_id,
                created_by=user_id
            )
            self.editor.documents[self.document_id] = document
            
            # Adicionar usuário como colaborador
            document.collaborators.add(user_id)
            self.editor.user_sessions[user_id] = f"session_{user_id}"
            
            print(f"✅ {user_info['name']} entrou no documento")
            
            # Simular movimento de cursor
            cursor = CursorPosition(
                user_id=user_id,
                position=0,
                color=user_info['color'],
                name=user_info['name']
            )
            document.cursors[user_id] = cursor
            
            await asyncio.sleep(0.1)  # Simular latência
    
    async def simulate_collaborative_editing(self):
        """Simula edição colaborativa em tempo real"""
        print("\n✏️ 2. SIMULAÇÃO DE EDIÇÃO COLABORATIVA")
        print("-" * 40)
        
        document = self.editor.documents[self.document_id]
        
        # Simular operações simultâneas
        operations = [
            {
                "user_id": "user1",
                "type": OperationType.INSERT,
                "position": 0,
                "content": "Olá, pessoal! Vamos trabalhar juntos neste documento.\n\n"
            },
            {
                "user_id": "user2",
                "type": OperationType.INSERT,
                "position": 0,
                "content": "Perfeito! Vou adicionar algumas ideias:\n\n"
            },
            {
                "user_id": "user3",
                "type": OperationType.INSERT,
                "position": 0,
                "content": "Excelente iniciativa! Aqui estão minhas sugestões:\n\n"
            }
        ]
        
        # Aplicar operações
        for index, op_data in enumerate(operations):
            operation = Operation(
                type=op_data["type"],
                position=op_data["position"],
                content=op_data["content"],
                user_id=op_data["user_id"],
                session_id=f"session_{op_data['user_id']}",
                version=index + 1
            )
            
            # Aplicar operação
            await self.editor.apply_operation(document, operation)
            
            user_name = self.users[op_data["user_id"]]["name"]
            print(f"✏️ {user_name} adicionou: '{op_data['content'].strip()}'")
            
            # Simular movimento de cursor
            cursor = CursorPosition(
                user_id=op_data["user_id"],
                position=len(document.content),
                color=self.users[op_data["user_id"]]["color"],
                name=user_name
            )
            document.cursors[op_data["user_id"]] = cursor
            
            await asyncio.sleep(0.2)  # Simular latência
        
        # Simular edições simultâneas
        print("\n🔄 Simulando edições simultâneas...")
        
        # User1 edita no meio do texto
        operation1 = Operation(
            type=OperationType.INSERT,
            position=20,
            content="[EDITADO POR JOÃO] ",
            user_id="user1",
            session_id="session_user1",
            version=4
        )
        
        # User2 edita no final
        operation2 = Operation(
            type=OperationType.INSERT,
            position=len(document.content),
            content="\n\n[ADICIONADO POR MARIA] Vamos continuar colaborando!",
            user_id="user2",
            session_id="session_user2",
            version=5
        )
        
        # Aplicar operações simultaneamente
        await asyncio.gather(
            self.editor.apply_operation(document, operation1),
            self.editor.apply_operation(document, operation2)
        )
        
        print(f"📄 Conteúdo final do documento ({len(document.content)} caracteres):")
        print(f"'{document.content[:100]}...'")
        print(f"👥 Colaboradores ativos: {len(document.collaborators)}")
        print(f"📊 Total de operações: {len(document.operations)}")
    
    async def simulate_comment_system(self):
        """Simula sistema de comentários"""
        print("\n💬 3. SIMULAÇÃO DE SISTEMA DE COMENTÁRIOS")
        print("-" * 40)
        
        # Criar comentários
        comments_data = [
            {
                "user_id": "user1",
                "content": "Este parágrafo precisa ser revisado",
                "position": 10,
                "comment_type": CommentType.SUGGESTION,
                "tags": {"revisão", "melhoria"}
            },
            {
                "user_id": "user2",
                "content": "Encontrei um erro de gramática aqui",
                "position": 25,
                "comment_type": CommentType.BUG,
                "tags": {"gramática", "correção"}
            },
            {
                "user_id": "user3",
                "content": "Sugestão: adicionar mais exemplos",
                "position": 50,
                "comment_type": CommentType.FEATURE,
                "tags": {"exemplos", "melhoria"}
            }
        ]
        
        comments = []
        for comment_data in comments_data:
            comment = self.comment_system.create_comment(
                document_id=self.document_id,
                **comment_data
            )
            comments.append(comment)
            
            user_name = self.users[comment_data["user_id"]]["name"]
            print(f"💬 {user_name} comentou: '{comment_data['content']}'")
        
        # Adicionar respostas aos comentários
        replies_data = [
            {"comment_index": 0, "user_id": "user2", "content": "Concordo, vou revisar"},
            {"comment_index": 1, "user_id": "user1", "content": "Obrigado, vou corrigir"},
            {"comment_index": 2, "user_id": "user2", "content": "Ótima sugestão!"}
        ]
        
        for reply_data in replies_data:
            comment = comments[reply_data["comment_index"]]
            reply = self.comment_system.add_reply(
                comment_id=comment.id,
                user_id=reply_data["user_id"],
                content=reply_data["content"]
            )
            
            user_name = self.users[reply_data["user_id"]]["name"]
            print(f"  ↳ {user_name} respondeu: '{reply_data['content']}'")
        
        # Resolver um comentário
        resolved_comment = self.comment_system.resolve_comment(
            comment_id=comments[1].id,
            user_id="user1"
        )
        print(f"✅ Comentário resolvido por {self.users['user1']['name']}")
        
        # Mostrar estatísticas dos comentários
        stats = self.comment_system.get_statistics(self.document_id)
        print(f"\n📊 Estatísticas dos comentários:")
        print(f"  • Total: {stats['total_comments']}")
        print(f"  • Ativos: {stats['active_comments']}")
        print(f"  • Resolvidos: {stats['resolved_comments']}")
        print(f"  • Respostas: {stats['total_replies']}")
        print(f"  • Média de respostas: {stats['avg_replies_per_comment']:.1f}")
    
    async def simulate_version_control(self):
        """Simula sistema de versionamento"""
        print("\n🔄 4. SIMULAÇÃO DE SISTEMA DE VERSIONAMENTO")
        print("-" * 40)
        
        # Criar versão inicial
        initial_content = "Conteúdo inicial do documento colaborativo."
        version1 = self.version_control.create_version(
            document_id=self.document_id,
            content=initial_content,
            author_id="user1",
            version_type=VersionType.MANUAL,
            message="Versão inicial"
        )
        print(f"📝 Versão {version1.version_number} criada por {self.users['user1']['name']}")
        
        # Criar branch para feature
        feature_branch = self.version_control.create_branch(
            document_id=self.document_id,
            branch_name="feature-melhoria",
            source_branch="main",
            author_id="user2"
        )
        print(f"🌿 Branch '{feature_branch.name}' criado por {self.users['user2']['name']}")
        
        # Adicionar versão no branch principal
        main_content = initial_content + "\n\nAdições no branch principal."
        version2 = self.version_control.create_version(
            document_id=self.document_id,
            content=main_content,
            author_id="user1",
            version_type=VersionType.AUTO,
            message="Adições no main"
        )
        print(f"📝 Versão {version2.version_number} no main")
        
        # Adicionar versão no branch feature
        feature_content = initial_content + "\n\nMelhorias no branch feature."
        version3 = self.version_control.create_version(
            document_id=self.document_id,
            content=feature_content,
            author_id="user2",
            version_type=VersionType.MANUAL,
            message="Melhorias implementadas",
            branch_name="feature-melhoria"
        )
        print(f"📝 Versão {version3.version_number} no branch feature")
        
        # Criar merge request
        merge_request = self.version_control.create_merge_request(
            document_id=self.document_id,
            source_branch="feature-melhoria",
            target_branch="main",
            requester_id="user2",
            message="Merge das melhorias"
        )
        print(f"🔀 Merge request criado: {merge_request.source_branch} → {merge_request.target_branch}")
        
        # Mostrar histórico de versões
        main_history = self.version_control.get_version_history(self.document_id, "main")
        feature_history = self.version_control.get_version_history(self.document_id, "feature-melhoria")
        
        print(f"\n📋 Histórico do main: {len(main_history)} versões")
        print(f"📋 Histórico do feature: {len(feature_history)} versões")
        
        # Mostrar branches
        branches = self.version_control.get_branches(self.document_id)
        print(f"🌿 Branches ativos: {len(branches)}")
        for branch in branches:
            print(f"  • {branch.name} (criado por {self.users.get(branch.created_by, branch.created_by)['name']})")
    
    async def simulate_branch_merging(self):
        """Simula merge de branches"""
        print("\n🔀 5. SIMULAÇÃO DE MERGE DE BRANCHES")
        print("-" * 40)
        
        # Verificar conflitos no merge request
        merge_requests = self.version_control.get_merge_requests(self.document_id)
        if merge_requests:
            merge_request = merge_requests[0]
            
            print(f"🔍 Verificando conflitos no merge request {merge_request.id}...")
            conflicts = self.version_control.check_merge_conflicts(merge_request.id)
            
            if conflicts:
                print(f"⚠️ {len(conflicts)} conflitos detectados")
                for conflict in conflicts:
                    print(f"  • {conflict['description']}")
                
                # Resolver conflitos
                print("🔧 Resolvendo conflitos...")
                resolved_content = "Conteúdo inicial do documento colaborativo.\n\nAdições no branch principal.\n\nMelhorias do branch feature (resolvidas)."
                
                resolved_version = self.version_control.resolve_merge_conflicts(
                    merge_request.id,
                    resolved_content,
                    "user3"
                )
                print(f"✅ Conflitos resolvidos por {self.users['user3']['name']}")
                
                # Completar merge
                self.version_control.complete_merge(merge_request.id, "user3")
                print("✅ Merge completado com sucesso!")
                
                # Mostrar versão final
                latest_version = self.version_control.get_latest_version(self.document_id, "main")
                print(f"📝 Versão final: {latest_version.version_number}")
                print(f"📄 Conteúdo: '{latest_version.content[:50]}...'")
            else:
                print("✅ Nenhum conflito detectado")
    
    def show_final_statistics(self):
        """Mostra estatísticas finais do sistema"""
        print("\n📊 6. ESTATÍSTICAS FINAIS DO SISTEMA")
        print("-" * 40)
        
        # Estatísticas do editor
        editor_stats = self.editor.get_system_stats()
        print("🎯 EDITOR COLABORATIVO:")
        print(f"  • Sessões ativas: {editor_stats['active_sessions']}")
        print(f"  • Usuários ativos: {editor_stats['active_users']}")
        print(f"  • Documentos: {editor_stats['documents_count']}")
        print(f"  • Total de operações: {editor_stats['total_operations']}")
        
        # Estatísticas dos comentários
        comment_stats = self.comment_system.get_statistics(self.document_id)
        print("\n💬 SISTEMA DE COMENTÁRIOS:")
        print(f"  • Total de comentários: {comment_stats['total_comments']}")
        print(f"  • Comentários ativos: {comment_stats['active_comments']}")
        print(f"  • Comentários resolvidos: {comment_stats['resolved_comments']}")
        print(f"  • Total de respostas: {comment_stats['total_replies']}")
        print(f"  • Média de respostas: {comment_stats['avg_replies_per_comment']:.1f}")
        
        # Estatísticas do versionamento
        version_stats = self.version_control.get_statistics(self.document_id)
        print("\n🔄 SISTEMA DE VERSIONAMENTO:")
        print(f"  • Total de versões: {version_stats['total_versions']}")
        print(f"  • Total de branches: {version_stats['total_branches']}")
        print(f"  • Merge requests: {version_stats['total_merge_requests']}")
        
        # Detalhes por tipo
        print(f"  • Versões por tipo:")
        for version_type, count in version_stats['versions_by_type'].items():
            print(f"    - {version_type}: {count}")
        
        print(f"  • Branches por documento:")
        for doc_id, count in version_stats['branches_by_document'].items():
            print(f"    - {doc_id}: {count}")
        
        # Resumo final
        print("\n🎉 RESUMO FINAL:")
        total_operations = (
            editor_stats['total_operations'] +
            comment_stats['total_comments'] +
            version_stats['total_versions']
        )
        print(f"  • Total de operações no sistema: {total_operations}")
        print(f"  • Usuários participantes: {len(self.users)}")
        print(f"  • Documento colaborativo: {self.document_id}")
        print(f"  • Tempo de execução: {time.time() - self.start_time:.2f}string_data")


async def main():
    """Função principal"""
    example = CollaborationExample()
    example.start_time = time.time()
    await example.run_complete_example()


if __name__ == "__main__":
    asyncio.run(main()) 