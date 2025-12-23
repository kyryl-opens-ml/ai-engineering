import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CursorClient } from '../../src/main/cursor-client'

describe('CursorClient', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    vi.resetAllMocks()
    global.fetch = vi.fn()
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  it('uses basic auth with API key', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ agents: [] })
    })
    global.fetch = mockFetch

    const client = new CursorClient('test-api-key')
    await client.listAgents()

    expect(mockFetch).toHaveBeenCalledWith(
      'https://api.cursor.com/v0/agents',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Basic ${Buffer.from('test-api-key:').toString('base64')}`
        })
      })
    )
  })

  it('handles successful agent creation', async () => {
    const mockAgent = {
      id: 'bc_abc123',
      name: 'Test Agent',
      status: 'CREATING',
      source: { repository: 'https://github.com/test/repo' },
      target: { url: 'https://cursor.com/agents?id=bc_abc123' }
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockAgent)
    })

    const client = new CursorClient('test-api-key')
    const result = await client.createAgent({
      prompt: { text: 'Test prompt' },
      source: { repository: 'https://github.com/test/repo' }
    })

    expect(result).toEqual(mockAgent)
  })

  it('handles API errors with status code', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized')
    })

    const client = new CursorClient('invalid-key')
    await expect(client.listAgents()).rejects.toThrow('API error 401: Unauthorized')
  })

  it('paginates through agent list', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ agents: [], nextCursor: 'cursor123' })
    })

    const client = new CursorClient('test-api-key')
    await client.listAgents(50, 'prev-cursor')

    expect(global.fetch).toHaveBeenCalledWith(
      'https://api.cursor.com/v0/agents?limit=50&cursor=prev-cursor',
      expect.anything()
    )
  })

  it('sends followup to correct endpoint', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'bc_abc123' })
    })

    const client = new CursorClient('test-api-key')
    await client.addFollowup('bc_abc123', { text: 'Follow up message' })

    expect(global.fetch).toHaveBeenCalledWith(
      'https://api.cursor.com/v0/agents/bc_abc123/followup',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ prompt: { text: 'Follow up message' } })
      })
    )
  })
})

