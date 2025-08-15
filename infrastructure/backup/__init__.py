from typing import Dict, List, Optional, Any
"""
Módulo de Backup e Recuperação Automática

Este módulo fornece funcionalidades completas de backup automático,
recuperação e validação de integridade para o sistema Omni Keywords Finder.

Funcionalidades:
- Backup automático diário
- Retenção configurável
- Compressão de dados
- Validação de integridade
- Recuperação automática
- Monitoramento de performance

Autor: Sistema de Backup Automático
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

from .auto_backup import AutoBackupSystem, BackupMetadata, BackupIntegrityValidator, DatabaseBackupManager

__all__ = [
    'AutoBackupSystem',
    'BackupMetadata', 
    'BackupIntegrityValidator',
    'DatabaseBackupManager'
] 