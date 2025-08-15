import os
import shutil
import datetime
import logging
from typing import Dict, List, Optional, Any

BACKUP_DIR = 'backups'
ITENS = ['blogs', 'logs', 'uploads', 'relatorio_performance.json', 'docs/relatorio_negocio.html']

logging.basicConfig(filename='logs/backup_restore.log', level=logging.INFO)

def backup():
    data = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    nome = f'backup_{data}.zip'
    path = os.path.join(BACKUP_DIR, nome)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.make_archive(path.replace('.zip', ''), 'zip', '.')
    logging.info(f'[{data}] BACKUP criado: {path}')
    print(f'[OK] Backup salvo em {path}')

def restore(backup_file):
    if not os.path.exists(backup_file):
        print(f'[ERRO] Arquivo não encontrado: {backup_file}')
        return
    shutil.unpack_archive(backup_file, '.')
    data = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    logging.info(f'[{data}] RESTORE executado: {backup_file}')
    print(f'[OK] Restore concluído de {backup_file}')

def listar():
    print('Backups disponíveis:')
    for f in os.listdir(BACKUP_DIR):
        if f.endswith('.zip'):
            print(f'- {f}')

def main():
    import sys
    if len(sys.argv) < 2:
        print('Uso: python scripts/backup_restore.py [backup|restore|listar] [arquivo]')
        return
    cmd = sys.argv[1]
    if cmd == 'backup':
        backup()
    elif cmd == 'restore' and len(sys.argv) > 2:
        restore(sys.argv[2])
    elif cmd == 'listar':
        listar()
    else:
        print('Comando inválido.')

if __name__ == '__main__':
    main() 