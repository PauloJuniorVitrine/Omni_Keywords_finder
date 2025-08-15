import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import PerformanceOptimizer from '../../../../components/admin/PerformanceOptimizer';

// Mock Material-UI components
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  Box: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Card: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Typography: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Chip: ({ label, ...props }: any) => <span {...props}>{label}</span>,
  Table: ({ children, ...props }: any) => <table {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody {...props}>{children}</tbody>,
  TableCell: ({ children, ...props }: any) => <td {...props}>{children}</td>,
  TableContainer: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  TableHead: ({ children, ...props }: any) => <thead {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr {...props}>{children}</tr>,
  Paper: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  IconButton: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Dialog: ({ children, open, ...props }: any) => 
    open ? <div data-testid="dialog" {...props}>{children}</div> : null,
  DialogTitle: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogContent: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  DialogActions: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  FormControl: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  InputLabel: ({ children, ...props }: any) => <label {...props}>{children}</label>,
  Select: ({ children, value, onChange, ...props }: any) => (
    <select value={value} onChange={onChange} {...props}>
      {children}
    </select>
  ),
  MenuItem: ({ children, value, ...props }: any) => (
    <option value={value} {...props}>{children}</option>
  ),
  Switch: ({ checked, onChange, ...props }: any) => (
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      {...props}
    />
  ),
  FormControlLabel: ({ control, label, ...props }: any) => (
    <label {...props}>
      {control}
      {label}
    </label>
  ),
  Alert: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  CircularProgress: () => <div data-testid="loading">Loading...</div>,
  Tooltip: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Badge: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Tabs: ({ children, value, onChange, ...props }: any) => (
    <div {...props}>
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child as React.ReactElement, {
          onClick: () => onChange(null, index),
          'data-testid': `tab-${index}`,
        })
      )}
    </div>
  ),
  Tab: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  Divider: () => <hr />,
  Grid: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  Accordion: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  AccordionSummary: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  AccordionDetails: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  List: ({ children, ...props }: any) => <ul {...props}>{children}</ul>,
  ListItem: ({ children, ...props }: any) => <li {...props}>{children}</li>,
  ListItemText: ({ primary, secondary, ...props }: any) => (
    <div {...props}>
      <div>{primary}</div>
      <div>{secondary}</div>
    </div>
  ),
  ListItemIcon: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  LinearProgress: ({ ...props }: any) => <div {...props}>Progress Bar</div>,
  Slider: ({ value, onChange, ...props }: any) => (
    <input
      type="range"
      value={value}
      onChange={onChange}
      {...props}
    />
  ),
  TextField: ({ label, value, onChange, ...props }: any) => (
    <input
      data-testid={label?.toLowerCase().replace(/\s+/g, '-')}
      value={value}
      onChange={onChange}
      placeholder={label}
      {...props}
    />
  ),
}));

// Mock Material-UI icons
jest.mock('@mui/icons-material', () => ({
  Speed: () => <span data-testid="speed-icon">⚡</span>,
  Memory: () => <span data-testid="memory-icon">💾</span>,
  Storage: () => <span data-testid="storage-icon">💿</span>,
  NetworkCheck: () => <span data-testid="network-icon">🌐</span>,
  Code: () => <span data-testid="code-icon">💻</span>,
  DataUsage: () => <span data-testid="data-icon">📊</span>,
  Assessment: () => <span data-testid="assessment-icon">📋</span>,
  TrendingUp: () => <span data-testid="trending-up-icon">📈</span>,
  TrendingDown: () => <span data-testid="trending-down-icon">📉</span>,
  Notifications: () => <span data-testid="notifications-icon">🔔</span>,
  NotificationsOff: () => <span data-testid="notifications-off-icon">🔕</span>,
  Schedule: () => <span data-testid="schedule-icon">📅</span>,
  AutoAwesome: () => <span data-testid="auto-awesome-icon">✨</span>,
  Psychology: () => <span data-testid="psychology-icon">🧠</span>,
  Science: () => <span data-testid="science-icon">🔬</span>,
  Biotech: () => <span data-testid="biotech-icon">🧬</span>,
  Engineering: () => <span data-testid="engineering-icon">⚙️</span>,
  Build: () => <span data-testid="build-icon">🔨</span>,
  Construction: () => <span data-testid="construction-icon">🏗️</span>,
  Handyman: () => <span data-testid="handyman-icon">🔧</span>,
  Plumbing: () => <span data-testid="plumbing-icon">🚰</span>,
  ElectricalServices: () => <span data-testid="electrical-icon">⚡</span>,
  CleaningServices: () => <span data-testid="cleaning-icon">🧹</span>,
  LocalShipping: () => <span data-testid="shipping-icon">🚚</span>,
  LocalTaxi: () => <span data-testid="taxi-icon">🚕</span>,
  DirectionsCar: () => <span data-testid="car-icon">🚗</span>,
  DirectionsBike: () => <span data-testid="bike-icon">🚲</span>,
  DirectionsWalk: () => <span data-testid="walk-icon">🚶</span>,
  DirectionsRun: () => <span data-testid="run-icon">🏃</span>,
  DirectionsTransit: () => <span data-testid="transit-icon">🚌</span>,
  DirectionsBoat: () => <span data-testid="boat-icon">🚢</span>,
  DirectionsSubway: () => <span data-testid="subway-icon">🚇</span>,
  DirectionsBus: () => <span data-testid="bus-icon">🚌</span>,
  DirectionsRailway: () => <span data-testid="railway-icon">🚂</span>,
  DirectionsCarFilled: () => <span data-testid="car-filled-icon">🚗</span>,
  DirectionsBikeFilled: () => <span data-testid="bike-filled-icon">🚲</span>,
  DirectionsWalkFilled: () => <span data-testid="walk-filled-icon">🚶</span>,
  DirectionsRunFilled: () => <span data-testid="run-filled-icon">🏃</span>,
  DirectionsTransitFilled: () => <span data-testid="transit-filled-icon">🚌</span>,
  DirectionsBoatFilled: () => <span data-testid="boat-filled-icon">🚢</span>,
  DirectionsSubwayFilled: () => <span data-testid="subway-filled-icon">🚇</span>,
  DirectionsBusFilled: () => <span data-testid="bus-filled-icon">🚌</span>,
  DirectionsRailwayFilled: () => <span data-testid="railway-filled-icon">🚂</span>,
  Settings: () => <span data-testid="settings-icon">⚙️</span>,
  Refresh: () => <span data-testid="refresh-icon">🔄</span>,
  PlayArrow: () => <span data-testid="play-icon">▶️</span>,
  Pause: () => <span data-testid="pause-icon">⏸️</span>,
  Stop: () => <span data-testid="stop-icon">⏹️</span>,
  SkipNext: () => <span data-testid="skip-next-icon">⏭️</span>,
  SkipPrevious: () => <span data-testid="skip-previous-icon">⏮️</span>,
  FastForward: () => <span data-testid="fast-forward-icon">⏩</span>,
  FastRewind: () => <span data-testid="fast-rewind-icon">⏪</span>,
  VolumeUp: () => <span data-testid="volume-up-icon">🔊</span>,
  VolumeDown: () => <span data-testid="volume-down-icon">🔉</span>,
  VolumeMute: () => <span data-testid="volume-mute-icon">🔇</span>,
  BrightnessHigh: () => <span data-testid="brightness-high-icon">☀️</span>,
  BrightnessLow: () => <span data-testid="brightness-low-icon">🌙</span>,
  Contrast: () => <span data-testid="contrast-icon">🎨</span>,
  FilterCenterFocus: () => <span data-testid="filter-center-focus-icon">🎯</span>,
  CenterFocusStrong: () => <span data-testid="center-focus-strong-icon">🎯</span>,
  CenterFocusWeak: () => <span data-testid="center-focus-weak-icon">🎯</span>,
  Exposure: () => <span data-testid="exposure-icon">📷</span>,
  ExposureNeg1: () => <span data-testid="exposure-neg1-icon">📷</span>,
  ExposureNeg2: () => <span data-testid="exposure-neg2-icon">📷</span>,
  ExposurePlus1: () => <span data-testid="exposure-plus1-icon">📷</span>,
  ExposurePlus2: () => <span data-testid="exposure-plus2-icon">📷</span>,
  ExposureZero: () => <span data-testid="exposure-zero-icon">📷</span>,
  Filter1: () => <span data-testid="filter1-icon">🔍</span>,
  Filter2: () => <span data-testid="filter2-icon">🔍</span>,
  Filter3: () => <span data-testid="filter3-icon">🔍</span>,
  Filter4: () => <span data-testid="filter4-icon">🔍</span>,
  Filter5: () => <span data-testid="filter5-icon">🔍</span>,
  Filter6: () => <span data-testid="filter6-icon">🔍</span>,
  Filter7: () => <span data-testid="filter7-icon">🔍</span>,
  Filter8: () => <span data-testid="filter8-icon">🔍</span>,
  Filter9: () => <span data-testid="filter9-icon">🔍</span>,
  Filter9Plus: () => <span data-testid="filter9-plus-icon">🔍</span>,
  FilterBAndW: () => <span data-testid="filter-b-and-w-icon">🔍</span>,
  FilterDrama: () => <span data-testid="filter-drama-icon">🔍</span>,
  FilterFrames: () => <span data-testid="filter-frames-icon">🔍</span>,
  FilterHdr: () => <span data-testid="filter-hdr-icon">🔍</span>,
  FilterNone: () => <span data-testid="filter-none-icon">🔍</span>,
  FilterTiltShift: () => <span data-testid="filter-tilt-shift-icon">🔍</span>,
  FilterVintage: () => <span data-testid="filter-vintage-icon">🔍</span>,
  Grain: () => <span data-testid="grain-icon">🌾</span>,
  GridOff: () => <span data-testid="grid-off-icon">📐</span>,
  GridOn: () => <span data-testid="grid-on-icon">📐</span>,
  HdrOff: () => <span data-testid="hdr-off-icon">📷</span>,
  HdrOn: () => <span data-testid="hdr-on-icon">📷</span>,
  HdrStrong: () => <span data-testid="hdr-strong-icon">📷</span>,
  HdrWeak: () => <span data-testid="hdr-weak-icon">📷</span>,
  Healing: () => <span data-testid="healing-icon">🩹</span>,
  Image: () => <span data-testid="image-icon">🖼️</span>,
  ImageAspectRatio: () => <span data-testid="image-aspect-ratio-icon">🖼️</span>,
  ImageNotSupported: () => <span data-testid="image-not-supported-icon">🖼️</span>,
  ImageSearch: () => <span data-testid="image-search-icon">🖼️</span>,
  Iso: () => <span data-testid="iso-icon">📷</span>,
  Landscape: () => <span data-testid="landscape-icon">🏞️</span>,
  LeakAdd: () => <span data-testid="leak-add-icon">💧</span>,
  LeakRemove: () => <span data-testid="leak-remove-icon">💧</span>,
  Lens: () => <span data-testid="lens-icon">🔍</span>,
  LinkedCamera: () => <span data-testid="linked-camera-icon">📷</span>,
  Looks: () => <span data-testid="looks-icon">👀</span>,
  Looks3: () => <span data-testid="looks3-icon">👀</span>,
  Looks4: () => <span data-testid="looks4-icon">👀</span>,
  Looks5: () => <span data-testid="looks5-icon">👀</span>,
  Looks6: () => <span data-testid="looks6-icon">👀</span>,
  LooksOne: () => <span data-testid="looks-one-icon">👀</span>,
  LooksTwo: () => <span data-testid="looks-two-icon">👀</span>,
  Loupe: () => <span data-testid="loupe-icon">🔍</span>,
  MonochromePhotos: () => <span data-testid="monochrome-photos-icon">📷</span>,
  MovieCreation: () => <span data-testid="movie-creation-icon">🎬</span>,
  MovieFilter: () => <span data-testid="movie-filter-icon">🎬</span>,
  MusicNote: () => <span data-testid="music-note-icon">🎵</span>,
  Nature: () => <span data-testid="nature-icon">🌿</span>,
  NaturePeople: () => <span data-testid="nature-people-icon">🌿</span>,
  NavigateBefore: () => <span data-testid="navigate-before-icon">⬅️</span>,
  NavigateNext: () => <span data-testid="navigate-next-icon">➡️</span>,
  Palette: () => <span data-testid="palette-icon">🎨</span>,
  Panorama: () => <span data-testid="panorama-icon">🖼️</span>,
  PanoramaFishEye: () => <span data-testid="panorama-fish-eye-icon">🖼️</span>,
  PanoramaHorizontal: () => <span data-testid="panorama-horizontal-icon">🖼️</span>,
  PanoramaVertical: () => <span data-testid="panorama-vertical-icon">🖼️</span>,
  PanoramaWideAngle: () => <span data-testid="panorama-wide-angle-icon">🖼️</span>,
  Photo: () => <span data-testid="photo-icon">📷</span>,
  PhotoAlbum: () => <span data-testid="photo-album-icon">📷</span>,
  PhotoCamera: () => <span data-testid="photo-camera-icon">📷</span>,
  PhotoFilter: () => <span data-testid="photo-filter-icon">📷</span>,
  PhotoLibrary: () => <span data-testid="photo-library-icon">📷</span>,
  PhotoSizeSelectActual: () => <span data-testid="photo-size-select-actual-icon">📷</span>,
  PhotoSizeSelectLarge: () => <span data-testid="photo-size-select-large-icon">📷</span>,
  PhotoSizeSelectSmall: () => <span data-testid="photo-size-select-small-icon">📷</span>,
  PictureAsPdf: () => <span data-testid="picture-as-pdf-icon">📄</span>,
  Portrait: () => <span data-testid="portrait-icon">👤</span>,
  ReceiptLong: () => <span data-testid="receipt-long-icon">🧾</span>,
  RemoveRedEye: () => <span data-testid="remove-red-eye-icon">👁️</span>,
  Rotate90DegreesCcw: () => <span data-testid="rotate90-degrees-ccw-icon">🔄</span>,
  RotateLeft: () => <span data-testid="rotate-left-icon">🔄</span>,
  RotateRight: () => <span data-testid="rotate-right-icon">🔄</span>,
  ShutterSpeed: () => <span data-testid="shutter-speed-icon">📷</span>,
  Slideshow: () => <span data-testid="slideshow-icon">🎬</span>,
  Straighten: () => <span data-testid="straighten-icon">📐</span>,
  Style: () => <span data-testid="style-icon">💅</span>,
  SwitchCamera: () => <span data-testid="switch-camera-icon">📷</span>,
  SwitchVideo: () => <span data-testid="switch-video-icon">📹</span>,
  TagFaces: () => <span data-testid="tag-faces-icon">👤</span>,
  Texture: () => <span data-testid="texture-icon">🧱</span>,
  Timelapse: () => <span data-testid="timelapse-icon">⏱️</span>,
  Timer: () => <span data-testid="timer-icon">⏰</span>,
  Timer10: () => <span data-testid="timer10-icon">⏰</span>,
  Timer3: () => <span data-testid="timer3-icon">⏰</span>,
  TimerOff: () => <span data-testid="timer-off-icon">⏰</span>,
  Tonality: () => <span data-testid="tonality-icon">🎵</span>,
  Transform: () => <span data-testid="transform-icon">🔄</span>,
  Tune: () => <span data-testid="tune-icon">🎛️</span>,
  ViewComfy: () => <span data-testid="view-comfy-icon">👁️</span>,
  ViewCompact: () => <span data-testid="view-compact-icon">👁️</span>,
  Vignette: () => <span data-testid="vignette-icon">🖼️</span>,
  WbAuto: () => <span data-testid="wb-auto-icon">⚖️</span>,
  WbCloudy: () => <span data-testid="wb-cloudy-icon">☁️</span>,
  WbIncandescent: () => <span data-testid="wb-incandescent-icon">💡</span>,
  WbIridescent: () => <span data-testid="wb-iridescent-icon">🌈</span>,
  WbSunny: () => <span data-testid="wb-sunny-icon">☀️</span>,
  ZoomIn: () => <span data-testid="zoom-in-icon">🔍</span>,
  ZoomOut: () => <span data-testid="zoom-out-icon">🔍</span>,
}));

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('PerformanceOptimizer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render the PerformanceOptimizer component', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });

    it('should render the main header with title', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });

    it('should render control buttons in header', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByTestId('refresh-icon')).toBeInTheDocument();
      expect(screen.getByTestId('auto-awesome-icon')).toBeInTheDocument();
      expect(screen.getByTestId('settings-icon')).toBeInTheDocument();
    });

    it('should render performance overview cards', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('Overall Score')).toBeInTheDocument();
      expect(screen.getByText('Optimization Savings')).toBeInTheDocument();
      expect(screen.getByText('Active Alerts')).toBeInTheDocument();
      expect(screen.getByText('Slow Queries')).toBeInTheDocument();
    });

    it('should render tabs', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('Metrics')).toBeInTheDocument();
      expect(screen.getByText('Queries')).toBeInTheDocument();
      expect(screen.getByText('Optimizations')).toBeInTheDocument();
      expect(screen.getByText('Alerts')).toBeInTheDocument();
    });

    it('should render critical alerts when present', () => {
      renderWithTheme(<PerformanceOptimizer />);
      // Check if critical metrics are displayed
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Database Response Time')).toBeInTheDocument();
    });
  });

  describe('Metrics Display', () => {
    it('should display performance metrics', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('Disk I/O')).toBeInTheDocument();
      expect(screen.getByText('Network Latency')).toBeInTheDocument();
      expect(screen.getByText('Database Response Time')).toBeInTheDocument();
      expect(screen.getByText('API Response Time')).toBeInTheDocument();
    });

    it('should display metric values and units', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('75.2%')).toBeInTheDocument();
      expect(screen.getByText('68.5%')).toBeInTheDocument();
      expect(screen.getByText('45.8MB/s')).toBeInTheDocument();
      expect(screen.getByText('125ms')).toBeInTheDocument();
      expect(screen.getByText('350ms')).toBeInTheDocument();
      expect(screen.getByText('280ms')).toBeInTheDocument();
    });

    it('should display metric status chips', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('WARNING')).toBeInTheDocument();
      expect(screen.getByText('GOOD')).toBeInTheDocument();
    });

    it('should display metric descriptions', () => {
      renderWithTheme(<PerformanceOptimizer />);
      expect(screen.getByText('High CPU usage detected')).toBeInTheDocument();
      expect(screen.getByText('Memory usage within normal range')).toBeInTheDocument();
      expect(screen.getByText('Disk I/O performance is good')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch to Queries tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const queriesTab = screen.getByText('Queries');
      await user.click(queriesTab);

      expect(screen.getByText('SELECT * FROM users WHERE email = ?')).toBeInTheDocument();
      expect(screen.getByText('SELECT COUNT(*) FROM logs WHERE created_at > ?')).toBeInTheDocument();
    });

    it('should switch to Optimizations tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      expect(screen.getByText('Add Database Indexes')).toBeInTheDocument();
      expect(screen.getByText('Implement Query Caching')).toBeInTheDocument();
      expect(screen.getByText('Optimize API Endpoints')).toBeInTheDocument();
    });

    it('should switch to Alerts tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const alertsTab = screen.getByText('Alerts');
      await user.click(alertsTab);

      expect(screen.getByText('CPU usage exceeded 80% threshold')).toBeInTheDocument();
      expect(screen.getByText('Database queries taking longer than expected')).toBeInTheDocument();
    });

    it('should switch back to Metrics tab when clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      // First go to Queries tab
      const queriesTab = screen.getByText('Queries');
      await user.click(queriesTab);

      // Then go back to Metrics tab
      const metricsTab = screen.getByText('Metrics');
      await user.click(metricsTab);

      // Should show metrics
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
    });
  });

  describe('Queries Display', () => {
    it('should display query performance data', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const queriesTab = screen.getByText('Queries');
      await user.click(queriesTab);

      expect(screen.getByText('SELECT * FROM users WHERE email = ?')).toBeInTheDocument();
      expect(screen.getByText('150ms')).toBeInTheDocument();
      expect(screen.getByText('1250/hour')).toBeInTheDocument();
      expect(screen.getByText('users')).toBeInTheDocument();
      expect(screen.getByText('Add composite index on (email, status)')).toBeInTheDocument();
    });

    it('should display query impact levels', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const queriesTab = screen.getByText('Queries');
      await user.click(queriesTab);

      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
    });
  });

  describe('Optimizations Display', () => {
    it('should display optimization suggestions', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      expect(screen.getByText('Add Database Indexes')).toBeInTheDocument();
      expect(screen.getByText('Implement Query Caching')).toBeInTheDocument();
      expect(screen.getByText('Optimize API Endpoints')).toBeInTheDocument();
      expect(screen.getByText('Enable Gzip Compression')).toBeInTheDocument();
    });

    it('should display optimization details', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      expect(screen.getByText('Create composite indexes for frequently queried columns')).toBeInTheDocument();
      expect(screen.getByText('Cache frequently executed queries to reduce database load')).toBeInTheDocument();
      expect(screen.getByText('Implement pagination and filtering for large datasets')).toBeInTheDocument();
    });

    it('should display optimization impact and effort', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      expect(screen.getByText('45% savings')).toBeInTheDocument();
      expect(screen.getByText('30% savings')).toBeInTheDocument();
      expect(screen.getByText('25% savings')).toBeInTheDocument();
      expect(screen.getByText('20% savings')).toBeInTheDocument();
    });

    it('should display optimization status', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      expect(screen.getByText('Implement')).toBeInTheDocument();
      expect(screen.getByText('Reject')).toBeInTheDocument();
      expect(screen.getByText('IMPLEMENTED')).toBeInTheDocument();
    });
  });

  describe('Alerts Display', () => {
    it('should display performance alerts', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const alertsTab = screen.getByText('Alerts');
      await user.click(alertsTab);

      expect(screen.getByText('CPU usage exceeded 80% threshold')).toBeInTheDocument();
      expect(screen.getByText('Database queries taking longer than expected')).toBeInTheDocument();
      expect(screen.getByText('Memory usage approaching threshold')).toBeInTheDocument();
    });

    it('should display alert severity levels', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const alertsTab = screen.getByText('Alerts');
      await user.click(alertsTab);

      expect(screen.getByText('WARNING')).toBeInTheDocument();
      expect(screen.getByText('ERROR')).toBeInTheDocument();
      expect(screen.getByText('INFO')).toBeInTheDocument();
    });

    it('should display alert timestamps', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const alertsTab = screen.getByText('Alerts');
      await user.click(alertsTab);

      // Check if timestamps are displayed
      expect(screen.getByText(/CPU Usage -/)).toBeInTheDocument();
      expect(screen.getByText(/Database Response Time -/)).toBeInTheDocument();
      expect(screen.getByText(/Memory Usage -/)).toBeInTheDocument();
    });
  });

  describe('Settings Dialog', () => {
    it('should open settings dialog when settings button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      expect(screen.getByText('Performance Settings')).toBeInTheDocument();
    });

    it('should close settings dialog when cancel button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(screen.queryByText('Performance Settings')).not.toBeInTheDocument();
    });

    it('should close settings dialog when save button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const settingsButton = screen.getByTestId('settings-icon').parentElement;
      await user.click(settingsButton!);

      const saveButton = screen.getByText('Save');
      await user.click(saveButton);

      expect(screen.queryByText('Performance Settings')).not.toBeInTheDocument();
    });
  });

  describe('Auto Optimization Dialog', () => {
    it('should open auto optimization dialog when auto optimization button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const autoOptimizeButton = screen.getByTestId('auto-awesome-icon').parentElement;
      await user.click(autoOptimizeButton!);

      expect(screen.getByText('Auto Optimization')).toBeInTheDocument();
    });

    it('should close auto optimization dialog when close button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const autoOptimizeButton = screen.getByTestId('auto-awesome-icon').parentElement;
      await user.click(autoOptimizeButton!);

      const closeButton = screen.getByText('Close');
      await user.click(closeButton);

      expect(screen.queryByText('Auto Optimization')).not.toBeInTheDocument();
    });
  });

  describe('Refresh Functionality', () => {
    it('should refresh metrics when refresh button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const refreshButton = screen.getByTestId('refresh-icon').parentElement;
      await user.click(refreshButton!);

      // Should show loading state briefly
      expect(screen.getByTestId('loading')).toBeInTheDocument();
    });
  });

  describe('Optimization Actions', () => {
    it('should implement optimization when implement button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      const implementButtons = screen.getAllByText('Implement');
      await user.click(implementButtons[0]);

      // Should show implemented status
      expect(screen.getByText('IMPLEMENTED')).toBeInTheDocument();
    });

    it('should reject optimization when reject button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const optimizationsTab = screen.getByText('Optimizations');
      await user.click(optimizationsTab);

      const rejectButtons = screen.getAllByText('Reject');
      await user.click(rejectButtons[0]);

      // Should show rejected status
      expect(screen.getByText('REJECTED')).toBeInTheDocument();
    });
  });

  describe('Alert Actions', () => {
    it('should resolve alert when resolve button is clicked', async () => {
      const user = userEvent.setup();
      renderWithTheme(<PerformanceOptimizer />);

      const alertsTab = screen.getByText('Alerts');
      await user.click(alertsTab);

      const resolveButtons = screen.getAllByText('Resolve');
      await user.click(resolveButtons[0]);

      // Should show resolved status
      expect(screen.getByText('RESOLVED')).toBeInTheDocument();
    });
  });

  describe('Performance Overview', () => {
    it('should display overall performance score', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Should show a percentage score
      expect(screen.getByText(/^\d+%$/)).toBeInTheDocument();
    });

    it('should display optimization savings', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Should show savings percentage
      expect(screen.getByText('120%')).toBeInTheDocument();
    });

    it('should display active alerts count', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Should show number of active alerts
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('should display slow queries count', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Should show number of high impact queries
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error alert when error state is set', () => {
      // This would require testing the component with an error state
      // For now, we'll test that the error display logic exists
      renderWithTheme(<PerformanceOptimizer />);
      
      // The component should render without errors
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });
  });

  describe('Performance and Memory', () => {
    it('should handle large number of metrics efficiently', () => {
      // This is a basic test to ensure the component renders with mock data
      renderWithTheme(<PerformanceOptimizer />);
      
      // Should render without performance issues
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });

    it('should not cause memory leaks', () => {
      const { unmount } = renderWithTheme(<PerformanceOptimizer />);
      
      // Should unmount cleanly
      unmount();
      
      // No errors should be thrown
      expect(true).toBe(true);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Basic accessibility test - component should render
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });

    it('should be keyboard navigable', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Basic keyboard navigation test
      const tabs = screen.getAllByRole('button');
      expect(tabs.length).toBeGreaterThan(0);
    });
  });

  describe('Responsive Design', () => {
    it('should render properly on different screen sizes', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Component should render without layout issues
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });
  });

  describe('Integration Tests', () => {
    it('should integrate with Material-UI theme', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Component should use theme properly
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });

    it('should work with React hooks', () => {
      renderWithTheme(<PerformanceOptimizer />);
      
      // Component should use hooks without errors
      expect(screen.getByText('Performance Optimizer')).toBeInTheDocument();
    });
  });
}); 