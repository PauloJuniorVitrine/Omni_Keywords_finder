/// <reference types="cypress" />

describe('Painel de Governança - E2E', () => {
  beforeEach(() => {
    cy.visit('/governanca');
  });

  it('deve permitir upload de regras YAML válidas', () => {
    const yaml = 'score_minimo: 0.5\nblacklist:\n  - termo1\n  - termo2';
    cy.get('textarea#editor-regras').clear().type(yaml, { delay: 0 });
    cy.get('textarea#editor-regras').should('have.value', yaml);
    cy.contains('YAML inválido').should('not.exist');
    // Removido: cy.screenshot();
  });

  it('deve exibir logs e permitir filtro por evento', () => {
    cy.get('table').should('exist');
    cy.get('input#filtro-evento').type('validacao_keywords');
    cy.get('table tbody tr').should('contain', 'validacao_keywords');
  });

  it('deve paginar os logs', () => {
    cy.get('button').contains('Próxima').then(($btn) => {
      if ($btn.is(':disabled')) {
        cy.get('span').should('contain', 'Página 1');
      } else {
        cy.wrap($btn).click();
        cy.get('span').should('contain', 'Página 2');
        cy.get('button').contains('Anterior').click();
        cy.get('span').should('contain', 'Página 1');
      }
    });
  });

  it('deve exportar logs em CSV e JSON', () => {
    cy.get('button').contains('Exportar CSV').should('not.be.disabled');
    cy.get('button').contains('Exportar JSON').should('not.be.disabled');
  });

  it('deve exibir fallback de logs mockados se backend estiver indisponível', () => {
    cy.intercept('GET', '/api/governanca/logs*', { forceNetworkError: true }).as('getLogs');
    cy.visit('/governanca');
    cy.get('div').should('contain', 'Não foi possível carregar logs reais');
    cy.get('table').should('exist');
  });
}); 