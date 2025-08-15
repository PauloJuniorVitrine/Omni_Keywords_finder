import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';
import yaml from 'js-yaml';

interface UploadRegrasProps {
  onUpload: (regras: object) => void;
  regrasIniciais?: object;
}

const translations = {
  pt: {
    upload_label: 'Upload de regras (YAML ou JSON):',
    editor_label: 'Editor inline (YAML):',
    placeholder: 'Cole ou edite suas regras YAML aqui...',
    file_too_large: 'Arquivo muito grande (máx. 1MB)',
    file_type_invalid: 'Tipo de arquivo não suportado. Use YAML ou JSON.',
    content_too_long: 'Conteúdo muito extenso',
    structure_invalid: 'Estrutura inválida',
    structure_required: 'Regras devem conter: score_minimo (número), blacklist (array), whitelist (array)',
    file_invalid: 'Arquivo inválido:',
    yaml_invalid: 'YAML inválido:',
    loading: 'Carregando arquivo...'
  }
};
const t = (key: string) => translations.pt[key] || key;

const UploadRegras: React.FC<UploadRegrasProps> = ({ onUpload, regrasIniciais }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [conteudo, setConteudo] = useState<string>('');
  const [erro, setErro] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    if (file.size > 1024 * 1024) { // Limite de 1MB
      setErro('Arquivo muito grande (máx. 1MB)');
      setLoading(false);
      return;
    }
    if (!/\.(ya?ml|json)$/i.test(file.name)) {
      setErro('Tipo de arquivo não suportado. Use YAML ou JSON.');
      setLoading(false);
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setConteudo(text);
      setErro(null);
      try {
        if (text.length > 100000) throw new Error('Conteúdo muito extenso');
        const sanitized = text.replace(/<script.*?>.*?<\/script>/gi, '');
        const parsed = file.name.endsWith('.yaml') || file.name.endsWith('.yml')
          ? yaml.load(sanitized)
          : JSON.parse(sanitized);
        if (typeof parsed !== 'object' || !parsed) throw new Error('Estrutura inválida');
        if (
          typeof parsed.score_minimo !== 'number' ||
          !Array.isArray(parsed.blacklist) ||
          !Array.isArray(parsed.whitelist)
        ) {
          throw new Error('Regras devem conter: score_minimo (número), blacklist (array), whitelist (array)');
        }
        onUpload(parsed as object);
      } catch (err) {
        setErro('Arquivo inválido: ' + (err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsText(file);
  };

  const handleConteudoChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setConteudo(e.target.value);
    setErro(null);
    try {
      const parsed = yaml.load(e.target.value);
      if (
        typeof parsed !== 'object' || !parsed ||
        typeof (parsed as any).score_minimo !== 'number' ||
        !Array.isArray((parsed as any).blacklist) ||
        !Array.isArray((parsed as any).whitelist)
      ) {
        throw new Error('Regras devem conter: score_minimo (número), blacklist (array), whitelist (array)');
      }
      onUpload(parsed as object);
    } catch (err) {
      setErro('YAML inválido: ' + (err as Error).message);
    }
  };

  return (
    <div className="upload-regras">
      <label htmlFor="file-upload" style={{ display: 'block', marginBottom: 8 }}>
        {t('upload_label')}
      </label>
      <input
        id="file-upload"
        type="file"
        accept=".yaml,.yml,.json"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ marginBottom: 16 }}
        aria-label="Selecionar arquivo de regras YAML ou JSON"
        tabIndex={0}
        role="button"
      />
      <label htmlFor="editor-regras" style={{ display: 'block', marginBottom: 8 }}>
        {t('editor_label')}
      </label>
      <textarea
        id="editor-regras"
        value={conteudo}
        onChange={handleConteudoChange}
        rows={12}
        style={{ width: '100%', fontFamily: 'monospace', marginBottom: 8, background: '#fff', color: '#222', borderColor: '#333' }}
        placeholder={t('placeholder')}
        aria-label="Editor de regras YAML"
        tabIndex={0}
        role="textbox"
      />
      {erro && <div style={{ color: '#b00020', marginBottom: 8 }} role="alert" aria-live="assertive">{erro}</div>}
      {loading && <div style={{ color: '#333', marginBottom: 8 }} role="status" aria-live="polite">{t('loading')} <span className="spinner" style={{ display: 'inline-block', width: 16, height: 16, border: '2px solid #333', borderRadius: '50%', borderTop: '2px solid transparent', animation: 'spin 1s linear infinite' }} /></div>}
    </div>
  );
};

UploadRegras.propTypes = {
  onUpload: PropTypes.func.isRequired,
  regrasIniciais: PropTypes.object,
};

export default UploadRegras; 