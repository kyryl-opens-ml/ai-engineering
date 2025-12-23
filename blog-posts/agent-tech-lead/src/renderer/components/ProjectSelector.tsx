import { useState, useEffect } from 'react'
import type { Project } from '../../shared/types'

declare global {
  interface Window {
    api: typeof import('../../preload/index').Api
  }
}

interface ParsedRepo {
  repository: string
  defaultBranch?: string
  subfolder?: string
}

function parseGitHubUrl(url: string): ParsedRepo {
  const trimmed = url.trim()
  const match = trimmed.match(/^(https:\/\/github\.com\/[^\/]+\/[^\/]+)\/tree\/([^\/]+)\/(.+)$/)
  if (match) {
    return {
      repository: match[1],
      defaultBranch: match[2],
      subfolder: match[3]
    }
  }
  return { repository: trimmed }
}

interface ProjectSelectorProps {
  currentProject: Project | null
  onSelectProject: (project: Project) => void
}

export function ProjectSelector({ currentProject, onSelectProject }: ProjectSelectorProps) {
  const [projects, setProjects] = useState<Project[]>([])
  const [showNew, setShowNew] = useState(false)
  const [name, setName] = useState('')
  const [repository, setRepository] = useState('')
  const [loading, setLoading] = useState(true)
  const [parsedRepo, setParsedRepo] = useState<ParsedRepo>({ repository: '' })

  useEffect(() => {
    loadProjects()
  }, [])

  useEffect(() => {
    setParsedRepo(parseGitHubUrl(repository))
  }, [repository])

  async function loadProjects() {
    setLoading(true)
    const list = await window.api.project.list()
    setProjects(list)
    setLoading(false)
  }

  async function createProject() {
    if (!name.trim() || !repository.trim()) return
    const parsed = parseGitHubUrl(repository)
    const project = await window.api.project.create(
      name.trim(),
      parsed.repository,
      parsed.defaultBranch,
      parsed.subfolder
    )
    setProjects([project, ...projects])
    setName('')
    setRepository('')
    setParsedRepo({ repository: '' })
    setShowNew(false)
    onSelectProject(project)
  }

  async function deleteProject(id: string) {
    await window.api.project.delete(id)
    setProjects(projects.filter((p) => p.id !== id))
    if (currentProject?.id === id) {
      onSelectProject(projects.find((p) => p.id !== id) ?? null!)
    }
  }

  if (loading) {
    return <div className="project-selector loading">Loading projects...</div>
  }

  return (
    <div className="project-selector">
      <div className="project-header">
        <h2>Projects</h2>
        <button className="btn-new" onClick={() => setShowNew(!showNew)}>
          {showNew ? '✕' : '+ New'}
        </button>
      </div>

      {showNew && (
        <div className="new-project-form">
          <input
            type="text"
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Repository URL (e.g. https://github.com/org/repo)"
            value={repository}
            onChange={(e) => setRepository(e.target.value)}
          />
          {parsedRepo.subfolder && (
            <div className="monorepo-info">
              <span className="monorepo-label">Monorepo detected:</span>
              <span className="monorepo-detail">Branch: {parsedRepo.defaultBranch}</span>
              <span className="monorepo-detail">Subfolder: {parsedRepo.subfolder}</span>
            </div>
          )}
          <button className="btn-create" onClick={createProject}>
            Create Project
          </button>
        </div>
      )}

      <div className="project-list">
        {projects.length === 0 ? (
          <p className="empty">No projects yet. Create one to get started!</p>
        ) : (
          projects.map((project) => (
            <div
              key={project.id}
              className={`project-item ${currentProject?.id === project.id ? 'active' : ''}`}
              onClick={() => onSelectProject(project)}
            >
              <div className="project-info">
                <span className="project-name">{project.name}</span>
                <span className="project-repo">{project.repository}</span>
                {project.subfolder && (
                  <span className="project-subfolder">📁 {project.subfolder}</span>
                )}
              </div>
              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation()
                  deleteProject(project.id)
                }}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

