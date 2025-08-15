import { vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock do React Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  useQueryClient: vi.fn(),
  QueryClient: vi.fn(),
  QueryClientProvider: vi.fn(),
}))

// Mock do React Router
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(),
  useLocation: vi.fn(),
  useParams: vi.fn(),
  Link: vi.fn(),
  Navigate: vi.fn(),
}))

// Mock do Material-UI
vi.mock('@mui/material', () => ({
  Button: vi.fn(),
  TextField: vi.fn(),
  Box: vi.fn(),
  Typography: vi.fn(),
  Container: vi.fn(),
  Paper: vi.fn(),
}))

// Mock do React Hot Toast
vi.mock('react-hot-toast', () => ({
  toast: vi.fn(),
  Toaster: vi.fn(),
}))

// Cleanup após cada teste
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

// Configuração global
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

global.matchMedia = vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}))
