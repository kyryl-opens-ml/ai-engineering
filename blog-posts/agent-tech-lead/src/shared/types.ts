export type TaskStatus = 'backlog' | 'build' | 'review' | 'human' | 'done' | 'canceled'

export type AgentStatus = 'CREATING' | 'RUNNING' | 'FINISHED' | 'STOPPED' | 'ERROR'

export interface Project {
  id: string
  name: string
  repository: string
  default_branch: string | null
  subfolder: string | null
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
  base_branch: string | null
  target_branch: string | null
  model: string | null
  position: number
  created_at: string
  updated_at: string
}

export interface CreateTaskParams {
  title: string
  description?: string
  baseBranch?: string
  targetBranch?: string
  model?: string
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

