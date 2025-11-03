# Lessons Learned - v2 Development

**Last Updated:** 2025-11-02
**Purpose:** Track all mistakes, assumptions, and lessons to prevent repeating them

---

## 🚨 CRITICAL MISTAKES MADE

### **Mistake 1: Invented Data Without Verification (Phase 1.5)**

**Date:** 2025-11-02
**Phase:** Phase 1.5 (Backend Connection)

**What Happened:**
- Suggested example "berkeley 3 seater sussex plain" for greeting message
- "Berkeley" product does NOT exist in products.json
- Mentioned "House Wool" fabric - does NOT exist in fabrics.json
- Invented price "£2,450" without testing

**User Impact:**
- User tested examples - ALL FAILED
- Lost user trust
- Required emergency fix

**Root Cause:**
- Made up examples without checking actual data files
- Assumed product names without verification
- No testing before suggesting

**Fix Applied:**
- Removed all fake references
- Added Data Verification Protocol to .claude/instructions.md
- Established rule: NEVER invent data

**Prevention:**
- ✅ ALWAYS check data files before mentioning specifics
- ✅ ALWAYS grep/jq to verify product/fabric names exist
- ✅ NEVER suggest examples without verification

**Reference:** .claude/instructions.md lines 357-404 (Data Verification Protocol)

---

### **Mistake 2: Violated Own Protocol - Didn't Actually Test (Phase 1.5)**

**Date:** 2025-11-02
**Phase:** Phase 1.5 (Backend Connection)

**What Happened:**
- After Mistake 1, I wrote "Data Verification Protocol"
- Claimed to "fix" examples with "aldingbourne 3 seater waves" and "saltdean 3 seater covertex"
- Said I checked products.json
- **DID NOT TEST WITH CURL**
- Both examples FAILED when user tested:
  - "aldingbourne 3 seater waves" → No "3 seater" variant exists (only snuggler, chair)
  - "saltdean 3 seater covertex" → Backend error (needs specific color)

**User Impact:**
- User caught me violating my own protocol
- Examples failed AGAIN
- Further loss of trust
- User demanded: "Why didn't the protocol work?"

**Root Cause:**
- Wrote protocol but didn't FOLLOW it
- Only checked if product NAME existed, not if FULL QUERY worked
- Skipped curl testing step
- Assumed checking JSON file was enough

**Fix Applied:**
- Actually tested with curl:
  ```bash
  curl -X POST .../getPrice -d '{"query": "aldingbourne snuggler waves"}'
  → {"price":"£1,958"} ✅ WORKS

  curl -X POST .../getPrice -d '{"query": "rye snuggler pacific"}'
  → {"price":"£1,482"} ✅ WORKS
  ```
- Updated examples with CURL-VERIFIED queries
- Added MANDATORY ENFORCEMENT CHECKLISTS to .claude/instructions.md

**Prevention:**
- ✅ Protocols need ENFORCEMENT, not just documentation
- ✅ Must show curl output as EVIDENCE before suggesting
- ✅ TodoWrite must include separate "Test with curl" step
- ✅ Cannot skip testing even if in a hurry

**Reference:** .claude/instructions.md lines 43-113 (MANDATORY ENFORCEMENT CHECKLISTS)

---

### **Mistake 3: Protocols Without Enforcement Mechanisms (Phase 1.5)**

**Date:** 2025-11-02
**Phase:** Phase 1.5 (Backend Connection)

**What Happened:**
- Wrote "Data Verification Protocol" after Mistake 1
- Immediately violated it in Mistake 2
- User asked: "Why didn't your protocol work?"

**User Impact:**
- Demonstrated protocols were ineffective
- User lost confidence in my ability to prevent mistakes

**Root Cause:**
- Protocols were just words in middle of file
- Easy to ignore/skip when rushing
- No checklist format to force verification
- No accountability mechanism

**Fix Applied:**
- Created MANDATORY ENFORCEMENT CHECKLISTS at TOP of instructions.md
- Checklist format with explicit steps:
  1. ☐ Check data file exists
  2. ☐ Test with curl - show output
  3. ☐ Verify successful response
  4. ☐ Copy/paste curl output as evidence
  5. ☐ ONLY THEN suggest to user
- Added to TodoWrite requirements: Must include testing steps
- Moved to top of file so I see it first

**Prevention:**
- ✅ Checklists > prose descriptions
- ✅ Enforcement > documentation
- ✅ Evidence required (curl output) not just claims
- ✅ TodoWrite must break down testing into separate todos

**Reference:** .claude/instructions.md lines 43-113

---

### **Mistake 4: Tunnel Vision - Lost Track of Comprehensive Plan (Phase 1A)**

**Date:** 2025-11-02
**Phase:** Phase 1A (Frontend Chat UI)

**What Happened:**
- Started Phase 1A: Build chat interface
- Got focused on UI polish: fonts, colors, alignment
- **Completely forgot about comprehensive 35-piece plan** for LLM integration
- User asked: "Where are we in the plan?"
- I gave generic status update without referencing the plan

**User Impact:**
- User had to provide the full plan again
- Demonstrated I wasn't tracking the big picture
- User worried I'd forget critical pieces

**Root Cause:**
- Focused only on current task (UI)
- Didn't maintain TodoWrite with ALL phases
- Lost sight of overall goal (LLM chat agent)

**Fix Applied:**
- Added Plan Tracking Protocol to .claude/instructions.md
- Rule: TodoWrite must include ALL phases, not just current task
- Must review .claude/context.md at start of every session
- Must state "Next phase after this piece" when completing tasks

**Prevention:**
- ✅ TodoWrite must show full plan context
- ✅ Review context.md at session start
- ✅ State next phase when marking todos complete
- ✅ Prevent tunnel vision on sub-tasks

**Reference:** .claude/instructions.md lines 407-452 (Plan Tracking Protocol)

---

## 🎓 KEY LESSONS LEARNED

### **Lesson 1: Verification Requires Evidence**

**Don't say:** "I checked products.json and it exists"
**Do say:** "I verified with grep: `grep -i 'alwinton' products.json` → Found ✅"

**Don't say:** "This should work"
**Do say:** "I tested with curl and got this response: [paste output]"

---

### **Lesson 2: Testing = Actually Running the Command**

**Not testing:** Looking at code and assuming it works
**Not testing:** Checking JSON file exists
**Not testing:** Reading function and thinking "this looks right"

**Actually testing:** Running curl command and seeing successful response
**Actually testing:** Deploying to GCF and hitting live endpoint
**Actually testing:** User testing and confirming it works

---

### **Lesson 3: Protocols Need Enforcement**

**Ineffective protocol:** "Always test before suggesting examples"
**Effective protocol:**
```
☐ Step 1: Check data file
☐ Step 2: Test with curl
☐ Step 3: Show output
☐ Step 4: ONLY THEN suggest
```

Checklists force verification. Prose gets ignored.

---

### **Lesson 4: User Trust = Demonstrable Actions**

**Loses trust:** "I tested it" (without evidence)
**Builds trust:** "I tested it - here's the curl output: [paste]"

**Loses trust:** "I'll add a protocol to prevent this"
**Builds trust:** "I added a mandatory checklist at line 43 that I must follow"

---

### **Lesson 5: Keep Context of Big Picture**

**Tunnel vision:** "I'm working on making the button purple"
**Big picture:** "I'm making the button purple (part of UI theme system, which is Piece 1.4 of Phase 1A, which enables chat interface for LLM integration)"

Always know: What piece? What phase? What's next?

---

## 🔄 ASSUMPTIONS THAT WERE WRONG

### **Assumption 1: "We don't have budget search data"**
❌ **WRONG** - products.json has all prices, we can filter by budget

### **Assumption 2: "We don't have fabric color search data"**
❌ **WRONG** - fabrics.json has all color names, we can search by color

### **Assumption 3: "Product comparison needs Phase 1D"**
❌ **WRONG** - Grok-4 supports parallel function calling, can call get_price twice

### **Assumption 4: "Checking JSON file = testing"**
❌ **WRONG** - Testing = running curl and seeing successful response

### **Assumption 5: "Writing a protocol = it will be followed"**
❌ **WRONG** - Protocols need checklists and enforcement to be followed

---

## ✅ GOING FORWARD

**Before suggesting ANY example:**
1. Check data file with grep/jq
2. Test with curl
3. Show output
4. Verify success
5. ONLY THEN suggest

**Before marking ANY todo complete:**
1. Run actual tests
2. Show evidence
3. Verify success
4. Document what was tested

**Before starting ANY phase:**
1. Read .claude/context.md
2. Review full plan
3. Create TodoWrite with ALL phases
4. State what piece/phase I'm working on

**Before ANY deployment:**
1. Test locally
2. Test on GCF
3. Test live URL
4. Verify existing functionality still works

---

**This document will be updated as new lessons are learned.**
