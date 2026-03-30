# Subagent Delegation Reference

## When to Use Each Subagent Type

| Subagent | Use for | Don't use for |
|---|---|---|
| `Explore` | Codebase grep, finding patterns, understanding existing code structure | External docs, writing code |
| `general-purpose` | Complex implementation, external research, multi-step tasks | Simple file reads you can do directly |
| `Plan` | Designing architecture, thinking through trade-offs before implementing | Quick tasks, already-clear plans |

## Explore Agent — Codebase Grep

Explore is a fast, read-only codebase searcher. Use it like a smart grep, not a consultant.

**Always run in background. Always parallel.**

Good Explore prompts are specific and tell the agent exactly what to skip:

```
[CONTEXT]: I'm implementing rate limiting middleware for src/api/middleware/.
I need to match existing middleware conventions exactly so it integrates cleanly.
[GOAL]: Understand how existing middleware is structured and registered.
[REQUEST]: Find: middleware files in src/api/middleware/, how they're exported and registered
in the app, any existing rate-limit or auth middleware as reference. Skip test files and node_modules.
Return file paths, key function signatures, and registration pattern.
```

**Bad Explore prompts (too vague):**
```
Find the middleware code.
```

## General-Purpose Agent — Research & Complex Implementation

Use for:
- Looking up external documentation or library APIs
- Implementing features that span multiple files
- Tasks that require writing AND reading code together

**When delegating implementation, include all 6 sections:**

```
TASK: Add a POST /api/users endpoint that creates a user in the database.

EXPECTED OUTCOME: A working endpoint at src/api/routes/users.ts that:
- Validates email and password fields
- Hashes the password with bcrypt
- Saves to the users table
- Returns 201 with the new user (no password field)
- Returns 400 for validation errors

REQUIRED TOOLS: Read, Edit, Write, Bash (for running tests only)

MUST DO:
- Follow the existing route pattern in src/api/routes/posts.ts
- Use the existing db utility at src/lib/db.ts
- Add input validation using zod (already a dependency)
- Include error handling matching the pattern in src/api/middleware/error-handler.ts

MUST NOT DO:
- Do not add new dependencies
- Do not modify any existing files except src/api/routes/users.ts
- Do not add authentication (that's a separate task)
- Do not commit

CONTEXT:
- Existing route example: src/api/routes/posts.ts
- DB utility: src/lib/db.ts (has query(), transaction() helpers)
- Error format: { error: string, code: string }
- Zod validation example: src/api/routes/auth.ts lines 12-28
```

## Plan Agent — Architecture Consultation

Use before implementing something complex or unfamiliar.

```
Agent(subagent_type="Plan",
  prompt="I need to add real-time notifications to a Next.js app.
  Current stack: Next.js 14, PostgreSQL, Prisma.
  Options I'm considering: WebSockets, SSE, polling.
  Please design the implementation approach considering:
  - Scalability (currently single server, may go multi)
  - Complexity vs benefit
  - Integration with existing Prisma models
  Return a step-by-step implementation plan.")
```

## Parallelization Patterns

### Pattern 1: Parallel Exploration
Fire multiple Explore agents in the same turn for different aspects of the codebase:

```
// Same turn — fires simultaneously
Agent(subagent_type="Explore", run_in_background=true, prompt="Find auth patterns...")
Agent(subagent_type="Explore", run_in_background=true, prompt="Find error handling patterns...")
Agent(subagent_type="Explore", run_in_background=true, prompt="Find test file patterns...")
```

### Pattern 2: Parallel Independent Implementation
When a feature has independent frontend + backend parts:

```
// Both agents work simultaneously
Agent(subagent_type="general-purpose", run_in_background=true,
  prompt="TASK: Implement backend endpoint... [6 sections]")

Agent(subagent_type="general-purpose", run_in_background=true,
  prompt="TASK: Implement frontend component... [6 sections]")
```

### Pattern 3: Research + Implement
Research external docs while exploring codebase:

```
Agent(subagent_type="Explore", run_in_background=true,
  prompt="Find existing API client patterns in src/...")

Agent(subagent_type="general-purpose", run_in_background=true,
  prompt="Look up the Stripe API docs for subscription management.
  Find: how to create subscriptions, handle webhooks, cancel subscriptions.
  Return: API endpoints, required params, webhook event types.")
```

## Reading Background Results

When agents complete, you receive a notification. Collect results with `TaskOutput`:

1. Check which agents completed
2. Call `TaskOutput(id="...")` for each completed agent
3. Synthesize results before proceeding
4. Cancel any agents you no longer need with `TaskStop`
