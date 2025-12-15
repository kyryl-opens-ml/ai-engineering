import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { CursorClient } from '../../scripts/cursor-client.js'

const mockFetch = vi.fn()
global.fetch = mockFetch

describe('CursorClient', () => {
  const TEST_API_KEY = 'test-api-key'

  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('constructor', () => {
    it('should create client with provided API key', () => {
      const client = new CursorClient(TEST_API_KEY)
      expect(client).toBeDefined()
    })

    it('should throw error when no API key provided', () => {
      const originalEnv = process.env.CURSOR_API_KEY
      delete process.env.CURSOR_API_KEY
      expect(() => new CursorClient()).toThrow('CURSOR_API_KEY is required')
      process.env.CURSOR_API_KEY = originalEnv
    })

    it('should use environment variable when no key provided', () => {
      const originalEnv = process.env.CURSOR_API_KEY
      process.env.CURSOR_API_KEY = 'env-api-key'
      const client = new CursorClient()
      expect(client).toBeDefined()
      process.env.CURSOR_API_KEY = originalEnv
    })
  })

  describe('listAgents', () => {
    it('should fetch agents without params', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockResponse = { agents: [], nextCursor: undefined }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const result = await client.listAgents()

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('should fetch agents with limit and cursor', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockResponse = { agents: [], nextCursor: 'next' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      await client.listAgents(10, 'cursor123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents?limit=10&cursor=cursor123',
        expect.any(Object)
      )
    })
  })

  describe('getAgent', () => {
    it('should fetch specific agent by id', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockAgent = {
        id: 'agent-123',
        name: 'Test Agent',
        status: 'RUNNING',
        source: { repository: 'test/repo' },
        target: {},
        createdAt: '2024-01-01T00:00:00Z'
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAgent)
      })

      const result = await client.getAgent('agent-123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents/agent-123',
        expect.any(Object)
      )
      expect(result).toEqual(mockAgent)
    })
  })

  describe('getConversation', () => {
    it('should fetch conversation for agent', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockConversation = {
        id: 'conv-123',
        messages: [{ id: 'msg-1', type: 'user_message', text: 'Hello' }]
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockConversation)
      })

      const result = await client.getConversation('agent-123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents/agent-123/conversation',
        expect.any(Object)
      )
      expect(result).toEqual(mockConversation)
    })
  })

  describe('createAgent', () => {
    it('should create new agent', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockAgent = {
        id: 'new-agent',
        name: 'New Agent',
        status: 'CREATING',
        source: { repository: 'test/repo' },
        target: {},
        createdAt: '2024-01-01T00:00:00Z'
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAgent)
      })

      const params = {
        prompt: { text: 'Build a feature' },
        source: { repository: 'test/repo' }
      }
      const result = await client.createAgent(params)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(params)
        })
      )
      expect(result).toEqual(mockAgent)
    })
  })

  describe('addFollowup', () => {
    it('should add followup to agent', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'agent-123' })
      })

      const prompt = { text: 'Also do this' }
      const result = await client.addFollowup('agent-123', prompt)

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents/agent-123/followup',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ prompt })
        })
      )
      expect(result).toEqual({ id: 'agent-123' })
    })
  })

  describe('stopAgent', () => {
    it('should stop agent', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'agent-123' })
      })

      const result = await client.stopAgent('agent-123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents/agent-123/stop',
        expect.objectContaining({ method: 'POST' })
      )
      expect(result).toEqual({ id: 'agent-123' })
    })
  })

  describe('deleteAgent', () => {
    it('should delete agent', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'agent-123' })
      })

      const result = await client.deleteAgent('agent-123')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/agents/agent-123',
        expect.objectContaining({ method: 'DELETE' })
      )
      expect(result).toEqual({ id: 'agent-123' })
    })
  })

  describe('getMe', () => {
    it('should fetch API key info', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockInfo = {
        apiKeyName: 'my-key',
        createdAt: '2024-01-01T00:00:00Z',
        userEmail: 'test@example.com'
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockInfo)
      })

      const result = await client.getMe()

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/me',
        expect.any(Object)
      )
      expect(result).toEqual(mockInfo)
    })
  })

  describe('listModels', () => {
    it('should list available models', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockModels = { models: ['model-1', 'model-2'] }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockModels)
      })

      const result = await client.listModels()

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/models',
        expect.any(Object)
      )
      expect(result).toEqual(mockModels)
    })
  })

  describe('listRepositories', () => {
    it('should list repositories', async () => {
      const client = new CursorClient(TEST_API_KEY)
      const mockRepos = {
        repositories: [
          { owner: 'user', name: 'repo', repository: 'user/repo' }
        ]
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRepos)
      })

      const result = await client.listRepositories()

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.cursor.com/v0/repositories',
        expect.any(Object)
      )
      expect(result).toEqual(mockRepos)
    })
  })

  describe('error handling', () => {
    it('should throw on API error', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: () => Promise.resolve('Unauthorized')
      })

      await expect(client.listAgents()).rejects.toThrow('API error 401: Unauthorized')
    })

    it('should throw on server error', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: () => Promise.resolve('Internal Server Error')
      })

      await expect(client.getAgent('123')).rejects.toThrow('API error 500: Internal Server Error')
    })
  })

  describe('authorization header', () => {
    it('should send correct Basic auth header', async () => {
      const client = new CursorClient(TEST_API_KEY)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ agents: [] })
      })

      await client.listAgents()

      const expectedAuth = `Basic ${Buffer.from(TEST_API_KEY + ':').toString('base64')}`
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: expectedAuth
          })
        })
      )
    })
  })
})
