import { ipcMain, shell } from 'electron'
import * as db from './db'
import { AgentService } from './agent-service'
import type { TaskStatus, CreateTaskParams } from '../shared/types'

export function registerIpcHandlers(agentService: AgentService) {
  ipcMain.handle('project:list', () => {
    return db.listProjects()
  })

  ipcMain.handle('project:get', (_, id: string) => {
    return db.getProject(id)
  })

  ipcMain.handle('project:create', (_, name: string, repository: string, defaultBranch?: string, subfolder?: string) => {
    return db.createProject(name, repository, defaultBranch, subfolder)
  })

  ipcMain.handle('project:delete', (_, id: string) => {
    db.deleteProject(id)
  })

  ipcMain.handle('project:rename', (_, id: string, name: string) => {
    return db.renameProject(id, name)
  })

  ipcMain.handle('task:list', (_, projectId: string) => {
    return db.listTasks(projectId)
  })

  ipcMain.handle('task:get', (_, id: string) => {
    return db.getTask(id)
  })

  ipcMain.handle('task:create', (_, projectId: string, params: CreateTaskParams) => {
    return db.createTask(projectId, params.title, params.description, params.baseBranch, params.targetBranch, params.model)
  })

  ipcMain.handle('task:update', (_, id: string, updates: { title?: string; description?: string }) => {
    return db.updateTask(id, updates)
  })

  ipcMain.handle('task:move', async (_, id: string, newStatus: TaskStatus, newPosition: number) => {
    const task = db.getTask(id)
    if (!task) throw new Error('Task not found')
    
    const previousStatus = task.status
    const movedTask = db.moveTask(id, newStatus, newPosition)
    
    if (newStatus === 'build' && !task.agent_id) {
      try {
        const updated = await agentService.startBuild(id)
        agentService.broadcastTaskUpdate(updated)
        return updated
      } catch (err) {
        db.moveTask(id, previousStatus, task.position)
        throw err
      }
    }
    
    if ((newStatus === 'done' || newStatus === 'canceled' || newStatus === 'human') && task.agent_id) {
      await agentService.stopAgent(id)
    }
    
    return db.getTask(id)!
  })

  ipcMain.handle('task:delete', async (_, id: string) => {
    await agentService.deleteAgent(id)
    db.deleteTask(id)
  })

  ipcMain.handle('agent:start-build', async (_, taskId: string) => {
    const task = await agentService.startBuild(taskId)
    agentService.broadcastTaskUpdate(task)
    return task
  })

  ipcMain.handle('agent:send-followup', async (_, taskId: string, message: string) => {
    const task = await agentService.sendFollowup(taskId, message)
    agentService.broadcastTaskUpdate(task)
    return task
  })

  ipcMain.handle('agent:get-conversation', async (_, taskId: string) => {
    return agentService.getConversation(taskId)
  })

  ipcMain.handle('models:list', async () => {
    return agentService.listModels()
  })

  ipcMain.handle('shell:open-external', (_, url: string) => {
    return shell.openExternal(url)
  })

  ipcMain.handle('settings:has-api-key', () => {
    return agentService.hasApiKey()
  })

  ipcMain.handle('settings:set-api-key', (_, apiKey: string) => {
    agentService.setApiKey(apiKey)
  })

  ipcMain.handle('settings:get-me', async () => {
    return agentService.getMe()
  })

  ipcMain.handle('settings:list-agents', async (_, limit?: number) => {
    return agentService.listAgents(limit)
  })

  ipcMain.handle('settings:list-repositories', async () => {
    return agentService.listRepositories()
  })
}
