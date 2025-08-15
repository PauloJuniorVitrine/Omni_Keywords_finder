/**
 * Testes Unitários - Componente FileUpload
 * Testa funcionalidades de upload, validação e processamento
 * 
 * @author Omni Keywords Finder Team
 * @version 1.0.0
 * @date 2025-01-27
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import userEvent from '@testing-library/user-event';
import FileUpload from '../components/FileUpload';

// Mock do Material-UI
const theme = createTheme();

// Mock das funções de callback
const mockOnFilesUploaded = jest.fn();
const mockOnFileProcessed = jest.fn();

// Wrapper para renderizar com tema
const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

// Mock de arquivo
const createMockFile = (name: string, content: string, size: number = 1024) => {
  const file = new File([content], name, { type: 'text/plain' });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('FileUpload Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização', () => {
    it('deve renderizar a área de upload corretamente', () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      expect(screen.getByText(/Arraste arquivos ou clique para selecionar/)).toBeInTheDocument();
      expect(screen.getByText(/Tipos suportados:/)).toBeInTheDocument();
      expect(screen.getByText(/Tamanho máximo:/)).toBeInTheDocument();
    });

    it('deve mostrar configurações personalizadas', () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          maxFiles={5}
          maxFileSize={1024 * 1024}
          allowedTypes={['.txt']}
        />
      );

      expect(screen.getByText(/Máximo: 5 arquivos/)).toBeInTheDocument();
      expect(screen.getByText(/Tamanho máximo: 1 MB/)).toBeInTheDocument();
      expect(screen.getByText(/Tipos suportados: .txt/)).toBeInTheDocument();
    });
  });

  describe('Upload de Arquivos', () => {
    it('deve permitir seleção de arquivos via input', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'palavra1\npalavra2\npalavra3');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      // Simular seleção de arquivo
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(mockOnFilesUploaded).toHaveBeenCalled();
      });
    });

    it('deve validar tipo de arquivo', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          allowedTypes={['.txt']}
        />
      );

      const file = createMockFile('test.pdf', 'conteudo', 1024);
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText(/Tipo de arquivo não suportado/)).toBeInTheDocument();
      });
    });

    it('deve validar tamanho do arquivo', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          maxFileSize={1024}
        />
      );

      const file = createMockFile('test.txt', 'conteudo', 2048);
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText(/Arquivo muito grande/)).toBeInTheDocument();
      });
    });

    it('deve validar limite de arquivos', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          maxFiles={1}
        />
      );

      const file1 = createMockFile('test1.txt', 'conteudo1');
      const file2 = createMockFile('test2.txt', 'conteudo2');

      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file1, file2] } });
      }

      await waitFor(() => {
        expect(screen.getByText(/Limite de arquivos atingido/)).toBeInTheDocument();
      });
    });
  });

  describe('Drag and Drop', () => {
    it('deve permitir drag and drop quando habilitado', () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          enableDragDrop={true}
        />
      );

      const dropZone = screen.getByText(/Arraste arquivos ou clique para selecionar/).closest('div');
      
      if (dropZone) {
        fireEvent.dragOver(dropZone);
        expect(dropZone).toHaveClass('MuiPaper-root');
      }
    });

    it('não deve permitir drag and drop quando desabilitado', () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          enableDragDrop={false}
        />
      );

      const dropZone = screen.getByText(/Arraste arquivos ou clique para selecionar/).closest('div');
      
      if (dropZone) {
        fireEvent.dragOver(dropZone);
        // Não deve mudar a aparência
        expect(dropZone).toHaveClass('MuiPaper-root');
      }
    });
  });

  describe('Lista de Arquivos', () => {
    it('deve mostrar arquivos carregados', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'palavra1\npalavra2');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText('test.txt')).toBeInTheDocument();
        expect(screen.getByText('2 linhas')).toBeInTheDocument();
      });
    });

    it('deve permitir remover arquivo', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        const removeButton = screen.getByLabelText('Remover');
        fireEvent.click(removeButton);
      });

      await waitFor(() => {
        expect(screen.getByText('Arquivo removido com sucesso!')).toBeInTheDocument();
      });
    });

    it('deve mostrar progresso de upload', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText('0% concluído')).toBeInTheDocument();
      });
    });
  });

  describe('Preview de Arquivos', () => {
    it('deve mostrar preview quando habilitado', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          showPreview={true}
        />
      );

      const file = createMockFile('test.txt', 'linha1\nlinha2\nlinha3');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        const previewButton = screen.getByLabelText('Visualizar');
        expect(previewButton).toBeInTheDocument();
      });
    });

    it('deve abrir dialog de preview', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          showPreview={true}
        />
      );

      const file = createMockFile('test.txt', 'linha1\nlinha2');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        const previewButton = screen.getByLabelText('Visualizar');
        fireEvent.click(previewButton);
      });

      await waitFor(() => {
        expect(screen.getByText('Visualizar: test.txt')).toBeInTheDocument();
        expect(screen.getByText('linha1')).toBeInTheDocument();
        expect(screen.getByText('linha2')).toBeInTheDocument();
      });
    });
  });

  describe('Processamento Automático', () => {
    it('deve processar automaticamente quando habilitado', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          autoProcess={true}
        />
      );

      const file = createMockFile('test.txt', 'palavra1\npalavra2');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(mockOnFilesUploaded).toHaveBeenCalled();
      });

      // Aguardar processamento automático
      await waitFor(() => {
        expect(mockOnFileProcessed).toHaveBeenCalled();
      }, { timeout: 5000 });
    });
  });

  describe('Botões de Ação', () => {
    it('deve mostrar botões de ação quando há arquivos', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText('Processar Todos')).toBeInTheDocument();
        expect(screen.getByText('Limpar Todos')).toBeInTheDocument();
      });
    });

    it('deve limpar todos os arquivos', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        const clearButton = screen.getByText('Limpar Todos');
        fireEvent.click(clearButton);
      });

      await waitFor(() => {
        expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
      });
    });
  });

  describe('Mensagens de Feedback', () => {
    it('deve mostrar mensagem de sucesso', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText('1 arquivo(s) carregado(s) com sucesso!')).toBeInTheDocument();
      });
    });

    it('deve mostrar mensagem de erro para arquivo inválido', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
          allowedTypes={['.txt']}
        />
      );

      const file = createMockFile('test.pdf', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByText(/Tipo de arquivo não suportado/)).toBeInTheDocument();
      });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados', () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      expect(screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ })).toBeInTheDocument();
    });

    it('deve ter tooltips nos botões de ação', async () => {
      renderWithTheme(
        <FileUpload
          onFilesUploaded={mockOnFilesUploaded}
          onFileProcessed={mockOnFileProcessed}
        />
      );

      const file = createMockFile('test.txt', 'conteudo');
      const input = screen.getByRole('button', { name: /Arraste arquivos ou clique para selecionar/ });

      fireEvent.click(input);

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [file] } });
      }

      await waitFor(() => {
        expect(screen.getByLabelText('Visualizar')).toBeInTheDocument();
        expect(screen.getByLabelText('Download')).toBeInTheDocument();
        expect(screen.getByLabelText('Remover')).toBeInTheDocument();
      });
    });
  });
}); 