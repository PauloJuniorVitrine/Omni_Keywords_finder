import React from 'react';
import { render, screen } from '@testing-library/react';
import { Breadcrumb } from '../../../../app/components/ui/navigation/Breadcrumb';

describe('Breadcrumb Component', () => {
  const mockItems = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Users', href: '/dashboard/users' },
    { label: 'Profile' }
  ];

  it('should render breadcrumb with items', () => {
    render(<Breadcrumb items={mockItems} />);
    
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Users')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('should render without home item when showHome is false', () => {
    render(<Breadcrumb items={mockItems} showHome={false} />);
    
    expect(screen.queryByText('Home')).not.toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('should render links for non-last items', () => {
    render(<Breadcrumb items={mockItems} />);
    
    const dashboardLink = screen.getByText('Dashboard').closest('a');
    const usersLink = screen.getByText('Users').closest('a');
    
    expect(dashboardLink).toHaveAttribute('href', '/dashboard');
    expect(usersLink).toHaveAttribute('href', '/dashboard/users');
  });

  it('should not render link for last item', () => {
    render(<Breadcrumb items={mockItems} />);
    
    const profileElement = screen.getByText('Profile');
    expect(profileElement.closest('a')).not.toBeInTheDocument();
    expect(profileElement).toHaveAttribute('aria-current', 'page');
  });

  it('should have proper ARIA attributes', () => {
    render(<Breadcrumb items={mockItems} />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label', 'Breadcrumb navigation');
  });

  it('should apply custom aria-label', () => {
    const customLabel = 'Custom breadcrumb';
    render(<Breadcrumb items={mockItems} aria-label={customLabel} />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label', customLabel);
  });

  it('should apply custom className', () => {
    const customClass = 'custom-breadcrumb';
    render(<Breadcrumb items={mockItems} className={customClass} />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveClass(customClass);
  });

  it('should render with custom home href', () => {
    const customHomeHref = '/custom-home';
    render(<Breadcrumb items={mockItems} homeHref={customHomeHref} />);
    
    const homeLink = screen.getByText('Home').closest('a');
    expect(homeLink).toHaveAttribute('href', customHomeHref);
  });

  it('should handle empty items array', () => {
    render(<Breadcrumb items={[]} />);
    
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Home')).toHaveAttribute('aria-current', 'page');
  });

  it('should handle single item', () => {
    const singleItem = [{ label: 'Single Item' }];
    render(<Breadcrumb items={singleItem} showHome={false} />);
    
    expect(screen.getByText('Single Item')).toBeInTheDocument();
    expect(screen.getByText('Single Item')).toHaveAttribute('aria-current', 'page');
  });
}); 