import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { Task, TaskStatus } from '../../../shared/types'

interface AgentProps {
  task: Task
  cityPosition: [number, number, number]
  index: number
}

const STATUS_COLORS: Record<TaskStatus, string> = {
  backlog: '#9ca3af',
  build: '#f59e0b',
  review: '#3b82f6',
  human: '#ec4899',
  done: '#10b981',
  canceled: '#ef4444',
}

function createSketchyPath(points: [number, number, number][], wobble = 0.008): number[] {
  const result: number[] = []
  for (let i = 0; i < points.length - 1; i++) {
    const [x1, y1, z1] = points[i]
    const [x2, y2, z2] = points[i + 1]
    const segments = 4
    for (let j = 0; j < segments; j++) {
      const t1 = j / segments
      const t2 = (j + 1) / segments
      const w1 = j === 0 ? 0 : (Math.random() - 0.5) * wobble
      const w2 = j === segments - 1 ? 0 : (Math.random() - 0.5) * wobble
      result.push(
        x1 + (x2 - x1) * t1 + w1, y1 + (y2 - y1) * t1 + w1, z1 + (z2 - z1) * t1 + w1,
        x1 + (x2 - x1) * t2 + w2, y1 + (y2 - y1) * t2 + w2, z1 + (z2 - z1) * t2 + w2
      )
    }
  }
  return result
}

export function Agent({ task, cityPosition, index }: AgentProps) {
  const groupRef = useRef<THREE.Group>(null)
  const leftLegRef = useRef<THREE.Group>(null)
  const rightLegRef = useRef<THREE.Group>(null)
  const leftArmRef = useRef<THREE.Group>(null)
  const rightArmRef = useRef<THREE.Group>(null)

  const walkAngle = useRef(Math.random() * Math.PI * 2)
  const walkRadius = useRef(1.0 + Math.random() * 0.8)
  const walkSpeed = useRef(0.4 + Math.random() * 0.3)
  const phaseOffset = useRef(index * 0.7 + Math.random())

  const color = STATUS_COLORS[task.status] || '#1e1e1e'
  const scale = 1.8

  const headGeometry = useMemo(() => {
    const points: number[] = []
    const r = 0.07
    const h = 0.1
    points.push(
      ...createSketchyPath([[-r, 0, 0], [-r * 0.85, h * 0.7, 0], [-r * 0.4, h, 0], [r * 0.4, h, 0], [r * 0.85, h * 0.7, 0], [r, 0, 0]]),
      ...createSketchyPath([[r, 0, 0], [r * 0.85, -h * 0.4, 0], [r * 0.3, -h * 0.55, 0], [-r * 0.3, -h * 0.55, 0], [-r * 0.85, -h * 0.4, 0], [-r, 0, 0]])
    )
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const hairGeometry = useMemo(() => {
    const points: number[] = []
    points.push(...createSketchyPath([[-0.05, 0.1, 0], [-0.03, 0.13, 0], [0, 0.12, 0]]))
    points.push(...createSketchyPath([[0, 0.12, 0], [0.03, 0.14, 0], [0.05, 0.1, 0]]))
    points.push(...createSketchyPath([[-0.06, 0.08, 0], [-0.07, 0.11, 0]]))
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const faceGeometry = useMemo(() => {
    const points: number[] = []
    points.push(-0.025, 0.03, 0.01, -0.015, 0.03, 0.01)
    points.push(0.015, 0.03, 0.01, 0.025, 0.03, 0.01)
    points.push(-0.012, 0.015, 0.01, 0.012, 0.015, 0.01)
    points.push(...createSketchyPath([[-0.02, -0.02, 0.01], [-0.01, -0.035, 0.01], [0.01, -0.035, 0.01], [0.02, -0.02, 0.01]]))
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const neckGeometry = useMemo(() => {
    const points = createSketchyPath([[0, 0, 0], [0, -0.04, 0]])
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const torsoGeometry = useMemo(() => {
    const points: number[] = []
    points.push(...createSketchyPath([[-0.045, 0, 0], [-0.05, -0.12, 0], [-0.03, -0.2, 0]]))
    points.push(...createSketchyPath([[0.045, 0, 0], [0.05, -0.12, 0], [0.03, -0.2, 0]]))
    points.push(...createSketchyPath([[-0.045, 0, 0], [0.045, 0, 0]]))
    points.push(...createSketchyPath([[-0.03, -0.2, 0], [0.03, -0.2, 0]]))
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const torsoDetailGeometry = useMemo(() => {
    const points: number[] = []
    points.push(...createSketchyPath([[0, -0.02, 0.005], [0, -0.18, 0.005]]))
    points.push(-0.015, -0.05, 0.005, 0.015, -0.05, 0.005)
    points.push(-0.012, -0.1, 0.005, 0.012, -0.1, 0.005)
    points.push(-0.01, -0.15, 0.005, 0.01, -0.15, 0.005)
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const upperArmGeometry = useMemo(() => {
    const points = createSketchyPath([[0, 0, 0], [0.015, -0.09, 0]])
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const lowerArmGeometry = useMemo(() => {
    const points = createSketchyPath([[0, 0, 0], [-0.01, -0.08, 0]])
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const handGeometry = useMemo(() => {
    const points: number[] = []
    points.push(...createSketchyPath([[0, 0, 0], [0.015, -0.02, 0]]))
    points.push(...createSketchyPath([[0, 0, 0], [0, -0.025, 0]]))
    points.push(...createSketchyPath([[0, 0, 0], [-0.012, -0.02, 0]]))
    points.push(...createSketchyPath([[0, 0, 0], [-0.02, -0.01, 0]]))
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const upperLegGeometry = useMemo(() => {
    const points = createSketchyPath([[0, 0, 0], [0.01, -0.11, 0]])
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const lowerLegGeometry = useMemo(() => {
    const points = createSketchyPath([[0, 0, 0], [-0.005, -0.1, 0]])
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  const footGeometry = useMemo(() => {
    const points: number[] = []
    points.push(...createSketchyPath([[0, 0, 0], [0.035, 0, 0], [0.04, -0.015, 0]]))
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [])

  useFrame((state) => {
    if (!groupRef.current) return

    const time = state.clock.elapsedTime + phaseOffset.current

    walkAngle.current += walkSpeed.current * 0.025
    const x = cityPosition[0] + Math.cos(walkAngle.current) * walkRadius.current
    const z = cityPosition[2] + Math.sin(walkAngle.current) * walkRadius.current

    groupRef.current.position.x = x
    groupRef.current.position.z = z
    groupRef.current.rotation.y = walkAngle.current + Math.PI / 2

    const bobAmount = Math.sin(time * 6) * 0.03
    groupRef.current.position.y = bobAmount

    const legSwing = Math.sin(time * 8) * 0.5
    if (leftLegRef.current) leftLegRef.current.rotation.x = legSwing
    if (rightLegRef.current) rightLegRef.current.rotation.x = -legSwing
    if (leftArmRef.current) leftArmRef.current.rotation.x = -legSwing * 0.7
    if (rightArmRef.current) rightArmRef.current.rotation.x = legSwing * 0.7
  })

  return (
    <group ref={groupRef} position={[cityPosition[0], 0, cityPosition[2]]} scale={[scale, scale, scale]}>
      <group position={[0, 0.6, 0]}>
        <lineSegments geometry={headGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <lineSegments geometry={hairGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <lineSegments geometry={faceGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
      </group>

      <group position={[0, 0.5, 0]}>
        <lineSegments geometry={neckGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
      </group>

      <group position={[0, 0.46, 0]}>
        <lineSegments geometry={torsoGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <lineSegments geometry={torsoDetailGeometry}>
          <lineBasicMaterial color={color} linewidth={1} />
        </lineSegments>
      </group>

      <group ref={leftArmRef} position={[0.05, 0.45, 0]}>
        <lineSegments geometry={upperArmGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <group position={[0.015, -0.09, 0]}>
          <lineSegments geometry={lowerArmGeometry}>
            <lineBasicMaterial color={color} linewidth={2} />
          </lineSegments>
          <group position={[-0.01, -0.08, 0]}>
            <lineSegments geometry={handGeometry}>
              <lineBasicMaterial color={color} linewidth={1} />
            </lineSegments>
          </group>
        </group>
      </group>

      <group ref={rightArmRef} position={[-0.05, 0.45, 0]}>
        <lineSegments geometry={upperArmGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <group position={[0.015, -0.09, 0]}>
          <lineSegments geometry={lowerArmGeometry}>
            <lineBasicMaterial color={color} linewidth={2} />
          </lineSegments>
          <group position={[-0.01, -0.08, 0]}>
            <lineSegments geometry={handGeometry}>
              <lineBasicMaterial color={color} linewidth={1} />
            </lineSegments>
          </group>
        </group>
      </group>

      <group ref={leftLegRef} position={[0.025, 0.26, 0]}>
        <lineSegments geometry={upperLegGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <group position={[0.01, -0.11, 0]}>
          <lineSegments geometry={lowerLegGeometry}>
            <lineBasicMaterial color={color} linewidth={2} />
          </lineSegments>
          <group position={[-0.005, -0.1, 0]}>
            <lineSegments geometry={footGeometry}>
              <lineBasicMaterial color={color} linewidth={2} />
            </lineSegments>
          </group>
        </group>
      </group>

      <group ref={rightLegRef} position={[-0.025, 0.26, 0]}>
        <lineSegments geometry={upperLegGeometry}>
          <lineBasicMaterial color={color} linewidth={2} />
        </lineSegments>
        <group position={[0.01, -0.11, 0]}>
          <lineSegments geometry={lowerLegGeometry}>
            <lineBasicMaterial color={color} linewidth={2} />
          </lineSegments>
          <group position={[-0.005, -0.1, 0]}>
            <lineSegments geometry={footGeometry}>
              <lineBasicMaterial color={color} linewidth={2} />
            </lineSegments>
          </group>
        </group>
      </group>

      <mesh position={[0, 0.4, 0]}>
        <sphereGeometry args={[0.12, 8, 8]} />
        <meshBasicMaterial color={color} transparent opacity={0.1} />
      </mesh>
    </group>
  )
}
