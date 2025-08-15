import React, { useRef } from 'react';

interface PromptUploadProps {
  onUpload: (files: FileList) => void;
}

const PromptUpload: React.FC<PromptUploadProps> = ({ onUpload }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  return (
    <div style={{ padding: 16, border: '1px dashed #aaa', borderRadius: 8, textAlign: 'center' }}>
      <p>Arraste e solte arquivos .txt aqui ou</p>
      <button type="button" onClick={() => fileInputRef.current?.click()}>Selecionar arquivos</button>
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt"
        multiple
        style={{ display: 'none' }}
        onChange={e => e.target.files && onUpload(e.target.files)}
        aria-label="Upload de prompts .txt"
      />
    </div>
  );
};

export default PromptUpload; 