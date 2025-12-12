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
    expect(screen.getByText('Agentic feature')).toBeInTheDocument()
    expect(screen.getByText('Deterministic feature')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('hides text when collapsed', () => {
    renderSidebar(true)
    expect(screen.queryByText('Home')).not.toBeInTheDocument()
    expect(screen.queryByText('Agentic feature')).not.toBeInTheDocument()
  })

  it('calls onToggle when toggle button clicked', () => {
    const onToggle = vi.fn()
    renderSidebar(false, onToggle)
    fireEvent.click(screen.getByText('←'))
    expect(onToggle).toHaveBeenCalledTimes(1)
  })

  it('renders workspace dropdown', () => {
    renderSidebar()
    expect(screen.getByText('Test Workspace')).toBeInTheDocument()
  })

  it('renders admin section links', () => {
    renderSidebar()
    expect(screen.getByText('Workspaces')).toBeInTheDocument()
    expect(screen.getByText('Billing')).toBeInTheDocument()
    expect(screen.getByText('API Status')).toBeInTheDocument()
  })
})
