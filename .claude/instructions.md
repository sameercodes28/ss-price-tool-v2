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

**Project:** Sofas & Stuff Voice Price Tool v2.0.0-alpha (EXPERIMENTAL)
**Status:** 🚧 Development / Experimentation
**Architecture:** Frontend (GitHub Pages) → Backend (GCF v2) → S&S APIs
**Parent:** v1.0.0 (stable) at ~/Desktop/SS-1

**Key Files:**
- `main.py` - Backend (line 188: entry point)
- `index.html` - Frontend (line 187: v2 backend URL)
- 4 JSON files - Translation dictionaries (loaded at startup)

**Important:**
- This is v2 EXPERIMENTAL - safe to break things!
- v1 is at ~/Desktop/SS-1 (DO NOT MODIFY v1 from here)
- v2 has separate GitHub repo, GCF project, and deployment

**Documentation:**
1. `README.md` - Start here (v2 specific)
2. `V1_V2_SETUP_GUIDE.md` - v1/v2 workflow guide
3. `TECHNICAL_GUIDE.md` - How everything works
4. `ARCHITECTURE.md` - System design
5. `.claude/context.md` - Session memory (read first!)

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
