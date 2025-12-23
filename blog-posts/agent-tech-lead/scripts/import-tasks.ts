import Database from 'better-sqlite3'
import { randomUUID } from 'node:crypto'
import * as fs from 'node:fs'
import * as path from 'node:path'

interface ParsedTask {
  title: string
  description: string
}

function parseTasks(input: string): ParsedTask[] {
  const tasks: ParsedTask[] = []
  const lines = input.split('\n')
  
  let currentTask: ParsedTask | null = null
  let descriptionLines: string[] = []
  
  for (const line of lines) {
    const taskMatch = line.match(/^(\d+)\.\s+(.+)$/)
    
    if (taskMatch) {
      if (currentTask) {
        currentTask.description = [currentTask.title, ...descriptionLines].join('\n').trim()
        tasks.push(currentTask)
      }
      currentTask = { title: taskMatch[2].trim(), description: '' }
      descriptionLines = []
    } else if (currentTask) {
      if (line.trim() === '###' || line.trim() === '') {
        if (descriptionLines.length > 0 || line.trim() !== '') {
          descriptionLines.push(line)
        }
      } else {
        descriptionLines.push(line)
      }
    }
  }
  
  if (currentTask) {
    currentTask.description = [currentTask.title, ...descriptionLines].join('\n').trim()
    tasks.push(currentTask)
  }
  
  return tasks
}

function initDb(dbPath: string): Database.Database {
  const db = new Database(dbPath)
  db.pragma('journal_mode = WAL')
  
  db.exec(`
    CREATE TABLE IF NOT EXISTS projects (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      repository TEXT NOT NULL,
      default_branch TEXT,
      subfolder TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      status TEXT NOT NULL DEFAULT 'backlog',
      agent_id TEXT,
      agent_status TEXT,
      agent_url TEXT,
      base_branch TEXT,
      target_branch TEXT,
      model TEXT,
      position INTEGER DEFAULT 0,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
  `)
  
  return db
}

function getProjectByName(db: Database.Database, name: string): { id: string; name: string; repository: string } | undefined {
  return db.prepare('SELECT id, name, repository FROM projects WHERE name = ?').get(name) as { id: string; name: string; repository: string } | undefined
}

function createProject(db: Database.Database, name: string, repository: string): string {
  const id = randomUUID()
  db.prepare('INSERT INTO projects (id, name, repository) VALUES (?, ?, ?)').run(id, name, repository)
  return id
}

function createTask(db: Database.Database, projectId: string, title: string, description: string): void {
  const id = randomUUID()
  const maxPos = db
    .prepare('SELECT COALESCE(MAX(position), -1) as max FROM tasks WHERE project_id = ? AND status = ?')
    .get(projectId, 'backlog') as { max: number }

  db.prepare(
    'INSERT INTO tasks (id, project_id, title, description, status, position) VALUES (?, ?, ?, ?, ?, ?)'
  ).run(id, projectId, title, description, 'backlog', maxPos.max + 1)
}

function printUsage() {
  console.log('Usage: npx tsx scripts/import-tasks.ts --name <project> --repo <url> --file <tasks.txt> [--db <path>]')
  console.log('')
  console.log('Options:')
  console.log('  --name <project>   Project name (creates if not exists)')
  console.log('  --repo <url>       GitHub repository URL (e.g. https://github.com/org/repo)')
  console.log('  --file <path>      Path to text file with tasks')
  console.log('  --db <path>        Path to database file (default: ./db.db)')
  console.log('  --yes              Skip confirmation prompt')
  console.log('')
  console.log('Example:')
  console.log('  npx tsx scripts/import-tasks.ts --name "My Project" --repo "https://github.com/me/repo" --file tasks.txt')
}

async function main() {
  const args = process.argv.slice(2)
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage()
    process.exit(0)
  }

  let projectName: string | undefined
  let repoUrl: string | undefined
  let inputFile: string | undefined
  let dbPath = path.join(process.cwd(), 'db.db')
  let skipConfirm = false

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--name':
        projectName = args[++i]
        break
      case '--repo':
        repoUrl = args[++i]
        break
      case '--file':
        inputFile = args[++i]
        break
      case '--db':
        dbPath = args[++i]
        break
      case '--yes':
      case '-y':
        skipConfirm = true
        break
    }
  }

  if (!projectName || !repoUrl || !inputFile) {
    console.error('Error: --name, --repo, and --file are required\n')
    printUsage()
    process.exit(1)
  }

  if (!inputFile || !fs.existsSync(inputFile)) {
    console.error(`File not found: ${inputFile}`)
    process.exit(1)
  }

  const db = initDb(dbPath)
  
  let project = getProjectByName(db, projectName)
  let projectId: string
  
  if (project) {
    console.log(`Using existing project: ${project.name} (${project.repository})`)
    projectId = project.id
  } else {
    projectId = createProject(db, projectName, repoUrl)
    console.log(`Created new project: ${projectName} (${repoUrl})`)
  }

  const input = fs.readFileSync(inputFile, 'utf-8')
  const tasks = parseTasks(input)

  if (tasks.length === 0) {
    console.log('No tasks found in input file')
    db.close()
    process.exit(0)
  }

  console.log(`\nParsed ${tasks.length} tasks:`)
  tasks.forEach((t, i) => console.log(`  ${i + 1}. ${t.title}`))

  if (!skipConfirm) {
    const readline = await import('readline')
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    
    const confirm = await new Promise<string>(resolve => {
      rl.question('\nImport these tasks to backlog? (y/n): ', resolve)
    })
    rl.close()

    if (confirm.toLowerCase() !== 'y') {
      console.log('Aborted')
      db.close()
      process.exit(0)
    }
  }

  for (const task of tasks) {
    createTask(db, projectId, task.title, task.description)
    console.log(`  ✓ ${task.title}`)
  }

  console.log(`\nImported ${tasks.length} tasks to backlog`)
  db.close()
}

main().catch(console.error)
