#!/bin/bash
# Pre-Commit Hook - Prevent Version Drift & Documentation Issues
#
# Installation:
#   cp .claude/pre-commit-hook-template.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# This runs automatically before every git commit

echo "🔍 Running pre-commit checks..."

# ============================================
# CHECK 1: Version Consistency
# ============================================
echo "Checking version consistency..."

VERSIONS=$(grep -rh "v2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/context.md .claude/instructions.md 2>/dev/null | grep -oE "v2\.[0-9]\.[0-9]" | sort -u)
VERSION_COUNT=$(echo "$VERSIONS" | wc -l | tr -d ' ')

if [ "$VERSION_COUNT" -gt 1 ]; then
    echo ""
    echo "❌ VERSION DRIFT DETECTED!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Found multiple versions:"
    echo "$VERSIONS"
    echo ""
    echo "Files to check:"
    grep -l "v2\.[0-9]\.[0-9]" README.md CHANGELOG.md .claude/context.md .claude/instructions.md 2>/dev/null
    echo ""
    echo "Please update all files to the same version before committing."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

CURRENT_VERSION=$(echo "$VERSIONS" | head -1)
echo "✅ Version consistency: $CURRENT_VERSION"

# ============================================
# CHECK 2: Backup Files in Root
# ============================================
echo "Checking for backup files in root..."

BACKUP_FILES=$(ls -1 2>/dev/null | grep -E "backup|test-.*\.html|.*-old\.|temp-" | grep -v "index-before-cleanup.html")

if [ ! -z "$BACKUP_FILES" ]; then
    echo ""
    echo "⚠️  BACKUP FILES FOUND IN ROOT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$BACKUP_FILES"
    echo ""
    echo "Consider moving to backups/archive/ before committing:"
    echo "  git mv <file> backups/archive/"
    echo ""
    echo "Or run commit with --no-verify to skip this check."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # WARNING only, don't block commit
    # If you want to block, uncomment the next line:
    # exit 1
fi

# ============================================
# CHECK 3: CHANGELOG Updated
# ============================================
echo "Checking if CHANGELOG mentions current version..."

if ! grep -q "$CURRENT_VERSION" CHANGELOG.md 2>/dev/null; then
    echo ""
    echo "⚠️  CHANGELOG MAY BE OUTDATED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Current version $CURRENT_VERSION not found in CHANGELOG.md"
    echo "Did you forget to add a changelog entry?"
    echo ""
    echo "Run commit with --no-verify to skip this check."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # WARNING only, don't block commit
    # exit 1
fi

# ============================================
# CHECK 4: TODO/FIXME in Staged Files
# ============================================
echo "Checking for TODO/FIXME in staged changes..."

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(py|html|js|md)$")

if [ ! -z "$STAGED_FILES" ]; then
    TODOS=$(echo "$STAGED_FILES" | xargs grep -n "TODO\|FIXME\|HACK\|XXX" 2>/dev/null || true)

    if [ ! -z "$TODOS" ]; then
        echo ""
        echo "ℹ️  TODO/FIXME COMMENTS FOUND"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$TODOS"
        echo ""
        echo "Consider resolving or documenting these before committing."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        # INFO only, don't block
    fi
fi

# ============================================
# ALL CHECKS PASSED
# ============================================
echo ""
echo "✅ Pre-commit checks passed!"
echo ""

exit 0
