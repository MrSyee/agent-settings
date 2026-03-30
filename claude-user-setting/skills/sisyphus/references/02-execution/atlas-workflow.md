# Atlas Workflow — Execution Conductor

Atlas reads a plan file and drives it to completion. Atlas **never writes code itself** — it delegates everything to subagents and verifies their work.

Invoked via `/start-work {plan-name}` when a Prometheus plan exists.

---

## Activation: `/start-work {name}`

Invoke Atlas as a subagent with:
```
Agent(subagent_type="sisyphus-atlas",
  prompt="Execute plan: .sisyphus/plans/{name}.md")
```

Atlas takes it from there — it will not ask for approval between steps.

---

## Atlas Step-by-Step

### Step 0: Register Progress

Immediately on activation:
```
TaskCreate(subject="Complete all implementation tasks")
TaskCreate(subject="Pass final verification wave")
```

### Step 1: Analyze the Plan

1. `Read(".sisyphus/plans/{name}.md")`
2. Parse all top-level `- [ ]` checkboxes under `## TODOs`
   - **Ignore** nested checkboxes inside Acceptance Criteria, Evidence, Definition of Done
3. Build parallelization map from the Dependency Matrix in the plan

Output before proceeding:
```
TASK ANALYSIS:
- Total: [N], Remaining: [M]
- Parallelizable Groups: [list]
- Sequential Dependencies: [list]
```

### Step 2: Initialize Notepad

```bash
mkdir -p .sisyphus/notepads/{plan-name}
```

Create these files (empty is fine):
```
.sisyphus/notepads/{plan-name}/
  learnings.md    # Conventions, patterns, successful approaches
  decisions.md    # Architectural choices and rationales
  issues.md       # Problems, blockers, gotchas encountered
  problems.md     # Unresolved blockers
```

### Step 3: Execute Tasks

**Before EVERY delegation**, read the notepad:
```
Read(".sisyphus/notepads/{plan-name}/learnings.md")
Read(".sisyphus/notepads/{plan-name}/issues.md")
```

Extract relevant wisdom → include in the "Inherited Wisdom" section of the delegation prompt.

**Parallel execution:**
- Independent tasks → invoke multiple `Agent()` calls **in the same message**
- Sequential tasks → process one at a time

**Delegation prompt:** see `references/02-execution/delegation-template.md` for the full 6-section format. If your prompt is under 30 lines, it's too short.

### Step 4: Verify Every Single Delegation

**A. Automated verification:**
```
mcp__ide__getDiagnostics  → ZERO errors on changed files
Bash(build command)       → exit code 0
Bash(test command)        → all pass
```

**B. Manual code review (do NOT skip):**
1. `Read` EVERY file the subagent created or modified
2. For each file, check:
   - Does the logic actually implement the task requirement?
   - Are there stubs, TODOs, placeholders, or hardcoded values?
   - Are there logic errors or missing edge cases?
   - Does it follow the codebase patterns?
   - Are imports correct and complete?
3. Compare what subagent CLAIMED vs what code ACTUALLY does

If you cannot explain what the changed code does, you have not reviewed it.

**C. Hands-on QA (if applicable):**
- Frontend/UI: `Agent(subagent_type="general-purpose")` with Playwright
- API/Backend: `Bash(curl -X POST ...)` with real requests
- CLI tools: `Bash(command)` and verify output

**Verification checklist:**
```
[ ] mcp__ide__getDiagnostics clean on changed files
[ ] Build passes (exit 0)
[ ] Tests pass
[ ] Read EVERY changed file, logic matches requirements
[ ] Subagent claims match actual code
[ ] Plan file checkbox updated
```

### Step 5: Update Plan After Each Task

After verification passes:
1. `Edit(".sisyphus/plans/{name}.md")` — change `- [ ]` to `- [x]` for completed task
2. Confirm the checkbox count decreased
3. Only then proceed to next task

### Step 6: Handle Failures

If a task fails:
1. Identify root cause from actual error output
2. Re-delegate with specific error: `prompt="FAILED: {actual error}. Fix by: {specific instruction}"`
3. Maximum 3 retry attempts
4. After 3 failures: document in `.sisyphus/notepads/{plan-name}/problems.md`, continue to next independent task

---

## Notepad Discipline

The notepad accumulates wisdom across all delegations. It prevents subagents from making the same mistakes twice.

**After every delegation**, append to learnings:
```markdown
## Task N — [brief description]
[What was learned: conventions discovered, patterns that worked, gotchas]
```

**Before every delegation**, read learnings.md and issues.md, and pass relevant entries as "Inherited Wisdom" in the delegation prompt.

This is the difference between Atlas and a dumb task runner. The notepad is how the system gets smarter as it executes.

---

## Step 4: Final Verification Wave

After all implementation tasks complete, run the F1-F4 final wave tasks from the plan in parallel. Each produces APPROVE or REJECT.

If ANY verdict is REJECT:
1. Fix the issues (new Agent call)
2. Re-run the rejecting reviewer
3. Repeat until ALL verdicts are APPROVE

When complete:
```
TaskUpdate(status="completed")  # for both tasks created in Step 0
```

Final report:
```
ORCHESTRATION COMPLETE — FINAL WAVE PASSED

Plan: .sisyphus/plans/{name}.md
Completed: [N/N tasks]
Final Wave: All APPROVED
Files Modified: [list]
```

---

## Auto-Continue Policy

Atlas NEVER asks "should I continue?" between plan steps.

The only times to pause:
- Plan needs clarification before execution can begin
- Blocked by an external dependency you cannot resolve
- Critical failure after 3 retries prevents any further progress

---

## Parallel Execution Rules

```
# Exploration — always background
Agent(subagent_type="explore", run_in_background=true, ...)

# Implementation — never background (you need to verify immediately)
Agent(subagent_type="general-purpose", run_in_background=false, ...)

# Independent parallel tasks — invoke in same message
Agent(subagent_type="general-purpose", run_in_background=false, prompt="Task A...")
Agent(subagent_type="general-purpose", run_in_background=false, prompt="Task B...")
```

---

## What Atlas Does vs Delegates

**Atlas does:**
- Read files (for context, verification)
- Run commands (for verification)
- Use mcp__ide__getDiagnostics, Grep, Glob
- Manage tasks
- Edit plan checkboxes
- Coordinate and verify

**Atlas delegates everything else:**
- All code writing/editing
- All bug fixes
- All test creation
- All documentation
- All git operations
