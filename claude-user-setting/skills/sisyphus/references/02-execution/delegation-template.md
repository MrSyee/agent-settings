# Delegation Template — 6-Section Prompt Format

Every delegation to `sisyphus-junior` or `general-purpose` MUST include all 6 sections. **If your prompt is under 30 lines, it's too short.**

The executor has NO context from your interview or planning session. The delegation prompt is their entire world.

---

## Full Template

```markdown
## 1. TASK
[Quote the EXACT checkbox item from the plan. Be obsessively specific about what to build/change.
One atomic action per delegation — never combine unrelated work.]

## 2. EXPECTED OUTCOME
- [ ] Files created/modified: [exact paths]
- [ ] Functionality: [exact behavior — what should happen when X is called with Y]
- [ ] Verification: `[command]` passes with output `[expected string]`
- [ ] No new files outside the specified scope

## 3. REQUIRED TOOLS
- Read: Understand existing code before editing
- Edit/Write: Make the specified changes
- Bash: Run verification commands
- mcp__ide__getDiagnostics: Verify no TypeScript/lint errors after changes
- mcp__serena__find_symbol: Locate [specific symbol] before editing
- [Any other tools needed — be explicit]

## 4. MUST DO
- Follow the pattern in `[reference file:lines]`
- Run mcp__ide__getDiagnostics after all changes — must be clean
- Append findings to `.sisyphus/notepads/{plan-name}/learnings.md` (NEVER overwrite, only append)
- [Other specific requirements]

## 5. MUST NOT DO
- Do NOT modify files outside [exact scope — list specific files]
- Do NOT add dependencies not listed in this prompt
- Do NOT refactor code adjacent to your task
- Do NOT leave TODOs, stubs, or placeholder implementations
- Do NOT commit
- [Other prohibitions specific to this task]

## 6. CONTEXT
### Inherited Wisdom
[Paste relevant entries from .sisyphus/notepads/{plan-name}/learnings.md]
[Include any gotchas, conventions, or decisions from previous tasks]

### Dependencies
[What previous tasks produced that this task needs]
[e.g., "Task 1 created the User type at src/types/user.ts — use it"]

### Reference Patterns
[File paths with line numbers showing the pattern to follow]
[e.g., "Follow the service pattern in src/services/auth.ts:45-78 — JWT creation and refresh token handling"]
[e.g., "Error response shape from src/middleware/error.ts:20-35 — use this exact format"]
```

---

## Example: Adding a new API endpoint

```markdown
## 1. TASK
Implement POST /api/users/reset-password endpoint that accepts { email: string } and
sends a password reset email via the existing mailer service. Task 5 from plan: add-auth.

## 2. EXPECTED OUTCOME
- [ ] Files created: src/api/routes/reset-password.ts
- [ ] Files modified: src/api/index.ts (register the route)
- [ ] Functionality: POST /api/users/reset-password with valid email → returns 202, triggers email
- [ ] Functionality: POST /api/users/reset-password with invalid email → returns 400 with error message
- [ ] Functionality: POST /api/users/reset-password with unknown email → returns 202 (don't leak existence)
- [ ] Verification: `mcp__ide__getDiagnostics` clean on both files
- [ ] Verification: `bun test src/api/routes/reset-password.test.ts` → 3 tests, 0 failures

## 3. REQUIRED TOOLS
- Read: Read existing route files before implementing
- Write/Edit: Create and register the route
- Bash: Run `bun test src/api/routes/reset-password.test.ts` to verify
- mcp__ide__getDiagnostics: Check for type errors after changes
- mcp__serena__find_symbol: Find MailerService if you can't locate it from the reference

## 4. MUST DO
- Follow the route structure in `src/api/routes/login.ts:1-80` exactly
- Use the MailerService pattern from `src/services/mailer.ts:sendEmail()`
- Return 202 for both valid and unknown emails (security: don't reveal account existence)
- Validate email format with the existing `validateEmail` util from `src/utils/validation.ts`
- Append findings to `.sisyphus/notepads/add-auth/learnings.md`

## 5. MUST NOT DO
- Do NOT modify any file outside src/api/routes/reset-password.ts and src/api/index.ts
- Do NOT add any new npm dependencies
- Do NOT implement the actual email sending logic (use MailerService.sendEmail — it's already there)
- Do NOT return 404 for unknown emails (security requirement — always 202)
- Do NOT commit

## 6. CONTEXT
### Inherited Wisdom
From learnings.md:
- Routes follow Express Router pattern, not inline app.use()
- Error responses always use { error: string, code: string } shape (see src/middleware/error.ts:25)
- Validation happens at route level using validateInput() wrapper, not inline
- MailerService is injected via container.get(MailerService) — don't instantiate directly

### Dependencies
- Task 3 created MailerService at src/services/mailer.ts — use sendPasswordReset(email) method
- Task 4 created the User type — import from src/types/user.ts

### Reference Patterns
- Route structure: `src/api/routes/login.ts:1-80` — Router setup, middleware ordering, error handling
- Input validation: `src/api/routes/register.ts:15-30` — validateInput() pattern
- Email validation: `src/utils/validation.ts:validateEmail()` — already imported in login.ts
- Error response: `src/middleware/error.ts:20-40` — { error, code } shape with status codes
- Mailer usage: `src/services/password-change.ts:45` — sendPasswordReset example
```

---

## Example: Refactoring a function

```markdown
## 1. TASK
Rename `getUserData()` to `fetchUserProfile()` in src/services/user.ts and update all call sites.
Task 2 from plan: refactor-user-service.

## 2. EXPECTED OUTCOME
- [ ] `getUserData` renamed to `fetchUserProfile` in src/services/user.ts
- [ ] All call sites updated: src/api/routes/profile.ts, src/api/routes/dashboard.ts, src/workers/sync.ts
- [ ] No other files modified
- [ ] Verification: `mcp__ide__getDiagnostics` clean on all 4 files
- [ ] Verification: `bun test` → all pass (no new failures)

## 3. REQUIRED TOOLS
- mcp__serena__rename_symbol: Use this for the rename — it finds all references automatically
- mcp__ide__getDiagnostics: Verify clean after rename
- Bash: Run `bun test` after rename to confirm no regressions

## 4. MUST DO
- Use mcp__serena__rename_symbol for the rename — do NOT manually search-and-replace
- Run mcp__ide__getDiagnostics after rename — must be clean on all changed files
- Append findings to `.sisyphus/notepads/refactor-user-service/learnings.md`

## 5. MUST NOT DO
- Do NOT change the function signature or behavior — rename only
- Do NOT refactor any code adjacent to this function
- Do NOT modify test files (they will be updated by the rename tool automatically)
- Do NOT commit

## 6. CONTEXT
### Inherited Wisdom
From learnings.md:
- This codebase uses mcp__serena successfully — serena has the project indexed
- getUserData is exported publicly — some tests import it directly by name

### Dependencies
None — this is an independent rename task.

### Reference Patterns
- Current implementation: `src/services/user.ts:getUserData()` — the symbol to rename
```

---

## Delegation Anti-Patterns

**Too vague (will produce garbage):**
```
## 1. TASK
Fix the auth bug.
```

**Scoping too wide (produces scope creep):**
```
## 5. MUST NOT DO
Don't break anything.
```

**Missing references (executor invents patterns):**
```
## 6. CONTEXT
The project uses TypeScript and Express.
```

**The right mindset:** The executor is a smart engineer who has never seen your codebase. They need enough detail to do exactly the right thing without guessing. If something is left implicit, they will make an assumption — and it might be wrong.
