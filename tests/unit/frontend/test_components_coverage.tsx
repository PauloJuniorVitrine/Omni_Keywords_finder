/**
 * 🧪 Testes de Cobertura - Componentes Frontend
 * 🎯 Objetivo: Garantir cobertura >90% para todos os componentes
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: FRONTEND_TEST_COVERAGE_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FileUpload } from '../../../app/components/ui/FileUpload';
import { AdminDashboard } from '../../../app/components/admin/AdminDashboard';
import ApiClient from '../../../app/services/api/ApiClient';

// Mock do módulo de utilitários
jest.mock('../../../app/utils/cn', () => ({
  cn: (...classes: string[]) => classes.filter(Boolean).join(' ')
}));

// Mock do fetch para testes de API
global.fetch = jest.fn();

describe('FileUpload Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render correctly with default props', () => {
    render(<FileUpload />);
    
    expect(screen.getByText('Selecionar Arquivos')).toBeInTheDocument();
    expect(screen.getByText('Arraste arquivos aqui ou clique para selecionar')).toBeInTheDocument();
  });

  it('should handle file selection', async () => {
    const onFilesSelected = jest.fn();
    render(<FileUpload onFilesSelected={onFilesSelected} />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    // Simular seleção de arquivo
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(onFilesSelected).toHaveBeenCalledWith([file]);
    });
  });

  it('should validate file size', async () => {
    const onError = jest.fn();
    render(<FileUpload maxSize={1024} onError={onError} />);
    
    const largeFile = new File(['x'.repeat(2048)], 'large.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('Arquivo muito grande'));
    });
  });

  it('should validate file type', async () => {
    const onError = jest.fn();
    render(<FileUpload accept=".pdf,.doc" onError={onError} />);
    
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('Tipo de arquivo não suportado'));
    });
  });

  it('should handle drag and drop', async () => {
    const onFilesSelected = jest.fn();
    render(<FileUpload onFilesSelected={onFilesSelected} />);
    
    const dropZone = screen.getByText('Arraste arquivos aqui ou clique para selecionar').parentElement;
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.dragOver(dropZone!);
    fireEvent.drop(dropZone!, {
      dataTransfer: {
        files: [file]
      }
    });
    
    await waitFor(() => {
      expect(onFilesSelected).toHaveBeenCalledWith([file]);
    });
  });

  it('should handle multiple files', async () => {
    const onFilesSelected = jest.fn();
    render(<FileUpload multiple onFilesSelected={onFilesSelected} />);
    
    const files = [
      new File(['content1'], 'file1.txt', { type: 'text/plain' }),
      new File(['content2'], 'file2.txt', { type: 'text/plain' })
    ];
    
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files } });
    
    await waitFor(() => {
      expect(onFilesSelected).toHaveBeenCalledWith(files);
    });
  });

  it('should remove files', async () => {
    const onFilesSelected = jest.fn();
    render(<FileUpload onFilesSelected={onFilesSelected} />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument();
    });
    
    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);
    
    await waitFor(() => {
      expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
    });
  });

  it('should be disabled when disabled prop is true', () => {
    render(<FileUpload disabled />);
    
    const button = screen.getByRole('button', { name: /selecionar arquivos/i });
    expect(button).toBeDisabled();
  });
});

describe('AdminDashboard Component', () => {
  const mockData = {
    users: {
      total: 1250,
      active: 890,
      newToday: 23,
      growthRate: 12.5
    },
    executions: {
      total: 15420,
      completed: 14890,
      failed: 530,
      successRate: 96.6
    },
    system: {
      cpuUsage: 45.2,
      memoryUsage: 67.8,
      diskUsage: 34.1,
      uptime: 99.8
    },
    alerts: [
      {
        id: '1',
        type: 'warning' as const,
        message: 'Uso de memória acima de 80%',
        timestamp: '2025-01-27T15:30:00Z'
      }
    ],
    recentActivity: [
      {
        id: '1',
        type: 'user_login',
        description: 'Usuário fez login',
        user: 'admin@example.com',
        timestamp: '2025-01-27T15:25:00Z'
      }
    ]
  };

  it('should render correctly with data', () => {
    render(<AdminDashboard data={mockData} />);
    
    expect(screen.getByText('Painel Administrativo')).toBeInTheDocument();
    expect(screen.getByText('1250')).toBeInTheDocument(); // Total users
    expect(screen.getByText('15420')).toBeInTheDocument(); // Total executions
    expect(screen.getByText('45.2%')).toBeInTheDocument(); // CPU usage
  });

  it('should render with mock data when no data provided', () => {
    render(<AdminDashboard />);
    
    expect(screen.getByText('Painel Administrativo')).toBeInTheDocument();
    expect(screen.getByText('Visão Geral')).toBeInTheDocument();
    expect(screen.getByText('Usuários')).toBeInTheDocument();
    expect(screen.getByText('Sistema')).toBeInTheDocument();
    expect(screen.getByText('Alertas')).toBeInTheDocument();
  });

  it('should handle navigation between sections', () => {
    const onNavigate = jest.fn();
    render(<AdminDashboard onNavigate={onNavigate} />);
    
    const usersButton = screen.getByText('Usuários');
    fireEvent.click(usersButton);
    
    expect(onNavigate).toHaveBeenCalledWith('users');
  });

  it('should handle refresh', async () => {
    const onRefresh = jest.fn();
    render(<AdminDashboard onRefresh={onRefresh} />);
    
    const refreshButton = screen.getByText('Atualizar');
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it('should display alerts correctly', () => {
    render(<AdminDashboard data={mockData} />);
    
    expect(screen.getByText('Uso de memória acima de 80%')).toBeInTheDocument();
  });

  it('should display recent activity', () => {
    render(<AdminDashboard data={mockData} />);
    
    expect(screen.getByText('Usuário fez login')).toBeInTheDocument();
    expect(screen.getByText('admin@example.com')).toBeInTheDocument();
  });

  it('should show loading state during refresh', async () => {
    const onRefresh = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<AdminDashboard onRefresh={onRefresh} />);
    
    const refreshButton = screen.getByText('Atualizar');
    fireEvent.click(refreshButton);
    
    expect(screen.getByText('Atualizando...')).toBeInTheDocument();
  });
});

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should make GET request successfully', async () => {
    const mockResponse = { data: 'test', success: true };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockResponse
    });

    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });
    const response = await client.get('/test');

    expect(response.success).toBe(true);
    expect(response.data).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/test',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        })
      })
    );
  });

  it('should make POST request successfully', async () => {
    const mockResponse = { data: 'created', success: true };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockResponse
    });

    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });
    const postData = { name: 'test' };
    const response = await client.post('/test', postData);

    expect(response.success).toBe(true);
    expect(response.data).toEqual(mockResponse);
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/test',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(postData)
      })
    );
  });

  it('should handle authentication token', async () => {
    const mockResponse = { data: 'authenticated', success: true };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockResponse
    });

    const client = new ApiClient({ 
      baseURL: 'http://localhost:8000/api',
      authToken: 'test-token'
    });
    
    const response = await client.get('/protected');

    expect(response.success).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/protected',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token'
        })
      })
    );
  });

  it('should handle 401 unauthorized error', async () => {
    const onUnauthorized = jest.fn();
    const client = new ApiClient({ 
      baseURL: 'http://localhost:8000/api',
      onUnauthorized
    });

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ message: 'Unauthorized' })
    });

    await expect(client.get('/protected')).rejects.toThrow();
    expect(onUnauthorized).toHaveBeenCalled();
  });

  it('should retry on server errors', async () => {
    const client = new ApiClient({ 
      baseURL: 'http://localhost:8000/api',
      retries: 2
    });

    // Primeira tentativa falha
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Server error'));
    
    // Segunda tentativa falha
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Server error'));
    
    // Terceira tentativa sucesso
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ data: 'success' })
    });

    const response = await client.get('/test');

    expect(response.success).toBe(true);
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it('should handle timeout', async () => {
    const client = new ApiClient({ 
      baseURL: 'http://localhost:8000/api',
      timeout: 100
    });

    (fetch as jest.Mock).mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(resolve, 200))
    );

    await expect(client.get('/slow')).rejects.toThrow('Timeout na requisição');
  });

  it('should upload file with progress', async () => {
    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const onProgress = jest.fn();

    // Mock XMLHttpRequest
    const mockXHR = {
      upload: {
        addEventListener: jest.fn()
      },
      addEventListener: jest.fn(),
      open: jest.fn(),
      setRequestHeader: jest.fn(),
      send: jest.fn()
    };

    global.XMLHttpRequest = jest.fn(() => mockXHR) as any;

    const uploadPromise = client.uploadFile('/upload', file, onProgress);

    // Simular progresso
    const progressEvent = { lengthComputable: true, loaded: 50, total: 100 };
    mockXHR.upload.addEventListener.mock.calls[0][1](progressEvent);

    // Simular sucesso
    mockXHR.addEventListener.mock.calls[0][1]();

    const response = await uploadPromise;

    expect(response.success).toBe(true);
    expect(onProgress).toHaveBeenCalledWith(50);
  });

  it('should download file', async () => {
    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });
    const mockBlob = new Blob(['test content']);
    
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      blob: async () => mockBlob
    });

    // Mock URL.createObjectURL e document.createElement
    const mockUrl = 'blob:test';
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn()
    };

    global.URL.createObjectURL = jest.fn(() => mockUrl);
    global.URL.revokeObjectURL = jest.fn();
    document.createElement = jest.fn(() => mockLink as any);
    document.body.appendChild = jest.fn();
    document.body.removeChild = jest.fn();

    await client.downloadFile('/download', 'test.txt');

    expect(URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
    expect(mockLink.download).toBe('test.txt');
    expect(mockLink.click).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl);
  });
});

describe('Component Integration Tests', () => {
  it('should integrate FileUpload with ApiClient', async () => {
    const mockUploadResponse = { url: 'http://example.com/file.txt' };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockUploadResponse
    });

    const onUploadComplete = jest.fn();
    render(<FileUpload onUploadComplete={onUploadComplete} />);

    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Enviar Todos');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(onUploadComplete).toHaveBeenCalled();
    });
  });

  it('should integrate AdminDashboard with ApiClient', async () => {
    const mockMetricsResponse = {
      users: { total: 1000, active: 800 },
      executions: { total: 5000, successRate: 95 }
    };

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockMetricsResponse
    });

    const onRefresh = jest.fn();
    render(<AdminDashboard onRefresh={onRefresh} />);

    const refreshButton = screen.getByText('Atualizar');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(onRefresh).toHaveBeenCalled();
    });
  });
});

describe('Error Handling Tests', () => {
  it('should handle network errors gracefully', async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });

    await expect(client.get('/test')).rejects.toThrow('Network error');
  });

  it('should handle invalid JSON responses', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => {
        throw new Error('Invalid JSON');
      }
    });

    const client = new ApiClient({ baseURL: 'http://localhost:8000/api' });

    await expect(client.get('/test')).rejects.toThrow('Invalid JSON');
  });

  it('should handle file validation errors', async () => {
    const onError = jest.fn();
    render(<FileUpload maxSize={1} onError={onError} />);

    const largeFile = new File(['x'.repeat(1024)], 'large.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('Arquivo muito grande'));
    });
  });
});

describe('Performance Tests', () => {
  it('should handle large file lists efficiently', async () => {
    const onFilesSelected = jest.fn();
    render(<FileUpload multiple onFilesSelected={onFilesSelected} />);

    const files = Array.from({ length: 100 }, (_, i) => 
      new File(['content'], `file${i}.txt`, { type: 'text/plain' })
    );

    const input = screen.getByRole('button', { name: /selecionar arquivos/i });
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(fileInput, { target: { files } });

    await waitFor(() => {
      expect(onFilesSelected).toHaveBeenCalledWith(files);
    });
  });

  it('should handle rapid state updates', async () => {
    const onNavigate = jest.fn();
    render(<AdminDashboard onNavigate={onNavigate} />);

    const buttons = ['Visão Geral', 'Usuários', 'Sistema', 'Alertas'];

    for (const buttonText of buttons) {
      const button = screen.getByText(buttonText);
      fireEvent.click(button);
    }

    expect(onNavigate).toHaveBeenCalledTimes(4);
  });
}); 