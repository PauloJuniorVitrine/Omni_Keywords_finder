import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import DashboardPage from '../../pages/dashboard';
import GovernancaPage from '../../pages/governanca';
import Notifications from '../../pages/dashboard/Notifications';
import AgendarExecucao from '../../pages/dashboard/AgendarExecucao';

expect.extend(toHaveNoViolations);

describe('Acessibilidade (axe-core)', () => {
  it('Dashboard não possui violações críticas', async () => {
    const { container } = render(<DashboardPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Governança não possui violações críticas', async () => {
    const { container } = render(<GovernancaPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Notificações não possui violações críticas', async () => {
    const { container } = render(<Notifications />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Agendamento não possui violações críticas', async () => {
    const { container } = render(<AgendarExecucao />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
}); 