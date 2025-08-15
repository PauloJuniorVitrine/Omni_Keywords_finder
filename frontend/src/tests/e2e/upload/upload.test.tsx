/**
 * Testes E2E - Funcionalidade de Upload
 * 
 * Tracing ID: E2E_UPLOAD_TESTS_20250127_001
 * Data: 2025-01-27
 * Responsável: Frontend Team
 * 
 * Testes E2E baseados na funcionalidade de upload real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileUpload } from '../../../pages/FileUpload';
import { testUtils } from '../../unit/setup.test';

// Mock do ThemeProvider
jest.mock('../../../providers/ThemeProvider', () => ({
  useTheme: () => ({
    theme: 'light',
    tokens: {
      colors: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        danger: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
      }
    }
  })
}));

// Mock do serviço de upload
jest.mock('../../../services/uploadService', () => ({
  uploadKeywordsFile: jest.fn().mockResolvedValue({
    success: true,
    data: {
      id: 'upload_001',
      filename: 'keywords_analysis.csv',
      status: 'completed',
      keywordsCount: 150,
      processingTime: 2.5,
      results: {
        totalKeywords: 150,
        uniqueKeywords: 120,
        averageRelevance: 0.85,
        topKeywords: [
          { text: 'machine learning', frequency: 45, relevance: 0.95 },
          { text: 'python', frequency: 38, relevance: 0.92 },
          { text: 'data science', frequency: 32, relevance: 0.88 }
        ]
      }
    }
  })
}));

describe('E2E - Funcionalidade de Upload', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    // Limpa o localStorage antes de cada teste
    localStorage.clear();
  });

  describe('Fluxo Completo de Upload', () => {
    test('deve permitir upload de arquivo CSV com sucesso', async () => {
      render(<FileUpload />);
      
      // Verifica se a página de upload está carregada
      expect(screen.getByText(/upload keywords/i)).toBeInTheDocument();
      expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
      
      // Simula seleção de arquivo
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      // Verifica se o arquivo foi selecionado
      await waitFor(() => {
        expect(screen.getByText('keywords.csv')).toBeInTheDocument();
      });
      
      // Clica no botão de upload
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o upload foi iniciado
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
      });
      
      // Verifica se o upload foi concluído
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
        expect(screen.getByText(/150 keywords processed/i)).toBeInTheDocument();
      });
    });

    test('deve permitir upload de arquivo Excel com sucesso', async () => {
      render(<FileUpload />);
      
      // Simula seleção de arquivo Excel
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1\tkeyword2\tkeyword3'], 'keywords.xlsx', {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      await user.upload(fileInput, file);
      
      // Verifica se o arquivo foi selecionado
      await waitFor(() => {
        expect(screen.getByText('keywords.xlsx')).toBeInTheDocument();
      });
      
      // Clica no botão de upload
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o upload foi concluído
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
    });

    test('deve permitir upload de arquivo TXT com sucesso', async () => {
      render(<FileUpload />);
      
      // Simula seleção de arquivo TXT
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1\nkeyword2\nkeyword3'], 'keywords.txt', {
        type: 'text/plain'
      });
      
      await user.upload(fileInput, file);
      
      // Verifica se o arquivo foi selecionado
      await waitFor(() => {
        expect(screen.getByText('keywords.txt')).toBeInTheDocument();
      });
      
      // Clica no botão de upload
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o upload foi concluído
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Validação de Arquivos', () => {
    test('deve rejeitar arquivo com formato inválido', async () => {
      render(<FileUpload />);
      
      // Simula seleção de arquivo inválido
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['invalid content'], 'document.pdf', {
        type: 'application/pdf'
      });
      
      await user.upload(fileInput, file);
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/invalid file format/i)).toBeInTheDocument();
        expect(screen.getByText(/please select a csv, xlsx, or txt file/i)).toBeInTheDocument();
      });
      
      // Verifica se o botão de upload está desabilitado
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      expect(uploadButton).toBeDisabled();
    });

    test('deve rejeitar arquivo muito grande', async () => {
      render(<FileUpload />);
      
      // Simula arquivo muito grande (cria um arquivo de 11MB)
      const largeContent = 'a'.repeat(11 * 1024 * 1024); // 11MB
      const file = new File([largeContent], 'large_file.csv', {
        type: 'text/csv'
      });
      
      const fileInput = screen.getByLabelText(/choose file/i);
      await user.upload(fileInput, file);
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/file too large/i)).toBeInTheDocument();
        expect(screen.getByText(/maximum file size is 10mb/i)).toBeInTheDocument();
      });
    });

    test('deve rejeitar arquivo vazio', async () => {
      render(<FileUpload />);
      
      // Simula arquivo vazio
      const file = new File([''], 'empty_file.csv', {
        type: 'text/csv'
      });
      
      const fileInput = screen.getByLabelText(/choose file/i);
      await user.upload(fileInput, file);
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/file is empty/i)).toBeInTheDocument();
      });
    });
  });

  describe('Drag and Drop', () => {
    test('deve permitir upload via drag and drop', async () => {
      render(<FileUpload />);
      
      const dropZone = screen.getByTestId('drop-zone');
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      // Simula drag and drop
      fireEvent.dragEnter(dropZone);
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file]
        }
      });
      
      // Verifica se o arquivo foi aceito
      await waitFor(() => {
        expect(screen.getByText('keywords.csv')).toBeInTheDocument();
      });
    });

    test('deve rejeitar arquivo inválido via drag and drop', async () => {
      render(<FileUpload />);
      
      const dropZone = screen.getByTestId('drop-zone');
      const file = new File(['invalid content'], 'document.pdf', {
        type: 'application/pdf'
      });
      
      // Simula drag and drop de arquivo inválido
      fireEvent.dragEnter(dropZone);
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file]
        }
      });
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/invalid file format/i)).toBeInTheDocument();
      });
    });

    test('deve mostrar feedback visual durante drag', async () => {
      render(<FileUpload />);
      
      const dropZone = screen.getByTestId('drop-zone');
      
      // Simula drag enter
      fireEvent.dragEnter(dropZone);
      
      // Verifica se o feedback visual foi ativado
      expect(dropZone).toHaveClass('drag-over');
      
      // Simula drag leave
      fireEvent.dragLeave(dropZone);
      
      // Verifica se o feedback visual foi removido
      expect(dropZone).not.toHaveClass('drag-over');
    });
  });

  describe('Progresso e Feedback', () => {
    test('deve mostrar progresso durante upload', async () => {
      render(<FileUpload />);
      
      // Simula seleção de arquivo
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      // Clica no botão de upload
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o progresso é exibido
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
        expect(screen.getByTestId('progress-bar')).toBeInTheDocument();
      });
      
      // Verifica se o progresso foi concluído
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
    });

    test('deve mostrar mensagem de sucesso após upload', async () => {
      render(<FileUpload />);
      
      // Simula upload bem-sucedido
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica mensagem de sucesso
      await waitFor(() => {
        expect(screen.getByText(/upload completed successfully/i)).toBeInTheDocument();
        expect(screen.getByText(/150 keywords processed/i)).toBeInTheDocument();
        expect(screen.getByText(/processing time: 2.5s/i)).toBeInTheDocument();
      });
    });

    test('deve mostrar resumo dos resultados', async () => {
      render(<FileUpload />);
      
      // Simula upload bem-sucedido
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica resumo dos resultados
      await waitFor(() => {
        expect(screen.getByText(/total keywords: 150/i)).toBeInTheDocument();
        expect(screen.getByText(/unique keywords: 120/i)).toBeInTheDocument();
        expect(screen.getByText(/average relevance: 85%/i)).toBeInTheDocument();
      });
      
      // Verifica top keywords
      expect(screen.getByText('machine learning')).toBeInTheDocument();
      expect(screen.getByText('python')).toBeInTheDocument();
      expect(screen.getByText('data science')).toBeInTheDocument();
    });
  });

  describe('Navegação e Ações', () => {
    test('deve permitir navegar para dashboard após upload', async () => {
      render(<FileUpload />);
      
      // Simula upload bem-sucedido
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Aguarda conclusão do upload
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
      
      // Clica no botão para ir ao dashboard
      const dashboardButton = screen.getByRole('button', { name: /go to dashboard/i });
      await user.click(dashboardButton);
      
      // Verifica se navegou para o dashboard
      expect(window.location.pathname).toBe('/dashboard');
    });

    test('deve permitir fazer novo upload', async () => {
      render(<FileUpload />);
      
      // Simula upload bem-sucedido
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Aguarda conclusão do upload
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
      
      // Clica no botão para novo upload
      const newUploadButton = screen.getByRole('button', { name: /upload another file/i });
      await user.click(newUploadButton);
      
      // Verifica se voltou ao estado inicial
      expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
      expect(screen.queryByText(/upload completed/i)).not.toBeInTheDocument();
    });

    test('deve permitir cancelar upload em andamento', async () => {
      render(<FileUpload />);
      
      // Simula seleção de arquivo
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o upload foi iniciado
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
      });
      
      // Clica no botão de cancelar
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);
      
      // Verifica se o upload foi cancelado
      await waitFor(() => {
        expect(screen.getByText(/upload cancelled/i)).toBeInTheDocument();
      });
    });
  });

  describe('Acessibilidade E2E', () => {
    test('deve ser totalmente acessível por teclado', async () => {
      render(<FileUpload />);
      
      // Navega por teclado
      const fileInput = screen.getByLabelText(/choose file/i);
      fileInput.focus();
      
      // Simula seleção de arquivo via teclado
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      // Simula upload via teclado
      Object.defineProperty(fileInput, 'files', {
        value: [file]
      });
      
      fireEvent.change(fileInput);
      
      // Navega para o botão de upload
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      uploadButton.focus();
      
      // Ativa o botão via teclado
      fireEvent.keyDown(uploadButton, { key: 'Enter' });
      
      // Verifica se o upload foi iniciado
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
      });
    });

    test('deve ter labels e descrições adequadas', () => {
      render(<FileUpload />);
      
      // Verifica labels adequados
      expect(screen.getByLabelText(/choose file/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/upload keywords file/i)).toBeInTheDocument();
      
      // Verifica descrições
      expect(screen.getByText(/drag and drop your keywords file here/i)).toBeInTheDocument();
      expect(screen.getByText(/supported formats: csv, xlsx, txt/i)).toBeInTheDocument();
    });

    test('deve anunciar mudanças de estado para screen reader', async () => {
      render(<FileUpload />);
      
      // Simula upload
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      // Verifica se o estado foi anunciado
      await waitFor(() => {
        expect(screen.getByText('keywords.csv')).toBeInTheDocument();
      });
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o progresso foi anunciado
      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
      });
    });
  });

  describe('Tratamento de Erros', () => {
    test('deve tratar erro de rede durante upload', async () => {
      // Mock de erro de rede
      jest.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('Network error'));
      
      render(<FileUpload />);
      
      // Simula upload
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
      
      // Verifica se há opção de tentar novamente
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    test('deve tratar erro de servidor durante upload', async () => {
      // Mock de erro de servidor
      jest.spyOn(global, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      } as Response);
      
      render(<FileUpload />);
      
      // Simula upload
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica se o erro foi exibido
      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
        expect(screen.getByText(/server error/i)).toBeInTheDocument();
      });
    });

    test('deve permitir tentar novamente após erro', async () => {
      // Mock de erro seguido de sucesso
      const mockFetch = jest.spyOn(global, 'fetch')
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            success: true,
            data: {
              id: 'upload_001',
              filename: 'keywords.csv',
              status: 'completed',
              keywordsCount: 150
            }
          })
        } as Response);
      
      render(<FileUpload />);
      
      // Primeira tentativa - falha
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      await user.click(uploadButton);
      
      // Verifica erro
      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
      });
      
      // Tenta novamente
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      await user.click(tryAgainButton);
      
      // Verifica sucesso na segunda tentativa
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Performance E2E', () => {
    test('deve carregar rapidamente', () => {
      const startTime = performance.now();
      
      render(<FileUpload />);
      
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      
      expect(loadTime).toBeLessThan(100); // Menos de 100ms
    });

    test('deve processar upload rapidamente', async () => {
      render(<FileUpload />);
      
      const fileInput = screen.getByLabelText(/choose file/i);
      const file = new File(['keyword1,keyword2,keyword3'], 'keywords.csv', {
        type: 'text/csv'
      });
      
      await user.upload(fileInput, file);
      
      const uploadButton = screen.getByRole('button', { name: /upload/i });
      
      const startTime = performance.now();
      await user.click(uploadButton);
      
      await waitFor(() => {
        expect(screen.getByText(/upload completed/i)).toBeInTheDocument();
      });
      
      const endTime = performance.now();
      const uploadTime = endTime - startTime;
      
      expect(uploadTime).toBeLessThan(5000); // Menos de 5 segundos
    });
  });
}); 