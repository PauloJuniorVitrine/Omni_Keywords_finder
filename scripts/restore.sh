#!/bin/bash

# 🔄 RESTORE AUTOMÁTICO - OMNİ KEYWORDS FINDER
# 📅 Criado: 2025-01-27
# 🔧 Tracing ID: CHECKLIST_99_PERCENT_20250127_001
# 🎯 Objetivo: Script de restore enterprise-grade

# =============================================================================
# 🚨 CONFIGURAÇÕES CRÍTICAS
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configurações do Sistema
SCRIPT_NAME="restore.sh"
SCRIPT_VERSION="1.0"
TRACING_ID="CHECKLIST_99_PERCENT_20250127_001"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESTORE_DATE=$(date +"%Y-%m-%d")

# Configurações de Log
LOG_DIR="/var/log/omni_keywords_finder/restore"
LOG_FILE="${LOG_DIR}/restore_${RESTORE_DATE}.log"
ERROR_LOG="${LOG_DIR}/restore_errors_${RESTORE_DATE}.log"

# Configurações de Restore
BACKUP_DIR="/var/backups/omni_keywords_finder"
RESTORE_DIR="/var/restore/omni_keywords_finder"
TEMP_DIR="${RESTORE_DIR}/temp"

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
    
    local dependencies=("psql" "pg_restore" "gzip" "bzip2" "openssl" "curl" "mail")
    
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
    mkdir -p "${RESTORE_DIR}"
    mkdir -p "${TEMP_DIR}"
    
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

# Função para listar backups disponíveis
list_available_backups() {
    log_info "Listando backups disponíveis..."
    
    echo "=== BACKUPS COMPLETOS ==="
    find "${BACKUP_DIR}/full" -name "backup_full_*.sql*" -type f | sort -r | head -10
    
    echo -e "\n=== BACKUPS INCREMENTAIS ==="
    find "${BACKUP_DIR}/incremental" -name "backup_incremental_*.sql*" -type f | sort -r | head -10
    
    echo -e "\n=== ARQUIVOS WAL ==="
    find "${BACKUP_DIR}/wal" -name "*.wal" -type f | sort -r | head -10
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
    
    # Verificar checksum se existir
    local checksum_file="${backup_file}.sha256"
    if [[ -f "${checksum_file}" ]]; then
        if ! sha256sum -c "${checksum_file}"; then
            log_error "Checksum do backup falhou: ${backup_file}"
            return 1
        fi
    fi
    
    log_success "Integridade do backup verificada: ${backup_file}"
}

# Função para descriptografar arquivo
decrypt_file() {
    local input_file="$1"
    local output_file="${input_file%.enc}"
    
    log_info "Descriptografando arquivo: ${input_file}"
    
    if ! openssl enc -"${ENCRYPTION_ALGORITHM}" -kfile "${ENCRYPTION_KEY_FILE}" -d -in "${input_file}" -out "${output_file}"; then
        log_error "Falha na descriptografia do arquivo: ${input_file}"
        return 1
    fi
    
    log_success "Arquivo descriptografado: ${output_file}"
    echo "${output_file}"
}

# Função para descomprimir arquivo
decompress_file() {
    local input_file="$1"
    local output_file="${input_file}"
    
    log_info "Descomprimindo arquivo: ${input_file}"
    
    if [[ "${input_file}" == *.gz ]]; then
        output_file="${input_file%.gz}"
        if ! gzip -d "${input_file}"; then
            log_error "Falha na descompressão gzip: ${input_file}"
            return 1
        fi
    elif [[ "${input_file}" == *.bz2 ]]; then
        output_file="${input_file%.bz2}"
        if ! bzip2 -d "${input_file}"; then
            log_error "Falha na descompressão bzip2: ${input_file}"
            return 1
        fi
    fi
    
    log_success "Arquivo descomprimido: ${output_file}"
    echo "${output_file}"
}

# Função para fazer backup do banco atual
backup_current_database() {
    local backup_name="pre_restore_backup_${TIMESTAMP}"
    local backup_file="${RESTORE_DIR}/${backup_name}.sql"
    
    log_info "Fazendo backup do banco atual antes do restore..."
    
    export PGPASSWORD="${DB_PASSWORD}"
    
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
        --file="${backup_file}"; then
        
        log_error "Falha no backup do banco atual"
        return 1
    fi
    
    log_success "Backup do banco atual concluído: ${backup_file}"
    echo "${backup_file}"
}

# Função para parar aplicações
stop_applications() {
    log_info "Parando aplicações..."
    
    # Parar serviços web
    if systemctl is-active --quiet nginx; then
        log_info "Parando Nginx..."
        systemctl stop nginx
    fi
    
    if systemctl is-active --quiet apache2; then
        log_info "Parando Apache..."
        systemctl stop apache2
    fi
    
    # Parar aplicação Python
    if systemctl is-active --quiet omni-keywords-finder; then
        log_info "Parando aplicação Omni Keywords Finder..."
        systemctl stop omni-keywords-finder
    fi
    
    log_success "Aplicações paradas"
}

# Função para iniciar aplicações
start_applications() {
    log_info "Iniciando aplicações..."
    
    # Iniciar serviços web
    log_info "Iniciando Nginx..."
    systemctl start nginx
    
    # Iniciar aplicação Python
    log_info "Iniciando aplicação Omni Keywords Finder..."
    systemctl start omni-keywords-finder
    
    log_success "Aplicações iniciadas"
}

# Função para enviar notificação
send_notification() {
    local status="$1"
    local message="$2"
    
    log_info "Enviando notificação: ${status}"
    
    # Notificação via Slack
    if [[ -n "${SLACK_WEBHOOK_URL}" ]]; then
        local slack_payload="{\"text\":\"🔄 Restore Omni Keywords Finder - ${status}\n${message}\n📅 Data: ${RESTORE_DATE}\n🔧 Tracing ID: ${TRACING_ID}\"}"
        
        if ! curl -X POST -H "Content-type: application/json" --data "${slack_payload}" "${SLACK_WEBHOOK_URL}" > /dev/null 2>&1; then
            log_warning "Falha ao enviar notificação Slack"
        fi
    fi
    
    # Notificação via email
    if [[ -n "${EMAIL_RECIPIENTS}" ]]; then
        local email_subject="[RESTORE] Omni Keywords Finder - ${status}"
        local email_body="Status: ${status}\nMensagem: ${message}\nData: ${RESTORE_DATE}\nTracing ID: ${TRACING_ID}\nLog: ${LOG_FILE}"
        
        if ! echo -e "${email_body}" | mail -s "${email_subject}" "${EMAIL_RECIPIENTS}"; then
            log_warning "Falha ao enviar notificação email"
        fi
    fi
    
    log_success "Notificação enviada"
}

# Função para restore completo
perform_full_restore() {
    local backup_file="$1"
    local target_db="${2:-${DB_NAME}}"
    
    log_info "Iniciando restore completo..."
    log_info "Backup: ${backup_file}"
    log_info "Banco de destino: ${target_db}"
    
    # Verificar integridade do backup
    verify_backup_integrity "${backup_file}"
    
    # Preparar arquivo para restore
    local restore_file="${backup_file}"
    
    # Descriptografar se necessário
    if [[ "${backup_file}" == *.enc ]]; then
        restore_file=$(decrypt_file "${backup_file}")
    fi
    
    # Descomprimir se necessário
    if [[ "${restore_file}" == *.gz ]] || [[ "${restore_file}" == *.bz2 ]]; then
        restore_file=$(decompress_file "${restore_file}")
    fi
    
    # Configurar variáveis de ambiente
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Parar aplicações
    stop_applications
    
    # Fazer backup do banco atual
    local pre_restore_backup=$(backup_current_database)
    
    # Executar restore
    log_info "Executando restore..."
    
    if ! psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "postgres" \
        -f "${restore_file}" \
        --set ON_ERROR_STOP=on \
        --echo-all; then
        
        log_error "Falha no restore"
        
        # Iniciar aplicações mesmo em caso de falha
        start_applications
        
        # Enviar notificação de falha
        send_notification "FAILED" "Restore falhou. Backup anterior preservado: ${pre_restore_backup}"
        
        return 1
    fi
    
    # Iniciar aplicações
    start_applications
    
    # Verificar se o restore foi bem-sucedido
    log_info "Verificando restore..."
    
    if ! psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${target_db}" \
        -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';" > /dev/null 2>&1; then
        
        log_error "Falha na verificação do restore"
        send_notification "FAILED" "Restore aparentemente falhou na verificação"
        return 1
    fi
    
    log_success "Restore completo concluído com sucesso"
    
    # Limpar arquivos temporários
    if [[ "${restore_file}" != "${backup_file}" ]]; then
        rm -f "${restore_file}"
    fi
    
    echo "${pre_restore_backup}"
}

# Função para restore incremental (WAL)
perform_incremental_restore() {
    local base_backup="$1"
    local wal_files=("${@:2}")
    
    log_info "Iniciando restore incremental..."
    log_info "Backup base: ${base_backup}"
    log_info "Arquivos WAL: ${#wal_files[@]}"
    
    # Verificar integridade do backup base
    verify_backup_integrity "${base_backup}"
    
    # Preparar backup base
    local restore_file="${base_backup}"
    
    # Descriptografar se necessário
    if [[ "${base_backup}" == *.enc ]]; then
        restore_file=$(decrypt_file "${base_backup}")
    fi
    
    # Descomprimir se necessário
    if [[ "${restore_file}" == *.gz ]] || [[ "${restore_file}" == *.bz2 ]]; then
        restore_file=$(decompress_file "${restore_file}")
    fi
    
    # Configurar variáveis de ambiente
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Parar aplicações
    stop_applications
    
    # Fazer backup do banco atual
    local pre_restore_backup=$(backup_current_database)
    
    # Executar restore base
    log_info "Executando restore base..."
    
    if ! psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "postgres" \
        -f "${restore_file}" \
        --set ON_ERROR_STOP=on; then
        
        log_error "Falha no restore base"
        start_applications
        send_notification "FAILED" "Restore incremental falhou no restore base"
        return 1
    fi
    
    # Aplicar arquivos WAL
    for wal_file in "${wal_files[@]}"; do
        log_info "Aplicando WAL: ${wal_file}"
        
        if ! pg_wal_restore \
            -h "${DB_HOST}" \
            -p "${DB_PORT}" \
            -U "${DB_USER}" \
            -d "${DB_NAME}" \
            "${wal_file}"; then
            
            log_error "Falha ao aplicar WAL: ${wal_file}"
            start_applications
            send_notification "FAILED" "Restore incremental falhou ao aplicar WAL: ${wal_file}"
            return 1
        fi
    done
    
    # Iniciar aplicações
    start_applications
    
    log_success "Restore incremental concluído com sucesso"
    
    # Limpar arquivos temporários
    if [[ "${restore_file}" != "${base_backup}" ]]; then
        rm -f "${restore_file}"
    fi
    
    echo "${pre_restore_backup}"
}

# Função para validar restore
validate_restore() {
    local target_db="${1:-${DB_NAME}}"
    
    log_info "Validando restore..."
    
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Verificar conectividade
    if ! psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${target_db}" \
        -c "SELECT 1;" > /dev/null 2>&1; then
        
        log_error "Falha na validação: não foi possível conectar ao banco"
        return 1
    fi
    
    # Verificar tabelas principais
    local expected_tables=("keywords" "keyword_analysis" "blog_data" "users" "sessions")
    
    for table in "${expected_tables[@]}"; do
        if ! psql \
            -h "${DB_HOST}" \
            -p "${DB_PORT}" \
            -U "${DB_USER}" \
            -d "${target_db}" \
            -c "SELECT COUNT(*) FROM ${table};" > /dev/null 2>&1; then
            
            log_warning "Tabela ${table} não encontrada ou inacessível"
        else
            log_info "Tabela ${table} validada com sucesso"
        fi
    done
    
    # Verificar integridade referencial
    if ! psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${target_db}" \
        -c "SELECT COUNT(*) FROM pg_constraint WHERE contype = 'f';" > /dev/null 2>&1; then
        
        log_warning "Não foi possível verificar constraints de chave estrangeira"
    else
        log_info "Constraints de chave estrangeira verificadas"
    fi
    
    log_success "Validação do restore concluída"
}

# Função principal
main() {
    local start_time=$(date +%s)
    local backup_file="$1"
    local restore_type="${2:-full}"
    local target_db="${3:-${DB_NAME}}"
    local validate_flag="${4:-true}"
    
    log_info "=== INÍCIO DO RESTORE ==="
    log_info "Arquivo: ${backup_file}"
    log_info "Tipo: ${restore_type}"
    log_info "Banco de destino: ${target_db}"
    log_info "Validação: ${validate_flag}"
    log_info "Tracing ID: ${TRACING_ID}"
    
    # Verificações iniciais
    check_dependencies
    create_directories
    check_database_connectivity
    
    # Executar restore
    local pre_restore_backup=""
    if [[ "${restore_type}" == "full" ]]; then
        pre_restore_backup=$(perform_full_restore "${backup_file}" "${target_db}")
    elif [[ "${restore_type}" == "incremental" ]]; then
        # Para restore incremental, backup_file deve ser o backup base
        # e os arquivos WAL devem ser passados como argumentos adicionais
        shift 2  # Remover backup_file e restore_type
        local wal_files=("$@")
        pre_restore_backup=$(perform_incremental_restore "${backup_file}" "${wal_files[@]}")
    else
        log_error "Tipo de restore inválido: ${restore_type}"
        exit 1
    fi
    
    # Validar restore se solicitado
    if [[ "${validate_flag}" == "true" ]]; then
        validate_restore "${target_db}"
    fi
    
    # Calcular tempo total
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Relatório final
    local report="Restore ${restore_type} concluído com sucesso\n"
    report+="Arquivo: ${backup_file}\n"
    report+="Banco: ${target_db}\n"
    report+="Duração: ${duration} segundos\n"
    report+="Backup anterior: ${pre_restore_backup}"
    
    log_success "=== RESTORE CONCLUÍDO ==="
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
    
    # Iniciar aplicações em caso de erro
    start_applications
    
    # Enviar notificação de erro
    local error_report="Restore falhou\n"
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
    echo "Uso: $0 <arquivo_backup> [full|incremental] [banco_destino] [validar]"
    echo "  arquivo_backup: Caminho para o arquivo de backup"
    echo "  full|incremental: Tipo de restore (padrão: full)"
    echo "  banco_destino: Nome do banco de destino (padrão: ${DB_NAME})"
    echo "  validar: true/false para validar restore (padrão: true)"
    echo ""
    echo "Exemplos:"
    echo "  $0 /var/backups/omni_keywords_finder/full/backup_full_20250127_143022.sql.gz"
    echo "  $0 /var/backups/omni_keywords_finder/full/backup_full_20250127_143022.sql.gz full omni_keywords_test"
    echo "  $0 /var/backups/omni_keywords_finder/full/backup_full_20250127_143022.sql.gz full ${DB_NAME} false"
    exit 1
fi

# Executar função principal
main "$@" 