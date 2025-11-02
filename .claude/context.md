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

### Session: 2025-11-02 (Phase 1A: Frontend Chat UI - COMPLETE)

**Objective:** Build beautiful full-screen chat interface for conversational agent

**Changes Made:**

1. ✅ **Complete chat interface redesign (index.html)**
   - WhatsApp/Claude-style full-screen chat layout
   - Message bubbles (user right, agent left)
   - Auto-resizing textarea input
   - Typing indicator with animated dots
   - Smooth scroll behavior with hidden scrollbar
   - Message fade-in animations

2. ✅ **Theme system implementation**
   - Random theme selection on page load (Warm Sunset vs Soft Lavender)
   - Theme-coordinated colors for all UI elements:
     - Background gradients
     - Logo and submit button
     - Input border and focus states
     - Agent avatar gradient
     - Typing indicator dots
   - CSS variables for easy theme switching

3. ✅ **Visual polish and branding**
   - Replaced purple message icon with couch SVG for agent avatar
   - Applied couch icon to typing indicator too
   - Changed user bubble to dark slate gray (distinct from agent)
   - Applied Plus Jakarta Sans font throughout
   - Fixed submit button alignment with input box
   - Added proper shadows and visual hierarchy

4. ✅ **Improved orb animation**
   - Changed from 22 pastel colors to 21 vivid colors
   - Faster animation cycle (15s → 5s)
   - Glowing orb with pulsing effects
   - Example questions cycling below orb

5. ✅ **Updated context.md with comprehensive plan**
   - Documented all 35 pieces of implementation plan
   - Added OpenRouter API key and configuration
   - Clear phase status indicators (✅ COMPLETED, ⏳ NEXT, 🔜 UPCOMING)
   - Prevents losing track of overall goal

**Files Modified:**
- `index.html` - Complete UI overhaul (lines 1-747)
  - Added theme system (lines 349-462)
  - Updated chat message bubbles (lines 501-527)
  - Fixed typing indicator with couch icon (lines 300-316)
  - Changed to Plus Jakarta Sans font (lines 11-18)
  - Removed font switcher code
- `.claude/context.md` - Added comprehensive plan (lines 366-427)

**Decisions Made:**
- Full-screen chat (like ChatGPT/Claude) ✅
- User bubbles: Dark slate gray (distinct from theme colors) ✅
- Agent avatar: Couch icon with theme gradient ✅
- Font: Plus Jakarta Sans ✅
- Themes: Random selection between Warm Sunset and Soft Lavender ✅

**Testing:**
- Manual testing of all UI elements
- Theme switching tested on page reload
- Message bubbles display correctly
- Typing indicator shows couch icon
- Input alignment verified
- Font applied consistently

**User Feedback:**
- User approved UI design
- User confirmed colors are distinct
- User happy with Plus Jakarta Sans font
- Ready to move to Phase 1B (Backend Session Memory)

**What's NOT Done (Next Phases):**
- Frontend still uses `simulateBackendResponse()` (not connected to real backend)
- No session management yet
- No LLM integration yet
- No enhanced tools (compare, budget search, etc.)

**Commits:**
- 59cd3e1: "v2: Complete Phase 1A - Full-screen chat UI with themes and polish"
- 27ba86d: Merge Phase 1A to main (demo-ready)

**Tags:**
- demo-ready-v2.1.0-phase1a: Phase 1A complete - Beautiful full-screen chat UI with themes

**Branches:**
- main: ✅ Phase 1A merged and pushed
- feature/chat-interface-with-memory: ✅ Ready for Phase 1B work

---

### Session: 2025-11-02 (Phase 1.5: Backend Connection + Critical Protocol Enforcement)

**Objective:** Connect chat UI to real v2 backend, test with static keywords before adding LLM

**Changes Made:**

1. ✅ **Connected frontend to v2 GCF backend (index.html lines 566-638)**
   - Replaced `simulateBackendResponse()` with real fetch() call
   - Connected to: `https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice`
   - Added `formatPriceResponse()` function to parse backend JSON
   - Updated message display with `white-space: pre-wrap` for line breaks

2. ✅ **Improved error handling and greeting messages**
   - Added greeting handler for "hello", "hi", "help"
   - Provided helpful error messages with spelling tips, format guidance
   - Listed popular products when queries fail
   - Updated greeting examples with real, tested products

3. ✅ **Backend response formatting**
   - Parses JSON: `{productName, price, oldPrice, fabricName, fabricDetails}`
   - Displays formatted price with fabric tier info
   - Shows old price if product is on sale

**Critical Mistakes Made & Fixed:**

**MISTAKE 1: Invented "Berkeley" Product**
- Suggested example "berkeley 3 seater sussex plain" without checking products.json
- Mentioned "House Wool" fabric without checking fabrics.json
- User tested and examples failed with error messages
- **Root Cause:** Made up examples without verification

**FIX 1: Removed fake products, updated examples**
- Checked products.json for real products
- Updated to "aldingbourne 3 seater waves" and "saltdean 3 seater covertex"
- Committed as "CRITICAL FIX - Remove fake product examples"

**MISTAKE 2: Violated Own Protocol - Didn't Actually Test**
- Claimed to "fix" examples but DIDN'T TEST WITH CURL
- "aldingbourne 3 seater waves" → No "3 seater" variant exists (only snuggler, chair)
- "saltdean 3 seater covertex" → Backend error, needs specific color
- User tested again and examples STILL failed
- **Root Cause:** Only checked if product NAME existed, not if FULL QUERY worked

**FIX 2: Actually tested with curl, updated examples**
```bash
# STEP 1: Test with curl (ACTUALLY TESTED THIS TIME)
curl -X POST .../getPrice -d '{"query": "aldingbourne snuggler waves"}'
→ {"price":"£1,958"} ✅

curl -X POST .../getPrice -d '{"query": "rye snuggler pacific"}'
→ {"price":"£1,482"} ✅
```
- Updated examples with curl-verified queries
- Committed as "DOUBLE FIX - Replace with CURL-TESTED examples"

**MISTAKE 3: Protocols Written But Not Followed**
- Wrote "Data Verification Protocol" but immediately violated it
- User asked: "Ok so whatever you told yourself before to actually test before didn't actually work... why?"
- **Root Cause:** Protocols were just words with no enforcement mechanism

**FIX 3: MANDATORY ENFORCEMENT CHECKLISTS**
- Added to TOP of .claude/instructions.md (lines 43-113)
- Cannot suggest examples without:
  1. ☐ Check data file exists
  2. ☐ Test with curl - show output
  3. ☐ Verify successful response
  4. ☐ Copy/paste curl output as evidence
  5. ☐ ONLY THEN suggest to user
- TodoWrite must include separate "Test with curl" step
- Session protocol requires reviewing checklists

**Protocols Established:**

1. **Data Verification Protocol** (lines 357-404 in .claude/instructions.md)
   - NEVER invent product names, fabrics, sizes, prices
   - ALWAYS check actual data files before mentioning specifics
   - Verify examples work with curl BEFORE suggesting them

2. **Plan Tracking Protocol** (lines 407-452)
   - Prevent tunnel vision on sub-tasks
   - Keep full plan in TodoWrite with ALL phases
   - Review .claude/context.md at start of every session

3. **Commit Communication Protocol** (lines 456-504)
   - Be explicit about commit, branch, pushed status, live URL
   - Use template format for consistency

4. **MANDATORY ENFORCEMENT CHECKLISTS** (lines 43-113)
   - Cannot skip steps when suggesting examples
   - Must show curl test output as evidence
   - TodoWrite must include testing steps

**Files Modified:**
- `index.html` - Backend connection, error handling, greeting messages (lines 566-638)
- `.claude/instructions.md` - Added 4 protocols + enforcement checklists (lines 43-113, 357-504)

**Working Examples (curl-verified):**
1. "alwinton snuggler pacific" → £1,958 ✅
2. "aldingbourne snuggler waves" → £1,958 ✅
3. "rye snuggler pacific" → £1,482 ✅

**Decisions Made:**
- Phase 1.5 (backend connection) comes BEFORE Phase 1C (LLM)
- Test with static keywords first, then add natural language
- Protocols need enforcement mechanisms, not just documentation
- TodoWrite must break down testing into separate steps
- Cannot suggest examples without curl test evidence

**Testing:**
- All greeting examples tested by user and confirmed working
- Backend connection tested with multiple product queries
- Error messages tested with invalid queries
- Price formatting tested with products on sale

**User Feedback:**
- User caught all three protocol violations
- User demanded enforcement mechanisms
- User confirmed all examples work after final fix
- User ready to proceed with Phase 1C

**Commits:**
- ddbc4b2: "Phase 1.5: Connect frontend to backend"
- 050e83c: "Improve error messages and greeting"
- b9f1f92: Merge improved error messages
- e505d5c: "CRITICAL FIX: Remove fake Berkeley product"
- 9c7c1fc: "DOUBLE FIX: CURL-TESTED examples + protocols"
- cd5b3b4: Merge tested examples
- 08be4d3: "Add MANDATORY ENFORCEMENT CHECKLISTS"
- 04f9032: Merge enforcement checklists

**Tags:**
- (None yet - can tag when Phase 1C complete)

**Current State:**
- ✅ Phase 1A complete (Frontend Chat UI)
- ✅ Phase 1.5 complete (Backend Connection)
- ⏳ Phase 1C next (Grok LLM Integration)
- All examples tested and working
- All commits pushed to main
- Live at: https://sameercodes28.github.io/ss-price-tool-v2/

**Key Lessons:**
- Protocols without enforcement = will be violated
- Must show evidence (curl output) not just claim to have tested
- TodoWrite must include separate testing steps to force verification
- User trust requires demonstrable testing, not just assertions

---

### Session: 2025-11-02 (Phase 1C: Grok LLM Integration - COMPLETE)

**Objective:** Integrate Grok-4 LLM via OpenRouter with 3 tools for conversational agent

**Changes Made:**

1. ✅ **OpenRouter/Grok-4 Integration (main.py)**
   - Added OpenAI client configured for OpenRouter API
   - Model: `x-ai/grok-4` (best function calling support)
   - Environment variables: `OPENROUTER_API_KEY`, `GROK_MODEL`
   - Lines 13, 63-77: Client initialization with error handling

2. ✅ **Comprehensive System Prompt (200 lines)**
   - Lines 79-279: Full product knowledge, conversation patterns
   - Company background (210+ products, British craftsmanship)
   - Product catalog (Alwinton, Rye, Saltdean, etc.)
   - Fabric tiers (Essentials, Premium, Luxury)
   - Tool descriptions and usage guidelines
   - Response style and examples
   - Edge case handling

3. ✅ **Chat Handler with Full Tool Calling Loop**
   - Lines 633-789: `/chat` endpoint with conversation management
   - Tool calling loop (max 5 iterations)
   - Tracks total tokens across iterations
   - Session ID support (future-proofing for Phase 1B)
   - Error handling with fallback messages

4. ✅ **Three Tools Implemented:**

   **Tool 1: get_price** (Lines 285-330)
   - Wrapper around existing `get_price_logic()`
   - Returns exact pricing for specific configurations
   - MockRequest pattern to reuse existing code

   **Tool 2: search_by_budget** (Lines 354-454)
   - Searches products under max price
   - Returns up to 20 products sorted by price
   - Includes fabric tier guidance
   - Filters by product type (sofa, bed, all, etc.)

   **Tool 3: search_fabrics_by_color** (Lines 456-568)
   - Searches fabrics matching color name
   - Deduplicates across products
   - Groups by tier (Essentials, Premium, Luxury)
   - Returns up to 30 unique fabric options
   - Optional product_name parameter for context-aware search

5. ✅ **Frontend Integration (index.html)**
   - Lines 341-376: LLM configuration with feature flag
   - `USE_LLM = true` - Feature flag for LLM vs direct matching
   - Session management (generateSessionId, resetConversation)
   - Conversation history tracking (OpenAI message format)
   - Lines 597-742: Dual-path sendMessage() function:
     - LLM path: Calls `/chat` with full history
     - Non-LLM path: Falls back to `/getPrice` (Phase 1.5 logic)
   - Metadata logging (tokens, iterations, model)

**Backend Test Results (All PASSED ✅):**
```bash
# Test 1: /getPrice (No Breakage)
curl .../getPrice -d '{"query": "alwinton snuggler pacific"}'
→ {"price": "£1,958", ...} ✅

# Test 2: /chat Greeting
curl .../chat -d @test_chat.json
→ Natural greeting response (3,861 tokens) ✅

# Test 3: get_price Tool
curl .../chat -d '{"messages":[{"role":"user","content":"How much is Alwinton snuggler in Pacific?"}]}'
→ £1,958 with full product details (8,812 tokens, 2 iterations) ✅

# Test 4: search_by_budget Tool
curl .../chat -d '{"messages":[{"role":"user","content":"Show me sofas under £2000"}]}'
→ Found Midhurst £1,937 and Petworth £1,941 (8,420 tokens) ✅

# Test 5: search_fabrics_by_color Tool
curl .../chat -d '{"messages":[{"role":"user","content":"Show me blue fabrics"}]}'
→ Found 24 blue fabrics with examples (11,908 tokens) ✅
```

**Files Modified:**
- `main.py` - Added 695 lines (tools, system prompt, chat handler)
- `index.html` - Added 219 lines (LLM integration, conversation tracking)
- `requirements.txt` - Added `openai>=1.12.0`, `python-dotenv>=1.0.0`
- `.env` (local only) - OpenRouter API key configuration
- `.env.example` - Environment variable documentation
- `test_openrouter.py` - Connection test script

**Implementation Strategy:**
- Feature branch: `feature/grok-llm`
- Tagged baseline: `demo-ready-before-phase-1c`
- Incremental pieces (3.1-3.10) with commits at each stage
- Tested backend separately before frontend changes
- Feature flag allows rollback (`USE_LLM=false`)

**Deployment:**
- Backend: `https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2`
- Frontend: `https://sameercodes28.github.io/ss-price-tool-v2/`
- OpenRouter API Key: New key created with $10 credits
- All endpoints tested live and working

**Key Decisions:**
- Used `x-ai/grok-4` (not grok-beta) for best function calling
- Temperature NOT set (defaults to 1.0 - needs fixing in Demo Polish)
- Fabric tier pricing kept generic ("varies by product" - not specific amounts)
- Tool calling loop with max 5 iterations prevents infinite loops
- Session ID passed but not stored yet (Phase 1B will add memory)

**Token Usage:**
- Greeting: ~3,800 tokens
- get_price tool call: ~8,800 tokens (2 iterations)
- search_by_budget: ~8,400 tokens (2 iterations)
- search_fabrics_by_color: ~11,900 tokens (2 iterations)
- **Cost per conversation: $0.03-0.12** (Grok pricing)

**Commits:**
- b81874d: Pre-implementation setup (lessons learned, checklist, recovery protocol)
- d50fa6e: Piece 3.1 - OpenRouter setup (connection test skipped due to API key 401)
- b3a602d: Piece 3.2 - Basic /chat endpoint with system prompt
- 2867e3e: Piece 3.3 - Tool registry + get_price tool
- 3b575b6: Piece 3.4 - search_by_budget tool
- 5618e1a: Piece 3.5 - search_fabrics_by_color tool
- 541d425: Piece 3.8 - Backend deployed and tested (all 5 tests passed)
- 0a523f7: Piece 3.9 - Frontend integration with conversation tracking
- a0a4ed0: Piece 3.10 - Enable LLM features (USE_LLM=true)
- 5854a29: Merge to main

**Tags:**
- `demo-ready-before-phase-1c` - Baseline before LLM integration
- `demo-ready-phase-1c-complete` - Phase 1C fully deployed and tested

**User Feedback:**
- Impressed with backend test results
- Requested improvements for demo polish:
  - Real-time streaming (no typing dots)
  - Better response formatting (markdown, bullet points)
  - Follow-up question suggestions (Perplexity-style chips)
  - Temperature = 0.1 (more precise, less creative)
  - Clickable product/fabric links to sofasandstuff.com
  - Update all documentation

**Current State:**
- ✅ Phase 1A complete (Frontend Chat UI)
- ✅ Phase 1.5 complete (Backend Connection)
- ✅ Phase 1C complete (Grok LLM + 3 Tools)
- ⏳ Demo Polish next (streaming, formatting, links, etc.)
- 🔜 Phase 1B upcoming (Backend Session Memory)

**Status:** ✅ **WORKING DEMO - LIVE AND FUNCTIONAL**

---

### Session: 2025-11-02 (Demo Polish Phase - PLANNING)

**Objective:** Improve UX for demo presentation based on user feedback

**Status:** 📋 **DOCUMENTATION FIRST** (before any code changes)

**User Requirements:**
1. ✅ Real-time streaming responses (no typing dots)
2. ✅ Better formatting (markdown, bullet points, spacing)
3. ✅ Follow-up question suggestions (Perplexity-style clickable chips)
4. ✅ Temperature = 0.1 (precise, deterministic responses)
5. ✅ Clickable product/fabric links (direct to sofasandstuff.com)
6. ✅ Update all .md files with Phase 1C changes

**Investigation Results:**

**1. Streaming:** ✅ FULLY POSSIBLE
- OpenRouter supports SSE with `stream: true`
- GCF Gen 2 supports SSE responses
- OpenAI Python SDK has built-in streaming
- Implementation: Separate `/chat-stream` endpoint (keeps `/chat` working)
- Complexity: HIGH (tool calling in streaming mode is complex)
- Value: VERY HIGH (much better UX)

**2. Formatting:** ✅ EASY WIN
- Update system prompt to use markdown syntax
- Add marked.js library to frontend (5KB)
- Render LLM responses as formatted HTML
- Complexity: LOW
- Value: HIGH

**3. Follow-up Suggestions:** ✅ FULLY POSSIBLE
- System prompt outputs suggestions in special format
- Frontend parses and renders as clickable chips
- Clicking chip sends question automatically
- Complexity: MEDIUM
- Value: VERY HIGH (guides conversation)

**4. Temperature:** ❌ NOT SET (CRITICAL FIX)
- Currently defaults to 1.0 (too creative for pricing)
- Fix: Add `temperature=0.1` to chat endpoint
- Complexity: TRIVIAL (one line)
- Value: HIGH (reduces hallucinations)

**5. Product Links:** ✅ FULLY POSSIBLE
- Data already exists in products.json (url field)
- Tool handlers can include URLs in results
- System prompt instructs Grok to format as links
- Complexity: MEDIUM
- Value: VERY HIGH (instant access to products)

**6. Documentation:** ⏳ IN PROGRESS
- .claude/context.md - Adding Phase 1C summary ✅
- README.md - Adding Demo Stage notice
- CHANGELOG.md - Adding Phase 1C entry
- TECHNICAL_GUIDE.md - Adding architecture details

**Implementation Plan:**
- **Piece 1:** Temperature=0.1 (5 min, ZERO risk)
- **Piece 2:** Response formatting (30 min, LOW risk)
- **Piece 3:** Follow-up suggestions (45 min, MEDIUM risk)
- **Piece 4:** Product links (1 hour, MEDIUM-HIGH risk)
- **Piece 5:** Streaming (2 hours, HIGHEST risk)

**Safety Strategy:**
- Create feature branch: `feature/demo-polish`
- Each piece has feature flag for easy disable
- Test with curl after each piece
- Verify /getPrice still works (must return £1,958)
- Deploy to GCF and test live before merging
- Keep `/chat` non-streaming, add `/chat-stream` separately

**Total Time Estimate:** 5 hours (including thorough testing)

**Next Steps:**
1. ✅ Update all .md files (this session)
2. Create feature branch
3. Implement pieces 1-5 incrementally
4. Test at each stage
5. Tag: `demo-ready-demo-polish-complete`

---

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

**Additional Changes:**
7. ✅ **Added "Deliberate Change Protocol"** (revised from initial version)
   - Lines 233-344 in .claude/instructions.md: Protocol to prevent regressions AND bloat
   - **Revised approach:** Prefer simplicity and code removal over adding duplicates
   - Establishes preference hierarchy: Remove > Modify > Add (revised from Add > Modify)
   - Requires explicit justification for ANY change (add, modify, or remove)
   - Includes four code examples (worst, best, good, acceptable approaches)
   - Added baseline testing requirement before/after any code changes

**Deliberate Change Protocol:**
- **Best:** Remove unnecessary code, simplify existing code
- **Good:** Modify existing code to handle new case (if cleaner)
- **Acceptable:** Add new code if truly needed (avoid duplication)
- **Worst:** Add duplicate/similar code that bloats the codebase
- **Key principle:** "Prefer simplicity and fewer lines over bloat"
- **Decision tree:** Can I remove? → Can I modify? → Must I add?

**Additional Changes:**
8. ✅ **Added "Demo-Ready State Protocol"**
   - Lines 453-575 in .claude/instructions.md: Comprehensive workflow to keep main always demo-ready
   - Feature branch workflow - all development in branches, never directly on main
   - Git tagging strategy - tag every demo-ready state for easy rollback
   - Emergency revert procedures - quick recovery if something breaks
   - Tag naming convention: `demo-ready-YYYY-MM-DD` or `demo-ready-v2.x.x`

**Demo-Ready State Protocol:**
- **Main branch = ALWAYS demo-ready** (never broken)
- **Feature branches = development** (safe to break, debug, experiment)
- **Tags = rollback points** (can revert to any demo-ready state instantly)
- **Merge to main only when tested** (local + deployed testing required)
- **Emergency revert:** `git revert -m 1 HEAD` or `git reset --hard <tag>`

**Current Demo-Ready State:**
- Tag: `demo-ready-2025-11-02-baseline`
- Description: v2 baseline with all v1 functionality working
- Status: ✅ Deployed and operational

**Additional Changes:**
9. ✅ **Added "Living Documentation Protocol"**
   - Lines 162-351 in .claude/instructions.md: Comprehensive documentation maintenance protocol
   - Five-part documentation workflow: comments, logging, architecture, design, context
   - Documentation checklist before marking features complete
   - Examples of good comments, logging, and doc updates
   - Clear guidance on when and what to update

**Living Documentation Protocol:**
- **Code comments** - Explain WHY, not just WHAT
- **Debug logging** - Log important operations with appropriate levels
- **Architecture docs** - Update ARCHITECTURE.md and TECHNICAL_GUIDE.md when structure changes
- **Design docs** - Update PRD.md, README.md, CHANGELOG.md when features change
- **Context.md** - Update every session with what was built
- **Key principle:** "Docs must evolve with code - stale docs are worse than no docs"

**Documentation Checklist:**
- [ ] Code comments explain WHY for non-obvious logic
- [ ] Debug logging for important operations
- [ ] ARCHITECTURE.md updated if architecture changed
- [ ] TECHNICAL_GUIDE.md updated if technical approach changed
- [ ] PRD.md updated if features changed
- [ ] README.md updated if user-facing changes
- [ ] CHANGELOG.md updated with version entry
- [ ] .claude/context.md updated with session summary

**Commits:**
- e703f56: "v2: Remove all 'experimental' references - change to production development status"
- 3fe1741: "v2: Document session changes in context.md"
- 34d35ab: "v2: Clarify testing approach - Claude tests, no frameworks"
- 87638c3: "v2: Update context.md with testing approach documentation"
- 3ac6aa7: "v2: Clarify instructions - definitions, deployment, phases, line numbers"
- c9b4203: "v2: Document instruction clarifications in context.md"
- 8a694d7: "v2: Add 'Working Code Protection Protocol' to prevent regressions"
- 67e36de: "v2: Document Working Code Protection Protocol in context.md"
- 53f0021: "v2: Revise protocol to prefer simplicity and code removal over bloat"
- 17e8fd3: "v2: Update context.md with revised protocol (simplicity over bloat)"
- 79f3fe6: "v2: Add Demo-Ready State Protocol with feature branches and tags"
- 30c9f0c: "v2: Document Demo-Ready State Protocol in context.md"
- f36e0fa: "v2: Add Living Documentation Protocol - keep all docs synchronized"

**Tags:**
- demo-ready-2025-11-02-baseline: v2 baseline with all v1 functionality working

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

### Active Development: Chat Agent Transformation (COMPREHENSIVE PLAN)

**Goal:** Transform v2 into conversational chat agent with Grok LLM via OpenRouter

**User Requirements:**
- Full-screen chat experience (like ChatGPT/Claude)
- 1-hour session TTL, "New Conversation" button
- Natural language understanding with LLM
- Instant pricing + guided quoting (clarifying questions)
- Product comparisons, budget search, fabric search by color
- Voice input: Later phase (focus on chat first)

**Implementation Status:**

**PHASE 1A: Frontend Chat UI** ✅ COMPLETED
- [x] Piece 1.1: Chat message container with scrolling
- [x] Piece 1.2: Message input area (auto-resize textarea)
- [x] Piece 1.3: Typing indicator (animated dots)
- [x] Piece 1.4: UI polish (themes, fonts, colors, alignment)
- [x] Piece 1.5: Distinct user/agent colors (dark gray vs theme-colored)
- [x] Piece 1.6: Plus Jakarta Sans font applied

**PHASE 1.5: Backend Connection** ✅ COMPLETED
- [x] Connect frontend to real v2 GCF backend
- [x] Replace simulateBackendResponse() with fetch()
- [x] Test with real product queries
- [x] Add error handling and helpful messages
- [x] Verify all examples work with curl

**PHASE 1C: Grok LLM Integration (OpenRouter)** ⏳ NEXT
- [ ] Piece 3.1: OpenRouter API setup (API key: already have it)
- [ ] Piece 3.2: Create LLM conversation handler (system prompt, history)
- [ ] Piece 3.3: Implement tool/function calling (get_price, compare, etc.)

**PHASE 1B: Backend Session Memory** 🔜 UPCOMING
- [ ] Piece 2.1: Create session store (in-memory dict, 1-hour TTL)
- [ ] Piece 2.2: Add session endpoints (create, message, history)
- [ ] Piece 2.3: Store conversation context (last product, fabric, quote items)

**PHASE 1D: Enhanced Backend Tools** 🔜 UPCOMING
- [ ] Piece 4.1: compare_products() - side-by-side comparison
- [ ] Piece 4.2: get_variants() - all sizes/depths/covers
- [ ] Piece 4.3: search_by_budget() - products under max price
- [ ] Piece 4.4: get_fabric_info() - material, durability, lifestyle
- [ ] Piece 4.5: calculate_quote() - itemized total with add-ons
- [ ] Piece 4.6: search_fabrics_by_color() - "bluish fabrics"

**PHASE 1E: Integration & Polish** 🔜 UPCOMING
- [ ] Piece 5.1: Connect frontend to new backend (replace simulateBackendResponse)
- [ ] Piece 5.2: Add suggested actions based on context
- [ ] Piece 5.3: Error handling & fallbacks
- [ ] Piece 5.4: Add debug logging
- [ ] Piece 5.5: Update all documentation

**Files to Create/Modify:**
- `main.py` - Add conversation manager, LLM integration, tools
- `session_manager.py` (new) - Handle session memory
- `llm_handler.py` (new) - Grok/OpenRouter integration
- `tools.py` (new) - All tool functions
- `index.html` - Connect to new backend endpoints
- `requirements.txt` - Add openai, python-dotenv
- `.env` (new) - Store OpenRouter API key

**OpenRouter Configuration:**
- API Key: `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`
- Model: `x-ai/grok-beta` (cheapest option)
- Base URL: `https://openrouter.ai/api/v1`

**Estimated Time:** ~18 hours (35 pieces, 15-60 min each)

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

## ⚡ CRITICAL: Grok-4 vs Grok-4-fast Performance Learnings

**Date:** 2025-11-02
**Context:** Demo Polish Phase - Timeout Investigation

### 🚨 PROBLEM: Backend Timeouts (120+ seconds)

**Symptoms:**
- Consistent timeouts at 120 seconds
- "upstream request timeout" errors
- User experiencing connection failures

**Initial Hypothesis (WRONG):**
1. ❌ Frontend HTML formatting causing issues → NO (runs in browser)
2. ❌ SYSTEM_PROMPT too large (320 lines) → NO (reducing to 60 lines didn't help)
3. ❌ Backend deployment issues → NO (deployment successful)

**Root Cause (CORRECT):**
✅ **Grok-4 is inherently slow** - prioritizes reasoning over speed

### 📊 Evidence from GCF Logs

Execution `J3qpzBQzdA5h`:
```
09:04:39 - Iteration 1: Calling Grok...
09:04:55 - Iteration 2: Calling Grok... (16 seconds)
09:09:19 - Final response (4 minutes 24 seconds!)
```

**Grok-4 takes 4-5 minutes per API call** even with lean SYSTEM_PROMPT

### 🔍 Research Findings

- Grok-4 has ~13.5 seconds Time to First Token (TTFT) latency
- Prioritizes intelligence and reasoning over speed
- Known characteristic since release (not a bug)
- **Grok-4-fast** exists specifically for performance

### ✅ SOLUTION: Switch to Grok-4-fast

**Change:** Environment variable `GROK_MODEL` from `x-ai/grok-4` to `x-ai/grok-4-fast`

**Results:**

| Metric | Grok-4 | Grok-4-fast | Improvement |
|--------|--------|-------------|-------------|
| Response Time | 120s+ (timeout) | **7.5-10s** | **16x faster** |
| Token Usage | ~11,000 | ~4,300 | 2.5x more efficient |
| Formatting Quality | ✅ Good | ✅ Good | Maintained |
| Upselling Quality | ✅ Good | ✅ Good | Maintained |

**Live Test Results:**
```bash
curl test → 7.5 seconds
Comparison query → 10.7 seconds
All formatting works perfectly
```

### 🎯 KEY LESSONS FOR FUTURE

1. **ALWAYS use Grok-4-fast for production** - Never use standard Grok-4 for user-facing features
2. **Check model performance characteristics** - Not all issues are code-related
3. **Test with actual API calls** - Logs are your friend for diagnosing LLM issues
4. **Token count matters less than model speed** - Reducing SYSTEM_PROMPT didn't fix the issue
5. **Frontend changes can't cause backend timeouts** - Browser-side formatting has no impact on API response time

### 📝 Configuration for Future Reference

**Correct GCF Environment Variables:**
```bash
GROK_MODEL=x-ai/grok-4-fast
OPENROUTER_API_KEY=sk-or-v1-...
LOG_EXECUTION_ID=true
```

**GCF Timeout Setting:**
- 120 seconds (allows for occasional spikes)
- With Grok-4-fast, responses typically complete in 7-10s

### ⚠️ DO NOT

- ❌ Use `x-ai/grok-4` for user-facing features (too slow)
- ❌ Assume timeout issues are always code-related
- ❌ Skip checking GCF logs when diagnosing API issues
- ❌ Reduce SYSTEM_PROMPT unnecessarily (quality matters)

### ✅ DO

- ✅ Use `x-ai/grok-4-fast` for production (7-10s response time)
- ✅ Monitor GCF logs for actual LLM response times
- ✅ Test with curl to measure real-world performance
- ✅ Keep SYSTEM_PROMPT focused but comprehensive

**Status:** ✅ **RESOLVED - PRODUCTION READY**

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
