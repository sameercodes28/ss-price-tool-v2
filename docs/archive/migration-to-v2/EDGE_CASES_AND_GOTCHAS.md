# 🔥 Edge Cases & Gotchas from v2 Development

## Critical Edge Cases We've Already Handled (MUST PRESERVE)

### 1. The TOTAL Price Format Bug
**What Happened:** Grok outputs `**TOTAL: £amount**` but we expected `TOTAL: **£amount**`
**Hours Wasted:** 4+ hours of blind debugging
**The Fix:** Lines 889-904 in formatLLMResponse now handles BOTH formats
**Test:**
```javascript
formatLLMResponse("**TOTAL: £3,000**\n- Item: £3,000");
// Must show large total display, not regular text
```

### 2. Follow-up Suggestions Extraction
**What Happened:** Grok outputs suggestions after `### 💬` header
**Edge Case:** Sometimes has 3, sometimes 4-5 suggestions
**The Fix:** Lines 880-886 + 1017-1027 dynamically extract any number
**Test:**
```javascript
formatLLMResponse("### 💬 What next?\n- Option 1\n- Option 2\n- Option 3");
// Must create clickable chips, not bullet list
```

### 3. Price with Strikethrough and Bold
**Pattern:** `Was ~~£2,000~~ now **£1,500** (Save £500!)`
**Edge Case:** Multiple price formats in one line
**The Fix:** Lines 942-962 parse old price, new price, and savings separately
**Test:**
```javascript
formatLLMResponse("Was ~~£2,000~~ now **£1,500** (Save £500!)");
// Must show old price with strikethrough, new price large, savings badge
```

### 4. Conversation History Tracking
**Edge Case:** User sends message, API fails, history gets corrupted
**The Fix:** Lines 1127-1133 + 1208-1211 remove failed messages from history
**Test:**
```javascript
// Disconnect WiFi, send message, check:
console.log(conversationHistory.length); // Should not increase if failed
```

### 5. Session ID Format
**Edge Case:** Backend expects specific format
**The Fix:** Line 621 generates `session_[timestamp]_[random]`
**Test:**
```javascript
sessionId.match(/session_\d+_[a-z0-9]+/); // Must match pattern
```

### 6. Theme System Updates
**Edge Case:** Theme must update ALL elements including dynamic ones
**The Fix:** Lines 673-722 update logo, button, input, avatars, typing dots
**Test:**
```javascript
// After theme change, ALL these should update:
// - Logo face color
// - Send button gradient
// - Input focus shadow
// - Agent avatars (including new messages)
// - Typing indicator dots
```

### 7. Enter vs Shift+Enter
**Edge Case:** Enter should send, Shift+Enter should add new line
**The Fix:** Lines 1297-1302 check for shiftKey
**Test:**
```javascript
// Press Enter → Message sends
// Press Shift+Enter → New line in textarea
```

### 8. Auto-resize Textarea
**Edge Case:** Textarea should grow but not exceed max height
**The Fix:** Lines 746-749 with max height of 150px
**Test:**
```javascript
// Type multiple lines
// Should grow until 150px, then scroll internally
```

### 9. Greeting Detection
**Edge Case:** "hello", "hi", "help" should not try price lookup
**The Fix:** Lines 1141-1155 check for greetings first
**Test:**
```javascript
// Type "hello" with USE_LLM=false
// Should get help message, not error
```

### 10. Product Name Parsing
**Edge Case:** "Alwinton 3 Seater in Pacific Velvet"
**The Fix:** Lines 968-975 split on " in " to italicize fabric
**Test:**
```javascript
formatLLMResponse("**Alwinton 3 Seater in Pacific Velvet**");
// Should show: Alwinton 3 Seater *in Pacific Velvet*
```

---

## Gotchas That Broke Production

### 1. The Berkeley Product That Doesn't Exist
**What We Did Wrong:** Suggested "berkeley 3 seater sussex plain"
**Reality:** Product doesn't exist in database
**Lesson:** ALWAYS verify with actual data files
**Prevention:** Test every example with curl

### 2. The Aldingbourne Configuration Error
**What We Did Wrong:** Suggested "aldingbourne 3 seater waves"
**Reality:** Aldingbourne doesn't have 3 seater variant
**Lesson:** Products have specific valid configurations
**Prevention:** Check products.json for valid sizes

### 3. The Grok-4 Timeout Disaster
**What Happened:** Grok-4 took 4+ minutes, caused timeouts
**Failed Fixes:** Reducing prompt size, removing context
**Actual Fix:** Switch to Grok-4-fast model
**Lesson:** Model selection > prompt optimization

### 4. The Duplicate Typing Indicator
**What Happened:** Multiple typing indicators appeared
**Cause:** Not removing previous indicator before adding new
**Fix:** Lines 1543-1547 check and remove existing

### 5. The Scroll Timing Issue
**What Happened:** Messages didn't scroll to bottom
**Cause:** Scroll called before DOM update
**Fix:** Line 1268 scrollToBottom() after appendChild

---

## Hidden Dependencies That Will Break If Changed

### 1. Message Container ID
**Current:** `messages-container` and `messages-list`
**Why Critical:** Multiple functions reference these IDs
**If Changed:** Breaks scrolling, message addition, welcome hide

### 2. Input Field ID
**Current:** `message-input`
**Why Critical:** Auto-resize, focus, value retrieval all use this
**If Changed:** Can't send messages

### 3. Agent Avatar Class
**Current:** `agent-avatar`
**Why Critical:** Theme system updates all elements with this class
**If Changed:** New messages won't get theme colors

### 4. Typing Indicator Structure
**Current:** Three dots with `typing-dot` class
**Why Critical:** CSS animation targets specific structure
**If Changed:** Animation breaks

### 5. Button Onclick Format
**Current:** `onclick="handleSuggestionClick('text')"`
**Why Critical:** Single quotes inside, escaped properly
**If Changed:** XSS vulnerability or syntax errors

---

## Performance Gotchas

### 1. Response Time Expectations
**Reality:** 7-10 seconds with Grok-4-fast
**Not Possible:** <5 seconds (model limitation)
**User Perception:** Typing indicator critical for perceived performance

### 2. Conversation History Growth
**Issue:** History grows with each message
**Impact:** Eventually hits token limits
**Current:** No trimming (future feature needed)

### 3. Mobile Keyboard Behavior
**Issue:** Keyboard covers input on some devices
**Fix:** Viewport height calculations account for keyboard

### 4. Animation Performance
**Issue:** Complex orb animations can lag on old devices
**Mitigation:** CSS-only animations, no JavaScript animation loops

---

## Security Gotchas

### 1. XSS Prevention
**Critical Function:** escapeHtml() on lines 833-841
**Used In:** All user input, suggestion chips, product names
**Test:** Try injecting `<script>alert('XSS')</script>`

### 2. Suggestion Click Injection
**Risk:** Onclick attributes with user data
**Prevention:** Line 1023 escapes quotes properly
**Test:** Suggestion with quote marks and apostrophes

### 3. Markdown Injection
**Risk:** Markdown could contain scripts
**Prevention:** formatLLMResponse escapes before formatting
**Note:** We DON'T use marked.js for LLM responses

---

## Data Integrity Gotchas

### 1. Price Format Variations
**Formats Seen:**
- "£1,958"
- "£1958"
- "**£1,958**"
- "Price: £1,958"

**Must Handle All:** Regex must be flexible

### 2. Product Name Variations
**Formats Seen:**
- "Alwinton Snuggler"
- "Alwinton Snuggler in Pacific"
- "**Alwinton Snuggler** in **Pacific**"

**Must Parse All:** Don't assume fixed format

### 3. Fabric Tier Indicators
**Formats Seen:**
- "Grade A"
- "Tier 1"
- "Standard"
- "(Grade A)"

**Must Recognize All:** Multiple tier formats exist

---

## The "Works on My Machine" Gotchas

### 1. Font Loading
**Issue:** Custom fonts may not load immediately
**Impact:** Layout shift when fonts load
**Mitigation:** Font-display: swap

### 2. localStorage Availability
**Issue:** Private browsing blocks localStorage
**Current:** New design uses it, v2 doesn't
**Decision Needed:** Remove or add fallback

### 3. Network Timeouts
**Issue:** 2-minute default may be too long
**Current:** No custom timeout
**Consider:** 30-second timeout with retry

### 4. CORS in Development
**Issue:** Local testing may hit CORS
**Solution:** Test with deployed version or use proxy

---

## Testing Gotchas

### 1. The "It Worked Before" Trap
**Reality:** Every change can break previous fixes
**Prevention:** Run full test suite after EVERY change

### 2. The Mock Data Trap
**Issue:** Testing with fake data that doesn't match reality
**Example:** Berkeley product, wrong prices
**Prevention:** ONLY test with real API calls

### 3. The Console.log Removal Trap
**Issue:** Removing debug logs can change timing
**Example:** Scroll might work with logs, break without
**Prevention:** Test after removing logs

### 4. The Cache Trap
**Issue:** Browser caches old JavaScript
**Prevention:** Hard refresh (Cmd+Shift+R) every test

---

## Integration Gotchas

### 1. Backend Response Format
**Expected:** `{ response: string, metadata: object }`
**Edge Case:** Sometimes metadata missing
**Handle:** Check if metadata exists before accessing

### 2. Feature Flag Behavior
**Current:** USE_LLM switches between /chat and /getPrice
**Gotcha:** Different response formats
**Must:** Check flag before parsing response

### 3. Session Timeout
**Backend:** 1-hour timeout
**Frontend:** No handling
**TODO:** Add session refresh or warning

---

## The Ultimate Gotcha

### DON'T TRUST ANYTHING WITHOUT TESTING

**Every example in the new design:** WRONG
**Every price shown:** FAKE
**Every response pattern:** HARDCODED
**Every follow-up:** STATIC

**The new design is a beautiful lie. Your job is to keep the beauty but make it tell the truth.**

---

*These gotchas cost us 50+ hours during v2 development. Learn from our pain.*