import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { Canvas, useThree, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { Project, Task } from '../../shared/types'
import { City } from './game/City'
import { Agent } from './game/Agent'

interface ProjectWithTasks {
  project: Project
  tasks: Task[]
}

function CameraControls() {
  const { camera, gl } = useThree()
  const isDragging = useRef(false)
  const previousMouse = useRef({ x: 0, y: 0 })
  const targetPosition = useRef(new THREE.Vector3(0, 0, 0))
  const targetZoom = useRef(50)

  useEffect(() => {
    const canvas = gl.domElement

    const handleMouseDown = (e: MouseEvent) => {
      if (e.button === 0) {
        isDragging.current = true
        previousMouse.current = { x: e.clientX, y: e.clientY }
        canvas.style.cursor = 'grabbing'
      }
    }

    const handleMouseUp = () => {
      isDragging.current = false
      canvas.style.cursor = 'grab'
    }

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return

      const deltaX = e.clientX - previousMouse.current.x
      const deltaY = e.clientY - previousMouse.current.y
      previousMouse.current = { x: e.clientX, y: e.clientY }

      const panSpeed = 0.02 / (camera as THREE.OrthographicCamera).zoom * 80
      targetPosition.current.x -= deltaX * panSpeed
      targetPosition.current.z -= deltaY * panSpeed
    }

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault()
      const zoomSpeed = 0.1
      const delta = e.deltaY > 0 ? 1 - zoomSpeed : 1 + zoomSpeed
      targetZoom.current = Math.max(20, Math.min(200, targetZoom.current * delta))
    }

    canvas.style.cursor = 'grab'
    canvas.addEventListener('mousedown', handleMouseDown)
    canvas.addEventListener('mouseup', handleMouseUp)
    canvas.addEventListener('mouseleave', handleMouseUp)
    canvas.addEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('wheel', handleWheel, { passive: false })

    return () => {
      canvas.removeEventListener('mousedown', handleMouseDown)
      canvas.removeEventListener('mouseup', handleMouseUp)
      canvas.removeEventListener('mouseleave', handleMouseUp)
      canvas.removeEventListener('mousemove', handleMouseMove)
      canvas.removeEventListener('wheel', handleWheel)
    }
  }, [camera, gl])

  useFrame(() => {
    const orthoCamera = camera as THREE.OrthographicCamera

    const cameraOffset = new THREE.Vector3(10, 10, 10)
    const targetCameraPos = targetPosition.current.clone().add(cameraOffset)

    camera.position.lerp(targetCameraPos, 0.1)
    orthoCamera.zoom += (targetZoom.current - orthoCamera.zoom) * 0.1
    orthoCamera.updateProjectionMatrix()

    camera.lookAt(targetPosition.current)
  })

  return null
}

function SketchyGrid({ size }: { size: number }) {
  const geometry = useMemo(() => {
    const points: number[] = []
    const step = 2

    for (let i = -size; i <= size; i += step) {
      const wobbleStart = (Math.random() - 0.5) * 0.1
      const wobbleEnd = (Math.random() - 0.5) * 0.1
      points.push(i + wobbleStart, 0, -size)
      points.push(i + wobbleEnd, 0, size)
      points.push(-size, 0, i + wobbleStart)
      points.push(size, 0, i + wobbleEnd)
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [size])

  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color="#e0e0e0" linewidth={1} />
    </lineSegments>
  )
}

function Legend() {
  const statuses = [
    { label: 'Backlog', color: '#9ca3af' },
    { label: 'Build', color: '#f59e0b' },
    { label: 'Review', color: '#3b82f6' },
    { label: 'Human', color: '#ec4899' },
    { label: 'Done', color: '#10b981' },
    { label: 'Canceled', color: '#ef4444' },
  ]

  return (
    <div className="game-legend">
      <h4>Agent Status</h4>
      {statuses.map(s => (
        <div key={s.label} className="legend-item">
          <span className="legend-dot" style={{ background: s.color }} />
          <span>{s.label}</span>
        </div>
      ))}
      <div className="legend-controls">
        <span>🖱️ Drag to pan</span>
        <span>🔄 Scroll to zoom</span>
      </div>
    </div>
  )
}

function Stats({ projects, totalTasks }: { projects: number; totalTasks: number }) {
  return (
    <div className="game-stats">
      <div className="stat">
        <span className="stat-value">{projects}</span>
        <span className="stat-label">Projects</span>
      </div>
      <div className="stat">
        <span className="stat-value">{totalTasks}</span>
        <span className="stat-label">Agents</span>
      </div>
    </div>
  )
}

export function GameView() {
  const [projectsWithTasks, setProjectsWithTasks] = useState<ProjectWithTasks[]>([])
  const [loading, setLoading] = useState(true)

  const loadData = useCallback(async () => {
    const projects = await window.api.project.list()
    const results: ProjectWithTasks[] = []

    for (const project of projects) {
      const tasks = await window.api.task.list(project.id)
      results.push({ project, tasks })
    }

    setProjectsWithTasks(results)
    setLoading(false)
  }, [])

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [loadData])

  const cityPositions = useMemo(() => {
    const positions: Map<string, [number, number, number]> = new Map()
    const cols = Math.ceil(Math.sqrt(projectsWithTasks.length))
    const spacing = 6

    projectsWithTasks.forEach((p, i) => {
      const row = Math.floor(i / cols)
      const col = i % cols
      const x = (col - (cols - 1) / 2) * spacing
      const z = (row - Math.floor(projectsWithTasks.length / cols) / 2) * spacing
      positions.set(p.project.id, [x, 0, z])
    })

    return positions
  }, [projectsWithTasks])

  const totalTasks = projectsWithTasks.reduce((sum, p) => sum + p.tasks.length, 0)

  if (loading) {
    return (
      <div className="game-view loading">
        <p>Loading game world...</p>
      </div>
    )
  }

  return (
    <div className="game-view">
      <div className="game-header">
        <h2>🎮 Agent World</h2>
        <p>Your projects as cities, your agents as characters</p>
      </div>

      <Stats projects={projectsWithTasks.length} totalTasks={totalTasks} />

      <div className="game-canvas-container">
        <Canvas
          orthographic
          camera={{ position: [10, 10, 10], zoom: 50, near: 0.1, far: 100 }}
          gl={{ antialias: true }}
          style={{ background: '#fefefe' }}
        >
          <CameraControls />
          <ambientLight intensity={1} />

          <SketchyGrid size={15} />

          {projectsWithTasks.map((p) => {
            const pos = cityPositions.get(p.project.id)!
            return (
              <City
                key={p.project.id}
                project={p.project}
                position={pos}
                taskCount={p.tasks.length}
              />
            )
          })}

          {projectsWithTasks.flatMap((p) => {
            const pos = cityPositions.get(p.project.id)!
            return p.tasks.map((task, i) => (
              <Agent key={task.id} task={task} cityPosition={pos} index={i} />
            ))
          })}
        </Canvas>
      </div>

      <Legend />
    </div>
  )
}
