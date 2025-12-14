import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import App from './App'

function renderApp(route = '/') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>
  )
}

describe('App', () => {
  it('renders dashboard on home route', () => {
    renderApp('/')
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })

  it('renders sidebar with navigation', () => {
    renderApp('/')
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Agentic feature')).toBeInTheDocument()
    expect(screen.getByText('Deterministic feature')).toBeInTheDocument()
  })

  it('renders agentic feature page', () => {
    renderApp('/agent')
    expect(screen.getByRole('heading', { name: 'Agentic feature' })).toBeInTheDocument()
    expect(screen.getByText('Upload a PDF to generate a D3.js visualization')).toBeInTheDocument()
  })

  it('renders deterministic feature page', () => {
    renderApp('/deterministic')
    expect(screen.getByRole('heading', { name: 'Deterministic feature' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Create Item' })).toBeInTheDocument()
  })

  it('renders settings page', () => {
    renderApp('/settings')
    expect(screen.getByRole('heading', { name: 'Settings' })).toBeInTheDocument()
    expect(screen.getByText('Sign Out')).toBeInTheDocument()
  })

  it('renders workspaces page', () => {
    renderApp('/workspaces')
    expect(screen.getByRole('heading', { name: 'Workspaces' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Your Workspaces' })).toBeInTheDocument()
  })
})
