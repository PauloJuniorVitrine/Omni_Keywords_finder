#!/bin/bash
# terraform/templates/user_data.sh
# Tracing ID: IMP004_USER_DATA_001
# Data: 2025-01-27
# Versão: 1.0
# Status: Em Implementação

# User Data script para configuração automática de instâncias
# Este script é executado na primeira inicialização da instância

set -e

# Variáveis do template
CLUSTER_NAME="${cluster_name}"
AWS_REGION="${region}"

# Configuração de logging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== INICIANDO CONFIGURAÇÃO DA INSTÂNCIA ==="
echo "Data/Hora: $(date)"
echo "Cluster: $CLUSTER_NAME"
echo "Região: $AWS_REGION"

# Função para logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função para tratamento de erros
error_exit() {
    log "ERRO: $1"
    exit 1
}

# Atualizar sistema
log "Atualizando sistema..."
yum update -y || error_exit "Falha ao atualizar sistema"

# Instalar dependências
log "Instalando dependências..."
yum install -y \
    docker \
    jq \
    curl \
    wget \
    unzip \
    git \
    htop \
    iotop \
    nethogs \
    tcpdump \
    netstat-nat \
    python3 \
    python3-pip \
    aws-cli \
    || error_exit "Falha ao instalar dependências"

# Configurar Docker
log "Configurando Docker..."
systemctl enable docker
systemctl start docker

# Configurar usuário ec2-user para usar Docker
usermod -a -G docker ec2-user

# Instalar Docker Compose
log "Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configurar AWS CLI
log "Configurando AWS CLI..."
mkdir -p /home/ec2-user/.aws
cat > /home/ec2-user/.aws/config << EOF
[default]
region = $AWS_REGION
output = json
EOF

chown -R ec2-user:ec2-user /home/ec2-user/.aws

# Configurar CloudWatch Agent
log "Configurando CloudWatch Agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Configuração do CloudWatch Agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/user-data.log",
                        "log_group_name": "/aws/ec2/omni-keywords-finder/user-data",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    },
                    {
                        "file_path": "/var/log/docker",
                        "log_group_name": "/aws/ec2/omni-keywords-finder/docker",
                        "log_stream_name": "{instance_id}",
                        "timezone": "UTC"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "OmniKeywords/EC2",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "metrics_collection_interval": 60,
                "totalcpu": false
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "diskio": {
                "measurement": [
                    "io_time"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            },
            "netstat": {
                "measurement": [
                    "tcp_established",
                    "tcp_time_wait"
                ],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": [
                    "swap_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Iniciar CloudWatch Agent
systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent

# Configurar health check endpoint
log "Configurando health check endpoint..."
mkdir -p /opt/health-check

cat > /opt/health-check/health.py << 'EOF'
#!/usr/bin/env python3
"""
Health Check Endpoint
Tracing ID: IMP004_HEALTH_CHECK_001
"""

import http.server
import socketserver
import json
import subprocess
import psutil
import os
from datetime import datetime

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = self.get_health_data()
            self.wfile.write(json.dumps(health_data, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_health_data(self):
        """Coleta dados de saúde do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Docker status
            docker_status = self.check_docker_status()
            
            # Load average
            load_avg = os.getloadavg()
            
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "instance_id": self.get_instance_id(),
                "system": {
                    "cpu": {
                        "usage_percent": cpu_percent,
                        "count": cpu_count,
                        "load_average": {
                            "1min": load_avg[0],
                            "5min": load_avg[1],
                            "15min": load_avg[2]
                        }
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_percent": memory.percent
                    },
                    "disk": {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2),
                        "used_percent": round((disk.used / disk.total) * 100, 2)
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    }
                },
                "services": {
                    "docker": docker_status,
                    "cloudwatch_agent": self.check_cloudwatch_status()
                }
            }
            
            # Marcar como unhealthy se algum critério não for atendido
            if (cpu_percent > 90 or 
                memory.percent > 90 or 
                (disk.used / disk.total) * 100 > 90 or
                docker_status["status"] != "running"):
                health_data["status"] = "unhealthy"
            
            return health_data
            
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def check_docker_status(self):
        """Verifica status do Docker"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'docker'], 
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            
            if status == "active":
                return {"status": "running", "details": "Docker service is active"}
            else:
                return {"status": "stopped", "details": f"Docker service status: {status}"}
        except Exception as e:
            return {"status": "error", "details": str(e)}
    
    def check_cloudwatch_status(self):
        """Verifica status do CloudWatch Agent"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'amazon-cloudwatch-agent'], 
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            
            if status == "active":
                return {"status": "running", "details": "CloudWatch Agent is active"}
            else:
                return {"status": "stopped", "details": f"CloudWatch Agent status: {status}"}
        except Exception as e:
            return {"status": "error", "details": str(e)}
    
    def get_instance_id(self):
        """Obtém ID da instância"""
        try:
            with open('/var/lib/cloud/data/instance-id', 'r') as f:
                return f.read().strip()
        except:
            return "unknown"
    
    def log_message(self, format, *args):
        """Suprime logs de acesso"""
        pass

def main():
    """Função principal"""
    PORT = 8080
    
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"Health check server running on port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
EOF

# Instalar psutil para o health check
pip3 install psutil

# Criar serviço systemd para health check
cat > /etc/systemd/system/health-check.service << EOF
[Unit]
Description=Health Check Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/health-check
ExecStart=/usr/bin/python3 /opt/health-check/health.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar health check service
systemctl enable health-check
systemctl start health-check

# Configurar firewall
log "Configurando firewall..."
systemctl enable firewalld
systemctl start firewalld

# Permitir portas necessárias
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload

# Configurar limites do sistema
log "Configurando limites do sistema..."
cat >> /etc/security/limits.conf << EOF
# Limites para o usuário ec2-user
ec2-user soft nofile 65536
ec2-user hard nofile 65536
ec2-user soft nproc 32768
ec2-user hard nproc 32768

# Limites para root
root soft nofile 65536
root hard nofile 65536
root soft nproc 32768
root hard nproc 32768
EOF

# Configurar sysctl para otimização de rede
log "Configurando otimizações de rede..."
cat >> /etc/sysctl.conf << EOF
# Otimizações de rede
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
net.ipv4.tcp_notsent_lowat = 131072
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fack = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_max_syn_backlog = 8192
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535
EOF

# Aplicar configurações sysctl
sysctl -p

# Configurar logrotate
log "Configurando logrotate..."
cat > /etc/logrotate.d/omni-keywords << EOF
/var/log/user-data.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload health-check > /dev/null 2>&1 || true
    endscript
}

/var/log/docker {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF

# Criar diretórios de trabalho
log "Criando diretórios de trabalho..."
mkdir -p /opt/omni-keywords-finder/{logs,data,config}
chown -R ec2-user:ec2-user /opt/omni-keywords-finder

# Configurar variáveis de ambiente
log "Configurando variáveis de ambiente..."
cat > /etc/environment << EOF
CLUSTER_NAME=$CLUSTER_NAME
AWS_REGION=$AWS_REGION
ENVIRONMENT=production
EOF

# Configurar cron jobs
log "Configurando cron jobs..."
cat > /etc/cron.d/omni-keywords << EOF
# Limpeza de logs antigos
0 2 * * * root find /var/log -name "*.log" -mtime +30 -delete

# Verificação de saúde
*/5 * * * * root curl -f http://localhost:8080/health > /dev/null 2>&1 || systemctl restart health-check

# Backup de configurações
0 3 * * * root tar -czf /opt/omni-keywords-finder/backup/config-\$(date +\%Y\%m\%d).tar.gz /opt/omni-keywords-finder/config/

# Limpeza de backups antigos
0 4 * * * root find /opt/omni-keywords-finder/backup -name "*.tar.gz" -mtime +7 -delete
EOF

# Configurar monitoramento de recursos
log "Configurando monitoramento de recursos..."
cat > /opt/monitor-resources.sh << 'EOF'
#!/bin/bash
# Script de monitoramento de recursos

LOG_FILE="/var/log/resource-monitor.log"
THRESHOLD_CPU=90
THRESHOLD_MEMORY=90
THRESHOLD_DISK=90

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
}

# CPU
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$cpu_usage > $THRESHOLD_CPU" | bc -l) )); then
    log "WARNING: CPU usage is ${cpu_usage}%"
fi

# Memory
memory_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$memory_usage > $THRESHOLD_MEMORY" | bc -l) )); then
    log "WARNING: Memory usage is ${memory_usage}%"
fi

# Disk
disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ "$disk_usage" -gt "$THRESHOLD_DISK" ]; then
    log "WARNING: Disk usage is ${disk_usage}%"
fi
EOF

chmod +x /opt/monitor-resources.sh

# Adicionar monitoramento ao cron
echo "*/5 * * * * root /opt/monitor-resources.sh" >> /etc/cron.d/omni-keywords

# Configurar backup automático
log "Configurando backup automático..."
mkdir -p /opt/omni-keywords-finder/backup

cat > /opt/backup-config.sh << 'EOF'
#!/bin/bash
# Script de backup de configurações

BACKUP_DIR="/opt/omni-keywords-finder/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de configurações
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /opt/omni-keywords-finder/config \
    /opt/health-check \
    /etc/environment \
    /etc/cron.d/omni-keywords

# Limpar backups antigos (manter apenas 7 dias)
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +7 -delete

echo "Backup completed: config_$DATE.tar.gz"
EOF

chmod +x /opt/backup-config.sh

# Configurar finalização
log "Configurando finalização..."
cat > /opt/cleanup.sh << 'EOF'
#!/bin/bash
# Script de limpeza na finalização da instância

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> /var/log/cleanup.log
}

log "Iniciando limpeza da instância..."

# Parar serviços
systemctl stop health-check || true
systemctl stop amazon-cloudwatch-agent || true
systemctl stop docker || true

# Backup final
/opt/backup-config.sh

# Limpar logs temporários
find /var/log -name "*.tmp" -delete
find /tmp -type f -mtime +1 -delete

log "Limpeza concluída"
EOF

chmod +x /opt/cleanup.sh

# Configurar finalização automática
echo "#!/bin/bash" > /etc/rc0.d/K99cleanup
echo "/opt/cleanup.sh" >> /etc/rc0.d/K99cleanup
chmod +x /etc/rc0.d/K99cleanup

# Configurar permissões
log "Configurando permissões..."
chown -R ec2-user:ec2-user /home/ec2-user
chmod +x /opt/*.sh

# Verificar se tudo está funcionando
log "Verificando serviços..."
systemctl is-active --quiet docker && log "Docker: OK" || log "Docker: FAILED"
systemctl is-active --quiet health-check && log "Health Check: OK" || log "Health Check: FAILED"
systemctl is-active --quiet amazon-cloudwatch-agent && log "CloudWatch: OK" || log "CloudWatch: FAILED"

# Testar health check endpoint
sleep 5
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    log "Health check endpoint: OK"
else
    log "Health check endpoint: FAILED"
fi

log "=== CONFIGURAÇÃO CONCLUÍDA ==="
log "Instância pronta para uso"
log "Health check disponível em: http://localhost:8080/health"

# Marcar como concluído
touch /var/lib/cloud/instances/$(curl -s http://169.254.169.254/latest/meta-data/instance-id)/user-data-complete 