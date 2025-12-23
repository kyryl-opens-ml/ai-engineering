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
  return db
}

function getProjects(db: Database.Database): { id: string; name: string; repository: string }[] {
  return db.prepare('SELECT id, name, repository FROM projects ORDER BY created_at DESC').all() as { id: string; name: string; repository: string }[]
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

async function main() {
  const args = process.argv.slice(2)
  
  if (args.length < 1) {
    console.log('Usage: npx tsx scripts/import-tasks.ts <file.txt> [--db <path>] [--project <id>]')
    console.log('\nOptions:')
    console.log('  <file.txt>       Path to text file with tasks')
    console.log('  --db <path>      Path to database file (default: ./db.db)')
    console.log('  --project <id>   Project ID to import tasks into')
    process.exit(1)
  }

  const inputFile = args[0]
  let dbPath = path.join(process.cwd(), 'db.db')
  let projectId: string | undefined

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--db' && args[i + 1]) {
      dbPath = args[++i]
    } else if (args[i] === '--project' && args[i + 1]) {
      projectId = args[++i]
    }
  }

  if (!fs.existsSync(inputFile)) {
    console.error(`File not found: ${inputFile}`)
    process.exit(1)
  }

  if (!fs.existsSync(dbPath)) {
    console.error(`Database not found: ${dbPath}`)
    process.exit(1)
  }

  const db = initDb(dbPath)
  let projects = getProjects(db)

  if (projects.length === 0) {
    console.log('No projects found. Let\'s create one.\n')
    
    const readline = await import('readline')
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    
    const name = await new Promise<string>(resolve => {
      rl.question('Project name: ', resolve)
    })
    const repository = await new Promise<string>(resolve => {
      rl.question('Repository (e.g. github.com/org/repo): ', resolve)
    })
    rl.close()
    
    if (!name || !repository) {
      console.error('Name and repository are required')
      db.close()
      process.exit(1)
    }
    
    projectId = createProject(db, name, repository)
    console.log(`\nCreated project: ${name}`)
  }

  if (!projectId) {
    projects = getProjects(db)
    console.log('\nAvailable projects:')
    projects.forEach((p, i) => console.log(`  ${i + 1}. ${p.name} (${p.repository})`))
    
    const readline = await import('readline')
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
    
    const answer = await new Promise<string>(resolve => {
      rl.question('\nSelect project number: ', resolve)
    })
    rl.close()
    
    const idx = parseInt(answer, 10) - 1
    if (idx < 0 || idx >= projects.length) {
      console.error('Invalid selection')
      db.close()
      process.exit(1)
    }
    projectId = projects[idx].id
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

  for (const task of tasks) {
    createTask(db, projectId, task.title, task.description)
    console.log(`  ✓ ${task.title}`)
  }

  console.log(`\nImported ${tasks.length} tasks to backlog`)
  db.close()
}

main().catch(console.error)

