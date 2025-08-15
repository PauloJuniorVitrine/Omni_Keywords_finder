"""
Canal de Email para Notificações
================================

Implementa notificações via email com suporte a templates HTML,
múltiplos provedores SMTP e fallback inteligente.

Tracing ID: NOTIF_20241219_001
Autor: Sistema de Notificações Avançado
Data: 2024-12-19
Versão: 1.0.0
"""

import asyncio
import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SMTPConfig:
    """Configuração SMTP."""
    server: str
    port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30
    from_email: str = ""
    from_name: str = "Omni Keywords Finder"


@dataclass
class EmailTemplate:
    """Template de email HTML."""
    name: str
    subject: str
    html_content: str
    text_content: str = ""
    variables: List[str] = None
    attachments: List[str] = None


class EmailChannel:
    """Canal de notificação via Email."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = SMTPConfig(**smtp_config)
        self.templates: Dict[str, EmailTemplate] = {}
        self.user_emails: Dict[str, str] = {}  # Cache de emails
        self.fallback_configs: List[SMTPConfig] = []
        
        # Inicializa templates padrão
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Inicializa templates de email padrão."""
        
        # Template de execução concluída
        execucao_template = EmailTemplate(
            name="execucao_concluida",
            subject="✅ Execução {{execucao_id}} concluída com sucesso",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .metric { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Execução Concluída</h1>
                    </div>
                    <div class="content">
                        <p>Olá <strong>{{user_name}}</strong>,</p>
                        <p>A execução <strong>{{execucao_id}}</strong> foi concluída com sucesso!</p>
                        
                        <div class="metric">
                            <strong>📊 Resultados:</strong><br>
                            • Keywords encontradas: <strong>{{keywords_count}}</strong><br>
                            • Tempo de execução: <strong>{{tempo_execucao}}</strong><br>
                            • Status: <span style="color: #4CAF50;">✅ Sucesso</span>
                        </div>
                        
                        <div class="metric">
                            <strong>🔍 Detalhes:</strong><br>
                            • Blog analisado: <strong>{{blog_url}}</strong><br>
                            • Data de início: <strong>{{data_inicio}}</strong><br>
                            • Data de conclusão: <strong>{{data_conclusao}}</strong>
                        </div>
                        
                        <p><a href="{{dashboard_url}}" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver no Dashboard</a></p>
                    </div>
                    <div class="footer">
                        <p>Omni Keywords Finder - Plataforma Enterprise</p>
                        <p>Este email foi enviado automaticamente. Não responda a este email.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_content="""
            Execução Concluída
            
            Olá {{user_name}},
            
            A execução {{execucao_id}} foi concluída com sucesso!
            
            Resultados:
            - Keywords encontradas: {{keywords_count}}
            - Tempo de execução: {{tempo_execucao}}
            - Status: Sucesso
            
            Detalhes:
            - Blog analisado: {{blog_url}}
            - Data de início: {{data_inicio}}
            - Data de conclusão: {{data_conclusao}}
            
            Acesse o dashboard: {{dashboard_url}}
            
            Omni Keywords Finder - Plataforma Enterprise
            """,
            variables=["user_name", "execucao_id", "keywords_count", "tempo_execucao", "blog_url", "data_inicio", "data_conclusao", "dashboard_url"]
        )
        
        # Template de erro
        erro_template = EmailTemplate(
            name="execucao_erro",
            subject="❌ Erro na execução {{execucao_id}}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #f44336; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .error { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>❌ Erro na Execução</h1>
                    </div>
                    <div class="content">
                        <p>Olá <strong>{{user_name}}</strong>,</p>
                        <p>A execução <strong>{{execucao_id}}</strong> falhou.</p>
                        
                        <div class="error">
                            <strong>🚨 Erro:</strong><br>
                            {{error_message}}
                        </div>
                        
                        <div class="error">
                            <strong>🔧 Ações recomendadas:</strong><br>
                            • Verifique a URL do blog<br>
                            • Confirme se o site está acessível<br>
                            • Tente executar novamente<br>
                            • Entre em contato com o suporte se o problema persistir
                        </div>
                        
                        <p><a href="{{dashboard_url}}" style="background: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver no Dashboard</a></p>
                    </div>
                    <div class="footer">
                        <p>Omni Keywords Finder - Plataforma Enterprise</p>
                        <p>Este email foi enviado automaticamente. Não responda a este email.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_content="""
            Erro na Execução
            
            Olá {{user_name}},
            
            A execução {{execucao_id}} falhou.
            
            Erro:
            {{error_message}}
            
            Ações recomendadas:
            - Verifique a URL do blog
            - Confirme se o site está acessível
            - Tente executar novamente
            - Entre em contato com o suporte se o problema persistir
            
            Acesse o dashboard: {{dashboard_url}}
            
            Omni Keywords Finder - Plataforma Enterprise
            """,
            variables=["user_name", "execucao_id", "error_message", "dashboard_url"]
        )
        
        # Template de relatório semanal
        relatorio_template = EmailTemplate(
            name="relatorio_semanal",
            subject="📊 Relatório Semanal - {{periodo}}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #2196F3; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .metric { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Relatório Semanal</h1>
                        <p>{{periodo}}</p>
                    </div>
                    <div class="content">
                        <p>Olá <strong>{{user_name}}</strong>,</p>
                        <p>Aqui está seu relatório semanal de atividades:</p>
                        
                        <div class="metric">
                            <strong>📈 Estatísticas Gerais:</strong><br>
                            • Execuções realizadas: <strong>{{execucoes_count}}</strong><br>
                            • Keywords encontradas: <strong>{{keywords_total}}</strong><br>
                            • Tempo total de processamento: <strong>{{tempo_total}}</strong>
                        </div>
                        
                        <div class="metric">
                            <strong>🏆 Top Keywords:</strong><br>
                            {{top_keywords}}
                        </div>
                        
                        <div class="metric">
                            <strong>📊 Performance:</strong><br>
                            • Taxa de sucesso: <strong>{{taxa_sucesso}}%</strong><br>
                            • Tempo médio por execução: <strong>{{tempo_medio}}</strong>
                        </div>
                        
                        <p><a href="{{dashboard_url}}" style="background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Dashboard Completo</a></p>
                    </div>
                    <div class="footer">
                        <p>Omni Keywords Finder - Plataforma Enterprise</p>
                        <p>Este email foi enviado automaticamente. Não responda a este email.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            variables=["user_name", "periodo", "execucoes_count", "keywords_total", "tempo_total", "top_keywords", "taxa_sucesso", "tempo_medio", "dashboard_url"]
        )
        
        # Adiciona templates
        self.templates["execucao_concluida"] = execucao_template
        self.templates["execucao_erro"] = erro_template
        self.templates["relatorio_semanal"] = relatorio_template
    
    async def send(self, notification) -> bool:
        """Envia notificação via email."""
        try:
            # Busca email do usuário
            user_email = self._get_user_email(notification.user_id)
            if not user_email:
                logger.error(f"Email não encontrado para usuário {notification.user_id}")
                return False
            
            # Renderiza template se especificado
            if notification.template_name:
                email_content = self._render_template(notification.template_name, notification.variables)
                if not email_content:
                    logger.error(f"Erro ao renderizar template {notification.template_name}")
                    return False
                
                subject = email_content["subject"]
                html_content = email_content["html"]
                text_content = email_content["text"]
            else:
                subject = notification.subject
                html_content = notification.content
                text_content = self._html_to_text(notification.content)
            
            # Cria mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.smtp_config.from_name} <{self.smtp_config.from_email}>"
            msg['To'] = user_email
            msg['Subject'] = subject
            
            # Adiciona conteúdo HTML e texto
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # Tenta enviar com configuração principal
            if await self._send_with_config(msg, self.smtp_config):
                logger.info(f"Email enviado para {user_email}")
                return True
            
            # Tenta fallback se disponível
            for fallback_config in self.fallback_configs:
                if await self._send_with_config(msg, fallback_config):
                    logger.info(f"Email enviado via fallback para {user_email}")
                    return True
            
            logger.error(f"Falha ao enviar email para {user_email}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return False
    
    async def _send_with_config(self, msg: MIMEMultipart, config: SMTPConfig) -> bool:
        """Envia email usando configuração específica."""
        try:
            context = ssl.create_default_context() if config.use_tls else None
            
            with smtplib.SMTP(config.server, config.port, timeout=config.timeout) as server:
                if config.use_tls:
                    server.starttls(context=context)
                elif config.use_ssl:
                    server = smtplib.SMTP_SSL(config.server, config.port, timeout=config.timeout)
                
                if config.username and config.password:
                    server.login(config.username, config.password)
                
                server.send_message(msg)
                return True
                
        except Exception as e:
            logger.error(f"Erro com configuração SMTP {config.server}: {e}")
            return False
    
    def _get_user_email(self, user_id: str) -> Optional[str]:
        """Busca email do usuário (implementar conforme modelo de usuário)."""
        # TODO: Implementar busca no banco de dados
        if user_id in self.user_emails:
            return self.user_emails[user_id]
        
        # Simula busca no banco
        email = f"{user_id}@example.com"
        self.user_emails[user_id] = email
        return email
    
    def _render_template(self, template_name: str, variables: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Renderiza template de email."""
        if template_name not in self.templates:
            logger.error(f"Template não encontrado: {template_name}")
            return None
        
        template = self.templates[template_name]
        
        try:
            from jinja2 import Template
            
            # Renderiza subject
            subject_template = Template(template.subject)
            subject = subject_template.render(**variables)
            
            # Renderiza conteúdo HTML
            html_template = Template(template.html_content)
            html_content = html_template.render(**variables)
            
            # Renderiza conteúdo texto
            if template.text_content:
                text_template = Template(template.text_content)
                text_content = text_template.render(**variables)
            else:
                text_content = self._html_to_text(html_content)
            
            return {
                "subject": subject,
                "html": html_content,
                "text": text_content
            }
            
        except Exception as e:
            logger.error(f"Erro ao renderizar template {template_name}: {e}")
            return None
    
    def _html_to_text(self, html_content: str) -> str:
        """Converte HTML para texto simples."""
        import re
        
        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Remove espaços extras
        text = re.sub(r'\string_data+', ' ', text)
        
        # Remove quebras de linha extras
        text = re.sub(r'\n\string_data*\n', '\n\n', text)
        
        return text.strip()
    
    def is_available(self) -> bool:
        """Verifica se o servidor SMTP está disponível."""
        try:
            with smtplib.SMTP(self.smtp_config.server, self.smtp_config.port, timeout=5) as server:
                if self.smtp_config.use_tls:
                    server.starttls()
                return True
        except Exception as e:
            logger.error(f"SMTP não disponível: {e}")
            return False
    
    def get_name(self) -> str:
        return "email"
    
    def add_template(self, template: EmailTemplate):
        """Adiciona novo template de email."""
        self.templates[template.name] = template
        logger.info(f"Template de email adicionado: {template.name}")
    
    def add_fallback_config(self, config: SMTPConfig):
        """Adiciona configuração SMTP de fallback."""
        self.fallback_configs.append(config)
        logger.info(f"Configuração SMTP de fallback adicionada: {config.server}")
    
    def get_templates(self) -> List[str]:
        """Retorna lista de templates disponíveis."""
        return list(self.templates.keys()) 