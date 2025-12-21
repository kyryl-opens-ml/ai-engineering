import Database from 'better-sqlite3'
import { app } from 'electron'
import path from 'node:path'
import { randomUUID } from 'node:crypto'
import type { Project, Task, TaskStatus, AgentStatus, TaskUpdate } from '../shared/types'

let db: Database.Database

export function initDb(dbPath?: string): Database.Database {
  const defaultPath = path.join(app.getPath('userData'), 'agent-kanban.db')
  db = new Database(dbPath ?? defaultPath)
  db.pragma('journal_mode = WAL')

  db.exec(`
    CREATE TABLE IF NOT EXISTS projects (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      repository TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      status TEXT NOT NULL DEFAULT 'backlog',
      agent_id TEXT,
      agent_status TEXT,
      agent_url TEXT,
      position INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
  `)

  return db
}

export function getDb(): Database.Database {
  if (!db) throw new Error('Database not initialized')
  return db
}

export function listProjects(): Project[] {
  return getDb().prepare('SELECT * FROM projects ORDER BY created_at DESC').all() as Project[]
}

export function getProject(id: string): Project | undefined {
  return getDb().prepare('SELECT * FROM projects WHERE id = ?').get(id) as Project | undefined
}

export function createProject(name: string, repository: string): Project {
  const id = randomUUID()
  getDb().prepare('INSERT INTO projects (id, name, repository) VALUES (?, ?, ?)').run(id, name, repository)
  return getProject(id)!
}

export function deleteProject(id: string): void {
  getDb().prepare('DELETE FROM projects WHERE id = ?').run(id)
}

export function listTasks(projectId: string): Task[] {
  return getDb()
    .prepare('SELECT * FROM tasks WHERE project_id = ? ORDER BY status, position')
    .all(projectId) as Task[]
}

export function getTask(id: string): Task | undefined {
  return getDb().prepare('SELECT * FROM tasks WHERE id = ?').get(id) as Task | undefined
}

export function createTask(projectId: string, title: string, description?: string): Task {
  const id = randomUUID()
  const maxPos = getDb()
    .prepare('SELECT COALESCE(MAX(position), -1) as max FROM tasks WHERE project_id = ? AND status = ?')
    .get(projectId, 'backlog') as { max: number }

  getDb()
    .prepare(
      'INSERT INTO tasks (id, project_id, title, description, status, position) VALUES (?, ?, ?, ?, ?, ?)'
    )
    .run(id, projectId, title, description ?? null, 'backlog', maxPos.max + 1)

  return getTask(id)!
}

export function updateTask(id: string, updates: TaskUpdate): Task {
  const task = getTask(id)
  if (!task) throw new Error('Task not found')

  const fields: string[] = []
  const values: unknown[] = []

  if (updates.title !== undefined) {
    fields.push('title = ?')
    values.push(updates.title)
  }
  if (updates.description !== undefined) {
    fields.push('description = ?')
    values.push(updates.description)
  }
  if (updates.status !== undefined) {
    fields.push('status = ?')
    values.push(updates.status)
  }
  if (updates.position !== undefined) {
    fields.push('position = ?')
    values.push(updates.position)
  }

  if (fields.length > 0) {
    fields.push('updated_at = CURRENT_TIMESTAMP')
    values.push(id)
    getDb().prepare(`UPDATE tasks SET ${fields.join(', ')} WHERE id = ?`).run(...values)
  }

  return getTask(id)!
}

export function moveTask(id: string, newStatus: TaskStatus, newPosition: number): Task {
  const task = getTask(id)
  if (!task) throw new Error('Task not found')

  const transaction = getDb().transaction(() => {
    if (task.status !== newStatus) {
      getDb()
        .prepare('UPDATE tasks SET position = position - 1 WHERE project_id = ? AND status = ? AND position > ?')
        .run(task.project_id, task.status, task.position)
    }

    getDb()
      .prepare('UPDATE tasks SET position = position + 1 WHERE project_id = ? AND status = ? AND position >= ?')
      .run(task.project_id, newStatus, newPosition)

    getDb()
      .prepare('UPDATE tasks SET status = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
      .run(newStatus, newPosition, id)
  })

  transaction()
  return getTask(id)!
}

export function deleteTask(id: string): void {
  const task = getTask(id)
  if (task) {
    getDb()
      .prepare('UPDATE tasks SET position = position - 1 WHERE project_id = ? AND status = ? AND position > ?')
      .run(task.project_id, task.status, task.position)
  }
  getDb().prepare('DELETE FROM tasks WHERE id = ?').run(id)
}

export function updateAgentStatus(
  taskId: string,
  agentId: string,
  status: AgentStatus,
  url?: string
): Task {
  getDb()
    .prepare(
      `UPDATE tasks SET agent_id = ?, agent_status = ?, agent_url = COALESCE(?, agent_url), updated_at = CURRENT_TIMESTAMP WHERE id = ?`
    )
    .run(agentId, status, url ?? null, taskId)
  return getTask(taskId)!
}

export function getTasksWithRunningAgents(): Task[] {
  return getDb()
    .prepare(
      `SELECT * FROM tasks WHERE agent_status IN ('CREATING', 'RUNNING')`
    )
    .all() as Task[]
}

