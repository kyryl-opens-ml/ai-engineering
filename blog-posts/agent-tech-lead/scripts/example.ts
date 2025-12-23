// Example ad-hoc script
// Run with: make run-script FILE=example.ts
// Or directly: npx tsx scripts/example.ts

console.log('Hello from TypeScript script!')

const data = {
  name: 'Agent Tech Lead',
  version: '1.0.0',
  timestamp: new Date().toISOString()
}

console.log('Data:', JSON.stringify(data, null, 2))

// Example async operation
async function fetchExample() {
  console.log('Running async operation...')
  await new Promise(resolve => setTimeout(resolve, 100))
  console.log('Done!')
}

fetchExample()

