import { describe, it, expect, beforeEach, vi, beforeAll } from 'vitest'
import Database from 'better-sqlite3'
import { randomUUID } from 'node:crypto'

vi.mock('electron', () => ({
  app: {
    getPath: () => '/tmp'
  }
}))

describe('Database', () => {
  let db: Database.Database

  beforeAll(() => {
    db = new Database(':memory:')
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
        design_agent_id TEXT,
        design_agent_status TEXT,
        design_agent_url TEXT,
        build_agent_id TEXT,
        build_agent_status TEXT,
        build_agent_url TEXT,
        position INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
      );
    `)
  })

  beforeEach(() => {
    db.exec('DELETE FROM comments')
    db.exec('DELETE FROM tasks')
    db.exec('DELETE FROM projects')
  })

  function createProject(name: string, repository: string) {
    const id = randomUUID()
    db.prepare('INSERT INTO projects (id, name, repository) VALUES (?, ?, ?)').run(id, name, repository)
    return db.prepare('SELECT * FROM projects WHERE id = ?').get(id) as { id: string; name: string; repository: string }
  }

  function getProject(id: string) {
    return db.prepare('SELECT * FROM projects WHERE id = ?').get(id)
  }

  function listProjects() {
    return db.prepare('SELECT * FROM projects ORDER BY created_at DESC').all()
  }

  function deleteProject(id: string) {
    db.prepare('DELETE FROM projects WHERE id = ?').run(id)
  }

  function createTask(projectId: string, title: string, description?: string) {
    const id = randomUUID()
    const maxPos = db
      .prepare('SELECT COALESCE(MAX(position), -1) as max FROM tasks WHERE project_id = ? AND status = ?')
      .get(projectId, 'backlog') as { max: number }
    db.prepare('INSERT INTO tasks (id, project_id, title, description, status, position) VALUES (?, ?, ?, ?, ?, ?)')
      .run(id, projectId, title, description ?? null, 'backlog', maxPos.max + 1)
    return db.prepare('SELECT * FROM tasks WHERE id = ?').get(id) as { id: string; title: string; description: string | null; status: string; position: number }
  }

  function updateTask(id: string, updates: { title?: string; description?: string }) {
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
    if (fields.length > 0) {
      fields.push('updated_at = CURRENT_TIMESTAMP')
      values.push(id)
      db.prepare(`UPDATE tasks SET ${fields.join(', ')} WHERE id = ?`).run(...values)
    }
    return db.prepare('SELECT * FROM tasks WHERE id = ?').get(id)
  }

  function moveTask(id: string, newStatus: string, newPosition: number) {
    db.prepare('UPDATE tasks SET status = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(newStatus, newPosition, id)
    return db.prepare('SELECT * FROM tasks WHERE id = ?').get(id) as { id: string; status: string; position: number }
  }

  function listTasks(projectId: string) {
    return db.prepare('SELECT * FROM tasks WHERE project_id = ? ORDER BY status, position').all(projectId)
  }

  function updateAgentStatus(taskId: string, phase: string, agentId: string, status: string, url?: string) {
    const prefix = phase === 'design' ? 'design' : 'build'
    db.prepare(
      `UPDATE tasks SET ${prefix}_agent_id = ?, ${prefix}_agent_status = ?, ${prefix}_agent_url = COALESCE(?, ${prefix}_agent_url), updated_at = CURRENT_TIMESTAMP WHERE id = ?`
    ).run(agentId, status, url ?? null, taskId)
    return db.prepare('SELECT * FROM tasks WHERE id = ?').get(taskId) as { design_agent_id: string; design_agent_status: string; design_agent_url: string; build_agent_id: string; build_agent_status: string; build_agent_url: string }
  }

  function getTasksWithRunningAgents() {
    return db.prepare(
      `SELECT * FROM tasks WHERE 
       (design_agent_status IN ('CREATING', 'RUNNING')) OR 
       (build_agent_status IN ('CREATING', 'RUNNING'))`
    ).all() as { design_agent_status: string }[]
  }

  function addComment(taskId: string, content: string, author: string) {
    const id = randomUUID()
    db.prepare('INSERT INTO comments (id, task_id, content, author) VALUES (?, ?, ?, ?)').run(id, taskId, content, author)
    return db.prepare('SELECT * FROM comments WHERE id = ?').get(id) as { content: string; author: string }
  }

  function listComments(taskId: string) {
    return db.prepare('SELECT * FROM comments WHERE task_id = ? ORDER BY created_at ASC').all(taskId) as { content: string }[]
  }

  describe('projects', () => {
    it('creates and retrieves a project', () => {
      const project = createProject('Test Project', 'https://github.com/test/repo')
      expect(project.name).toBe('Test Project')
      expect(project.repository).toBe('https://github.com/test/repo')

      const retrieved = getProject(project.id)
      expect(retrieved).toEqual(project)
    })

    it('lists all projects', () => {
      createProject('Project 1', 'https://github.com/test/repo1')
      createProject('Project 2', 'https://github.com/test/repo2')

      const projects = listProjects()
      expect(projects).toHaveLength(2)
    })

    it('deletes project', () => {
      const project = createProject('To Delete', 'https://github.com/test/repo')
      deleteProject(project.id)

      const retrieved = getProject(project.id)
      expect(retrieved).toBeUndefined()
    })
  })

  describe('tasks', () => {
    it('creates task in backlog', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task', 'Description')

      expect(task.title).toBe('Test Task')
      expect(task.description).toBe('Description')
      expect(task.status).toBe('backlog')
      expect(task.position).toBe(0)
    })

    it('updates task description', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      const updated = updateTask(task.id, { description: 'New description' }) as { description: string }
      expect(updated.description).toBe('New description')
    })

    it('moves task to new column', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      const moved = moveTask(task.id, 'design', 0)
      expect(moved.status).toBe('design')
      expect(moved.position).toBe(0)
    })

    it('retrieves tasks by project', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      createTask(project.id, 'Task 1')
      createTask(project.id, 'Task 2')

      const tasks = listTasks(project.id)
      expect(tasks).toHaveLength(2)
    })

    it('retrieves tasks with running agents', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')
      updateAgentStatus(task.id, 'design', 'agent-123', 'RUNNING', 'https://cursor.com/agents?id=agent-123')

      const running = getTasksWithRunningAgents()
      expect(running).toHaveLength(1)
      expect(running[0].design_agent_status).toBe('RUNNING')
    })
  })

  describe('comments', () => {
    it('adds user comment to task', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      const comment = addComment(task.id, 'Test comment', 'user')
      expect(comment.content).toBe('Test comment')
      expect(comment.author).toBe('user')
    })

    it('retrieves comments for task in order', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      addComment(task.id, 'First', 'user')
      addComment(task.id, 'Second', 'agent')

      const comments = listComments(task.id)
      expect(comments).toHaveLength(2)
      expect(comments[0].content).toBe('First')
      expect(comments[1].content).toBe('Second')
    })
  })

  describe('agent status updates', () => {
    it('updates design agent status', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      const updated = updateAgentStatus(task.id, 'design', 'agent-123', 'RUNNING', 'https://cursor.com/agents?id=agent-123')
      expect(updated.design_agent_id).toBe('agent-123')
      expect(updated.design_agent_status).toBe('RUNNING')
      expect(updated.design_agent_url).toBe('https://cursor.com/agents?id=agent-123')
    })

    it('updates build agent status', () => {
      const project = createProject('Test', 'https://github.com/test/repo')
      const task = createTask(project.id, 'Test Task')

      const updated = updateAgentStatus(task.id, 'build', 'agent-456', 'CREATING', 'https://cursor.com/agents?id=agent-456')
      expect(updated.build_agent_id).toBe('agent-456')
      expect(updated.build_agent_status).toBe('CREATING')
      expect(updated.build_agent_url).toBe('https://cursor.com/agents?id=agent-456')
    })
  })
})
