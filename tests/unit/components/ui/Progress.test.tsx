import React from 'react';
import { render, screen } from '@testing-library/react';
import { Progress } from '../../../../app/components/ui/feedback/Progress';

describe('Progress Component', () => {
  const defaultProps = {
    value: 50,
    max: 100,
    min: 0
  };

  it('should render progress bar with correct value', () => {
    render(<Progress {...defaultProps} />);
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '100');
  });

  it('should render with custom aria-label', () => {
    const customLabel = 'Custom progress label';
    render(<Progress {...defaultProps} aria-label={customLabel} />);
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-label', customLabel);
  });

  it('should render with default aria-label when not provided', () => {
    render(<Progress {...defaultProps} />);
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-label', 'Progress: 50%');
  });

  it('should apply different size classes', () => {
    const { rerender } = render(<Progress {...defaultProps} size="sm" />);
    let progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('h-1');

    rerender(<Progress {...defaultProps} size="md" />);
    progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('h-2');

    rerender(<Progress {...defaultProps} size="lg" />);
    progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('h-3');
  });

  it('should apply different variant classes', () => {
    const { rerender } = render(<Progress {...defaultProps} variant="default" />);
    let progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('bg-blue-600');

    rerender(<Progress {...defaultProps} variant="success" />);
    progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('bg-green-600');

    rerender(<Progress {...defaultProps} variant="warning" />);
    progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('bg-yellow-600');

    rerender(<Progress {...defaultProps} variant="error" />);
    progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('bg-red-600');
  });

  it('should render label when showLabel is true', () => {
    render(<Progress {...defaultProps} showLabel={true} />);
    
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('should not render label when showLabel is false', () => {
    render(<Progress {...defaultProps} showLabel={false} />);
    
    expect(screen.queryByText('50%')).not.toBeInTheDocument();
  });

  it('should render label in different positions', () => {
    const { rerender } = render(
      <Progress {...defaultProps} showLabel={true} labelPosition="top" />
    );
    expect(screen.getByText('50%')).toBeInTheDocument();

    rerender(
      <Progress {...defaultProps} showLabel={true} labelPosition="bottom" />
    );
    expect(screen.getByText('50%')).toBeInTheDocument();

    rerender(
      <Progress {...defaultProps} showLabel={true} labelPosition="left" />
    );
    expect(screen.getByText('50%')).toBeInTheDocument();

    rerender(
      <Progress {...defaultProps} showLabel={true} labelPosition="right" />
    );
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('should calculate percentage correctly with custom min/max', () => {
    render(<Progress value={25} min={0} max={50} showLabel={true} />);
    
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('should clamp percentage between 0 and 100', () => {
    const { rerender } = render(<Progress value={150} showLabel={true} />);
    expect(screen.getByText('100%')).toBeInTheDocument();

    rerender(<Progress value={-10} showLabel={true} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const customClass = 'custom-progress';
    render(<Progress {...defaultProps} className={customClass} />);
    
    const container = screen.getByRole('progressbar').parentElement;
    expect(container).toHaveClass(customClass);
  });

  it('should apply animation classes when animated is true', () => {
    render(<Progress {...defaultProps} animated={true} />);
    
    const progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('transition-all', 'duration-300', 'ease-out');
  });

  it('should apply striped classes when striped is true', () => {
    render(<Progress {...defaultProps} striped={true} />);
    
    const progressFill = screen.getByRole('progressbar').querySelector('div');
    expect(progressFill).toHaveClass('bg-gradient-to-r', 'from-transparent', 'via-white', 'to-transparent');
  });

  it('should render page info when totalItems and itemsPerPage are provided', () => {
    render(
      <Progress 
        {...defaultProps} 
        totalItems={100} 
        itemsPerPage={10} 
        showLabel={true} 
      />
    );
    
    expect(screen.getByText('Mostrando 1-10 de 100')).toBeInTheDocument();
  });
}); 