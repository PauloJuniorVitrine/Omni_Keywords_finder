"""
Hash-based Audit Trails - Sistema de Trilhas de Auditoria com Hash
Tracing ID: METRICS-003
Data/Hora: 2024-12-20 02:00:00 UTC
Versão: 1.0
Status: IMPLEMENTAÇÃO INICIAL

Sistema enterprise para trilhas de auditoria com hash SHA-256, verificação
de integridade, chain de hashes e compliance com regulamentações.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import sqlite3
import threading
from collections import deque
import hmac
import base64

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Níveis de auditoria"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditCategory(Enum):
    """Categorias de auditoria"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIG = "system_config"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"
    SECURITY = "security"

@dataclass
class AuditEntry:
    """Entrada de auditoria"""
    entry_id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    user_id: Optional[str]
    session_id: Optional[str]
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    hash_value: str
    previous_hash: Optional[str]
    chain_position: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'category': self.category.value
        }
    
    def to_hash_string(self) -> str:
        """Converte para string para cálculo de hash"""
        return json.dumps({
            'entry_id': self.entry_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'category': self.category.value,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'action': self.action,
            'resource': self.resource,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'previous_hash': self.previous_hash,
            'chain_position': self.chain_position
        }, sort_keys=True, default=str)

@dataclass
class AuditChain:
    """Cadeia de auditoria"""
    chain_id: str
    start_timestamp: datetime
    end_timestamp: Optional[datetime]
    entry_count: int
    root_hash: str
    current_hash: str
    is_complete: bool
    integrity_verified: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'start_timestamp': self.start_timestamp.isoformat(),
            'end_timestamp': self.end_timestamp.isoformat() if self.end_timestamp else None
        }

@dataclass
class IntegrityReport:
    """Relatório de integridade"""
    report_id: str
    timestamp: datetime
    chain_id: str
    total_entries: int
    verified_entries: int
    corrupted_entries: int
    missing_entries: int
    integrity_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class HashBasedAuditTrail:
    """
    Sistema de trilhas de auditoria baseado em hash
    """
    
    def __init__(self, db_path: str = "audit_trail.db", 
                 redis_client: Optional[redis.Redis] = None,
                 secret_key: Optional[str] = None):
        """
        Inicializa o sistema de trilhas de auditoria
        
        Args:
            db_path: Caminho do banco SQLite
            redis_client: Cliente Redis para cache (opcional)
            secret_key: Chave secreta para HMAC (opcional)
        """
        self.db_path = db_path
        self.redis_client = redis_client
        self.secret_key = secret_key or "default_secret_key_change_in_production"
        self.current_chain: Optional[AuditChain] = None
        self.chain_lock = threading.Lock()
        
        # Inicializa banco de dados
        self._init_database()
        
        # Inicia nova cadeia
        self._start_new_chain()
        
        logger.info("[HASH_TRAIL] Sistema de trilhas de auditoria inicializado")
    
    def _init_database(self):
        """Inicializa banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de entradas de auditoria
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_entries (
                        entry_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        category TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        details TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        hash_value TEXT NOT NULL,
                        previous_hash TEXT,
                        chain_position INTEGER NOT NULL,
                        chain_id TEXT NOT NULL
                    )
                """)
                
                # Tabela de cadeias de auditoria
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_chains (
                        chain_id TEXT PRIMARY KEY,
                        start_timestamp TEXT NOT NULL,
                        end_timestamp TEXT,
                        entry_count INTEGER NOT NULL,
                        root_hash TEXT NOT NULL,
                        current_hash TEXT NOT NULL,
                        is_complete BOOLEAN NOT NULL,
                        integrity_verified BOOLEAN NOT NULL
                    )
                """)
                
                # Índices para performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_entries(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_entries(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_entries(action)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_chain_id ON audit_entries(chain_id)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao inicializar banco de dados: {e}")
            raise
    
    def _start_new_chain(self):
        """Inicia nova cadeia de auditoria"""
        try:
            with self.chain_lock:
                chain_id = f"chain_{int(time.time())}_{hash(str(datetime.utcnow()))}"
                root_hash = self._calculate_root_hash()
                
                self.current_chain = AuditChain(
                    chain_id=chain_id,
                    start_timestamp=datetime.utcnow(),
                    end_timestamp=None,
                    entry_count=0,
                    root_hash=root_hash,
                    current_hash=root_hash,
                    is_complete=False,
                    integrity_verified=True
                )
                
                # Salva no banco
                self._save_chain(self.current_chain)
                
                logger.info(f"[HASH_TRAIL] Nova cadeia iniciada: {chain_id}")
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao iniciar nova cadeia: {e}")
            raise
    
    def _calculate_root_hash(self) -> str:
        """Calcula hash raiz da cadeia"""
        root_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': 'omni_keywords_finder',
            'version': '1.0',
            'type': 'audit_chain_root'
        }
        
        root_string = json.dumps(root_data, sort_keys=True, default=str)
        return hashlib.sha256(root_string.encode()).hexdigest()
    
    def _save_chain(self, chain: AuditChain):
        """Salva cadeia no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO audit_chains 
                    (chain_id, start_timestamp, end_timestamp, entry_count, 
                     root_hash, current_hash, is_complete, integrity_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chain.chain_id,
                    chain.start_timestamp.isoformat(),
                    chain.end_timestamp.isoformat() if chain.end_timestamp else None,
                    chain.entry_count,
                    chain.root_hash,
                    chain.current_hash,
                    chain.is_complete,
                    chain.integrity_verified
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao salvar cadeia: {e}")
            raise
    
    def _save_entry(self, entry: AuditEntry):
        """Salva entrada no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_entries 
                    (entry_id, timestamp, level, category, user_id, session_id,
                     action, resource, details, ip_address, user_agent,
                     hash_value, previous_hash, chain_position, chain_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.entry_id,
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.category.value,
                    entry.user_id,
                    entry.session_id,
                    entry.action,
                    entry.resource,
                    json.dumps(entry.details),
                    entry.ip_address,
                    entry.user_agent,
                    entry.hash_value,
                    entry.previous_hash,
                    entry.chain_position,
                    self.current_chain.chain_id if self.current_chain else None
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao salvar entrada: {e}")
            raise
    
    def add_audit_entry(self, level: AuditLevel,
                       category: AuditCategory,
                       action: str,
                       resource: str,
                       details: Dict[str, Any],
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None) -> AuditEntry:
        """
        Adiciona entrada de auditoria
        
        Args:
            level: Nível de auditoria
            category: Categoria de auditoria
            action: Ação realizada
            resource: Recurso afetado
            details: Detalhes da ação
            user_id: ID do usuário (opcional)
            session_id: ID da sessão (opcional)
            ip_address: Endereço IP (opcional)
            user_agent: User agent (opcional)
            
        Returns:
            Entrada de auditoria criada
        """
        try:
            with self.chain_lock:
                if not self.current_chain:
                    self._start_new_chain()
                
                # Gera ID único
                entry_id = f"entry_{int(time.time() * 1000000)}_{hash(str(datetime.utcnow()))}"
                
                # Posição na cadeia
                chain_position = self.current_chain.entry_count
                
                # Hash anterior
                previous_hash = self.current_chain.current_hash
                
                # Cria entrada
                entry = AuditEntry(
                    entry_id=entry_id,
                    timestamp=datetime.utcnow(),
                    level=level,
                    category=category,
                    user_id=user_id,
                    session_id=session_id,
                    action=action,
                    resource=resource,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    hash_value="",  # Será calculado
                    previous_hash=previous_hash,
                    chain_position=chain_position
                )
                
                # Calcula hash da entrada
                entry.hash_value = self._calculate_entry_hash(entry)
                
                # Atualiza hash da cadeia
                self.current_chain.current_hash = entry.hash_value
                self.current_chain.entry_count += 1
                
                # Salva entrada e cadeia
                self._save_entry(entry)
                self._save_chain(self.current_chain)
                
                # Cache no Redis se disponível
                if self.redis_client:
                    cache_key = f"audit_entry:{entry_id}"
                    self.redis_client.setex(
                        cache_key,
                        3600,  # 1 hora
                        json.dumps(entry.to_dict())
                    )
                
                # Verifica se deve finalizar cadeia
                if self.current_chain.entry_count >= 10000:  # Limite de 10k entradas por cadeia
                    self._finalize_current_chain()
                
                logger.info(f"[HASH_TRAIL] Entrada adicionada: {entry_id}")
                return entry
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao adicionar entrada: {e}")
            raise
    
    def _calculate_entry_hash(self, entry: AuditEntry) -> str:
        """Calcula hash SHA-256 da entrada"""
        try:
            # String para hash
            hash_string = entry.to_hash_string()
            
            # Hash SHA-256
            hash_object = hashlib.sha256(hash_string.encode())
            
            # Adiciona HMAC se chave secreta estiver disponível
            if self.secret_key:
                hmac_object = hmac.new(
                    self.secret_key.encode(),
                    hash_object.digest(),
                    hashlib.sha256
                )
                return hmac_object.hexdigest()
            else:
                return hash_object.hexdigest()
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao calcular hash: {e}")
            raise
    
    def _finalize_current_chain(self):
        """Finaliza cadeia atual"""
        try:
            if self.current_chain:
                self.current_chain.end_timestamp = datetime.utcnow()
                self.current_chain.is_complete = True
                self._save_chain(self.current_chain)
                
                logger.info(f"[HASH_TRAIL] Cadeia finalizada: {self.current_chain.chain_id}")
                
                # Inicia nova cadeia
                self._start_new_chain()
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao finalizar cadeia: {e}")
            raise
    
    def get_audit_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Obtém entrada de auditoria por ID"""
        try:
            # Tenta cache primeiro
            if self.redis_client:
                cache_key = f"audit_entry:{entry_id}"
                cached = self.redis_client.get(cache_key)
                if cached:
                    data = json.loads(cached)
                    return self._dict_to_audit_entry(data)
            
            # Busca no banco
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT entry_id, timestamp, level, category, user_id, session_id,
                           action, resource, details, ip_address, user_agent,
                           hash_value, previous_hash, chain_position
                    FROM audit_entries
                    WHERE entry_id = ?
                """, (entry_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_audit_entry(row)
                
                return None
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao obter entrada {entry_id}: {e}")
            return None
    
    def _row_to_audit_entry(self, row: Tuple) -> AuditEntry:
        """Converte linha do banco para AuditEntry"""
        return AuditEntry(
            entry_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            level=AuditLevel(row[2]),
            category=AuditCategory(row[3]),
            user_id=row[4],
            session_id=row[5],
            action=row[6],
            resource=row[7],
            details=json.loads(row[8]),
            ip_address=row[9],
            user_agent=row[10],
            hash_value=row[11],
            previous_hash=row[12],
            chain_position=row[13]
        )
    
    def _dict_to_audit_entry(self, data: Dict[str, Any]) -> AuditEntry:
        """Converte dicionário para AuditEntry"""
        return AuditEntry(
            entry_id=data['entry_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            level=AuditLevel(data['level']),
            category=AuditCategory(data['category']),
            user_id=data['user_id'],
            session_id=data['session_id'],
            action=data['action'],
            resource=data['resource'],
            details=data['details'],
            ip_address=data['ip_address'],
            user_agent=data['user_agent'],
            hash_value=data['hash_value'],
            previous_hash=data['previous_hash'],
            chain_position=data['chain_position']
        )
    
    def verify_chain_integrity(self, chain_id: str) -> IntegrityReport:
        """
        Verifica integridade de uma cadeia de auditoria
        
        Args:
            chain_id: ID da cadeia
            
        Returns:
            Relatório de integridade
        """
        try:
            # Obtém cadeia
            chain = self._get_chain(chain_id)
            if not chain:
                raise ValueError(f"Cadeia {chain_id} não encontrada")
            
            # Obtém todas as entradas da cadeia
            entries = self._get_chain_entries(chain_id)
            
            verified_entries = 0
            corrupted_entries = 0
            missing_entries = 0
            violations = []
            
            previous_hash = chain.root_hash
            
            for index, entry in enumerate(entries):
                # Verifica se entrada está na posição correta
                if entry.chain_position != index:
                    missing_entries += 1
                    violations.append({
                        'type': 'position_mismatch',
                        'entry_id': entry.entry_id,
                        'expected_position': index,
                        'actual_position': entry.chain_position
                    })
                    continue
                
                # Verifica hash anterior
                if entry.previous_hash != previous_hash:
                    corrupted_entries += 1
                    violations.append({
                        'type': 'hash_mismatch',
                        'entry_id': entry.entry_id,
                        'expected_hash': previous_hash,
                        'actual_hash': entry.previous_hash
                    })
                    continue
                
                # Verifica hash da entrada
                calculated_hash = self._calculate_entry_hash(entry)
                if entry.hash_value != calculated_hash:
                    corrupted_entries += 1
                    violations.append({
                        'type': 'entry_hash_mismatch',
                        'entry_id': entry.entry_id,
                        'expected_hash': calculated_hash,
                        'actual_hash': entry.hash_value
                    })
                    continue
                
                verified_entries += 1
                previous_hash = entry.hash_value
            
            # Verifica se há entradas faltando
            if len(entries) < chain.entry_count:
                missing_entries += (chain.entry_count - len(entries))
                violations.append({
                    'type': 'missing_entries',
                    'expected_count': chain.entry_count,
                    'actual_count': len(entries)
                })
            
            # Calcula score de integridade
            total_entries = chain.entry_count
            integrity_score = (verified_entries / total_entries) * 100 if total_entries > 0 else 0
            
            # Gera recomendações
            recommendations = []
            if corrupted_entries > 0:
                recommendations.append("Investigar entradas corrompidas")
            if missing_entries > 0:
                recommendations.append("Recuperar entradas faltando")
            if integrity_score < 100:
                recommendations.append("Implementar medidas de segurança adicionais")
            
            report = IntegrityReport(
                report_id=f"INTEGRITY_{chain_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.utcnow(),
                chain_id=chain_id,
                total_entries=total_entries,
                verified_entries=verified_entries,
                corrupted_entries=corrupted_entries,
                missing_entries=missing_entries,
                integrity_score=integrity_score,
                violations=violations,
                recommendations=recommendations
            )
            
            logger.info(f"[HASH_TRAIL] Verificação de integridade concluída para {chain_id}")
            return report
            
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao verificar integridade da cadeia {chain_id}: {e}")
            raise
    
    def _get_chain(self, chain_id: str) -> Optional[AuditChain]:
        """Obtém cadeia do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT chain_id, start_timestamp, end_timestamp, entry_count,
                           root_hash, current_hash, is_complete, integrity_verified
                    FROM audit_chains
                    WHERE chain_id = ?
                """, (chain_id,))
                
                row = cursor.fetchone()
                if row:
                    return AuditChain(
                        chain_id=row[0],
                        start_timestamp=datetime.fromisoformat(row[1]),
                        end_timestamp=datetime.fromisoformat(row[2]) if row[2] else None,
                        entry_count=row[3],
                        root_hash=row[4],
                        current_hash=row[5],
                        is_complete=bool(row[6]),
                        integrity_verified=bool(row[7])
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao obter cadeia {chain_id}: {e}")
            return None
    
    def _get_chain_entries(self, chain_id: str) -> List[AuditEntry]:
        """Obtém todas as entradas de uma cadeia"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT entry_id, timestamp, level, category, user_id, session_id,
                           action, resource, details, ip_address, user_agent,
                           hash_value, previous_hash, chain_position
                    FROM audit_entries
                    WHERE chain_id = ?
                    ORDER BY chain_position
                """, (chain_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_audit_entry(row) for row in rows]
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao obter entradas da cadeia {chain_id}: {e}")
            return []
    
    def search_audit_entries(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           user_id: Optional[str] = None,
                           action: Optional[str] = None,
                           level: Optional[AuditLevel] = None,
                           category: Optional[AuditCategory] = None,
                           limit: int = 100) -> List[AuditEntry]:
        """
        Busca entradas de auditoria com filtros
        
        Args:
            start_date: Data inicial
            end_date: Data final
            user_id: ID do usuário
            action: Ação específica
            level: Nível de auditoria
            category: Categoria de auditoria
            limit: Limite de resultados
            
        Returns:
            Lista de entradas de auditoria
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT entry_id, timestamp, level, category, user_id, session_id,
                           action, resource, details, ip_address, user_agent,
                           hash_value, previous_hash, chain_position
                    FROM audit_entries
                    WHERE 1=1
                """
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if action:
                    query += " AND action = ?"
                    params.append(action)
                
                if level:
                    query += " AND level = ?"
                    params.append(level.value)
                
                if category:
                    query += " AND category = ?"
                    params.append(category.value)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_audit_entry(row) for row in rows]
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao buscar entradas: {e}")
            return []
    
    def get_audit_statistics(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas de auditoria
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Estatísticas de auditoria
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                where_clause = "WHERE 1=1"
                params = []
                
                if start_date:
                    where_clause += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    where_clause += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                # Total de entradas
                cursor.execute(f"SELECT COUNT(*) FROM audit_entries {where_clause}", params)
                total_entries = cursor.fetchone()[0]
                
                # Entradas por nível
                cursor.execute(f"""
                    SELECT level, COUNT(*) 
                    FROM audit_entries 
                    {where_clause}
                    GROUP BY level
                """, params)
                entries_by_level = dict(cursor.fetchall())
                
                # Entradas por categoria
                cursor.execute(f"""
                    SELECT category, COUNT(*) 
                    FROM audit_entries 
                    {where_clause}
                    GROUP BY category
                """, params)
                entries_by_category = dict(cursor.fetchall())
                
                # Entradas por usuário
                cursor.execute(f"""
                    SELECT user_id, COUNT(*) 
                    FROM audit_entries 
                    {where_clause} AND user_id IS NOT NULL
                    GROUP BY user_id
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                """, params)
                entries_by_user = dict(cursor.fetchall())
                
                # Ações mais comuns
                cursor.execute(f"""
                    SELECT action, COUNT(*) 
                    FROM audit_entries 
                    {where_clause}
                    GROUP BY action
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                """, params)
                entries_by_action = dict(cursor.fetchall())
                
                return {
                    'total_entries': total_entries,
                    'entries_by_level': entries_by_level,
                    'entries_by_category': entries_by_category,
                    'entries_by_user': entries_by_user,
                    'entries_by_action': entries_by_action,
                    'period': {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    }
                }
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao obter estatísticas: {e}")
            return {}
    
    def export_audit_trail(self, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          format: str = "json") -> Union[str, bytes]:
        """
        Exporta trilha de auditoria
        
        Args:
            start_date: Data inicial
            end_date: Data final
            format: Formato de exportação (json, csv)
            
        Returns:
            Dados exportados
        """
        try:
            entries = self.search_audit_entries(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Limite para exportação
            )
            
            if format.lower() == "json":
                export_data = {
                    'export_info': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'total_entries': len(entries),
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    },
                    'entries': [entry.to_dict() for entry in entries]
                }
                return json.dumps(export_data, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Cabeçalho
                writer.writerow([
                    'entry_id', 'timestamp', 'level', 'category', 'user_id',
                    'session_id', 'action', 'resource', 'ip_address',
                    'hash_value', 'chain_position'
                ])
                
                # Dados
                for entry in entries:
                    writer.writerow([
                        entry.entry_id,
                        entry.timestamp.isoformat(),
                        entry.level.value,
                        entry.category.value,
                        entry.user_id,
                        entry.session_id,
                        entry.action,
                        entry.resource,
                        entry.ip_address,
                        entry.hash_value,
                        entry.chain_position
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Formato não suportado: {format}")
                
        except Exception as e:
            logger.error(f"[HASH_TRAIL] Erro ao exportar trilha: {e}")
            raise


# Instância global
audit_trail = HashBasedAuditTrail()

# Funções de conveniência
def add_audit_entry(level: AuditLevel, category: AuditCategory, action: str, 
                   resource: str, details: Dict[str, Any], **kwargs) -> AuditEntry:
    """Função de conveniência para adicionar entrada"""
    return audit_trail.add_audit_entry(level, category, action, resource, details, **kwargs)

def get_audit_entry(entry_id: str) -> Optional[AuditEntry]:
    """Função de conveniência para obter entrada"""
    return audit_trail.get_audit_entry(entry_id)

def verify_chain_integrity(chain_id: str) -> IntegrityReport:
    """Função de conveniência para verificar integridade"""
    return audit_trail.verify_chain_integrity(chain_id)

def search_audit_entries(**kwargs) -> List[AuditEntry]:
    """Função de conveniência para buscar entradas"""
    return audit_trail.search_audit_entries(**kwargs) 