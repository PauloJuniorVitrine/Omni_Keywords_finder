/**
 * 🧪 Chaos Tester Component
 * 🎯 Objetivo: Interface para chaos testing e validação de resiliência
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: CHAOS_TESTER_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { 
  Play, 
  Square, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Activity,
  Zap,
  Shield,
  TrendingUp,
  BarChart3
} from 'lucide-react';

// Tipos para chaos testing
interface ChaosTest {
  id: string;
  name: string;
  type: 'latency' | 'timeout' | 'connection_drop' | 'packet_loss' | 'bandwidth_limit' | 'dns_failure' | 'ssl_error' | 'rate_limit';
  severity: 'low' | 'medium' | 'high' | 'critical';
  duration: number;
  probability: number;
  targetEndpoints: string[];
  status: 'idle' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  results?: ChaosTestResult;
}

interface ChaosTestResult {
  successCount: number;
  failureCount: number;
  timeoutCount: number;
  avgResponseTime: number;
  circuitBreakerTrips: number;
  recoveryTime?: number;
  errorDetails: string[];
  resilienceScore: number;
}

interface ChaosScenario {
  id: string;
  name: string;
  description: string;
  tests: Omit<ChaosTest, 'id' | 'status' | 'startTime' | 'endTime' | 'results'>[];
  category: 'basic' | 'advanced' | 'critical' | 'custom';
}

interface ResilienceMetrics {
  overallScore: number;
  availability: number;
  responseTime: number;
  errorRate: number;
  circuitBreakerEfficiency: number;
  recoveryTime: number;
}

// Dados de exemplo
const CHAOS_SCENARIOS: ChaosScenario[] = [
  {
    id: 'basic-latency',
    name: 'Teste de Latência Básico',
    description: 'Simula latência de rede para validar timeouts',
    category: 'basic',
    tests: [
      {
        name: 'Latência Média',
        type: 'latency',
        severity: 'medium',
        duration: 60,
        probability: 0.3,
        targetEndpoints: ['/api/health', '/api/keywords', '/api/analytics']
      }
    ]
  },
  {
    id: 'advanced-timeout',
    name: 'Teste de Timeout Avançado',
    description: 'Simula timeouts para validar circuit breakers',
    category: 'advanced',
    tests: [
      {
        name: 'Timeout Alto',
        type: 'timeout',
        severity: 'high',
        duration: 120,
        probability: 0.2,
        targetEndpoints: ['/api/health', '/api/keywords', '/api/analytics']
      }
    ]
  },
  {
    id: 'critical-connection-drop',
    name: 'Teste Crítico de Queda de Conexão',
    description: 'Simula quedas de conexão para validar resiliência',
    category: 'critical',
    tests: [
      {
        name: 'Queda de Conexão Crítica',
        type: 'connection_drop',
        severity: 'critical',
        duration: 180,
        probability: 0.15,
        targetEndpoints: ['/api/health', '/api/keywords', '/api/analytics']
      }
    ]
  },
  {
    id: 'comprehensive-resilience',
    name: 'Teste Abrangente de Resiliência',
    description: 'Combina múltiplos tipos de caos para validação completa',
    category: 'critical',
    tests: [
      {
        name: 'Latência + Timeout',
        type: 'latency',
        severity: 'high',
        duration: 300,
        probability: 0.4,
        targetEndpoints: ['/api/health', '/api/keywords', '/api/analytics']
      },
      {
        name: 'Queda de Conexão',
        type: 'connection_drop',
        severity: 'medium',
        duration: 300,
        probability: 0.2,
        targetEndpoints: ['/api/health', '/api/keywords', '/api/analytics']
      }
    ]
  }
];

export const ChaosTester: React.FC = () => {
  // Estados
  const [activeTests, setActiveTests] = useState<ChaosTest[]>([]);
  const [completedTests, setCompletedTests] = useState<ChaosTest[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [customTest, setCustomTest] = useState<Partial<ChaosTest>>({
    name: '',
    type: 'latency',
    severity: 'medium',
    duration: 60,
    probability: 0.3,
    targetEndpoints: []
  });
  const [resilienceMetrics, setResilienceMetrics] = useState<ResilienceMetrics>({
    overallScore: 85,
    availability: 98.5,
    responseTime: 250,
    errorRate: 1.2,
    circuitBreakerEfficiency: 95,
    recoveryTime: 2.5
  });
  const [isMonitoring, setIsMonitoring] = useState(false);

  // Simulação de API
  const chaosAPI = {
    startTest: async (test: Omit<ChaosTest, 'id' | 'status' | 'startTime' | 'endTime' | 'results'>): Promise<string> => {
      // Simular delay de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const testId = `chaos_${Date.now()}`;
      const newTest: ChaosTest = {
        ...test,
        id: testId,
        status: 'running',
        startTime: new Date()
      };
      
      setActiveTests(prev => [...prev, newTest]);
      
      // Simular execução do teste
      setTimeout(() => {
        completeTest(testId);
      }, test.duration * 1000);
      
      return testId;
    },
    
    stopTest: async (testId: string): Promise<boolean> => {
      setActiveTests(prev => prev.filter(test => test.id !== testId));
      return true;
    },
    
    getMetrics: async (): Promise<ResilienceMetrics> => {
      // Simular métricas em tempo real
      return {
        overallScore: Math.random() * 20 + 80,
        availability: Math.random() * 2 + 97,
        responseTime: Math.random() * 200 + 150,
        errorRate: Math.random() * 2 + 0.5,
        circuitBreakerEfficiency: Math.random() * 10 + 90,
        recoveryTime: Math.random() * 3 + 1
      };
    }
  };

  // Funções auxiliares
  const completeTest = useCallback((testId: string) => {
    setActiveTests(prev => {
      const test = prev.find(t => t.id === testId);
      if (!test) return prev;
      
      // Gerar resultados simulados
      const results: ChaosTestResult = {
        successCount: Math.floor(Math.random() * 100) + 50,
        failureCount: Math.floor(Math.random() * 20),
        timeoutCount: Math.floor(Math.random() * 10),
        avgResponseTime: Math.random() * 500 + 100,
        circuitBreakerTrips: Math.floor(Math.random() * 5),
        recoveryTime: Math.random() * 10 + 1,
        errorDetails: ['Simulated error 1', 'Simulated error 2'],
        resilienceScore: Math.random() * 30 + 70
      };
      
      const completedTest: ChaosTest = {
        ...test,
        status: 'completed',
        endTime: new Date(),
        results
      };
      
      setCompletedTests(prev => [...prev, completedTest]);
      return prev.filter(t => t.id !== testId);
    });
  }, []);

  const startScenario = useCallback(async (scenarioId: string) => {
    const scenario = CHAOS_SCENARIOS.find(s => s.id === scenarioId);
    if (!scenario) return;
    
    for (const test of scenario.tests) {
      await chaosAPI.startTest(test);
    }
  }, [chaosAPI]);

  const startCustomTest = useCallback(async () => {
    if (!customTest.name || customTest.targetEndpoints?.length === 0) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }
    
    await chaosAPI.startTest(customTest as Omit<ChaosTest, 'id' | 'status' | 'startTime' | 'endTime' | 'results'>);
    
    // Limpar formulário
    setCustomTest({
      name: '',
      type: 'latency',
      severity: 'medium',
      duration: 60,
      probability: 0.3,
      targetEndpoints: []
    });
  }, [customTest, chaosAPI]);

  const stopAllTests = useCallback(async () => {
    for (const test of activeTests) {
      await chaosAPI.stopTest(test.id);
    }
  }, [activeTests, chaosAPI]);

  // Monitoramento em tempo real
  useEffect(() => {
    if (!isMonitoring) return;
    
    const interval = setInterval(async () => {
      const metrics = await chaosAPI.getMetrics();
      setResilienceMetrics(metrics);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [isMonitoring, chaosAPI]);

  // Cálculos derivados
  const totalTests = useMemo(() => activeTests.length + completedTests.length, [activeTests, completedTests]);
  const successRate = useMemo(() => {
    if (completedTests.length === 0) return 0;
    const totalResults = completedTests.reduce((sum, test) => {
      if (!test.results) return sum;
      return sum + test.results.successCount + test.results.failureCount;
    }, 0);
    const totalSuccess = completedTests.reduce((sum, test) => {
      if (!test.results) return sum;
      return sum + test.results.successCount;
    }, 0);
    return totalResults > 0 ? (totalSuccess / totalResults) * 100 : 0;
  }, [completedTests]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="w-4 h-4 animate-pulse" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🧪 Chaos Tester</h1>
          <p className="text-gray-600">Teste de resiliência e validação de fallbacks</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            variant={isMonitoring ? "destructive" : "default"}
            onClick={() => setIsMonitoring(!isMonitoring)}
          >
            {isMonitoring ? <Square className="w-4 h-4 mr-2" /> : <Activity className="w-4 h-4 mr-2" />}
            {isMonitoring ? 'Parar Monitoramento' : 'Iniciar Monitoramento'}
          </Button>
          {activeTests.length > 0 && (
            <Button variant="destructive" onClick={stopAllTests}>
              <Square className="w-4 h-4 mr-2" />
              Parar Todos os Testes
            </Button>
          )}
        </div>
      </div>

      {/* Métricas de Resiliência */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="w-5 h-5 mr-2" />
            Métricas de Resiliência
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{resilienceMetrics.overallScore.toFixed(1)}</div>
              <div className="text-sm text-gray-600">Score Geral</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{resilienceMetrics.availability.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Disponibilidade</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{resilienceMetrics.responseTime.toFixed(0)}ms</div>
              <div className="text-sm text-gray-600">Tempo de Resposta</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{resilienceMetrics.errorRate.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Taxa de Erro</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{resilienceMetrics.circuitBreakerEfficiency.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Eficiência CB</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">{resilienceMetrics.recoveryTime.toFixed(1)}s</div>
              <div className="text-sm text-gray-600">Tempo Recuperação</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="scenarios" className="space-y-4">
        <TabsList>
          <TabsTrigger value="scenarios">Cenários Predefinidos</TabsTrigger>
          <TabsTrigger value="custom">Teste Customizado</TabsTrigger>
          <TabsTrigger value="active">Testes Ativos</TabsTrigger>
          <TabsTrigger value="results">Resultados</TabsTrigger>
        </TabsList>

        {/* Cenários Predefinidos */}
        <TabsContent value="scenarios" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {CHAOS_SCENARIOS.map((scenario) => (
              <Card key={scenario.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{scenario.name}</span>
                    <Badge variant={scenario.category === 'critical' ? 'destructive' : 'secondary'}>
                      {scenario.category}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">{scenario.description}</p>
                  <div className="space-y-2">
                    {scenario.tests.map((test, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span>{test.name}</span>
                        <Badge className={getSeverityColor(test.severity)}>
                          {test.severity}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  <Button 
                    className="w-full mt-4" 
                    onClick={() => startScenario(scenario.id)}
                    disabled={activeTests.length > 0}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Executar Cenário
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Teste Customizado */}
        <TabsContent value="custom" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Criar Teste Customizado</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="test-name">Nome do Teste</Label>
                  <Input
                    id="test-name"
                    value={customTest.name}
                    onChange={(e) => setCustomTest(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Ex: Teste de Latência Crítica"
                  />
                </div>
                <div>
                  <Label htmlFor="test-type">Tipo de Caos</Label>
                  <Select
                    value={customTest.type}
                    onValueChange={(value) => setCustomTest(prev => ({ ...prev, type: value as any }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="latency">Latência</SelectItem>
                      <SelectItem value="timeout">Timeout</SelectItem>
                      <SelectItem value="connection_drop">Queda de Conexão</SelectItem>
                      <SelectItem value="packet_loss">Perda de Pacotes</SelectItem>
                      <SelectItem value="bandwidth_limit">Limitação de Banda</SelectItem>
                      <SelectItem value="dns_failure">Falha DNS</SelectItem>
                      <SelectItem value="ssl_error">Erro SSL</SelectItem>
                      <SelectItem value="rate_limit">Rate Limit</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="test-severity">Severidade</Label>
                  <Select
                    value={customTest.severity}
                    onValueChange={(value) => setCustomTest(prev => ({ ...prev, severity: value as any }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Baixa</SelectItem>
                      <SelectItem value="medium">Média</SelectItem>
                      <SelectItem value="high">Alta</SelectItem>
                      <SelectItem value="critical">Crítica</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="test-duration">Duração (segundos)</Label>
                  <Input
                    id="test-duration"
                    type="number"
                    value={customTest.duration}
                    onChange={(e) => setCustomTest(prev => ({ ...prev, duration: parseInt(e.target.value) || 60 }))}
                    min="10"
                    max="3600"
                  />
                </div>
                <div>
                  <Label htmlFor="test-probability">Probabilidade (0-1)</Label>
                  <Input
                    id="test-probability"
                    type="number"
                    step="0.1"
                    value={customTest.probability}
                    onChange={(e) => setCustomTest(prev => ({ ...prev, probability: parseFloat(e.target.value) || 0.3 }))}
                    min="0"
                    max="1"
                  />
                </div>
                <div>
                  <Label htmlFor="test-endpoints">Endpoints (separados por vírgula)</Label>
                  <Input
                    id="test-endpoints"
                    value={customTest.targetEndpoints?.join(', ')}
                    onChange={(e) => setCustomTest(prev => ({ 
                      ...prev, 
                      targetEndpoints: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                    }))}
                    placeholder="/api/health, /api/keywords"
                  />
                </div>
              </div>
              <Button onClick={startCustomTest} className="w-full">
                <Zap className="w-4 h-4 mr-2" />
                Iniciar Teste Customizado
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Testes Ativos */}
        <TabsContent value="active" className="space-y-4">
          {activeTests.length === 0 ? (
            <Alert>
              <AlertDescription>Nenhum teste ativo no momento.</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {activeTests.map((test) => (
                <Card key={test.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(test.status)}
                        <div>
                          <h3 className="font-semibold">{test.name}</h3>
                          <p className="text-sm text-gray-600">
                            {test.type} • {test.severity} • {test.duration}s
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeverityColor(test.severity)}>
                          {test.severity}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => chaosAPI.stopTest(test.id)}
                        >
                          <Square className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="mt-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span>Progresso</span>
                        <span>{test.startTime ? Math.floor((Date.now() - test.startTime.getTime()) / 1000)}s / {test.duration}s</span>
                      </div>
                      <Progress 
                        value={test.startTime ? ((Date.now() - test.startTime.getTime()) / 1000 / test.duration) * 100 : 0} 
                        className="w-full" 
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Resultados */}
        <TabsContent value="results" className="space-y-4">
          {completedTests.length === 0 ? (
            <Alert>
              <AlertDescription>Nenhum resultado disponível.</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Resultados dos Testes</h3>
                <div className="text-sm text-gray-600">
                  Taxa de Sucesso: {successRate.toFixed(1)}%
                </div>
              </div>
              
              {completedTests.map((test) => (
                <Card key={test.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(test.status)}
                        <div>
                          <h3 className="font-semibold">{test.name}</h3>
                          <p className="text-sm text-gray-600">
                            {test.startTime?.toLocaleString()} - {test.endTime?.toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <Badge className={getSeverityColor(test.severity)}>
                        {test.severity}
                      </Badge>
                    </div>
                    
                    {test.results && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">{test.results.successCount}</div>
                          <div className="text-sm text-gray-600">Sucessos</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">{test.results.failureCount}</div>
                          <div className="text-sm text-gray-600">Falhas</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">{test.results.timeoutCount}</div>
                          <div className="text-sm text-gray-600">Timeouts</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{test.results.resilienceScore.toFixed(1)}</div>
                          <div className="text-sm text-gray-600">Score Resiliência</div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChaosTester; 