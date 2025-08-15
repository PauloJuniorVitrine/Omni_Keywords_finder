# 🔐 **DOCUMENTAÇÃO DO PROCESSO DE CRIPTOGRAFIA**

## 📋 **VISÃO GERAL**

Este documento descreve o processo de criptografia implementado no sistema de credenciais do Omni Keywords Finder, garantindo a segurança e integridade dos dados sensíveis.

---

## 🎯 **OBJETIVOS DE SEGURANÇA**

### **Princípios Fundamentais**
- **Confidencialidade**: Dados sensíveis nunca são armazenados em texto plano
- **Integridade**: Detecção de qualquer modificação não autorizada
- **Disponibilidade**: Acesso seguro aos dados quando necessário
- **Auditoria**: Rastreabilidade completa de operações criptográficas

### **Padrões de Compliance**
- **OWASP Cryptographic Storage**: Seguindo as melhores práticas
- **NIST SP 800-38A**: Padrões de criptografia do governo americano
- **PCI-DSS 3.4**: Proteção de dados de cartão de crédito
- **GDPR Article 32**: Proteção de dados pessoais

---

## 🔧 **ARQUITETURA DE CRIPTOGRAFIA**

### **Componentes Principais**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Master Key    │    │ Encryption       │    │ Encrypted Data  │
│   (Environment) │───▶│ Service          │───▶│ (Database/File) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Audit Service    │
                       │ (Logging)        │
                       └──────────────────┘
```

### **Fluxo de Criptografia**

1. **Entrada**: Credencial em texto plano
2. **Validação**: Verificação de formato e integridade
3. **Criptografia**: Conversão usando AES-256
4. **Armazenamento**: Dados criptografados + metadados
5. **Auditoria**: Log de operação criptográfica

---

## 🔑 **GERENCIAMENTO DE CHAVES**

### **Master Key**

#### **Configuração**
```bash
# Variável de ambiente obrigatória
CREDENTIAL_MASTER_KEY=your-256-bit-master-key-here
```

#### **Geração Segura**
```python
import secrets
import base64

# Gerar chave mestra de 256 bits (32 bytes)
master_key = secrets.token_bytes(32)
encoded_key = base64.b64encode(master_key).decode('utf-8')
print(f"CREDENTIAL_MASTER_KEY={encoded_key}")
```

#### **Validação da Chave**
- **Comprimento**: Exatamente 32 bytes (256 bits)
- **Entropia**: Mínimo 256 bits de entropia
- **Formato**: Base64 encoded
- **Armazenamento**: Apenas em variáveis de ambiente

### **Rotação de Chaves**

#### **Ciclo de Rotação**
- **Frequência**: A cada 90 dias
- **Processo**: Automático com notificação
- **Backup**: Chave anterior mantida por 30 dias
- **Migração**: Re-criptografia automática de dados

#### **Processo de Rotação**
```python
# 1. Gerar nova chave
new_master_key = generate_new_master_key()

# 2. Re-criptografar dados existentes
for credential in all_credentials:
    decrypted = decrypt_with_old_key(credential.encrypted_data)
    re_encrypted = encrypt_with_new_key(decrypted)
    credential.encrypted_data = re_encrypted

# 3. Atualizar variável de ambiente
update_environment_variable(new_master_key)

# 4. Invalidar chave antiga
invalidate_old_key()
```

---

## 🔐 **ALGORITMO DE CRIPTOGRAFIA**

### **AES-256-GCM**

#### **Especificações Técnicas**
- **Algoritmo**: AES (Advanced Encryption Standard)
- **Tamanho da Chave**: 256 bits
- **Modo de Operação**: GCM (Galois/Counter Mode)
- **Tamanho do IV**: 12 bytes (96 bits)
- **Tamanho da Tag**: 16 bytes (128 bits)

#### **Vantagens do AES-256-GCM**
- **Autenticação**: Garante integridade dos dados
- **Performance**: Otimizado para hardware moderno
- **Padrão**: Amplamente aceito e auditado
- **Segurança**: Resistente a ataques conhecidos

### **Implementação**

#### **Criptografia**
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os

def encrypt_credential(plaintext: str, master_key: bytes) -> str:
    """
    Criptografa uma credencial usando AES-256-GCM.
    
    Args:
        plaintext: Credencial em texto plano
        master_key: Chave mestra de 256 bits
        
    Returns:
        String base64 com dados criptografados
    """
    # Gerar IV único
    iv = os.urandom(12)
    
    # Criar instância AES-GCM
    aesgcm = AESGCM(master_key)
    
    # Criptografar dados
    ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
    
    # Combinar IV + ciphertext + tag
    encrypted_data = iv + ciphertext
    
    # Retornar em base64
    return base64.b64encode(encrypted_data).decode('utf-8')
```

#### **Descriptografia**
```python
def decrypt_credential(encrypted_data: str, master_key: bytes) -> str:
    """
    Descriptografa uma credencial usando AES-256-GCM.
    
    Args:
        encrypted_data: Dados criptografados em base64
        master_key: Chave mestra de 256 bits
        
    Returns:
        Credencial em texto plano
        
    Raises:
        ValueError: Se dados são inválidos ou corrompidos
    """
    try:
        # Decodificar base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Separar IV e ciphertext
        iv = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        
        # Criar instância AES-GCM
        aesgcm = AESGCM(master_key)
        
        # Descriptografar dados
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
        
        return plaintext.decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Falha na descriptografia: {str(e)}")
```

---

## 📊 **FORMATO DOS DADOS CRIPTOGRAFADOS**

### **Estrutura dos Dados**

```
┌─────────────┬─────────────────────┬─────────────────┐
│     IV      │    Ciphertext       │      Tag        │
│   (12B)     │     (Variable)      │     (16B)       │
└─────────────┴─────────────────────┴─────────────────┘
```

### **Exemplo de Dados Criptografados**

```json
{
  "encrypted_api_key": "AES256_GCM:eyJpdiI6IjEyMzQ1Njc4OTBhYmNkZWYiLCJkYXRhIjoiY2lwaGVydGV4dCJ9",
  "encryption_metadata": {
    "algorithm": "AES-256-GCM",
    "version": "1.0",
    "created_at": "2025-01-27T10:30:00Z",
    "key_id": "master_key_v1"
  }
}
```

### **Metadados de Criptografia**

```python
class EncryptionMetadata:
    """Metadados de criptografia para auditoria."""
    
    def __init__(self):
        self.algorithm = "AES-256-GCM"
        self.version = "1.0"
        self.created_at = datetime.utcnow().isoformat()
        self.key_id = "master_key_v1"
        self.iv_size = 12
        self.tag_size = 16
        self.key_size = 256
```

---

## 🔍 **VALIDAÇÃO E INTEGRIDADE**

### **Validação de Entrada**

#### **Verificação de Formato**
```python
def validate_credential_format(credential: str, provider: str) -> bool:
    """
    Valida formato da credencial antes da criptografia.
    
    Args:
        credential: Credencial em texto plano
        provider: Nome do provedor
        
    Returns:
        True se formato é válido
    """
    validators = {
        'openai': lambda x: x.startswith('sk-') and len(x) >= 20,
        'deepseek': lambda x: x.startswith('sk-') and len(x) >= 20,
        'claude': lambda x: x.startswith('sk-ant-') and len(x) >= 25,
        'gemini': lambda x: len(x) >= 20 and 'AIza' in x,
        'instagram': lambda x: len(x) >= 3,  # username
        'tiktok': lambda x: len(x) >= 20,
        'youtube': lambda x: len(x) >= 20,
        'stripe': lambda x: x.startswith('sk_') and len(x) >= 20,
        'paypal': lambda x: len(x) >= 20,
        'slack': lambda x: x.startswith('https://hooks.slack.com/'),
        'discord': lambda x: len(x) >= 50,
        'telegram': lambda x: len(x) >= 40
    }
    
    validator = validators.get(provider)
    if not validator:
        return True  # Provedor desconhecido, aceitar
    
    return validator(credential)
```

#### **Verificação de Integridade**
```python
def verify_encrypted_data_integrity(encrypted_data: str) -> bool:
    """
    Verifica integridade dos dados criptografados.
    
    Args:
        encrypted_data: Dados criptografados
        
    Returns:
        True se dados são válidos
    """
    try:
        # Decodificar base64
        data = base64.b64decode(encrypted_data)
        
        # Verificar tamanho mínimo
        if len(data) < 28:  # IV(12) + Tag(16)
            return False
        
        # Verificar formato
        if not data.startswith(b'AES256_GCM:'):
            return False
        
        return True
        
    except Exception:
        return False
```

---

## 📝 **AUDITORIA E LOGGING**

### **Eventos de Auditoria**

#### **Tipos de Eventos**
```python
class EncryptionEventType:
    """Tipos de eventos de criptografia."""
    
    ENCRYPTION_STARTED = "encryption_started"
    ENCRYPTION_COMPLETED = "encryption_completed"
    ENCRYPTION_FAILED = "encryption_failed"
    DECRYPTION_STARTED = "decryption_started"
    DECRYPTION_COMPLETED = "decryption_completed"
    DECRYPTION_FAILED = "decryption_failed"
    KEY_ROTATION_STARTED = "key_rotation_started"
    KEY_ROTATION_COMPLETED = "key_rotation_completed"
    KEY_ROTATION_FAILED = "key_rotation_failed"
    INTEGRITY_CHECK_PASSED = "integrity_check_passed"
    INTEGRITY_CHECK_FAILED = "integrity_check_failed"
```

#### **Estrutura do Log**
```python
def log_encryption_event(
    event_type: str,
    provider: str,
    user_id: str,
    success: bool,
    details: dict = None
):
    """
    Registra evento de criptografia para auditoria.
    
    Args:
        event_type: Tipo do evento
        provider: Nome do provedor
        user_id: ID do usuário
        success: Se operação foi bem-sucedida
        details: Detalhes adicionais
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "provider": provider,
        "user_id": user_id,
        "success": success,
        "ip_address": get_client_ip(),
        "user_agent": get_user_agent(),
        "details": details or {}
    }
    
    # Salvar em arquivo de auditoria
    audit_logger.info(json.dumps(log_entry))
    
    # Alertar se falha crítica
    if not success and event_type in CRITICAL_EVENTS:
        send_security_alert(log_entry)
```

### **Métricas de Criptografia**

#### **Coleta de Métricas**
```python
class EncryptionMetrics:
    """Métricas de performance e segurança."""
    
    def __init__(self):
        self.total_encryptions = 0
        self.total_decryptions = 0
        self.encryption_failures = 0
        self.decryption_failures = 0
        self.avg_encryption_time = 0.0
        self.avg_decryption_time = 0.0
        self.last_key_rotation = None
        self.integrity_check_failures = 0
    
    def record_encryption(self, duration: float, success: bool):
        """Registra métrica de criptografia."""
        self.total_encryptions += 1
        if not success:
            self.encryption_failures += 1
        
        # Atualizar tempo médio
        self.avg_encryption_time = (
            (self.avg_encryption_time * (self.total_encryptions - 1) + duration) /
            self.total_encryptions
        )
    
    def get_metrics_report(self) -> dict:
        """Gera relatório de métricas."""
        return {
            "total_encryptions": self.total_encryptions,
            "total_decryptions": self.total_decryptions,
            "encryption_success_rate": (
                (self.total_encryptions - self.encryption_failures) /
                self.total_encryptions * 100
            ),
            "decryption_success_rate": (
                (self.total_decryptions - self.decryption_failures) /
                self.total_decryptions * 100
            ),
            "avg_encryption_time_ms": self.avg_encryption_time * 1000,
            "avg_decryption_time_ms": self.avg_decryption_time * 1000,
            "last_key_rotation": self.last_key_rotation,
            "integrity_check_failures": self.integrity_check_failures
        }
```

---

## 🛡️ **MEDIDAS DE SEGURANÇA**

### **Proteção Contra Ataques**

#### **Timing Attacks**
- **Problema**: Ataques baseados em tempo de resposta
- **Solução**: Tempo constante para operações criptográficas
- **Implementação**: Uso de `secrets.compare_digest()`

#### **Side-Channel Attacks**
- **Problema**: Vazamento de informação através de canais laterais
- **Solução**: Limpeza de memória após operações
- **Implementação**: Zeroização automática de buffers

#### **Brute Force Attacks**
- **Problema**: Tentativas de adivinhar a chave
- **Solução**: Rate limiting e bloqueio temporário
- **Implementação**: 5 tentativas por minuto, bloqueio de 1 hora

### **Segurança da Chave Mestra**

#### **Armazenamento Seguro**
```python
def get_master_key() -> bytes:
    """
    Obtém chave mestra de forma segura.
    
    Returns:
        Chave mestra em bytes
        
    Raises:
        SecurityError: Se chave não está configurada corretamente
    """
    master_key = os.getenv('CREDENTIAL_MASTER_KEY')
    
    if not master_key:
        raise SecurityError("CREDENTIAL_MASTER_KEY não configurada")
    
    try:
        # Decodificar base64
        key_bytes = base64.b64decode(master_key)
        
        # Verificar tamanho
        if len(key_bytes) != 32:
            raise SecurityError("Chave mestra deve ter 256 bits (32 bytes)")
        
        return key_bytes
        
    except Exception as e:
        raise SecurityError(f"Chave mestra inválida: {str(e)}")
```

#### **Validação de Entropia**
```python
def validate_key_entropy(key_bytes: bytes) -> bool:
    """
    Valida entropia da chave mestra.
    
    Args:
        key_bytes: Chave em bytes
        
    Returns:
        True se entropia é adequada
    """
    # Calcular entropia de Shannon
    byte_counts = [0] * 256
    for byte in key_bytes:
        byte_counts[byte] += 1
    
    entropy = 0
    for count in byte_counts:
        if count > 0:
            probability = count / len(key_bytes)
            entropy -= probability * math.log2(probability)
    
    # Mínimo 7.5 bits de entropia por byte (240 bits total)
    return entropy >= 7.5
```

---

## 🔄 **RECUPERAÇÃO E BACKUP**

### **Estratégia de Backup**

#### **Backup Automático**
- **Frequência**: A cada alteração de credencial
- **Localização**: Sistema de arquivos seguro
- **Retenção**: 30 dias
- **Criptografia**: Backup também criptografado

#### **Backup Manual**
```python
def create_encrypted_backup() -> str:
    """
    Cria backup criptografado das credenciais.
    
    Returns:
        Caminho do arquivo de backup
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup/credentials_{timestamp}.enc"
    
    # Obter todas as credenciais
    credentials = get_all_credentials()
    
    # Criptografar backup
    backup_data = {
        "timestamp": timestamp,
        "credentials": credentials,
        "metadata": get_encryption_metadata()
    }
    
    # Salvar backup criptografado
    encrypted_backup = encrypt_data(json.dumps(backup_data))
    
    with open(backup_file, 'w') as f:
        f.write(encrypted_backup)
    
    return backup_file
```

### **Processo de Recuperação**

#### **Validação de Backup**
```python
def validate_backup(backup_file: str) -> bool:
    """
    Valida integridade de um backup.
    
    Args:
        backup_file: Caminho do arquivo de backup
        
    Returns:
        True se backup é válido
    """
    try:
        with open(backup_file, 'r') as f:
            encrypted_data = f.read()
        
        # Descriptografar backup
        decrypted_data = decrypt_data(encrypted_data)
        backup_info = json.loads(decrypted_data)
        
        # Verificar estrutura
        required_fields = ['timestamp', 'credentials', 'metadata']
        if not all(field in backup_info for field in required_fields):
            return False
        
        # Verificar timestamp
        backup_time = datetime.fromisoformat(backup_info['timestamp'])
        if backup_time < datetime.now() - timedelta(days=30):
            return False
        
        return True
        
    except Exception:
        return False
```

#### **Restauração de Backup**
```python
def restore_from_backup(backup_file: str, user_id: str) -> bool:
    """
    Restaura credenciais de um backup.
    
    Args:
        backup_file: Caminho do arquivo de backup
        user_id: ID do usuário autorizado
        
    Returns:
        True se restauração foi bem-sucedida
    """
    try:
        # Validar backup
        if not validate_backup(backup_file):
            raise ValueError("Backup inválido")
        
        # Verificar permissões
        if not has_restore_permission(user_id):
            raise PermissionError("Usuário sem permissão para restauração")
        
        # Ler e descriptografar backup
        with open(backup_file, 'r') as f:
            encrypted_data = f.read()
        
        decrypted_data = decrypt_data(encrypted_data)
        backup_info = json.loads(decrypted_data)
        
        # Restaurar credenciais
        for provider, credential in backup_info['credentials'].items():
            restore_credential(provider, credential)
        
        # Log da restauração
        log_encryption_event(
            "backup_restored",
            "system",
            user_id,
            True,
            {"backup_file": backup_file}
        )
        
        return True
        
    except Exception as e:
        log_encryption_event(
            "backup_restore_failed",
            "system",
            user_id,
            False,
            {"error": str(e), "backup_file": backup_file}
        )
        return False
```

---

## 📊 **MONITORAMENTO E ALERTAS**

### **Métricas de Segurança**

#### **Indicadores de Performance**
- **Tempo de Criptografia**: <10ms por operação
- **Tempo de Descriptografia**: <5ms por operação
- **Taxa de Sucesso**: >99.9%
- **Uso de Memória**: <1MB por operação

#### **Indicadores de Segurança**
- **Falhas de Integridade**: 0 por dia
- **Tentativas de Acesso Não Autorizado**: <5 por hora
- **Falhas de Criptografia**: <0.1%
- **Rotação de Chaves**: A cada 90 dias

### **Sistema de Alertas**

#### **Alertas Críticos**
```python
CRITICAL_ALERTS = {
    "encryption_failure_rate": {
        "threshold": 1.0,  # 1% de falhas
        "action": "immediate_notification"
    },
    "integrity_check_failure": {
        "threshold": 1,  # Qualquer falha
        "action": "immediate_notification"
    },
    "key_rotation_overdue": {
        "threshold": 95,  # 95 dias
        "action": "daily_reminder"
    },
    "unauthorized_access_attempt": {
        "threshold": 10,  # 10 tentativas
        "action": "immediate_block"
    }
}
```

#### **Canais de Notificação**
- **Email**: Para alertas críticos
- **Slack**: Para alertas de segurança
- **SMS**: Para emergências
- **Dashboard**: Para monitoramento em tempo real

---

## 🔧 **CONFIGURAÇÃO E DEPLOYMENT**

### **Variáveis de Ambiente**

#### **Obrigatórias**
```bash
# Chave mestra para criptografia (256 bits em base64)
CREDENTIAL_MASTER_KEY=your-256-bit-master-key-here

# Configurações de segurança
CREDENTIAL_ENCRYPTION_ALGORITHM=AES-256-GCM
CREDENTIAL_KEY_ROTATION_DAYS=90
CREDENTIAL_BACKUP_RETENTION_DAYS=30
```

#### **Opcionais**
```bash
# Configurações de performance
CREDENTIAL_ENCRYPTION_TIMEOUT_MS=1000
CREDENTIAL_DECRYPTION_TIMEOUT_MS=500

# Configurações de auditoria
CREDENTIAL_AUDIT_LOG_LEVEL=INFO
CREDENTIAL_AUDIT_LOG_FILE=/var/log/credential_audit.log

# Configurações de backup
CREDENTIAL_BACKUP_DIR=/var/backups/credentials
CREDENTIAL_BACKUP_ENCRYPTION=true
```

### **Configuração de Produção**

#### **Checklist de Segurança**
- [ ] Chave mestra gerada com alta entropia
- [ ] Variáveis de ambiente configuradas
- [ ] Permissões de arquivo restritas
- [ ] Logs de auditoria habilitados
- [ ] Backup automático configurado
- [ ] Monitoramento de alertas ativo
- [ ] Rotação de chaves agendada
- [ ] Testes de recuperação realizados

#### **Comandos de Verificação**
```bash
# Verificar configuração
python -c "from app.services.credential_encryption import CredentialEncryptionService; print('Configuração OK')"

# Testar criptografia
python -c "from app.services.credential_encryption import test_encryption; test_encryption()"

# Verificar logs
tail -f /var/log/credential_audit.log

# Verificar métricas
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/credentials/metrics
```

---

## 📚 **REFERÊNCIAS TÉCNICAS**

### **Padrões e Especificações**
- **AES**: FIPS 197 (Advanced Encryption Standard)
- **GCM**: NIST SP 800-38D (Galois/Counter Mode)
- **Base64**: RFC 4648 (The Base16, Base32, and Base64 Data Encodings)
- **OWASP**: Cryptographic Storage Cheat Sheet

### **Bibliotecas Utilizadas**
- **cryptography**: Biblioteca Python para criptografia
- **secrets**: Geração segura de números aleatórios
- **base64**: Codificação/decodificação base64
- **json**: Serialização de dados

### **Recursos Adicionais**
- **NIST Cybersecurity Framework**: Estrutura de segurança
- **OWASP Top 10**: Principais vulnerabilidades web
- **PCI-DSS**: Padrão de segurança de dados
- **GDPR**: Regulamento de proteção de dados

---

## 📞 **SUPORTE TÉCNICO**

### **Contatos para Questões de Criptografia**
- **Email**: security@omnikeywordsfinder.com
- **Slack**: #security-encryption
- **Documentação**: https://docs.omnikeywordsfinder.com/security

### **Procedimentos de Emergência**
1. **Comprometimento de Chave**: Rotação imediata
2. **Falha de Criptografia**: Fallback para backup
3. **Perda de Dados**: Restauração de backup
4. **Ataque Detectado**: Isolamento e análise

---

**Última atualização**: 2025-01-27
**Versão da documentação**: 1.0
**Autor**: Paulo Júnior
**Revisão de Segurança**: Aprovada pelo CISO 