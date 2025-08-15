# Identidade Visual e Branding — Omni Keywords Finder

## Padrões Obrigatórios

- Logotipo presente no topo da interface (componente <Branding />).
- Nome do sistema exibido no header e no <title> da página.
- Paleta de cores centralizada em `/ui/theme/colors.ts`.
- Tipografia padronizada em `/ui/theme/typography.ts`.
- Sombreamento e espaçamentos definidos em `/ui/theme/shadows.ts`.
- Favicon customizado (ou placeholder).

## Exemplos

```tsx
import Branding from '../components/branding/Branding';

<header>
  <Branding />
</header>
```

## Recomendações

- Utilize sempre tokens do tema para cores, fontes e sombras.
- Atualize o logotipo em `/static/image/logo.svg` para refletir a identidade da marca.
- Garanta contraste e legibilidade em todos os estados visuais.
- Mantenha o nome do sistema sincronizado entre header, <title> e documentação.
- Documente qualquer alteração visual relevante.

## Status Atual
- Logotipo: Presente (placeholder se ausente).
- Nome do sistema: Presente no header e dashboard.
- Paleta e tipografia: Centralizadas e aplicadas.
- Favicon: Verificar necessidade de customização.

---

*Este documento deve ser revisado a cada alteração de identidade visual ou branding.* 