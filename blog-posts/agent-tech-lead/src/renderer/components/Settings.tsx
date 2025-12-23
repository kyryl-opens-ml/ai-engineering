import { useState, useEffect } from 'react'
import type { Project } from '../../shared/types'

interface Agent {
  id: string
  name: string
  status: string
  createdAt: string
}

interface Repository {
  owner: string
  name: string
  repository: string
}

interface SettingsProps {
  onClose: () => void
}

export function Settings({ onClose }: SettingsProps) {
  const [apiKey, setApiKey] = useState('')
  const [hasKey, setHasKey] = useState(false)
  const [userEmail, setUserEmail] = useState('')
  const [projects, setProjects] = useState<Project[]>([])
  const [models, setModels] = useState<string[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'api' | 'projects' | 'models' | 'agents' | 'repos'>('api')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [hasApiKey, projectList] = await Promise.all([
        window.api.settings.hasApiKey(),
        window.api.project.list()
      ])
      setHasKey(hasApiKey)
      setProjects(projectList)

      if (hasApiKey) {
        await loadApiData()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    }
    setLoading(false)
  }

  async function loadApiData() {
    try {
      const [me, modelList, agentList, repoList] = await Promise.all([
        window.api.settings.getMe(),
        window.api.models.list(),
        window.api.settings.listAgents(50),
        window.api.settings.listRepositories()
      ])
      setUserEmail(me.userEmail)
      setModels(modelList)
      setAgents(agentList.agents)
      setRepositories(repoList.repositories)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load API data')
    }
  }

  async function saveApiKey() {
    if (!apiKey.trim()) return
    try {
      await window.api.settings.setApiKey(apiKey.trim())
      setHasKey(true)
      setApiKey('')
      await loadApiData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set API key')
    }
  }

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal settings-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Settings</h2>
            <button className="btn-close" onClick={onClose}>✕</button>
          </div>
          <div className="modal-body">
            <p>Loading...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="settings-tabs">
          <button className={activeTab === 'api' ? 'active' : ''} onClick={() => setActiveTab('api')}>
            API Key
          </button>
          <button className={activeTab === 'projects' ? 'active' : ''} onClick={() => setActiveTab('projects')}>
            Projects ({projects.length})
          </button>
          <button className={activeTab === 'models' ? 'active' : ''} onClick={() => setActiveTab('models')}>
            Models ({models.length})
          </button>
          <button className={activeTab === 'agents' ? 'active' : ''} onClick={() => setActiveTab('agents')}>
            Agents ({agents.length})
          </button>
          <button className={activeTab === 'repos' ? 'active' : ''} onClick={() => setActiveTab('repos')}>
            Repos ({repositories.length})
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="modal-body">
          {activeTab === 'api' && (
            <div className="settings-section">
              <h3>Cursor API Key</h3>
              {hasKey ? (
                <div className="api-status connected">
                  <span className="status-dot">●</span>
                  <span>Connected as {userEmail}</span>
                </div>
              ) : (
                <div className="api-status disconnected">
                  <span className="status-dot">●</span>
                  <span>Not connected</span>
                </div>
              )}
              <div className="api-key-form">
                <input
                  type="password"
                  placeholder="Enter Cursor API key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
                <button className="btn-primary" onClick={saveApiKey}>
                  {hasKey ? 'Update Key' : 'Save Key'}
                </button>
              </div>
              <p className="hint">Get your API key from cursor.com/settings</p>
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="settings-section">
              <h3>Projects</h3>
              {projects.length === 0 ? (
                <p className="empty-list">No projects yet</p>
              ) : (
                <div className="settings-list">
                  {projects.map((p) => (
                    <div key={p.id} className="settings-list-item">
                      <div className="item-main">
                        <span className="item-name">{p.name}</span>
                        <span className="item-detail">{p.repository}</span>
                        {p.subfolder && <span className="item-subfolder">📁 {p.subfolder}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'models' && (
            <div className="settings-section">
              <h3>Available Models</h3>
              {!hasKey ? (
                <p className="empty-list">Set API key to see models</p>
              ) : models.length === 0 ? (
                <p className="empty-list">No models available</p>
              ) : (
                <div className="settings-list">
                  {models.map((m) => (
                    <div key={m} className="settings-list-item">
                      <span className="item-name">{m}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="settings-section">
              <h3>Recent Agents</h3>
              {!hasKey ? (
                <p className="empty-list">Set API key to see agents</p>
              ) : agents.length === 0 ? (
                <p className="empty-list">No agents found</p>
              ) : (
                <div className="settings-list">
                  {agents.map((a) => (
                    <div key={a.id} className="settings-list-item">
                      <div className="item-main">
                        <span className="item-name">{a.name || a.id.slice(0, 8)}</span>
                        <span className={`agent-status-badge ${a.status.toLowerCase()}`}>{a.status}</span>
                      </div>
                      <span className="item-detail">{new Date(a.createdAt).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'repos' && (
            <div className="settings-section">
              <h3>Connected Repositories</h3>
              {!hasKey ? (
                <p className="empty-list">Set API key to see repositories</p>
              ) : repositories.length === 0 ? (
                <p className="empty-list">No repositories connected</p>
              ) : (
                <div className="settings-list">
                  {repositories.map((r) => (
                    <div key={r.repository} className="settings-list-item">
                      <div className="item-main">
                        <span className="item-name">{r.owner}/{r.name}</span>
                      </div>
                      <span className="item-detail">{r.repository}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

