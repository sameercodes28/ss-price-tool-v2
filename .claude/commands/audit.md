# Slash Command: /audit

Run comprehensive codebase audit to prevent documentation drift and code bloat.

## What This Does

1. **Version Consistency Check** - Ensure all files reference same version
2. **Dead Code Detection** - Find TODO/FIXME/DEPRECATED comments
3. **Backup File Audit** - List temporary files in root directory
4. **Documentation Accuracy** - Verify docs match current state
5. **Generate Report** - Create actionable findings list

## How to Use

Just type `/audit` in Claude Code and I'll:
- Check for version drift
- Find orphaned code
- Identify stray backup files
- Create commit fixing issues (if you approve)

## When to Run

- ✅ After completing any feature
- ✅ Before bumping version numbers
- ✅ Monthly maintenance check
- ✅ Before major deployments

## Expected Output

```
🔍 CODEBASE AUDIT REPORT
========================

VERSION CHECK:
✅ All files show v2.4.0 (consistent)

DEAD CODE CHECK:
⚠️ Found 2 TODO comments in main.py
⚠️ Found unused CSS class .old-header

BACKUP FILES:
⚠️ test-feature.html (7 days old) - should archive
✅ index-before-cleanup.html (recent, OK to keep)

DOCUMENTATION:
✅ CHANGELOG up to date
✅ README features match codebase

ACTIONS NEEDED:
1. Archive test-feature.html
2. Remove unused CSS
3. Resolve TODOs in main.py
```

## Automation

This runs the same checks as `.claude/maintenance-protocol.md` but automatically.
