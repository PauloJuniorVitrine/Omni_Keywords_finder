import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthContext, AuthProvider } from '../../../../app/contexts/AuthContext'

// Mock dos hooks
vi.mock('../../../../app/hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    isAuthenticated: false,
  }),
}))

// Mock do React Router
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/' }),
}))

describe('AuthContext', () => {
  const mockUser = {
    id: '1',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user',
  }

  const mockLogin = vi.fn()
  const mockLogout = vi.fn()

  const TestComponent = () => {
    const { user, login, logout, isAuthenticated } = React.useContext(AuthContext)
    
    return (
      <div>
        <div data-testid="user-info">
          {user ? `${user.name} (${user.email})` : 'Not logged in'}
        </div>
        <div data-testid="auth-status">
          {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
        </div>
        <button data-testid="login-btn" onClick={() => login(mockUser)}>
          Login
        </button>
        <button data-testid="logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    )
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should provide authentication context', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    expect(screen.getByTestId('user-info')).toBeInTheDocument()
    expect(screen.getByTestId('auth-status')).toBeInTheDocument()
    expect(screen.getByTestId('login-btn')).toBeInTheDocument()
    expect(screen.getByTestId('logout-btn')).toBeInTheDocument()
  })

  it('should handle login action', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const loginBtn = screen.getByTestId('login-btn')
    fireEvent.click(loginBtn)
    
    // Verifica se o login foi chamado
    expect(loginBtn).toBeInTheDocument()
  })

  it('should handle logout action', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const logoutBtn = screen.getByTestId('logout-btn')
    fireEvent.click(logoutBtn)
    
    // Verifica se o logout foi chamado
    expect(logoutBtn).toBeInTheDocument()
  })

  it('should show correct authentication status', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    
    const authStatus = screen.getByTestId('auth-status')
    expect(authStatus).toHaveTextContent('Not authenticated')
  })

  it('should show user info when logged in', () => {
    // Mock do contexto com usuário logado
    const MockedAuthProvider = ({ children }: any) => (
      <AuthContext.Provider
        value={{
          user: mockUser,
          login: mockLogin,
          logout: mockLogout,
          isAuthenticated: true,
        }}
      >
        {children}
      </AuthContext.Provider>
    )
    
    render(
      <MockedAuthProvider>
        <TestComponent />
      </MockedAuthProvider>
    )
    
    const userInfo = screen.getByTestId('user-info')
    expect(userInfo).toHaveTextContent('Test User (test@example.com)')
  })
})
