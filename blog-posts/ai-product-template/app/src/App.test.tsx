import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import App from './App'

function renderApp() {
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}

describe('App', () => {
  it('renders dashboard on home route', () => {
    renderApp()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('renders sidebar', () => {
    renderApp()
    expect(screen.getByText('Home')).toBeInTheDocument()
  })
})
