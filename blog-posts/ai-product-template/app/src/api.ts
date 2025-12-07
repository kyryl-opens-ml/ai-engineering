import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL;

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (session) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  return headers;
}

export async function fetchHealth() {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) throw new Error('Failed to fetch health');
  return response.json();
}

export async function fetchWorkspaces() {
  const response = await fetch(`${API_URL}/workspaces/`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch workspaces');
  return response.json();
}

export async function createWorkspace(name: string) {
  const response = await fetch(`${API_URL}/workspaces/`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ name }),
  });
  if (!response.ok) throw new Error('Failed to create workspace');
  return response.json();
}

export async function fetchWorkspaceMembers(workspaceId: string) {
  const response = await fetch(`${API_URL}/workspaces/${workspaceId}/members`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch members');
  return response.json();
}

export async function addWorkspaceMember(workspaceId: string, email: string) {
  const response = await fetch(`${API_URL}/workspaces/${workspaceId}/members`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ email }),
  });
  if (!response.ok) throw new Error('Failed to add member');
  return response.json();
}

export async function removeWorkspaceMember(workspaceId: string, memberId: string) {
  const response = await fetch(`${API_URL}/workspaces/${workspaceId}/members/${memberId}`, {
    method: 'DELETE',
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to remove member');
  return response.json();
}

export async function fetchItems(workspaceId: string) {
  const response = await fetch(`${API_URL}/items/?workspace_id=${workspaceId}`, {
    headers: await getAuthHeaders(),
  });
  if (!response.ok) throw new Error('Failed to fetch items');
  return response.json();
}

export async function createItem(workspaceId: string, title: string, description: string) {
  const response = await fetch(`${API_URL}/items/?workspace_id=${workspaceId}`, {
    method: 'POST',
    headers: await getAuthHeaders(),
    body: JSON.stringify({ title, description }),
  });
  if (!response.ok) throw new Error('Failed to create item');
  return response.json();
}
