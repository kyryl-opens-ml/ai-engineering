---
theme: excali-slide
title: Everyone Can Build
drawings:
  persist: false
transition: fade
mdc: true
---

# Everyone Can Build

---

# Agenda

- Part 1: Overview
- Part 2: Workshop

---
layout: section
---

# Part 1: Overview

---

# Everyone Can Build

<div class="grid grid-cols-2 gap-8">
<div>

- **283 PRs from non-engineers** shipped at Alan (€700M ARR)
- Before: spotted issue → opened ticket → fell behind priorities → shipped sprints later
- Now: non-tech person just ships the PR

<a href="https://alan.com/en/blog/discover-alan/a/everyone-can-build" target="_blank">alan.com/blog</a>

</div>
<div>
  <img src="/images/alan-1.png" class="h-80" />
</div>
</div>

---

# Where We're Going

<div class="grid grid-cols-2 gap-8">
<div>

- It's clear where we are going
- AI capability for software tasks is growing exponentially
- Claude Opus 4.5 can complete 5-hour human tasks

<a href="https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/" target="_blank">metr.org/blog</a>

</div>
<div>
  <img src="/images/metr-1.png" class="h-80" />
</div>
</div>

---

# AI-Resistant Evaluations

<div class="grid grid-cols-2 gap-8">
<div>

- Anthropic - best research lab for coding LLMs
- They're having trouble designing take-home tests
- Claude keeps beating their technical evaluations

<a href="https://www.anthropic.com/engineering/AI-resistant-technical-evaluations" target="_blank">anthropic.com/engineering</a>

</div>
<div>
  <img src="/images/anth-1.png" class="h-80" />
</div>
</div>

---

# Same Shift as Compilers

<div class="grid grid-cols-2 gap-4">
<div class="flex flex-col gap-2">
  <img src="/images/gb-1.png" class="h-36" />
  <img src="/images/nodejs-1.png" class="h-36" />
</div>
<div>
  <img src="/images/gh-1.png" class="h-80" />
</div>
</div>

---

# Why? Agents!

- <a href="https://cursor.com/" target="_blank">Cursor</a> - AI-first code editor
- <a href="https://openai.com/codex/" target="_blank">Codex</a> - OpenAI's cloud coding agent
- <a href="https://code.claude.com/docs/en/overview" target="_blank">Claude Code</a> - Anthropic's terminal agent
- <a href="https://roocode.com/" target="_blank">Roo Code</a> - Open-source VS Code extension
- <a href="https://ampcode.com/" target="_blank">Amp</a> - Frontier coding agent

---

# What is an Agent?

- **Agent = LLM + Actions + Loop**
- Reasoning and multi-step capabilities are so good
- Coding Agent = tools are editing files and running programs

---

# Actions

- **Tools** - built-in capabilities (read, write, execute)
- <a href="https://modelcontextprotocol.io/docs/getting-started/intro" target="_blank">MCP</a> - Model Context Protocol for external integrations
- <a href="https://code.claude.com/docs/en/skills" target="_blank">Skills</a> - reusable task-specific instructions

---

# Intuitive Way of Understanding Agents

<div class="flex flex-col gap-6">
<div>

**Business Process** (static)

<div class="flex items-center gap-2 text-sm">
  <div class="border px-4 py-2 rounded">Input</div>
  <span>→</span>
  <div class="border px-4 py-2 rounded bg-gray-100">Step 1</div>
  <span>→</span>
  <div class="border px-4 py-2 rounded bg-gray-100">Step 2</div>
  <span>→</span>
  <div class="border px-4 py-2 rounded bg-gray-100">Step 3</div>
  <span>→</span>
  <div class="border px-4 py-2 rounded">Output</div>
</div>

</div>
<div>

**Agent** (dynamic)

<script setup>
import { ref } from 'vue'
const flow = ref([])
const generate = () => {
  const count = Math.floor(Math.random() * 4) + 4
  const branches = new Set()
  const numBranches = Math.floor(Math.random() * 3) + 1
  while (branches.size < numBranches && branches.size < count) {
    branches.add(Math.floor(Math.random() * count))
  }
  flow.value = Array.from({ length: count }, (_, i) => ({
    name: `Step ${i + 1}`,
    branch: branches.has(i)
  }))
}
generate()
</script>

<div class="flex items-center gap-1 text-xs flex-wrap">
  <div @click="generate" class="border px-3 py-2 rounded bg-green-100 cursor-pointer hover:bg-green-200">Input</div>
  <span>→</span>
  <template v-for="(step, i) in flow" :key="i">
    <div v-if="step.branch" class="flex flex-col gap-1">
      <div class="border px-2 py-1 rounded bg-blue-100">{{ step.name }}a</div>
      <div class="border px-2 py-1 rounded bg-purple-100">{{ step.name }}b</div>
    </div>
    <div v-else class="border px-3 py-2 rounded bg-blue-100">{{ step.name }}</div>
    <span>→</span>
  </template>
  <div class="border px-3 py-2 rounded">Output</div>
</div>

</div>
</div>

---

# Who Benefits the Most?

- **Engineers** - multiply productivity, focus on architecture
- **Prototypers** - rapid iteration, validate ideas fast
- **Those who can steer agents best** - the new superpower

The skill: knowing what to ask and when to course-correct

<a href="https://newsletter.pragmaticengineer.com/p/when-ai-writes-almost-all-code-what" target="_blank">pragmaticengineer.com</a>

---

# Glimpses of the Future

<div class="grid grid-cols-2 gap-8">
<div>

- **SE, Product, ML Eng → Product Builders**
- <a href="https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/" target="_blank">Generative UI</a> - each app becomes a platform, unique UI per user
- Self-driving SaaS - software that builds itself
- Product building = RTS game

<a href="https://kyrylai.com/2025/12/23/becoming-an-aiagent-tech-lead/" target="_blank">kyrylai.com/agent-tech-lead</a>

</div>
<div>
  <img src="/images/sc-1.png" class="h-72" />
</div>
</div>

---

# Where to Start?

<div class="grid grid-cols-3 gap-4 text-sm">

<div class="border-2 rounded-lg p-4 bg-green-50">

**1. Prototype + Vision**

- <a href="https://aistudio.google.com/" target="_blank">AI Studio</a>
- <a href="https://lovable.dev/" target="_blank">Lovable</a>
- <a href="https://bolt.new/" target="_blank">Bolt</a>

*No setup required, only account*

</div>

<div class="border-2 rounded-lg p-4 bg-blue-50">

**2. More Impact**

- <a href="https://code.claude.com/docs/en/overview" target="_blank">Claude Code</a>
- <a href="https://openai.com/codex/" target="_blank">Codex</a>
- <a href="https://github.com/google-gemini/gemini-cli" target="_blank">Gemini CLI</a>

*Requires: Terminal, GitHub, Hosting*

</div>

<div class="border-2 rounded-lg p-4 bg-purple-50">

**3. Direct Contribution**

- Slack integrations
- Web integrations
- Task tracker integrations

*Requires: Custom setup + Verification*

</div>

</div>

---
layout: section
---

# AI Studio Demo

<a href="https://aistudio.google.com/apps?source=showcase&showcaseTag=gemini-3" target="_blank">aistudio.google.com/apps</a>

---

# Claude Trio Demo

<div class="grid grid-cols-2 gap-8">
<div>

Based on Claude Opus 4.5

- <a href="https://claude.ai/" target="_blank">Claude Chat</a> - conversational AI
- <a href="https://code.claude.com/docs/en/overview" target="_blank">Claude Code</a> - terminal coding agent
- <a href="https://support.claude.com/en/articles/13345190-getting-started-with-cowork" target="_blank">Claude Cowork</a> - collaborative workspace

</div>
<div>
  <img src="/images/claude-1.png" class="h-80" />
</div>
</div>

---
layout: section
---

# Part 2: Workshop

---

# Let's Build!

<div class="text-sm">

**Start from the Problem** - Good description = 80% there

If you ever have an idea and are part of a catalyst session with AXL, you may be able to vibe code it to communicate the idea/vision

</div>

<div class="grid grid-cols-3 gap-3 text-xs mt-4">

<div class="border-4 border-green-500 rounded-lg p-3 bg-green-50">

**1. Prototype + Vision** ← Today

- <a href="https://aistudio.google.com/" target="_blank">AI Studio</a>
- <a href="https://lovable.dev/" target="_blank">Lovable</a>
- <a href="https://bolt.new/" target="_blank">Bolt</a>

*No setup required*

</div>

<div class="border rounded-lg p-3 bg-blue-50 opacity-60">

**2. More Impact**

- <a href="https://code.claude.com/docs/en/overview" target="_blank">Claude Code</a>
- <a href="https://openai.com/codex/" target="_blank">Codex</a>
- <a href="https://github.com/google-gemini/gemini-cli" target="_blank">Gemini CLI</a>

*Requires: Terminal, GitHub*

</div>

<div class="border rounded-lg p-3 bg-purple-50 opacity-60">

**3. Direct Contribution**

- Slack integrations
- Web integrations
- Task tracker integrations

*Requires: Custom setup*

</div>

</div>

<div class="mt-4 text-center">

**→ Go to <a href="https://aistudio.google.com/" target="_blank">aistudio.google.com</a> and build! ←**

</div>

---

# Questions?
