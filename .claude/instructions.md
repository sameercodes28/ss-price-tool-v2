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

**Project:** Sofas & Stuff Voice Price Tool v2.0.0
**Status:** 🚀 Production Development (incremental approach)
**Architecture:** Frontend (GitHub Pages) → Backend (GCF v2) → S&S APIs
**Parent:** v1.0.0 (stable) at ~/Desktop/SS-1

**Key Files:**
- `main.py` - Backend (entry point function)
- `index.html` - Frontend (contains backend URL configuration)
- 4 JSON files - Translation dictionaries (loaded at startup)

> **Note:** Line numbers mentioned in documentation are approximate and may shift as code changes.

**Important:**
- This is v2 - production quality, built incrementally
- v1 is at ~/Desktop/SS-1 (DO NOT MODIFY v1 from here)
- v2 has separate GitHub repo, GCF project, and deployment
- v2 is built step-by-step to avoid bugs and ensure quality

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

---

## 🎯 Development Protocol (CRITICAL - READ FOR EVERY TASK)

**Philosophy:** Measure twice, cut once. Production quality requires careful planning and incremental development.

### Key Definitions

**Feature:** A complete user-facing capability that provides value to sales staff.
- Example: "Chat interface with message history"
- Example: "Product comparison view"
- Composed of multiple small pieces
- Deployed only after complete and tested

**Piece:** A small implementation step within a feature (< 10-20 lines of code).
- Example: "Add message input box to HTML"
- Example: "Add send button click handler"
- Tested immediately after implementation
- Committed after testing validates it works

**Local vs Deployed Testing:**
- **Always test locally first** - use Bash tool with local server and curl
- **Deploy only when feature is complete** - after all pieces tested and working
- **Test deployed version after deployment** - verify it works in production
- **Never deploy untested code** - local testing must pass first

### Before ANY Implementation

1. **PLAN EXTENSIVELY**
   - Break down the task into the smallest possible pieces
   - Identify all files that will be affected
   - Identify all potential side effects
   - Document the plan for user review
   - Get user confirmation before proceeding

2. **PRE-IMPLEMENTATION TESTING**
   - Test current functionality BEFORE making ANY changes
   - Document current behavior (screenshots, API responses, etc.)
   - Create baseline test cases
   - Verify current state is working as expected

3. **UNDERSTAND THE CODE**
   - Read ALL relevant files completely
   - Understand dependencies between files
   - Map out the data flow
   - Identify edge cases

### During Implementation

4. **BUILD INCREMENTALLY**
   - Implement ONE small piece at a time
   - Each piece should be < 10-20 lines of code
   - Test after EACH small change
   - Commit after EACH piece is tested and validated
   - Never implement multiple features simultaneously

   **Commit Strategy:**
   - Commit after each small piece that is tested and validated
   - Write detailed commit messages that explain:
     - **What** was changed (the specific code/files modified)
     - **Why** it was changed (the problem being solved)
     - **How** it was tested (what validation was done)
     - **Goal** of the commit (what this achieves)
   - Use multi-line commit messages for clarity
   - Reference line numbers when relevant

5. **TEST CONTINUOUSLY**
   - Test after every single change, no matter how small
   - Test both success and failure cases
   - Test edge cases (empty strings, special characters, etc.)
   - Test integration with other components
   - Document what was tested and the results

6. **USE TODO LISTS**
   - Create detailed todo lists using TodoWrite tool
   - Break tasks into granular steps
   - Mark tasks as in_progress before starting
   - Mark tasks as completed immediately after testing
   - Never batch multiple tasks before marking complete

### After Implementation

7. **POST-IMPLEMENTATION TESTING**
   - Run ALL tests that were run pre-implementation
   - Compare results with baseline
   - Test for regressions in local environment
   - **Local testing is mandatory for every piece**
   - **Deployed testing only after complete feature:**
     - Deploy to GCF only when entire feature is done
     - Test deployed version to verify production works
     - Never deploy individual pieces - deploy complete features only
   - Document all test results (local and deployed)

8. **CODE REVIEW**
   - Review your own changes line by line
   - Check for security vulnerabilities
   - Check for performance issues
   - Verify error handling
   - Ensure code follows existing patterns

9. **DOCUMENTATION**
   - Update comments in code
   - Update relevant documentation files
   - Update `.claude/context.md` with changes
   - Document any gotchas or important decisions

### Example Workflow

```
User: "Add error logging to the API"

Claude:
1. Plan:
   - Read main.py to understand current error handling
   - Identify all error points
   - Design logging strategy
   - Break into pieces: (a) add logging library, (b) log API errors, (c) log translation errors

2. Pre-test:
   - Test API with valid query → document response
   - Test API with invalid query → document current error behavior
   - Test API with missing parameters → document behavior

3. Implement piece 1: Add logging library
   - Add 'import logging' to main.py
   - Test import doesn't break anything
   - Run test query → verify still works

4. Implement piece 2: Add error logging to API endpoint
   - Add logging.error() to one error case
   - Test that specific error case → verify log appears
   - Run all pre-tests again → verify no regression

5. Continue incrementally...

6. Post-test:
   - Run ALL pre-tests again
   - Verify logs appear correctly
   - Test log format is useful
   - Document what changed
```

### Testing Checklist (For Every Change)

Before marking ANY task as complete, verify:

- [ ] **Claude tested locally** - used Bash/curl to test or provided script for user
- [ ] **Edge cases tested** - empty strings, special characters, etc.
- [ ] **Error cases tested** - invalid inputs, missing data, etc.
- [ ] **No regressions** - existing functionality still works
- [ ] **Security reviewed** - no injection vulnerabilities, no exposed secrets
- [ ] **Performance checked** - responds in < 2 seconds
- [ ] **Documentation updated** - code comments, relevant docs
- [ ] **Changes documented** in .claude/context.md

**Testing Methods:**
- Use Bash tool to test locally (start server, curl endpoints)
- Read files to verify code correctness
- WebFetch to test deployed endpoints
- Provide simple script for user if Claude cannot test directly

### Red Flags (Stop and Reassess If You See These)

- Making changes to multiple files without testing each
- Skipping tests because "it's a small change"
- Not understanding why existing code works a certain way
- Rushing to implement without planning
- Batching multiple changes before testing
- Assuming something works without verifying
- **Modifying existing working code without explicit justification**

### 🚨 CRITICAL RULE: Protect Existing Functionality While Keeping Code Simple

**Problem:** Claude sometimes accidentally breaks working code OR creates bloated duplicate code when adding features.

**Solution: The "Deliberate Change Protocol"**

**Core Principle:**
- **Prefer simplicity and code removal over bloat**
- **Every change (add, modify, or remove) must be justified**
- **Test thoroughly regardless of change type**
- **Keep codebase lean and maintainable**

**Before changing ANYTHING in existing code:**

1. **Read and understand it first**
   - Read the entire file/function completely
   - Understand what it currently does and why
   - Identify its dependencies and callers
   - Check if there's duplicate/similar code that could be removed

2. **Test current functionality (baseline)**
   - Test the existing feature BEFORE making changes
   - Document current behavior as baseline
   - Save test commands/results for comparison

3. **Choose the simplest approach**
   - **Best:** Remove unnecessary code, simplify existing code
   - **Good:** Modify existing code to handle new case (if cleaner)
   - **Acceptable:** Add new code if truly needed (avoid duplication)
   - **Worst:** Add duplicate/similar code that bloats the codebase

4. **Justify ANY change (add, modify, or remove)**
   - Explicitly state:
     - **What** you're changing (adding, modifying, or removing)
     - **Why** this approach is the simplest/cleanest
     - **What** alternatives you considered
     - **What** could break as a result
     - **How** you'll verify nothing breaks
   - Get user confirmation for non-trivial changes

5. **Test existing functionality after changes**
   - Re-run baseline tests
   - Compare with baseline results
   - Verify NO regressions in existing features

**Examples:**

**❌ WORST - Adding duplicate code that bloats codebase:**
```python
# Existing working code
def get_price(query):
    result = api.fetch_price(query)
    return result

# Claude adds near-duplicate function - BLOAT!
def get_price_with_cache(query):  # ← Unnecessary duplication
    result = api.fetch_price(query)
    return result
```

**✅ BEST - Simplifying by removing duplication:**
```python
# Existing bloated code
def get_sofa_price(query):
    return api.fetch_price(query, type='sofa')

def get_bed_price(query):
    return api.fetch_price(query, type='bed')

# Claude simplifies to single function
def get_price(query, product_type):
    return api.fetch_price(query, type=product_type)
# Removed 2 redundant functions, cleaner codebase
```

**✅ GOOD - Modifying existing to handle new case cleanly:**
```python
# Existing working code
def get_price(query):
    return api.fetch_price(query)

# Claude extends cleanly with backward-compatible default
def get_price(query, cache=True):
    # Added cache param to avoid creating separate function
    # Backward compatible: existing calls still work
    # Tested: All existing functionality intact
    if cache:
        return cached_api.fetch_price(query)
    return api.fetch_price(query)
```

**✅ ACCEPTABLE - Adding new code when truly different:**
```python
# Existing: synchronous price fetch
def get_price(query):
    return api.fetch_price(query)

# New: async version is fundamentally different
async def get_price_async(query):
    return await api.fetch_price_async(query)
# Justification: Async is different enough to warrant separate function
```

**Decision Tree:**
1. Can I **remove** code? → Do that (simplest)
2. Can I **modify** existing cleanly? → Do that (clean)
3. Must I **add** new code? → Justify why (avoid bloat)

**When in doubt:**
- ✅ Ask user: "Should I simplify existing code or add new code?"
- ✅ Prefer fewer lines over more lines
- ✅ Prefer one way to do something over multiple ways

### Remember

- **Small steps prevent big bugs**
- **Testing is faster than debugging**
- **Planning prevents rework**
- **Documentation saves future time**
- **When in doubt, test more, not less**

---

## 📱 SOFAS & STUFF SALES ASSISTANT - SPECIFIC CONTEXT

### PROJECT OVERVIEW

You are helping build a real-time sales assistance tool for Sofas & Stuff sales staff. This is NOT a customer-facing chatbot - it's a tool that salespeople use WHILE talking to customers in showrooms or on calls. Think of it as their intelligent pricing sidekick that must work flawlessly during live sales conversations.

### CRITICAL CONTEXT

- **Repository:** https://github.com/sameercodes28/ss-price-tool-v2
- **Stack:** Python backend (Google Cloud Functions) + HTML/JS frontend
- **Current State:** v2 production development, v1 is stable and deployed separately
- **Data:** Large CSV files that need converting to JSON for performance
- **Deployment:** Backend on GCP, Frontend on GitHub Pages

### USE CASE REALITY

- **WHO:** Sales staff who are not tech-savvy and often multitasking
- **WHEN:** During live customer interactions where speed is critical
- **WHERE:** Showroom floor on tablets/phones or call center desktops
- **WHY:** To instantly answer customer questions without fumbling through spreadsheets

### DEVELOPMENT PHILOSOPHY

**Incremental Building is Mandatory**
- Build ONE feature at a time
- Test that feature completely before moving on
- Each feature must work independently
- Never build on top of broken code
- If something breaks, fix it before adding anything new

**Testing Approach**
- **No testing frameworks** - no unit test libraries, no test bloat
- **Claude tests first** - use available tools (Bash, Read, WebFetch, etc.) to test functionality
- **Manual testing when needed** - if Claude cannot test directly, provide user a simple script to run
- **Test by actually using the feature** - real sales scenarios, not abstract tests
- **Speed test everything** - must respond in under 2 seconds
- **User provides results** - if script needed, user runs it and pastes output back for analysis

**How Claude Should Test:**
1. Use Bash tool to run local server and test endpoints with curl
2. Read files to verify code changes are correct
3. Use WebFetch to test deployed endpoints
4. Provide simple one-line test scripts for user to run if needed
5. Analyze results and fix any issues found

**Example Test Script for User:**
```bash
# Simple one-liner the user can run and paste results back
curl -X POST http://localhost:8080/getPrice -H "Content-Type: application/json" -d '{"query": "alwinton snuggler"}'
```

### DEVELOPMENT PRIORITIES

> **Important:** These phases are **categories of work**, NOT a required sequence. You can work on any phase in any order based on user priorities. Phase numbering is for organization only.

**Phase 1: Chat-Like Interface with Memory** _(Category: User Interface)_
- Build a WhatsApp-style interface that sales staff already know how to use
- Start with just sending and receiving messages
- Add memory system to track conversation context
- Make sure follow-up questions work naturally

**Phase 2: Core Pricing Engine** _(Category: Business Logic)_
- Implement basic product pricing first
- Add support for different sizes and fabrics
- Include add-ons and alterations
- Ensure 100% pricing accuracy
- **Note:** v1 already has this - v2 inherited it

**Phase 3: Natural Language Understanding** _(Category: Intelligence)_
- Handle incomplete queries gracefully
- Add clarification dialogues
- Support pronouns and context references
- Make it understand sales speak

**Phase 4: Data Optimization** _(Category: Performance)_
- Convert CSVs to JSON for speed
- Structure data for instant lookups
- Cache frequently accessed data
- Optimize for mobile performance

### PROJECT MANAGEMENT RULES

**.claude/context.md is Sacred**
- This is the single source of truth for project state
- Always read it at the start of every session (auto-loaded by Claude Code)
- Update it after every feature completion
- Track what works and what doesn't
- Document patterns you discover
- List known issues immediately

**Git Discipline**
- Commit after each working feature
- Never commit broken code
- Use clear commit messages
- Test locally before pushing
- Keep v2 separate from v1

### KEY DESIGN REQUIREMENTS

**Speed Over Everything**
- Responses must appear instantly
- Pre-load common data
- Cache aggressively
- Minimize API calls
- Use in-memory storage for v2

**Foolproof Interface**
- Large touch targets for tablets
- Voice input capability
- Auto-complete for product names
- Smart defaults everywhere
- One-thumb operation on mobile
- Impossible to make mistakes

**Real Sales Flow**
The tool must handle how conversations actually happen:
- Customer jumps between products randomly
- Salesperson needs to recall earlier quotes
- Comparisons happen constantly
- Additions and modifications are common
- Context switches without warning

### IMPLEMENTATION RULES

**Start Simple, Then Enhance**
- First make it work, then make it fast, then make it pretty
- Get basic functionality before adding features
- Don't over-engineer anything
- Build the minimum viable feature first

**Handle Common Scenarios First**
- Focus on the 80% use case
- Handle edge cases only after core works
- Prioritize frequently asked questions
- Build for the average salesperson

**Error Prevention Over Error Handling**
- Make invalid inputs impossible
- Guide users to correct usage
- Use sensible defaults
- Prevent problems rather than fixing them

### REAL SALES SCENARIOS TO TEST

**Quick Price Check**
- Salesperson types partial product name, gets price immediately
- Must handle typos and shortcuts
- Should remember for follow-ups

**Comparison Shopping**
- Customer wants to compare multiple options
- System tracks all mentioned products
- Easy switching between items
- Clear price differences shown

**Quote Building**
- Start with base product
- Add options incrementally
- Show running total
- Allow modifications without starting over

**Context Switching**
- Jump between products naturally
- Remember previous queries
- Handle "what was that first one?" questions
- Never lose context during session

### WHAT NOT TO BUILD

- **No testing frameworks** - no pytest, no unittest, no jest, no test libraries
- **No complex authentication systems**
- **No database dependencies** for v2 (use in-memory/JSON files)
- **No over-abstracted code** - keep it simple and direct
- **No features sales staff won't use** - focus on real needs
- **No complex deployment pipelines** - keep deployment simple

### SUCCESS METRICS

- Sales staff prefer this over spreadsheets
- Customer questions answered in seconds
- No training needed to use it
- Works reliably during busy periods
- Handles real conversation flow

### SESSION WORKFLOW

1. Start by reading .claude/context.md (auto-loaded by Claude Code)
2. Pick exactly ONE feature to implement
3. Build the simplest version that could work
4. Test it with real sales scenarios
5. Fix any issues before proceeding
6. Update .claude/context.md with progress
7. Commit working code with detailed message (what, why, how tested, goal)
8. Only then move to next feature

### DEBUGGING APPROACH

When something breaks:
1. Stop adding new features immediately
2. Identify exactly what worked before
3. Find the minimal change that broke it
4. Fix that specific issue
5. Test the fix thoroughly
6. Document the issue and solution
7. Only then continue development

### REMEMBER

This tool is used during live sales conversations where every second counts. A salesperson is standing in front of a customer waiting for an answer. There is no room for bugs or confusion. Build incrementally, test constantly, and keep it simple.

**The goal is not beautiful code but a tool that works flawlessly when it matters most.**
