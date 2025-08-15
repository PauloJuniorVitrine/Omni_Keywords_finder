"""
Módulo de geração de prompts base para clusters e palavras-chave.
Responsável por substituir placeholders em templates com dados validados.
"""
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from domain.models import Keyword, Cluster
from shared.logger import logger
from datetime import datetime
import re
from string import Template
import os
import json
from shared.config import ProcessingConfig

class GeradorPrompt:
    """
    Gera prompts a partir de templates e dados validados (keywords, clusters).
    Suporta múltiplos formatos, placeholders customizados, validação, relatório e callback.
    """
    def __init__(
        self,
        template: Optional[str] = None,
        template_path: Optional[str] = None,
        separador_secundarias: str = ", ",
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Inicializa o gerador de prompt.
        Args:
            template: string do template base
            template_path: caminho para arquivo de template (opcional)
            separador_secundarias: separador para keywords secundárias
            callback: função chamada após geração
        """
        if template_path:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template não encontrado: {template_path}")
            with open(template_path, encoding="utf-8") as f:
                self.template = f.read()
        elif template:
            self.template = template
        else:
            raise ValueError("É obrigatório fornecer template ou template_path.")
        self.separador_secundarias = separador_secundarias
        self.callback = callback

    def _formatar_lista(self, itens: List[Any], formato: Optional[str] = None) -> str:
        """
        Formata uma lista para inserção no prompt.
        Args:
            itens: lista de strings ou objetos
            formato: 'numerada', 'tabela', None
        Returns:
            String formatada
        """
        if not itens:
            return ""
        if formato == "numerada":
            return "\n".join([f"{index+1}. {str(it)}" for index, it in enumerate(itens)])
        if formato == "tabela":
            return "\n".join(["| " + str(it) + " |" for it in itens])
        return self.separador_secundarias.join([str(it) for it in itens])

    def _placeholders_nao_substituidos(self, prompt: str) -> List[str]:
        return re.findall(r"{([^}]+)}", prompt)

    def gerar_prompt(
        self,
        primary_keyword: Keyword,
        secondary_keywords: List[Keyword],
        cluster: Optional[Cluster] = None,
        extras: Optional[Dict[str, Any]] = None,
        formato_secundarias: Optional[str] = None,
        relatorio: bool = False
    ) -> Union[str, Tuple[str, Dict[str, Any]]]:
        """
        Gera prompt substituindo placeholders do template.
        Placeholders suportados: {primary_keyword}, {secondary_keyword}, {secondary_keywords}, {cluster}, {extras}
        Args:
            primary_keyword: keyword principal (obrigatório)
            secondary_keywords: lista de keywords secundárias
            cluster: cluster relacionado (opcional)
            extras: dicionário de dados extras (opcional)
            formato_secundarias: 'numerada', 'tabela', None
            relatorio: se True, retorna relatório de substituição
        Returns:
            String do prompt gerado ou (prompt, relatório)
        """
        if not primary_keyword or not isinstance(primary_keyword, Keyword):
            raise ValueError("primary_keyword é obrigatório e deve ser Keyword.")
        if secondary_keywords is None:
            secondary_keywords = []
        valores = {
            "primary_keyword": primary_keyword.termo,
            "secondary_keyword": secondary_keywords[0].termo if secondary_keywords else "",
            "secondary_keywords": self._formatar_lista([key.termo for key in secondary_keywords], formato_secundarias),
            "cluster": cluster.id if cluster else ""
        }
        if extras:
            for key, value in extras.items():
                valores[key] = value
        # Log temporário para diagnóstico
        print(f"[DEBUG] valores usados na substituição do template: {valores}")
        # Renderização segura
        template = Template(self.template)
        try:
            prompt = template.safe_substitute(valores)
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "erro_geracao_prompt",
                "status": "error",
                "source": "gerador_prompt.gerar_prompt",
                "details": {"erro": str(e), "valores": valores}
            })
            raise
        # Substituição de extras não utilizados por vazio
        prompt = re.sub(r"{[^}]+}", "", prompt)
        placeholders_restantes = self._placeholders_nao_substituidos(prompt)
        relatorio_dict = {
            "primary_keyword": primary_keyword.termo,
            "secondary_keywords": [key.termo for key in secondary_keywords],
            "cluster": cluster.id if cluster else None,
            "extras": extras,
            "placeholders_nao_substituidos": placeholders_restantes,
            "prompt_final": prompt
        }
        if placeholders_restantes:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "placeholders_nao_substituidos",
                "status": "warning",
                "source": "gerador_prompt.gerar_prompt",
                "details": {"placeholders": placeholders_restantes, "template": self.template}
            })
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "geracao_prompt",
            "status": "success",
            "source": "gerador_prompt.gerar_prompt",
            "details": relatorio_dict
        })
        if self.callback:
            self.callback(relatorio_dict)
        if relatorio:
            prompt_out = prompt
        else:
            prompt_out = prompt
        # --- Bloco JSON e Checklist ---
        checklist = {
            "cta_incluido": bool(re.search(r'CTA|call to action|chamada para ação', prompt, re.IGNORECASE)),
            "densidade_keyword": round(prompt.lower().count(primary_keyword.termo.lower()) / max(1, len(prompt.split())), 4),
            "uso_h2": bool(re.search(r'<h2>|^## ', prompt, re.MULTILINE)),
            "uso_h3": bool(re.search(r'<h3>|^### ', prompt, re.MULTILINE)),
            "faq_incluido": bool(re.search(r'faq|perguntas frequentes', prompt, re.IGNORECASE)),
            "fase_funil_conectada": hasattr(primary_keyword, 'fase_funil') and primary_keyword.fase_funil in prompt
        }
        aqr = self._validar_aqr(prompt, primary_keyword, repeticao_max=getattr(ProcessingConfig, 'KEYWORD_DENSITY', 0.1))
        resumo = {
            "termo_principal": primary_keyword.termo,
            "intencao": str(getattr(primary_keyword, 'intencao', '')),
            "fase_funil": getattr(primary_keyword, 'fase_funil', ''),
            "racional_escolha": getattr(primary_keyword, 'justificativa', ''),
            "checklist": checklist,
            "aqr": aqr
        }
        prompt_out += f"\n\n---\nResumo e Checklist:\n{json.dumps(resumo, ensure_ascii=False, indent=2)}\n"
        # Logging do bloco extra
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "resumo_checklist_prompt",
            "status": "success",
            "source": "gerador_prompt.gerar_prompt",
            "details": resumo
        })
        if relatorio:
            return prompt_out, relatorio_dict
        return prompt_out

    def _validar_aqr(self, prompt: str, primary_keyword: Keyword, repeticao_max: float = None) -> dict:
        """
        Valida o prompt gerado segundo critérios AQR:
        - Accuracy: termo principal e intenção presentes, contexto aderente
        - Quality: presença de H1, H2, H3, meta (no início), introdução, conclusão, CTA, FAQ (>=8)
        - Reliability: ausência de repetições excessivas (configurável), contradições básicas (dicionário expandido)
        - Score AQR: média dos critérios (0-1)
        Retorna dicionário com resultado, score e observações.
        """
        obs = []
        # Configuração de repetição máxima
        if repeticao_max is None:
            repeticao_max = 0.1  # 10% do texto
        # Accuracy
        accuracy = primary_keyword.termo.lower() in prompt.lower()
        if not accuracy:
            obs.append("Termo principal não encontrado no texto.")
        intencao = getattr(primary_keyword, 'intencao', '').lower()
        accuracy_intencao = False
        if intencao:
            if intencao == 'comercial':
                accuracy_intencao = any(value in prompt.lower() for value in ['comprar', 'preço', 'oferta', 'promoção', 'desconto'])
            elif intencao == 'informacional':
                accuracy_intencao = any(value in prompt.lower() for value in ['como', 'o que', 'guia', 'explicação', 'passo a passo'])
            elif intencao == 'navegacional':
                accuracy_intencao = any(value in prompt.lower() for value in ['site oficial', 'acessar', 'login', 'entrar'])
            elif intencao == 'transacional':
                accuracy_intencao = any(value in prompt.lower() for value in ['assinar', 'contratar', 'comprar', 'adquirir'])
            else:
                accuracy_intencao = intencao in prompt.lower()
        if not accuracy_intencao:
            obs.append("Intenção não aderente ao texto.")
        # Quality
        quality_checks = [
            bool(re.search(r'<h1>|^# ', prompt, re.MULTILINE)),
            bool(re.search(r'<h2>|^## ', prompt, re.MULTILINE)),
            bool(re.search(r'<h3>|^### ', prompt, re.MULTILINE)),
            bool(re.search(r'meta descri[cç][aã]o', prompt[:500], re.IGNORECASE)),
            bool(re.search(r'introdu[cç][aã]o', prompt[:1000], re.IGNORECASE)),
            bool(re.search(r'conclus[aã]o|considera[cç][aã]o final', prompt[-1000:], re.IGNORECASE)),
            bool(re.search(r'CTA|call to action|chamada para ação', prompt, re.IGNORECASE)),
        ]
        quality = all(quality_checks)
        if not quality:
            obs.append("Estrutura editorial incompleta (H1, H2, H3, meta, introdução, conclusão, CTA).")
        # FAQ
        faqs = re.findall(r'(faq|perguntas frequentes)', prompt, re.IGNORECASE)
        faq_ok = len(faqs) >= 8
        if not faq_ok:
            obs.append("Menos de 8 FAQs encontradas.")
        # Reliability
        repeticoes = prompt.lower().count(primary_keyword.termo.lower())
        densidade = repeticoes / max(1, len(prompt.split()))
        reliability = densidade < repeticao_max
        if not reliability:
            obs.append("Repetição excessiva do termo principal.")
        contradicoes = [
            'contradiz', 'inconsistente', 'erro', 'não faz sentido', 'incoerente', 'confuso', 'ambíguo', 'contradição', 'conflito', 'paradoxo'
        ]
        contradicao = any(value in prompt.lower() for value in contradicoes)
        if contradicao:
            obs.append("Possível contradição textual detectada.")
        # Score AQR
        score = sum([
            accuracy,
            accuracy_intencao,
            quality,
            faq_ok,
            reliability and not contradicao
        ]) / 5.0
        return {
            "accuracy": accuracy and accuracy_intencao,
            "quality": quality and faq_ok,
            "reliability": reliability and not contradicao,
            "score_aqr": round(score, 2),
            "observacoes": obs
        } 