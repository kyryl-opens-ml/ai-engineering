import { BrowserWindow } from 'electron'
import { CursorClient } from './cursor-client'
import * as db from './db'
import type { Task, AgentStatus, AgentMessage } from '../shared/types'

const POLL_INTERVAL = 10_000
const CACHE_TTL = 5 * 60 * 1000

interface CacheEntry<T> {
  data: T
  timestamp: number
}

export class AgentService {
  private client: CursorClient
  private pollInterval: NodeJS.Timeout | null = null
  private cache: Map<string, CacheEntry<unknown>> = new Map()

  constructor(apiKey?: string) {
    this.client = new CursorClient(apiKey)
  }

  private getCached<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null
    if (Date.now() - entry.timestamp > CACHE_TTL) {
      this.cache.delete(key)
      return null
    }
    return entry.data as T
  }

  private setCache<T>(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() })
  }

  clearCache(): void {
    this.cache.clear()
  }

  async startBuild(taskId: string): Promise<Task> {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (!task.description) throw new Error('Task needs a description to start the agent')

    const project = db.getProject(task.project_id)
    if (!project) throw new Error('Project not found')

    let promptText = task.description
    if (project.subfolder) {
      promptText = `Work from ${project.subfolder} subfolder\n\n${task.description}`
    }

    const baseBranch = task.base_branch || project.default_branch

    const agent = await this.client.createAgent({
      prompt: { text: promptText },
      source: {
        repository: project.repository,
        ...(baseBranch && { ref: baseBranch })
      },
      model: task.model || undefined,
      target: {
        autoCreatePr: false,
        ...(task.target_branch && { branchName: task.target_branch })
      }
    })

    db.updateAgentStatus(taskId, agent.id, agent.status as AgentStatus, agent.target.url)

    return db.getTask(taskId)!
  }

  async sendFollowup(taskId: string, message: string): Promise<Task> {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (!task.agent_id) throw new Error('No agent found for task')

    await this.client.addFollowup(task.agent_id, { text: message })
    db.updateAgentStatus(taskId, task.agent_id, 'RUNNING')

    return db.getTask(taskId)!
  }

  async getConversation(taskId: string): Promise<AgentMessage[]> {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (!task.agent_id) return []

    try {
      const response = await this.client.getConversation(task.agent_id)
      return response.messages
    } catch {
      return []
    }
  }

  startPolling(onUpdate: (task: Task) => void) {
    if (this.pollInterval) return

    this.pollInterval = setInterval(async () => {
      const runningTasks = db.getTasksWithRunningAgents()

      for (const task of runningTasks) {
        try {
          if (task.agent_id) {
            const agent = await this.client.getAgent(task.agent_id)
            if (agent.status !== task.agent_status) {
              db.updateAgentStatus(task.id, task.agent_id, agent.status as AgentStatus)
              if (agent.status === 'FINISHED' && task.status === 'build') {
                db.moveTask(task.id, 'review', 0)
              }
              onUpdate(db.getTask(task.id)!)
            }
          }
        } catch (err) {
          console.error(`Failed to poll agent status for task ${task.id}:`, err)
        }
      }
    }, POLL_INTERVAL)
  }

  stopPolling() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
      this.pollInterval = null
    }
  }

  broadcastTaskUpdate(task: Task) {
    const windows = BrowserWindow.getAllWindows()
    for (const win of windows) {
      win.webContents.send('task:updated', task)
    }
  }

  async stopAgent(taskId: string): Promise<void> {
    const task = db.getTask(taskId)
    if (!task?.agent_id) return
    try {
      await this.client.stopAgent(task.agent_id)
      db.updateAgentStatus(taskId, task.agent_id, 'STOPPED')
    } catch {
      // Agent may already be stopped
    }
  }

  async deleteAgent(taskId: string): Promise<void> {
    const task = db.getTask(taskId)
    if (!task?.agent_id) return
    try {
      await this.client.deleteAgent(task.agent_id)
    } catch {
      // Agent may already be deleted
    }
  }

  async listAgents(limit?: number) {
    const cacheKey = `agents:${limit}`
    const cached = this.getCached<Awaited<ReturnType<typeof this.client.listAgents>>>(cacheKey)
    if (cached) return cached
    const result = await this.client.listAgents(limit)
    this.setCache(cacheKey, result)
    return result
  }

  async listRepositories() {
    const cacheKey = 'repositories'
    const cached = this.getCached<Awaited<ReturnType<typeof this.client.listRepositories>>>(cacheKey)
    if (cached) return cached
    const result = await this.client.listRepositories()
    this.setCache(cacheKey, result)
    return result
  }

  async listModels(): Promise<string[]> {
    const cacheKey = 'models'
    const cached = this.getCached<string[]>(cacheKey)
    if (cached) return cached
    try {
      const response = await this.client.listModels()
      this.setCache(cacheKey, response.models)
      return response.models
    } catch {
      return []
    }
  }

  setApiKey(apiKey: string) {
    this.client.setApiKey(apiKey)
    this.clearCache()
  }

  hasApiKey(): boolean {
    return this.client.hasApiKey()
  }

  async getMe() {
    const cacheKey = 'me'
    const cached = this.getCached<Awaited<ReturnType<typeof this.client.getMe>>>(cacheKey)
    if (cached) return cached
    const result = await this.client.getMe()
    this.setCache(cacheKey, result)
    return result
  }
}
