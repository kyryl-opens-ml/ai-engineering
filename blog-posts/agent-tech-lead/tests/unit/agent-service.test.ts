import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('electron', () => ({
  BrowserWindow: {
    getAllWindows: () => []
  }
}))

const mockCreateAgent = vi.fn()
const mockGetAgent = vi.fn()
const mockAddFollowup = vi.fn()

vi.mock('../../src/main/cursor-client', () => ({
  CursorClient: vi.fn().mockImplementation(() => ({
    createAgent: mockCreateAgent,
    getAgent: mockGetAgent,
    addFollowup: mockAddFollowup
  }))
}))

const mockGetTask = vi.fn()
const mockGetProject = vi.fn()
const mockUpdateAgentStatus = vi.fn()
const mockMoveTask = vi.fn()
const mockAddComment = vi.fn()
const mockGetTasksWithRunningAgents = vi.fn()

vi.mock('../../src/main/db', () => ({
  getTask: (id: string) => mockGetTask(id),
  getProject: (id: string) => mockGetProject(id),
  updateAgentStatus: (...args: unknown[]) => mockUpdateAgentStatus(...args),
  moveTask: (...args: unknown[]) => mockMoveTask(...args),
  addComment: (...args: unknown[]) => mockAddComment(...args),
  getTasksWithRunningAgents: () => mockGetTasksWithRunningAgents()
}))

import { AgentService } from '../../src/main/agent-service'

describe('AgentService', () => {
  let service: AgentService

  beforeEach(() => {
    vi.clearAllMocks()
    service = new AgentService('test-api-key')
  })

  describe('START_DESIGN', () => {
    it('creates agent with user-provided prompt', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'backlog' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-1', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-1' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, design_agent_id: 'agent-1' })
      mockMoveTask.mockReturnValue({ ...task, status: 'design' })

      await service.startDesign('task-1', 'Plan this feature')

      expect(mockCreateAgent).toHaveBeenCalledWith({
        prompt: { text: 'Plan this feature' },
        source: { repository: 'https://github.com/test/repo' },
        target: { autoCreatePr: false }
      })
    })

    it('updates task with design_agent_id', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'backlog' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-1', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-1' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, design_agent_id: 'agent-1' })
      mockMoveTask.mockReturnValue({ ...task, status: 'design' })

      await service.startDesign('task-1', 'Plan this')

      expect(mockUpdateAgentStatus).toHaveBeenCalledWith(
        'task-1',
        'design',
        'agent-1',
        'CREATING',
        'https://cursor.com/agents?id=agent-1'
      )
    })

    it('moves task to design column', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'backlog' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-1', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-1' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, design_agent_id: 'agent-1' })
      mockMoveTask.mockReturnValue({ ...task, status: 'design' })

      await service.startDesign('task-1', 'Plan this')

      expect(mockMoveTask).toHaveBeenCalledWith('task-1', 'design', 0)
    })

    it('throws if task not in backlog', async () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'design' })

      await expect(service.startDesign('task-1', 'Plan this')).rejects.toThrow('Task must be in backlog to start design')
    })
  })

  describe('START_BUILD', () => {
    it('creates agent with user-provided prompt', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'design' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-2', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-2' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, build_agent_id: 'agent-2' })
      mockMoveTask.mockReturnValue({ ...task, status: 'build' })

      await service.startBuild('task-1', 'Implement this feature')

      expect(mockCreateAgent).toHaveBeenCalledWith({
        prompt: { text: 'Implement this feature' },
        source: { repository: 'https://github.com/test/repo' },
        target: { autoCreatePr: false }
      })
    })

    it('sets autoCreatePr to false', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'design' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-2', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-2' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, build_agent_id: 'agent-2' })
      mockMoveTask.mockReturnValue({ ...task, status: 'build' })

      await service.startBuild('task-1', 'Build')

      expect(mockCreateAgent).toHaveBeenCalledWith(
        expect.objectContaining({
          target: { autoCreatePr: false }
        })
      )
    })

    it('moves task to build column', async () => {
      const task = { id: 'task-1', project_id: 'proj-1', status: 'design' }
      const project = { id: 'proj-1', repository: 'https://github.com/test/repo' }
      const agent = { id: 'agent-2', status: 'CREATING', target: { url: 'https://cursor.com/agents?id=agent-2' } }

      mockGetTask.mockReturnValue(task)
      mockGetProject.mockReturnValue(project)
      mockCreateAgent.mockResolvedValue(agent)
      mockUpdateAgentStatus.mockReturnValue({ ...task, build_agent_id: 'agent-2' })
      mockMoveTask.mockReturnValue({ ...task, status: 'build' })

      await service.startBuild('task-1', 'Build')

      expect(mockMoveTask).toHaveBeenCalledWith('task-1', 'build', 0)
    })

    it('throws if task not in design', async () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'backlog' })

      await expect(service.startBuild('task-1', 'Build')).rejects.toThrow('Task must be in design to start build')
    })
  })

  describe('SEND_FOLLOWUP', () => {
    it('sends followup to design agent when in design', async () => {
      const task = { id: 'task-1', status: 'design', design_agent_id: 'agent-1' }
      mockGetTask.mockReturnValue(task)
      mockAddFollowup.mockResolvedValue({ id: 'agent-1' })
      mockUpdateAgentStatus.mockReturnValue(task)

      await service.sendFollowup('task-1', 'design', 'Add more details')

      expect(mockAddFollowup).toHaveBeenCalledWith('agent-1', { text: 'Add more details' })
    })

    it('sends followup to build agent when in build', async () => {
      const task = { id: 'task-1', status: 'build', build_agent_id: 'agent-2' }
      mockGetTask.mockReturnValue(task)
      mockAddFollowup.mockResolvedValue({ id: 'agent-2' })
      mockUpdateAgentStatus.mockReturnValue(task)

      await service.sendFollowup('task-1', 'build', 'Fix the bug')

      expect(mockAddFollowup).toHaveBeenCalledWith('agent-2', { text: 'Fix the bug' })
    })

    it('adds user comment to task', async () => {
      const task = { id: 'task-1', status: 'design', design_agent_id: 'agent-1' }
      mockGetTask.mockReturnValue(task)
      mockAddFollowup.mockResolvedValue({ id: 'agent-1' })
      mockUpdateAgentStatus.mockReturnValue(task)

      await service.sendFollowup('task-1', 'design', 'Comment text')

      expect(mockAddComment).toHaveBeenCalledWith('task-1', 'Comment text', 'user')
    })

    it('throws if no agent exists for phase', async () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'design', design_agent_id: null })

      await expect(service.sendFollowup('task-1', 'design', 'Message')).rejects.toThrow('No design agent found for task')
    })
  })

  describe('state transitions', () => {
    it('allows direct cancel from any state', () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'build' })
      mockMoveTask.mockReturnValue({ id: 'task-1', status: 'canceled' })

      const result = service.cancel('task-1')

      expect(mockMoveTask).toHaveBeenCalledWith('task-1', 'canceled', 0)
      expect(result.status).toBe('canceled')
    })

    it('move to review from build', () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'build' })
      mockMoveTask.mockReturnValue({ id: 'task-1', status: 'review' })

      service.moveToReview('task-1')

      expect(mockMoveTask).toHaveBeenCalledWith('task-1', 'review', 0)
    })

    it('approve from review', () => {
      mockGetTask.mockReturnValue({ id: 'task-1', status: 'review' })
      mockMoveTask.mockReturnValue({ id: 'task-1', status: 'done' })

      service.approve('task-1')

      expect(mockMoveTask).toHaveBeenCalledWith('task-1', 'done', 0)
    })
  })
})

