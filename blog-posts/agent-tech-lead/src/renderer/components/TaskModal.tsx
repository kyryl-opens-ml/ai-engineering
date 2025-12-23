import { useState, useEffect, useRef } from 'react'
import type { Task, AgentMessage } from '../../shared/types'

interface TaskModalProps {
  task: Task
  onClose: () => void
  onUpdate: (task: Task) => void
  onDelete: () => void
}

export function TaskModal({ task, onClose, onUpdate, onDelete }: TaskModalProps) {
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description ?? '')
  const [conversation, setConversation] = useState<AgentMessage[]>([])
  const [followup, setFollowup] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<NodeJS.Timeout | null>(null)
  const conversationEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setTitle(task.title)
    setDescription(task.description ?? '')
    if (task.agent_id) {
      loadConversation()
      pollRef.current = setInterval(loadConversation, 5000)
    } else {
      setConversation([])
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [task.id, task.agent_id])

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation])

  async function loadConversation() {
    const messages = await window.api.agent.getConversation(task.id)
    setConversation(messages)
  }

  async function saveTask() {
    if (title !== task.title || description !== (task.description ?? '')) {
      const updated = await window.api.task.update(task.id, { title, description })
      onUpdate(updated)
    }
  }

  async function handleDelete() {
    if (confirm('Delete this task?')) {
      await window.api.task.delete(task.id)
      onDelete()
    }
  }

  async function sendFollowup() {
    if (!followup.trim()) return
    setLoading(true)
    setError(null)
    try {
      const updated = await window.api.agent.sendFollowup(task.id, followup.trim())
      onUpdate(updated)
      setFollowup('')
      await loadConversation()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setLoading(false)
    }
  }

  function openInBrowser() {
    if (task.agent_url) {
      window.api.openExternal(task.agent_url)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendFollowup()
    }
  }

  const canSendFollowup = task.status === 'build' && task.agent_id
  const isReadOnly = ['done', 'canceled'].includes(task.status)
  const isBacklog = task.status === 'backlog'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal task-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <input
            type="text"
            className="task-title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={saveTask}
            readOnly={isReadOnly}
          />
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="error-banner">
              <span>{error}</span>
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}

          <div className="task-meta">
            <div className="task-status-badge" data-status={task.status}>
              {task.status.toUpperCase()}
            </div>
            {task.base_branch && (
              <span className="branch-badge">{task.base_branch}</span>
            )}
            {task.model && (
              <span className="model-badge">{task.model}</span>
            )}
          </div>

          <div className="field">
            <label>Description {isBacklog && '(agent prompt)'}</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={saveTask}
              placeholder="Describe what the agent should do..."
              rows={4}
              readOnly={isReadOnly}
            />
          </div>

          {task.agent_url && (
            <button className="view-cursor-btn" onClick={openInBrowser}>
              View in Cursor →
            </button>
          )}

          {(conversation.length > 0 || canSendFollowup) && (
            <div className="chat-section">
              <div className="chat-header">
                <label>Conversation</label>
                <span className="sync-note">Synced with Cursor</span>
              </div>
              <div className="chat-messages">
                {conversation.map((msg) => (
                  <div key={msg.id} className={`chat-message ${msg.type}`}>
                    <span className="chat-author">
                      {msg.type === 'user_message' ? 'You' : 'Agent'}
                    </span>
                    <p className="chat-content">{msg.text}</p>
                  </div>
                ))}
                <div ref={conversationEndRef} />
              </div>

              {canSendFollowup && (
                <div className="chat-input-wrapper">
                  <textarea
                    value={followup}
                    onChange={(e) => setFollowup(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Send a message... (Enter to send, Shift+Enter for newline)"
                    rows={2}
                    disabled={loading}
                  />
                  <button
                    className="btn-send"
                    onClick={sendFollowup}
                    disabled={loading || !followup.trim()}
                  >
                    {loading ? '...' : '↑'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-delete" onClick={handleDelete}>Delete</button>
        </div>
      </div>
    </div>
  )
}
