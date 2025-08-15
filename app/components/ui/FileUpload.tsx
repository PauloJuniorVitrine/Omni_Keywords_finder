/**
 * 📁 Componente FileUpload - Upload de Arquivos
 * 🎯 Objetivo: Interface moderna para upload de arquivos
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: FRONTEND_UI_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useRef, useCallback } from 'react';
import { cn } from '../../utils/cn';

// Ícones simples em SVG para evitar dependência externa
const UploadIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

const XIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const AlertCircleIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const LoaderIcon = () => (
  <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

interface FileUploadProps {
  /** Tipos de arquivo aceitos */
  accept?: string;
  /** Tamanho máximo em bytes */
  maxSize?: number;
  /** Múltiplos arquivos */
  multiple?: boolean;
  /** Callback quando arquivos são selecionados */
  onFilesSelected?: (files: File[]) => void;
  /** Callback quando upload é iniciado */
  onUploadStart?: (files: File[]) => void;
  /** Callback quando upload é concluído */
  onUploadComplete?: (results: UploadResult[]) => void;
  /** Callback quando há erro */
  onError?: (error: string) => void;
  /** Texto do botão */
  buttonText?: string;
  /** Texto de ajuda */
  helpText?: string;
  /** Desabilitado */
  disabled?: boolean;
  /** Classe CSS adicional */
  className?: string;
}

interface UploadResult {
  file: File;
  success: boolean;
  url?: string;
  error?: string;
}

interface FileWithProgress extends File {
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  accept = '*/*',
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = false,
  onFilesSelected,
  onUploadStart,
  onUploadComplete,
  onError,
  buttonText = 'Selecionar Arquivos',
  helpText = 'Arraste arquivos aqui ou clique para selecionar',
  disabled = false,
  className
}) => {
  const [files, setFiles] = useState<FileWithProgress[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Gerar ID único para arquivo
  const generateFileId = useCallback(() => {
    return Math.random().toString(36).substr(2, 9);
  }, []);

  // Validar arquivo
  const validateFile = useCallback((file: File): string | null => {
    // Verificar tamanho
    if (file.size > maxSize) {
      return `Arquivo muito grande. Máximo: ${(maxSize / 1024 / 1024).toFixed(1)}MB`;
    }

    // Verificar tipo (se especificado)
    if (accept !== '*/*') {
      const acceptedTypes = accept.split(',').map(type => type.trim());
      const fileType = file.type;
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      
      const isAccepted = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExtension === type;
        }
        return fileType === type || fileType.startsWith(type.replace('*', ''));
      });

      if (!isAccepted) {
        return `Tipo de arquivo não suportado. Aceitos: ${accept}`;
      }
    }

    return null;
  }, [accept, maxSize]);

  // Processar arquivos selecionados
  const processFiles = useCallback((selectedFiles: FileList | File[]) => {
    const fileArray = Array.from(selectedFiles);
    const validFiles: FileWithProgress[] = [];
    const errors: string[] = [];

    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(`${file.name}: ${error}`);
      } else {
        validFiles.push({
          ...file,
          id: generateFileId(),
          progress: 0,
          status: 'pending'
        });
      }
    });

    if (errors.length > 0) {
      onError?.(errors.join('\n'));
    }

    if (validFiles.length > 0) {
      setFiles(prev => multiple ? [...prev, ...validFiles] : validFiles);
      onFilesSelected?.(validFiles);
    }
  }, [validateFile, multiple, onFilesSelected, onError, generateFileId]);

  // Simular upload (substitua pela implementação real)
  const uploadFiles = useCallback(async (filesToUpload: FileWithProgress[]) => {
    setIsUploading(true);
    onUploadStart?.(filesToUpload);

    const results: UploadResult[] = [];

    for (const file of filesToUpload) {
      try {
        // Simular progresso
        for (let progress = 0; progress <= 100; progress += 10) {
          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? { ...f, progress, status: 'uploading' }
              : f
          ));
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Simular sucesso
        setFiles(prev => prev.map(f => 
          f.id === file.id 
            ? { ...f, progress: 100, status: 'success' }
            : f
        ));

        results.push({
          file,
          success: true,
          url: `https://example.com/uploads/${file.name}`
        });

      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === file.id 
            ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Erro desconhecido' }
            : f
        ));

        results.push({
          file,
          success: false,
          error: error instanceof Error ? error.message : 'Erro desconhecido'
        });
      }
    }

    setIsUploading(false);
    onUploadComplete?.(results);
  }, [onUploadStart, onUploadComplete]);

  // Handlers
  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      processFiles(selectedFiles);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFiles]);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = event.dataTransfer.files;
    if (droppedFiles) {
      processFiles(droppedFiles);
    }
  }, [processFiles]);

  const handleRemoveFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  const handleUpload = useCallback(() => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    if (pendingFiles.length > 0) {
      uploadFiles(pendingFiles);
    }
  }, [files, uploadFiles]);

  const handleClearAll = useCallback(() => {
    setFiles([]);
  }, []);

  // Renderizar ícone baseado no tipo de arquivo
  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'xls':
      case 'xlsx':
        return '📊';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️';
      case 'zip':
      case 'rar':
        return '📦';
      default:
        return '📁';
    }
  };

  // Renderizar status do arquivo
  const getFileStatus = (file: FileWithProgress) => {
    switch (file.status) {
      case 'pending':
        return <span className="text-gray-500">Pendente</span>;
      case 'uploading':
        return (
          <div className="flex items-center gap-2">
            <LoaderIcon />
            <span className="text-blue-600">Enviando... {file.progress}%</span>
          </div>
        );
      case 'success':
        return (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircleIcon />
            <span>Concluído</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircleIcon />
            <span>Erro</span>
          </div>
        );
    }
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Área de Upload */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
          isDragOver 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <UploadIcon />
        <p className="text-lg font-medium text-gray-900 mb-2">
          {buttonText}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          {helpText}
        </p>
        
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className={cn(
            'px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors',
            disabled && 'cursor-not-allowed opacity-50'
          )}
        >
          Selecionar Arquivos
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />
        
        <p className="text-xs text-gray-400 mt-2">
          Tipos aceitos: {accept === '*/*' ? 'Todos' : accept}
          <br />
          Tamanho máximo: {(maxSize / 1024 / 1024).toFixed(1)}MB
        </p>
      </div>

      {/* Lista de Arquivos */}
      {files.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Arquivos Selecionados ({files.length})
            </h3>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleUpload}
                disabled={isUploading || files.every(f => f.status !== 'pending')}
                className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {isUploading ? 'Enviando...' : 'Enviar Todos'}
              </button>
              <button
                type="button"
                onClick={handleClearAll}
                className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
              >
                Limpar Todos
              </button>
            </div>
          </div>

          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">{getFileIcon(file)}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {getFileStatus(file)}
                  
                  {file.status === 'uploading' && (
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={() => handleRemoveFile(file.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                    disabled={file.status === 'uploading'}
                  >
                    <XIcon />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Barra de Progresso Geral */}
          {isUploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>Progresso Geral</span>
                <span>
                  {files.filter(f => f.status === 'success').length} / {files.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${(files.filter(f => f.status === 'success').length / files.length) * 100}%`
                  }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUpload; 