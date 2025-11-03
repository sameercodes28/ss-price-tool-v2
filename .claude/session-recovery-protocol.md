# Session Recovery Protocol

**Purpose:** If context window compacts mid-Phase 1C, this protocol ensures I don't lose track

---

## 🔄 RECOVERY STEPS (Run after context compacting)

### **Step 1: Check TodoWrite**
```
Look at TodoWrite current state:
- How many items marked "completed"?
- Which item is "in_progress"?
- Which items are still "pending"?

Example: "Piece 3.4 is in_progress, need to finish budget search tool"
```

### **Step 2: Read Context File**
```
Read .claude/context.md:
- What was the last session entry?
- What was the last piece completed?
- What was tested?
- What's the current state?

Example: "Last entry shows Piece 3.3 completed, get_price tool working"
```

### **Step 3: Check Git Log**
```
Run: git log --oneline -10

Shows recent commits:
- "Phase 1C Piece 3.3: get_price tool" ← Last completed
- "Phase 1C Piece 3.2: Basic /chat endpoint"
- "Phase 1C Piece 3.1: OpenRouter setup"

Example: "3 pieces committed, working on Piece 3.4 next"
```

### **Step 4: Check Pre-Implementation Checklist**
```
Read .claude/pre-implementation-checklist.md:
- Which pieces are marked complete in PROGRESS TRACKING?
- What's the current piece status?

Example: "Piece 3.3: ✅ Complete, Piece 3.4: ⏳ In Progress"
```

### **Step 5: Test Current State**
```
Run curl tests to verify what's working:

# Test existing functionality
curl -X POST https://.../getPrice -d '{"query": "alwinton snuggler pacific"}'
→ Should work ✅

# Test new /chat endpoint (if deployed)
curl -X POST https://.../chat -d '{"messages": [{"role": "user", "content": "Hello"}]}'
→ Check if working

Example: "Backend deployed with 2 tools working, need to add tool 3"
```

### **Step 6: Review Lessons Learned**
```
Read .claude/lessons-learned.md:
- What mistakes did I make before?
- What protocols must I follow?
- What's the enforcement checklist?

Example: "Must test with curl before suggesting, must show evidence"
```

### **Step 7: State Current Context**
```
Summarize to user:

"After context recovery, here's where we are:
- Phase 1C in progress
- Completed: Pieces 3.1, 3.2, 3.3 (OpenRouter setup, basic /chat, get_price tool)
- In progress: Piece 3.4 (search_by_budget tool)
- Remaining: Pieces 3.5-3.11
- Current status: Backend has 1 tool working, need to add 2 more tools
- Testing: All tests passing for completed pieces
- Next step: Complete Piece 3.4, then test with curl"
```

---

## 📋 RECOVERY CHECKLIST

When context compacts, run through this checklist:

- [ ] Check TodoWrite (which item is in_progress?)
- [ ] Read .claude/context.md (what was last completed?)
- [ ] Run git log (what's been committed?)
- [ ] Read .claude/pre-implementation-checklist.md (progress tracking)
- [ ] Test with curl (what's currently working?)
- [ ] Review .claude/lessons-learned.md (what must I avoid?)
- [ ] State current context to user (where are we?)
- [ ] Confirm next step before proceeding

---

## ✅ CONFIDENCE CHECK

After recovery, I should be able to answer:

1. **What phase are we in?** → Phase 1C (Grok LLM integration)
2. **What piece am I working on?** → Check TodoWrite for in_progress item
3. **What's been completed?** → Check git log and TodoWrite completed items
4. **What's currently working?** → Test with curl
5. **What's next?** → Check TodoWrite pending items
6. **What must I avoid?** → Review lessons-learned.md

If I can answer all 6 questions, I have full context and can continue safely.

---

## 🚨 IF STILL CONFUSED

If after recovery I'm uncertain about anything:

1. **STOP** - Don't proceed with coding
2. **ASK USER** - "After context recovery, I see X in files. Is that correct?"
3. **VERIFY** - Show what I found in files and ask for confirmation
4. **WAIT** - Get user approval before writing any code

Better to ask than to make assumptions and break things.
