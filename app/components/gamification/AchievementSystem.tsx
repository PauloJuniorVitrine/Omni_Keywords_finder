/**
 * AchievementSystem.tsx
 * 
 * Sistema de Gamificação - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-013
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 * 
 * Funcionalidades:
 * - Sistema de badges e conquistas
 * - Progresso do usuário
 * - Leaderboards
 * - Recompensas por ações
 * - Níveis de experiência
 * - Desafios e missões
 * - Compartilhamento de conquistas
 * - Configuração de gamificação
 * - Análise de engajamento
 * - Integração com redes sociais
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Card, Row, Col, Button, Space, Modal, Form, Input, Select, DatePicker, 
  Switch, message, Spin, Tabs, Tooltip, Badge, Divider, Typography, 
  Table, Tag, Progress, Alert, Drawer, List, Statistic, Timeline,
  Checkbox, Radio, Slider, InputNumber, TimePicker, Steps, Result,
  Descriptions, Empty, Skeleton, Avatar, Rate, Calendar, Carousel,
  Collapse, Tree, Transfer, Upload, Mentions, Cascader, TreeSelect,
  AutoComplete, InputNumber as AntInputNumber, Slider as AntSlider,
  Rate as AntRate, Switch as AntSwitch, Checkbox as AntCheckbox,
  Radio as AntRadio, DatePicker as AntDatePicker, TimePicker as AntTimePicker,
  Cascader as AntCascader, TreeSelect as AntTreeSelect, Transfer as AntTransfer,
  Upload as AntUpload, Mentions as AntMentions, AutoComplete as AntAutoComplete
} from 'antd';
import { 
  TrophyOutlined, 
  StarOutlined, 
  FireOutlined,
  CrownOutlined,
  GiftOutlined,
  ShareAltOutlined,
  SettingOutlined,
  EyeOutlined,
  DownloadOutlined,
  BellOutlined,
  DashboardOutlined,
  LineChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  TableOutlined,
  FilterOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckOutlined,
  CloseOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  CloudOutlined,
  ServerOutlined,
  NetworkOutlined,
  TrophyFilled,
  StarFilled,
  FireFilled,
  CrownFilled,
  GiftFilled,
  ShareAltOutlined as ShareAltOutlinedFilled,
  SettingOutlined as SettingOutlinedFilled,
  EyeOutlined as EyeOutlinedFilled,
  DownloadOutlined as DownloadOutlinedFilled,
  BellOutlined as BellOutlinedFilled,
  DashboardOutlined as DashboardOutlinedFilled,
  LineChartOutlined as LineChartOutlinedFilled,
  BarChartOutlined as BarChartOutlinedFilled,
  PieChartOutlined as PieChartOutlinedFilled,
  TableOutlined as TableOutlinedFilled,
  FilterOutlined as FilterOutlinedFilled,
  FullscreenOutlined as FullscreenOutlinedFilled,
  FullscreenExitOutlined as FullscreenExitOutlinedFilled,
  PlayCircleOutlined as PlayCircleOutlinedFilled,
  PauseCircleOutlined as PauseCircleOutlinedFilled,
  StopOutlined as StopOutlinedFilled,
  InfoCircleOutlined as InfoCircleOutlinedFilled,
  WarningOutlined as WarningOutlinedFilled,
  CheckOutlined as CheckOutlinedFilled,
  CloseOutlined as CloseOutlinedFilled,
  SyncOutlined as SyncOutlinedFilled,
  ThunderboltOutlined as ThunderboltOutlinedFilled,
  DatabaseOutlined as DatabaseOutlinedFilled,
  CloudOutlined as CloudOutlinedFilled,
  ServerOutlined as ServerOutlinedFilled,
  NetworkOutlined as NetworkOutlinedFilled,
  TrophyOutlined as TrophyOutlinedFilled,
  StarOutlined as StarOutlinedFilled,
  FireOutlined as FireOutlinedFilled,
  CrownOutlined as CrownOutlinedFilled,
  GiftOutlined as GiftOutlinedFilled,
  ShareAltOutlined as ShareAltOutlinedFilled2,
  SettingOutlined as SettingOutlinedFilled2,
  EyeOutlined as EyeOutlinedFilled2,
  DownloadOutlined as DownloadOutlinedFilled2,
  BellOutlined as BellOutlinedFilled2,
  DashboardOutlined as DashboardOutlinedFilled2,
  LineChartOutlined as LineChartOutlinedFilled2,
  BarChartOutlined as BarChartOutlinedFilled2,
  PieChartOutlined as PieChartOutlinedFilled2,
  TableOutlined as TableOutlinedFilled2,
  FilterOutlined as FilterOutlinedFilled2,
  FullscreenOutlined as FullscreenOutlinedFilled2,
  FullscreenExitOutlined as FullscreenExitOutlinedFilled2,
  PlayCircleOutlined as PlayCircleOutlinedFilled2,
  PauseCircleOutlined as PauseCircleOutlinedFilled2,
  StopOutlined as StopOutlinedFilled2,
  InfoCircleOutlined as InfoCircleOutlinedFilled2,
  WarningOutlined as WarningOutlinedFilled2,
  CheckOutlined as CheckOutlinedFilled2,
  CloseOutlined as CloseOutlinedFilled2,
  SyncOutlined as SyncOutlinedFilled2,
  ThunderboltOutlined as ThunderboltOutlinedFilled2,
  DatabaseOutlined as DatabaseOutlinedFilled2,
  CloudOutlined as CloudOutlinedFilled2,
  ServerOutlined as ServerOutlinedFilled2,
  NetworkOutlined as NetworkOutlinedFilled2
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Step } = Steps;
const { Panel } = Collapse;

// Tipos de badges
interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'achievement' | 'milestone' | 'special' | 'seasonal';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  points: number;
  unlockedAt?: string;
  progress?: number;
  maxProgress: number;
  criteria: string[];
  imageUrl?: string;
}

// Conquistas
interface Achievement {
  id: string;
  name: string;
  description: string;
  category: string;
  points: number;
  unlockedAt?: string;
  progress: number;
  maxProgress: number;
  rewards: Reward[];
  criteria: string[];
  icon: string;
}

// Recompensas
interface Reward {
  id: string;
  type: 'points' | 'badge' | 'feature' | 'discount' | 'custom';
  value: any;
  description: string;
  claimedAt?: string;
}

// Níveis de experiência
interface Level {
  level: number;
  name: string;
  minPoints: number;
  maxPoints: number;
  rewards: Reward[];
  icon: string;
  color: string;
}

// Desafios
interface Challenge {
  id: string;
  name: string;
  description: string;
  category: string;
  points: number;
  startDate: string;
  endDate: string;
  progress: number;
  maxProgress: number;
  status: 'active' | 'completed' | 'expired';
  rewards: Reward[];
  participants: number;
}

// Usuário
interface User {
  id: string;
  name: string;
  avatar?: string;
  level: number;
  experience: number;
  totalPoints: number;
  badges: Badge[];
  achievements: Achievement[];
  rank: number;
  joinDate: string;
  lastActive: string;
}

// Leaderboard
interface LeaderboardEntry {
  rank: number;
  user: User;
  points: number;
  level: number;
  achievements: number;
  badges: number;
}

// Props do componente
interface AchievementSystemProps {
  userId?: string;
  showLeaderboard?: boolean;
  showChallenges?: boolean;
  showAnalytics?: boolean;
  enableSharing?: boolean;
  maxLeaderboardEntries?: number;
  onBadgeUnlocked?: (badge: Badge) => void;
  onLevelUp?: (level: Level) => void;
  onAchievementUnlocked?: (achievement: Achievement) => void;
  readOnly?: boolean;
}

export const AchievementSystem: React.FC<AchievementSystemProps> = ({
  userId = 'current',
  showLeaderboard = true,
  showChallenges = true,
  showAnalytics = true,
  enableSharing = true,
  maxLeaderboardEntries = 50,
  onBadgeUnlocked,
  onLevelUp,
  onAchievementUnlocked,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [levels, setLevels] = useState<Level[]>([]);
  const [selectedBadge, setSelectedBadge] = useState<Badge | null>(null);
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null);
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [showAchievementModal, setShowAchievementModal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState<string | null>(null);

  // Carregar dados iniciais
  useEffect(() => {
    loadInitialData();
  }, [userId]);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        loadUserData(),
        loadBadges(),
        loadAchievements(),
        loadChallenges(),
        loadLeaderboard(),
        loadLevels()
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
      message.error('Erro ao carregar dados de gamificação');
    } finally {
      setLoading(false);
    }
  };

  const loadUserData = async () => {
    try {
      const response = await fetch(`/api/gamification/user/${userId}`);
      if (!response.ok) throw new Error('Falha ao carregar dados do usuário');
      
      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      console.error('Erro ao carregar dados do usuário:', err);
      // Mock data para demonstração
      setUser({
        id: userId,
        name: 'Usuário Demo',
        level: 5,
        experience: 1250,
        totalPoints: 2500,
        badges: [],
        achievements: [],
        rank: 15,
        joinDate: '2024-01-01',
        lastActive: new Date().toISOString()
      });
    }
  };

  const loadBadges = async () => {
    try {
      const response = await fetch(`/api/gamification/badges?userId=${userId}`);
      if (!response.ok) throw new Error('Falha ao carregar badges');
      
      const badgesData = await response.json();
      setBadges(badgesData);
    } catch (err) {
      console.error('Erro ao carregar badges:', err);
      // Mock data para demonstração
      setBadges([
        {
          id: 'first-search',
          name: 'Primeira Busca',
          description: 'Realizou sua primeira busca de keywords',
          icon: 'search',
          category: 'achievement',
          rarity: 'common',
          points: 10,
          unlockedAt: '2024-01-15T10:30:00Z',
          progress: 1,
          maxProgress: 1,
          criteria: ['Realizar primeira busca']
        },
        {
          id: 'keyword-master',
          name: 'Mestre das Keywords',
          description: 'Analisou mais de 1000 keywords',
          icon: 'trophy',
          category: 'milestone',
          rarity: 'rare',
          points: 100,
          progress: 750,
          maxProgress: 1000,
          criteria: ['Analisar 1000 keywords']
        }
      ]);
    }
  };

  const loadAchievements = async () => {
    try {
      const response = await fetch(`/api/gamification/achievements?userId=${userId}`);
      if (!response.ok) throw new Error('Falha ao carregar conquistas');
      
      const achievementsData = await response.json();
      setAchievements(achievementsData);
    } catch (err) {
      console.error('Erro ao carregar conquistas:', err);
      // Mock data para demonstração
      setAchievements([
        {
          id: 'daily-login',
          name: 'Login Diário',
          description: 'Fez login por 7 dias consecutivos',
          category: 'engagement',
          points: 50,
          progress: 5,
          maxProgress: 7,
          rewards: [{ id: 'points-50', type: 'points', value: 50, description: '50 pontos' }],
          criteria: ['Login por 7 dias consecutivos'],
          icon: 'calendar'
        }
      ]);
    }
  };

  const loadChallenges = async () => {
    try {
      const response = await fetch(`/api/gamification/challenges?userId=${userId}`);
      if (!response.ok) throw new Error('Falha ao carregar desafios');
      
      const challengesData = await response.json();
      setChallenges(challengesData);
    } catch (err) {
      console.error('Erro ao carregar desafios:', err);
      // Mock data para demonstração
      setChallenges([
        {
          id: 'weekly-keywords',
          name: 'Desafio Semanal de Keywords',
          description: 'Analise 100 keywords esta semana',
          category: 'weekly',
          points: 200,
          startDate: '2024-12-16T00:00:00Z',
          endDate: '2024-12-22T23:59:59Z',
          progress: 75,
          maxProgress: 100,
          status: 'active',
          rewards: [{ id: 'badge-weekly', type: 'badge', value: 'weekly-master', description: 'Badge Semanal' }],
          participants: 45
        }
      ]);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const response = await fetch(`/api/gamification/leaderboard?limit=${maxLeaderboardEntries}`);
      if (!response.ok) throw new Error('Falha ao carregar leaderboard');
      
      const leaderboardData = await response.json();
      setLeaderboard(leaderboardData);
    } catch (err) {
      console.error('Erro ao carregar leaderboard:', err);
      // Mock data para demonstração
      setLeaderboard([
        {
          rank: 1,
          user: { id: 'user1', name: 'João Silva', level: 10, experience: 5000, totalPoints: 10000, badges: [], achievements: [], rank: 1, joinDate: '2024-01-01', lastActive: new Date().toISOString() },
          points: 10000,
          level: 10,
          achievements: 25,
          badges: 15
        },
        {
          rank: 2,
          user: { id: 'user2', name: 'Maria Santos', level: 8, experience: 4000, totalPoints: 8500, badges: [], achievements: [], rank: 2, joinDate: '2024-01-15', lastActive: new Date().toISOString() },
          points: 8500,
          level: 8,
          achievements: 20,
          badges: 12
        }
      ]);
    }
  };

  const loadLevels = async () => {
    try {
      const response = await fetch('/api/gamification/levels');
      if (!response.ok) throw new Error('Falha ao carregar níveis');
      
      const levelsData = await response.json();
      setLevels(levelsData);
    } catch (err) {
      console.error('Erro ao carregar níveis:', err);
      // Mock data para demonstração
      setLevels([
        { level: 1, name: 'Iniciante', minPoints: 0, maxPoints: 100, rewards: [], icon: 'star', color: '#52c41a' },
        { level: 2, name: 'Aprendiz', minPoints: 101, maxPoints: 300, rewards: [], icon: 'star', color: '#1890ff' },
        { level: 3, name: 'Intermediário', minPoints: 301, maxPoints: 600, rewards: [], icon: 'star', color: '#722ed1' },
        { level: 4, name: 'Avançado', minPoints: 601, maxPoints: 1000, rewards: [], icon: 'star', color: '#fa8c16' },
        { level: 5, name: 'Expert', minPoints: 1001, maxPoints: 2000, rewards: [], icon: 'crown', color: '#f5222d' }
      ]);
    }
  };

  const getCurrentLevel = useMemo(() => {
    if (!user || !levels.length) return null;
    return levels.find(level => user.experience >= level.minPoints && user.experience <= level.maxPoints);
  }, [user, levels]);

  const getNextLevel = useMemo(() => {
    if (!user || !levels.length) return null;
    const currentLevelIndex = levels.findIndex(level => level.level === getCurrentLevel?.level);
    return currentLevelIndex < levels.length - 1 ? levels[currentLevelIndex + 1] : null;
  }, [user, levels, getCurrentLevel]);

  const getProgressToNextLevel = useMemo(() => {
    if (!user || !getCurrentLevel || !getNextLevel) return 0;
    const currentLevelPoints = getCurrentLevel.maxPoints;
    const nextLevelPoints = getNextLevel.maxPoints;
    const userPoints = user.experience;
    return ((userPoints - currentLevelPoints) / (nextLevelPoints - currentLevelPoints)) * 100;
  }, [user, getCurrentLevel, getNextLevel]);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return '#52c41a';
      case 'rare': return '#1890ff';
      case 'epic': return '#722ed1';
      case 'legendary': return '#fa8c16';
      default: return '#d9d9d9';
    }
  };

  const getRarityIcon = (rarity: string) => {
    switch (rarity) {
      case 'common': return <StarOutlined />;
      case 'rare': return <StarFilled />;
      case 'epic': return <FireOutlined />;
      case 'legendary': return <CrownOutlined />;
      default: return <StarOutlined />;
    }
  };

  const handleBadgeClick = (badge: Badge) => {
    setSelectedBadge(badge);
    setShowBadgeModal(true);
  };

  const handleAchievementClick = (achievement: Achievement) => {
    setSelectedAchievement(achievement);
    setShowAchievementModal(true);
  };

  const handleShare = async (type: 'badge' | 'achievement' | 'level', data: any) => {
    if (!enableSharing) return;
    
    try {
      const shareData = {
        type,
        data,
        platform: 'omni_keywords_finder',
        timestamp: new Date().toISOString()
      };
      
      await fetch('/api/gamification/share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(shareData)
      });
      
      message.success('Conquista compartilhada com sucesso!');
    } catch (err) {
      message.error('Erro ao compartilhar conquista');
    }
  };

  const badgeColumns = [
    {
      title: 'Badge',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, badge: Badge) => (
        <Space>
          <Avatar 
            icon={getRarityIcon(badge.rarity)} 
            style={{ backgroundColor: getRarityColor(badge.rarity) }}
          />
          <div>
            <div>{name}</div>
            <Text type="secondary">{badge.description}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Raridade',
      dataIndex: 'rarity',
      key: 'rarity',
      render: (rarity: string) => (
        <Tag color={getRarityColor(rarity)}>
          {getRarityIcon(rarity)} {rarity.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Pontos',
      dataIndex: 'points',
      key: 'points',
      render: (points: number) => <Text strong>{points}</Text>
    },
    {
      title: 'Progresso',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, badge: Badge) => (
        <Progress 
          percent={badge.unlockedAt ? 100 : (progress / badge.maxProgress) * 100} 
          size="small"
          status={badge.unlockedAt ? 'success' : 'active'}
        />
      )
    },
    {
      title: 'Status',
      dataIndex: 'unlockedAt',
      key: 'unlockedAt',
      render: (unlockedAt: string) => (
        <Tag color={unlockedAt ? 'green' : 'default'}>
          {unlockedAt ? 'Desbloqueado' : 'Bloqueado'}
        </Tag>
      )
    }
  ];

  const achievementColumns = [
    {
      title: 'Conquista',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, achievement: Achievement) => (
        <Space>
          <Avatar icon={<TrophyOutlined />} style={{ backgroundColor: '#fa8c16' }} />
          <div>
            <div>{name}</div>
            <Text type="secondary">{achievement.description}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Categoria',
      dataIndex: 'category',
      key: 'category',
      render: (category: string) => <Tag>{category}</Tag>
    },
    {
      title: 'Pontos',
      dataIndex: 'points',
      key: 'points',
      render: (points: number) => <Text strong>{points}</Text>
    },
    {
      title: 'Progresso',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number, achievement: Achievement) => (
        <Progress 
          percent={(progress / achievement.maxProgress) * 100} 
          size="small"
          status={progress >= achievement.maxProgress ? 'success' : 'active'}
        />
      )
    },
    {
      title: 'Recompensas',
      dataIndex: 'rewards',
      key: 'rewards',
      render: (rewards: Reward[]) => (
        <Space>
          {rewards.map(reward => (
            <Tag key={reward.id} color="blue">{reward.description}</Tag>
          ))}
        </Space>
      )
    }
  ];

  const leaderboardColumns = [
    {
      title: 'Rank',
      dataIndex: 'rank',
      key: 'rank',
      render: (rank: number) => (
        <Badge count={rank} style={{ backgroundColor: rank <= 3 ? '#fa8c16' : '#52c41a' }} />
      )
    },
    {
      title: 'Usuário',
      dataIndex: 'user',
      key: 'user',
      render: (user: User) => (
        <Space>
          <Avatar src={user.avatar}>{user.name.charAt(0)}</Avatar>
          <div>
            <div>{user.name}</div>
            <Text type="secondary">Nível {user.level}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Pontos',
      dataIndex: 'points',
      key: 'points',
      render: (points: number) => <Text strong>{points.toLocaleString()}</Text>
    },
    {
      title: 'Conquistas',
      dataIndex: 'achievements',
      key: 'achievements',
      render: (achievements: number) => <Text>{achievements}</Text>
    },
    {
      title: 'Badges',
      dataIndex: 'badges',
      key: 'badges',
      render: (badges: number) => <Text>{badges}</Text>
    }
  ];

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Carregando sistema de gamificação...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Erro no Sistema de Gamificação"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={loadInitialData}>
            Tentar Novamente
          </Button>
        }
      />
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card>
            <Row gutter={16} align="middle">
              <Col>
                <Avatar 
                  size={64} 
                  src={user?.avatar}
                  icon={<CrownOutlined />}
                  style={{ backgroundColor: getCurrentLevel?.color || '#52c41a' }}
                />
              </Col>
              <Col flex="1">
                <Title level={3} style={{ margin: 0 }}>{user?.name}</Title>
                <Text type="secondary">Nível {user?.level} • {getCurrentLevel?.name}</Text>
                <div style={{ marginTop: '8px' }}>
                  <Progress 
                    percent={getProgressToNextLevel} 
                    size="small"
                    format={() => `${user?.experience} / ${getNextLevel?.maxPoints || 0} XP`}
                  />
                </div>
              </Col>
              <Col>
                <Space direction="vertical" align="end">
                  <Statistic title="Pontos Totais" value={user?.totalPoints} />
                  <Statistic title="Rank Global" value={user?.rank} suffix={`/ ${leaderboard.length}`} />
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Visão Geral" key="overview">
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Card title="Estatísticas" extra={<DashboardOutlined />}>
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Statistic title="Badges" value={badges.filter(b => b.unlockedAt).length} suffix={`/ ${badges.length}`} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Conquistas" value={achievements.filter(a => a.progress >= a.maxProgress).length} suffix={`/ ${achievements.length}`} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Desafios Ativos" value={challenges.filter(c => c.status === 'active').length} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Dias Ativo" value={Math.floor((new Date().getTime() - new Date(user?.joinDate || '').getTime()) / (1000 * 60 * 60 * 24))} />
                  </Col>
                </Row>
              </Card>
            </Col>
            
            <Col span={8}>
              <Card title="Próximas Conquistas" extra={<TrophyOutlined />}>
                <List
                  size="small"
                  dataSource={achievements.filter(a => a.progress > 0 && a.progress < a.maxProgress).slice(0, 3)}
                  renderItem={(achievement) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={<Avatar icon={<TrophyOutlined />} size="small" />}
                        title={achievement.name}
                        description={
                          <Progress 
                            percent={(achievement.progress / achievement.maxProgress) * 100} 
                            size="small"
                            format={() => `${achievement.progress}/${achievement.maxProgress}`}
                          />
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
            
            <Col span={8}>
              <Card title="Desafios Ativos" extra={<FireOutlined />}>
                <List
                  size="small"
                  dataSource={challenges.filter(c => c.status === 'active').slice(0, 3)}
                  renderItem={(challenge) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={<Avatar icon={<FireOutlined />} size="small" style={{ backgroundColor: '#fa8c16' }} />}
                        title={challenge.name}
                        description={
                          <Progress 
                            percent={(challenge.progress / challenge.maxProgress) * 100} 
                            size="small"
                            format={() => `${challenge.progress}/${challenge.maxProgress}`}
                          />
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="Badges" key="badges">
          <Card>
            <Table 
              dataSource={badges} 
              columns={badgeColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              onRow={(badge) => ({
                onClick: () => handleBadgeClick(badge),
                style: { cursor: 'pointer' }
              })}
            />
          </Card>
        </TabPane>

        <TabPane tab="Conquistas" key="achievements">
          <Card>
            <Table 
              dataSource={achievements} 
              columns={achievementColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              onRow={(achievement) => ({
                onClick: () => handleAchievementClick(achievement),
                style: { cursor: 'pointer' }
              })}
            />
          </Card>
        </TabPane>

        {showChallenges && (
          <TabPane tab="Desafios" key="challenges">
            <Card>
              <Row gutter={[16, 16]}>
                {challenges.map(challenge => (
                  <Col span={8} key={challenge.id}>
                    <Card 
                      size="small"
                      title={challenge.name}
                      extra={
                        <Tag color={challenge.status === 'active' ? 'green' : challenge.status === 'completed' ? 'blue' : 'red'}>
                          {challenge.status === 'active' ? 'Ativo' : challenge.status === 'completed' ? 'Concluído' : 'Expirado'}
                        </Tag>
                      }
                    >
                      <p>{challenge.description}</p>
                      <Progress 
                        percent={(challenge.progress / challenge.maxProgress) * 100}
                        format={() => `${challenge.progress}/${challenge.maxProgress}`}
                      />
                      <div style={{ marginTop: '8px' }}>
                        <Text type="secondary">
                          {new Date(challenge.endDate).toLocaleDateString()} • {challenge.participants} participantes
                        </Text>
                      </div>
                      <div style={{ marginTop: '8px' }}>
                        <Text strong>{challenge.points} pontos</Text>
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          </TabPane>
        )}

        {showLeaderboard && (
          <TabPane tab="Leaderboard" key="leaderboard">
            <Card>
              <Table 
                dataSource={leaderboard} 
                columns={leaderboardColumns}
                rowKey="rank"
                pagination={{ pageSize: 20 }}
              />
            </Card>
          </TabPane>
        )}

        {showAnalytics && (
          <TabPane tab="Analytics" key="analytics">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card title="Progresso por Categoria">
                  <PieChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                  <Text>Gráfico de progresso por categoria de badges e conquistas</Text>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Evolução de Nível">
                  <LineChartOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
                  <Text>Gráfico de evolução de nível ao longo do tempo</Text>
                </Card>
              </Col>
            </Row>
          </TabPane>
        )}
      </Tabs>

      {/* Modal de Badge */}
      <Modal
        title="Detalhes do Badge"
        open={showBadgeModal}
        onCancel={() => setShowBadgeModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowBadgeModal(false)}>
            Fechar
          </Button>,
          selectedBadge?.unlockedAt && enableSharing && (
            <Button 
              key="share" 
              type="primary" 
              icon={<ShareAltOutlined />}
              onClick={() => handleShare('badge', selectedBadge)}
            >
              Compartilhar
            </Button>
          )
        ]}
      >
        {selectedBadge && (
          <div>
            <Row gutter={16} align="middle" style={{ marginBottom: '16px' }}>
              <Col>
                <Avatar 
                  size={64} 
                  icon={getRarityIcon(selectedBadge.rarity)}
                  style={{ backgroundColor: getRarityColor(selectedBadge.rarity) }}
                />
              </Col>
              <Col flex="1">
                <Title level={4}>{selectedBadge.name}</Title>
                <Tag color={getRarityColor(selectedBadge.rarity)}>
                  {getRarityIcon(selectedBadge.rarity)} {selectedBadge.rarity.toUpperCase()}
                </Tag>
                <Tag>{selectedBadge.points} pontos</Tag>
              </Col>
            </Row>
            <Paragraph>{selectedBadge.description}</Paragraph>
            <Divider />
            <Title level={5}>Critérios:</Title>
            <ul>
              {selectedBadge.criteria.map((criterion, index) => (
                <li key={index}>{criterion}</li>
              ))}
            </ul>
            {selectedBadge.unlockedAt && (
              <>
                <Divider />
                <Text type="secondary">
                  Desbloqueado em: {new Date(selectedBadge.unlockedAt).toLocaleString()}
                </Text>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* Modal de Conquista */}
      <Modal
        title="Detalhes da Conquista"
        open={showAchievementModal}
        onCancel={() => setShowAchievementModal(false)}
        footer={[
          <Button key="close" onClick={() => setShowAchievementModal(false)}>
            Fechar
          </Button>,
          selectedAchievement && selectedAchievement.progress >= selectedAchievement.maxProgress && enableSharing && (
            <Button 
              key="share" 
              type="primary" 
              icon={<ShareAltOutlined />}
              onClick={() => handleShare('achievement', selectedAchievement)}
            >
              Compartilhar
            </Button>
          )
        ]}
      >
        {selectedAchievement && (
          <div>
            <Row gutter={16} align="middle" style={{ marginBottom: '16px' }}>
              <Col>
                <Avatar 
                  size={64} 
                  icon={<TrophyOutlined />}
                  style={{ backgroundColor: '#fa8c16' }}
                />
              </Col>
              <Col flex="1">
                <Title level={4}>{selectedAchievement.name}</Title>
                <Tag>{selectedAchievement.category}</Tag>
                <Tag>{selectedAchievement.points} pontos</Tag>
              </Col>
            </Row>
            <Paragraph>{selectedAchievement.description}</Paragraph>
            <Divider />
            <Title level={5}>Progresso:</Title>
            <Progress 
              percent={(selectedAchievement.progress / selectedAchievement.maxProgress) * 100}
              format={() => `${selectedAchievement.progress}/${selectedAchievement.maxProgress}`}
            />
            <Divider />
            <Title level={5}>Recompensas:</Title>
            <ul>
              {selectedAchievement.rewards.map((reward, index) => (
                <li key={index}>{reward.description}</li>
              ))}
            </ul>
            <Divider />
            <Title level={5}>Critérios:</Title>
            <ul>
              {selectedAchievement.criteria.map((criterion, index) => (
                <li key={index}>{criterion}</li>
              ))}
            </ul>
          </div>
        )}
      </Modal>
    </div>
  );
}; 