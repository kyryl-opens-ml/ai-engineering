import { ipcMain } from 'electron'
import * as db from './db'
import { AgentService } from './agent-service'
import type { TaskStatus } from '../shared/types'

export function registerIpcHandlers(agentService: AgentService) {
  ipcMain.handle('project:list', () => {
    return db.listProjects()
  })

  ipcMain.handle('project:get', (_, id: string) => {
    return db.getProject(id)
  })

  ipcMain.handle('project:create', (_, name: string, repository: string) => {
    return db.createProject(name, repository)
  })

  ipcMain.handle('project:delete', (_, id: string) => {
    db.deleteProject(id)
  })

  ipcMain.handle('task:list', (_, projectId: string) => {
    return db.listTasks(projectId)
  })

  ipcMain.handle('task:get', (_, id: string) => {
    return db.getTask(id)
  })

  ipcMain.handle('task:create', (_, projectId: string, title: string, description?: string) => {
    return db.createTask(projectId, title, description)
  })

  ipcMain.handle('task:update', (_, id: string, updates: { title?: string; description?: string }) => {
    return db.updateTask(id, updates)
  })

  ipcMain.handle('task:move', (_, id: string, newStatus: TaskStatus, newPosition: number) => {
    return db.moveTask(id, newStatus, newPosition)
  })

  ipcMain.handle('task:delete', (_, id: string) => {
    db.deleteTask(id)
  })

  ipcMain.handle('agent:start-build', async (_, taskId: string, prompt: string, baseBranch?: string, targetBranch?: string) => {
    const task = await agentService.startBuild(taskId, prompt, baseBranch, targetBranch)
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

  ipcMain.handle('agent:move-to-review', (_, taskId: string) => {
    const task = agentService.moveToReview(taskId)
    agentService.broadcastTaskUpdate(task)
    return task
  })

  ipcMain.handle('agent:approve', (_, taskId: string) => {
    const task = agentService.approve(taskId)
    agentService.broadcastTaskUpdate(task)
    return task
  })

  ipcMain.handle('agent:cancel', (_, taskId: string) => {
    const task = agentService.cancel(taskId)
    agentService.broadcastTaskUpdate(task)
    return task
  })
}
