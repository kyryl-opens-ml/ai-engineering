export type TaskStatus = 'backlog' | 'build' | 'review' | 'done' | 'canceled'

export type AgentStatus = 'CREATING' | 'RUNNING' | 'FINISHED' | 'STOPPED' | 'ERROR'

export interface Project {
  id: string
  name: string
  repository: string
  created_at: string
}

export interface Task {
  id: string
  project_id: string
  title: string
  description: string | null
  status: TaskStatus
  agent_id: string | null
  agent_status: AgentStatus | null
  agent_url: string | null
  position: number
  created_at: string
  updated_at: string
}

export interface AgentMessage {
  id: string
  type: 'user_message' | 'assistant_message'
  text: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: TaskStatus
  position?: number
}

