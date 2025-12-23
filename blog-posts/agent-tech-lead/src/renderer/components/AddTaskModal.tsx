import { useState, useEffect } from 'react'

interface AddTaskModalProps {
  onClose: () => void
  onCreate: (params: {
    title: string
    description?: string
    baseBranch?: string
    targetBranch?: string
    model?: string
  }) => void
}

export function AddTaskModal({ onClose, onCreate }: AddTaskModalProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [baseBranch, setBaseBranch] = useState('main')
  const [targetBranch, setTargetBranch] = useState('')
  const [model, setModel] = useState('')
  const [models, setModels] = useState<string[]>([])

  useEffect(() => {
    window.api.models.list().then(setModels)
  }, [])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    onCreate({
      title: title.trim(),
      description: description.trim() || undefined,
      baseBranch: baseBranch.trim() || undefined,
      targetBranch: targetBranch.trim() || undefined,
      model: model || undefined
    })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal add-task-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>New Task</h2>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="field">
              <label>Name</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Task name..."
                autoFocus
              />
            </div>

            <div className="field">
              <label>Description (this will be the agent prompt)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what the agent should do..."
                rows={5}
              />
            </div>

            <div className="field-row">
              <div className="field">
                <label>Base Branch</label>
                <input
                  type="text"
                  value={baseBranch}
                  onChange={(e) => setBaseBranch(e.target.value)}
                  placeholder="main"
                />
              </div>

              <div className="field">
                <label>Target Branch (optional)</label>
                <input
                  type="text"
                  value={targetBranch}
                  onChange={(e) => setTargetBranch(e.target.value)}
                  placeholder="feature/..."
                />
              </div>
            </div>

            <div className="field">
              <label>Model</label>
              <select value={model} onChange={(e) => setModel(e.target.value)}>
                <option value="">Default</option>
                {models.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={!title.trim()}>
              Create Task
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

