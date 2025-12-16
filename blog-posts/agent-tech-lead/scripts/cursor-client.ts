import 'dotenv/config'

const BASE_URL = 'https://api.cursor.com'

interface AgentSource {
  repository: string
  ref?: string
}

interface AgentTarget {
  branchName?: string
  url?: string
  prUrl?: string
  autoCreatePr?: boolean
  openAsCursorGithubApp?: boolean
  skipReviewerRequest?: boolean
}

interface Agent {
  id: string
  name: string
  status: 'CREATING' | 'RUNNING' | 'FINISHED' | 'STOPPED'
  source: AgentSource
  target: AgentTarget
  summary?: string
  createdAt: string
}

interface ListAgentsResponse {
  agents: Agent[]
  nextCursor?: string
}

interface Message {
  id: string
  type: 'user_message' | 'assistant_message'
  text: string
}

interface ConversationResponse {
  id: string
  messages: Message[]
}

interface PromptImage {
  data: string
  dimension: { width: number; height: number }
}

interface Prompt {
  text: string
  images?: PromptImage[]
}

interface CreateAgentParams {
  prompt: Prompt
  source: AgentSource
  model?: string
  target?: {
    autoCreatePr?: boolean
    openAsCursorGithubApp?: boolean
    skipReviewerRequest?: boolean
    branchName?: string
  }
  webhook?: {
    url: string
    secret?: string
  }
}

interface ApiKeyInfo {
  apiKeyName: string
  createdAt: string
  userEmail: string
}

interface ModelsResponse {
  models: string[]
}

interface Repository {
  owner: string
  name: string
  repository: string
}

interface RepositoriesResponse {
  repositories: Repository[]
}

export class CursorClient {
  private apiKey: string

  constructor(apiKey?: string) {
    this.apiKey = apiKey ?? process.env.CURSOR_API_KEY ?? ''
    if (!this.apiKey) {
      throw new Error('CURSOR_API_KEY is required')
    }
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: {
        Authorization: `Basic ${Buffer.from(this.apiKey + ':').toString('base64')}`,
        'Content-Type': 'application/json'
      },
      body: body ? JSON.stringify(body) : undefined
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(`API error ${response.status}: ${text}`)
    }

    return response.json()
  }

  async listAgents(limit?: number, cursor?: string): Promise<ListAgentsResponse> {
    const params = new URLSearchParams()
    if (limit) params.set('limit', String(limit))
    if (cursor) params.set('cursor', cursor)
    const query = params.toString() ? `?${params}` : ''
    return this.request('GET', `/v0/agents${query}`)
  }

  async getAgent(id: string): Promise<Agent> {
    return this.request('GET', `/v0/agents/${id}`)
  }

  async getConversation(id: string): Promise<ConversationResponse> {
    return this.request('GET', `/v0/agents/${id}/conversation`)
  }

  async createAgent(params: CreateAgentParams): Promise<Agent> {
    return this.request('POST', '/v0/agents', params)
  }

  async addFollowup(id: string, prompt: Prompt): Promise<{ id: string }> {
    return this.request('POST', `/v0/agents/${id}/followup`, { prompt })
  }

  async stopAgent(id: string): Promise<{ id: string }> {
    return this.request('POST', `/v0/agents/${id}/stop`)
  }

  async deleteAgent(id: string): Promise<{ id: string }> {
    return this.request('DELETE', `/v0/agents/${id}`)
  }

  async getMe(): Promise<ApiKeyInfo> {
    return this.request('GET', '/v0/me')
  }

  async listModels(): Promise<ModelsResponse> {
    return this.request('GET', '/v0/models')
  }

  async listRepositories(): Promise<RepositoriesResponse> {
    return this.request('GET', '/v0/repositories')
  }
}

export type {
  Agent,
  AgentSource,
  AgentTarget,
  ListAgentsResponse,
  Message,
  ConversationResponse,
  Prompt,
  PromptImage,
  CreateAgentParams,
  ApiKeyInfo,
  ModelsResponse,
  Repository,
  RepositoriesResponse
}

