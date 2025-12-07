import { createContext } from 'react';

export interface Workspace {
  id: string;
  name: string;
  owner_id: string;
  role: string;
}

export interface WorkspaceContextType {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspace: (ws: Workspace | null) => void;
  createWorkspace: (name: string) => Promise<void>;
  loading: boolean;
}

export const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

