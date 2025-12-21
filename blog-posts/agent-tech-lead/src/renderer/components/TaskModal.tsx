import { useState, useEffect } from 'react'
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
  const [prompt, setPrompt] = useState('')
  const [baseBranch, setBaseBranch] = useState('')
  const [targetBranch, setTargetBranch] = useState('')
  const [followup, setFollowup] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    setTitle(task.title)
    setDescription(task.description ?? '')
    if (task.agent_id) {
      loadConversation()
    } else {
      setConversation([])
    }
  }, [task.id, task.agent_id])

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

  async function startBuild() {
    if (!prompt.trim()) return
    setLoading(true)
    setError(null)
    try {
      const updated = await window.api.agent.startBuild(
        task.id,
        prompt.trim(),
        baseBranch.trim() || undefined,
        targetBranch.trim() || undefined
      )
      onUpdate(updated)
      setPrompt('')
      setBaseBranch('')
      setTargetBranch('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start agent')
    } finally {
      setLoading(false)
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
      setError(err instanceof Error ? err.message : 'Failed to send follow-up')
    } finally {
      setLoading(false)
    }
  }

  async function moveToReview() {
    const updated = await window.api.agent.moveToReview(task.id)
    onUpdate(updated)
  }

  async function approve() {
    const updated = await window.api.agent.approve(task.id)
    onUpdate(updated)
  }

  async function cancel() {
    const updated = await window.api.agent.cancel(task.id)
    onUpdate(updated)
  }

  function openInBrowser() {
    if (task.agent_url) {
      window.api.openExternal(task.agent_url)
    }
  }

  function copyUrl() {
    if (task.agent_url) {
      navigator.clipboard.writeText(task.agent_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const canStartBuild = task.status === 'backlog'
  const canSendFollowup = task.status === 'build' && task.agent_id
  const canMoveToReview = task.status === 'build'
  const canApprove = task.status === 'review'
  const canCancel = !['done', 'canceled'].includes(task.status)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <input
            type="text"
            className="task-title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={saveTask}
          />
          <button className="btn-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {error && (
            <div className="error-banner">
              <span>{error}</span>
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}

          <div className="task-status-badge" data-status={task.status}>
            {task.status.toUpperCase()}
          </div>

          <div className="field">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              onBlur={saveTask}
              placeholder="Add a description..."
              rows={3}
            />
          </div>

          {task.agent_url && (
            <div className="agent-link-section">
              <span>Agent:</span>
              <button className="btn-link" onClick={openInBrowser}>
                View in Cursor →
              </button>
              <button className="btn-copy" onClick={copyUrl}>
                {copied ? '✓ Copied' : 'Copy URL'}
              </button>
              <span className="agent-status-text">{task.agent_status}</span>
            </div>
          )}

          {canStartBuild && (
            <div className="prompt-section">
              <label>Start Agent</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter prompt for agent..."
                rows={4}
              />
              <div className="branch-inputs">
                <input
                  type="text"
                  value={baseBranch}
                  onChange={(e) => setBaseBranch(e.target.value)}
                  placeholder="Base branch (default: main)"
                />
                <input
                  type="text"
                  value={targetBranch}
                  onChange={(e) => setTargetBranch(e.target.value)}
                  placeholder="Target branch name (optional)"
                />
              </div>
              <button
                className="btn-primary"
                onClick={startBuild}
                disabled={loading || !prompt.trim()}
              >
                {loading ? 'Starting...' : 'Start Agent'}
              </button>
            </div>
          )}

          {canSendFollowup && (
            <div className="followup-section">
              <label>Send Follow-up</label>
              <textarea
                value={followup}
                onChange={(e) => setFollowup(e.target.value)}
                placeholder="Enter follow-up message..."
                rows={3}
              />
              <button
                className="btn-secondary"
                onClick={sendFollowup}
                disabled={loading || !followup.trim()}
              >
                {loading ? 'Sending...' : 'Send Follow-up'}
              </button>
            </div>
          )}

          {conversation.length > 0 && (
            <div className="conversation-section">
              <label>Conversation</label>
              <div className="conversation-list">
                {conversation.map((msg) => (
                  <div key={msg.id} className={`message ${msg.type}`}>
                    <span className="message-author">
                      {msg.type === 'user_message' ? 'You' : 'Agent'}
                    </span>
                    <p className="message-content">{msg.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          {canMoveToReview && (
            <button className="btn-secondary" onClick={moveToReview}>
              Request Review
            </button>
          )}
          {canApprove && (
            <button className="btn-primary" onClick={approve}>
              Approve
            </button>
          )}
          {canCancel && (
            <button className="btn-danger" onClick={cancel}>
              Cancel Task
            </button>
          )}
          <button className="btn-delete" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
