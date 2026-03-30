# Verification & Diagnostics Reference

## Evidence Requirements by Task Type

Every task type has a required evidence standard. A task is not complete without it.

### File Edits

```
// After editing any TypeScript/JavaScript file
mcp__ide__getDiagnostics  // must be clean on changed files
```

If diagnostics show errors:
- Errors YOU caused → fix before marking complete
- Pre-existing errors → note them explicitly, do not fix unless asked:
  ```
  Done. Note: found 3 pre-existing TypeScript errors in auth.ts unrelated to my changes.
  ```

### Build Commands

```bash
# Run the project's build command if it exists
npm run build
# or
pnpm build
# or
bun run build
```

Exit code must be 0. If non-zero, investigate and fix errors you caused.

### Tests

```bash
# Run relevant tests, not the entire suite unless needed
npm test -- --testPathPattern=auth
# or
pnpm test src/api/auth.test.ts
```

- Tests pass → done
- Tests fail on code YOU changed → fix
- Tests were already failing before your change → note it, don't fix unless asked

### Delegation Results

After a subagent completes:
1. Read its output with `TaskOutput`
2. Check: did it accomplish the stated goal?
3. Check: did it follow MUST DO / MUST NOT DO?
4. If incomplete → send follow-up to same agent (continuation)
5. If broken → send fix request to same agent

## Diagnostics Patterns

### When to Run Diagnostics

- After completing a logical unit of work
- Before marking a task item `completed`
- Before reporting to user that you're done
- After any file edit that touches types or imports

### Reading Diagnostics Output

Focus on:
- **Errors** (severity: error) → must fix if caused by your changes
- **Warnings** on changed files → fix if straightforward, skip if pre-existing
- Ignore: warnings in untouched files, node_modules errors

### Common Diagnostic Issues After Edits

| Symptom | Likely cause | Fix |
|---|---|---|
| "Cannot find module" | Missing import or wrong path | Check the actual file path |
| "Property X does not exist on type Y" | Type mismatch | Read the type definition, don't use `as any` |
| "Object is possibly undefined" | Unhandled null case | Add null check or use optional chaining |
| "Argument of type X is not assignable to Y" | Wrong type passed | Fix the call site or the type |

## Git Safety

Before making significant changes to existing code:

```bash
git status          # know what's already modified
git stash           # if you need a clean slate for testing
git diff            # review your own changes before reporting done
```

Never commit unless the user explicitly asks.

If something goes badly wrong after 3 failures:
```bash
git checkout -- src/path/to/file.ts   # revert single file
git stash                              # revert all changes to last commit
```

## Completion Checklist

Before telling the user you're done:

```
[ ] All planned tasks marked completed
[ ] mcp__ide__getDiagnostics clean on changed files
[ ] Build passes (if build command exists)
[ ] Tests pass (if tests were touched or relevant)
[ ] No background agents still running (cancel with TaskStop if needed)
[ ] Pre-existing issues (if any) noted in completion message
```
