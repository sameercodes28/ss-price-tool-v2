# Claude Context - Sofas & Stuff Price Tool - v2

**Last Updated:** 2025-11-02 (v2 status changed to production development)
**Current Version:** v2.0.0
**Project Status:** 🚀 Production Development (incremental approach)

> **Important:** This is the v2 repository. Build incrementally with thorough testing.
> **v1 Stable:** See ~/Desktop/SS-1 (ss-price-tool-v1) - DO NOT MODIFY

> **Purpose:** This file helps Claude (or any LLM) quickly understand the project state, recent changes, and ongoing work. Update this file at the end of each session.

> **Note:** Claude Code automatically reads this file via `.claude/instructions.md` - no manual prompting needed!

---

## 📋 Quick Project Summary

**What is this?**
This is v2 of the voice-enabled price lookup tool for Sofas & Stuff salespeople. Users speak/type queries like "alwinton snuggler pacific" and get real-time pricing from S&S internal APIs.

**Relationship to v1:**
- **Forked from:** v1.0.0 (stable, production)
- **Purpose:** Production v2 development with new features and improvements
- **Isolation:** v1 and v2 are completely separate (different repos, different GCF projects)
- **Fallback:** If v2 has issues, v1 continues running unaffected

**Architecture:**
```
Frontend (index.html) → Backend (main.py on GCF v2) → S&S APIs (2 different endpoints)
GitHub Pages (free)     Google Cloud Functions (v2)      Sofa API + Bed API
```

**Key Innovation:** Smart 2-API routing system that automatically selects the correct S&S API based on product type.

**Current Deployment:**
- Backend: ✅ Deployed to GCF → https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2
- Frontend: ✅ Deployed to GitHub Pages → https://sameercodes28.github.io/ss-price-tool-v2/

---

## 🎯 Current State

### What's Working ✅
- [x] v2 directory created (forked from v1.0.0)
- [x] v2 README updated for production development
- [x] v2 context file created
- [x] All v1 code inherited (210 products, 4 JSON files, etc.)
- [x] GitHub repository created (ss-price-tool-v2)
- [x] Google Cloud project created (sofa-project-v2)
- [x] v2 backend deployed to GCF
- [x] v2 frontend updated with v2 backend URL
- [x] v2 frontend deployed to GitHub Pages
- [x] v2 deployment tested and working

### Setup Complete ✅
All infrastructure is deployed and operational!

### v2 Development Goals 🎯
*(Document your v2 objectives here as you develop)*

- [ ] New feature 1
- [ ] New feature 2
- [ ] Performance improvements
- [ ] Architecture changes

---

## 📂 Important File Locations

### Core Backend Files (Deploy to v2 GCF)
- `main.py` - Backend translator (383 lines) - INHERITED FROM v1
- `requirements.txt` - Backend dependencies
- `products.json` - Product catalog (71 KB)
- `sizes.json` - Size options (20 KB)
- `covers.json` - Cover types (4.8 KB)
- `fabrics.json` - Fabric data (23 MB)

### Frontend Files
- `index.html` - Voice/text interface (478 lines) - INHERITED FROM v1
  - **Line 187:** Backend API URL (needs updating to v2 GCF URL)

### Data Generation
- `sku_discovery_tool.py` - Web scraper (680 lines)
- `requirements_scraper.txt` - Scraper dependencies

### Documentation
- `README.md` - v2 getting started guide (updated for v2)
- `TECHNICAL_GUIDE.md` - Complete technical deep dive (inherited)
- `ARCHITECTURE.md` - System architecture overview (inherited)
- `CHANGELOG.md` - Version history (to be updated for v2)
- `docs/PRD.md` - Product requirements (inherited)

### AI Context
- `.claude/context.md` - This file (for LLM session continuity)

---

## 🔧 Recent Changes

### Session: 2025-11-02 (Remove Experimental Status - Production Development)

**Objective:** Remove all "experimental" references and establish v2 as production development

**Changes Made:**

1. ✅ **Updated all documentation to production development status**
   - Removed "experimental" from 6 files (.claude/instructions.md, .claude/context.md, CHANGELOG.md, docs/PRD.md, README.md, V1_V2_SETUP_GUIDE.md)
   - Changed version from "2.0.0-alpha" to "2.0.0"
   - Updated status from "Experimental / Development" to "Production Development (incremental approach)"

2. ✅ **Added detailed commit strategy to instructions**
   - Lines 96-104 in .claude/instructions.md
   - Clarified commits should explain: what, why, how tested, and goal
   - Emphasized committing after each tested piece

3. ✅ **Clarified .claude/context.md as single source of truth**
   - Updated PROJECT_CONTEXT.md references to .claude/context.md
   - Lines 276-282 in .claude/instructions.md
   - Made clear this file is auto-loaded by Claude Code

4. ✅ **Updated messaging throughout codebase**
   - Changed from "safe to break things" to "build incrementally with thorough testing"
   - Removed "experiment freely" language
   - Added emphasis on production quality and testing

**Files Modified:**
- `.claude/instructions.md` - Production development protocol, commit strategy, file references
- `.claude/context.md` - All experimental references removed
- `CHANGELOG.md` - Version updated to 2.0.0, production status
- `docs/PRD.md` - Production development status
- `README.md` - Updated title, version, status
- `V1_V2_SETUP_GUIDE.md` - Development approach section updated

**Decisions Made:**
- v2 is production quality code, not experimental
- Build incrementally with thorough testing at each step
- Commit after each tested piece with detailed messages
- .claude/context.md is the single source of truth (not PROJECT_CONTEXT.md)
- All future development follows production standards

**Testing:**
- Grep search verified all "experimental" references found
- Each file reviewed for consistency after updates
- No "experimental" references remain in documentation

**Additional Changes:**
5. ✅ **Clarified testing approach**
   - Lines 241-260 in .claude/instructions.md: No testing frameworks, Claude tests first
   - Lines 377-382: Updated "WHAT NOT TO BUILD" to emphasize no test libraries
   - Lines 183-196: Enhanced testing checklist with specific tools
   - Lines 251-269 in .claude/context.md: Updated ongoing tasks, removed automated testing items

**Testing Approach Established:**
- Claude tests using Bash, curl, WebFetch tools directly
- No testing frameworks (no pytest, unittest, jest, etc.)
- User runs simple scripts only if Claude cannot test
- Keeps codebase lean and focused

**Additional Changes:**
6. ✅ **Clarified ambiguous instructions**
   - Lines 25-26 in .claude/instructions.md: Added line number disclaimer
   - Lines 68-86: Added clear definitions of "Feature" vs "Piece"
   - Lines 82-86: Added "Local vs Deployed Testing" rules
   - Lines 290-317: Clarified phases are categories, not sequential
   - Lines 144-153: Updated post-implementation testing with deployment rules

**Key Clarifications Made:**
- **Feature** = complete user-facing capability (deployed when done)
- **Piece** = small step < 10-20 lines (tested and committed immediately)
- **Local testing** = mandatory for every piece
- **Deployed testing** = only for complete features
- **Phases** = work categories, not sequential steps (can do any order)
- **Line numbers** = approximate references (will shift as code changes)

**Commits:**
- e703f56: "v2: Remove all 'experimental' references - change to production development status"
- 3fe1741: "v2: Document session changes in context.md"
- 34d35ab: "v2: Clarify testing approach - Claude tests, no frameworks"
- 87638c3: "v2: Update context.md with testing approach documentation"
- 3ac6aa7: "v2: Clarify instructions - definitions, deployment, phases, line numbers"

---

### Session: 2025-11-02 (v2 Reference Cleanup & Memory System Verification)

**Objective:** Ensure all v2 files reference v2 properly and verify Claude memory system works

**Changes Made:**

1. ✅ **Fixed placeholder usernames in README.md**
   - Replaced "YOUR_USERNAME" with actual GitHub username (sameercodes28)
   - Updated v1 repo link to correct URL

2. ✅ **Updated PRD.md for v2**
   - Changed from "v1.0.0 - Production" to "v2.0.0 - Production Development"
   - Added parent project reference to v1
   - Updated executive summary to reflect v2 production development status

3. ✅ **Rewrote CHANGELOG.md for v2**
   - Created v2-specific changelog (separate from v1)
   - Documented v2 initial release (2.0.0)
   - Included infrastructure details (separate repos, GCF projects)
   - Added v2 development goals section

4. ✅ **Updated .claude/instructions.md for v2**
   - Changed project reference to "v2.0.0 - Production Development"
   - Added parent project location (~/Desktop/SS-1)
   - Clarified v2-specific documentation

5. ✅ **Verified Claude memory system**
   - Confirmed .claude/context.md is v2-specific
   - Verified /update-context command exists and works
   - All session continuity features operational

**Files Modified:**
- `README.md` - Fixed placeholder usernames, v1 repo links
- `docs/PRD.md` - Updated to v2 production development status
- `CHANGELOG.md` - Completely rewritten for v2
- `.claude/instructions.md` - Updated for v2 references
- `.claude/context.md` - This file (added this session entry)

**Decisions Made:**
- v2 is production quality, built incrementally to avoid bugs
- All v1 references that indicate origin (forked from v1.0.0) should remain
- CHANGELOG.md for v2 should be separate from v1 changelog
- Claude memory system works identically in v2 as it did in v1

**Additional Notes:**
- All files now properly reference v2
- Claude will auto-read context.md at start of each session (same as v1)
- User can use /update-context command same as v1
- v2 is now fully configured for incremental production development

---

### Session: 2025-11-02 (v2 Initialization)

**Objective:** Create v2 production branch from v1.0.0

**Changes Made:**

1. ✅ **Marked v1 as stable**
   - Updated v1 README to indicate it's stable
   - Updated v1 context to maintain as stable version

2. ✅ **Created v2 directory**
   - Copied entire SS-1 to SS-2
   - Removed v1 git history from v2

3. ✅ **Updated v2 documentation**
   - Created new v2 README for production development
   - Created new v2 context file (this file)
   - Marked v2 as 2.0.0

**Files Created:**
- `~/Desktop/SS-2/` - Entire v2 directory structure
- `~/Desktop/SS-2/README.md` - v2-specific README
- `~/Desktop/SS-2/.claude/context.md` - This file

**Files Modified:**
- None yet (v2 is fresh copy of v1)

**Decisions Made:**
- v2 is production quality, built incrementally to avoid bugs
- v2 will use separate GitHub repo
- v2 will use separate Google Cloud project
- v2 will have separate GCF function name
- v2 will have separate GitHub Pages URL
- v1 remains untouched and continues running

**Next Steps:**
1. Create new GitHub repo for v2
2. Create new Google Cloud project for v2
3. Initialize git in v2
4. Deploy v2 backend
5. Deploy v2 frontend
6. Start v2 development

---

## 🎯 Ongoing Tasks

### High Priority (Setup)
- [x] Create new GitHub repository for v2
- [x] Create new Google Cloud project for v2
- [x] Deploy v2 backend to new GCF
- [x] Update v2 frontend with new backend URL
- [x] Deploy v2 frontend to GitHub Pages
- [x] Test v2 deployment
- [x] Update all documentation to production development status

### Next Steps (Development)
- [ ] Define specific v2 features to build
- [ ] Begin Phase 1: Chat-Like Interface with Memory (per instructions.md)
- [ ] Document each new feature in context.md
- [ ] Test all v2 changes don't affect v1

### Ongoing Maintenance
- [ ] Keep v2 documentation updated as features are added
- [ ] Monitor and document any issues discovered
- [ ] Maintain .claude/context.md after each session

---

## 💡 Important Context for LLMs

### Critical Design Decisions

1. **Why separate repos/projects for v2?**
   - Complete isolation from v1
   - Safe experimentation without risk
   - Different deployment URLs
   - Can fail without affecting v1
   - Easier to manage mentally

2. **What's inherited from v1?**
   - All code (main.py, index.html, sku_discovery_tool.py)
   - All data (4 JSON files with 210 products)
   - All documentation (TECHNICAL_GUIDE, ARCHITECTURE, etc.)
   - All architecture (2-API routing, caching, etc.)

3. **What's different in v2?**
   - Separate GitHub repository
   - Separate Google Cloud project
   - Separate GCF function (sofa-price-calculator-v2)
   - Separate GitHub Pages URL
   - New features and improvements (built incrementally)

### Common Gotchas

1. **Don't confuse v1 and v2 directories**
   - v1: ~/Desktop/SS-1 (NEVER MODIFY)
   - v2: ~/Desktop/SS-2 (MODIFY FREELY)

2. **Don't deploy v2 to v1's GCF**
   - v1 GCF: sofa-price-calculator (project: sofaproject-476903)
   - v2 GCF: sofa-price-calculator-v2 (project: YOUR-V2-PROJECT-ID)

3. **Update backend URL in v2 frontend**
   - v2 index.html:187 must point to v2 GCF URL
   - NOT the v1 GCF URL

4. **Git repositories are separate**
   - v1 repo: ss-price-tool-v1
   - v2 repo: ss-price-tool-v2
   - They don't share git history

---

## 🔗 External References

### v1 (Stable)
- **Local Directory:** ~/Desktop/SS-1
- **Google Cloud Project:** `sofaproject-476903`
- **GCF Function:** `sofa-price-calculator`
- **GCF Region:** `europe-west2`
- **Backend URL:** https://europe-west2-sofaproject-476903.cloudfunctions.net/sofa-price-calculator
- **Frontend URL:** (Your GitHub Pages URL)
- **S&S Website:** https://sofasandstuff.com

### v2 (Production Development)
- **Local Directory:** ~/Desktop/SS-2
- **GitHub Repo:** https://github.com/sameercodes28/ss-price-tool-v2
- **Google Cloud Project:** `sofa-project-v2`
- **GCF Function:** `sofa-price-calculator-v2`
- **GCF Region:** `europe-west2`
- **Backend URL:** https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2
- **Frontend URL:** https://sameercodes28.github.io/ss-price-tool-v2/

---

## 💬 Communication Style

When working on v2:
- Build incrementally with careful testing
- Document what you change
- Compare to v1 when helpful
- Test thoroughly to avoid bugs
- Update this context file frequently

---

**End of Context File**

*This file should be updated at the end of each v2 session to maintain continuity.*
