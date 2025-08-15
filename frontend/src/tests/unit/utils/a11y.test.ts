/**
 * Testes Unitários - Utilitários de Acessibilidade
 * 
 * Tracing ID: A11Y_UTILS_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Testes baseados nos utilitários de acessibilidade reais do sistema Omni Keywords Finder
 */

import {
  validateAriaProps,
  generateAriaProps,
  validateContrast,
  getFocusableElements,
  trapFocus,
  restoreFocus,
  announceToScreenReader,
  getA11yStats
} from '../../../utils/a11y';

describe('Utilitários de Acessibilidade', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Limpa o DOM antes de cada teste
    document.body.innerHTML = '';
  });

  describe('Validação de Props ARIA', () => {
    test('deve validar props ARIA válidas', () => {
      const validProps = {
        'aria-label': 'Botão de upload',
        'aria-describedby': 'description',
        'aria-required': true,
        'aria-invalid': false
      };
      
      const validation = validateAriaProps(validProps);
      
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    test('deve detectar props ARIA inválidas', () => {
      const invalidProps = {
        'aria-label': '', // Label vazio
        'aria-describedby': 'non-existent-id', // ID inexistente
        'aria-required': 'invalid-value', // Valor inválido
        'aria-invalid': 'maybe' // Valor inválido
      };
      
      const validation = validateAriaProps(invalidProps);
      
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });

    test('deve validar props ARIA vazias', () => {
      const validation = validateAriaProps({});
      
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    test('deve validar props ARIA com valores undefined', () => {
      const propsWithUndefined = {
        'aria-label': undefined,
        'aria-describedby': undefined,
        'aria-required': undefined
      };
      
      const validation = validateAriaProps(propsWithUndefined);
      
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });
  });

  describe('Geração de Props ARIA', () => {
    test('deve gerar props ARIA para botão', () => {
      const ariaProps = generateAriaProps({
        role: 'button',
        label: 'Upload keywords',
        description: 'Upload file with keywords',
        required: true,
        invalid: false
      });
      
      expect(ariaProps).toHaveProperty('role', 'button');
      expect(ariaProps).toHaveProperty('aria-label', 'Upload keywords');
      expect(ariaProps).toHaveProperty('aria-describedby');
      expect(ariaProps).toHaveProperty('aria-required', true);
      expect(ariaProps).toHaveProperty('aria-invalid', false);
    });

    test('deve gerar props ARIA para input', () => {
      const ariaProps = generateAriaProps({
        role: 'textbox',
        label: 'Keywords input',
        description: 'Enter your keywords here',
        required: true,
        invalid: false,
        type: 'text'
      });
      
      expect(ariaProps).toHaveProperty('role', 'textbox');
      expect(ariaProps).toHaveProperty('aria-label', 'Keywords input');
      expect(ariaProps).toHaveProperty('aria-required', true);
      expect(ariaProps).toHaveProperty('aria-invalid', false);
    });

    test('deve gerar props ARIA para modal', () => {
      const ariaProps = generateAriaProps({
        role: 'dialog',
        label: 'Configurações',
        description: 'Configurações do sistema de keywords',
        modal: true
      });
      
      expect(ariaProps).toHaveProperty('role', 'dialog');
      expect(ariaProps).toHaveProperty('aria-label', 'Configurações');
      expect(ariaProps).toHaveProperty('aria-modal', true);
    });

    test('deve gerar props ARIA para tabela', () => {
      const ariaProps = generateAriaProps({
        role: 'grid',
        label: 'Keywords table',
        description: 'Table with keywords and frequencies'
      });
      
      expect(ariaProps).toHaveProperty('role', 'grid');
      expect(ariaProps).toHaveProperty('aria-label', 'Keywords table');
    });
  });

  describe('Validação de Contraste', () => {
    test('deve validar contraste adequado', () => {
      const contrastValidation = validateContrast('#000000', '#FFFFFF');
      
      expect(contrastValidation.isValid).toBe(true);
      expect(contrastValidation.ratio).toBeGreaterThan(4.5);
      expect(contrastValidation.meetsWCAGAA).toBe(true);
      expect(contrastValidation.meetsWCAGAAA).toBe(true);
    });

    test('deve detectar contraste insuficiente', () => {
      const contrastValidation = validateContrast('#CCCCCC', '#FFFFFF');
      
      expect(contrastValidation.isValid).toBe(false);
      expect(contrastValidation.ratio).toBeLessThan(4.5);
      expect(contrastValidation.meetsWCAGAA).toBe(false);
      expect(contrastValidation.meetsWCAGAAA).toBe(false);
    });

    test('deve sugerir cores alternativas para contraste insuficiente', () => {
      const contrastValidation = validateContrast('#CCCCCC', '#FFFFFF');
      
      expect(contrastValidation.suggestions).toBeDefined();
      expect(contrastValidation.suggestions.length).toBeGreaterThan(0);
      
      // Verifica se as sugestões têm contraste adequado
      contrastValidation.suggestions.forEach(suggestion => {
        const suggestionValidation = validateContrast(suggestion.foreground, suggestion.background);
        expect(suggestionValidation.isValid).toBe(true);
      });
    });

    test('deve lidar com cores hex inválidas', () => {
      const contrastValidation = validateContrast('invalid-color', 'another-invalid');
      
      expect(contrastValidation.isValid).toBe(false);
      expect(contrastValidation.ratio).toBe(0);
      expect(contrastValidation.error).toBeDefined();
    });

    test('deve validar contraste para diferentes tamanhos de texto', () => {
      // Texto grande (18pt+ ou 14pt+ bold)
      const largeTextValidation = validateContrast('#666666', '#FFFFFF', 'large');
      expect(largeTextValidation.meetsWCAGAA).toBeDefined();
      
      // Texto normal
      const normalTextValidation = validateContrast('#666666', '#FFFFFF', 'normal');
      expect(normalTextValidation.meetsWCAGAA).toBeDefined();
    });
  });

  describe('Gerenciamento de Foco', () => {
    test('deve obter elementos focáveis', () => {
      // Simula elementos no DOM
      document.body.innerHTML = `
        <button>Button 1</button>
        <input type="text" />
        <a href="#">Link</a>
        <div tabindex="0">Focusable div</div>
        <div>Non-focusable div</div>
      `;
      
      const focusableElements = getFocusableElements();
      
      expect(focusableElements.length).toBe(4);
      expect(focusableElements[0].tagName).toBe('BUTTON');
      expect(focusableElements[1].tagName).toBe('INPUT');
      expect(focusableElements[2].tagName).toBe('A');
      expect(focusableElements[3].tagName).toBe('DIV');
    });

    test('deve obter elementos focáveis em container específico', () => {
      document.body.innerHTML = `
        <div id="container">
          <button>Button 1</button>
          <input type="text" />
        </div>
        <button>Outside button</button>
      `;
      
      const container = document.getElementById('container');
      const focusableElements = getFocusableElements(container);
      
      expect(focusableElements.length).toBe(2);
      expect(focusableElements[0].tagName).toBe('BUTTON');
      expect(focusableElements[1].tagName).toBe('INPUT');
    });

    test('deve fazer trap de foco em container', () => {
      // Simula modal no DOM
      document.body.innerHTML = `
        <div id="modal">
          <button>Close</button>
          <input type="text" />
          <button>Save</button>
        </div>
        <button>Outside button</button>
      `;
      
      const modal = document.getElementById('modal');
      const trapFocusResult = trapFocus(modal);
      
      expect(trapFocusResult).toBeDefined();
      expect(typeof trapFocusResult.cleanup).toBe('function');
    });

    test('deve restaurar foco para elemento anterior', () => {
      // Simula elemento que tinha foco
      document.body.innerHTML = '<button id="previous-focus">Previous</button>';
      const previousElement = document.getElementById('previous-focus');
      
      if (previousElement) {
        // Simula que o elemento anterior tinha foco
        previousElement.focus();
        
        // Restaura foco
        restoreFocus();
        
        expect(document.activeElement).toBe(previousElement);
      }
    });

    test('deve lidar com trap de foco em container vazio', () => {
      const trapFocusResult = trapFocus(null);
      
      expect(trapFocusResult).toBeDefined();
      expect(typeof trapFocusResult.cleanup).toBe('function');
    });
  });

  describe('Anúncios para Screen Reader', () => {
    test('deve anunciar mensagem para screen reader', () => {
      const announceResult = announceToScreenReader('Keywords processadas com sucesso');
      
      expect(announceResult).toBeDefined();
      expect(typeof announceResult).toBe('boolean');
    });

    test('deve anunciar mensagem com prioridade assertiva', () => {
      const announceResult = announceToScreenReader('Alerta importante', 'assertive');
      
      expect(announceResult).toBeDefined();
      expect(typeof announceResult).toBe('boolean');
    });

    test('deve anunciar mensagem com prioridade polida', () => {
      const announceResult = announceToScreenReader('Informação importante', 'polite');
      
      expect(announceResult).toBeDefined();
      expect(typeof announceResult).toBe('boolean');
    });

    test('deve lidar com mensagens vazias', () => {
      const announceResult = announceToScreenReader('');
      
      expect(announceResult).toBeDefined();
      expect(typeof announceResult).toBe('boolean');
    });

    test('deve lidar com mensagens null/undefined', () => {
      const announceResult1 = announceToScreenReader(null as any);
      const announceResult2 = announceToScreenReader(undefined as any);
      
      expect(announceResult1).toBeDefined();
      expect(announceResult2).toBeDefined();
    });
  });

  describe('Estatísticas de Acessibilidade', () => {
    test('deve gerar estatísticas de acessibilidade', () => {
      // Simula página com elementos
      document.body.innerHTML = `
        <button aria-label="Upload">Upload</button>
        <input type="text" aria-required="true" />
        <div role="dialog" aria-labelledby="title">Modal</div>
        <table role="grid">Table</table>
      `;
      
      const stats = getA11yStats();
      
      expect(stats).toHaveProperty('totalElements');
      expect(stats).toHaveProperty('elementsWithAria');
      expect(stats).toHaveProperty('elementsWithRoles');
      expect(stats).toHaveProperty('focusableElements');
      expect(stats).toHaveProperty('landmarks');
      expect(stats).toHaveProperty('score');
    });

    test('deve calcular score de acessibilidade', () => {
      // Simula página com boa acessibilidade
      document.body.innerHTML = `
        <nav role="navigation">Navigation</nav>
        <main role="main">Main content</main>
        <button aria-label="Action">Action</button>
        <input type="text" aria-required="true" aria-describedby="help" />
        <div id="help">Help text</div>
      `;
      
      const stats = getA11yStats();
      
      expect(stats.score).toBeGreaterThan(0);
      expect(stats.score).toBeLessThanOrEqual(100);
    });

    test('deve identificar landmarks', () => {
      document.body.innerHTML = `
        <nav role="navigation">Navigation</nav>
        <main role="main">Main content</main>
        <aside role="complementary">Sidebar</aside>
        <footer role="contentinfo">Footer</footer>
      `;
      
      const stats = getA11yStats();
      
      expect(stats.landmarks).toHaveLength(4);
      expect(stats.landmarks).toContain('navigation');
      expect(stats.landmarks).toContain('main');
      expect(stats.landmarks).toContain('complementary');
      expect(stats.landmarks).toContain('contentinfo');
    });
  });

  describe('Cenários de Uso Real', () => {
    test('deve funcionar com formulário de upload de keywords', () => {
      // Simula formulário de upload
      document.body.innerHTML = `
        <form>
          <label for="file-input">Upload Keywords File</label>
          <input id="file-input" type="file" accept=".csv,.xlsx" />
          <button type="submit">Process Keywords</button>
        </form>
      `;
      
      // Valida props ARIA do input
      const inputAriaProps = generateAriaProps({
        role: 'textbox',
        label: 'Upload Keywords File',
        required: true
      });
      
      expect(inputAriaProps).toHaveProperty('aria-label', 'Upload Keywords File');
      expect(inputAriaProps).toHaveProperty('aria-required', true);
      
      // Anuncia ação
      const announceResult = announceToScreenReader('Arquivo selecionado para processamento');
      expect(announceResult).toBeDefined();
      
      // Obtém estatísticas
      const stats = getA11yStats();
      expect(stats.totalElements).toBeGreaterThan(0);
    });

    test('deve funcionar com modal de configurações', () => {
      // Simula modal de configurações
      document.body.innerHTML = `
        <div id="settings-modal" role="dialog" aria-labelledby="modal-title">
          <h2 id="modal-title">Configurações</h2>
          <input type="text" placeholder="Limite de keywords" />
          <button>Salvar</button>
          <button>Cancelar</button>
        </div>
      `;
      
      const modal = document.getElementById('settings-modal');
      
      // Valida props ARIA do modal
      const modalAriaProps = generateAriaProps({
        role: 'dialog',
        label: 'Configurações',
        description: 'Configurações do sistema de keywords'
      });
      
      expect(modalAriaProps).toHaveProperty('role', 'dialog');
      expect(modalAriaProps).toHaveProperty('aria-label', 'Configurações');
      
      // Faz trap de foco no modal
      if (modal) {
        const trapFocusResult = trapFocus(modal);
        expect(trapFocusResult).toBeDefined();
      }
      
      // Anuncia abertura do modal
      const announceResult = announceToScreenReader('Modal de configurações aberto');
      expect(announceResult).toBeDefined();
    });

    test('deve funcionar com dashboard de resultados', () => {
      // Simula dashboard com resultados
      document.body.innerHTML = `
        <div id="dashboard">
          <h1>Resultados da Análise</h1>
          <div role="region" aria-label="Estatísticas">
            <p>Total de keywords: 150</p>
            <p>Keywords únicas: 120</p>
          </div>
          <table role="grid" aria-label="Top Keywords">
            <thead>
              <tr>
                <th>Keyword</th>
                <th>Frequência</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>machine learning</td>
                <td>45</td>
              </tr>
            </tbody>
          </table>
        </div>
      `;
      
      // Valida contraste dos elementos
      const contrastValidation = validateContrast('#333333', '#FFFFFF');
      expect(contrastValidation.isValid).toBe(true);
      
      // Anuncia resultados
      const announceResult = announceToScreenReader('Análise concluída. 150 keywords processadas');
      expect(announceResult).toBeDefined();
      
      // Obtém estatísticas
      const stats = getA11yStats();
      expect(stats.landmarks).toContain('region');
      expect(stats.landmarks).toContain('grid');
    });
  });

  describe('Performance', () => {
    test('deve validar contraste rapidamente', () => {
      const startTime = performance.now();
      
      for (let i = 0; i < 100; i++) {
        validateContrast('#000000', '#FFFFFF');
      }
      
      const endTime = performance.now();
      const validationTime = endTime - startTime;
      
      expect(validationTime).toBeLessThan(100); // Menos de 100ms
    });

    test('deve gerar props ARIA rapidamente', () => {
      const startTime = performance.now();
      
      for (let i = 0; i < 100; i++) {
        generateAriaProps({
          role: 'button',
          label: `Button ${i}`,
          required: true
        });
      }
      
      const endTime = performance.now();
      const generationTime = endTime - startTime;
      
      expect(generationTime).toBeLessThan(50); // Menos de 50ms
    });

    test('deve obter elementos focáveis rapidamente', () => {
      // Simula muitos elementos
      document.body.innerHTML = Array.from({ length: 100 }, (_, i) => 
        `<button>Button ${i}</button>`
      ).join('');
      
      const startTime = performance.now();
      
      getFocusableElements();
      
      const endTime = performance.now();
      const getTime = endTime - startTime;
      
      expect(getTime).toBeLessThan(10); // Menos de 10ms
    });
  });

  describe('Edge Cases', () => {
    test('deve lidar com DOM vazio', () => {
      const focusableElements = getFocusableElements();
      expect(focusableElements).toHaveLength(0);
      
      const stats = getA11yStats();
      expect(stats.totalElements).toBe(0);
      expect(stats.score).toBe(0);
    });

    test('deve lidar com elementos sem atributos', () => {
      document.body.innerHTML = '<div>Content</div>';
      
      const stats = getA11yStats();
      expect(stats.elementsWithAria).toBe(0);
      expect(stats.elementsWithRoles).toBe(0);
    });

    test('deve lidar com cores hex incompletas', () => {
      const contrastValidation = validateContrast('#123', '#456');
      
      expect(contrastValidation.isValid).toBe(false);
      expect(contrastValidation.error).toBeDefined();
    });

    test('deve lidar com elementos removidos do DOM', () => {
      document.body.innerHTML = '<button id="test">Test</button>';
      
      const button = document.getElementById('test');
      const focusableElements = getFocusableElements();
      expect(focusableElements.length).toBe(1);
      
      // Remove o elemento
      button?.remove();
      
      const focusableElementsAfter = getFocusableElements();
      expect(focusableElementsAfter.length).toBe(0);
    });
  });
}); 