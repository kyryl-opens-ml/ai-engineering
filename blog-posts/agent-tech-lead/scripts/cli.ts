import 'dotenv/config'
import * as readline from 'readline'
import { CursorClient, Agent } from './cursor-client.js'

function getClient() {
  return new CursorClient()
}

async function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close()
      resolve(answer.trim())
    })
  })
}

async function getAllAgents(client: CursorClient): Promise<Agent[]> {
  const allAgents: Agent[] = []
  let cursor: string | undefined

  do {
    const response = await client.listAgents(100, cursor)
    allAgents.push(...response.agents)
    cursor = response.nextCursor
  } while (cursor)

  return allAgents
}

async function list() {
  const client = getClient()
  const repoArg = process.argv[3]

  const allAgents = await getAllAgents(client)

  let filteredAgents = allAgents

  if (repoArg) {
    filteredAgents = allAgents.filter(a => a.source.repository === repoArg)
  } else {
    const repos = [...new Set(allAgents.map(a => a.source.repository))]
    if (repos.length > 1) {
      console.log('\nAvailable repositories:')
      repos.forEach((r, i) => console.log(`  ${i + 1}. ${r}`))
      console.log(`  0. All repositories`)
      const choice = await prompt('\nSelect repository (0 for all): ')
      const idx = parseInt(choice, 10)
      if (idx > 0 && idx <= repos.length) {
        filteredAgents = allAgents.filter(a => a.source.repository === repos[idx - 1])
      }
    }
  }

  console.log(`\nTotal agents: ${filteredAgents.length}`)
  console.log(JSON.stringify(filteredAgents, null, 2))
}

async function status() {
  const client = getClient()
  const id = process.argv[3]
  if (!id) {
    console.error('Usage: npx tsx scripts/cli.ts status <agent_id>')
    process.exit(1)
  }
  const response = await client.getAgent(id)
  console.log(JSON.stringify(response, null, 2))
}

async function models() {
  const client = getClient()
  const response = await client.listModels()
  console.log(JSON.stringify(response, null, 2))
}

async function me() {
  const client = getClient()
  const response = await client.getMe()
  console.log(JSON.stringify(response, null, 2))
}

async function repos() {
  const client = getClient()
  const response = await client.listRepositories()
  console.log(JSON.stringify(response, null, 2))
}

const command = process.argv[2]

switch (command) {
  case 'list':
    list()
    break
  case 'status':
    status()
    break
  case 'models':
    models()
    break
  case 'me':
    me()
    break
  case 'repos':
    repos()
    break
  default:
    console.log('Usage: npx tsx scripts/cli.ts <command>')
    console.log('\nCommands:')
    console.log('  list [repo]    - List all agents (optional: exact repo match)')
    console.log('  status <id>    - Get agent status')
    console.log('  models         - List available models')
    console.log('  me             - Get API key info')
    console.log('  repos          - List GitHub repositories')
}

