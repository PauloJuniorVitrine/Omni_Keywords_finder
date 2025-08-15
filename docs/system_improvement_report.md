## IMP-001 Refatoração de Pipelines e Handlers
- Diretório: ./infrastructure/processamento/
- Tipo: refatoração / modularização
- Descrição técnica: Extração dos handlers Normalizador, Limpeza, Validação e Enriquecimento para módulos independentes, com docstrings e comentários.
- Justificativa: Reduzir acoplamento, facilitar manutenção, garantir SRP e modularidade.
- Status: 🔶 pendente de testes

## IMP-002 Padronização de Interfaces Públicas
- Diretório: ./domain/
- Tipo: refatoração / limpeza
- Descrição técnica: Uniformização das assinaturas e comportamento dos métodos to_dict e from_dict em todas as entidades do domínio.
- Justificativa: Garantir consistência intermodular e facilitar serialização/deserialização.
- Status: 🔶 pendente de testes

## IMP-003 Centralização de Lógica de Normalização e Validação
- Diretório: ./shared/
- Tipo: refatoração / limpeza
- Descrição técnica: Criação do módulo shared/keyword_utils.py para centralizar funções de normalização e validação de keywords.
- Justificativa: Eliminar código duplicado, facilitar manutenção e evolução.
- Status: 🔶 pendente de testes

## IMP-004 Documentação Inline e Docstrings
- Diretório: múltiplos
- Tipo: limpeza / documentação
- Descrição técnica: Inclusão de docstrings e comentários explicativos em handlers, utilitários e pontos críticos do pipeline.
- Justificativa: Melhorar legibilidade, onboarding e rastreabilidade.
- Status: 🔶 pendente de testes

## IMP-005 Fortalecimento de Segurança em Uploads e Entradas
- Diretório: ./app/components/governanca/
- Tipo: segurança / correção
- Descrição técnica: Reforço de validação de arquivos e entradas do usuário no upload de regras (tipo, tamanho, sanitização, mensagens de erro).
- Justificativa: Mitigar riscos de segurança e garantir robustez.
- Status: 🔶 pendente de testes

## IMP-006 Limitação de Concorrência e Uso de Recursos
- Diretório: ./infrastructure/processamento/
- Tipo: refatoração / performance
- Descrição técnica: Implementação de controle explícito de concorrência em pipelines paralelos, limitando número de workers/threads.
- Justificativa: Melhorar performance e estabilidade sob carga.
- Status: 🔶 pendente de testes

## IMP-007 Padronização de Nomenclatura e Legibilidade
- Diretório: múltiplos
- Tipo: limpeza / refatoração
- Descrição técnica: Renomeação de variáveis, funções e argumentos pouco descritivos para nomes claros e autoexplicativos.
- Justificativa: Aumentar clareza e aderência ao padrão CoCoT.
- Status: 🔶 pendente de testes

## IMP-008 Redução de Tamanho de Arquivos Excedentes
- Diretório: ./infrastructure/processamento/
- Tipo: modularização / refatoração
- Descrição técnica: Divisão de arquivos com mais de 300 linhas em módulos menores e coesos.
- Justificativa: Facilitar manutenção, revisão e testes.
- Status: 🔶 pendente de testes

## IMP-009 Padronização de Interfaces Públicas de Coletores
- Diretório: ./infrastructure/coleta/
- Tipo: refatoração / limpeza
- Descrição técnica: Uniformização de métodos e assinaturas dos coletores, garantindo interface clara e estável.
- Justificativa: Facilitar extensão e integração de novos coletores.
- Status: 🔶 pendente de testes

## IFACE-001 Validação Estrutural de Regras no Editor Inline
- Diretório: ./app/components/governanca/
- Tipo: validação / robustez
- Descrição técnica: Implementação de validação da estrutura esperada das regras (score_minimo, blacklist, whitelist) no upload e editor inline.
- Justificativa: Prevenir uploads de regras malformadas e garantir integridade dos dados enviados ao backend.
- Status: 🔶 pendente de testes

## IFACE-002 Aprimoramento de Acessibilidade (A11y)
- Diretório: ./app/components/governanca/
- Tipo: acessibilidade / usabilidade
- Descrição técnica: Inclusão de atributos ARIA, roles e navegação por teclado nos campos e botões do componente, além de contraste mínimo.
- Justificativa: Tornar a interface acessível para todos os usuários, incluindo PCD.
- Status: 🔶 pendente de testes

## IFACE-003 Feedback Visual em Uploads e Operações Assíncronas
- Diretório: ./app/components/governanca/
- Tipo: UX / usabilidade
- Descrição técnica: Inclusão de spinner durante upload de arquivo e carregamento de regras.
- Justificativa: Melhorar experiência do usuário, tornando operações longas mais transparentes.
- Status: 🔶 pendente de testes

## IFACE-004 Padronização Visual com Design System
- Diretório: ./app/components/governanca/
- Tipo: refatoração / UX
- Descrição técnica: Preparação do componente para futura adoção de design system ou biblioteca de UI.
- Justificativa: Garantir consistência visual e facilitar manutenção.
- Status: 🔶 pendente de testes

## IFACE-005 Internacionalização (i18n) da Interface
- Diretório: ./app/components/governanca/
- Tipo: internacionalização / escalabilidade
- Descrição técnica: Extração de textos fixos para objeto de tradução e uso de função t().
- Justificativa: Facilitar adaptação para outros idiomas e ampliar acessibilidade global.
- Status: �� pendente de testes 