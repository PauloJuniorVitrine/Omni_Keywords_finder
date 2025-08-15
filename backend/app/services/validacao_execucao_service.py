"""
Serviço especializado para validação de execuções.
Responsável por validar dados de entrada e regras de negócio.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-002
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from backend.app.models import Categoria
from backend.app.utils.log_event import log_event


class ValidacaoExecucaoService:
    """
    Serviço especializado para validação de execuções.
    
    Responsabilidades:
    - Validação de dados de entrada
    - Verificação de regras de negócio
    - Validação de existência de recursos
    - Geração de mensagens de erro estruturadas
    
    Princípios aplicados:
    - SRP: Apenas validação
    - Reutilização: Validações centralizadas
    - Rastreabilidade: Logging detalhado
    - Configurabilidade: Regras customizáveis
    """
    
    def __init__(self):
        """Inicializa o serviço de validação."""
        self.regras_validacao = {
            'categoria_id': {
                'tipo': int,
                'min': 1,
                'obrigatorio': True
            },
            'palavras_chave': {
                'tipo': list,
                'min_items': 1,
                'max_tamanho_item': 100,
                'obrigatorio': True
            },
            'cluster': {
                'tipo': str,
                'max_tamanho': 255,
                'obrigatorio': False
            }
        }
    
    def validar_item_lote(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Valida um item de lote de execução.
        
        Args:
            item: Item a ser validado
            
        Returns:
            Tupla (valido, erro, dados_validados)
        """
        try:
            # Extrair dados
            categoria_id = item.get('categoria_id')
            palavras_chave = item.get('palavras_chave')
            cluster = item.get('cluster')
            
            # Validar categoria_id
            if not categoria_id:
                return False, 'categoria_id é obrigatório', {}
            
            if not isinstance(categoria_id, int) or categoria_id <= 0:
                return False, 'categoria_id deve ser inteiro positivo', {}
            
            # Validar palavras_chave
            if not isinstance(palavras_chave, list) or not palavras_chave:
                return False, 'palavras_chave deve ser lista não vazia', {}
            
            if not all(isinstance(p, str) and 1 <= len(p) <= 100 for p in palavras_chave):
                return False, 'palavras_chave deve ser lista de strings (1-100 caracteres)', {}
            
            # Validar cluster
            if cluster is not None and (not isinstance(cluster, str) or len(cluster) < 1 or len(cluster) > 255):
                return False, 'cluster deve ser string de 1 a 255 caracteres', {}
            
            dados_validados = {
                'categoria_id': categoria_id,
                'palavras_chave': palavras_chave,
                'cluster': cluster
            }
            
            return True, None, dados_validados
            
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro na validação de item: {e}')
            return False, f'Erro interno na validação: {str(e)}', {}
    
    def validar_categoria_existe(self, categoria_id: int) -> Tuple[bool, Optional[str], Optional[Categoria]]:
        """
        Valida se a categoria existe.
        
        Args:
            categoria_id: ID da categoria
            
        Returns:
            Tupla (existe, erro, categoria)
        """
        try:
            categoria = Categoria.query.get(categoria_id)
            
            if not categoria:
                return False, f'Categoria {categoria_id} não encontrada', None
            
            return True, None, categoria
            
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro ao validar categoria {categoria_id}: {e}')
            return False, f'Erro interno ao validar categoria: {str(e)}', None
    
    def validar_arquivo_prompt(self, prompt_path: str) -> Tuple[bool, Optional[str]]:
        """
        Valida se o arquivo de prompt existe e é legível.
        
        Args:
            prompt_path: Caminho do arquivo de prompt
            
        Returns:
            Tupla (valido, erro)
        """
        try:
            import os
            
            if not os.path.exists(prompt_path):
                return False, f'Arquivo de prompt não encontrado: {prompt_path}'
            
            if not os.access(prompt_path, os.R_OK):
                return False, f'Arquivo de prompt não é legível: {prompt_path}'
            
            # Tentar ler o arquivo
            with open(prompt_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            if not conteudo.strip():
                return False, f'Arquivo de prompt está vazio: {prompt_path}'
            
            return True, None
            
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro ao validar arquivo de prompt {prompt_path}: {e}')
            return False, f'Erro interno ao validar arquivo de prompt: {str(e)}'
    
    def validar_palavras_chave_json(self, palavras_chave_json: str) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Valida se o JSON de palavras-chave é válido.
        
        Args:
            palavras_chave_json: JSON serializado de palavras-chave
            
        Returns:
            Tupla (valido, erro, palavras_chave)
        """
        try:
            palavras_chave = json.loads(palavras_chave_json)
            
            if not isinstance(palavras_chave, list):
                return False, 'palavras_chave deve ser uma lista', None
            
            if not palavras_chave:
                return False, 'palavras_chave não pode ser vazia', None
            
            if not all(isinstance(p, str) for p in palavras_chave):
                return False, 'palavras_chave deve conter apenas strings', None
            
            return True, None, palavras_chave
            
        except json.JSONDecodeError as e:
            return False, f'JSON de palavras-chave inválido: {str(e)}', None
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro ao validar JSON de palavras-chave: {e}')
            return False, f'Erro interno ao validar JSON: {str(e)}', None
    
    def validar_data_agendamento(self, data_agendada: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Valida se a data de agendamento é válida.
        
        Args:
            data_agendada: Data de agendamento em formato ISO
            
        Returns:
            Tupla (valido, erro, data_formatada)
        """
        try:
            from datetime import datetime
            
            data = datetime.fromisoformat(data_agendada.replace('Z', '+00:00'))
            agora = datetime.utcnow()
            
            if data <= agora:
                return False, 'Data de agendamento deve ser futura', None
            
            return True, None, data.isoformat()
            
        except ValueError as e:
            return False, f'Formato de data inválido: {str(e)}', None
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro ao validar data de agendamento: {e}')
            return False, f'Erro interno ao validar data: {str(e)}', None
    
    def validar_execucao_completa(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validação completa de um item de execução.
        
        Args:
            item: Item a ser validado
            
        Returns:
            Tupla (valido, erro, dados_validados)
        """
        try:
            # Validação básica
            valido, erro, dados_basicos = self.validar_item_lote(item)
            if not valido:
                return False, erro, {}
            
            categoria_id = dados_basicos['categoria_id']
            
            # Validar existência da categoria
            categoria_existe, erro_categoria, categoria = self.validar_categoria_existe(categoria_id)
            if not categoria_existe:
                return False, erro_categoria, {}
            
            # Validar arquivo de prompt
            prompt_valido, erro_prompt = self.validar_arquivo_prompt(categoria.prompt_path)
            if not prompt_valido:
                return False, erro_prompt, {}
            
            dados_validados = {
                **dados_basicos,
                'categoria': categoria,
                'prompt_path': categoria.prompt_path
            }
            
            return True, None, dados_validados
            
        except Exception as e:
            log_event('erro', 'ValidacaoExecucao', 
                     detalhes=f'Erro na validação completa: {e}')
            return False, f'Erro interno na validação completa: {str(e)}', {}
    
    def validar_lote_completo(self, dados: List[Dict[str, Any]]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
        """
        Valida um lote completo de execuções.
        
        Args:
            dados: Lista de itens a serem validados
            
        Returns:
            Tupla (valido, erros, dados_validados)
        """
        if not isinstance(dados, list):
            return False, ['O payload deve ser uma lista'], []
        
        if not dados:
            return False, ['A lista de execuções não pode estar vazia'], []
        
        erros = []
        dados_validados = []
        
        for index, item in enumerate(dados):
            if not isinstance(item, dict):
                erros.append(f'Item {index}: deve ser um dicionário')
                continue
            
            valido, erro, dados_item = self.validar_execucao_completa(item)
            if not valido:
                erros.append(f'Item {index}: {erro}')
            else:
                dados_validados.append(dados_item)
        
        return len(erros) == 0, erros, dados_validados
    
    def gerar_relatorio_validacao(self, total_items: int, erros: List[str], 
                                 dados_validados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera relatório de validação.
        
        Args:
            total_items: Total de itens processados
            erros: Lista de erros encontrados
            dados_validados: Dados que passaram na validação
            
        Returns:
            Relatório de validação
        """
        return {
            'total_items': total_items,
            'total_erros': len(erros),
            'total_validados': len(dados_validados),
            'taxa_sucesso': len(dados_validados) / total_items if total_items > 0 else 0,
            'erros': erros,
            'timestamp': datetime.utcnow().isoformat()
        } 