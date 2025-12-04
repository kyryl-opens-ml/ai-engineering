import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL;

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    return { Authorization: `Bearer ${session.access_token}` };
  }
  return {};
}

export async function fetchHealth() {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) throw new Error('Failed to fetch health');
  return response.json();
}

export async function fetchItems() {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/items/`, { headers });
  if (!response.ok) throw new Error('Failed to fetch items');
  return response.json();
}

export async function createItem(title: string, description: string) {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ title, description }),
  });
  if (!response.ok) throw new Error('Failed to create item');
  return response.json();
}
