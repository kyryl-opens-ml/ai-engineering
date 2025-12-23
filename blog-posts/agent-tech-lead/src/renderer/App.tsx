import { useState } from 'react'
import type { Project } from '../shared/types'
import { ProjectSelector } from './components/ProjectSelector'
import { KanbanBoard } from './components/KanbanBoard'
import { Settings } from './components/Settings'
import { GameView } from './components/GameView'

type ViewMode = 'kanban' | 'game'

export default function App() {
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('kanban')

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <h1>Agent Tech Lead</h1>
          <button className="btn-settings" onClick={() => setShowSettings(true)}>⚙</button>
        </div>

        <div className="view-toggle">
          <button
            className={viewMode === 'kanban' ? 'active' : ''}
            onClick={() => setViewMode('kanban')}
          >
            📋 Kanban
          </button>
          <button
            className={viewMode === 'game' ? 'active' : ''}
            onClick={() => setViewMode('game')}
          >
            🎮 Game
          </button>
        </div>

        {viewMode === 'kanban' && (
          <ProjectSelector currentProject={currentProject} onSelectProject={setCurrentProject} />
        )}
      </aside>

      <main className="main-content">
        {viewMode === 'game' ? (
          <GameView />
        ) : currentProject ? (
          <KanbanBoard project={currentProject} />
        ) : (
          <div className="empty-state">
            <h2>Welcome!</h2>
            <p>Select or create a project to get started.</p>
          </div>
        )}
      </main>

      {showSettings && <Settings onClose={() => setShowSettings(false)} />}
    </div>
  )
}
