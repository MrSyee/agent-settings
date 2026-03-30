# Ultrawork — Autonomous Full-Stack Execution

**Trigger**: User says `ultrawork` or `ulw`

Ultrawork is for when the user has a task they want done without the overhead of an explicit planning interview. You take the request and execute it autonomously — research, plan, implement, verify — without stopping to ask for approval.

---

## When to Use Ultrawork

- User says "ultrawork" or "ulw" explicitly
- Complex task where explaining context would be tedious
- User clearly trusts you to figure out the approach
- Task is self-contained enough that you can define acceptance criteria yourself

**Not appropriate for:**
- Tasks with genuine ambiguity about what success looks like
- Tasks touching critical infrastructure (auth, payments, data migrations)
- Tasks where the user has strong opinions about approach you haven't heard yet

---

## Ultrawork Execution

### Step 1: Verbalize intent and start immediately

```
I detect [intent type] — [reason]. Full autonomous execution.
Approach: [1-2 sentences on strategy].
```

No acknowledgments. No "I'll get started." Just state intent and begin.

### Step 2: Parallel codebase research

Fire 2-5 explore agents in parallel to understand the terrain:

```
Agent(subagent_type="explore", run_in_background=true,
  prompt="[CONTEXT]: About to implement [feature].
  [GOAL]: Understand existing patterns to follow exactly.
  [REQUEST]: Find similar implementations — file structure, naming,
  public API exports, error handling, registration steps.
  Return concrete file paths and patterns.")

Agent(subagent_type="explore", run_in_background=true,
  prompt="[CONTEXT]: Implementing [feature], need to know test coverage.
  [GOAL]: Understand what tests exist and what patterns to follow.
  [REQUEST]: Find test files for similar features — assertion style,
  mock patterns, test organization. Return the canonical test structure.")
```

If external technology is involved, add a librarian agent.

### Step 3: Build a quick plan (internal, not a .sisyphus/plans/ file)

From research results, create a mental map:
- What tasks, in what order
- What can run in parallel
- What the acceptance criteria are (you define them from the request)

Use `TaskCreate` to track steps:
```
TaskCreate(subject="[Step 1 description]")
TaskCreate(subject="[Step 2 description]")
...
```

### Step 4: Execute directly or via delegation

For each step:
- **Trivial** (single file, obvious change) → execute directly with Read + Edit
- **Non-trivial** → delegate to `sisyphus-junior` with full 6-section prompt (see `references/02-execution/delegation-template.md`)

Mark each task in_progress before starting, completed immediately after.

### Step 5: Verify as you go

After each significant change:
```
mcp__ide__getDiagnostics  → clean on changed files
```

After all changes:
```
Bash(build command)  → exit code 0
Bash(test command)   → all pass
```

### Step 6: Complete

```
Done. [What was changed, 1-2 sentences.]
[Optional: pre-existing issues found but not fixed.]
```

No summary of every file touched. No explanation of code.

---

## Ultrawork vs @plan

| | Ultrawork | @plan |
|---|---|---|
| **Trigger** | `ulw` / `ultrawork` | `@plan [task]` |
| **Interview** | None — you define approach | Prometheus conducts interview |
| **Plan file** | No persistent plan file | `.sisyphus/plans/{name}.md` |
| **Good for** | Well-understood task, trust me to figure it out | Complex task needing precise planning |
| **Session resume** | No boulder state | `/start-work` resumes |

---

## Failure Recovery in Ultrawork

After 3 consecutive failures on the same issue:
1. Stop all edits
2. `Bash("git stash")` or `git checkout -- {file}` to revert
3. Spawn oracle with full failure context
4. If oracle can't resolve → ask user before proceeding

Never: leave code broken, continue hoping it'll work, delete failing tests.
