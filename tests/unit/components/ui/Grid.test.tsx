import React from 'react';
import { render, screen } from '@testing-library/react';
import { Grid, GridItem, CardGrid, ListGrid, FormGrid } from '../../../../app/components/ui/layout/Grid';

describe('Grid Component', () => {
  const defaultProps = {
    children: <div data-testid="test-child">Test Child</div>
  };

  it('should render grid with default props', () => {
    render(<Grid {...defaultProps} />);
    
    const grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('grid', 'grid-cols-1', 'gap-4');
  });

  it('should render with different column configurations', () => {
    const { rerender } = render(<Grid {...defaultProps} cols={2} />);
    let grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2');

    rerender(<Grid {...defaultProps} cols={3} />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3');

    rerender(<Grid {...defaultProps} cols={4} />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-4');

    rerender(<Grid {...defaultProps} cols={5} />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3', 'xl:grid-cols-5');

    rerender(<Grid {...defaultProps} cols={6} />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3', 'xl:grid-cols-6');

    rerender(<Grid {...defaultProps} cols={12} />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-4', 'xl:grid-cols-6', '2xl:grid-cols-12');
  });

  it('should render with different gap sizes', () => {
    const { rerender } = render(<Grid {...defaultProps} gap="sm" />);
    let grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('gap-2');

    rerender(<Grid {...defaultProps} gap="md" />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('gap-4');

    rerender(<Grid {...defaultProps} gap="lg" />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('gap-6');

    rerender(<Grid {...defaultProps} gap="xl" />);
    grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass('gap-8');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-grid';
    render(<Grid {...defaultProps} className={customClass} />);
    
    const grid = screen.getByTestId('test-child').parentElement;
    expect(grid).toHaveClass(customClass);
  });

  it('should render multiple children', () => {
    render(
      <Grid>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
        <div data-testid="child-3">Child 3</div>
      </Grid>
    );
    
    expect(screen.getByTestId('child-1')).toBeInTheDocument();
    expect(screen.getByTestId('child-2')).toBeInTheDocument();
    expect(screen.getByTestId('child-3')).toBeInTheDocument();
  });
});

describe('GridItem Component', () => {
  const defaultProps = {
    children: <div data-testid="test-child">Test Child</div>
  };

  it('should render grid item with default props', () => {
    render(<GridItem {...defaultProps} />);
    
    const item = screen.getByTestId('test-child').parentElement;
    expect(item).toBeInTheDocument();
  });

  it('should apply span classes correctly', () => {
    const span = {
      sm: 2,
      md: 3,
      lg: 4,
      xl: 5,
      '2xl': 6
    };

    render(<GridItem {...defaultProps} span={span} />);
    
    const item = screen.getByTestId('test-child').parentElement;
    expect(item).toHaveClass('sm:col-span-2', 'md:col-span-3', 'lg:col-span-4', 'xl:col-span-5', '2xl:col-span-6');
  });

  it('should apply partial span classes', () => {
    const span = {
      sm: 2,
      lg: 4
    };

    render(<GridItem {...defaultProps} span={span} />);
    
    const item = screen.getByTestId('test-child').parentElement;
    expect(item).toHaveClass('sm:col-span-2', 'lg:col-span-4');
    expect(item).not.toHaveClass('md:col-span-3', 'xl:col-span-5', '2xl:col-span-6');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-grid-item';
    render(<GridItem {...defaultProps} className={customClass} />);
    
    const item = screen.getByTestId('test-child').parentElement;
    expect(item).toHaveClass(customClass);
  });

  it('should render without span classes when span is not provided', () => {
    render(<GridItem {...defaultProps} />);
    
    const item = screen.getByTestId('test-child').parentElement;
    expect(item).not.toHaveClass('sm:col-span-2', 'md:col-span-3', 'lg:col-span-4');
  });
});

describe('CardGrid Component', () => {
  it('should render card grid with correct props', () => {
    render(
      <CardGrid>
        <div data-testid="card-1">Card 1</div>
        <div data-testid="card-2">Card 2</div>
      </CardGrid>
    );
    
    const grid = screen.getByTestId('card-1').parentElement;
    expect(grid).toHaveClass('grid', 'grid-cols-1', 'sm:grid-cols-2', 'lg:grid-cols-3', 'gap-6');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-card-grid';
    render(
      <CardGrid className={customClass}>
        <div data-testid="card">Card</div>
      </CardGrid>
    );
    
    const grid = screen.getByTestId('card').parentElement;
    expect(grid).toHaveClass(customClass);
  });
});

describe('ListGrid Component', () => {
  it('should render list grid with correct props', () => {
    render(
      <ListGrid>
        <div data-testid="item-1">Item 1</div>
        <div data-testid="item-2">Item 2</div>
      </ListGrid>
    );
    
    const grid = screen.getByTestId('item-1').parentElement;
    expect(grid).toHaveClass('grid', 'grid-cols-1', 'gap-4');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-list-grid';
    render(
      <ListGrid className={customClass}>
        <div data-testid="item">Item</div>
      </ListGrid>
    );
    
    const grid = screen.getByTestId('item').parentElement;
    expect(grid).toHaveClass(customClass);
  });
});

describe('FormGrid Component', () => {
  it('should render form grid with correct props', () => {
    render(
      <FormGrid>
        <div data-testid="field-1">Field 1</div>
        <div data-testid="field-2">Field 2</div>
      </FormGrid>
    );
    
    const grid = screen.getByTestId('field-1').parentElement;
    expect(grid).toHaveClass('grid', 'grid-cols-1', 'sm:grid-cols-2', 'gap-4');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-form-grid';
    render(
      <FormGrid className={customClass}>
        <div data-testid="field">Field</div>
      </FormGrid>
    );
    
    const grid = screen.getByTestId('field').parentElement;
    expect(grid).toHaveClass(customClass);
  });
}); 