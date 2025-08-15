/**
 * Tests for Lazy Loading System
 * 
 * Tracing ID: LAZY_LOADING_TESTS_20250127_001
 * Prompt: CHECKLIST_INTERFACE_2.md - Item 4.1
 * Ruleset: enterprise_control_layer.yaml
 * Date: 2025-01-27
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { useLazyLoad, LazyLoad, LazyImage, createLazyComponent } from '../../optimizations/lazyLoading';

// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn();
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
global.IntersectionObserver = mockIntersectionObserver;

describe('Lazy Loading System', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useLazyLoad Hook', () => {
    it('should initialize with default values', () => {
      const TestComponent = () => {
        const { isVisible, hasLoaded } = useLazyLoad();
        return (
          <div>
            <span data-testid="is-visible">{isVisible.toString()}</span>
            <span data-testid="has-loaded">{hasLoaded.toString()}</span>
          </div>
        );
      };

      render(<TestComponent />);
      
      expect(screen.getByTestId('is-visible')).toHaveTextContent('false');
      expect(screen.getByTestId('has-loaded')).toHaveTextContent('false');
    });

    it('should trigger visibility when element becomes visible', async () => {
      const TestComponent = () => {
        const { elementRef, isVisible, hasLoaded } = useLazyLoad();
        return (
          <div ref={elementRef} data-testid="lazy-element">
            <span data-testid="is-visible">{isVisible.toString()}</span>
            <span data-testid="has-loaded">{hasLoaded.toString()}</span>
          </div>
        );
      };

      render(<TestComponent />);

      // Simulate intersection observer callback
      const observerCallback = mockIntersectionObserver.mock.calls[0][0];
      observerCallback([{ isIntersecting: true }]);

      await waitFor(() => {
        expect(screen.getByTestId('is-visible')).toHaveTextContent('true');
        expect(screen.getByTestId('has-loaded')).toHaveTextContent('true');
      });
    });

    it('should preload when preload option is true', () => {
      const TestComponent = () => {
        const { isVisible, hasLoaded } = useLazyLoad({ preload: true });
        return (
          <div>
            <span data-testid="is-visible">{isVisible.toString()}</span>
            <span data-testid="has-loaded">{hasLoaded.toString()}</span>
          </div>
        );
      };

      render(<TestComponent />);
      
      expect(screen.getByTestId('is-visible')).toHaveTextContent('true');
      expect(screen.getByTestId('has-loaded')).toHaveTextContent('true');
    });
  });

  describe('LazyLoad Component', () => {
    it('should render fallback when not visible', () => {
      render(
        <LazyLoad>
          <div data-testid="content">Content</div>
        </LazyLoad>
      );

      expect(screen.getByText('Carregando...')).toBeInTheDocument();
      expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    });

    it('should render content when visible', async () => {
      const TestComponent = () => {
        const [isVisible, setIsVisible] = React.useState(false);
        
        React.useEffect(() => {
          setTimeout(() => setIsVisible(true), 0);
        }, []);

        return (
          <LazyLoad options={{ preload: isVisible }}>
            <div data-testid="content">Content</div>
          </LazyLoad>
        );
      };

      render(<TestComponent />);

      await waitFor(() => {
        expect(screen.getByTestId('content')).toBeInTheDocument();
      });
    });

    it('should call onLoad callback when loaded', async () => {
      const onLoadMock = jest.fn();
      
      const TestComponent = () => {
        const [isVisible, setIsVisible] = React.useState(false);
        
        React.useEffect(() => {
          setTimeout(() => setIsVisible(true), 0);
        }, []);

        return (
          <LazyLoad options={{ preload: isVisible }} onLoad={onLoadMock}>
            <div data-testid="content">Content</div>
          </LazyLoad>
        );
      };

      render(<TestComponent />);

      await waitFor(() => {
        expect(onLoadMock).toHaveBeenCalled();
      });
    });
  });

  describe('LazyImage Component', () => {
    it('should render with fallback initially', () => {
      render(
        <LazyImage
          src="test-image.jpg"
          alt="Test image"
          fallback="fallback-image.jpg"
        />
      );

      const img = screen.getByAltText('Test image');
      expect(img).toHaveAttribute('src', 'fallback-image.jpg');
    });

    it('should load actual image when visible', async () => {
      const TestComponent = () => {
        const [isVisible, setIsVisible] = React.useState(false);
        
        React.useEffect(() => {
          setTimeout(() => setIsVisible(true), 0);
        }, []);

        return (
          <LazyImage
            src="test-image.jpg"
            alt="Test image"
            fallback="fallback-image.jpg"
          />
        );
      };

      render(<TestComponent />);

      // Simulate intersection observer callback
      const observerCallback = mockIntersectionObserver.mock.calls[0][0];
      observerCallback([{ isIntersecting: true }]);

      await waitFor(() => {
        const img = screen.getByAltText('Test image');
        expect(img).toHaveAttribute('src', 'test-image.jpg');
      });
    });
  });

  describe('createLazyComponent', () => {
    it('should create lazy component with fallback', () => {
      const TestComponent = () => <div data-testid="test-component">Test</div>;
      const importFunc = jest.fn().mockResolvedValue({ default: TestComponent });
      
      const LazyTestComponent = createLazyComponent(importFunc);
      
      render(<LazyTestComponent />);
      
      expect(screen.getByText('Carregando...')).toBeInTheDocument();
    });
  });
}); 