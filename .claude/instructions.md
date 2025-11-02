# Claude Code Project Instructions

**IMPORTANT:** At the start of EVERY new conversation, read `.claude/context.md` first to understand:
- Current project state
- Recent changes
- Ongoing tasks
- Known issues
- Important design decisions

This ensures continuity between sessions and prevents hallucinations.

---

## Quick Project Reference

**Project:** Sofas & Stuff Voice Price Tool v1.0.0
**Status:** Production Ready
**Architecture:** Frontend (GitHub Pages) → Backend (GCF) → S&S APIs

**Key Files:**
- `main.py` - Backend (line 188: entry point)
- `index.html` - Frontend (line 188: backend URL)
- 4 JSON files - Translation dictionaries (loaded at startup)

**Documentation:**
1. `README.md` - Start here
2. `TECHNICAL_GUIDE.md` - How everything works
3. `ARCHITECTURE.md` - System design
4. `.claude/context.md` - Session memory (read first!)

---

## Session Protocol

**Start of Session:**
1. Read `.claude/context.md` (mandatory)
2. Check for recent changes
3. Review ongoing tasks

**During Session:**
- Reference specific line numbers when discussing code
- Update context mentally as changes are made
- Document any new gotchas discovered

**End of Session:**
- Update `.claude/context.md` with:
  - Changes made
  - Files modified
  - Decisions made
  - New tasks/issues discovered
