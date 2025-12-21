import { BrowserWindow } from 'electron'
import { CursorClient } from './cursor-client'
import * as db from './db'
import type { Task, AgentStatus, AgentMessage } from '../shared/types'

const POLL_INTERVAL = 10_000

export class AgentService {
  private client: CursorClient
  private pollInterval: NodeJS.Timeout | null = null

  constructor(apiKey?: string) {
    this.client = new CursorClient(apiKey)
  }

  async startBuild(taskId: string, prompt: string, baseBranch?: string, targetBranch?: string): Promise<Task> {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (task.status !== 'backlog') throw new Error('Task must be in backlog to start build')

    const project = db.getProject(task.project_id)
    if (!project) throw new Error('Project not found')

    const agent = await this.client.createAgent({
      prompt: { text: prompt },
      source: {
        repository: project.repository,
        ...(baseBranch && { ref: baseBranch })
      },
      target: {
        autoCreatePr: false,
        ...(targetBranch && { branchName: targetBranch })
      }
    })

    db.updateAgentStatus(taskId, agent.id, agent.status as AgentStatus, agent.target.url)
    db.moveTask(taskId, 'build', 0)

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

  moveToReview(taskId: string): Task {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (task.status !== 'build') throw new Error('Task must be in build to move to review')

    return db.moveTask(taskId, 'review', 0)
  }

  approve(taskId: string): Task {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')
    if (task.status !== 'review') throw new Error('Task must be in review to approve')

    return db.moveTask(taskId, 'done', 0)
  }

  cancel(taskId: string): Task {
    const task = db.getTask(taskId)
    if (!task) throw new Error('Task not found')

    return db.moveTask(taskId, 'canceled', 0)
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
}
