/**
 * Design System - Omni Keywords Finder
 * 
 * Sistema de design completo com component library, design tokens,
 * accessibility compliance e theming system
 * 
 * Tracing ID: DS-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

// =============================================================================
// DESIGN TOKENS
// =============================================================================

export * from '../theme/colors';
export * from '../theme/typography';
export * from '../theme/shadows';

// =============================================================================
// COMPONENTES BASE
// =============================================================================

// Layout Components
export { default as Box } from './components/Box';
export { default as Container } from './components/Container';
export { default as Grid } from './components/Grid';
export { default as Flex } from './components/Flex';
export { default as Stack } from './components/Stack';

// Typography Components
export { default as Text } from './components/Text';
export { default as Heading } from './components/Heading';
export { default as Paragraph } from './components/Paragraph';
export { default as Link } from './components/Link';

// Form Components
export { default as Button } from './components/Button';
export { default as Input } from './components/Input';
export { default as Select } from './components/Select';
export { default as Checkbox } from './components/Checkbox';
export { default as Radio } from './components/Radio';
export { default as Textarea } from './components/Textarea';
export { default as Switch } from './components/Switch';

// Feedback Components
export { default as Alert } from './components/Alert';
export { default as Badge } from './components/Badge';
export { default as Toast } from './components/Toast';
export { default as Progress } from './components/Progress';
export { default as Spinner } from './components/Spinner';
export { default as Skeleton } from './components/Skeleton';

// Navigation Components
export { default as Breadcrumb } from './components/Breadcrumb';
export { default as Pagination } from './components/Pagination';
export { default as Tabs } from './components/Tabs';
export { default as Menu } from './components/Menu';

// Data Display Components
export { default as Card } from './components/Card';
export { default as Table } from './components/Table';
export { default as List } from './components/List';
export { default as Avatar } from './components/Avatar';
export { default as Icon } from './components/Icon';

// Overlay Components
export { default as Modal } from './components/Modal';
export { default as Drawer } from './components/Drawer';
export { default as Popover } from './components/Popover';
export { default as Tooltip } from './components/Tooltip';

// =============================================================================
// COMPONENTES AVANÇADOS
// =============================================================================

// Analytics Components
export { default as Chart } from './components/analytics/Chart';
export { default as MetricCard } from './components/analytics/MetricCard';
export { default as DataTable } from './components/analytics/DataTable';
export { default as FilterBar } from './components/analytics/FilterBar';

// Dashboard Components
export { default as DashboardCard } from './components/dashboard/DashboardCard';
export { default as StatCard } from './components/dashboard/StatCard';
export { default as ActivityFeed } from './components/dashboard/ActivityFeed';
export { default as QuickActions } from './components/dashboard/QuickActions';

// =============================================================================
// HOOKS E UTILITÁRIOS
// =============================================================================

export { useTheme } from './hooks/useTheme';
export { useColorMode } from './hooks/useColorMode';
export { useBreakpoint } from './hooks/useBreakpoint';
export { useAccessibility } from './hooks/useAccessibility';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export type {
  Theme,
  ColorMode,
  Breakpoint,
  ComponentProps,
  VariantProps,
  SizeProps,
  ColorProps
} from './types';

// =============================================================================
// CONSTANTES
// =============================================================================

export {
  BREAKPOINTS,
  SPACING,
  BORDER_RADIUS,
  SHADOWS,
  TRANSITIONS,
  Z_INDEX
} from './constants';

// =============================================================================
// UTILITÁRIOS
// =============================================================================

export {
  createTheme,
  mergeThemes,
  getContrastRatio,
  getAccessibleColor,
  formatColor,
  validateColor
} from './utils'; 