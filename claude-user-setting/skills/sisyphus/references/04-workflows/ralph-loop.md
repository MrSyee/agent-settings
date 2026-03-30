# Ralph Loop — Self-Referential Execution Loop

**Trigger**: `/ralph-loop [goal]`

The ralph loop runs until a goal is achieved. It executes → evaluates → adjusts → repeats. Named for the self-referential nature: you keep pushing until it works.

---

## When to Use

- Iterative tasks where the end state isn't deterministic (e.g., "get all tests passing")
- Tasks that require multiple rounds of fix-verify-fix
- Exploratory implementation where you learn the requirements as you go
- Any task where "done" means a condition becomes true, not a checklist completes

---

## Loop Structure

```
while NOT goal_achieved:
    1. Assess current state
    2. Identify the most impactful next action
    3. Execute that action
    4. Verify outcome
    5. Update understanding
```

### Step 1: Define the Goal Condition

Before starting, make the goal concrete and verifiable:

```
Goal: [what condition is true when done]
Verification: [exact command that proves it]
```

Examples:
- Goal: All tests pass. Verification: `bun test` exits 0.
- Goal: TypeScript compiles clean. Verification: `tsc --noEmit` exits 0.
- Goal: Feature X works end-to-end. Verification: [specific curl command or Playwright scenario].

### Step 2: Initial State Assessment

```
Agent(subagent_type="explore", run_in_background=true,
  prompt="[CONTEXT]: Starting ralph-loop to achieve [goal].
  [GOAL]: Understand current state to know where to start.
  [REQUEST]: [specific things to find that reveal current state]")
```

### Step 3: Execute-Verify Loop

Each iteration:
1. Run verification → check if goal achieved → if yes, done
2. Identify the single most impactful thing to fix
3. Fix it (directly or via delegation)
4. Run verification again
5. Repeat

**Focus on one thing at a time.** Don't try to fix multiple issues in one iteration — you'll lose the signal on what worked.

### Step 4: Progress Tracking

Use TaskCreate for the loop objective and update as you go:
```
TaskCreate(subject="Achieve: [goal condition]")
TaskCreate(subject="Iteration [N]: [specific action]")
```

### Step 5: Exit Conditions

**Success**: Verification command confirms goal achieved.

**Stuck**: Same failure appearing after 3+ iterations despite different approaches. Options:
1. Spawn oracle with full failure history
2. Ask user for guidance
3. Document blocker and exit loop

**Over-budget**: If the loop has run 10+ iterations without meaningful progress, stop and escalate.

---

## Anti-Patterns

- **Thrashing**: Undoing and redoing the same changes across iterations
- **Symptom fixing**: Making tests pass by weakening assertions rather than fixing code
- **Scope creep**: Fixing things not related to the current goal
- **Invisible progress**: Making changes without running verification

---

## Example

```
/ralph-loop get all tests passing

Goal: `bun test` exits 0 with 0 failures
Current: 12 failures

Iteration 1:
  - Run: `bun test` → 12 failures
  - Analyze: 8 failures are in auth.test.ts, all same error: "Cannot read property 'userId' of undefined"
  - Fix: UserService.getUser() returns null for missing users, not undefined — update test mocks
  - Verify: `bun test src/auth.test.ts` → 0 failures

Iteration 2:
  - Run: `bun test` → 4 failures
  - Analyze: 4 failures in payment.test.ts — "PaymentService not in container"
  - Fix: PaymentService registration missing from test setup in beforeAll
  - Verify: `bun test src/payment.test.ts` → 0 failures

Iteration 3:
  - Run: `bun test` → 0 failures
  - Goal achieved. Done.
```
