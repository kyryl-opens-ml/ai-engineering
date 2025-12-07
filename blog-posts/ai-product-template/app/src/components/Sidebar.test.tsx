import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import { Sidebar } from './Sidebar'

function renderSidebar(collapsed = false, onToggle = vi.fn()) {
  return render(
    <BrowserRouter>
      <Sidebar collapsed={collapsed} onToggle={onToggle} />
    </BrowserRouter>
  )
}

describe('Sidebar', () => {
  it('renders navigation links', () => {
    renderSidebar()
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Feature 1')).toBeInTheDocument()
    expect(screen.getByText('Feature 2')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('hides text when collapsed', () => {
    renderSidebar(true)
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
    expect(screen.queryByText('Feature 1')).not.toBeInTheDocument()
  })

  it('calls onToggle when toggle button clicked', () => {
    const onToggle = vi.fn()
    renderSidebar(false, onToggle)
    fireEvent.click(screen.getByText('←'))
    expect(onToggle).toHaveBeenCalledTimes(1)
  })
})
