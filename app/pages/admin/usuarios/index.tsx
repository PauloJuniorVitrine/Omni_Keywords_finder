import React, { useState } from 'react';
import ActionButton from '../../../components/shared/ActionButton';
import ModalConfirm from '../../../components/shared/ModalConfirm';
import Badge from '../../../components/shared/Badge';
import Loader from '../../../components/shared/Loader';
import Toast from '../../../components/shared/Toast';

// Mock inicial de dados
const mockUsuarios = [
  { id: 1, nome: 'Admin', email: 'admin@exemplo.com', papel: 'admin', status: 'ativo' },
  { id: 2, nome: 'Gestor', email: 'gestor@exemplo.com', papel: 'gestor', status: 'ativo' },
  { id: 3, nome: 'Usuário', email: 'user@exemplo.com', papel: 'user', status: 'inativo' },
];

const UsuariosAdminPage: React.FC = () => {
  const [usuarios, setUsuarios] = useState(mockUsuarios);
  const [showModal, setShowModal] = useState(false);
  const [usuarioSelecionado, setUsuarioSelecionado] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Handlers simulados
  const handleDelete = (usuario: any) => {
    setUsuarioSelecionado(usuario);
    setShowModal(true);
  };
  const confirmDelete = () => {
    setLoading(true);
    setTimeout(() => {
      setUsuarios(usuarios.filter(u => u.id !== usuarioSelecionado.id));
      setShowModal(false);
      setLoading(false);
      setToast({ type: 'success', message: 'Usuário excluído com sucesso.' });
    }, 1000);
  };

  return (
    <div role="main" aria-label="Administração de Usuários" tabIndex={0}>
      <h1 aria-label="Título da página">Administração de Usuários, Papéis e Permissões</h1>
      <ActionButton label="Criar Usuário" variant="primary" onClick={() => setToast({ type: 'error', message: 'Funcionalidade não implementada.' })} />
      <table aria-label="Tabela de usuários" style={{ width: '100%', marginTop: 24 }}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Papel</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map(usuario => (
            <tr key={usuario.id}>
              <td>{usuario.nome}</td>
              <td>{usuario.email}</td>
              <td><Badge label={usuario.papel} color={usuario.papel === 'admin' ? '#4f8cff' : '#eab308'} /></td>
              <td><Badge label={usuario.status} color={usuario.status === 'ativo' ? '#22c55e' : '#ef4444'} /></td>
              <td>
                <ActionButton label="Editar" variant="secondary" onClick={() => setToast({ type: 'error', message: 'Funcionalidade não implementada.' })} />
                <ActionButton label="Excluir" variant="secondary" onClick={() => handleDelete(usuario)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {showModal && (
        <ModalConfirm
          open={showModal}
          message={`Deseja realmente excluir o usuário ${usuarioSelecionado?.nome}?`}
          onConfirm={confirmDelete}
          onCancel={() => setShowModal(false)}
        />
      )}
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}
    </div>
  );
};

export default UsuariosAdminPage; 