// Permite importação de SVGs como módulos em TypeScript
declare module '*.svg' {
  const content: string;
  export default content;
} 