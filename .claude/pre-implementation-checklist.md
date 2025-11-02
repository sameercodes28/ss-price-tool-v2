# Pre-Implementation Checklist - Phase 1C

**Purpose:** Force myself to review all lessons learned BEFORE writing code
**Must complete:** ALL items before writing first line of code

---

## ☐ STEP 1: Review Past Mistakes

- [ ] Read `.claude/lessons-learned.md` completely
- [ ] Review Mistake 1: Invented "Berkeley" product
- [ ] Review Mistake 2: Didn't test with curl
- [ ] Review Mistake 3: Protocols without enforcement
- [ ] Review Mistake 4: Tunnel vision on UI, forgot plan
- [ ] Acknowledge: I WILL make similar mistakes unless I follow protocols

---

## ☐ STEP 2: Review Enforcement Mechanisms

- [ ] Read `.claude/instructions.md` lines 43-113 (MANDATORY ENFORCEMENT CHECKLISTS)
- [ ] Understand: Before suggesting examples, must show curl evidence
- [ ] Understand: TodoWrite must include testing steps
- [ ] Understand: Cannot skip steps even when rushing
- [ ] Commit: I will follow checklists, not skip steps

---

## ☐ STEP 3: Review Current State

- [ ] Read `.claude/context.md` - full file
- [ ] Understand: Phase 1A complete (Frontend UI)
- [ ] Understand: Phase 1.5 complete (Backend connection)
- [ ] Understand: Now starting Phase 1C (Grok LLM + 3 tools)
- [ ] Understand: What comes after (Phase 1B: Session memory)
- [ ] Can state: "I'm working on Piece X.Y, which is part of Phase Z"

---

## ☐ STEP 4: Verify Current Baseline Works

- [ ] Run: `curl -X POST https://.../getPrice -d '{"query": "alwinton snuggler pacific"}'`
- [ ] Verify: Returns `{"price": "£1,958", ...}`
- [ ] Document: Baseline test output saved
- [ ] Understand: This MUST keep working after Phase 1C

---

## ☐ STEP 5: Review Phase 1C Scope

**Tools to build:**
- [ ] Tool 1: get_price (exact pricing)
- [ ] Tool 2: search_by_budget (products under max price with fabric tiers)
- [ ] Tool 3: search_fabrics_by_color (all fabrics matching color)

**NOT building:**
- [ ] NOT: Separate compare_products tool (Grok handles via parallel calls)
- [ ] NOT: Add-ons pricing (data doesn't exist yet - Phase 1D)
- [ ] NOT: Session storage backend (Phase 1B)

**Can state:**
- [ ] "Phase 1C builds 3 tools: get_price, search_by_budget, search_fabrics_by_color"
- [ ] "Phase 1C adds session_id parameter but doesn't store it yet"
- [ ] "Phase 1C uses feature flag to preserve demo-ready state"

---

## ☐ STEP 6: Review Demo-Ready Protection Strategy

- [ ] Tag current state: `demo-ready-before-phase-1c`
- [ ] Create feature branch: `feature/grok-llm`
- [ ] Deploy backend FIRST, test with curl BEFORE touching frontend
- [ ] Add USE_LLM feature flag to frontend
- [ ] Test with USE_LLM=false (fallback to /getPrice)
- [ ] Only merge to main when BOTH backend and frontend tested live
- [ ] Understand: If something breaks, can rollback without affecting v1

---

## ☐ STEP 7: Review Testing Requirements

**For EACH piece:**
- [ ] Test locally with curl/browser
- [ ] Show command output as evidence
- [ ] Verify success (200 status, expected data)
- [ ] Commit only after testing
- [ ] Mark todo complete only after evidence shown

**Before deployment:**
- [ ] Test all pieces together locally
- [ ] Deploy backend to GCF
- [ ] Test backend with curl (all tools)
- [ ] Deploy frontend to GitHub Pages
- [ ] Test full flow on live site
- [ ] Verify /getPrice still works (no breakage)

**Before marking Phase 1C complete:**
- [ ] All 6 use case scenarios tested live
- [ ] All documentation updated (context, README, CHANGELOG, TECHNICAL_GUIDE)
- [ ] Tag created: `demo-ready-phase-1c-complete`

---

## ☐ STEP 8: Review Data Verification Requirements

**Before using any product/fabric name:**
- [ ] Check data file with grep/jq
- [ ] Example: `jq 'keys | .[] | select(. == "alwinton")' products.json`
- [ ] Verify it exists
- [ ] NEVER invent names

**Before suggesting any example:**
- [ ] Test with curl
- [ ] Show output
- [ ] Verify success
- [ ] ONLY THEN suggest

**Key rule:**
- [ ] Checking JSON file ≠ testing
- [ ] Testing = running curl and seeing successful response

---

## ☐ STEP 9: Review No-Assumption Rules

**Assumptions I will NOT make:**
- [ ] NOT: "This should work" → Test it
- [ ] NOT: "I checked the file" → Run curl
- [ ] NOT: "The protocol will prevent mistakes" → Use checklist format
- [ ] NOT: "We don't have this data" → Check data files first
- [ ] NOT: "This is too simple to test" → Test everything

**Only acceptable:**
- [ ] "I tested with curl and got this output: [paste]"
- [ ] "I verified in data file with this command: [paste]"
- [ ] "I deployed and tested live at this URL: [paste]"

---

## ☐ STEP 10: Commit to Process

I commit to:
- [ ] Follow EVERY step in TodoWrite (85 items)
- [ ] Show evidence for EVERY test (curl output)
- [ ] NOT skip steps even when rushing
- [ ] NOT assume anything works without testing
- [ ] NOT lose sight of big picture (Phase 1C → Phase 1B → Phase 1D)
- [ ] Update documentation BEFORE marking phase complete
- [ ] Ask user if uncertain rather than guess

---

## ✅ READY TO START

When ALL checkboxes above are checked, I am ready to write code.

**Signature:** I have reviewed all past mistakes and commit to following all protocols.

**Date:** 2025-11-02

---

## 📊 PROGRESS TRACKING

As I complete pieces, I will update this section:

**Pre-implementation:** ☐ Not started
**Piece 3.1 (OpenRouter setup):** ☐ Not started
**Piece 3.2 (Basic /chat):** ☐ Not started
**Piece 3.3 (get_price tool):** ☐ Not started
**Piece 3.4 (budget search):** ☐ Not started
**Piece 3.5 (fabric search):** ☐ Not started
**Piece 3.6 (system prompt):** ☐ Not started
**Piece 3.7 (logging/errors):** ☐ Not started
**Piece 3.8 (backend deploy):** ☐ Not started
**Piece 3.9 (frontend integration):** ☐ Not started
**Piece 3.10 (frontend deploy):** ☐ Not started
**Piece 3.11 (testing/docs):** ☐ Not started

**Current status:** Waiting for user approval to start
