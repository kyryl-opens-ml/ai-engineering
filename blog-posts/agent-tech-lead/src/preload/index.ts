import { contextBridge, ipcRenderer, shell } from 'electron'
import type { Project, Task, TaskStatus, AgentMessage } from '../shared/types'

const api = {
  project: {
    list: (): Promise<Project[]> => ipcRenderer.invoke('project:list'),
    get: (id: string): Promise<Project | undefined> => ipcRenderer.invoke('project:get', id),
    create: (name: string, repository: string): Promise<Project> =>
      ipcRenderer.invoke('project:create', name, repository),
    delete: (id: string): Promise<void> => ipcRenderer.invoke('project:delete', id)
  },

  task: {
    list: (projectId: string): Promise<Task[]> => ipcRenderer.invoke('task:list', projectId),
    get: (id: string): Promise<Task | undefined> => ipcRenderer.invoke('task:get', id),
    create: (projectId: string, title: string, description?: string): Promise<Task> =>
      ipcRenderer.invoke('task:create', projectId, title, description),
    update: (id: string, updates: { title?: string; description?: string }): Promise<Task> =>
      ipcRenderer.invoke('task:update', id, updates),
    move: (id: string, newStatus: TaskStatus, newPosition: number): Promise<Task> =>
      ipcRenderer.invoke('task:move', id, newStatus, newPosition),
    delete: (id: string): Promise<void> => ipcRenderer.invoke('task:delete', id)
  },

  agent: {
    startBuild: (taskId: string, prompt: string, baseBranch?: string, targetBranch?: string): Promise<Task> =>
      ipcRenderer.invoke('agent:start-build', taskId, prompt, baseBranch, targetBranch),
    sendFollowup: (taskId: string, message: string): Promise<Task> =>
      ipcRenderer.invoke('agent:send-followup', taskId, message),
    getConversation: (taskId: string): Promise<AgentMessage[]> =>
      ipcRenderer.invoke('agent:get-conversation', taskId),
    moveToReview: (taskId: string): Promise<Task> => ipcRenderer.invoke('agent:move-to-review', taskId),
    approve: (taskId: string): Promise<Task> => ipcRenderer.invoke('agent:approve', taskId),
    cancel: (taskId: string): Promise<Task> => ipcRenderer.invoke('agent:cancel', taskId)
  },

  openExternal: (url: string) => shell.openExternal(url),

  onTaskUpdated: (callback: (task: Task) => void) => {
    ipcRenderer.on('task:updated', (_, task) => callback(task))
    return () => ipcRenderer.removeAllListeners('task:updated')
  }
}

contextBridge.exposeInMainWorld('api', api)

export type Api = typeof api
