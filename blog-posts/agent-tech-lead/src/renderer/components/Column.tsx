import { Droppable } from '@hello-pangea/dnd'
import type { Task, TaskStatus } from '../../shared/types'
import { TaskCard } from './TaskCard'

interface ColumnProps {
  status: TaskStatus
  title: string
  tasks: Task[]
  onTaskClick: (task: Task) => void
  onAddTask?: () => void
}

const statusColors: Record<TaskStatus, string> = {
  backlog: '#6b7280',
  build: '#f59e0b',
  review: '#3b82f6',
  done: '#10b981',
  canceled: '#ef4444'
}

export function Column({ status, title, tasks, onTaskClick, onAddTask }: ColumnProps) {
  return (
    <div className="column" data-status={status}>
      <div className="column-header" style={{ borderBottomColor: statusColors[status] }}>
        <h3>{title}</h3>
        <span className="task-count">{tasks.length}</span>
        {onAddTask && (
          <button className="btn-add-task" onClick={onAddTask}>
            +
          </button>
        )}
      </div>

      <Droppable droppableId={status}>
        {(provided, snapshot) => (
          <div
            className={`column-content ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
            ref={provided.innerRef}
            {...provided.droppableProps}
          >
            {tasks.map((task, index) => (
              <TaskCard key={task.id} task={task} index={index} onClick={() => onTaskClick(task)} />
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}

