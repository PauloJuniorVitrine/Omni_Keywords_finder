import { renderHook, waitFor } from '@testing-library/react';
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

describe('useApi Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('GET requests', () => {
    it('should make GET request successfully', async () => {
      const mockData = { id: 1, name: 'Test' };
      mockHttpClient.get.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/test');

      expect(mockHttpClient.get).toHaveBeenCalledWith('/test', undefined);
      expect(response).toEqual({ data: mockData });
    });

    it('should make GET request with config', async () => {
      const mockData = { id: 1, name: 'Test' };
      const config = { params: { page: 1 } };
      mockHttpClient.get.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/test', config);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/test', config);
      expect(response).toEqual({ data: mockData });
    });

    it('should handle GET request error', async () => {
      const error = new Error('Network error');
      mockHttpClient.get.mockRejectedValue(error);

      const { result } = renderHook(() => useApi());

      await expect(result.current.get('/test')).rejects.toThrow('Network error');
    });
  });

  describe('POST requests', () => {
    it('should make POST request successfully', async () => {
      const mockData = { id: 1, name: 'Test' };
      const postData = { name: 'Test' };
      mockHttpClient.post.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.post('/test', postData);

      expect(mockHttpClient.post).toHaveBeenCalledWith('/test', postData, undefined);
      expect(response).toEqual({ data: mockData });
    });

    it('should make POST request with config', async () => {
      const mockData = { id: 1, name: 'Test' };
      const postData = { name: 'Test' };
      const config = { headers: { 'Content-Type': 'application/json' } };
      mockHttpClient.post.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.post('/test', postData, config);

      expect(mockHttpClient.post).toHaveBeenCalledWith('/test', postData, config);
      expect(response).toEqual({ data: mockData });
    });

    it('should handle POST request error', async () => {
      const error = new Error('Network error');
      mockHttpClient.post.mockRejectedValue(error);

      const { result } = renderHook(() => useApi());

      await expect(result.current.post('/test', {})).rejects.toThrow('Network error');
    });
  });

  describe('PUT requests', () => {
    it('should make PUT request successfully', async () => {
      const mockData = { id: 1, name: 'Updated Test' };
      const putData = { name: 'Updated Test' };
      mockHttpClient.put.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.put('/test/1', putData);

      expect(mockHttpClient.put).toHaveBeenCalledWith('/test/1', putData, undefined);
      expect(response).toEqual({ data: mockData });
    });

    it('should handle PUT request error', async () => {
      const error = new Error('Network error');
      mockHttpClient.put.mockRejectedValue(error);

      const { result } = renderHook(() => useApi());

      await expect(result.current.put('/test/1', {})).rejects.toThrow('Network error');
    });
  });

  describe('DELETE requests', () => {
    it('should make DELETE request successfully', async () => {
      mockHttpClient.delete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() => useApi());

      const response = await result.current.delete('/test/1');

      expect(mockHttpClient.delete).toHaveBeenCalledWith('/test/1', undefined);
      expect(response).toEqual({ data: { success: true } });
    });

    it('should handle DELETE request error', async () => {
      const error = new Error('Network error');
      mockHttpClient.delete.mockRejectedValue(error);

      const { result } = renderHook(() => useApi());

      await expect(result.current.delete('/test/1')).rejects.toThrow('Network error');
    });
  });

  describe('PATCH requests', () => {
    it('should make PATCH request successfully', async () => {
      const mockData = { id: 1, name: 'Partially Updated' };
      const patchData = { name: 'Partially Updated' };
      mockHttpClient.patch.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.patch('/test/1', patchData);

      expect(mockHttpClient.patch).toHaveBeenCalledWith('/test/1', patchData, undefined);
      expect(response).toEqual({ data: mockData });
    });

    it('should handle PATCH request error', async () => {
      const error = new Error('Network error');
      mockHttpClient.patch.mockRejectedValue(error);

      const { result } = renderHook(() => useApi());

      await expect(result.current.patch('/test/1', {})).rejects.toThrow('Network error');
    });
  });

  describe('Polling functionality', () => {
    it('should start polling when enabled', async () => {
      const mockData = { id: 1, status: 'processing' };
      mockHttpClient.get.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      const startPolling = result.current.startPolling;
      const stopPolling = result.current.stopPolling;

      expect(typeof startPolling).toBe('function');
      expect(typeof stopPolling).toBe('function');
    });

    it('should handle polling with success condition', async () => {
      const processingData = { id: 1, status: 'processing' };
      const completedData = { id: 1, status: 'completed' };
      
      mockHttpClient.get
        .mockResolvedValueOnce({ data: processingData })
        .mockResolvedValueOnce({ data: completedData });

      const { result } = renderHook(() => useApi());

      const response = await result.current.get('/test', undefined, {
        poll: true,
        pollInterval: 1000,
        pollCondition: (data) => data.status === 'completed'
      });

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2);
      expect(response).toEqual({ data: completedData });
    });
  });

  describe('Cache functionality', () => {
    it('should use cache when enabled', async () => {
      const mockData = { id: 1, name: 'Cached Data' };
      mockHttpClient.get.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      // Primeira chamada
      const response1 = await result.current.get('/test', undefined, { cache: true });
      
      // Segunda chamada (deve usar cache)
      const response2 = await result.current.get('/test', undefined, { cache: true });

      expect(mockHttpClient.get).toHaveBeenCalledTimes(1);
      expect(response1).toEqual({ data: mockData });
      expect(response2).toEqual({ data: mockData });
    });

    it('should not use cache when disabled', async () => {
      const mockData = { id: 1, name: 'Fresh Data' };
      mockHttpClient.get.mockResolvedValue({ data: mockData });

      const { result } = renderHook(() => useApi());

      // Primeira chamada
      await result.current.get('/test', undefined, { cache: false });
      
      // Segunda chamada (não deve usar cache)
      await result.current.get('/test', undefined, { cache: false });

      expect(mockHttpClient.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('Upload functionality', () => {
    it('should handle file upload', async () => {
      const mockResponse = { data: { url: 'https://example.com/file.pdf' } };
      const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      
      // Mock do método de upload (que seria uma extensão do httpClient)
      const mockUpload = jest.fn().mockResolvedValue(mockResponse);
      mockHttpClient.upload = mockUpload;

      const { result } = renderHook(() => useApi());

      const response = await result.current.upload('/upload', mockFile);

      expect(mockUpload).toHaveBeenCalledWith('/upload', mockFile, undefined);
      expect(response).toEqual(mockResponse);
    });

    it('should handle upload with progress callback', async () => {
      const mockResponse = { data: { url: 'https://example.com/file.pdf' } };
      const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const progressCallback = jest.fn();
      
      const mockUpload = jest.fn().mockResolvedValue(mockResponse);
      mockHttpClient.upload = mockUpload;

      const { result } = renderHook(() => useApi());

      const response = await result.current.upload('/upload', mockFile, {
        onProgress: progressCallback
      });

      expect(mockUpload).toHaveBeenCalledWith('/upload', mockFile, {
        onProgress: progressCallback
      });
      expect(response).toEqual(mockResponse);
    });
  });
}); 