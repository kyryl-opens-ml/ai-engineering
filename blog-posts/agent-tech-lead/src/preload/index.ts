import { contextBridge, ipcRenderer } from 'electron'
import type { Project, Task, TaskStatus, AgentMessage, CreateTaskParams } from '../shared/types'

const api = {
  project: {
    list: (): Promise<Project[]> => ipcRenderer.invoke('project:list'),
    get: (id: string): Promise<Project | undefined> => ipcRenderer.invoke('project:get', id),
    create: (name: string, repository: string, defaultBranch?: string, subfolder?: string): Promise<Project> =>
      ipcRenderer.invoke('project:create', name, repository, defaultBranch, subfolder),
    delete: (id: string): Promise<void> => ipcRenderer.invoke('project:delete', id)
  },

  task: {
    list: (projectId: string): Promise<Task[]> => ipcRenderer.invoke('task:list', projectId),
    get: (id: string): Promise<Task | undefined> => ipcRenderer.invoke('task:get', id),
    create: (projectId: string, params: CreateTaskParams): Promise<Task> =>
      ipcRenderer.invoke('task:create', projectId, params),
    update: (id: string, updates: { title?: string; description?: string }): Promise<Task> =>
      ipcRenderer.invoke('task:update', id, updates),
    move: (id: string, newStatus: TaskStatus, newPosition: number): Promise<Task> =>
      ipcRenderer.invoke('task:move', id, newStatus, newPosition),
    delete: (id: string): Promise<void> => ipcRenderer.invoke('task:delete', id)
  },

  agent: {
    startBuild: (taskId: string): Promise<Task> =>
      ipcRenderer.invoke('agent:start-build', taskId),
    sendFollowup: (taskId: string, message: string): Promise<Task> =>
      ipcRenderer.invoke('agent:send-followup', taskId, message),
    getConversation: (taskId: string): Promise<AgentMessage[]> =>
      ipcRenderer.invoke('agent:get-conversation', taskId)
  },

  openExternal: (url: string) => ipcRenderer.invoke('shell:open-external', url),

  models: {
    list: (): Promise<string[]> => ipcRenderer.invoke('models:list')
  },

  settings: {
    hasApiKey: (): Promise<boolean> => ipcRenderer.invoke('settings:has-api-key'),
    setApiKey: (apiKey: string): Promise<void> => ipcRenderer.invoke('settings:set-api-key', apiKey),
    getMe: (): Promise<{ apiKeyName: string; createdAt: string; userEmail: string }> => 
      ipcRenderer.invoke('settings:get-me'),
    listAgents: (limit?: number): Promise<{ agents: Array<{ id: string; name: string; status: string; createdAt: string }> }> =>
      ipcRenderer.invoke('settings:list-agents', limit),
    listRepositories: (): Promise<{ repositories: Array<{ owner: string; name: string; repository: string }> }> =>
      ipcRenderer.invoke('settings:list-repositories')
  },

  onTaskUpdated: (callback: (task: Task) => void) => {
    ipcRenderer.on('task:updated', (_, task) => callback(task))
    return () => ipcRenderer.removeAllListeners('task:updated')
  }
}

contextBridge.exposeInMainWorld('api', api)

export type Api = typeof api
