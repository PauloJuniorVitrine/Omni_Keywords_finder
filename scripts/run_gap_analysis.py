#!/usr/bin/env python3
"""
Script de Análise de Lacunas
============================

Script para executar análise completa de lacunas e integridade do projeto.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.analysis.gap_detector import GapDetector
from infrastructure.analysis.integrity_validator import IntegrityValidator
from shared.logger import logger


def setup_argparse():
    """Configura argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Análise de Lacunas e Integridade do Projeto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/run_gap_analysis.py                    # Análise completa
  python scripts/run_gap_analysis.py --gaps-only        # Apenas análise de lacunas
  python scripts/run_gap_analysis.py --integrity-only   # Apenas validação de integridade
  python scripts/run_gap_analysis.py --output reports/  # Salvar relatórios em reports/
  python scripts/run_gap_analysis.py --verbose          # Modo verboso
        """
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Diretório raiz do projeto (padrão: .)'
    )
    
    parser.add_argument(
        '--gaps-only',
        action='store_true',
        help='Executar apenas análise de lacunas'
    )
    
    parser.add_argument(
        '--integrity-only',
        action='store_true',
        help='Executar apenas validação de integridade'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='reports',
        help='Diretório para salvar relatórios (padrão: reports)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso com mais detalhes'
    )
    
    parser.add_argument(
        '--enable-nlp',
        action='store_true',
        help='Habilitar análise NLP (requer bibliotecas adicionais)'
    )
    
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.7,
        help='Threshold de confiança para detecção (padrão: 0.7)'
    )
    
    return parser


def create_output_directory(output_dir: str):
    """Cria diretório de saída se não existir."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório de saída: {output_path.absolute()}")
    return output_path


def run_gap_analysis(project_root: str, output_dir: Path, enable_nlp: bool, confidence_threshold: float, verbose: bool):
    """Executa análise de lacunas."""
    logger.info("🔍 Iniciando análise de lacunas...")
    
    try:
        # Inicializar detector de lacunas
        gap_detector = GapDetector(
            project_root=project_root,
            enable_nlp=enable_nlp,
            confidence_threshold=confidence_threshold
        )
        
        # Executar análise
        result = gap_detector.analyze_project()
        
        # Gerar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"gap_analysis_{timestamp}.md"
        report_content = gap_detector.generate_report(result, str(report_file))
        
        # Salvar resultado JSON
        json_file = output_dir / f"gap_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': result.metadata['analysis_timestamp'],
                'total_gaps': result.total_gaps,
                'critical_gaps': result.critical_gaps,
                'high_gaps': result.high_gaps,
                'medium_gaps': result.medium_gaps,
                'low_gaps': result.low_gaps,
                'info_gaps': result.info_gaps,
                'files_analyzed': result.files_analyzed,
                'coverage_score': result.coverage_score,
                'quality_score': result.quality_score,
                'processing_time': result.processing_time,
                'gaps': [
                    {
                        'type': gap.gap_type.value,
                        'severity': gap.severity.value,
                        'file_path': gap.file_path,
                        'line_number': gap.line_number,
                        'description': gap.description,
                        'suggestion': gap.suggestion,
                        'confidence': gap.confidence
                    }
                    for gap in result.gaps
                ]
            }, f, indent=2, ensure_ascii=False)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RESUMO DA ANÁLISE DE LACUNAS")
        print("="*60)
        print(f"📁 Projeto: {project_root}")
        print(f"📅 Data/Hora: {result.metadata['analysis_timestamp']}")
        print(f"⏱️  Tempo: {result.processing_time:.2f}s")
        print(f"📄 Arquivos analisados: {result.files_analyzed}")
        print()
        print("🚨 LACUNAS ENCONTRADAS:")
        print(f"   🔴 Críticas: {result.critical_gaps}")
        print(f"   🟠 Altas: {result.high_gaps}")
        print(f"   🟡 Médias: {result.medium_gaps}")
        print(f"   🟢 Baixas: {result.low_gaps}")
        print(f"   ⚪ Informativas: {result.info_gaps}")
        print(f"   📊 Total: {result.total_gaps}")
        print()
        print("📈 SCORES:")
        print(f"   📋 Cobertura: {result.coverage_score:.1%}")
        print(f"   🎯 Qualidade: {result.quality_score:.1%}")
        print()
        print("📁 RELATÓRIOS SALVOS:")
        print(f"   📄 Markdown: {report_file}")
        print(f"   📊 JSON: {json_file}")
        
        if verbose:
            print("\n" + "="*60)
            print("📋 LACUNAS DETALHADAS")
            print("="*60)
            
            for gap in result.gaps:
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                    'info': '⚪'
                }.get(gap.severity.value, '⚪')
                
                print(f"{severity_emoji} {gap.severity.value.upper()}: {gap.gap_type.value}")
                print(f"   📄 Arquivo: {gap.file_path}")
                if gap.line_number:
                    print(f"   📍 Linha: {gap.line_number}")
                print(f"   📝 Descrição: {gap.description}")
                print(f"   💡 Sugestão: {gap.suggestion}")
                print(f"   🎯 Confiança: {gap.confidence:.1%}")
                print()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na análise de lacunas: {e}")
        raise


def run_integrity_validation(project_root: str, output_dir: Path, verbose: bool):
    """Executa validação de integridade."""
    logger.info("🔍 Iniciando validação de integridade...")
    
    try:
        # Inicializar validador de integridade
        integrity_validator = IntegrityValidator(
            project_root=project_root,
            enable_all_validations=True
        )
        
        # Executar validação
        result = integrity_validator.validate_all()
        
        # Gerar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"integrity_validation_{timestamp}.md"
        report_content = integrity_validator.generate_report(result, str(report_file))
        
        # Salvar resultado JSON
        json_file = output_dir / f"integrity_validation_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': result.timestamp.isoformat(),
                'overall_status': result.overall_status.value,
                'total_issues': result.total_issues,
                'critical_issues': result.critical_issues,
                'high_issues': result.high_issues,
                'medium_issues': result.medium_issues,
                'low_issues': result.low_issues,
                'processing_time': result.processing_time,
                'results': [
                    {
                        'validation_type': res.validation_type.value,
                        'status': res.status.value,
                        'total_issues': res.total_issues,
                        'passed_checks': res.passed_checks,
                        'failed_checks': res.failed_checks,
                        'warnings': res.warnings,
                        'processing_time': res.processing_time,
                        'issues': [
                            {
                                'validation_type': issue.validation_type.value,
                                'status': issue.status.value,
                                'file_path': issue.file_path,
                                'line_number': issue.line_number,
                                'description': issue.description,
                                'suggestion': issue.suggestion,
                                'severity': issue.severity
                            }
                            for issue in res.issues
                        ]
                    }
                    for res in result.results
                ]
            }, f, indent=2, ensure_ascii=False)
        
        # Exibir resumo
        print("\n" + "="*60)
        print("🔍 RESUMO DA VALIDAÇÃO DE INTEGRIDADE")
        print("="*60)
        print(f"📁 Projeto: {project_root}")
        print(f"📅 Data/Hora: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Tempo: {result.processing_time:.2f}s")
        print()
        
        status_emoji = {
            'pass': '✅',
            'fail': '❌',
            'warning': '⚠️'
        }.get(result.overall_status.value, '❓')
        
        print(f"🎯 STATUS GERAL: {status_emoji} {result.overall_status.value.upper()}")
        print()
        print("🚨 ISSUES ENCONTRADOS:")
        print(f"   🔴 Críticos: {result.critical_issues}")
        print(f"   🟠 Altos: {result.high_issues}")
        print(f"   🟡 Médios: {result.medium_issues}")
        print(f"   🟢 Baixos: {result.low_issues}")
        print(f"   📊 Total: {result.total_issues}")
        print()
        print("📋 RESULTADOS POR TIPO:")
        for res in result.results:
            status_icon = "✅" if res.status.value == "pass" else "❌"
            print(f"   {status_icon} {res.validation_type.value}: {res.total_issues} issues")
        print()
        print("📁 RELATÓRIOS SALVOS:")
        print(f"   📄 Markdown: {report_file}")
        print(f"   📊 JSON: {json_file}")
        
        if verbose:
            print("\n" + "="*60)
            print("📋 ISSUES DETALHADOS")
            print("="*60)
            
            for res in result.results:
                if res.issues:
                    print(f"\n🔍 {res.validation_type.value.upper()}:")
                    for issue in res.issues:
                        severity_emoji = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(issue.severity, '⚪')
                        
                        print(f"   {severity_emoji} {issue.severity.upper()}: {issue.description}")
                        if issue.file_path:
                            print(f"      📄 Arquivo: {issue.file_path}")
                        if issue.line_number:
                            print(f"      📍 Linha: {issue.line_number}")
                        print(f"      💡 Sugestão: {issue.suggestion}")
                        print()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro na validação de integridade: {e}")
        raise


def main():
    """Função principal."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logger.setLevel('DEBUG')
    
    print("🚀 OMNİ KEYWORDS FINDER - ANÁLISE DE LACUNAS E INTEGRIDADE")
    print("="*60)
    print(f"📁 Projeto: {args.project_root}")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 NLP Habilitado: {args.enable_nlp}")
    print(f"🎯 Threshold de Confiança: {args.confidence_threshold}")
    print()
    
    try:
        # Criar diretório de saída
        output_dir = create_output_directory(args.output)
        
        # Executar análises
        gap_result = None
        integrity_result = None
        
        if not args.integrity_only:
            gap_result = run_gap_analysis(
                args.project_root,
                output_dir,
                args.enable_nlp,
                args.confidence_threshold,
                args.verbose
            )
        
        if not args.gaps_only:
            integrity_result = run_integrity_validation(
                args.project_root,
                output_dir,
                args.verbose
            )
        
        # Resumo final
        print("\n" + "="*60)
        print("🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
        if gap_result:
            print(f"📊 Lacunas encontradas: {gap_result.total_gaps}")
            print(f"🎯 Score de qualidade: {gap_result.quality_score:.1%}")
        
        if integrity_result:
            print(f"🔍 Issues de integridade: {integrity_result.total_issues}")
            print(f"✅ Status geral: {integrity_result.overall_status.value.upper()}")
        
        print(f"📁 Relatórios salvos em: {output_dir.absolute()}")
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Revisar relatórios gerados")
        print("   2. Priorizar correção de issues críticos")
        print("   3. Implementar melhorias sugeridas")
        print("   4. Executar análise novamente após correções")
        
    except KeyboardInterrupt:
        print("\n⚠️  Análise interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a análise: {e}")
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 