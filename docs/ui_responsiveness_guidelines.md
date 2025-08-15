# Guia de Responsividade — Omni Keywords Finder

## Padrões Obrigatórios

- Todos os layouts devem ser mobile-first, adaptando-se a telas de 320px até 1280px+.
- Utilize breakpoints centralizados do tema (`/ui/theme/breakpoints.ts`).
- Grids e flexbox devem ser preferidos para organização de elementos.
- Fontes e espaçamentos devem ser responsivos.
- Elementos interativos devem ser acessíveis e legíveis em telas pequenas.
- Teste em dispositivos reais e simulados.

## Exemplos

```tsx
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    padding: 16,
    [`@media (min-width: ${breakpoints.tablet}px)`]: {
      flexDirection: 'row',
      padding: 32,
    },
  },
};
```

## Recomendações

- Use unidades relativas (`em`, `rem`, `%`) para tamanhos e espaçamentos.
- Oculte ou adapte elementos não essenciais em telas pequenas.
- Teste navegação e usabilidade em mobile antes de cada release.
- Automatize testes de responsividade (Cypress, Playwright).
- Documente padrões e revise periodicamente.

---

*Este guia deve ser seguido e atualizado a cada nova feature ou refatoração visual.* 