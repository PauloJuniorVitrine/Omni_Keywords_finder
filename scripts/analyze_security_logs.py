#!/usr/bin/env python3
"""
Script para analisar logs de segurança e detectar anomalias
Implementa análise de padrões e geração de relatórios
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import argparse

class SecurityLogAnalyzer:
    """Analisador de logs de segurança"""
    
    def __init__(self, log_file: str = "logs/security_audit.log"):
        self.log_file = log_file
        self.events = []
        self.analysis_results = {}
    
    def load_logs(self, hours: int = 24) -> bool:
        """Carrega logs das últimas N horas"""
        if not os.path.exists(self.log_file):
            print(f"❌ Arquivo de log não encontrado: {self.log_file}")
            return False
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = json.loads(line)
                        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                        
                        if event_time >= cutoff_time:
                            self.events.append(event)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"⚠️ Erro ao processar linha: {e}")
                        continue
            
            print(f"✅ Carregados {len(self.events)} eventos das últimas {hours} horas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar logs: {e}")
            return False
    
    def analyze_events(self) -> Dict[str, Any]:
        """Analisa eventos de segurança"""
        if not self.events:
            print("⚠️ Nenhum evento para analisar")
            return {}
        
        analysis = {
            'summary': self._generate_summary(),
            'risk_analysis': self._analyze_risk_patterns(),
            'anomalies': self._detect_anomalies(),
            'top_ips': self._get_top_ips(),
            'top_users': self._get_top_users(),
            'event_distribution': self._get_event_distribution(),
            'security_alerts': self._get_security_alerts(),
            'recommendations': []
        }
        
        # Gerar recomendações
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        self.analysis_results = analysis
        return analysis
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Gera resumo dos eventos"""
        total_events = len(self.events)
        high_risk_events = sum(1 for e in self.events if e.get('security_level') in ['warning', 'critical', 'alert'])
        alert_events = sum(1 for e in self.events if e.get('security_level') == 'alert')
        
        return {
            'total_events': total_events,
            'high_risk_events': high_risk_events,
            'alert_events': alert_events,
            'risk_percentage': (high_risk_events / total_events * 100) if total_events > 0 else 0,
            'time_range': {
                'start': min(e['timestamp'] for e in self.events) if self.events else None,
                'end': max(e['timestamp'] for e in self.events) if self.events else None
            }
        }
    
    def _analyze_risk_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de risco"""
        risk_scores = [e.get('risk_score', 0) for e in self.events]
        high_risk_events = [e for e in self.events if e.get('risk_score', 0) >= 7]
        
        return {
            'average_risk_score': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'max_risk_score': max(risk_scores) if risk_scores else 0,
            'high_risk_count': len(high_risk_events),
            'risk_distribution': Counter(risk_scores),
            'high_risk_events': high_risk_events[:10]  # Top 10 eventos de alto risco
        }
    
    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detecta anomalias nos eventos"""
        anomalies = []
        
        # Análise por IP
        ip_events = defaultdict(list)
        for event in self.events:
            ip_events[event['ip_address']].append(event)
        
        for ip, events in ip_events.items():
            # Muitas tentativas de login falhadas
            failed_logins = [e for e in events if e.get('event_type') == 'login_failed']
            if len(failed_logins) > 5:
                anomalies.append({
                    'type': 'brute_force_attempt',
                    'ip_address': ip,
                    'failed_attempts': len(failed_logins),
                    'events': failed_logins
                })
            
            # Muitos eventos de alto risco
            high_risk = [e for e in events if e.get('risk_score', 0) >= 7]
            if len(high_risk) > 3:
                anomalies.append({
                    'type': 'suspicious_activity',
                    'ip_address': ip,
                    'high_risk_events': len(high_risk),
                    'events': high_risk
                })
        
        # Análise por usuário
        user_events = defaultdict(list)
        for event in self.events:
            if event.get('username'):
                user_events[event['username']].append(event)
        
        for username, events in user_events.items():
            # Muitas tentativas de login falhadas
            failed_logins = [e for e in events if e.get('event_type') == 'login_failed']
            if len(failed_logins) > 3:
                anomalies.append({
                    'type': 'account_targeted',
                    'username': username,
                    'failed_attempts': len(failed_logins),
                    'events': failed_logins
                })
        
        return anomalies
    
    def _get_top_ips(self) -> List[Dict[str, Any]]:
        """Obtém IPs com mais eventos"""
        ip_counts = Counter(e['ip_address'] for e in self.events)
        return [
            {'ip': ip, 'count': count, 'risk_score': self._get_ip_risk_score(ip)}
            for ip, count in ip_counts.most_common(10)
        ]
    
    def _get_ip_risk_score(self, ip: str) -> float:
        """Calcula score de risco para um IP"""
        ip_events = [e for e in self.events if e['ip_address'] == ip]
        if not ip_events:
            return 0
        
        risk_scores = [e.get('risk_score', 0) for e in ip_events]
        return sum(risk_scores) / len(risk_scores)
    
    def _get_top_users(self) -> List[Dict[str, Any]]:
        """Obtém usuários com mais eventos"""
        user_counts = Counter(e['username'] for e in self.events if e.get('username'))
        return [
            {'username': username, 'count': count}
            for username, count in user_counts.most_common(10)
        ]
    
    def _get_event_distribution(self) -> Dict[str, int]:
        """Obtém distribuição de tipos de eventos"""
        return Counter(e.get('event_type', 'unknown') for e in self.events)
    
    def _get_security_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas de segurança"""
        return [
            e for e in self.events 
            if e.get('security_level') == 'alert' or e.get('risk_score', 0) >= 8
        ]
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Análise de risco
        if analysis['risk_analysis']['high_risk_count'] > 10:
            recommendations.append("🔴 ALTO RISCO: Muitos eventos de alto risco detectados. Revisar configurações de segurança.")
        
        # Análise de anomalias
        if analysis['anomalies']:
            recommendations.append("⚠️ ANOMALIAS: Padrões suspeitos detectados. Investigar IPs e usuários suspeitos.")
        
        # Análise de IPs
        top_ip = analysis['top_ips'][0] if analysis['top_ips'] else None
        if top_ip and top_ip['count'] > 50:
            recommendations.append(f"🚨 IP SUSPEITO: IP {top_ip['ip']} com {top_ip['count']} eventos. Considerar bloqueio.")
        
        # Análise de tentativas falhadas
        failed_logins = analysis['event_distribution'].get('login_failed', 0)
        if failed_logins > 20:
            recommendations.append("🔒 FORÇA BRUTA: Muitas tentativas de login falhadas. Reforçar rate limiting.")
        
        # Análise de alertas
        if analysis['security_alerts']:
            recommendations.append("🚨 ALERTAS: Alertas de segurança ativos. Ação imediata necessária.")
        
        if not recommendations:
            recommendations.append("✅ SEGURO: Nenhuma ameaça crítica detectada. Manter monitoramento.")
        
        return recommendations
    
    def print_report(self, analysis: Dict[str, Any]):
        """Imprime relatório de análise"""
        print("\n" + "=" * 80)
        print("🔒 RELATÓRIO DE ANÁLISE DE SEGURANÇA - OMNI KEYWORDS FINDER")
        print("=" * 80)
        
        # Resumo
        summary = analysis['summary']
        print(f"\n📊 RESUMO:")
        print(f"   Total de eventos: {summary['total_events']}")
        print(f"   Eventos de alto risco: {summary['high_risk_events']}")
        print(f"   Alertas: {summary['alert_events']}")
        print(f"   Percentual de risco: {summary['risk_percentage']:.1f}%")
        
        # Análise de risco
        risk_analysis = analysis['risk_analysis']
        print(f"\n🎯 ANÁLISE DE RISCO:")
        print(f"   Score médio de risco: {risk_analysis['average_risk_score']:.2f}")
        print(f"   Score máximo de risco: {risk_analysis['max_risk_score']}")
        print(f"   Eventos de alto risco: {risk_analysis['high_risk_count']}")
        
        # Top IPs
        print(f"\n🌐 TOP IPs:")
        for i, ip_data in enumerate(analysis['top_ips'][:5], 1):
            print(f"   {i}. {ip_data['ip']} - {ip_data['count']} eventos (risco: {ip_data['risk_score']:.1f})")
        
        # Anomalias
        if analysis['anomalies']:
            print(f"\n🚨 ANOMALIAS DETECTADAS:")
            for anomaly in analysis['anomalies']:
                print(f"   - {anomaly['type']}: {anomaly.get('ip_address', anomaly.get('username', 'N/A'))}")
        
        # Distribuição de eventos
        print(f"\n📈 DISTRIBUIÇÃO DE EVENTOS:")
        for event_type, count in analysis['event_distribution'].items():
            print(f"   {event_type}: {count}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in analysis['recommendations']:
            print(f"   {rec}")
        
        print("\n" + "=" * 80)
    
    def save_report(self, analysis: Dict[str, Any], filename: str = "security_analysis_report.json"):
        """Salva relatório em arquivo JSON"""
        try:
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            print(f"✅ Relatório salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Analisador de logs de segurança')
    parser.add_argument('--log-file', default='logs/security_audit.log', help='Arquivo de log')
    parser.add_argument('--hours', type=int, default=24, help='Horas para analisar')
    parser.add_argument('--output', help='Arquivo de saída para o relatório')
    
    args = parser.parse_args()
    
    analyzer = SecurityLogAnalyzer(args.log_file)
    
    if not analyzer.load_logs(args.hours):
        return 1
    
    analysis = analyzer.analyze_events()
    
    if not analysis:
        print("❌ Nenhuma análise possível")
        return 1
    
    analyzer.print_report(analysis)
    
    if args.output:
        analyzer.save_report(analysis, args.output)
    else:
        analyzer.save_report(analysis)
    
    return 0

if __name__ == "__main__":
    exit(main()) 