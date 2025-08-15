import React from 'react';
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../../../app/components/ui/button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA attributes when disabled', async () => {
    const { container } = render(<Button disabled>Disabled Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-disabled', 'true');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA attributes when loading', async () => {
    const { container } = render(<Button loading>Loading Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).toHaveAttribute('aria-disabled', 'true');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA label when provided', async () => {
    const { container } = render(
      <Button aria-label="Custom button label">Button Text</Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Custom button label');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA describedby when provided', async () => {
    const { container } = render(
      <div>
        <div id="description">Button description</div>
        <Button aria-describedby="description">Button</Button>
      </div>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-describedby', 'description');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard accessible', async () => {
    const { container } = render(<Button>Keyboard Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('tabindex', '0');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper focus styles', async () => {
    const { container } = render(<Button>Focusable Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-blue-500');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper color contrast', async () => {
    const { container } = render(<Button>High Contrast Button</Button>);
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper text size for readability', async () => {
    const { container } = render(<Button>Readable Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('text-sm', 'font-medium');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper touch target size', async () => {
    const { container } = render(<Button>Touch Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('min-h-[44px]', 'min-w-[44px]');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should announce loading state to screen readers', async () => {
    const { container } = render(
      <Button loading aria-label="Loading button">
        Loading
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Loading button');
    expect(button).toHaveAttribute('aria-busy', 'true');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper role when used as link', async () => {
    const { container } = render(
      <Button as="a" href="/test">
        Link Button
      </Button>
    );
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/test');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA expanded when used as toggle', async () => {
    const { container } = render(
      <Button aria-expanded="false" aria-controls="menu">
        Toggle Menu
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-expanded', 'false');
    expect(button).toHaveAttribute('aria-controls', 'menu');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA pressed when used as toggle button', async () => {
    const { container } = render(
      <Button aria-pressed="false">
        Toggle Button
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-pressed', 'false');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA live region when used for notifications', async () => {
    const { container } = render(
      <Button aria-live="polite">
        Notification Button
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-live', 'polite');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have proper ARIA current when used for navigation', async () => {
    const { container } = render(
      <Button aria-current="page">
        Current Page
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-current', 'page');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
}); 