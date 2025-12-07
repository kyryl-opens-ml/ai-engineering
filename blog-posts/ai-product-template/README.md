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
Sentry for monitoring

And most importanta - AI engineerign first! What do I mean by this? 



## AI engineerign first

- Feature branches 
- Bullet proff testing
- Subgoal: run 10 agents in parallel 
- Anyone can edit it: slack, agetns, non tech 


## Studies 

https://developers.openai.com/codex/guides/build-ai-native-engineering-team/
https://linear.app/now/self-driving-saas


## TODO: 


1. Auth feature:
Keep only @ai-product-template context; everything else is irrelevant for this project.
Keep code simple and minimal, prioritizing maintainability and elegant solutions. The less code we have, the better we can support it.

I want you to implement the next feature:

User authentication and management

First:

- Authenticate users with Supabase.
- There are 3 objects: user, workspace, items.
  - User: self-explanatory.
  - Workspace: something a user owns; a user can create several.
  - Item: something a user owns that belongs to one workspace.
- A user can add other users to a workspace so they can see the workspace and its items.



- test manually 
- test api 
- test ui
- test end2end in github actions with supabase 


2. Agent feature:

3. Story

4. Stack

5. Verify

6. Reality check.


7. Grammar & movement & review 



Keep only @ai-product-template context; everything else is irrelevant for this project.
Keep code simple and minimal, prioritizing maintainability and elegant solutions. The less code we have, the better we can support it.

I want you to implement the next feature:

Let's plan first!


1. Auth features: 

1. Test for frontend + CI/CD to run them: DONE
2. Test for API + CI/CD to run them: DONE

3. Add auth with Supabase - make sure each user has it's own resourses 
6. Feature 1: Show how the API is connected
7. Feature 2: Some mock data
8. Docker-compose to run on-prem
9. Agentic feature + tests for it from API + UI
Agentic feature - let's use 
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