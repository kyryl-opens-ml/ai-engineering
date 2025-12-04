const API_URL = import.meta.env.VITE_API_URL;

export async function fetchHealth() {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) throw new Error('Failed to fetch health');
  return response.json();
}

export async function fetchItems() {
  const response = await fetch(`${API_URL}/items/`);
  if (!response.ok) throw new Error('Failed to fetch items');
  return response.json();
}

export async function createItem(title: string, description: string) {
  const response = await fetch(`${API_URL}/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description }),
  });
  if (!response.ok) throw new Error('Failed to create item');
  return response.json();
}
