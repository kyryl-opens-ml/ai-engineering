import '@testing-library/jest-dom'
import { vi } from 'vitest'

vi.mock('../supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } }),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signOut: vi.fn(),
    },
  },
}))

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    session: null,
    user: { id: 'test-user', email: 'test@test.com' },
    loading: false,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
  }),
}))

vi.mock('../hooks/useWorkspace', () => ({
  useWorkspace: () => ({
    workspaces: [{ id: '1', name: 'Test Workspace', owner_id: 'test-user', role: 'owner' }],
    currentWorkspace: { id: '1', name: 'Test Workspace', owner_id: 'test-user', role: 'owner' },
    setCurrentWorkspace: vi.fn(),
    createWorkspace: vi.fn(),
    loading: false,
  }),
}))
