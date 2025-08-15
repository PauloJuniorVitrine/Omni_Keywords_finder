# Guia de Microalívios e UX Progressiva — Omni Keywords Finder

## Padrões Obrigatórios

- Divida formulários longos em etapas progressivas (stepper).
- Adicione tooltips explicativos em ícones, botões e campos críticos.
- Use placeholders claros em todos os inputs.
- Implemente microanimações em botões (hover, loading, sucesso).
- Aplique fade-in/out em modais, toasts e cards.
- Exiba progresso visual em fluxos multi-etapas.
- Agrupe ações relacionadas em menus contextuais ou dropdowns.
- Oculte opções irrelevantes conforme permissão do usuário.

## Exemplos

```tsx
// Exemplo de Stepper
<Stepper steps={['Dados', 'Permissões', 'Confirmação']} currentStep={1} />

// Exemplo de Tooltip
<Tooltip content="Exporta keywords em CSV"><Button>Exportar CSV</Button></Tooltip>

// Exemplo de microanimação
<Button loading={isLoading}>Salvar</Button>

// Exemplo de agrupamento
<Dropdown actions={[{label: 'Editar'}, {label: 'Remover'}]} />
```

## Recomendações

- Prefira feedbacks visuais imediatos e discretos.
- Use animações suaves para não distrair o usuário.
- Teste a navegação e clareza dos fluxos com usuários reais.
- Documente padrões e revise periodicamente.

---

*Este guia deve ser seguido e atualizado a cada nova feature ou refatoração de UX.* 