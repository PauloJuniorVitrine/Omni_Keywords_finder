from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Script de Configuração e Inicialização do Sistema de Backup Automático

Este script configura e inicia o sistema de backup automático do Omni Keywords Finder.
Inclui validação de dependências, configuração de cronograma e monitoramento.

Autor: Sistema de Backup Automático
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.backup.auto_backup import AutoBackupSystem, BACKUP_CONFIG

def setup_logging():
    """Configura logging para o script de setup"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)string_data [%(levelname)string_data] [SETUP_BACKUP] %(message)string_data',
        handlers=[
            logging.FileHandler(log_dir / 'setup_backup.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verifica dependências necessárias"""
    logging.info("Verificando dependências...")
    
    required_packages = [
        'schedule',
        'psutil',
        'zipfile',
        'sqlite3',
        'hashlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logging.info(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logging.error(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        logging.error(f"Dependências faltando: {', '.join(missing_packages)}")
        logging.info("Instale as dependências com: pip install schedule psutil")
        return False
    
    logging.info("Todas as dependências estão instaladas")
    return True

def check_disk_space():
    """Verifica espaço em disco disponível"""
    logging.info("Verificando espaço em disco...")
    
    try:
        import psutil
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        
        logging.info(f"Espaço livre: {free_gb:.2f} GB")
        
        if free_gb < 1.0:  # Menos de 1GB
            logging.warning("⚠️ Espaço em disco baixo. Considere liberar espaço.")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"Erro ao verificar espaço em disco: {str(e)}")
        return False

def create_backup_config():
    """Cria arquivo de configuração personalizado"""
    logging.info("Criando configuração de backup...")
    
    config_file = Path('backup_config.json')
    
    if config_file.exists():
        logging.info("Arquivo de configuração já existe")
        return True
    
    config = {
        'backup_dir': 'backups',
        'retention_days': 30,
        'compression_level': 9,
        'max_backup_size_mb': 500,
        'backup_schedule': '02:00',
        'critical_files': [
            'backend/db.sqlite3',
            'backend/instance/db.sqlite3',
            'instance/db.sqlite3',
            'blogs/',
            'logs/',
            'uploads/',
            'relatorio_performance.json',
            'docs/relatorio_negocio.html',
            '.env',
            'env.example'
        ],
        'exclude_patterns': [
            '__pycache__',
            '.git',
            'node_modules',
            '*.tmp',
            '*.log',
            'backups/',
            'coverage/',
            'htmlcov/',
            'cypress/screenshots/'
        ],
        'notification_email': '',
        'notification_webhook': '',
        'auto_restart_on_failure': True,
        'max_retry_attempts': 3
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info(f"Configuração criada: {config_file}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao criar configuração: {str(e)}")
        return False

def test_backup_system():
    """Testa o sistema de backup"""
    logging.info("Testando sistema de backup...")
    
    try:
        backup_system = AutoBackupSystem()
        
        # Criar backup de teste
        metadata = backup_system.create_backup()
        
        if metadata and metadata.status == 'completed':
            logging.info("✅ Teste de backup bem-sucedido")
            
            # Listar backups
            backups = backup_system.list_backups()
            logging.info(f"Backups encontrados: {len(backups)}")
            
            return True
        else:
            logging.error("❌ Teste de backup falhou")
            if metadata:
                logging.error(f"Erro: {metadata.error_message}")
            return False
            
    except Exception as e:
        logging.error(f"Erro no teste de backup: {str(e)}")
        return False

def create_systemd_service():
    """Cria serviço systemd para backup automático (Linux)"""
    if os.name != 'posix':
        logging.info("Sistema não é Linux, pulando criação de serviço systemd")
        return True
    
    service_content = """[Unit]
Description=Omni Keywords Finder Auto Backup
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={workdir}
ExecStart={python} {script}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
""".format(
        user=os.getenv('USER', 'root'),
        workdir=os.getcwd(),
        python=sys.executable,
        script=os.path.join(os.getcwd(), 'infrastructure', 'backup', 'auto_backup.py')
    )
    
    service_file = '/etc/systemd/system/omni-backup.service'
    
    try:
        # Verificar se tem permissão de root
        if os.geteuid() != 0:
            logging.warning("⚠️ Execute como root para criar serviço systemd")
            logging.info(f"Conteúdo do serviço salvo em: {service_file}")
            return False
        
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Recarregar systemd
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        
        logging.info("✅ Serviço systemd criado")
        logging.info("Para ativar: sudo systemctl enable omni-backup")
        logging.info("Para iniciar: sudo systemctl start omni-backup")
        
        return True
        
    except Exception as e:
        logging.error(f"Erro ao criar serviço systemd: {str(e)}")
        return False

def create_windows_task():
    """Cria tarefa agendada do Windows"""
    if os.name != 'nt':
        logging.info("Sistema não é Windows, pulando criação de tarefa agendada")
        return True
    
    try:
        # Criar script PowerShell para agendar tarefa
        ps_script = f"""
$action = New-ScheduledTaskAction -Execute "{sys.executable}" -Argument "{os.path.join(os.getcwd(), 'infrastructure', 'backup', 'auto_backup.py')} daemon" -WorkingDirectory "{os.getcwd()}"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "{os.getenv('USERNAME')}" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName "OmniKeywordsBackup" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Backup automático do Omni Keywords Finder"
"""
        
        script_file = 'setup_backup_task.ps1'
        with open(script_file, 'w') as f:
            f.write(ps_script)
        
        logging.info(f"✅ Script PowerShell criado: {script_file}")
        logging.info("Execute como administrador: powershell -ExecutionPolicy Bypass -File setup_backup_task.ps1")
        
        return True
        
    except Exception as e:
        logging.error(f"Erro ao criar tarefa do Windows: {str(e)}")
        return False

def create_cron_job():
    """Cria job cron para backup automático (Unix/Linux)"""
    if os.name != 'posix':
        logging.info("Sistema não é Unix/Linux, pulando criação de job cron")
        return True
    
    cron_job = f"0 2 * * * cd {os.getcwd()} && {sys.executable} infrastructure/backup/auto_backup.py backup >> logs/cron_backup.log 2>&1"
    
    try:
        # Tentar adicionar ao crontab
        result = subprocess.run(['crontab', '-list_data'], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        if 'omni-backup' not in current_crontab:
            new_crontab = current_crontab + f"\n# Omni Keywords Finder Backup\n{cron_job}\n"
            
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(new_crontab)
                temp_file = f.name
            
            try:
                subprocess.run(['crontab', temp_file], check=True)
                logging.info("✅ Job cron criado")
                logging.info(f"Cron job: {cron_job}")
            finally:
                os.unlink(temp_file)
        else:
            logging.info("Job cron já existe")
        
        return True
        
    except Exception as e:
        logging.error(f"Erro ao criar job cron: {str(e)}")
        logging.info("Adicione manualmente ao crontab:")
        logging.info(f"crontab -e")
        logging.info(f"Adicione: {cron_job}")
        return False

def main():
    """Função principal"""
    print("🚀 Configuração do Sistema de Backup Automático")
    print("=" * 50)
    
    setup_logging()
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        return 1
    
    # Verificar espaço em disco
    if not check_disk_space():
        print("⚠️ Aviso sobre espaço em disco")
    
    # Criar configuração
    if not create_backup_config():
        print("❌ Falha na criação da configuração")
        return 1
    
    # Testar sistema
    if not test_backup_system():
        print("❌ Falha no teste do sistema")
        return 1
    
    # Configurar agendamento baseado no sistema operacional
    if os.name == 'nt':  # Windows
        create_windows_task()
    else:  # Unix/Linux
        create_cron_job()
        create_systemd_service()
    
    print("\n✅ Configuração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Verifique os logs em logs/setup_backup.log")
    print("2. Teste o backup manual: python infrastructure/backup/auto_backup.py backup")
    print("3. Liste backups: python infrastructure/backup/auto_backup.py list")
    print("4. Configure notificações no arquivo backup_config.json")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 