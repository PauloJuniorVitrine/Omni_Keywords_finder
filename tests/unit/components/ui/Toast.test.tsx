import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Toast, ToastContainer, useToast } from '../../../../app/components/ui/feedback/Toast';

// Mock para o hook useToast
const MockToastComponent: React.FC<{ toastType: 'success' | 'error' | 'warning' | 'info' }> = ({ toastType }) => {
  const { addToast } = useToast();
  
  const handleAddToast = () => {
    addToast({
      type: toastType,
      title: 'Test Toast',
      message: 'This is a test message'
    });
  };

  return (
    <button onClick={handleAddToast}>
      Add Toast
    </button>
  );
};

describe('Toast Component', () => {
  const mockToast = {
    id: 'test-toast',
    type: 'success' as const,
    title: 'Success',
    message: 'Operation completed successfully',
    onClose: jest.fn()
  };

  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('should render toast with title and message', () => {
    render(<Toast {...mockToast} />);
    
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
  });

  it('should render toast without message', () => {
    const toastWithoutMessage = { ...mockToast, message: undefined };
    render(<Toast {...toastWithoutMessage} />);
    
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.queryByText('Operation completed successfully')).not.toBeInTheDocument();
  });

  it('should have proper ARIA attributes', () => {
    render(<Toast {...mockToast} />);
    
    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
  });

  it('should call onClose when close button is clicked', () => {
    render(<Toast {...mockToast} />);
    
    const closeButton = screen.getByLabelText('Fechar notificação');
    fireEvent.click(closeButton);
    
    expect(mockToast.onClose).toHaveBeenCalledWith('test-toast');
  });

  it('should auto-close after duration', async () => {
    render(<Toast {...mockToast} duration={1000} />);
    
    // Avança o tempo para acionar o auto-close
    jest.advanceTimersByTime(1100);
    
    await waitFor(() => {
      expect(mockToast.onClose).toHaveBeenCalledWith('test-toast');
    });
  });

  it('should apply custom className', () => {
    const customClass = 'custom-toast';
    render(<Toast {...mockToast} className={customClass} />);
    
    const toastContainer = screen.getByRole('alert').parentElement;
    expect(toastContainer).toHaveClass(customClass);
  });

  it('should render different toast types with correct styles', () => {
    const toastTypes = ['success', 'error', 'warning', 'info'] as const;
    
    toastTypes.forEach(type => {
      const { unmount } = render(<Toast {...mockToast} type={type} />);
      
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
      
      unmount();
    });
  });
});

describe('ToastContainer Component', () => {
  it('should render children and toast container', () => {
    render(
      <ToastContainer>
        <div>Test Content</div>
      </ToastContainer>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should render toast when added via context', async () => {
    render(
      <ToastContainer>
        <MockToastComponent toastType="success" />
      </ToastContainer>
    );
    
    const addButton = screen.getByText('Add Toast');
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText('Test Toast')).toBeInTheDocument();
      expect(screen.getByText('This is a test message')).toBeInTheDocument();
    });
  });

  it('should limit number of toasts', async () => {
    render(
      <ToastContainer maxToasts={2}>
        <MockToastComponent toastType="success" />
      </ToastContainer>
    );
    
    const addButton = screen.getByText('Add Toast');
    
    // Adiciona 3 toasts
    fireEvent.click(addButton);
    fireEvent.click(addButton);
    fireEvent.click(addButton);
    
    await waitFor(() => {
      const toasts = screen.getAllByText('Test Toast');
      expect(toasts).toHaveLength(2); // Máximo de 2 toasts
    });
  });

  it('should position toasts correctly', () => {
    const positions = ['top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center', 'bottom-center'] as const;
    
    positions.forEach(position => {
      const { unmount } = render(
        <ToastContainer position={position}>
          <div>Test</div>
        </ToastContainer>
      );
      
      const container = screen.getByText('Test').parentElement?.nextElementSibling;
      expect(container).toBeInTheDocument();
      
      unmount();
    });
  });
});

describe('useToast Hook', () => {
  it('should throw error when used outside ToastContainer', () => {
    const TestComponent = () => {
      useToast();
      return <div>Test</div>;
    };

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useToast must be used within a ToastContainer');
  });

  it('should provide toast context when used within ToastContainer', () => {
    const TestComponent = () => {
      const { addToast, removeToast, clearToasts } = useToast();
      return (
        <div>
          <button onClick={() => addToast({ type: 'success', title: 'Test' })}>
            Add
          </button>
          <button onClick={() => removeToast('test')}>
            Remove
          </button>
          <button onClick={clearToasts}>
            Clear
          </button>
        </div>
      );
    };

    render(
      <ToastContainer>
        <TestComponent />
      </ToastContainer>
    );
    
    expect(screen.getByText('Add')).toBeInTheDocument();
    expect(screen.getByText('Remove')).toBeInTheDocument();
    expect(screen.getByText('Clear')).toBeInTheDocument();
  });
}); 