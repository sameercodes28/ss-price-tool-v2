# Claude Context - Sofas & Stuff Price Tool - v2

**Last Updated:** 2025-11-03 (Part 10: Critical Pricing Fixes & API Migration - USER RESTARTING)
**Current Version:** v2.5.0 (Production Hardened - Hotfixed)
**Project Status:** 🚀 Production - Deployed, Testing Pending After Restart

## 🔥 CRITICAL: SIMPLICITY PRINCIPLE

**NEVER repeat the markdown rendering disaster (2025-11-03).**

When implementing ANY rendering/parsing feature:

### Rule 1: Start Simple, Stay Simple
- ❌ DON'T: Add external library + fallback + try/catch
- ✅ DO: Write 10 lines of simple regex, test it, ship it

### Rule 2: Test Locally FIRST
- Create `/test.html` with the EXACT code
- Test in browser locally BEFORE deploying
- If it doesn't work locally, it won't work deployed

### Rule 3: Believe The User
- If user says "not working in Safari (fresh browser)", STOP blaming cache
- That means YOUR CODE IS BROKEN
- Go back to local testing

### Rule 4: One Code Path Only
- Multiple code paths = multiple failure modes
- If you add a fallback, you DOUBLE the testing burden
- Avoid: primary path → fallback path → error handler
- Prefer: one simple path that always works

### Rule 5: No "Fix It Later"
- Don't deploy broken code and debug in production
- Don't make user test 5 times while you fumble
- Get it working locally, THEN deploy ONCE

### Example: Markdown Rendering

**❌ WHAT I DID (WRONG):**
```javascript
// 60 lines, 2 libraries, 3 code paths, untested fallback
if (typeof marked !== 'undefined') {
    try { return marked.parse(content); }
    catch { /* fallback with escapeHtml bug */ }
}
```

**✅ WHAT I SHOULD HAVE DONE:**
```javascript
// 15 lines, zero dependencies, one path, easy to test
return content
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
```

**If this ever happens again:**
1. STOP immediately
2. Create `/test-markdown.html` with 20 lines
3. Test the regex locally
4. If it works, copy to main code
5. Deploy ONCE
6. User confirms working
7. Done

---

## 📋 Next Session Priority

**✅ v2.5.0 STABLE - HOTFIXES DEPLOYED**

Backend: revision 00021-luw (CORS fix)
Frontend: Latest deployment (timing tracking removed)

**Status:** 🟢 **ALL SYSTEMS OPERATIONAL**
- CORS configuration fixed ✅
- JavaScript crash bug fixed ✅
- Timing tracking removed for simplicity ✅
- Markdown rendering working ✅

**✅ COMPLETED SESSION (Part 9):**
1. ✅ **CRITICAL:** Fixed CORS configuration (added X-Request-ID header)
2. ✅ **CRITICAL:** Fixed Analytics initialization crash
3. ✅ **SIMPLIFICATION:** Removed timing tracking (57 lines)
4. ✅ **DOCS:** Comprehensive debugging session documentation
5. ✅ **PREVENTION:** Added checklists and protocols for future

**🟡 KNOWN ISSUE: Sofas & Stuff Website Down**

External dependency - S&S website showing contact page only.
- Their API returns 400 errors
- Our system handles this gracefully (returns fallback message)
- Will auto-resume when S&S website recovers
- **This is not our bug** - external service downtime

**⏭️ FUTURE CONSIDERATIONS (DEFERRED):**
- Structured JSON logging (not critical)
- localStorage quota detection UI (not critical)
- Request/response size limits (not critical)
- Complex function refactoring (not critical)

**🤝 DEBUGGING WORKFLOW (IMPORTANT):**

When debugging issues together, USER should:
1. Visit https://[domain]/debug.html
2. Click "Generate Debug Report"
3. Copy the markdown report
4. Share in Claude chat

This gives Claude:
- API health status
- Recent queries and errors
- Full event log
- System diagnostics

**Without this, Claude is blind to production issues!**

Future improvements to debug dashboard (implement as needed):
- Add GCF log streaming (show backend errors in real-time)
- Add "Test All APIs" button (one-check health check)
- Add query replay (reproduce exact user scenario)
- Add comparison mode (before/after for debugging regressions)
- Export bug report as GitHub issue template

---

## 🚨 CRITICAL LEARNING: PART 9 DEBUGGING SESSION (2025-11-03)

**Context:** User reported "connection error" on ALL queries despite backend working perfectly.

### Three Cascading Bugs Found & Fixed:

#### **Bug 1: CORS Configuration Missing X-Request-ID Header** 🔴 CRITICAL
**Impact:** ALL frontend requests failed with CORS preflight errors
**Root Cause:** Phase 3 added `X-Request-ID` header for request tracing, but forgot to update backend CORS configuration
**Error Message:** `Request header field x-request-id is not allowed by Access-Control-Allow-Headers in preflight response`

**Fix:** Added `X-Request-ID` to CORS allowed headers in `main.py:753`
```python
# BEFORE
response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')

# AFTER
response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Request-ID')
```

**Commit:** `5046fa6` - CRITICAL FIX: Add X-Request-ID to CORS allowed headers
**Deployed:** Backend revision 00021-luw

---

#### **Bug 2: Analytics timingBreakdowns Array Not Initialized** 🔴 CRITICAL
**Impact:** After CORS fix, queries succeeded but responses crashed before displaying
**Root Cause:** Phase 3 added `debugData.timingBreakdowns` array, but `loadData()` fallback didn't initialize it
**Error Message:** `TypeError: Cannot read properties of undefined (reading 'push')`

**The Insidious Flow:**
1. Backend returns response ✅
2. Frontend calls `addMessage()` and formats response ✅
3. Then calls `Analytics.trackTiming()` at line 2882
4. **JavaScript crashes** trying to push to undefined array 💥
5. Error handler shows "connection error" instead of formatted response
6. User sees error despite response being perfectly formatted in memory

**Fix:** Added `timingBreakdowns: []` to debugData fallback in `index.html:2326`

**Commit:** `3fb0768` - FIX: Initialize timingBreakdowns array in Analytics loadData

---

#### **Bug 3: Timing Tracking Added Unnecessary Complexity** 🟡 DESIGN FLAW
**Impact:** Caused Bug #2, added 57 lines of complexity with minimal value
**Root Cause:** Phase 3 added performance timing as "nice to have" without considering cost/benefit

**What it did:**
- Tracked network time, parse time, render time
- Stored 100 timing objects in localStorage
- Added 6 variables + 1 function + multiple tracking calls

**Why it wasn't worth keeping:**
- ❌ Just caused production crash
- ❌ Not actively monitored or used
- ❌ Debug dashboard already has essential metrics
- ❌ Added maintenance burden

**Fix:** Removed entire timing tracking subsystem (57 lines)
- Removed `trackTiming()` function
- Removed all `performance.now()` timing variables
- Removed `timingBreakdowns` array
- Kept essential debug tracking (errors, responses, API logs)

**Commit:** `a31ae2b` - Simplify analytics: Remove timing breakdown tracking

---

### Root Cause Analysis

**Why did this happen?**

1. **Incomplete feature implementation** - Added `X-Request-ID` header to frontend, but forgot backend CORS update
2. **Insufficient testing** - Phase 3 changes weren't tested end-to-end before deployment
3. **Feature creep** - Added "nice to have" timing tracking that introduced bugs
4. **Poor error visibility** - Real error (undefined array) was masked by generic "connection error"

**Why was it hard to debug?**

1. **Browser caching** - User kept seeing old cached code even after fixes deployed
2. **Multiple simultaneous bugs** - CORS issue masked the timing issue
3. **Confusing error messages** - "Connection error" appeared even when backend was healthy
4. **Missing tools** - Initially didn't use debug.html to see client-side errors

---

### Prevention Strategies

#### **1. CORS Header Checklist (CRITICAL)**

**RULE:** Whenever you add a new custom header to frontend requests, IMMEDIATELY update backend CORS.

**Checklist:**
- [ ] Added header to frontend? (e.g., `X-Request-ID`)
- [ ] Updated `main.py` OPTIONS handler to allow it
- [ ] Tested with curl CORS preflight request
- [ ] Verified in browser DevTools Network tab

**Example Test:**
```bash
curl -X OPTIONS "https://[backend-url]/chat" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,X-New-Header" \
  -H "Origin: https://[frontend-url]" -i
```

#### **2. Analytics Initialization Pattern**

**RULE:** All arrays used in Analytics MUST be initialized in THREE places:

1. **Initial object definition** (line ~2057)
2. **loadData() fallback** (line ~2285)
3. **Any place that might clear/reset the object**

**Example:**
```javascript
// 1. Initial definition
debugData: {
    newArray: [],  // ✅ Add here
    // ...
}

// 2. loadData() fallback
this.debugData = data.debugData || {
    newArray: [],  // ✅ AND here
    // ...
}
```

#### **3. Feature Addition Checklist**

Before adding ANY new tracking/monitoring feature:

**Ask:**
- [ ] **Is this actively monitored?** Will anyone look at this data regularly?
- [ ] **Does it solve a real problem?** Do we have evidence of the issue it's tracking?
- [ ] **What's the cost?** Code complexity, localStorage space, performance impact
- [ ] **What are alternatives?** Can we use existing tools (debug.html, logs)?
- [ ] **Test thoroughly** - Can I break this? What are edge cases?

**Examples:**
- ✅ **Keep:** Error stacks (used for debugging), API logs (used for debugging)
- ❌ **Remove:** Timing breakdowns (not monitored, caused bugs)

#### **4. Deployment Testing Protocol**

**After ANY deploy to production:**

1. **Wait 2-3 minutes** for GitHub Pages to deploy
2. **Open incognito window** (avoid cache)
3. **Open DevTools Console** BEFORE testing
4. **Test core flows:**
   - Price query: "How much is alwinton snuggler pacific?"
   - Fabric search: "Velvet options"
   - Budget search: "Under £2000"
5. **Check for errors:**
   - Red errors in Console tab
   - Failed requests in Network tab (look for CORS, 400, 500 errors)
6. **If user reports issue:**
   - Ask for debug.html report IMMEDIATELY
   - Check browser console for JavaScript errors
   - Don't assume caching - verify with curl

#### **5. Emergency Debug Workflow**

**When user reports "connection error" or "not working":**

1. **Get debug data:**
   - Ask user to visit `/debug.html`
   - Get console logs (screenshot or copy/paste)
   - Check Network tab for failed requests

2. **Verify backend first:**
   ```bash
   curl -X POST '[backend-url]/chat' \
     -H 'Content-Type: application/json' \
     -d '{"messages": [{"role": "user", "content": "test"}], "session_id": "debug"}'
   ```

3. **Check CORS if backend works:**
   ```bash
   curl -X OPTIONS '[backend-url]/chat' \
     -H 'Access-Control-Request-Headers: Content-Type,X-Request-ID' \
     -i | grep -i access-control
   ```

4. **Verify frontend deployment:**
   ```bash
   curl -s 'https://[frontend-url]/index.html' | grep -i "[recent change identifier]"
   ```

5. **Don't blame cache until you verify:**
   - Check with incognito mode
   - Verify timestamp of deployed file
   - Use `curl` to see what's actually deployed

---

### Commits from Part 9 Debugging Session

1. `34578b1` - FIX: Add robust markdown parsing fallback for unstructured responses
2. `5046fa6` - CRITICAL FIX: Add X-Request-ID to CORS allowed headers
3. `3fb0768` - FIX: Initialize timingBreakdowns array in Analytics loadData
4. `a31ae2b` - Simplify analytics: Remove timing breakdown tracking

**Total:** 4 commits, 2 critical bugs fixed, 1 feature removed for simplification

---

## ⚠️ CRITICAL LEARNING: MESSAGE FORMATTING ISSUES

**USER FREQUENTLY HITS ISSUES WITH MESSAGE BUBBLE FORMATTING**

This is a recurring problem - when Grok returns markdown, it often doesn't render properly in the chat UI.

### Root Cause (Discovered 2025-11-03)

The `formatLLMResponse()` function in index.html has **two branches**:

1. **Structured responses** (with `### 💰 Price`, `### 🎯 Opportunities` sections)
   - Custom HTML parsing
   - Works correctly
   - Used for price queries

2. **Unstructured responses** (fabric searches, budget searches, general conversation)
   - **BUG WAS HERE:** Used `escapeHtml()` which converts markdown to plain text
   - This killed all formatting: `**bold**` → `**bold**` (not rendered)
   - Links, italics, lists all broken

### The Fix (index.html:2576-2590)

**ALWAYS use marked.js** for unstructured content:

```javascript
// If no structured content, treat as helpful message
if (!hasStructuredContent) {
    // ✅ CORRECT: Use marked.js to parse markdown
    if (typeof marked !== 'undefined') {
        try {
            html = '<div class="llm-suggestion-response">';
            html += marked.parse(content);  // This renders markdown properly
            html += '</div>';
            return html;
        } catch (e) {
            console.error('[ERROR] Marked.js parsing failed:', e);
        }
    }

    // ❌ WRONG: Don't use escapeHtml() - it destroys markdown
    // html += `<p>${escapeHtml(para)}</p>`; // This breaks formatting!
}
```

### When User Reports "Formatting Not Working"

1. **Check if Grok is outputting markdown correctly** (backend)
   - System prompt should specify formatting: `**bold**`, `_italic_`, `[link](url)`
   - Tool should return proper markdown in responses

2. **Check if formatLLMResponse handles it** (frontend)
   - Does the response have structured sections? (### 💰, ### 🎯, etc.)
   - If NO → Goes to unstructured branch → MUST use marked.js
   - If YES → Goes to structured branch → Custom HTML parsing

3. **Common mistakes to avoid:**
   - Using `escapeHtml()` on markdown content
   - Forgetting to call `marked.parse()`
   - Not checking if `marked` library is loaded
   - Assuming custom parsing handles all markdown syntax

### Files to Check

- **Backend:** `main.py` - System prompt formatting instructions
- **Frontend:** `index.html` - `formatLLMResponse()` function (around line 2558)
- **Library:** Marked.js loaded at line 30: `<script src="https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"></script>`

### Testing Checklist

After any formatting changes:
- [ ] Test structured response: "How much is Alwinton snuggler pacific?" (should show formatted price sections)
- [ ] Test unstructured response: "Velvet options" (should show **bold**, _italics_, [links](url))
- [ ] Test budget search: "Under £2000" (should render markdown properly)
- [ ] Check browser console for errors
- [ ] Hard refresh browser (Cmd+Shift+R) to bypass cache

---

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
- Frontend: ✅ Deployed to GitHub Pages → https://britishmade.ai/

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

## 🔧 Recent Changes Summary

**For detailed session-by-session history, see:** `.claude/session-history.md`

### Most Recent Sessions (Nov 2025)

**Part 10 - CRITICAL FIXES (⚠️ Testing Incomplete)**
- **Fixed pricing bug:** Removed dangerous fuzzy matching that caused "3 seater" → "4 seater" confusion (£155 price error)
- **Added prefix matching:** Allows "3 seater" to match "3 seater sofa" safely
- **Fabric hallucination fix:** Added system prompt rules (needs verification)
- **API migration:** Switched from OpenRouter to xAI direct API
- **Deployment fix:** Renamed entry point to `main()` for Cloud Functions Gen2
- **Commits:** 612390d, ca59eae, 70f13e1, 2f9623b
- **Status:** USER RESTARTED COMPUTER - Tests pending

**Part 9 - DEBUGGING SESSION (3 Critical Bugs Fixed)**
- **Bug #1:** CORS missing X-Request-ID header (all requests failed)
- **Bug #2:** Analytics timingBreakdowns not initialized (responses crashed)
- **Bug #3:** Removed unnecessary timing tracking (57 lines of complexity)
- **Deployed:** Backend revision 00021-luw

**Part 8 - v2.5.0 PRODUCTION RELEASE**
- Security: Removed phone number from error messages
- UX: Enhanced error messages with conversational tone
- Protection: Comprehensive rate limiting (backend + frontend)
- Monitoring: Health check endpoint with metrics
- **Commits:** 6963c3a, 1e518ff, c25e2b0, b78aeea

**Part 7 - ENHANCED DEBUGGABILITY**
- Auto-retry with exponential backoff
- Request ID tracing (X-Request-ID header)
- Comprehensive docstrings and JSDoc
- Enhanced error context capture

### Key Commits Reference
- `f06edde` - Update context.md Part 10
- `2f9623b` - Fix prefix matching
- `70f13e1` - CRITICAL: Remove fuzzy matching
- `ca59eae` - xAI API migration
- `612390d` - CRITICAL: Rename to main()
- `5046fa6` - CRITICAL: Fix CORS
- `3fb0768` - Fix Analytics init
- `a31ae2b` - Remove timing tracking
- `6963c3a` - Security: Remove phone number
- `1e518ff` - Improve error messages
- `c25e2b0` - Add rate limiting
- `b78aeea` - Add health check

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

*For detailed session history, see `.claude/session-history.md`*
*This file should be updated at the end of each v2 session to maintain continuity.*
