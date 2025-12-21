import { app, BrowserWindow } from 'electron'
import path from 'node:path'
import { initDb } from './db'
import { AgentService } from './agent-service'
import { registerIpcHandlers } from './ipc'

let agentService: AgentService

function createWindow(): void {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  initDb()

  agentService = new AgentService()
  registerIpcHandlers(agentService)

  agentService.startPolling((task) => {
    agentService.broadcastTaskUpdate(task)
  })

  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  agentService?.stopPolling()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
