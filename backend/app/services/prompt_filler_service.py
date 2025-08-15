"""
Serviço para Preenchimento de Lacunas em Prompts
"""

import re
import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.prompt_system import (
    PromptBase, DadosColetados, PromptPreenchido, LogOperacao
)


class PromptFillerService:
    """Serviço para preenchimento automático de lacunas em prompts"""
    
    # Placeholders que devem ser substituídos
    PLACEHOLDERS = {
        'primary_keyword': r'\[PALAVRA-CHAVE PRINCIPAL DO CLUSTER\]',
        'secondary_keywords': r'\[PALAVRAS-CHAVE SECUNDÁRIAS\]',
        'cluster_content': r'\[CLUSTER DE CONTEÚDO\]'
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def detectar_lacunas(self, conteudo: str) -> Dict[str, List[str]]:
        """
        Detecta lacunas no conteúdo do prompt
        
        Args:
            conteudo: Conteúdo do prompt base
            
        Returns:
            Dict com lacunas encontradas por tipo
        """
        lacunas = {}
        
        for placeholder_type, pattern in self.PLACEHOLDERS.items():
            matches = re.findall(pattern, conteudo)
            if matches:
                lacunas[placeholder_type] = matches
        
        return lacunas
    
    def validar_dados_coletados(self, dados: DadosColetados) -> Tuple[bool, List[str]]:
        """
        Valida dados coletados antes do preenchimento
        
        Args:
            dados: Dados coletados para validação
            
        Returns:
            Tuple (válido, lista de erros)
        """
        erros = []
        
        # Validação de primary_keyword
        if not dados.primary_keyword or len(dados.primary_keyword.strip()) == 0:
            erros.append("Palavra-chave principal é obrigatória")
        elif len(dados.primary_keyword) > 255:
            erros.append("Palavra-chave principal deve ter no máximo 255 caracteres")
        
        # Validação de cluster_content
        if not dados.cluster_content or len(dados.cluster_content.strip()) == 0:
            erros.append("Cluster de conteúdo é obrigatório")
        elif len(dados.cluster_content) > 2000:
            erros.append("Cluster de conteúdo deve ter no máximo 2000 caracteres")
        
        # Validação de secondary_keywords (opcional)
        if dados.secondary_keywords and len(dados.secondary_keywords) > 1000:
            erros.append("Palavras-chave secundárias devem ter no máximo 1000 caracteres")
        
        return len(erros) == 0, erros
    
    def preencher_lacunas(self, prompt_base: PromptBase, dados: DadosColetados) -> Tuple[str, Dict]:
        """
        Preenche lacunas no prompt base com dados coletados
        
        Args:
            prompt_base: Prompt base com lacunas
            dados: Dados coletados para preenchimento
            
        Returns:
            Tuple (prompt preenchido, metadados do preenchimento)
        """
        inicio_processamento = time.time()
        
        # Validar dados
        dados_validos, erros = self.validar_dados_coletados(dados)
        if not dados_validos:
            raise HTTPException(status_code=400, detail=f"Dados inválidos: {', '.join(erros)}")
        
        # Detectar lacunas
        lacunas_detectadas = self.detectar_lacunas(prompt_base.conteudo)
        
        # Iniciar preenchimento
        prompt_preenchido = prompt_base.conteudo
        lacunas_preenchidas = {}
        
        # Substituir primary_keyword
        if 'primary_keyword' in lacunas_detectadas:
            prompt_preenchido = re.sub(
                self.PLACEHOLDERS['primary_keyword'],
                dados.primary_keyword,
                prompt_preenchido
            )
            lacunas_preenchidas['primary_keyword'] = {
                'original': '[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]',
                'substituido_por': dados.primary_keyword,
                'quantidade': len(lacunas_detectadas['primary_keyword'])
            }
        
        # Substituir secondary_keywords
        if 'secondary_keywords' in lacunas_detectadas:
            secondary_keywords = dados.secondary_keywords or ""
            prompt_preenchido = re.sub(
                self.PLACEHOLDERS['secondary_keywords'],
                secondary_keywords,
                prompt_preenchido
            )
            lacunas_preenchidas['secondary_keywords'] = {
                'original': '[PALAVRAS-CHAVE SECUNDÁRIAS]',
                'substituido_por': secondary_keywords,
                'quantidade': len(lacunas_detectadas['secondary_keywords'])
            }
        
        # Substituir cluster_content
        if 'cluster_content' in lacunas_detectadas:
            prompt_preenchido = re.sub(
                self.PLACEHOLDERS['cluster_content'],
                dados.cluster_content,
                prompt_preenchido
            )
            lacunas_preenchidas['cluster_content'] = {
                'original': '[CLUSTER DE CONTEÚDO]',
                'substituido_por': dados.cluster_content,
                'quantidade': len(lacunas_detectadas['cluster_content'])
            }
        
        # Calcular tempo de processamento
        tempo_processamento = int((time.time() - inicio_processamento) * 1000)
        
        # Preparar metadados
        metadados = {
            'lacunas_detectadas': lacunas_detectadas,
            'lacunas_preenchidas': lacunas_preenchidas,
            'tempo_processamento': tempo_processamento,
            'hash_original': prompt_base.hash_conteudo,
            'hash_preenchido': hashlib.sha256(prompt_preenchido.encode()).hexdigest()
        }
        
        return prompt_preenchido, metadados
    
    def processar_preenchimento(self, categoria_id: int, dados_id: int) -> PromptPreenchido:
        """
        Processa preenchimento completo de um prompt
        
        Args:
            categoria_id: ID da categoria
            dados_id: ID dos dados coletados
            
        Returns:
            PromptPreenchido criado
        """
        # Buscar prompt base e dados
        prompt_base = self.db.query(PromptBase).filter(
            PromptBase.categoria_id == categoria_id
        ).first()
        
        if not prompt_base:
            raise HTTPException(status_code=404, detail="Prompt base não encontrado")
        
        dados = self.db.query(DadosColetados).filter(
            DadosColetados.id == dados_id
        ).first()
        
        if not dados:
            raise HTTPException(status_code=404, detail="Dados coletados não encontrados")
        
        # Verificar se já existe preenchimento
        prompt_existente = self.db.query(PromptPreenchido).filter(
            PromptPreenchido.dados_coletados_id == dados_id,
            PromptPreenchido.prompt_base_id == prompt_base.id
        ).first()
        
        if prompt_existente:
            # Atualizar preenchimento existente
            prompt_preenchido, metadados = self.preencher_lacunas(prompt_base, dados)
            
            prompt_existente.prompt_preenchido = prompt_preenchido
            prompt_existente.lacunas_detectadas = json.dumps(metadados['lacunas_detectadas'])
            prompt_existente.lacunas_preenchidas = json.dumps(metadados['lacunas_preenchidas'])
            prompt_existente.tempo_processamento = metadados['tempo_processamento']
            prompt_existente.status = 'pronto'
            prompt_existente.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Log da operação
            self._log_operacao('update', 'prompt_preenchido', prompt_existente.id, {
                'categoria_id': categoria_id,
                'dados_id': dados_id,
                'tempo_processamento': metadados['tempo_processamento']
            })
            
            return prompt_existente
        
        # Criar novo preenchimento
        prompt_preenchido, metadados = self.preencher_lacunas(prompt_base, dados)
        
        novo_prompt = PromptPreenchido(
            dados_coletados_id=dados_id,
            prompt_base_id=prompt_base.id,
            prompt_original=prompt_base.conteudo,
            prompt_preenchido=prompt_preenchido,
            lacunas_detectadas=json.dumps(metadados['lacunas_detectadas']),
            lacunas_preenchidas=json.dumps(metadados['lacunas_preenchidas']),
            status='pronto',
            tempo_processamento=metadados['tempo_processamento']
        )
        
        self.db.add(novo_prompt)
        self.db.commit()
        self.db.refresh(novo_prompt)
        
        # Log da operação
        self._log_operacao('create', 'prompt_preenchido', novo_prompt.id, {
            'categoria_id': categoria_id,
            'dados_id': dados_id,
            'tempo_processamento': metadados['tempo_processamento']
        })
        
        return novo_prompt
    
    def processar_lote(self, nicho_id: int) -> List[PromptPreenchido]:
        """
        Processa preenchimento em lote para um nicho
        
        Args:
            nicho_id: ID do nicho
            
        Returns:
            Lista de prompts preenchidos
        """
        # Buscar todas as categorias do nicho com dados coletados
        categorias_com_dados = self.db.query(DadosColetados).filter(
            DadosColetados.nicho_id == nicho_id,
            DadosColetados.status == 'ativo'
        ).all()
        
        resultados = []
        
        for dados in categorias_com_dados:
            try:
                prompt_preenchido = self.processar_preenchimento(
                    dados.categoria_id, dados.id
                )
                resultados.append(prompt_preenchido)
            except Exception as e:
                # Log do erro
                self._log_operacao('error', 'prompt_preenchido', None, {
                    'categoria_id': dados.categoria_id,
                    'dados_id': dados.id,
                    'erro': str(e)
                })
        
        return resultados
    
    def _log_operacao(self, tipo: str, entidade: str, entidade_id: Optional[int], detalhes: Dict):
        """
        Registra log de operação
        
        Args:
            tipo: Tipo da operação
            entidade: Nome da entidade
            entidade_id: ID da entidade
            detalhes: Detalhes da operação
        """
        log = LogOperacao(
            tipo_operacao=tipo,
            entidade=entidade,
            entidade_id=entidade_id,
            detalhes=json.dumps(detalhes),
            status='sucesso' if tipo != 'error' else 'erro'
        )
        
        self.db.add(log)
        self.db.commit() 