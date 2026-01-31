# Everyone Can Build

## Dev:

```
npm install
npm run dev
```


Alan: https://alan.com/en/blog/discover-alan/a/everyone-can-build
AI is the new UI: https://x.com/davemorin/status/2013109271861350677
Claude Agent SDK: https://www.youtube.com/watch?v=TqC1qOfiVcQ
Linus Torvalds case https://x.com/rauchg/status/2010411457880772924?s=20
NPM X: https://x.com/rough__sea/status/2013280952370573666 
Grady X: https://x.com/Grady_Booch/status/2013331606795362398
https://claude.com/download


## Blog: 

### Context: 

1. Everyone Can Build 

This is the time when everyone can build. Companies must move from slow and error-prone processes of "see the issue -> get a ticket -> mess with other priorities" to a new process: "see the issue -> send a fix." With coding agents and the right process, it should be almost automatically done and mostly by non-tech teams!

Good case here from Alan (digital insurance service, $700M ARR+) - where they enable non-tech people to contribute to the core product via Cursor and delivered ~300 PRs to the product. See original post in the comment.

If you are not enabling everyone from your company to contribute to the product - you might fall behind those who do!

[alan-1.png]

https://alan.com/en/blog/discover-alan/a/everyone-can-build

2. It's very clear where we are going! 

You can find a bunch of AI slop and silly mistakes of LLMs with counting 'r' and comparing 9.11 and 9.9, but it's very clear to see where we are going.  
LLMs can perform long-running engineering tasks with superhuman performance.

[metr-1.png]

While humans are still extremely important to steer and manage them. As a small anecdote - even the website of this study ends up with a "Hiring sections"

[metr-2.png]

https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

3. If coding task is narrow and well specified - don't waste time - ask LLM. 

[anth-1.png]

Recent blog post from Anthropic where they gave up on their take-home assignment because nobody can beat LLM. Extremely fascinating! 

https://www.anthropic.com/engineering/AI-resistant-technical-evaluations

4. Same Shift as Compiler

See this image - we don't do this anymore! Punched cards, writing machine code, etc! Compilers changed software forever same as LLMs nowadays! 

[gh-1.png]

Animations: 

<programming language> -> [compiler] -> <machine code>

<task definitions / feedback> [agent] -> <programming language> -> [compiler] -> <machine code>

Which makes me 100x more bullish on software and code! 

### Why is this happenng

5. Intuitive Way of Understanding Agents 

One of the most intuitive ways to understand agents is to visualize it in comparison to a simple business process. Everyone is familiar with those: step 1, step 2, step 3. No matter what the input is, you already run it through the same 3 steps. It's very reliable and predictable but at the same time limited, because, well, it's static. Kind of a one-size-fits-all solution. 

<static agent>

While an agent is a set of those static business processes where each one is unique to its input. For input of user A, it could be step 1 - step 4, for input of user B - it could be step 1 - step 10 with branching, pauses and fallback. This is why agents are way way more powerful and their applications are way more broader but the trade-off is that it's non-static.

<gif of agent>

6. Who Benefits the Most from Coding Agents! 

- Engineers - multiply productivity, focus on architecture
- Prototypers - rapid iteration, validate ideas fast
- Those who can steer agents best - the new superpower

The skill: knowing what to ask and when to course-correct

7. Glimpses of the Future - Product Builders

SWE, PM, ML → Agent Tech Leads. The role is shifting! Engineers become orchestrators of AI agents, product managers define agent behavior specs, and ML engineers tune agent capabilities. The new job title emerging: Agent Tech Lead - someone who can steer multiple coding agents to deliver features.

[atl-1.png]

https://kyrylai.com/2025/12/23/becoming-an-aiagent-tech-lead/

### Glimpses of the Future

8. Glimpses of the Future - Generative UI

Each app becomes a platform! Instead of static interfaces, apps will generate custom UIs on the fly based on user needs. Google's research shows how prompts can create rich, custom, visual, interactive user experiences. No more one-size-fits-all interfaces - every user gets their own tailored experience.

[gui-1.png]

https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/

9. Glimpses of the Future - Self-Driving SaaS

Software builds itself! Linear is pioneering this with their self-driving approach - the software understands what needs to be done and executes autonomously. Imagine SaaS products that don't just run your business, but improve themselves, fix bugs, and add features based on your usage patterns.

[linear-2.png]

https://linear.app/now/self-driving-saas

10. Glimpses of the Future - Product Building = Multiplayer RTS

Building products now feels like playing a real-time strategy game! You're the commander, agents are your units. You allocate resources (context, prompts), deploy agents to different fronts (features, bugs, tests), and coordinate the attack. The best builders will be those who master this multiplayer orchestration.

[sc-1.png]

11. Glimpses of the Future - Cloud Agent SDK Explosion

Every major cloud provider is shipping agent SDKs! Anthropic's Claude Agent SDK, OpenAI's Agents API, Google's Agent Development Kit, AWS Bedrock Agents. This is the new cloud wars battleground. Just like we had the container/kubernetes explosion, we're now seeing the agent SDK explosion. The primitives are being built right now.

[claude-1.png]

https://www.youtube.com/watch?v=TqC1qOfiVcQ


### Where to start!

12. Where to Start

If you are non-technical but want to build, where to start? There are 3 tiers!

Tier 1. Prototype & Vision

<>

Tier 2. More Impact

<>

Tier 3. Direct Contributing

<> 

[tiers-1.png]

And remember, everyone can build!


13. Actual blog post! 


## Reading list: 

https://builders.ramp.com/post/why-we-built-our-background-agent
https://www.benedict.dev/closing-the-software-loop
https://www.greptile.com/blog/ai-code-review-bubble
https://openai.com/index/unrolling-the-codex-agent-loop/
https://zed.dev/blog/on-programming-with-agents

https://simonwillison.net/2026/Jan/19/scaling-long-running-autonomous-coding/
https://simonwillison.net/2026/Jan/12/claude-cowork/
https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
https://blog.silennai.com/claude-code
https://www.oneusefulthing.org/p/claude-code-and-what-comes-next
