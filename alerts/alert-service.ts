/**
 * Sistema de Alertas
 * 
 * Prompt: Implementação de itens de criticidade baixa - 11.5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { env } from '../config/environment';

// Tipos para alertas
interface AlertRule {
  id: string;
  name: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  condition: () => boolean | Promise<boolean>;
  cooldown: number; // Tempo em ms entre alertas
  channels: AlertChannel[];
  enabled: boolean;
  lastTriggered?: number;
}

interface AlertChannel {
  type: 'slack' | 'email' | 'webhook' | 'sms';
  config: Record<string, any>;
  enabled: boolean;
}

interface AlertNotification {
  id: string;
  ruleId: string;
  severity: AlertRule['severity'];
  message: string;
  timestamp: number;
  metadata: Record<string, any>;
  sent: boolean;
  error?: string;
}

/**
 * Classe principal de alertas
 */
export class AlertService {
  private rules: Map<string, AlertRule> = new Map();
  private notifications: AlertNotification[] = [];
  private isEnabled: boolean;

  constructor() {
    this.isEnabled = env.ENABLE_TELEMETRY;
    this.initializeAlertService();
  }

  /**
   * Inicializa o serviço de alertas
   */
  private initializeAlertService(): void {
    if (!this.isEnabled) {
      console.log('[ALERTS] Sistema de alertas desabilitado');
      return;
    }

    // Configurar regras padrão
    this.setupDefaultRules();
    
    // Iniciar verificação periódica
    this.startPeriodicChecks();
    
    console.log('[ALERTS] Sistema de alertas inicializado');
  }

  /**
   * Configura regras padrão de alerta
   */
  private setupDefaultRules(): void {
    // Alerta para alta utilização de CPU
    this.addRule({
      id: 'high_cpu_usage',
      name: 'Alta Utilização de CPU',
      description: 'CPU acima de 80% por mais de 5 minutos',
      severity: 'medium',
      condition: async () => {
        // Simulação - em produção você verificaria métricas reais
        const cpuUsage = Math.random() * 100;
        return cpuUsage > 80;
      },
      cooldown: 300000, // 5 minutos
      channels: [
        {
          type: 'slack',
          config: { channel: '#devops-alertas' },
          enabled: true
        },
        {
          type: 'email',
          config: { recipients: ['admin@example.com'] },
          enabled: true
        }
      ],
      enabled: true
    });

    // Alerta para falha de API
    this.addRule({
      id: 'api_failure',
      name: 'Falha de API',
      description: 'Taxa de erro da API acima de 5%',
      severity: 'high',
      condition: async () => {
        // Simulação - em produção você verificaria métricas reais
        const errorRate = Math.random() * 10;
        return errorRate > 5;
      },
      cooldown: 60000, // 1 minuto
      channels: [
        {
          type: 'slack',
          config: { channel: '#devops-critico' },
          enabled: true
        },
        {
          type: 'webhook',
          config: { url: env.ALERT_WEBHOOK_URL },
          enabled: true
        }
      ],
      enabled: true
    });

    // Alerta para espaço em disco
    this.addRule({
      id: 'disk_space',
      name: 'Espaço em Disco Baixo',
      description: 'Espaço em disco abaixo de 10%',
      severity: 'critical',
      condition: async () => {
        // Simulação - em produção você verificaria métricas reais
        const diskUsage = Math.random() * 100;
        return diskUsage > 90;
      },
      cooldown: 180000, // 3 minutos
      channels: [
        {
          type: 'slack',
          config: { channel: '#devops-critico' },
          enabled: true
        },
        {
          type: 'sms',
          config: { phone: '+5511999999999' },
          enabled: true
        }
      ],
      enabled: true
    });
  }

  /**
   * Adiciona uma regra de alerta
   */
  public addRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
    console.log(`[ALERTS] Regra adicionada: ${rule.name}`);
  }

  /**
   * Remove uma regra de alerta
   */
  public removeRule(ruleId: string): void {
    this.rules.delete(ruleId);
    console.log(`[ALERTS] Regra removida: ${ruleId}`);
  }

  /**
   * Habilita/desabilita uma regra
   */
  public toggleRule(ruleId: string, enabled: boolean): void {
    const rule = this.rules.get(ruleId);
    if (rule) {
      rule.enabled = enabled;
      console.log(`[ALERTS] Regra ${ruleId} ${enabled ? 'habilitada' : 'desabilitada'}`);
    }
  }

  /**
   * Inicia verificação periódica das regras
   */
  private startPeriodicChecks(): void {
    setInterval(async () => {
      await this.checkAllRules();
    }, 30000); // Verificar a cada 30 segundos
  }

  /**
   * Verifica todas as regras habilitadas
   */
  private async checkAllRules(): Promise<void> {
    for (const rule of this.rules.values()) {
      if (!rule.enabled) continue;

      // Verificar cooldown
      if (rule.lastTriggered && Date.now() - rule.lastTriggered < rule.cooldown) {
        continue;
      }

      try {
        const shouldTrigger = await rule.condition();
        if (shouldTrigger) {
          await this.triggerAlert(rule);
        }
      } catch (error) {
        console.error(`[ALERTS] Erro ao verificar regra ${rule.id}:`, error);
      }
    }
  }

  /**
   * Dispara um alerta
   */
  private async triggerAlert(rule: AlertRule): Promise<void> {
    rule.lastTriggered = Date.now();

    const notification: AlertNotification = {
      id: `${rule.id}_${Date.now()}`,
      ruleId: rule.id,
      severity: rule.severity,
      message: `${rule.name}: ${rule.description}`,
      timestamp: Date.now(),
      metadata: {
        ruleName: rule.name,
        severity: rule.severity,
        cooldown: rule.cooldown
      },
      sent: false
    };

    this.notifications.push(notification);

    // Enviar notificações para todos os canais habilitados
    for (const channel of rule.channels) {
      if (channel.enabled) {
        try {
          await this.sendNotification(notification, channel);
          notification.sent = true;
        } catch (error) {
          notification.error = error instanceof Error ? error.message : 'Unknown error';
          console.error(`[ALERTS] Erro ao enviar notificação via ${channel.type}:`, error);
        }
      }
    }

    console.log(`[ALERTS] Alerta disparado: ${rule.name} (${rule.severity})`);
  }

  /**
   * Envia notificação para um canal específico
   */
  private async sendNotification(
    notification: AlertNotification, 
    channel: AlertChannel
  ): Promise<void> {
    switch (channel.type) {
      case 'slack':
        await this.sendSlackNotification(notification, channel.config);
        break;
      case 'email':
        await this.sendEmailNotification(notification, channel.config);
        break;
      case 'webhook':
        await this.sendWebhookNotification(notification, channel.config);
        break;
      case 'sms':
        await this.sendSMSNotification(notification, channel.config);
        break;
      default:
        throw new Error(`Canal não suportado: ${channel.type}`);
    }
  }

  /**
   * Envia notificação para Slack
   */
  private async sendSlackNotification(
    notification: AlertNotification, 
    config: Record<string, any>
  ): Promise<void> {
    const message = {
      channel: config.channel,
      text: `🚨 *ALERTA ${notification.severity.toUpperCase()}*`,
      attachments: [
        {
          color: this.getSeverityColor(notification.severity),
          fields: [
            {
              title: 'Mensagem',
              value: notification.message,
              short: false
            },
            {
              title: 'Timestamp',
              value: new Date(notification.timestamp).toISOString(),
              short: true
            },
            {
              title: 'ID',
              value: notification.id,
              short: true
            }
          ]
        }
      ]
    };

    // Em produção, você usaria a API real do Slack
    console.log(`[ALERTS] Slack notification: ${JSON.stringify(message, null, 2)}`);
  }

  /**
   * Envia notificação por email
   */
  private async sendEmailNotification(
    notification: AlertNotification, 
    config: Record<string, any>
  ): Promise<void> {
    const emailData = {
      to: config.recipients,
      subject: `[ALERTA ${notification.severity.toUpperCase()}] ${notification.message}`,
      body: `
        <h2>🚨 Alerta do Sistema</h2>
        <p><strong>Severidade:</strong> ${notification.severity}</p>
        <p><strong>Mensagem:</strong> ${notification.message}</p>
        <p><strong>Timestamp:</strong> ${new Date(notification.timestamp).toISOString()}</p>
        <p><strong>ID:</strong> ${notification.id}</p>
      `
    };

    // Em produção, você usaria um serviço de email real
    console.log(`[ALERTS] Email notification: ${JSON.stringify(emailData, null, 2)}`);
  }

  /**
   * Envia notificação via webhook
   */
  private async sendWebhookNotification(
    notification: AlertNotification, 
    config: Record<string, any>
  ): Promise<void> {
    const payload = {
      alert: {
        id: notification.id,
        severity: notification.severity,
        message: notification.message,
        timestamp: notification.timestamp,
        metadata: notification.metadata
      },
      source: 'omni-keywords-finder',
      environment: env.NODE_ENV
    };

    // Em produção, você faria uma requisição HTTP real
    console.log(`[ALERTS] Webhook notification: ${JSON.stringify(payload, null, 2)}`);
  }

  /**
   * Envia notificação por SMS
   */
  private async sendSMSNotification(
    notification: AlertNotification, 
    config: Record<string, any>
  ): Promise<void> {
    const smsData = {
      to: config.phone,
      message: `ALERTA ${notification.severity.toUpperCase()}: ${notification.message}`
    };

    // Em produção, você usaria um serviço de SMS real
    console.log(`[ALERTS] SMS notification: ${JSON.stringify(smsData, null, 2)}`);
  }

  /**
   * Obtém cor para severidade no Slack
   */
  private getSeverityColor(severity: AlertRule['severity']): string {
    switch (severity) {
      case 'low': return '#36a64f'; // Verde
      case 'medium': return '#ffa500'; // Laranja
      case 'high': return '#ff0000'; // Vermelho
      case 'critical': return '#8b0000'; // Vermelho escuro
      default: return '#808080'; // Cinza
    }
  }

  /**
   * Obtém todas as regras
   */
  public getRules(): AlertRule[] {
    return Array.from(this.rules.values());
  }

  /**
   * Obtém notificações
   */
  public getNotifications(filter?: {
    severity?: AlertRule['severity'];
    sent?: boolean;
    ruleId?: string;
  }): AlertNotification[] {
    let filtered = this.notifications;

    if (filter?.severity) {
      filtered = filtered.filter(n => n.severity === filter.severity);
    }

    if (filter?.sent !== undefined) {
      filtered = filtered.filter(n => n.sent === filter.sent);
    }

    if (filter?.ruleId) {
      filtered = filtered.filter(n => n.ruleId === filter.ruleId);
    }

    return filtered;
  }

  /**
   * Gera relatório de alertas
   */
  public generateReport(): {
    rules: { total: number; enabled: number; disabled: number };
    notifications: { total: number; sent: number; failed: number; bySeverity: Record<string, number> };
    last24h: { triggered: number; resolved: number };
  } {
    const rules = Array.from(this.rules.values());
    const notifications = this.notifications;
    const last24h = Date.now() - 24 * 60 * 60 * 1000;

    const notificationsBySeverity = notifications.reduce((acc, notification) => {
      acc[notification.severity] = (acc[notification.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      rules: {
        total: rules.length,
        enabled: rules.filter(r => r.enabled).length,
        disabled: rules.filter(r => !r.enabled).length
      },
      notifications: {
        total: notifications.length,
        sent: notifications.filter(n => n.sent).length,
        failed: notifications.filter(n => !n.sent).length,
        bySeverity: notificationsBySeverity
      },
      last24h: {
        triggered: notifications.filter(n => n.timestamp > last24h).length,
        resolved: 0 // Implementar lógica de resolução se necessário
      }
    };
  }
}

// Instância singleton
export const alertService = new AlertService();

/**
 * Hook para usar o alert service
 */
export function useAlerts() {
  return {
    addRule: alertService.addRule.bind(alertService),
    removeRule: alertService.removeRule.bind(alertService),
    toggleRule: alertService.toggleRule.bind(alertService),
    getRules: alertService.getRules.bind(alertService),
    getNotifications: alertService.getNotifications.bind(alertService),
    generateReport: alertService.generateReport.bind(alertService),
  };
} 