## Goal: 

I want to build products fast! 
I want to use multiple agents to do this for me! 
I would prioritese simplicity and testing insatead pre-build features. 
I run 10s or maybe 100s of agents in cloud in parallel without them stepping on each oterhe foot! 

Long story short - I want to accelerate 
https://www.amazon.ca/Accelerate-Software-Performing-Technology-Organizations/dp/1942788339


How could I do this? 


## Stack:


TS + Vite for UI 
Python + FastAPI for API 
Supabase for Auth
Supabase for DB
Railway for Platform
Modal for ML 
Dagster for Jobs

And most importanta - AI engineerign first! What do I mean by this? 


## AI engineerign first

- Feature branches 
- Bullet proff testing
- Subgoal: run 10 agents in parallel 
- Anyone can edit it: slack, agetns, non tech 


## Studies 

https://developers.openai.com/codex/guides/build-ai-native-engineering-team/
https://linear.app/now/self-driving-saas


## 10 agents in parallel: 

1. Plan
2. Design
3. Build
4. Test
5. Review
6. Document
7. Deploy and Maintain





Keep only @ai-product-template context; everything else is irrelevant for this project.
Keep code simple and minimal, prioritizing maintainability and elegant solutions. The less code we have, the better we can support it.

I want you to implement the next feature:

Let's plan first!
1. Test for frontend + CI/CD to run them
2. Test for API + CI/CD to run them
3. User support for each item + auth with Supabase
4. Ruff style check + CI/CD to run it
5. TS style check + CI/CD to update it
6. Feature 1: Show how the API is connected
7. Feature 2: Some mock data
8. Docker-compose to run on-prem
9. Agentic feature + tests for it from API + UI
10. Settings page for user with placeholders


## History: 

git commit -m "0. init app"
git commit -m "1. api"
git commit -m "2. connect api and app"
git commit -m "3. sidebar"
git commit -m "4. add api"
git commit -m "5. feature branches"

git push origin ai-product-template


Please add a minimal sidebar to my app, just as a placeholder for now.

See screenshots of sidebars I really like. I really like the following structure:

Main page
<HOME>

Dedicated for each feature / agent / product / screen
<Features>

Admin section to manage users, payments, etc.
<Admin>


Remember to keep it minimal and simple.

The admin section should be at the bottom of the sidebar, please.

I use the Railway platform to deploy both the API and the app. It works like this: 
- Detect what the app is
- Build an internal Docker image 
- Run

For the app, I think it uses `npm build` or something similar. My point is that `VITE_API_URL` probably won't be read dynamically, because `npm build` creates static files.

This might be a problem because I want to:

- Have different environments
- Have feature branches where, for each PR, I create a new environment: API + app, and `VITE_API_URL` should be set up dynamically