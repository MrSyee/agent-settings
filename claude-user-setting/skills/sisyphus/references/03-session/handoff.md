# Handoff — Session Continuity Document

Use `/handoff` when a session is ending and you need a fresh Claude instance to continue the work. This creates a document that fully reconstructs the working context.

---

## When to Use

- Context window is getting full
- Session needs to pause and continue tomorrow
- Passing work to a different assistant
- Creating a checkpoint before a risky operation

---

## Handoff Document Format

Generated to `.sisyphus/handoffs/{timestamp}.md`:

```markdown
# Handoff — {Plan Name} — {timestamp}

## Status Summary
- **Plan**: `.sisyphus/plans/{name}.md`
- **Overall Progress**: {N}/{M} tasks complete
- **Current State**: {in_progress | blocked | between_waves}
- **Next Action**: {exactly what to do to continue}

## What Was Accomplished This Session
- Task N: [what was done, what files changed]
- Task M: [what was done, what files changed]

## What Remains
- [ ] Task X: [brief description]
- [ ] Task Y: [brief description]
- [ ] Task Z: [brief description]

## Active Context (don't re-explore this)

### Codebase Conventions Discovered
- [Convention 1]: [location] — [what it is]
- [Convention 2]: [location] — [what it is]

### Decisions Made
- [Decision 1]: [what was decided and why]
- [Decision 2]: [what was decided and why]

### Problems Encountered
- [Problem 1]: [what failed, how it was resolved or why it's blocked]

### Files Changed This Session
- `src/file1.ts` — [what changed]
- `src/file2.ts` — [what changed]

## How to Resume

1. Read the plan: `Read(".sisyphus/plans/{name}.md")`
2. Read the notepad: `Read(".sisyphus/notepads/{name}/learnings.md")`
3. Find first unchecked `- [ ]` task
4. Run: `/start-work {name}`

Or continue manually from task X with the context above.

## Warnings / Watch Out For
- [Any gotcha the next session needs to know]
- [Any partially complete state that needs attention]
- [Any external dependencies that were blocked]
```

---

## Generating a Handoff

When the user runs `/handoff`:

1. Read `.sisyphus/boulder.json` for current state
2. Read `.sisyphus/plans/{name}.md` for task progress
3. Read `.sisyphus/notepads/{name}/learnings.md` for accumulated wisdom
4. Read git diff to list files changed this session
5. Write the handoff document to `.sisyphus/handoffs/{timestamp}.md`
6. Update boulder.json with `last_active` timestamp and `session_notes`

Output to user:
```
Handoff document saved to `.sisyphus/handoffs/{timestamp}.md`

Progress: {N}/{M} tasks complete
Next: Task {X} — {description}

To resume: Run `/start-work {name}` in a new session, or share the handoff document.
```
