import { useState } from 'react'
import type { Project } from '../shared/types'
import { ProjectSelector } from './components/ProjectSelector'
import { KanbanBoard } from './components/KanbanBoard'
import { Settings } from './components/Settings'

export default function App() {
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <h1>Agent Tech Lead</h1>
          <button className="btn-settings" onClick={() => setShowSettings(true)}>⚙</button>
        </div>
        <ProjectSelector currentProject={currentProject} onSelectProject={setCurrentProject} />
      </aside>

      <main className="main-content">
        {currentProject ? (
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
