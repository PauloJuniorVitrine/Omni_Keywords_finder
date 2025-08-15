# Integração Storybook — Omni Keywords Finder (v1)

## 1. Como Rodar o Storybook

```bash
cd app
npx storybook dev -p 6006
```

## 2. Estrutura de Stories
- Stories localizados em `stories/`
- Cada componente possui um arquivo `.stories.mdx` com exemplos, props e referência visual
- Stories cobrem: DashboardCard, ActionButton, Loader, Badge, ModalConfirm

## 3. Expansão e Customização
- Adicione novos stories em `stories/` seguindo o padrão MDX
- Utilize os wireframes (`wireframes_dashboard.svg`, `wireframes_governanca.svg`) como referência visual
- Consulte `interface_proposta_v1.md` para metadados de animação, layer e estados

## 4. Mapeamento Visual
- Cada story deve corresponder a um elemento ou fluxo dos wireframes
- Utilize variantes para simular estados (erro, loading, sucesso)
- Adicione documentação inline para props e exemplos de uso

## 5. Observações
- O Storybook pode ser integrado ao pipeline CI/CD para validação visual
- Recomenda-se revisão visual a cada alteração de componente 