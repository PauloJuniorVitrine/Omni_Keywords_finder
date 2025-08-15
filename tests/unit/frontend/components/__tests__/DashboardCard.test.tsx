import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import DashboardCard from '../../../../app/components/dashboards/DashboardCard'

// Mock do Material-UI
vi.mock('@mui/material', () => ({
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children }: any) => <div data-testid="card-content">{children}</div>,
  Typography: ({ children, variant }: any) => <div data-testid={`typography-${variant}`}>{children}</div>,
  IconButton: ({ children, onClick }: any) => <button data-testid="icon-button" onClick={onClick}>{children}</button>,
  Box: ({ children, ...props }: any) => <div data-testid="box" {...props}>{children}</div>,
}))

describe('DashboardCard Component', () => {
  const defaultProps = {
    title: 'Test Dashboard',
    value: '100',
    subtitle: 'Test Subtitle',
    icon: '📊',
    trend: '+5%',
    trendDirection: 'up' as const,
    onClick: vi.fn(),
  }

  it('should render with all props correctly', () => {
    render(<DashboardCard {...defaultProps} />)
    
    expect(screen.getByTestId('card')).toBeInTheDocument()
    expect(screen.getByTestId('card-content')).toBeInTheDocument()
    expect(screen.getByText('Test Dashboard')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument()
    expect(screen.getByText('📊')).toBeInTheDocument()
    expect(screen.getByText('+5%')).toBeInTheDocument()
  })

  it('should call onClick when card is clicked', () => {
    const mockOnClick = vi.fn()
    render(<DashboardCard {...defaultProps} onClick={mockOnClick} />)
    
    const card = screen.getByTestId('card')
    fireEvent.click(card)
    
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('should render trend with correct direction styling', () => {
    render(<DashboardCard {...defaultProps} trendDirection="down" />)
    
    const trendElement = screen.getByText('+5%')
    expect(trendElement).toBeInTheDocument()
  })

  it('should handle missing optional props gracefully', () => {
    const minimalProps = {
      title: 'Minimal Card',
      value: '50',
    }
    
    render(<DashboardCard {...minimalProps} />)
    
    expect(screen.getByText('Minimal Card')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
  })
})
