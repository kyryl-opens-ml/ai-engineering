import { useState, useEffect, useCallback } from 'react'
import { DragDropContext, type DropResult } from '@hello-pangea/dnd'
import type { Project, Task, TaskStatus, CreateTaskParams } from '../../shared/types'
import { Column } from './Column'
import { TaskModal } from './TaskModal'
import { AddTaskModal } from './AddTaskModal'

interface KanbanBoardProps {
  project: Project
}

const columns: { status: TaskStatus; title: string }[] = [
  { status: 'backlog', title: 'Backlog' },
  { status: 'build', title: 'Build' },
  { status: 'review', title: 'Review' },
  { status: 'human', title: 'Human Takeover' },
  { status: 'done', title: 'Done' },
  { status: 'canceled', title: 'Canceled' }
]

export function KanbanBoard({ project }: KanbanBoardProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [showAddTask, setShowAddTask] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadTasks = useCallback(async () => {
    const list = await window.api.task.list(project.id)
    setTasks(list)
  }, [project.id])

  useEffect(() => {
    loadTasks()

    const unsubscribe = window.api.onTaskUpdated((updatedTask) => {
      setTasks((prev) => prev.map((t) => (t.id === updatedTask.id ? updatedTask : t)))
      if (selectedTask?.id === updatedTask.id) {
        setSelectedTask(updatedTask)
      }
    })

    return unsubscribe
  }, [loadTasks, selectedTask?.id])

  async function handleDragEnd(result: DropResult) {
    if (!result.destination) return

    const sourceStatus = result.source.droppableId as TaskStatus
    const destStatus = result.destination.droppableId as TaskStatus
    const taskId = result.draggableId

    if (sourceStatus === destStatus && result.source.index === result.destination.index) {
      return
    }

    const task = tasks.find((t) => t.id === taskId)
    if (!task) return

    setTasks((prev) => {
      const updated = prev.map((t) => {
        if (t.id === taskId) {
          return { ...t, status: destStatus, position: result.destination!.index }
        }
        return t
      })
      return updated.sort((a, b) => {
        if (a.status !== b.status) return 0
        return a.position - b.position
      })
    })

    try {
      setError(null)
      await window.api.task.move(taskId, destStatus, result.destination.index)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to move task')
      setTasks((prev) => {
        const reverted = prev.map((t) => {
          if (t.id === taskId) {
            return { ...t, status: sourceStatus, position: result.source.index }
          }
          return t
        })
        return reverted.sort((a, b) => {
          if (a.status !== b.status) return 0
          return a.position - b.position
        })
      })
    }
  }

  async function createTask(params: CreateTaskParams) {
    const task = await window.api.task.create(project.id, params)
    setTasks([...tasks, task])
    setShowAddTask(false)
  }

  function getTasksForColumn(status: TaskStatus): Task[] {
    return tasks.filter((t) => t.status === status).sort((a, b) => a.position - b.position)
  }

  return (
    <div className="kanban-board">
      <div className="board-header">
        <h2>{project.name}</h2>
        <span className="repo-badge">{project.repository}</span>
        {project.subfolder && <span className="subfolder-badge">📁 {project.subfolder}</span>}
      </div>

      {error && (
        <div className="board-error">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="columns">
          {columns.map((col) => (
            <Column
              key={col.status}
              status={col.status}
              title={col.title}
              tasks={getTasksForColumn(col.status)}
              onTaskClick={setSelectedTask}
              onAddTask={col.status === 'backlog' ? () => setShowAddTask(true) : undefined}
            />
          ))}
        </div>
      </DragDropContext>

      {selectedTask && (
        <TaskModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onUpdate={(updated) => {
            setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
            setSelectedTask(updated)
          }}
          onDelete={() => {
            setTasks((prev) => prev.filter((t) => t.id !== selectedTask.id))
            setSelectedTask(null)
          }}
        />
      )}

      {showAddTask && (
        <AddTaskModal
          onClose={() => setShowAddTask(false)}
          onCreate={createTask}
        />
      )}
    </div>
  )
}

