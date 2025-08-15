from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Script de Backup Completo do Sistema - Omni Keywords Finder
Tracing ID: BACKUP_SISTEMA_001_20241227
"""

import os
import shutil
import json
import datetime
from pathlib import Path
import hashlib

class SistemaBackup:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"backup_sistema_antigo_{self.timestamp}"
        self.manifest_file = f"backup_manifest_{self.timestamp}.json"
        self.checksums_file = f"backup_checksums_{self.timestamp}.json"
        
    def calcular_checksum(self, file_path):
        """Calcula MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Erro ao calcular checksum de {file_path}: {e}")
            return None
    
    def criar_backup(self):
        """Cria backup completo do sistema"""
        print(f"🔴 INICIANDO BACKUP COMPLETO DO SISTEMA")
        print(f"📁 Diretório de backup: {self.backup_dir}")
        
        # Criar diretório de backup
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Diretórios críticos para backup
        diretorios_criticos = [
            "infrastructure",
            "backend",
            "app",
            "tests",
            "scripts",
            "config",
            "docs"
        ]
        
        manifest = {
            "timestamp": self.timestamp,
            "sistema": "Omni Keywords Finder",
            "tipo": "Backup Completo",
            "arquivos": [],
            "checksums": {},
            "estatisticas": {
                "total_arquivos": 0,
                "total_diretorios": 0,
                "tamanho_total": 0
            }
        }
        
        total_arquivos = 0
        total_diretorios = 0
        tamanho_total = 0
        
        for diretorio in diretorios_criticos:
            if os.path.exists(diretorio):
                print(f"📂 Fazendo backup de: {diretorio}")
                
                # Copiar diretório
                destino = os.path.join(self.backup_dir, diretorio)
                try:
                    shutil.copytree(diretorio, destino, dirs_exist_ok=True)
                    
                    # Contar arquivos e calcular checksums
                    for root, dirs, files in os.walk(destino):
                        total_diretorios += len(dirs)
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, self.backup_dir)
                            
                            # Calcular checksum
                            checksum = self.calcular_checksum(file_path)
                            
                            # Estatísticas
                            try:
                                tamanho = os.path.getsize(file_path)
                                tamanho_total += tamanho
                            except:
                                tamanho = 0
                            
                            manifest["arquivos"].append({
                                "arquivo": rel_path,
                                "tamanho": tamanho,
                                "checksum": checksum,
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                            
                            if checksum:
                                manifest["checksums"][rel_path] = checksum
                            
                            total_arquivos += 1
                            
                except Exception as e:
                    print(f"❌ Erro ao fazer backup de {diretorio}: {e}")
        
        # Backup de arquivos importantes na raiz
        arquivos_raiz = [
            "requirements.txt",
            "package.json",
            "README.md",
            "CHANGELOG.md",
            "pytest.ini",
            "docker-compose.observability.yml",
            "openapi.yaml"
        ]
        
        for arquivo in arquivos_raiz:
            if os.path.exists(arquivo):
                print(f"📄 Fazendo backup de: {arquivo}")
                shutil.copy2(arquivo, self.backup_dir)
                
                # Calcular checksum
                checksum = self.calcular_checksum(arquivo)
                tamanho = os.path.getsize(arquivo)
                tamanho_total += tamanho
                
                manifest["arquivos"].append({
                    "arquivo": arquivo,
                    "tamanho": tamanho,
                    "checksum": checksum,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                if checksum:
                    manifest["checksums"][arquivo] = checksum
                
                total_arquivos += 1
        
        # Atualizar estatísticas
        manifest["estatisticas"]["total_arquivos"] = total_arquivos
        manifest["estatisticas"]["total_diretorios"] = total_diretorios
        manifest["estatisticas"]["tamanho_total"] = tamanho_total
        
        # Salvar manifest
        with open(os.path.join(self.backup_dir, self.manifest_file), 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # Salvar checksums separadamente
        with open(os.path.join(self.backup_dir, self.checksums_file), 'w', encoding='utf-8') as f:
            json.dump(manifest["checksums"], f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ BACKUP CONCLUÍDO COM SUCESSO!")
        print(f"📊 Estatísticas:")
        print(f"   - Arquivos: {total_arquivos}")
        print(f"   - Diretórios: {total_diretorios}")
        print(f"   - Tamanho total: {tamanho_total / (1024*1024):.2f} MB")
        print(f"   - Manifest: {self.manifest_file}")
        print(f"   - Checksums: {self.checksums_file}")
        
        return self.backup_dir, manifest
    
    def verificar_integridade(self, backup_dir):
        """Verifica integridade do backup"""
        print(f"🔍 VERIFICANDO INTEGRIDADE DO BACKUP")
        
        manifest_path = None
        for file in os.listdir(backup_dir):
            if file.startswith("backup_manifest_"):
                manifest_path = os.path.join(backup_dir, file)
                break
        
        if not manifest_path:
            print("❌ Manifest não encontrado")
            return False
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        arquivos_verificados = 0
        arquivos_corrompidos = 0
        
        for arquivo_info in manifest["arquivos"]:
            arquivo_path = os.path.join(backup_dir, arquivo_info["arquivo"])
            
            if os.path.exists(arquivo_path):
                checksum_atual = self.calcular_checksum(arquivo_path)
                checksum_original = arquivo_info.get("checksum")
                
                if checksum_atual == checksum_original:
                    arquivos_verificados += 1
                else:
                    arquivos_corrompidos += 1
                    print(f"❌ Arquivo corrompido: {arquivo_info['arquivo']}")
            else:
                arquivos_corrompidos += 1
                print(f"❌ Arquivo não encontrado: {arquivo_info['arquivo']}")
        
        print(f"✅ Verificação concluída:")
        print(f"   - Arquivos verificados: {arquivos_verificados}")
        print(f"   - Arquivos corrompidos: {arquivos_corrompidos}")
        
        return arquivos_corrompidos == 0

if __name__ == "__main__":
    backup = SistemaBackup()
    backup_dir, manifest = backup.criar_backup()
    
    # Verificar integridade
    if backup.verificar_integridade(backup_dir):
        print(f"\n🎉 BACKUP VÁLIDO E PRONTO PARA MIGRAÇÃO!")
        print(f"📁 Backup salvo em: {backup_dir}")
    else:
        print(f"\n⚠️ ATENÇÃO: Backup pode estar corrompido!") 