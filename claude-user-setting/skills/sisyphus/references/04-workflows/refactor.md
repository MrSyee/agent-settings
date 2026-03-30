# Refactor Workflow — Safe Codebase Refactoring

**Trigger**: `/refactor [target]`

Refactoring is the highest-risk category of code change because it modifies structure without (ideally) changing behavior. One missed call site = a broken production system. This workflow enforces the discipline that prevents regressions.

**Rule #1: Never change behavior while restructuring. One PR, one concern.**

---

## Phase 0: Pre-Refactor Safety Check

Before writing a single character, establish your safety net.

### 1. Map all usages

```
Agent(subagent_type="explore", run_in_background=true,
  prompt="[CONTEXT]: About to refactor [target].
  [GOAL]: Map every usage to identify regression risk.
  [REQUEST]: Find all call sites via mcp__serena__find_referencing_symbols.
  For each: file path, how return value is used, type flow,
  patterns that would break on signature changes.
  Also search for dynamic access patterns (string-based, computed properties)
  that symbol search might miss.
  Risk level per call site: high (direct coupling) / medium (indirect) / low (type only).
  Return: complete call site map with risk levels.")

Agent(subagent_type="explore", run_in_background=true,
  prompt="[CONTEXT]: About to refactor [target], need to know test coverage.
  [GOAL]: Decide whether current tests provide enough safety net.
  [REQUEST]: Find ALL test files that exercise [target] code —
  unit tests, integration tests, e2e tests.
  For each test: what behavior it asserts, what inputs it uses,
  whether it tests public API or internals.
  Coverage gaps: behaviors exercised in production but not in tests.
  Return: tested behaviors map + coverage gap list.")
```

### 2. Establish baseline

Before touching anything:
```bash
# Run current tests — record output
bun test 2>&1 | tee .sisyphus/refactor-baseline.txt

# Or for TypeScript:
tsc --noEmit 2>&1 | tee .sisyphus/refactor-ts-baseline.txt
```

This is your before-state. After each change, you'll compare against it.

### 3. Classify risk

From the usage map:
- **High risk** call sites: require careful attention, test coverage verification
- **Medium risk**: update in same PR, verify
- **Low risk**: type-only usage, rename is safe

---

## Phase 1: Plan the Refactor

Structure the refactor as atomic steps. Each step should be independently verifiable.

Example for renaming `getUserData` → `fetchUserProfile`:
```
Step 1: Rename the function definition
Step 2: Update call sites in src/api/ (5 files)
Step 3: Update call sites in src/workers/ (2 files)
Step 4: Update test files (3 files)
Step 5: Verify full test suite
```

**Never do all at once.** Atomic steps mean if something breaks, you know exactly where.

---

## Phase 2: Execute with Serena

For symbol renames, **always use `mcp__serena__rename_symbol`** — never manual search/replace.

```
mcp__serena__rename_symbol(
  symbol_name="getUserData",
  new_name="fetchUserProfile",
  relative_path="src/services/user.ts"
)
```

Why: Serena understands the AST. It handles:
- Export renames
- Import statement updates
- Re-export patterns
- Type references
- JSX usage

Manual search/replace will miss dynamic patterns and leave the codebase in an inconsistent state.

### For structural changes (not renames)

Make changes in smallest possible increments:
1. Add the new structure alongside the old (if non-destructive)
2. Update call sites one module at a time
3. Remove the old structure last
4. Verify after each step

```
# After each step:
mcp__ide__getDiagnostics  → must be clean before proceeding
```

---

## Phase 3: Verify at Every Step

After EACH step (not just at the end):

```
mcp__ide__getDiagnostics  → zero errors on changed files
bun test [affected test files]  → no new failures
```

Compare against baseline:
```bash
bun test 2>&1 | diff .sisyphus/refactor-baseline.txt -
```

**Any new failure = STOP.** Revert the last step. Understand why before proceeding.

---

## Phase 4: Final Verification

After all steps:

```bash
# Full test suite
bun test

# TypeScript compilation
tsc --noEmit

# If applicable:
bun build
```

All must match or improve on baseline.

---

## Bugfix Rule (Critical)

When you find a bug while refactoring:
1. Note it
2. **Finish the refactor first**
3. **Then fix the bug in a separate commit**

Never mix refactoring and bug fixing. This makes git history unreadable and makes it impossible to bisect regressions.

---

## Common Refactoring Patterns

### Rename symbol

```
mcp__serena__rename_symbol(symbol_name="oldName", new_name="newName", relative_path="src/file.ts")
```

### Move file (rename path)

1. Create new file at new location (copy content)
2. Update all imports via Bash + Edit (or serena if available)
3. Delete old file
4. Verify with mcp__ide__getDiagnostics

### Extract function

1. Identify the code to extract
2. Create new function with explicit parameter and return types
3. Replace original code with function call
4. Verify behavior is identical (same tests pass)

### Change function signature

This is the highest-risk refactor. Steps:
1. Add overload with new signature (TypeScript) OR add new function alongside old
2. Update call sites one at a time, verifying after each batch
3. Remove old signature/function once all call sites updated
4. Never break the build between steps — keep old signature working until all call sites are updated

---

## If Something Breaks

After 3 consecutive failures:
1. `git stash` or `git checkout -- {files}` — revert to baseline
2. Re-read the usage map
3. Spawn oracle with the failure context
4. Try a different approach

Never push through a broken state. Refactors that don't pass tests are worse than no refactor at all.
