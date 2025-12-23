import { describe, it, expect } from 'vitest'

describe('example', () => {
  it('should pass a basic test', () => {
    expect(1 + 1).toBe(2)
  })

  it('should work with strings', () => {
    const appName = 'Agent Tech Lead'
    expect(appName).toContain('Agent')
  })
})

