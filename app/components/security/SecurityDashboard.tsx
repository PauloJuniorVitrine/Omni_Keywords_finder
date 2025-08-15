import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Tooltip,
  Badge,
  Tabs,
  Tab,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  TextField,
} from '@mui/material';
import {
  Security,
  Warning,
  Error,
  Info,
  CheckCircle,
  Cancel,
  Refresh,
  Settings,
  Visibility,
  Block,
  Shield,
  Lock,
  Key,
  Fingerprint,
  VpnKey,
  Public,
  Private,
  VerifiedUser,
  AdminPanelSettings,
  BugReport,
  Report,
  Assessment,
  Timeline,
  TrendingUp,
  TrendingDown,
  Notifications,
  NotificationsOff,
  Schedule,
  AutoAwesome,
  Psychology,
  Science,
  Biotech,
  Engineering,
  Build,
  Construction,
  Handyman,
  Plumbing,
  ElectricalServices,
  CleaningServices,
  LocalShipping,
  LocalTaxi,
  DirectionsCar,
  DirectionsBike,
  DirectionsWalk,
  DirectionsRun,
  DirectionsTransit,
  DirectionsBoat,
  DirectionsSubway,
  DirectionsBus,
  DirectionsRailway,
  DirectionsCarFilled,
  DirectionsBikeFilled,
  DirectionsWalkFilled,
  DirectionsRunFilled,
  DirectionsTransitFilled,
  DirectionsBoatFilled,
  DirectionsSubwayFilled,
  DirectionsBusFilled,
  DirectionsRailwayFilled,
} from '@mui/icons-material';

// Types
interface SecurityThreat {
  id: string;
  type: 'malware' | 'phishing' | 'ddos' | 'brute_force' | 'sql_injection' | 'xss' | 'csrf';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  target: string;
  description: string;
  timestamp: string;
  status: 'active' | 'investigating' | 'resolved' | 'false_positive';
  confidence: number;
  indicators: string[];
  mitigation: string;
}

interface Vulnerability {
  id: string;
  cve: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  cvss_score: number;
  affected_components: string[];
  discovery_date: string;
  status: 'open' | 'investigating' | 'patched' | 'accepted';
  remediation: string;
  references: string[];
}

interface ComplianceCheck {
  id: string;
  framework: 'pci_dss' | 'iso_27001' | 'sox' | 'gdpr' | 'hipaa';
  control: string;
  description: string;
  status: 'compliant' | 'non_compliant' | 'partial' | 'not_applicable';
  last_check: string;
  next_check: string;
  evidence: string;
  remediation: string;
  risk_level: 'low' | 'medium' | 'high';
}

interface SecurityEvent {
  id: string;
  type: 'login' | 'logout' | 'access_denied' | 'privilege_escalation' | 'data_access' | 'config_change';
  user: string;
  ip_address: string;
  user_agent: string;
  timestamp: string;
  details: Record<string, any>;
  risk_score: number;
  location: string;
  session_id: string;
}

interface SecurityConfig {
  auto_block: boolean;
  threat_threshold: number;
  monitoring_level: 'basic' | 'standard' | 'advanced';
  retention_days: number;
  alert_channels: string[];
  compliance_frameworks: string[];
}

// Mock data
const mockThreats: SecurityThreat[] = [
  {
    id: '1',
    type: 'brute_force',
    severity: 'high',
    source: '192.168.1.100',
    target: 'admin@example.com',
    description: 'Multiple failed login attempts detected',
    timestamp: '2024-12-20T10:30:00Z',
    status: 'active',
    confidence: 95,
    indicators: ['Multiple failed logins', 'Suspicious IP', 'Unusual time'],
    mitigation: 'Block IP address and enable 2FA',
  },
  {
    id: '2',
    type: 'sql_injection',
    severity: 'critical',
    source: '203.0.113.45',
    target: '/api/users',
    description: 'SQL injection attempt detected in user search',
    timestamp: '2024-12-20T10:25:00Z',
    status: 'investigating',
    confidence: 98,
    indicators: ['SQL keywords in payload', 'Error response', 'Suspicious pattern'],
    mitigation: 'Update input validation and WAF rules',
  },
  {
    id: '3',
    type: 'phishing',
    severity: 'medium',
    source: 'phishing@malicious.com',
    target: 'user@example.com',
    description: 'Phishing email detected in user inbox',
    timestamp: '2024-12-20T10:20:00Z',
    status: 'resolved',
    confidence: 87,
    indicators: ['Suspicious sender', 'Urgent action required', 'Fake link'],
    mitigation: 'Quarantine email and update filters',
  },
];

const mockVulnerabilities: Vulnerability[] = [
  {
    id: '1',
    cve: 'CVE-2024-1234',
    title: 'SQL Injection in User Authentication',
    description: 'A SQL injection vulnerability exists in the user authentication system',
    severity: 'high',
    cvss_score: 8.5,
    affected_components: ['auth-service', 'user-api'],
    discovery_date: '2024-12-20T10:00:00Z',
    status: 'open',
    remediation: 'Implement parameterized queries and input validation',
    references: ['https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-1234'],
  },
  {
    id: '2',
    cve: 'CVE-2024-5678',
    title: 'Cross-Site Scripting in Search Function',
    description: 'XSS vulnerability allows execution of arbitrary JavaScript',
    severity: 'medium',
    cvss_score: 6.1,
    affected_components: ['search-api', 'frontend'],
    discovery_date: '2024-12-19T15:30:00Z',
    status: 'investigating',
    remediation: 'Implement proper output encoding and CSP headers',
    references: ['https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-5678'],
  },
  {
    id: '3',
    cve: 'CVE-2024-9012',
    title: 'Weak Password Policy',
    description: 'Password policy does not enforce sufficient complexity',
    severity: 'low',
    cvss_score: 3.1,
    affected_components: ['auth-service', 'user-management'],
    discovery_date: '2024-12-18T09:15:00Z',
    status: 'patched',
    remediation: 'Implement stronger password requirements and validation',
    references: ['https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-9012'],
  },
];

const mockCompliance: ComplianceCheck[] = [
  {
    id: '1',
    framework: 'pci_dss',
    control: 'PCI DSS 3.4',
    description: 'Render PAN unreadable anywhere it is stored',
    status: 'compliant',
    last_check: '2024-12-20T10:00:00Z',
    next_check: '2024-12-27T10:00:00Z',
    evidence: 'All PAN data is encrypted using AES-256',
    remediation: 'N/A',
    risk_level: 'low',
  },
  {
    id: '2',
    framework: 'iso_27001',
    control: 'A.12.4.1',
    description: 'Event logging and monitoring',
    status: 'partial',
    last_check: '2024-12-20T09:00:00Z',
    next_check: '2024-12-27T09:00:00Z',
    evidence: 'Basic logging implemented, advanced monitoring pending',
    remediation: 'Implement SIEM and advanced threat detection',
    risk_level: 'medium',
  },
  {
    id: '3',
    framework: 'gdpr',
    control: 'Article 32',
    description: 'Security of processing',
    status: 'non_compliant',
    last_check: '2024-12-20T08:00:00Z',
    next_check: '2024-12-27T08:00:00Z',
    evidence: 'Data encryption not implemented for all personal data',
    remediation: 'Implement end-to-end encryption for all personal data',
    risk_level: 'high',
  },
];

const mockEvents: SecurityEvent[] = [
  {
    id: '1',
    type: 'login',
    user: 'admin@example.com',
    ip_address: '192.168.1.100',
    user_agent: 'Mozilla/5.0...',
    timestamp: '2024-12-20T10:30:00Z',
    details: { method: 'password', success: true, mfa_used: true },
    risk_score: 15,
    location: 'New York, US',
    session_id: 'sess_123456',
  },
  {
    id: '2',
    type: 'access_denied',
    user: 'unknown',
    ip_address: '203.0.113.45',
    user_agent: 'curl/7.68.0',
    timestamp: '2024-12-20T10:25:00Z',
    details: { reason: 'invalid_credentials', attempts: 5 },
    risk_score: 85,
    location: 'Unknown',
    session_id: 'sess_789012',
  },
  {
    id: '3',
    type: 'data_access',
    user: 'user@example.com',
    ip_address: '192.168.1.101',
    user_agent: 'Mozilla/5.0...',
    timestamp: '2024-12-20T10:20:00Z',
    details: { resource: '/api/users/123', action: 'read', success: true },
    risk_score: 25,
    location: 'New York, US',
    session_id: 'sess_345678',
  },
];

const SecurityDashboard: React.FC = () => {
  // State
  const [threats, setThreats] = useState<SecurityThreat[]>(mockThreats);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>(mockVulnerabilities);
  const [compliance, setCompliance] = useState<ComplianceCheck[]>(mockCompliance);
  const [events, setEvents] = useState<SecurityEvent[]>(mockEvents);
  const [config, setConfig] = useState<SecurityConfig>({
    auto_block: true,
    threat_threshold: 75,
    monitoring_level: 'advanced',
    retention_days: 90,
    alert_channels: ['email', 'slack'],
    compliance_frameworks: ['pci_dss', 'iso_27001', 'gdpr'],
  });
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedThreat, setSelectedThreat] = useState<SecurityThreat | null>(null);
  const [threatDialogOpen, setThreatDialogOpen] = useState(false);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);

  // Memoized values
  const activeThreats = useMemo(() => {
    return threats.filter(threat => threat.status === 'active');
  }, [threats]);

  const criticalVulnerabilities = useMemo(() => {
    return vulnerabilities.filter(vuln => vuln.severity === 'critical');
  }, [vulnerabilities]);

  const nonCompliantChecks = useMemo(() => {
    return compliance.filter(check => check.status === 'non_compliant');
  }, [compliance]);

  const highRiskEvents = useMemo(() => {
    return events.filter(event => event.risk_score > 70);
  }, [events]);

  const securityScore = useMemo(() => {
    const totalChecks = compliance.length;
    const compliantChecks = compliance.filter(check => check.status === 'compliant').length;
    const partialChecks = compliance.filter(check => check.status === 'partial').length;
    return Math.round(((compliantChecks + (partialChecks * 0.5)) / totalChecks) * 100);
  }, [compliance]);

  // Handlers
  const handleThreatStatusChange = (threatId: string, status: SecurityThreat['status']) => {
    setThreats(prev =>
      prev.map(threat =>
        threat.id === threatId ? { ...threat, status } : threat
      )
    );
  };

  const handleVulnerabilityStatusChange = (vulnId: string, status: Vulnerability['status']) => {
    setVulnerabilities(prev =>
      prev.map(vuln =>
        vuln.id === vulnId ? { ...vuln, status } : threat
      )
    );
  };

  const handleRefreshSecurity = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Update with new data
      setThreats(prev =>
        prev.map(threat => ({
          ...threat,
          confidence: Math.random() * 100,
        }))
      );
    } catch (err) {
      setError('Failed to refresh security data');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'error';
      case 'investigating': return 'warning';
      case 'resolved': return 'success';
      case 'false_positive': return 'info';
      case 'compliant': return 'success';
      case 'non_compliant': return 'error';
      case 'partial': return 'warning';
      case 'not_applicable': return 'default';
      case 'open': return 'error';
      case 'patched': return 'success';
      case 'accepted': return 'info';
      default: return 'default';
    }
  };

  const getThreatIcon = (type: string) => {
    switch (type) {
      case 'malware': return <BugReport />;
      case 'phishing': return <Warning />;
      case 'ddos': return <Error />;
      case 'brute_force': return <Block />;
      case 'sql_injection': return <Code />;
      case 'xss': return <Code />;
      case 'csrf': return <Code />;
      default: return <Security />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Security Dashboard
        </Typography>
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Security Data">
            <IconButton onClick={handleRefreshSecurity}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Security Settings">
            <IconButton onClick={() => setConfigDialogOpen(true)}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Critical Alerts */}
      {activeThreats.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">
            {activeThreats.length} Active Security Threat{activeThreats.length > 1 ? 's' : ''} Detected
          </Typography>
          <Typography variant="body2">
            Immediate attention required for: {activeThreats.map(t => t.type.replace('_', ' ')).join(', ')}
          </Typography>
        </Alert>
      )}

      {/* Security Overview Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Shield color="primary" />
                <Typography variant="h6">Security Score</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {securityScore}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {compliance.filter(c => c.status === 'compliant').length} of {compliance.length} controls compliant
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Warning color="error" />
                <Typography variant="h6">Active Threats</Typography>
              </Box>
              <Typography variant="h4" color="error">
                {activeThreats.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {threats.filter(t => t.severity === 'critical').length} critical threats
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <BugReport color="warning" />
                <Typography variant="h6">Vulnerabilities</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {vulnerabilities.filter(v => v.status === 'open').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {criticalVulnerabilities.length} critical vulnerabilities
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Timeline color="info" />
                <Typography variant="h6">High Risk Events</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {highRiskEvents.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Events with risk score > 70
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label="Threats" />
          <Tab label="Vulnerabilities" />
          <Tab label="Compliance" />
          <Tab label="Events" />
        </Tabs>
      </Box>

      {/* Threats Tab */}
      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Target</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {threats.map((threat) => (
                <TableRow key={threat.id}>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {getThreatIcon(threat.type)}
                      <Typography>{threat.type.replace('_', ' ')}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={threat.severity.toUpperCase()}
                      color={getSeverityColor(threat.severity) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{threat.source}</TableCell>
                  <TableCell>{threat.target}</TableCell>
                  <TableCell>
                    <Chip
                      label={threat.status.toUpperCase()}
                      color={getStatusColor(threat.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">{threat.confidence}%</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={threat.confidence}
                        color={threat.confidence > 90 ? 'error' : threat.confidence > 70 ? 'warning' : 'success'}
                        sx={{ width: 50 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedThreat(threat);
                          setThreatDialogOpen(true);
                        }}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Vulnerabilities Tab */}
      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>CVE</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>CVSS Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Components</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {vulnerabilities.map((vuln) => (
                <TableRow key={vuln.id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {vuln.cve}
                    </Typography>
                  </TableCell>
                  <TableCell>{vuln.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={vuln.severity.toUpperCase()}
                      color={getSeverityColor(vuln.severity) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography color={vuln.cvss_score > 7 ? 'error' : vuln.cvss_score > 4 ? 'warning' : 'inherit'}>
                      {vuln.cvss_score}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={vuln.status.toUpperCase()}
                      color={getStatusColor(vuln.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={0.5}>
                      {vuln.affected_components.map((component, index) => (
                        <Chip key={index} label={component} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Compliance Tab */}
      {activeTab === 2 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Framework</TableCell>
                <TableCell>Control</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Last Check</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {compliance.map((check) => (
                <TableRow key={check.id}>
                  <TableCell>
                    <Chip label={check.framework.toUpperCase()} size="small" />
                  </TableCell>
                  <TableCell>{check.control}</TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {check.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={check.status.replace('_', ' ').toUpperCase()}
                      color={getStatusColor(check.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={check.risk_level.toUpperCase()}
                      color={getSeverityColor(check.risk_level) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(check.last_check).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Events Tab */}
      {activeTab === 3 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>User</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Risk Score</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.map((event) => (
                <TableRow key={event.id}>
                  <TableCell>
                    <Chip
                      label={event.type.replace('_', ' ').toUpperCase()}
                      color={event.risk_score > 70 ? 'error' : event.risk_score > 40 ? 'warning' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{event.user}</TableCell>
                  <TableCell>{event.ip_address}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">{event.risk_score}</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={event.risk_score}
                        color={event.risk_score > 70 ? 'error' : event.risk_score > 40 ? 'warning' : 'success'}
                        sx={{ width: 50 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>{event.location}</TableCell>
                  <TableCell>
                    {new Date(event.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Threat Detail Dialog */}
      <Dialog
        open={threatDialogOpen}
        onClose={() => setThreatDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Threat Details
          <IconButton
            onClick={() => setThreatDialogOpen(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Cancel />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedThreat && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Basic Information
                  </Typography>
                  <Box mt={1}>
                    <Typography><strong>Type:</strong> {selectedThreat.type.replace('_', ' ')}</Typography>
                    <Typography><strong>Severity:</strong> {selectedThreat.severity}</Typography>
                    <Typography><strong>Source:</strong> {selectedThreat.source}</Typography>
                    <Typography><strong>Target:</strong> {selectedThreat.target}</Typography>
                    <Typography><strong>Confidence:</strong> {selectedThreat.confidence}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Status Information
                  </Typography>
                  <Box mt={1}>
                    <Typography><strong>Status:</strong> {selectedThreat.status}</Typography>
                    <Typography><strong>Timestamp:</strong> {new Date(selectedThreat.timestamp).toLocaleString()}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Description
                  </Typography>
                  <Box mt={1} p={2} bgcolor="grey.100" borderRadius={1}>
                    <Typography>{selectedThreat.description}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Indicators
                  </Typography>
                  <Box mt={1}>
                    {selectedThreat.indicators.map((indicator, index) => (
                      <Chip key={index} label={indicator} size="small" sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Mitigation
                  </Typography>
                  <Box mt={1} p={2} bgcolor="grey.100" borderRadius={1}>
                    <Typography>{selectedThreat.mitigation}</Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setThreatDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              if (selectedThreat) {
                handleThreatStatusChange(selectedThreat.id, 'investigating');
                setThreatDialogOpen(false);
              }
            }}
          >
            Start Investigation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Security Settings</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={1}>
            <FormControlLabel
              control={
                <Switch
                  checked={config.auto_block}
                  onChange={(e) => setConfig(prev => ({ ...prev, auto_block: e.target.checked }))}
                />
              }
              label="Auto Block Threats"
            />
            
            <FormControl>
              <InputLabel>Monitoring Level</InputLabel>
              <Select
                value={config.monitoring_level}
                onChange={(e) => setConfig(prev => ({ ...prev, monitoring_level: e.target.value as any }))}
              >
                <MenuItem value="basic">Basic</MenuItem>
                <MenuItem value="standard">Standard</MenuItem>
                <MenuItem value="advanced">Advanced</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Threat Threshold"
              type="number"
              value={config.threat_threshold}
              onChange={(e) => setConfig(prev => ({ ...prev, threat_threshold: Number(e.target.value) }))}
            />

            <TextField
              label="Data Retention (days)"
              type="number"
              value={config.retention_days}
              onChange={(e) => setConfig(prev => ({ ...prev, retention_days: Number(e.target.value) }))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => setConfigDialogOpen(false)} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default SecurityDashboard; 