import { renderHook, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { useApi } from '../../../app/hooks/useApi';

// Mock do httpClient
const mockHttpClient = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  patch: jest.fn()
};

jest.mock('../../../app/utils/httpClient', () => ({
  httpClient: mockHttpClient
}));

// Mock do MSW para simular API
const server = setupServer(
  rest.get('/api/admin/dashboard', (req, res, ctx) => {
    return res(
      ctx.json({
        users: { total: 100, active: 85, inactive: 15 },
        keywords: { total: 5000, processed: 4500, pending: 500 },
        performance: { avgResponseTime: 250, uptime: 99.9 },
        security: { threats: 0, lastScan: '2025-01-27T18:30:00Z' }
      })
    );
  }),

  rest.get('/api/admin/users', (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1';
    const limit = req.url.searchParams.get('limit') || '10';
    
    return res(
      ctx.json({
        users: Array.from({ length: parseInt(limit) }, (_, i) => ({
          id: i + 1,
          name: `User ${i + 1}`,
          email: `user${i + 1}@example.com`,
          role: i % 3 === 0 ? 'admin' : i % 3 === 1 ? 'moderator' : 'user',
          status: i % 4 === 0 ? 'inactive' : 'active',
          lastLogin: new Date(Date.now() - i * 86400000).toISOString()
        })),
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: 100,
          pages: 10
        }
      })
    );
  }),

  rest.post('/api/admin/users', (req, res, ctx) => {
    const { name, email, role } = req.body as any;
    
    if (!name || !email || !role) {
      return res(
        ctx.status(400),
        ctx.json({ error: 'Missing required fields' })
      );
    }
    
    return res(
      ctx.status(201),
      ctx.json({
        id: Math.floor(Math.random() * 1000),
        name,
        email,
        role,
        status: 'active',
        createdAt: new Date().toISOString()
      })
    );
  }),

  rest.put('/api/admin/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    const { name, email, role, status } = req.body as any;
    
    return res(
      ctx.json({
        id: parseInt(id as string),
        name,
        email,
        role,
        status,
        updatedAt: new Date().toISOString()
      })
    );
  }),

  rest.delete('/api/admin/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    
    return res(
      ctx.json({
        success: true,
        message: `User ${id} deleted successfully`
      })
    );
  }),

  rest.get('/api/admin/logs', (req, res, ctx) => {
    const level = req.url.searchParams.get('level') || 'info';
    const limit = req.url.searchParams.get('limit') || '50';
    
    return res(
      ctx.json({
        logs: Array.from({ length: parseInt(limit) }, (_, i) => ({
          id: i + 1,
          timestamp: new Date(Date.now() - i * 60000).toISOString(),
          level,
          message: `Log message ${i + 1}`,
          source: 'api',
          userId: Math.floor(Math.random() * 100) + 1,
          ip: `192.168.1.${Math.floor(Math.random() * 255)}`
        })),
        pagination: {
          total: 1000,
          pages: 20
        }
      })
    );
  }),

  rest.get('/api/admin/performance', (req, res, ctx) => {
    return res(
      ctx.json({
        metrics: {
          responseTime: {
            avg: 250,
            p95: 500,
            p99: 1000
          },
          throughput: {
            requestsPerSecond: 100,
            totalRequests: 1000000
          },
          errors: {
            rate: 0.1,
            total: 1000
          }
        },
        recommendations: [
          'Consider implementing caching for frequently accessed data',
          'Database queries could be optimized',
          'Consider using CDN for static assets'
        ]
      })
    );
  }),

  rest.post('/api/admin/optimize', (req, res, ctx) => {
    const { type } = req.body as any;
    
    return res(
      ctx.json({
        success: true,
        message: `Optimization ${type} completed successfully`,
        improvements: {
          responseTime: -50,
          throughput: 10,
          memoryUsage: -20
        }
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Admin API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Dashboard API', () => {
    it('should fetch dashboard data successfully', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/api/admin/dashboard');

      expect(response.data).toEqual({
        users: { total: 100, active: 85, inactive: 15 },
        keywords: { total: 5000, processed: 4500, pending: 500 },
        performance: { avgResponseTime: 250, uptime: 99.9 },
        security: { threats: 0, lastScan: '2025-01-27T18:30:00Z' }
      });
    });

    it('should handle dashboard API errors', async () => {
      server.use(
        rest.get('/api/admin/dashboard', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ error: 'Internal server error' }));
        })
      );

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/api/admin/dashboard')).rejects.toThrow();
    });
  });

  describe('Users API', () => {
    it('should fetch users with pagination', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/api/admin/users', {
        params: { page: 2, limit: 5 }
      });

      expect(response.data.users).toHaveLength(5);
      expect(response.data.pagination.page).toBe(2);
      expect(response.data.pagination.limit).toBe(5);
    });

    it('should create new user successfully', async () => {
      const { result } = renderHook(() => useApi());

      const newUser = {
        name: 'John Doe',
        email: 'john@example.com',
        role: 'user'
      };

      const response = await result.current.post('/api/admin/users', newUser);

      expect(response.status).toBe(201);
      expect(response.data.name).toBe(newUser.name);
      expect(response.data.email).toBe(newUser.email);
      expect(response.data.role).toBe(newUser.role);
    });

    it('should handle user creation validation errors', async () => {
      const { result } = renderHook(() => useApi());

      const invalidUser = {
        name: 'John Doe'
        // Missing email and role
      };

      await expect(result.current.post('/api/admin/users', invalidUser)).rejects.toThrow();
    });

    it('should update user successfully', async () => {
      const { result } = renderHook(() => useApi());

      const updates = {
        name: 'Jane Doe',
        email: 'jane@example.com',
        role: 'moderator',
        status: 'active'
      };

      const response = await result.current.put('/api/admin/users/1', updates);

      expect(response.data.name).toBe(updates.name);
      expect(response.data.email).toBe(updates.email);
      expect(response.data.role).toBe(updates.role);
      expect(response.data.status).toBe(updates.status);
    });

    it('should delete user successfully', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.delete('/api/admin/users/1');

      expect(response.data.success).toBe(true);
      expect(response.data.message).toContain('deleted successfully');
    });
  });

  describe('Logs API', () => {
    it('should fetch logs with filters', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/api/admin/logs', {
        params: { level: 'error', limit: 10 }
      });

      expect(response.data.logs).toHaveLength(10);
      expect(response.data.logs[0].level).toBe('error');
      expect(response.data.pagination.total).toBe(1000);
    });

    it('should handle logs API errors', async () => {
      server.use(
        rest.get('/api/admin/logs', (req, res, ctx) => {
          return res(ctx.status(403), ctx.json({ error: 'Access denied' }));
        })
      );

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/api/admin/logs')).rejects.toThrow();
    });
  });

  describe('Performance API', () => {
    it('should fetch performance metrics', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/api/admin/performance');

      expect(response.data.metrics.responseTime.avg).toBe(250);
      expect(response.data.metrics.throughput.requestsPerSecond).toBe(100);
      expect(response.data.recommendations).toHaveLength(3);
    });

    it('should trigger optimization successfully', async () => {
      const { result } = renderHook(() => useApi());

      const response = await result.current.post('/api/admin/optimize', {
        type: 'database'
      });

      expect(response.data.success).toBe(true);
      expect(response.data.improvements.responseTime).toBe(-50);
      expect(response.data.improvements.throughput).toBe(10);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      server.use(
        rest.get('/api/admin/dashboard', (req, res, ctx) => {
          return res.networkError('Failed to connect');
        })
      );

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/api/admin/dashboard')).rejects.toThrow();
    });

    it('should handle timeout errors', async () => {
      server.use(
        rest.get('/api/admin/dashboard', (req, res, ctx) => {
          return res(ctx.delay(10000)); // 10 second delay
        })
      );

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/api/admin/dashboard')).rejects.toThrow();
    });
  });

  describe('Authentication Integration', () => {
    it('should include auth headers in requests', async () => {
      const { result } = renderHook(() => useApi());

      // Simular token no localStorage
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn().mockReturnValue('mock-token')
        },
        writable: true
      });

      await result.current.get('/api/admin/dashboard');

      // Verificar se o token foi incluído no header
      expect(mockHttpClient.get).toHaveBeenCalledWith(
        '/api/admin/dashboard',
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token'
          })
        })
      );
    });

    it('should handle token refresh on 401', async () => {
      server.use(
        rest.get('/api/admin/dashboard', (req, res, ctx) => {
          return res(ctx.status(401), ctx.json({ error: 'Unauthorized' }));
        })
      );

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/api/admin/dashboard')).rejects.toThrow();
    });
  });
}); 