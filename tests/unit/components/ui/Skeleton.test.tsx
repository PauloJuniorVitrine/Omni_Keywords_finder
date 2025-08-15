import React from 'react';
import { render, screen } from '@testing-library/react';
import { Skeleton, SkeletonText, SkeletonAvatar, SkeletonCard, SkeletonTable } from '../../../../app/components/ui/feedback/Skeleton';

describe('Skeleton Component', () => {
  const defaultProps = {
    variant: 'text' as const
  };

  it('should render skeleton with default props', () => {
    render(<Skeleton {...defaultProps} />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton).toHaveClass('bg-gray-200', 'h-4', 'rounded');
    expect(skeleton).toHaveAttribute('aria-hidden', 'true');
  });

  it('should render different variants correctly', () => {
    const { rerender } = render(<Skeleton variant="text" />);
    let skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('h-4', 'rounded');

    rerender(<Skeleton variant="circular" />);
    skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('rounded-full');

    rerender(<Skeleton variant="rectangular" />);
    skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('rounded');
  });

  it('should apply custom width and height', () => {
    render(<Skeleton {...defaultProps} width="200px" height="100px" />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveStyle({ width: '200px', height: '100px' });
  });

  it('should apply custom className', () => {
    const customClass = 'custom-skeleton';
    render(<Skeleton {...defaultProps} className={customClass} />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass(customClass);
  });

  it('should apply animation classes when animated is true', () => {
    render(<Skeleton {...defaultProps} animated={true} />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('animate-pulse', 'bg-gradient-to-r', 'from-gray-200', 'via-gray-300', 'to-gray-200');
  });

  it('should not apply animation classes when animated is false', () => {
    render(<Skeleton {...defaultProps} animated={false} />);
    
    const skeleton = screen.getByRole('generic');
    expect(skeleton).not.toHaveClass('animate-pulse');
  });

  it('should use default dimensions for each variant', () => {
    const { rerender } = render(<Skeleton variant="text" />);
    let skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveStyle({ width: '100%', height: '1rem' });

    rerender(<Skeleton variant="circular" />);
    skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveStyle({ width: '2rem', height: '2rem' });

    rerender(<Skeleton variant="rectangular" />);
    skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveStyle({ width: '100%', height: '8rem' });
  });
});

describe('SkeletonText Component', () => {
  it('should render skeleton text with default props', () => {
    render(<SkeletonText />);
    
    const container = screen.getByRole('generic');
    expect(container).toBeInTheDocument();
    expect(container).toHaveClass('space-y-2');
  });

  it('should render specified number of lines', () => {
    render(<SkeletonText lines={3} />);
    
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons).toHaveLength(3);
  });

  it('should apply custom className', () => {
    const customClass = 'custom-skeleton-text';
    render(<SkeletonText className={customClass} />);
    
    const container = screen.getByRole('generic');
    expect(container).toHaveClass(customClass);
  });

  it('should apply animation when animated is true', () => {
    render(<SkeletonText animated={true} />);
    
    const skeletons = screen.getAllByRole('generic');
    skeletons.forEach(skeleton => {
      expect(skeleton).toHaveClass('animate-pulse');
    });
  });
});

describe('SkeletonAvatar Component', () => {
  it('should render skeleton avatar with default size', () => {
    render(<SkeletonAvatar />);
    
    const avatar = screen.getByRole('generic');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveClass('w-12', 'h-12');
  });

  it('should render different sizes correctly', () => {
    const { rerender } = render(<SkeletonAvatar size="sm" />);
    let avatar = screen.getByRole('generic');
    expect(avatar).toHaveClass('w-8', 'h-8');

    rerender(<SkeletonAvatar size="md" />);
    avatar = screen.getByRole('generic');
    expect(avatar).toHaveClass('w-12', 'h-12');

    rerender(<SkeletonAvatar size="lg" />);
    avatar = screen.getByRole('generic');
    expect(avatar).toHaveClass('w-16', 'h-16');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-skeleton-avatar';
    render(<SkeletonAvatar className={customClass} />);
    
    const avatar = screen.getByRole('generic');
    expect(avatar).toHaveClass(customClass);
  });
});

describe('SkeletonCard Component', () => {
  it('should render skeleton card with default props', () => {
    render(<SkeletonCard />);
    
    const card = screen.getByRole('generic');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass('p-4', 'border', 'border-gray-200', 'rounded-lg');
  });

  it('should render avatar, text, and rectangular skeleton', () => {
    render(<SkeletonCard />);
    
    // Verifica se o avatar está presente
    const avatar = screen.getByRole('generic');
    expect(avatar).toBeInTheDocument();
    
    // Verifica se há múltiplos skeletons (avatar + text + rectangular)
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons.length).toBeGreaterThan(1);
  });

  it('should apply custom className', () => {
    const customClass = 'custom-skeleton-card';
    render(<SkeletonCard className={customClass} />);
    
    const card = screen.getByRole('generic');
    expect(card).toHaveClass(customClass);
  });
});

describe('SkeletonTable Component', () => {
  it('should render skeleton table with default props', () => {
    render(<SkeletonTable />);
    
    const table = screen.getByRole('generic');
    expect(table).toBeInTheDocument();
    expect(table).toHaveClass('overflow-hidden', 'border', 'border-gray-200', 'rounded-lg');
  });

  it('should render specified number of rows and columns', () => {
    render(<SkeletonTable rows={3} columns={4} />);
    
    // Verifica se há skeletons para header e rows
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should render table structure correctly', () => {
    render(<SkeletonTable />);
    
    // Verifica se há elementos de tabela
    const tableElements = screen.getAllByRole('generic');
    expect(tableElements.length).toBeGreaterThan(0);
  });

  it('should apply custom className', () => {
    const customClass = 'custom-skeleton-table';
    render(<SkeletonTable className={customClass} />);
    
    const table = screen.getByRole('generic');
    expect(table).toHaveClass(customClass);
  });
}); 