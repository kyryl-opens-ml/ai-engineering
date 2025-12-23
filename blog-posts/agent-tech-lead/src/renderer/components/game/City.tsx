import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import type { Project } from '../../../shared/types'

interface CityProps {
  project: Project
  position: [number, number, number]
  taskCount: number
}

function createSketchyLine(points: THREE.Vector3[], wobble = 0.05): THREE.Vector3[] {
  const result: THREE.Vector3[] = []
  for (let i = 0; i < points.length - 1; i++) {
    const start = points[i]
    const end = points[i + 1]
    const segments = 8
    for (let j = 0; j <= segments; j++) {
      const t = j / segments
      const x = start.x + (end.x - start.x) * t + (Math.random() - 0.5) * wobble
      const y = start.y + (end.y - start.y) * t + (Math.random() - 0.5) * wobble
      const z = start.z + (end.z - start.z) * t + (Math.random() - 0.5) * wobble
      result.push(new THREE.Vector3(x, y, z))
    }
  }
  return result
}

function SketchyBuilding({ height, offset }: { height: number; offset: [number, number] }) {
  const geometry = useMemo(() => {
    const w = 0.4
    const d = 0.4
    const [ox, oz] = offset

    const corners = [
      new THREE.Vector3(-w + ox, 0, -d + oz),
      new THREE.Vector3(w + ox, 0, -d + oz),
      new THREE.Vector3(w + ox, 0, d + oz),
      new THREE.Vector3(-w + ox, 0, d + oz),
    ]
    const topCorners = corners.map(c => new THREE.Vector3(c.x, height, c.z))
    const roofPeak = new THREE.Vector3(ox, height + 0.3, oz)

    const lines: THREE.Vector3[][] = [
      [...corners, corners[0]],
      [...topCorners, topCorners[0]],
      [corners[0], topCorners[0]],
      [corners[1], topCorners[1]],
      [corners[2], topCorners[2]],
      [corners[3], topCorners[3]],
      [topCorners[0], roofPeak, topCorners[2]],
      [topCorners[1], roofPeak, topCorners[3]],
    ]

    const allPoints: number[] = []
    lines.forEach(line => {
      const sketchy = createSketchyLine(line, 0.03)
      for (let i = 0; i < sketchy.length - 1; i++) {
        allPoints.push(sketchy[i].x, sketchy[i].y, sketchy[i].z)
        allPoints.push(sketchy[i + 1].x, sketchy[i + 1].y, sketchy[i + 1].z)
      }
    })

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(allPoints, 3))
    return geo
  }, [height, offset])

  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color="#1e1e1e" linewidth={1} />
    </lineSegments>
  )
}

function SketchyGround({ size }: { size: number }) {
  const geometry = useMemo(() => {
    const corners = [
      new THREE.Vector3(-size, 0, -size),
      new THREE.Vector3(size, 0, -size),
      new THREE.Vector3(size, 0, size),
      new THREE.Vector3(-size, 0, size),
    ]
    const sketchy = createSketchyLine([...corners, corners[0]], 0.05)
    const points: number[] = []
    for (let i = 0; i < sketchy.length - 1; i++) {
      points.push(sketchy[i].x, sketchy[i].y, sketchy[i].z)
      points.push(sketchy[i + 1].x, sketchy[i + 1].y, sketchy[i + 1].z)
    }

    for (let i = -size + 0.5; i < size; i += 0.5) {
      const crossLine = createSketchyLine([
        new THREE.Vector3(i, 0, -size),
        new THREE.Vector3(i, 0, size)
      ], 0.02)
      for (let j = 0; j < crossLine.length - 1; j++) {
        points.push(crossLine[j].x, crossLine[j].y, crossLine[j].z)
        points.push(crossLine[j + 1].x, crossLine[j + 1].y, crossLine[j + 1].z)
      }
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    return geo
  }, [size])

  return (
    <lineSegments geometry={geometry}>
      <lineBasicMaterial color="#ccc" linewidth={1} />
    </lineSegments>
  )
}

export function City({ project, position, taskCount }: CityProps) {
  const groupRef = useRef<THREE.Group>(null)
  const labelRef = useRef<THREE.Sprite>(null)

  const buildings = useMemo(() => {
    const count = Math.max(1, Math.min(5, Math.ceil(taskCount / 2)))
    const result: { height: number; offset: [number, number] }[] = []
    const positions: [number, number][] = [
      [0, 0],
      [-0.8, -0.5],
      [0.8, -0.5],
      [-0.5, 0.8],
      [0.7, 0.7],
    ]
    for (let i = 0; i < count; i++) {
      result.push({
        height: 0.6 + Math.random() * 0.6,
        offset: positions[i]
      })
    }
    return result
  }, [taskCount])

  const labelTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 128
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = 'transparent'
    ctx.fillRect(0, 0, 512, 128)
    ctx.font = '48px Virgil, Comic Sans MS, cursive'
    ctx.fillStyle = '#1e1e1e'
    ctx.textAlign = 'center'
    ctx.fillText(project.name, 256, 80)
    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    return texture
  }, [project.name])

  useFrame(() => {
    if (labelRef.current) {
      labelRef.current.material.rotation = 0
    }
  })

  return (
    <group ref={groupRef} position={position}>
      <SketchyGround size={1.5} />
      {buildings.map((b, i) => (
        <SketchyBuilding key={i} height={b.height} offset={b.offset} />
      ))}
      <sprite ref={labelRef} position={[0, 2, 0]} scale={[3, 0.75, 1]}>
        <spriteMaterial map={labelTexture} transparent />
      </sprite>
    </group>
  )
}
