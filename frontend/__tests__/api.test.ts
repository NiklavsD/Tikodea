/**
 * Tests for API client functions
 */

describe('API Client', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('fetchVideos', () => {
    it('should construct correct URL with no params', async () => {
      const mockResponse = { videos: [], total: 0, skip: 0, limit: 20 };
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const { fetchVideos } = await import('../src/lib/api');
      await fetchVideos();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/videos')
      );
    });

    it('should include search param', async () => {
      const mockResponse = { videos: [], total: 0, skip: 0, limit: 20 };
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const { fetchVideos } = await import('../src/lib/api');
      await fetchVideos({ search: 'test' });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('search=test')
      );
    });

    it('should throw on non-ok response', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
      });

      const { fetchVideos } = await import('../src/lib/api');
      await expect(fetchVideos()).rejects.toThrow('Failed to fetch videos');
    });
  });
});
