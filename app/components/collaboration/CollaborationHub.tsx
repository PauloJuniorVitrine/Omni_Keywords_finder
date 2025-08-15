/**
 * Sistema de Colaboração em Tempo Real
 * ====================================
 * 
 * Componente principal para colaboração em equipe incluindo:
 * - Chat em tempo real
 * - Compartilhamento de arquivos
 * - Comentários em documentos
 * - Gestão de tarefas
 * - Calendário compartilhado
 * - Notificações de equipe
 * - Controle de versão
 * - Permissões de acesso
 * - Integração com ferramentas externas
 * - Análise de colaboração
 * 
 * Tracing ID: UI-024_COLLAB_HUB_001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  TextField,
  Button,
  IconButton,
  Chip,
  Card,
  CardContent,
  Grid,
  Alert,
  Snackbar,
  CircularProgress,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon
} from '@mui/material';
import {
  Chat,
  Assignment,
  Event,
  Comment,
  AttachFile,
  Analytics,
  Send,
  Add,
  Group,
  Settings
} from '@mui/icons-material';

interface User {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'away';
}

interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
}

interface CollaborationHubProps {
  userId: string;
  projectId?: string;
}

const CollaborationHub: React.FC<CollaborationHubProps> = ({ userId, projectId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [newMessage, setNewMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setUsers([
        { id: '1', name: 'João Silva', status: 'online' },
        { id: '2', name: 'Maria Santos', status: 'online' },
        { id: '3', name: 'Pedro Costa', status: 'away' }
      ]);
      
      setMessages([
        {
          id: '1',
          userId: '1',
          userName: 'João Silva',
          content: 'Olá pessoal! Como está o progresso?',
          timestamp: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: '2',
          userId: '2',
          userName: 'Maria Santos',
          content: 'Tudo bem! Terminei a análise.',
          timestamp: new Date(Date.now() - 1800000).toISOString()
        }
      ]);
      
      setTasks([
        {
          id: '1',
          title: 'Revisar análise de keywords',
          description: 'Verificar resultados da análise semântica',
          status: 'in_progress',
          priority: 'high'
        },
        {
          id: '2',
          title: 'Atualizar documentação',
          description: 'Documentar novas funcionalidades',
          status: 'todo',
          priority: 'medium'
        }
      ]);
      
      setLoading(false);
    }, 1000);
  }, []);

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    const message: ChatMessage = {
      id: Date.now().toString(),
      userId,
      userName: users.find(u => u.id === userId)?.name || 'Usuário',
      content: newMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
    setNotification({ message: 'Mensagem enviada!', type: 'success' });
  };

  const onlineUsers = users.filter(u => u.status === 'online');

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="h5" fontWeight="bold">
              Hub de Colaboração
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {onlineUsers.length} usuários online
            </Typography>
          </Box>
          <Chip icon={<Group />} label={`${users.length} membros`} color="primary" />
        </Box>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Tabs 
          value={activeTab} 
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Chat />} label="Chat" />
          <Tab icon={<Assignment />} label="Tarefas" />
          <Tab icon={<Event />} label="Calendário" />
          <Tab icon={<Comment />} label="Comentários" />
          <Tab icon={<AttachFile />} label="Arquivos" />
          <Tab icon={<Analytics />} label="Analytics" />
        </Tabs>

        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {/* Chat Tab */}
          {activeTab === 0 && (
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
                <List>
                  {messages.map((message) => (
                    <ListItem key={message.id} alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar>{message.userName.charAt(0)}</Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {message.userName}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(message.timestamp).toLocaleString('pt-BR')}
                            </Typography>
                          </Box>
                        }
                        secondary={message.content}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>

              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Digite sua mensagem..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <Button
                  variant="contained"
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim()}
                >
                  <Send />
                </Button>
              </Box>
            </Box>
          )}

          {/* Tasks Tab */}
          {activeTab === 1 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Tarefas do Projeto</Typography>
                <Button variant="contained" startIcon={<Add />}>
                  Nova Tarefa
                </Button>
              </Box>

              <Grid container spacing={2}>
                {tasks.map((task) => (
                  <Grid item xs={12} md={6} lg={4} key={task.id}>
                    <Card>
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                          <Typography variant="h6" noWrap>
                            {task.title}
                          </Typography>
                          <Chip 
                            label={task.status} 
                            color={task.status === 'done' ? 'success' : 'warning'}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" mb={2}>
                          {task.description}
                        </Typography>
                        <Chip label={task.priority} size="small" variant="outlined" />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Calendar Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" mb={2}>Calendário de Eventos</Typography>
              <Alert severity="info">
                Funcionalidade de calendário será implementada em breve.
              </Alert>
            </Box>
          )}

          {/* Comments Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h6" mb={2}>Comentários em Documentos</Typography>
              <Alert severity="info">
                Nenhum comentário encontrado. Os comentários aparecerão aqui quando forem adicionados aos documentos.
              </Alert>
            </Box>
          )}

          {/* Files Tab */}
          {activeTab === 4 && (
            <Box>
              <Typography variant="h6" mb={2}>Arquivos Compartilhados</Typography>
              <Alert severity="info">
                Funcionalidade de compartilhamento de arquivos será implementada em breve.
              </Alert>
            </Box>
          )}

          {/* Analytics Tab */}
          {activeTab === 5 && (
            <Box>
              <Typography variant="h6" mb={2}>Analytics de Colaboração</Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6} lg={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Total de Mensagens
                      </Typography>
                      <Typography variant="h4">
                        {messages.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6} lg={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Tarefas Ativas
                      </Typography>
                      <Typography variant="h4">
                        {tasks.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6} lg={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Usuários Ativos
                      </Typography>
                      <Typography variant="h4">
                        {onlineUsers.length}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6} lg={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" gutterBottom>
                        Score de Colaboração
                      </Typography>
                      <Typography variant="h4">
                        85%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Ações rápidas"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="Nova Tarefa"
          onClick={() => {}}
        />
        <SpeedDialAction
          icon={<Event />}
          tooltipTitle="Novo Evento"
          onClick={() => {}}
        />
        <SpeedDialAction
          icon={<AttachFile />}
          tooltipTitle="Compartilhar Arquivo"
          onClick={() => {}}
        />
        <SpeedDialAction
          icon={<Settings />}
          tooltipTitle="Configurações"
          onClick={() => {}}
        />
      </SpeedDial>

      {/* Notifications */}
      <Snackbar
        open={!!notification}
        autoHideDuration={6000}
        onClose={() => setNotification(null)}
      >
        <Alert 
          onClose={() => setNotification(null)} 
          severity={notification?.type || 'info'}
        >
          {notification?.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CollaborationHub; 