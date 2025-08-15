import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from '../../../../app/App'

// Mock dos componentes filhos
vi.mock('../../../../app/components/layout/Header', () => ({
  default: () => <div data-testid="header">Header</div>
}))

vi.mock('../../../../app/components/layout/Sidebar', () => ({
  default: () => <div data-testid="sidebar">Sidebar</div>
}))

vi.mock('../../../../app/routes/AppRoutes', () => ({
  default: () => <div data-testid="app-routes">App Routes</div>
}))

describe('App Component', () => {
  it('should render without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('app-routes')).toBeInTheDocument()
  })

  it('should have proper layout structure', () => {
    render(<App />)
    const app = screen.getByRole('application')
    expect(app).toBeInTheDocument()
  })

  it('should render theme provider correctly', () => {
    render(<App />)
    // Verifica se o tema está sendo aplicado
    const app = screen.getByRole('application')
    expect(app).toHaveAttribute('data-theme')
  })
})
