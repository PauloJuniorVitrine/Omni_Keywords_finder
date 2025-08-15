# Guia de Acessibilidade — Omni Keywords Finder

## Padrões Obrigatórios

- Todos os elementos interativos devem possuir `aria-label` descritivo.
- Utilize `role` apropriado para modais, alertas, listas, regiões e botões.
- Garanta navegação por teclado (`tabIndex={0}`) em todos os fluxos.
- Mensagens de feedback (erro, sucesso, alerta) devem usar `role="alert"` ou `aria-live`.
- Contraste mínimo AA/AAA (WCAG 2.1) para textos, botões e badges.
- Inputs e formulários devem ter labels visíveis e associadas.
- Modais devem ser focáveis e acessíveis por teclado.
- Elementos de status devem usar `aria-live` para feedback dinâmico.

## Exemplos

```tsx
<button aria-label="Exportar CSV" tabIndex={0}>Exportar</button>
<div role="alert" aria-live="assertive">Erro ao salvar</div>
<input aria-label="Buscar keyword" />
<section aria-labelledby="dashboard-title">
  <h1 id="dashboard-title" tabIndex={0}>Dashboard</h1>
</section>
```

## Recomendações

- Teste navegação por teclado em todos os fluxos.
- Use ferramentas como axe, Lighthouse ou Playwright para validar acessibilidade.
- Prefira cores do tema para garantir contraste.
- Forneça feedback visual e sonoro para ações críticas.
- Documente padrões e revise periodicamente.

---

*Este guia deve ser seguido e atualizado a cada nova feature ou refatoração visual.* 