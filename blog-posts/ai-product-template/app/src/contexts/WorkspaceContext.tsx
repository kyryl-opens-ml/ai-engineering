import { useState, useEffect, useCallback, type ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { fetchWorkspaces, createWorkspace as apiCreateWorkspace } from '../api';
import { WorkspaceContext, type Workspace } from './workspace';

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadWorkspaces() {
      if (!user) {
        setWorkspaces([]);
        setCurrentWorkspace(null);
        setLoading(false);
        return;
      }
      try {
        const data = await fetchWorkspaces();
        if (!cancelled) {
          setWorkspaces(data);
          if (data.length > 0) {
            setCurrentWorkspace((current) => current || data[0]);
          }
        }
      } catch {
        if (!cancelled) setWorkspaces([]);
      }
      if (!cancelled) setLoading(false);
    }

    loadWorkspaces();
    return () => { cancelled = true; };
  }, [user]);

  const createWorkspace = useCallback(async (name: string) => {
    const ws = await apiCreateWorkspace(name);
    setWorkspaces((prev) => [...prev, ws]);
    setCurrentWorkspace(ws);
  }, []);

  return (
    <WorkspaceContext.Provider
      value={{ workspaces, currentWorkspace, setCurrentWorkspace, createWorkspace, loading }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

