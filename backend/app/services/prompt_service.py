"""
Serviço especializado para manipulação de prompts.
Responsável por leitura, preenchimento e validação de prompts.

Prompt: CHECKLIST_SEGUNDA_REVISAO.md - IMP-002
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
Versão: 1.0.0
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from backend.app.utils.log_event import log_event


class PromptService:
    """
    Serviço especializado para manipulação de prompts.
    
    Responsabilidades:
    - Leitura de arquivos de prompt
    - Preenchimento de templates
    - Validação de prompts
    - Cache de prompts
    - Versionamento de prompts
    
    Princípios aplicados:
    - SRP: Apenas manipulação de prompts
    - Performance: Cache de prompts
    - Rastreabilidade: Logging detalhado
    - Configurabilidade: Templates customizáveis
    """
    
    def __init__(self, cache_enabled: bool = True, max_cache_size: int = 100):
        """
        Inicializa o serviço de prompts.
        
        Args:
            cache_enabled: Se True, ativa cache de prompts
            max_cache_size: Tamanho máximo do cache
        """
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size
        self._prompt_cache = {}
        self._template_placeholders = {
            '[PALAVRA-CHAVE]': 'palavras_chave',
            '[CLUSTER]': 'cluster',
            '[CATEGORIA]': 'categoria',
            '[DATA]': 'data',
            '[USUARIO]': 'usuario'
        }
    
    def _normalizar_caminho(self, prompt_path: str) -> str:
        """
        Normaliza o caminho do arquivo de prompt.
        
        Args:
            prompt_path: Caminho do arquivo
            
        Returns:
            Caminho normalizado
        """
        return os.path.abspath(os.path.expanduser(prompt_path))
    
    def _gerar_chave_cache(self, prompt_path: str) -> str:
        """
        Gera chave para cache baseada no caminho e timestamp.
        
        Args:
            prompt_path: Caminho do arquivo
            
        Returns:
            Chave do cache
        """
        try:
            stat = os.stat(prompt_path)
            return f"{prompt_path}_{stat.st_mtime}"
        except OSError:
            return prompt_path
    
    def _limpar_cache_se_necessario(self):
        """Limpa cache se exceder o tamanho máximo."""
        if len(self._prompt_cache) > self.max_cache_size:
            # Remove itens mais antigos (primeiros 20%)
            items_to_remove = int(self.max_cache_size * 0.2)
            keys_to_remove = list(self._prompt_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self._prompt_cache[key]
    
    def ler_prompt(self, prompt_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Lê um arquivo de prompt.
        
        Args:
            prompt_path: Caminho do arquivo de prompt
            
        Returns:
            Tupla (sucesso, erro, conteudo)
        """
        try:
            caminho_normalizado = self._normalizar_caminho(prompt_path)
            
            # Verificar cache
            if self.cache_enabled:
                chave_cache = self._gerar_chave_cache(caminho_normalizado)
                if chave_cache in self._prompt_cache:
                    return True, None, self._prompt_cache[chave_cache]
            
            # Verificar se arquivo existe
            if not os.path.exists(caminho_normalizado):
                return False, f'Arquivo de prompt não encontrado: {caminho_normalizado}', None
            
            # Verificar permissões
            if not os.access(caminho_normalizado, os.R_OK):
                return False, f'Arquivo de prompt não é legível: {caminho_normalizado}', None
            
            # Ler arquivo
            with open(caminho_normalizado, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Validar conteúdo
            if not conteudo.strip():
                return False, f'Arquivo de prompt está vazio: {caminho_normalizado}', None
            
            # Adicionar ao cache
            if self.cache_enabled:
                chave_cache = self._gerar_chave_cache(caminho_normalizado)
                self._prompt_cache[chave_cache] = conteudo
                self._limpar_cache_se_necessario()
            
            log_event('info', 'PromptService', 
                     detalhes=f'Prompt lido com sucesso: {caminho_normalizado}')
            
            return True, None, conteudo
            
        except UnicodeDecodeError as e:
            erro = f'Erro de codificação ao ler prompt: {str(e)}'
            log_event('erro', 'PromptService', 
                     detalhes=f'{erro} - {prompt_path}')
            return False, erro, None
        except Exception as e:
            erro = f'Erro ao ler prompt: {str(e)}'
            log_event('erro', 'PromptService', 
                     detalhes=f'{erro} - {prompt_path}')
            return False, erro, None
    
    def _detectar_placeholders(self, prompt: str) -> List[str]:
        """
        Detecta placeholders no prompt.
        
        Args:
            prompt: Conteúdo do prompt
            
        Returns:
            Lista de placeholders encontrados
        """
        placeholders = []
        for placeholder in self._template_placeholders.keys():
            if placeholder in prompt:
                placeholders.append(placeholder)
        return placeholders
    
    def _validar_dados_preenchimento(self, dados: Dict[str, Any], placeholders: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Valida dados para preenchimento de placeholders.
        
        Args:
            dados: Dados para preenchimento
            placeholders: Placeholders encontrados no prompt
            
        Returns:
            Tupla (valido, erro)
        """
        for placeholder in placeholders:
            campo = self._template_placeholders.get(placeholder)
            if campo and campo not in dados:
                return False, f'Campo obrigatório não fornecido: {campo}'
        
        return True, None
    
    def preencher_prompt(self, prompt: str, dados: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Preenche um prompt com dados.
        
        Args:
            prompt: Prompt template
            dados: Dados para preenchimento
            
        Returns:
            Tupla (sucesso, erro, prompt_preenchido)
        """
        try:
            # Detectar placeholders
            placeholders = self._detectar_placeholders(prompt)
            
            # Validar dados
            valido, erro = self._validar_dados_preenchimento(dados, placeholders)
            if not valido:
                return False, erro, None
            
            # Preencher prompt
            prompt_preenchido = prompt
            
            for placeholder, campo in self._template_placeholders.items():
                if placeholder in prompt_preenchido and campo in dados:
                    valor = dados[campo]
                    
                    # Tratamento especial para diferentes tipos
                    if campo == 'palavras_chave' and isinstance(valor, list):
                        valor = ', '.join(valor)
                    elif campo == 'data' and valor is None:
                        from datetime import datetime
                        valor = datetime.utcnow().strftime('%Y-%m-%data %H:%M:%S')
                    
                    prompt_preenchido = prompt_preenchido.replace(placeholder, str(valor))
            
            # Verificar se ainda há placeholders não preenchidos
            placeholders_restantes = self._detectar_placeholders(prompt_preenchido)
            if placeholders_restantes:
                return False, f'Placeholders não preenchidos: {placeholders_restantes}', None
            
            log_event('info', 'PromptService', 
                     detalhes=f'Prompt preenchido com sucesso')
            
            return True, None, prompt_preenchido
            
        except Exception as e:
            erro = f'Erro ao preencher prompt: {str(e)}'
            log_event('erro', 'PromptService', 
                     detalhes=erro)
            return False, erro, None
    
    def processar_prompt_completo(self, prompt_path: str, dados: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Processa um prompt completo (leitura + preenchimento).
        
        Args:
            prompt_path: Caminho do arquivo de prompt
            dados: Dados para preenchimento
            
        Returns:
            Tupla (sucesso, erro, prompt_preenchido)
        """
        try:
            # Ler prompt
            sucesso, erro, prompt = self.ler_prompt(prompt_path)
            if not sucesso or prompt is None:
                return False, erro, None
            
            # Preencher prompt
            sucesso, erro, prompt_preenchido = self.preencher_prompt(prompt, dados)
            if not sucesso:
                return False, erro, None
            
            return True, None, prompt_preenchido
            
        except Exception as e:
            erro = f'Erro no processamento completo do prompt: {str(e)}'
            log_event('erro', 'PromptService', 
                     detalhes=f'{erro} - {prompt_path}')
            return False, erro, None
    
    def validar_prompt(self, prompt: str) -> Tuple[bool, List[str]]:
        """
        Valida um prompt.
        
        Args:
            prompt: Conteúdo do prompt
            
        Returns:
            Tupla (valido, erros)
        """
        erros = []
        
        # Verificar se está vazio
        if not prompt or not prompt.strip():
            erros.append('Prompt está vazio')
        
        # Verificar tamanho mínimo
        if len(prompt.strip()) < 10:
            erros.append('Prompt muito curto (mínimo 10 caracteres)')
        
        # Verificar tamanho máximo
        if len(prompt) > 10000:
            erros.append('Prompt muito longo (máximo 10.000 caracteres)')
        
        # Verificar placeholders válidos
        placeholders = self._detectar_placeholders(prompt)
        placeholders_invalidos = [p for p in placeholders if p not in self._template_placeholders]
        if placeholders_invalidos:
            erros.append(f'Placeholders inválidos: {placeholders_invalidos}')
        
        # Verificar caracteres especiais problemáticos
        caracteres_problematicos = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
        for char in caracteres_problematicos:
            if char in prompt:
                erros.append(f'Caractere inválido encontrado: {repr(char)}')
        
        return len(erros) == 0, erros
    
    def obter_estatisticas_cache(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache.
        
        Returns:
            Estatísticas do cache
        """
        return {
            'cache_enabled': self.cache_enabled,
            'tamanho_atual': len(self._prompt_cache),
            'tamanho_maximo': self.max_cache_size,
            'taxa_ocupacao': len(self._prompt_cache) / self.max_cache_size if self.max_cache_size > 0 else 0
        }
    
    def limpar_cache(self) -> Dict[str, Any]:
        """
        Limpa o cache de prompts.
        
        Returns:
            Resultado da limpeza
        """
        tamanho_anterior = len(self._prompt_cache)
        self._prompt_cache.clear()
        
        log_event('info', 'PromptService', 
                 detalhes=f'Cache limpo: {tamanho_anterior} itens removidos')
        
        return {
            'itens_removidos': tamanho_anterior,
            'tamanho_atual': 0
        }
    
    def adicionar_placeholder_personalizado(self, placeholder: str, campo: str) -> bool:
        """
        Adiciona um placeholder personalizado.
        
        Args:
            placeholder: Placeholder (ex: [CUSTOM])
            campo: Campo correspondente nos dados
            
        Returns:
            True se adicionado com sucesso
        """
        try:
            if not placeholder.startswith('[') or not placeholder.endswith(']'):
                return False
            
            self._template_placeholders[placeholder] = campo
            
            log_event('info', 'PromptService', 
                     detalhes=f'Placeholder personalizado adicionado: {placeholder} -> {campo}')
            
            return True
            
        except Exception as e:
            log_event('erro', 'PromptService', 
                     detalhes=f'Erro ao adicionar placeholder personalizado: {e}')
            return False 