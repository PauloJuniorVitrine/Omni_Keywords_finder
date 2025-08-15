import React, { useEffect, useState } from 'react';
import ActionButton from '../../components/shared/ActionButton';
import Loader from '../../components/shared/Loader';
import Tooltip from '../../components/shared/Tooltip_v1';
import Skeleton from '../../components/shared/Skeleton_v1';

interface Categoria {
  id: number;
  nome: string;
}

interface ExecucaoAgendada {
  id: number;
  categoria_id: number;
  palavras_chave: string[];
  cluster?: string;
  data_agendada: string;
  status: string;
  usuario?: string;
  criado_em: string;
  executado_em?: string;
  erro?: string;
}

const AgendarExecucao: React.FC = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriaId, setCategoriaId] = useState('');
  const [palavrasChave, setPalavrasChave] = useState('');
  const [cluster, setCluster] = useState('');
  const [dataAgendada, setDataAgendada] = useState('');
  const [usuario, setUsuario] = useState('');
  const [agendadas, setAgendadas] = useState<ExecucaoAgendada[]>([]);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [sugestoes, setSugestoes] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/categorias/1/')
      .then(async (res) => {
        if (!res.ok) throw new Error('Erro ao buscar categorias');
        const data = await res.json();
        setCategorias(data);
      });
    fetchAgendadas();
  }, []);

  useEffect(() => {
    if (!categoriaId) return;
    fetch(`/api/clusters/sugerir?categoria_id=${categoriaId}&palavras_chave=${encodeURIComponent(palavrasChave)}`)
      .then(async (res) => {
        if (!res.ok) return setSugestoes([]);
        const data = await res.json();
        setSugestoes(data.sugestoes || []);
      });
  }, [categoriaId, palavrasChave]);

  const fetchAgendadas = () => {
    fetch('/api/execucoes/agendadas')
      .then(async (res) => {
        if (!res.ok) throw new Error('Erro ao buscar execuções agendadas');
        const data = await res.json();
        setAgendadas(data);
      });
  };

  const handleAgendar = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErro(null);
    setMsg(null);
    fetch('/api/execucoes/agendar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        categoria_id: Number(categoriaId),
        palavras_chave: palavrasChave.split(',').map(s => s.trim()).filter(Boolean),
        cluster: cluster || undefined,
        data_agendada: dataAgendada,
        usuario: usuario || undefined,
      })
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.erro || 'Erro ao agendar execução');
        }
        setMsg('Execução agendada com sucesso!');
        setCategoriaId('');
        setPalavrasChave('');
        setCluster('');
        setDataAgendada('');
        setUsuario('');
        fetchAgendadas();
      })
      .catch((e) => setErro(e.message))
      .finally(() => setLoading(false));
  };

  const handleCancelar = (id: number) => {
    if (!window.confirm('Deseja cancelar este agendamento?')) return;
    fetch(`/api/execucoes/agendadas/${id}`, { method: 'DELETE' })
      .then(() => fetchAgendadas());
  };

  return (
    <section aria-labelledby="agendar-title" style={{ marginBottom: 40 }} data-testid="dashboard-agendar">
      <h2 id="agendar-title" style={{ fontSize: 22, marginBottom: 12 }} tabIndex={0}>Agendar Execução</h2>
      <form onSubmit={handleAgendar} style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
        <select required value={categoriaId} onChange={e => setCategoriaId(e.target.value)} style={{ minWidth: 180 }}>
          <option value="">Selecione a categoria</option>
          {categorias.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <input required type="text" placeholder="Palavras-chave (separadas por vírgula)" value={palavrasChave} onChange={e => setPalavrasChave(e.target.value)} style={{ minWidth: 220 }} />
        <input type="text" placeholder="Cluster (opcional)" value={cluster} onChange={e => setCluster(e.target.value)} style={{ minWidth: 120 }} list="sugestoes-cluster" autoComplete="off" />
        <datalist id="sugestoes-cluster">
          {sugestoes.map((s, i) => <option key={i} value={s} />)}
        </datalist>
        <input required type="datetime-local" value={dataAgendada} onChange={e => setDataAgendada(e.target.value)} style={{ minWidth: 180 }} />
        <input type="text" placeholder="Usuário (opcional)" value={usuario} onChange={e => setUsuario(e.target.value)} style={{ minWidth: 120 }} />
        <Tooltip content="Agendar execução" position="top">
          <ActionButton label={loading ? 'Agendando...' : 'Agendar'} variant="primary" disabled={loading} />
        </Tooltip>
      </form>
      {erro && <div style={{ color: 'orange', marginBottom: 8 }}>{erro}</div>}
      {msg && <div style={{ color: 'green', marginBottom: 8 }}>{msg}</div>}
      <h3 style={{ fontSize: 18, margin: '24px 0 8px 0' }}>Execuções Agendadas</h3>
      {loading ? (
        <div style={{ marginBottom: 12 }}>
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} variant="block" height={40} style={{ marginBottom: 8 }} />
          ))}
        </div>
      ) : (
        agendadas.length === 0 ? (
          <div style={{ color: '#888', fontSize: 16 }}>Nenhuma execução agendada.</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 8 }}>
            <thead>
              <tr style={{ background: '#f3f4f6' }}>
                <th>ID</th>
                <th>Categoria</th>
                <th>Palavras-chave</th>
                <th>Cluster</th>
                <th>Data Agendada</th>
                <th>Status</th>
                <th>Usuário</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {agendadas.map(a => (
                <tr key={a.id} style={{ borderBottom: '1px solid #eee', opacity: a.status === 'cancelada' ? 0.5 : 1 }}>
                  <td>{a.id}</td>
                  <td>{categorias.find(c => c.id === a.categoria_id)?.nome || a.categoria_id}</td>
                  <td>{a.palavras_chave.join(', ')}</td>
                  <td>{a.cluster}</td>
                  <td>{new Date(a.data_agendada).toLocaleString()}</td>
                  <td>{a.status}</td>
                  <td>{a.usuario}</td>
                  <td>
                    {(a.status === 'pendente' || a.status === 'erro') ? (
                      <Tooltip content="Cancelar execução agendada" position="top">
                        <ActionButton label="Cancelar" variant="secondary" onClick={() => handleCancelar(a.id)} />
                      </Tooltip>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      )}
    </section>
  );
};

export default AgendarExecucao; 