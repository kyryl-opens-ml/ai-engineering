import { Draggable } from '@hello-pangea/dnd'
import type { Task, AgentStatus } from '../../shared/types'

interface TaskCardProps {
  task: Task
  index: number
  onClick: () => void
}

const statusColors: Record<AgentStatus, string> = {
  CREATING: '#fbbf24',
  RUNNING: '#3b82f6',
  FINISHED: '#10b981',
  STOPPED: '#6b7280',
  ERROR: '#ef4444'
}

export function TaskCard({ task, index, onClick }: TaskCardProps) {
  return (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div
          className={`task-card ${snapshot.isDragging ? 'dragging' : ''}`}
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={onClick}
        >
          <h4 className="task-title">{task.title}</h4>

          {task.description && <p className="task-description">{task.description}</p>}

          {task.agent_status && (
            <div className="agent-badge" style={{ backgroundColor: statusColors[task.agent_status] }}>
              <span className="agent-status">{task.agent_status}</span>
            </div>
          )}
        </div>
      )}
    </Draggable>
  )
}
