import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Card,
  CardContent,
  Grid,
  Alert,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Check,
  ArrowForward,
  ArrowBack,
  Person,
  Business,
  Settings,
  CloudUpload,
  IntegrationInstructions,
  School,
  Feedback,
  Save,
  Close,
  Help,
  Info,
  Warning,
  CheckCircle,
  PlayArrow,
  Pause,
  Stop
} from '@mui/icons-material';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ReactNode;
  required: boolean;
  completed: boolean;
}

interface UserProfile {
  name: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer' | 'guest';
  company?: string;
  experience: 'beginner' | 'intermediate' | 'advanced';
  goals: string[];
  preferences: {
    notifications: boolean;
    analytics: boolean;
    collaboration: boolean;
    automation: boolean;
  };
}

interface OnboardingWizardProps {
  userId: string;
  onComplete?: (profile: UserProfile) => void;
  onSkip?: () => void;
  className?: string;
}

const OnboardingWizard: React.FC<OnboardingWizardProps> = ({
  userId,
  onComplete,
  onSkip,
  className
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [profile, setProfile] = useState<UserProfile>({
    name: '',
    email: '',
    role: 'viewer',
    experience: 'beginner',
    goals: [],
    preferences: {
      notifications: true,
      analytics: true,
      collaboration: true,
      automation: false
    }
  });
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [progress, setProgress] = useState(0);

  const goals = [
    'Análise de Keywords',
    'Otimização de SEO',
    'Monitoramento de Performance',
    'Relatórios Automatizados',
    'Colaboração em Equipe',
    'Integração com APIs',
    'Machine Learning',
    'Automação de Processos'
  ];

  const roles = [
    { value: 'admin', label: 'Administrador', description: 'Acesso completo ao sistema' },
    { value: 'editor', label: 'Editor', description: 'Pode criar e editar conteúdo' },
    { value: 'viewer', label: 'Visualizador', description: 'Apenas visualização' },
    { value: 'guest', label: 'Convidado', description: 'Acesso limitado' }
  ];

  const experiences = [
    { value: 'beginner', label: 'Iniciante', description: 'Primeira vez usando o sistema' },
    { value: 'intermediate', label: 'Intermediário', description: 'Já usou sistemas similares' },
    { value: 'advanced', label: 'Avançado', description: 'Experiência com ferramentas avançadas' }
  ];

  useEffect(() => {
    // Calcular progresso baseado em steps completados
    const completedSteps = steps.filter(step => step.completed).length;
    setProgress((completedSteps / steps.length) * 100);
  }, [profile]);

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      // Simular salvamento
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (onComplete) {
        onComplete(profile);
      }
    } catch (error) {
      console.error('Erro ao completar onboarding:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    }
  };

  const updateProfile = (updates: Partial<UserProfile>) => {
    setProfile(prev => ({ ...prev, ...updates }));
  };

  const toggleGoal = (goal: string) => {
    setProfile(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }));
  };

  const updatePreference = (key: keyof UserProfile['preferences'], value: boolean) => {
    setProfile(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
  };

  // Componentes dos steps
  const WelcomeStep = (
    <Box>
      <Typography variant="h5" gutterBottom>
        Bem-vindo ao Omni Keywords Finder! 🚀
      </Typography>
      <Typography variant="body1" paragraph>
        Vamos configurar seu perfil para personalizar sua experiência e maximizar sua produtividade.
      </Typography>
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            O que você vai conseguir:
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText primary="Análise avançada de keywords" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText primary="Relatórios personalizados" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText primary="Colaboração em tempo real" />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText primary="Automação inteligente" />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );

  const ProfileStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Informações Básicas
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Nome Completo"
            value={profile.name}
            onChange={(e) => updateProfile({ name: e.target.value })}
            required
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={profile.email}
            onChange={(e) => updateProfile({ email: e.target.value })}
            required
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Empresa (opcional)"
            value={profile.company || ''}
            onChange={(e) => updateProfile({ company: e.target.value })}
            margin="normal"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Função</InputLabel>
            <Select
              value={profile.role}
              onChange={(e) => updateProfile({ role: e.target.value as any })}
              label="Função"
            >
              {roles.map((role) => (
                <MenuItem key={role.value} value={role.value}>
                  <Box>
                    <Typography variant="body2">{role.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {role.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Box>
  );

  const ExperienceStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Nível de Experiência
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Isso nos ajudará a personalizar a interface e funcionalidades para você.
      </Typography>
      <Grid container spacing={2}>
        {experiences.map((exp) => (
          <Grid item xs={12} md={4} key={exp.value}>
            <Card
              sx={{
                cursor: 'pointer',
                border: profile.experience === exp.value ? 2 : 1,
                borderColor: profile.experience === exp.value ? 'primary.main' : 'divider',
                '&:hover': {
                  borderColor: 'primary.main',
                  boxShadow: 2
                }
              }}
              onClick={() => updateProfile({ experience: exp.value as any })}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {exp.label}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {exp.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const GoalsStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Seus Objetivos
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Selecione os objetivos que mais se alinham com suas necessidades.
      </Typography>
      <Grid container spacing={1}>
        {goals.map((goal) => (
          <Grid item xs={12} sm={6} md={4} key={goal}>
            <Chip
              label={goal}
              onClick={() => toggleGoal(goal)}
              color={profile.goals.includes(goal) ? 'primary' : 'default'}
              variant={profile.goals.includes(goal) ? 'filled' : 'outlined'}
              sx={{ m: 0.5 }}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const PreferencesStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Preferências do Sistema
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Configure como você quer que o sistema funcione para você.
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={profile.preferences.notifications}
                onChange={(e) => updatePreference('notifications', e.target.checked)}
              />
            }
            label="Notificações em tempo real"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={profile.preferences.analytics}
                onChange={(e) => updatePreference('analytics', e.target.checked)}
              />
            }
            label="Dashboard de Analytics"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={profile.preferences.collaboration}
                onChange={(e) => updatePreference('collaboration', e.target.checked)}
              />
            }
            label="Ferramentas de Colaboração"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={profile.preferences.automation}
                onChange={(e) => updatePreference('automation', e.target.checked)}
              />
            }
            label="Automação Inteligente"
          />
        </Grid>
      </Grid>
    </Box>
  );

  const ImportStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Importar Dados Existentes
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Você pode importar dados de outras ferramentas para começar rapidamente.
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              CSV/Excel
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Importe listas de keywords
            </Typography>
            <Button variant="outlined" size="small">
              Selecionar Arquivo
            </Button>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <IntegrationInstructions sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              APIs Externas
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Conecte com Google Analytics
            </Typography>
            <Button variant="outlined" size="small">
              Configurar
            </Button>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Settings sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Configuração Manual
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Configure tudo manualmente
            </Typography>
            <Button variant="outlined" size="small">
              Pular
            </Button>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const TrainingStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Treinamento e Suporte
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Escolha como você prefere aprender sobre o sistema.
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <School sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Tutoriais Interativos</Typography>
            </Box>
            <Typography variant="body2" paragraph>
              Aprenda passo a passo com tutoriais guiados
            </Typography>
            <Button variant="contained" size="small" startIcon={<PlayArrow />}>
              Iniciar Tutorial
            </Button>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <Help sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Centro de Ajuda</Typography>
            </Box>
            <Typography variant="body2" paragraph>
              Acesse documentação e FAQs
            </Typography>
            <Button variant="outlined" size="small">
              Explorar
            </Button>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const ReviewStep = (
    <Box>
      <Typography variant="h6" gutterBottom>
        Revisão Final
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Confirme suas configurações antes de finalizar.
      </Typography>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Perfil
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2">
                <strong>Nome:</strong> {profile.name}
              </Typography>
              <Typography variant="body2">
                <strong>Email:</strong> {profile.email}
              </Typography>
              <Typography variant="body2">
                <strong>Função:</strong> {roles.find(r => r.value === profile.role)?.label}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2">
                <strong>Experiência:</strong> {experiences.find(e => e.value === profile.experience)?.label}
              </Typography>
              <Typography variant="body2">
                <strong>Objetivos:</strong> {profile.goals.length} selecionados
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      <Alert severity="info">
        Você pode alterar essas configurações a qualquer momento nas configurações do perfil.
      </Alert>
    </Box>
  );

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Bem-vindo',
      description: 'Introdução ao sistema',
      component: WelcomeStep,
      required: false,
      completed: true
    },
    {
      id: 'profile',
      title: 'Perfil',
      description: 'Informações básicas',
      component: ProfileStep,
      required: true,
      completed: !!profile.name && !!profile.email
    },
    {
      id: 'experience',
      title: 'Experiência',
      description: 'Nível de conhecimento',
      component: ExperienceStep,
      required: true,
      completed: !!profile.experience
    },
    {
      id: 'goals',
      title: 'Objetivos',
      description: 'Seus objetivos principais',
      component: GoalsStep,
      required: false,
      completed: profile.goals.length > 0
    },
    {
      id: 'preferences',
      title: 'Preferências',
      description: 'Configurações do sistema',
      component: PreferencesStep,
      required: false,
      completed: true
    },
    {
      id: 'import',
      title: 'Importação',
      description: 'Dados existentes',
      component: ImportStep,
      required: false,
      completed: true
    },
    {
      id: 'training',
      title: 'Treinamento',
      description: 'Aprenda o sistema',
      component: TrainingStep,
      required: false,
      completed: true
    },
    {
      id: 'review',
      title: 'Revisão',
      description: 'Confirme configurações',
      component: ReviewStep,
      required: true,
      completed: steps?.filter(s => s.required).every(s => s.completed) || false
    }
  ];

  const canProceed = steps[activeStep]?.completed || !steps[activeStep]?.required;
  const isLastStep = activeStep === steps.length - 1;

  return (
    <Box className={className} sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Paper sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              Configuração Inicial
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Passo {activeStep + 1} de {steps.length}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Tooltip title="Ajuda">
              <IconButton onClick={() => setShowHelp(true)}>
                <Help />
              </IconButton>
            </Tooltip>
            <Button variant="outlined" onClick={handleSkip}>
              Pular
            </Button>
          </Box>
        </Box>

        {/* Progress Bar */}
        <Box mb={3}>
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {Math.round(progress)}% completo
          </Typography>
        </Box>

        {/* Stepper */}
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.id}>
              <StepLabel
                optional={!step.required}
                icon={step.completed ? <Check /> : index + 1}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="h6">{step.title}</Typography>
                  {step.required && <Chip label="Obrigatório" size="small" color="error" />}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
              <StepContent>
                <Box sx={{ mb: 2 }}>
                  {step.component}
                </Box>
                <Box display="flex" gap={1}>
                  <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                    startIcon={<ArrowBack />}
                  >
                    Voltar
                  </Button>
                  <Box sx={{ flex: '1 1 auto' }} />
                  {isLastStep ? (
                    <Button
                      variant="contained"
                      onClick={handleComplete}
                      disabled={!canProceed || loading}
                      startIcon={loading ? <CircularProgress size={16} /> : <Check />}
                    >
                      {loading ? 'Finalizando...' : 'Finalizar'}
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      onClick={handleNext}
                      disabled={!canProceed}
                      endIcon={<ArrowForward />}
                    >
                      Próximo
                    </Button>
                  )}
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Help Dialog */}
      <Dialog open={showHelp} onClose={() => setShowHelp(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Help color="primary" />
            <Typography variant="h6">Ajuda - Configuração Inicial</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Este assistente irá ajudá-lo a configurar o Omni Keywords Finder de acordo com suas necessidades.
          </Typography>
          <Typography variant="h6" gutterBottom>
            Passos do Assistente:
          </Typography>
          <List>
            {steps.map((step, index) => (
              <ListItem key={step.id}>
                <ListItemIcon>
                  <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                    {index + 1}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={step.title}
                  secondary={step.description}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHelp(false)}>
            Fechar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OnboardingWizard; 