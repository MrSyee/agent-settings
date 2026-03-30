# Boulder State — Session Continuity

The boulder is the state you carry between sessions. It tracks which plan is active, what's completed, and what's in progress — so work can resume seamlessly after a context loss or session restart.

---

## `/start-work {plan-name}`

This command does two things depending on state:

### If boulder exists for this plan

Resume from where you left off:
1. Read `.sisyphus/boulder.json`
2. Read `.sisyphus/plans/{plan-name}.md`
3. Find remaining unchecked `- [ ]` tasks
4. Spawn Atlas to continue execution

### If no boulder exists

Initialize a new execution session:
1. Verify `.sisyphus/plans/{plan-name}.md` exists
2. Create `.sisyphus/boulder.json`
3. Spawn Atlas to start execution from the beginning

---

## Boulder File Format

`.sisyphus/boulder.json`:

```json
{
  "plan": "plan-name",
  "plan_path": ".sisyphus/plans/plan-name.md",
  "started_at": "2024-01-15T10:30:00Z",
  "last_active": "2024-01-15T14:22:00Z",
  "status": "in_progress",
  "completed_tasks": [1, 2, 3],
  "current_task": 4,
  "failed_tasks": [],
  "notepad_path": ".sisyphus/notepads/plan-name/",
  "session_notes": "Wave 1 complete. Auth middleware done. Starting API routes in Wave 2."
}
```

Fields:
- `plan` — the plan slug (matches filename without .md)
- `status` — `in_progress` | `completed` | `blocked`
- `completed_tasks` — task numbers that have been checked off
- `current_task` — task number currently in progress (null if between waves)
- `failed_tasks` — task numbers that failed after 3 retries
- `session_notes` — freeform notes for context recovery

---

## Resuming a Session

When `/start-work` is called with an existing boulder:

1. Read boulder.json to understand current state
2. Read plan file to get full task list
3. Check plan's `- [x]` checkboxes — these are the ground truth (not boulder.json, which may be stale)
4. Find the first unchecked `- [ ]` task
5. Read notepad learnings.md for accumulated wisdom
6. Continue Atlas execution from there

**The plan file is ground truth.** If boulder.json says task 4 is complete but the plan still shows `- [ ]`, trust the plan.

---

## `/handoff` — Session Handoff

When you need to hand off to a new session (context limit approaching, or explicit request):

See `references/03-session/handoff.md` for the handoff document format.

The handoff creates a snapshot in `.sisyphus/handoffs/{timestamp}.md` that a fresh Claude instance can pick up to continue the work.

---

## Directory Structure

```
.sisyphus/
  boulder.json              # Active session state
  plans/
    {name}.md               # Work plans (checkboxes are ground truth)
  notepads/
    {name}/
      learnings.md          # Accumulated wisdom
      decisions.md          # Architectural choices
      issues.md             # Encountered problems
      problems.md           # Unresolved blockers
  drafts/
    {topic-slug}.md         # Interview drafts (deleted after plan generation)
  evidence/
    task-{N}-{slug}.{ext}   # QA evidence per task
    final-qa/               # Final verification wave evidence
  handoffs/
    {timestamp}.md          # Session handoff documents
```

---

## State Recovery Scenarios

### Scenario: Fresh start after context loss

1. Check if `.sisyphus/boulder.json` exists
2. If yes: read it, check plan for remaining tasks, resume
3. If no: treat as fresh `/start-work`

### Scenario: Plan partially complete, new session

```
/start-work {name}
```

Atlas will automatically pick up from the last unchecked task.

### Scenario: Stuck on a failed task

1. Check `.sisyphus/notepads/{name}/problems.md` for documented failures
2. Address the root cause manually or via targeted agent
3. Then run `/start-work {name}` to continue remaining tasks

### Scenario: Need to restart entirely

Delete boulder.json and re-run `/start-work {name}`. Atlas will start from task 1 (but completed checkboxes in the plan are preserved — edit them back to `- [ ]` if you want a true restart).
