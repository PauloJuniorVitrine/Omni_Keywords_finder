#!/bin/bash

# 🔄 BACKUP AUTOMÁTICO - OMNİ KEYWORDS FINDER
# 📅 Criado: 2025-01-27
# 🔧 Tracing ID: CHECKLIST_99_PERCENT_20250127_001
# 🎯 Objetivo: Script de backup enterprise-grade

# =============================================================================
# 🚨 CONFIGURAÇÕES CRÍTICAS
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configurações do Sistema
SCRIPT_NAME="backup.sh"
SCRIPT_VERSION="1.0"
TRACING_ID="CHECKLIST_99_PERCENT_20250127_001"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DATE=$(date +"%Y-%m-%d")

# Configurações de Log
LOG_DIR="/var/log/omni_keywords_finder/backup"
LOG_FILE="${LOG_DIR}/backup_${BACKUP_DATE}.log"
ERROR_LOG="${LOG_DIR}/backup_errors_${BACKUP_DATE}.log"

# Configurações de Backup
BACKUP_DIR="/var/backups/omni_keywords_finder"
BACKUP_RETENTION_DAYS=30
BACKUP_COMPRESSION="gzip"
BACKUP_PARALLEL_JOBS=4

# Configurações do PostgreSQL
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="omni_keywords_production"
DB_USER="omni_user"
DB_PASSWORD="omni_secure_password_2025_ultra_encrypted"
DB_SSL_MODE="require"

# Configurações de Criptografia
ENCRYPTION_KEY_FILE="/etc/ssl/private/backup_encryption.key"
ENCRYPTION_ALGORITHM="aes-256-gcm"

# Configurações de Notificação
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
EMAIL_RECIPIENTS="admin@omni-keywords-finder.com,dba@omni-keywords-finder.com"

# =============================================================================
# 🔧 FUNÇÕES AUXILIARES
# =============================================================================

# Função de logging
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] [${level}] [${TRACING_ID}] ${message}" | tee -a "${LOG_FILE}"
}

# Função de logging de erro
log_error() {
    local message="$1"
    log "ERROR" "${message}" | tee -a "${ERROR_LOG}"
}

# Função de logging de sucesso
log_success() {
    local message="$1"
    log "SUCCESS" "${message}"
}

# Função de logging de informação
log_info() {
    local message="$1"
    log "INFO" "${message}"
}

# Função de logging de warning
log_warning() {
    local message="$1"
    log "WARNING" "${message}"
}

# Função para verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    local dependencies=("pg_dump" "gzip" "openssl" "curl" "mail")
    
    for dep in "${dependencies[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Dependência não encontrada: ${dep}"
            exit 1
        fi
    done
    
    log_success "Todas as dependências estão disponíveis"
}

# Função para criar diretórios necessários
create_directories() {
    log_info "Criando diretórios necessários..."
    
    mkdir -p "${LOG_DIR}"
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${BACKUP_DIR}/full"
    mkdir -p "${BACKUP_DIR}/incremental"
    mkdir -p "${BACKUP_DIR}/wal"
    mkdir -p "${BACKUP_DIR}/temp"
    
    log_success "Diretórios criados com sucesso"
}

# Função para verificar conectividade com o banco
check_database_connectivity() {
    log_info "Verificando conectividade com o banco de dados..."
    
    export PGPASSWORD="${DB_PASSWORD}"
    
    if ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" > /dev/null 2>&1; then
        log_error "Não foi possível conectar ao PostgreSQL"
        return 1
    fi
    
    log_success "Conectividade com o banco verificada"
}

# Função para gerar nome do arquivo de backup
generate_backup_filename() {
    local backup_type="$1"
    local extension="sql"
    
    if [[ "${BACKUP_COMPRESSION}" == "gzip" ]]; then
        extension="sql.gz"
    elif [[ "${BACKUP_COMPRESSION}" == "bzip2" ]]; then
        extension="sql.bz2"
    fi
    
    echo "${BACKUP_DIR}/${backup_type}/backup_${backup_type}_${TIMESTAMP}.${extension}"
}

# Função para criptografar arquivo
encrypt_file() {
    local input_file="$1"
    local output_file="${input_file}.enc"
    
    log_info "Criptografando arquivo: ${input_file}"
    
    if ! openssl enc -"${ENCRYPTION_ALGORITHM}" -kfile "${ENCRYPTION_KEY_FILE}" -in "${input_file}" -out "${output_file}"; then
        log_error "Falha na criptografia do arquivo: ${input_file}"
        return 1
    fi
    
    # Remover arquivo original não criptografado
    rm -f "${input_file}"
    
    log_success "Arquivo criptografado: ${output_file}"
}

# Função para verificar integridade do backup
verify_backup_integrity() {
    local backup_file="$1"
    
    log_info "Verificando integridade do backup: ${backup_file}"
    
    # Verificar se o arquivo existe e tem tamanho > 0
    if [[ ! -f "${backup_file}" ]] || [[ ! -s "${backup_file}" ]]; then
        log_error "Arquivo de backup inválido ou vazio: ${backup_file}"
        return 1
    fi
    
    # Verificar checksum
    local checksum_file="${backup_file}.sha256"
    if [[ -f "${checksum_file}" ]]; then
        if ! sha256sum -c "${checksum_file}"; then
            log_error "Checksum do backup falhou: ${backup_file}"
            return 1
        fi
    fi
    
    log_success "Integridade do backup verificada: ${backup_file}"
}

# Função para limpar backups antigos
cleanup_old_backups() {
    log_info "Limpando backups antigos (mais de ${BACKUP_RETENTION_DAYS} dias)..."
    
    local deleted_count=0
    
    # Limpar backups completos
    while IFS= read -r -d '' file; do
        rm -f "$file"
        rm -f "${file}.sha256"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}/full" -name "backup_full_*.sql*" -mtime +${BACKUP_RETENTION_DAYS} -print0)
    
    # Limpar backups incrementais
    while IFS= read -r -d '' file; do
        rm -f "$file"
        rm -f "${file}.sha256"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}/incremental" -name "backup_incremental_*.sql*" -mtime +${BACKUP_RETENTION_DAYS} -print0)
    
    # Limpar WAL logs antigos
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}/wal" -name "*.wal" -mtime +7 -print0)
    
    log_success "Limpeza concluída. ${deleted_count} arquivos removidos"
}

# Função para enviar notificação
send_notification() {
    local status="$1"
    local message="$2"
    
    log_info "Enviando notificação: ${status}"
    
    # Notificação via Slack
    if [[ -n "${SLACK_WEBHOOK_URL}" ]]; then
        local slack_payload="{\"text\":\"🔄 Backup Omni Keywords Finder - ${status}\n${message}\n📅 Data: ${BACKUP_DATE}\n🔧 Tracing ID: ${TRACING_ID}\"}"
        
        if ! curl -X POST -H "Content-type: application/json" --data "${slack_payload}" "${SLACK_WEBHOOK_URL}" > /dev/null 2>&1; then
            log_warning "Falha ao enviar notificação Slack"
        fi
    fi
    
    # Notificação via email
    if [[ -n "${EMAIL_RECIPIENTS}" ]]; then
        local email_subject="[BACKUP] Omni Keywords Finder - ${status}"
        local email_body="Status: ${status}\nMensagem: ${message}\nData: ${BACKUP_DATE}\nTracing ID: ${TRACING_ID}\nLog: ${LOG_FILE}"
        
        if ! echo -e "${email_body}" | mail -s "${email_subject}" "${EMAIL_RECIPIENTS}"; then
            log_warning "Falha ao enviar notificação email"
        fi
    fi
    
    log_success "Notificação enviada"
}

# Função para backup completo
perform_full_backup() {
    log_info "Iniciando backup completo..."
    
    local backup_file=$(generate_backup_filename "full")
    local temp_file="${BACKUP_DIR}/temp/backup_full_${TIMESTAMP}.sql"
    
    # Configurar variáveis de ambiente
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Executar pg_dump
    log_info "Executando pg_dump..."
    
    if ! pg_dump \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --verbose \
        --clean \
        --create \
        --if-exists \
        --no-owner \
        --no-privileges \
        --format=plain \
        --file="${temp_file}" \
        --jobs="${BACKUP_PARALLEL_JOBS}" \
        --compress=0; then
        
        log_error "Falha no pg_dump"
        return 1
    fi
    
    # Comprimir backup
    if [[ "${BACKUP_COMPRESSION}" == "gzip" ]]; then
        log_info "Comprimindo backup com gzip..."
        if ! gzip -9 "${temp_file}"; then
            log_error "Falha na compressão gzip"
            return 1
        fi
        mv "${temp_file}.gz" "${backup_file}"
    elif [[ "${BACKUP_COMPRESSION}" == "bzip2" ]]; then
        log_info "Comprimindo backup com bzip2..."
        if ! bzip2 -9 "${temp_file}"; then
            log_error "Falha na compressão bzip2"
            return 1
        fi
        mv "${temp_file}.bz2" "${backup_file}"
    else
        mv "${temp_file}" "${backup_file}"
    fi
    
    # Gerar checksum
    log_info "Gerando checksum..."
    sha256sum "${backup_file}" > "${backup_file}.sha256"
    
    # Criptografar backup
    if [[ -f "${ENCRYPTION_KEY_FILE}" ]]; then
        encrypt_file "${backup_file}"
        backup_file="${backup_file}.enc"
    fi
    
    # Verificar integridade
    verify_backup_integrity "${backup_file}"
    
    log_success "Backup completo concluído: ${backup_file}"
    echo "${backup_file}"
}

# Função para backup incremental (WAL)
perform_incremental_backup() {
    log_info "Iniciando backup incremental (WAL)..."
    
    local wal_dir="/var/lib/postgresql/15/archive"
    local backup_files=()
    
    # Encontrar arquivos WAL não processados
    while IFS= read -r -d '' file; do
        local filename=$(basename "$file")
        local backup_file="${BACKUP_DIR}/wal/${filename}"
        
        # Copiar arquivo WAL
        if cp "$file" "${backup_file}"; then
            backup_files+=("${backup_file}")
            log_info "WAL copiado: ${filename}"
        else
            log_error "Falha ao copiar WAL: ${filename}"
        fi
    done < <(find "${wal_dir}" -name "*.wal" -mtime -1 -print0)
    
    if [[ ${#backup_files[@]} -eq 0 ]]; then
        log_warning "Nenhum arquivo WAL encontrado para backup"
        return 0
    fi
    
    log_success "Backup incremental concluído. ${#backup_files[@]} arquivos WAL processados"
    printf '%s\n' "${backup_files[@]}"
}

# Função para testar restore
test_restore() {
    local backup_file="$1"
    local test_db="test_restore_${TIMESTAMP}"
    
    log_info "Testando restore do backup: ${backup_file}"
    
    # Configurar variáveis de ambiente
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Criar banco de teste
    if ! createdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${test_db}"; then
        log_error "Falha ao criar banco de teste: ${test_db}"
        return 1
    fi
    
    # Descriptografar se necessário
    local restore_file="${backup_file}"
    if [[ "${backup_file}" == *.enc ]]; then
        restore_file="${BACKUP_DIR}/temp/restore_test_${TIMESTAMP}.sql"
        if ! openssl enc -"${ENCRYPTION_ALGORITHM}" -kfile "${ENCRYPTION_KEY_FILE}" -d -in "${backup_file}" -out "${restore_file}"; then
            log_error "Falha ao descriptografar backup para teste"
            dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${test_db}" 2>/dev/null || true
            return 1
        fi
    fi
    
    # Executar restore
    if ! psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${test_db}" -f "${restore_file}" > /dev/null 2>&1; then
        log_error "Falha no restore de teste"
        dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${test_db}" 2>/dev/null || true
        rm -f "${restore_file}"
        return 1
    fi
    
    # Limpar arquivo temporário
    rm -f "${restore_file}"
    
    # Remover banco de teste
    dropdb -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" "${test_db}" 2>/dev/null || true
    
    log_success "Teste de restore concluído com sucesso"
}

# Função principal
main() {
    local start_time=$(date +%s)
    local backup_type="${1:-full}"
    local test_restore_flag="${2:-false}"
    
    log_info "=== INÍCIO DO BACKUP ==="
    log_info "Tipo: ${backup_type}"
    log_info "Teste de restore: ${test_restore_flag}"
    log_info "Tracing ID: ${TRACING_ID}"
    
    # Verificações iniciais
    check_dependencies
    create_directories
    check_database_connectivity
    
    # Executar backup
    local backup_files=()
    if [[ "${backup_type}" == "full" ]]; then
        backup_files+=("$(perform_full_backup)")
    elif [[ "${backup_type}" == "incremental" ]]; then
        mapfile -t incremental_files < <(perform_incremental_backup)
        backup_files+=("${incremental_files[@]}")
    else
        log_error "Tipo de backup inválido: ${backup_type}"
        exit 1
    fi
    
    # Testar restore se solicitado
    if [[ "${test_restore_flag}" == "true" ]] && [[ "${backup_type}" == "full" ]]; then
        test_restore "${backup_files[0]}"
    fi
    
    # Limpeza
    cleanup_old_backups
    
    # Calcular tempo total
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Relatório final
    local report="Backup ${backup_type} concluído com sucesso\n"
    report+="Arquivos: ${#backup_files[@]}\n"
    report+="Duração: ${duration} segundos\n"
    report+="Tamanho total: $(du -sh "${backup_files[@]}" 2>/dev/null | awk '{sum+=$1} END {print sum "B"}')"
    
    log_success "=== BACKUP CONCLUÍDO ==="
    log_info "${report}"
    
    # Enviar notificação de sucesso
    send_notification "SUCCESS" "${report}"
    
    exit 0
}

# Função de tratamento de erro
error_handler() {
    local exit_code=$?
    local error_line=$1
    
    log_error "Erro na linha ${error_line} (código: ${exit_code})"
    
    # Enviar notificação de erro
    local error_report="Backup falhou\n"
    error_report+="Linha: ${error_line}\n"
    error_report+="Código: ${exit_code}\n"
    error_report+="Log: ${LOG_FILE}"
    
    send_notification "FAILED" "${error_report}"
    
    exit "${exit_code}"
}

# =============================================================================
# 🚀 EXECUÇÃO PRINCIPAL
# =============================================================================

# Configurar trap para tratamento de erro
trap 'error_handler ${LINENO}' ERR

# Verificar argumentos
if [[ $# -eq 0 ]]; then
    echo "Uso: $0 [full|incremental] [test_restore]"
    echo "  full: Backup completo do banco"
    echo "  incremental: Backup incremental (WAL)"
    echo "  test_restore: true/false para testar restore (apenas backup completo)"
    exit 1
fi

# Executar função principal
main "$@" 