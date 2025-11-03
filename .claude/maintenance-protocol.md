# Maintenance Protocol - Preventing Documentation Drift & Code Bloat

**Purpose:** Prevent version drift, documentation lag, and code accumulation
**Frequency:** Run after each significant feature/fix
**Owner:** Developer + Claude Code

---

## 🎯 The Core Problem

Without discipline, projects accumulate:
- ❌ Version inconsistencies (README says v2.4.0, instructions say v2.3.0)
- ❌ Stale documentation (migration docs sitting in root after completion)
- ❌ Dead code (unused CSS, removed Analytics features)
- ❌ Backup file sprawl (test files, old versions everywhere)

---

## 🛡️ Prevention Strategy: "Commit Checklist"

### **Before Every Git Commit - Run This Checklist:**

```bash
# 1. VERSION CHECK (30 seconds)
# Search for version numbers - ensure consistency
grep -r "version.*2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/context.md .claude/instructions.md

# If they don't match, update them FIRST before committing feature

# 2. DEAD CODE CHECK (1 minute)
# Look for TODOs, FIXMEs, unused code
grep -rn "TODO\|FIXME\|DEPRECATED\|UNUSED" --include="*.py" --include="*.html" --include="*.js" .

# If found, either:
# - Implement the TODO
# - Remove it if no longer relevant
# - Document why it's deferred

# 3. BACKUP FILE CHECK (30 seconds)
# List files in root that look temporary
ls -1 | grep -E "backup|test-|old|temp|-v[0-9]"

# If found, either:
# - Move to backups/archive/ with README explaining what it is
# - Delete if verified safe
# - Keep in root ONLY if actively used (like index-before-cleanup.html for 1 week)

# 4. DOCUMENTATION UPDATE (2 minutes)
# Did you add a feature? Update:
# - README.md (features list)
# - CHANGELOG.md (new version entry)
# - .claude/context.md (if it changes workflow)
```

---

## 📋 Detailed Checklist by Change Type

### **When Bumping Version (e.g., 2.3.1 → 2.4.0)**

**Files to Update (in this order):**
1. ✅ CHANGELOG.md - Add new version entry first
2. ✅ README.md - Update version number and features
3. ✅ .claude/context.md - Update "Current Version" and "Last Updated"
4. ✅ .claude/instructions.md - Update "Project: ... v2.X.X"
5. ✅ Commit all together: "docs: Bump version to vX.X.X across all files"

**Validation:**
```bash
# This should return ONLY your new version number
grep -r "v2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/*.md | grep -oE "v2\.[0-9]\.[0-9]" | sort -u
```

---

### **When Completing a Major Feature**

**Steps:**
1. ✅ Add CHANGELOG entry under current version
2. ✅ Update README features list if user-facing
3. ✅ Archive any planning docs (like TELEMETRY_CLEANUP_PLAN.md)
4. ✅ Remove any temporary test files created during development
5. ✅ Delete or archive any feature branch backups

**Example:**
```bash
# After completing telemetry cleanup:
# - Mark TELEMETRY_CLEANUP_PLAN.md as "✅ COMPLETED"
# - Add to CHANGELOG under v2.4.0
# - Remove test files: test-analytics.html
# - Archive backup: index-before-telemetry.html → backups/archive/
```

---

### **When Creating Backup Files**

**Rule:** NEVER leave backups in root for >1 week

**Best Practice:**
```bash
# GOOD - Descriptive name with date
cp index.html index-before-<feature>-$(date +%Y%m%d).html

# Immediately after successful deployment:
git mv index-before-<feature>-*.html backups/archive/

# Update backups/archive/README.md with why it exists
```

**Automated Cleanup Script:**
```bash
# Add to git hooks or run monthly
find . -maxdepth 1 -name "*backup*" -mtime +7 -exec echo "Old backup: {}" \;
# Review, then move to backups/archive/
```

---

### **When Removing Features**

**Checklist:**
1. ✅ Remove the code
2. ✅ Remove associated CSS/JS
3. ✅ Remove from documentation
4. ✅ Check for orphaned files (test files, config files)
5. ✅ Add removal to CHANGELOG

**Example (removing old Analytics):**
```bash
# 1. Remove code from index.html
# 2. Search for references:
grep -r "conversionFunnel\|productPopularity" .
# 3. Remove any test files testing those features
# 4. Update CHANGELOG: "Removed 488 lines of unused Analytics code"
```

---

## 🤖 Automation Opportunities

### **1. Pre-Commit Git Hook**

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for version consistency before commit

VERSIONS=$(grep -rh "v2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/*.md | grep -oE "v2\.[0-9]\.[0-9]" | sort -u)
VERSION_COUNT=$(echo "$VERSIONS" | wc -l)

if [ "$VERSION_COUNT" -gt 1 ]; then
    echo "❌ VERSION DRIFT DETECTED!"
    echo "Found multiple versions: $VERSIONS"
    echo "Please update all files to same version before committing."
    exit 1
fi

echo "✅ Version consistency check passed"
```

**Enable it:**
```bash
chmod +x .git/hooks/pre-commit
```

---

### **2. Monthly Cleanup Reminder**

Add to calendar/cron:
```bash
# First day of month - run cleanup audit
# Check for:
# - Backup files older than 30 days
# - TODO/FIXME comments
# - Unused test files
# - Version drift
```

---

### **3. Claude Code Slash Command**

Create `.claude/commands/audit.md`:
```markdown
# Slash Command: /audit

Run comprehensive codebase audit:

1. Check version consistency across README, CHANGELOG, .claude/*
2. Search for TODO/FIXME/DEPRECATED comments
3. List backup/test files in root directory
4. Check for unused CSS classes
5. Generate audit report

If issues found, create commit fixing them.
```

Then you can just run `/audit` in Claude Code!

---

## 📊 Regular Audit Schedule

### **After Every Feature (Immediate)**
- [ ] Update CHANGELOG
- [ ] Check version numbers
- [ ] Remove temp files
- [ ] Archive planning docs if feature complete

### **Weekly (5 minutes)**
- [ ] Review root directory for stray files
- [ ] Check for TODO comments
- [ ] Verify documentation matches code

### **Monthly (15 minutes)**
- [ ] Full codebase audit (like we just did)
- [ ] Archive old backups
- [ ] Update documentation for accuracy
- [ ] Clean up git history (squash WIP commits if needed)

### **Before Deployment (Critical)**
- [ ] Version numbers consistent
- [ ] CHANGELOG updated
- [ ] No debug code (console.log, test functions)
- [ ] Backups archived

---

## 🎓 Lessons from This Audit

### **What Caused the Drift:**

1. **Version Updates Without Full Sweep**
   - Updated README to 2.3.1 but forgot .claude/instructions.md
   - **Fix:** Use checklist or grep command

2. **Completed Work Not Archived**
   - 11 migration docs stayed in root after success
   - **Fix:** Archive immediately when "Done" status reached

3. **Feature Removal Didn't Clean Everything**
   - Old Analytics code removed, but CSS lingered
   - **Fix:** Search for all references before removing features

4. **No Backup Management Policy**
   - Test files accumulated during development
   - **Fix:** Move to archive/ immediately after verification

---

## 🚀 Quick Reference Card

**Print this and keep visible:**

```
┌─────────────────────────────────────────┐
│  COMMIT CHECKLIST - 3 Minutes           │
├─────────────────────────────────────────┤
│ ✅ Versions match everywhere?           │
│ ✅ CHANGELOG updated?                   │
│ ✅ Backups archived?                    │
│ ✅ Dead code removed?                   │
│ ✅ Documentation accurate?              │
└─────────────────────────────────────────┘

Commands to run:
$ grep -r "v2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/*.md
$ ls -1 | grep -E "backup|test-|old"
$ grep -rn "TODO\|FIXME" --include="*.py" --include="*.html" .
```

---

## 💡 Pro Tips

1. **Use descriptive commit messages**
   - Good: "docs: Update version to v2.4.0 across all files"
   - Bad: "update docs"

2. **One concern per commit**
   - Easier to revert
   - Clear git history
   - Easier to review

3. **Archive, don't delete**
   - Disk space is cheap
   - Reference value is high
   - Create archive/README.md explaining contents

4. **Make Claude your accountability partner**
   - Ask: "Did I update all version numbers?"
   - Ask: "Are there any stale files in root?"
   - Claude will check systematically

5. **Set calendar reminders**
   - Monthly: "Run codebase audit"
   - Quarterly: "Review and delete old archives"

---

## 🎯 Success Metrics

You'll know this is working when:
- ✅ No version drift for 3+ months
- ✅ No files in root older than 1 week (except core files)
- ✅ CHANGELOG always has latest version documented
- ✅ Can find any file's purpose in <30 seconds
- ✅ No orphaned code or comments

---

**Remember:** Discipline compounds. 3 minutes per commit prevents 3 hours of cleanup later.
