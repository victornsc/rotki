export class DefiPage {
  visit() {
    cy.get('.v-app-bar__nav-icon').click();
    cy.get('.navigation__defi').click();
  }

  goToSelectModules() {
    cy.get('.defi-wizard__select-modules').click();
  }

  selectModules() {
    cy.get('#defi-module-makerdao_dsr').find('button').click();
    cy.get('#defi-module-makerdao_vaults').find('button').click();
    cy.get('#defi-module-aave').should('be.visible');
    cy.get('#defi-module-makerdao_dsr').should('not.be.visible');
    cy.get('#defi-module-makerdao_vaults').should('not.be.visible');
    cy.get('.defi-wizard__select-accounts').click();
  }

  selectAccounts() {
    cy.get('.defi-address-selector')
      .find('.v-stepper__header')
      .children()
      .should('have.length', 1);
    cy.get('.defi-wizard__done').click();
  }

  defiOverviewIsVisible() {
    cy.contains('Defi Overview').should('be.visible');
  }
}
