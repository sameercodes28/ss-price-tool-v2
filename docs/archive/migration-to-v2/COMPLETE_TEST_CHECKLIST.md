# ✅ COMPLETE Testing Checklist - Frontend Migration

## 🔴 PRE-MIGRATION: Capture Current Behavior

### Save These Exact Outputs for Comparison

```bash
# Create test directory
mkdir migration-tests
cd migration-tests

# Test 1: Basic Price Query
curl -s -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}' \
  | tee test1-price.json | jq .

# EXPECTED: { "price": "£1,958", "productName": "Alwinton Snuggler", ... }

# Test 2: LLM Greeting
curl -s -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}], "session_id": "test-001"}' \
  | tee test2-greeting.json | jq .response | head -20

# EXPECTED: Natural language greeting

# Test 3: Budget Search
curl -s -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "show me sofas under 2000"}], "session_id": "test-002"}' \
  | tee test3-budget.json | jq .response | head -30

# EXPECTED: Lists Midhurst £1,937, Petworth £1,941, etc.

# Test 4: Fabric Search
curl -s -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "show me blue fabrics"}], "session_id": "test-003"}' \
  | tee test4-fabrics.json | jq .response | head -30

# EXPECTED: ~24 blue fabrics across tiers

# Test 5: Conversation Context
curl -s -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [
    {"role": "user", "content": "tell me about alwinton"},
    {"role": "assistant", "content": "[previous response about alwinton]"},
    {"role": "user", "content": "what about 2 seater?"}
  ], "session_id": "test-004"}' \
  | tee test5-context.json | jq .response | head -20

# EXPECTED: Response mentions Alwinton 2 seater (remembers context)
```

---

## 🟡 DURING MIGRATION: Test After Every Step

### After Adding CSS (Phase 1)

```javascript
// Browser Console Tests
console.log('=== CSS VERIFICATION ===');

// Test 1: CSS variables exist
const rootStyles = getComputedStyle(document.documentElement);
console.log('Fabric terracotta:', rootStyles.getPropertyValue('--fabric-terracotta'));
// EXPECTED: #C67E5F

// Test 2: No CSS conflicts
const messageInput = document.getElementById('message-input');
console.log('Input border before focus:', getComputedStyle(messageInput).borderColor);
messageInput.focus();
console.log('Input border on focus:', getComputedStyle(messageInput).borderColor);
// EXPECTED: Changes to accent color

// Test 3: Animations defined
const styleSheets = Array.from(document.styleSheets);
const hasOrbAnimation = styleSheets.some(sheet => {
    try {
        return Array.from(sheet.cssRules).some(rule =>
            rule.name === 'ultraWeave' || rule.name === 'fiberFlow'
        );
    } catch(e) { return false; }
});
console.log('Orb animations exist:', hasOrbAnimation);
// EXPECTED: true
```

### After Preserving Functions (Phase 2)

```javascript
// Browser Console Tests
console.log('=== FUNCTION VERIFICATION ===');

// Test 1: All critical functions exist
const criticalFunctions = [
    'formatLLMResponse',
    'handleSuggestionClick',
    'escapeHtml',
    'generateSessionId',
    'resetConversation',
    'sendMessage'
];

criticalFunctions.forEach(fn => {
    console.log(`${fn} exists:`, typeof window[fn] === 'function');
});
// EXPECTED: All true

// Test 2: formatLLMResponse handles all formats
const parserTests = [
    {
        input: "### 💰 Price\n£1,958",
        shouldContain: 'price-section'
    },
    {
        input: "### 🎯 Opportunities\n> Add cushions for £200",
        shouldContain: 'opportunities-section'
    },
    {
        input: "**TOTAL: £3,000**\n- Item 1: £2,000\n- Item 2: £1,000",
        shouldContain: 'total-price'
    },
    {
        input: "### 💬 What next?\n- Compare prices\n- View fabrics",
        shouldContain: 'suggestion-chip'
    },
    {
        input: "Was ~~£2,000~~ now **£1,500**",
        shouldContain: 'old-price'
    }
];

parserTests.forEach(test => {
    const result = formatLLMResponse(test.input);
    const passed = result.includes(test.shouldContain);
    console.log(`Parser test "${test.shouldContain}":`, passed ? '✅' : '❌');
    if (!passed) console.log('Result:', result);
});
// EXPECTED: All ✅

// Test 3: Session management
console.log('Session ID format:', sessionId);
console.log('Valid UUID:', /session_\d+_[a-z0-9]+/.test(sessionId));
console.log('Conversation history:', conversationHistory.length);
// EXPECTED: Valid session ID, empty history
```

### After Adding Visual Elements (Phase 3)

```javascript
// Browser Console Tests
console.log('=== VISUAL VERIFICATION ===');

// Test 1: Orb HTML exists
const orbElements = document.querySelectorAll('.ultra-fabric-orb');
console.log('Orb elements found:', orbElements.length);
// EXPECTED: At least 1

// Test 2: Orb animates
const orbSphere = document.querySelector('.ultra-fabric-sphere');
if (orbSphere) {
    const animation = getComputedStyle(orbSphere).animation;
    console.log('Orb animation:', animation);
    console.log('Is animating:', animation.includes('depthPulse') || animation.includes('holographicShift'));
}
// EXPECTED: true

// Test 3: Landing page exists
const landingContainer = document.getElementById('landingContainer');
console.log('Landing container exists:', !!landingContainer);
console.log('Landing visible:', !landingContainer.classList.contains('hidden'));
// EXPECTED: true, true (initially)

// Test 4: Chat container exists
const chatContainer = document.getElementById('chatContainer');
console.log('Chat container exists:', !!chatContainer);
console.log('Chat hidden initially:', !chatContainer.classList.contains('active'));
// EXPECTED: true, true
```

### After Connecting Backend (Phase 4)

```javascript
// Browser Console Tests
console.log('=== BACKEND VERIFICATION ===');

// Test 1: Backend URL correct
console.log('Backend URL:', BACKEND_API_URL);
console.log('Correct URL:', BACKEND_API_URL === 'https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2');
// EXPECTED: true

// Test 2: LLM flag enabled
console.log('USE_LLM:', USE_LLM);
// EXPECTED: true

// Test 3: Send real message (manual)
// Type: "hello"
// Open Network tab
// Look for: POST request to /chat
// Response time: Should be 7-10 seconds
// Response: Should have natural language

// Test 4: Conversation tracking
console.log('History before:', conversationHistory.length);
// Send a message
// ...wait for response...
console.log('History after:', conversationHistory.length);
// EXPECTED: Increases by 2 (user + assistant)

// Test 5: Error handling
// Disconnect WiFi
// Try sending message
// EXPECTED: Friendly error message, no crash
```

### After Removing Fake Functions (Phase 5)

```javascript
// Browser Console Tests
console.log('=== FAKE FUNCTION REMOVAL ===');

// Test 1: Fake functions don't exist
const fakeFunctions = [
    'generateAlwintonResponse',
    'generateVelvetResponse',
    'generateChesterResponse',
    'generateBudgetResponse',
    'generateGenericResponse'
];

fakeFunctions.forEach(fn => {
    console.log(`${fn} removed:`, typeof window[fn] === 'undefined');
});
// EXPECTED: All true

// Test 2: Pattern matching removed
const generateResponse = window.generateResponse.toString();
console.log('Contains "if (query.includes":', generateResponse.includes('if (query.toLowerCase().includes'));
// EXPECTED: false

// Test 3: Real API call exists
console.log('Contains "fetch(":', generateResponse.includes('fetch('));
console.log('Contains "/chat":', generateResponse.includes('/chat'));
// EXPECTED: true, true
```

---

## 🟢 POST-MIGRATION: Complete Verification

### Browser Test Sequence

```javascript
// Run this complete test sequence in browser console

console.log('=== COMPLETE VERIFICATION SUITE ===\n');

// Test Suite 1: Price Accuracy
console.log('1. PRICE ACCURACY TEST');
// Type: "alwinton snuggler pacific"
// VERIFY: Response shows £1,958 (NOT £2,449)
// VERIFY: Response time 7-10 seconds

// Test Suite 2: Follow-up Suggestions
console.log('2. FOLLOW-UP SUGGESTIONS TEST');
// After previous response
// VERIFY: 3-4 blue suggestion chips appear
// Click one
// VERIFY: Sends that query automatically

// Test Suite 3: Budget Search
console.log('3. BUDGET SEARCH TEST');
// Type: "show me sofas under 2000"
// VERIFY: Lists Midhurst, Petworth, etc.
// VERIFY: Prices are all under £2,000

// Test Suite 4: Fabric Search
console.log('4. FABRIC SEARCH TEST');
// Type: "show me blue fabrics"
// VERIFY: Returns ~24 fabrics
// VERIFY: Grouped by tier

// Test Suite 5: Context Memory
console.log('5. CONTEXT MEMORY TEST');
// Type: "tell me about alwinton"
// Wait for response
// Type: "what about 2 seater?"
// VERIFY: Mentions Alwinton 2 seater

// Test Suite 6: Visual Elements
console.log('6. VISUAL ELEMENTS TEST');
const visualChecks = {
    'Orb visible': !!document.querySelector('.ultra-fabric-orb'),
    'Orb animates': !!document.querySelector('.ultra-fabric-sphere'),
    'User bubble dark': getComputedStyle(document.querySelector('.message.user')).background.includes('slate'),
    'Typing dots work': !!document.querySelector('.typing-indicator'),
    'Scroll smooth': getComputedStyle(document.getElementById('messages-container')).scrollBehavior === 'smooth'
};
Object.entries(visualChecks).forEach(([test, result]) => {
    console.log(`  ${test}:`, result ? '✅' : '❌');
});

// Test Suite 7: Interaction
console.log('7. INTERACTION TEST');
// Press Enter → Sends message
// Press Shift+Enter → New line
// Click New Conversation → Clears chat
// Type in textarea → Auto-resizes

// Test Suite 8: Error Handling
console.log('8. ERROR HANDLING TEST');
// Disconnect WiFi
// Try sending message
// VERIFY: Shows error message
// VERIFY: Doesn't crash
// Reconnect WiFi
// VERIFY: Works again

// Test Suite 9: Performance
console.log('9. PERFORMANCE TEST');
console.time('Response Time');
// Send: "alwinton pricing"
// When response appears:
console.timeEnd('Response Time');
// EXPECTED: 7-10 seconds

// Test Suite 10: Console Health
console.log('10. CONSOLE HEALTH CHECK');
// Check browser console
// VERIFY: No red errors
// VERIFY: No 404s in Network tab
// VERIFY: No infinite loops
```

### Mobile Testing

```bash
# Use ngrok to test on real devices
ngrok http 8000  # If running local server

# OR test deployed version
# https://sameercodes28.github.io/ss-price-tool-v2/

# iPhone Safari Tests:
# 1. Orb displays and animates
# 2. Can type and send messages
# 3. Follow-up chips tappable
# 4. Scroll works smoothly
# 5. No viewport issues

# Android Chrome Tests:
# 1. Same as iPhone
# 2. Back button behavior correct
# 3. Keyboard doesn't cover input
```

---

## 🔴 FAILURE CONDITIONS

### If ANY of these occur, STOP IMMEDIATELY:

```javascript
// CRITICAL FAILURES - REVERT IF THESE HAPPEN

// Failure 1: Parser broken
formatLLMResponse("### 💰 Price\n£1,958");
// If this returns plain text instead of HTML → REVERT

// Failure 2: Wrong price
// If Alwinton shows £2,449 → STOP AND FIX

// Failure 3: No backend connection
// Network tab shows no /chat requests → FIX CONNECTION

// Failure 4: Session not tracked
conversationHistory.length === 0 // after sending message
// → Session management broken

// Failure 5: Console errors
// Any red errors in console → INVESTIGATE

// Failure 6: Response timeout
// Takes >20 seconds → Check backend

// Failure 7: Follow-ups missing
// No blue chips after response → Parser issue

// Failure 8: Theme conflict
// Colors flashing/changing → Theme systems fighting
```

---

## ✅ FINAL SIGN-OFF CHECKLIST

Before deploying to production, ALL must be checked:

```markdown
## Production Readiness Checklist

### Functionality
- [ ] Alwinton snuggler pacific = £1,958 ✓
- [ ] Follow-up suggestions appear ✓
- [ ] Clicking suggestions works ✓
- [ ] Budget search returns correct products ✓
- [ ] Fabric search returns ~24 results ✓
- [ ] Conversation maintains context ✓
- [ ] Error handling works offline ✓
- [ ] New conversation clears history ✓

### Visual
- [ ] Ultra Fabric Orb displays ✓
- [ ] Orb animates smoothly ✓
- [ ] Landing → Chat transition works ✓
- [ ] User bubbles are dark gray ✓
- [ ] Assistant has orb avatar ✓
- [ ] Typing indicator shows ✓
- [ ] Scroll is smooth ✓
- [ ] Mobile responsive ✓

### Performance
- [ ] Response time 7-10 seconds ✓
- [ ] No console errors ✓
- [ ] No memory leaks ✓
- [ ] Network requests succeed ✓

### Code Quality
- [ ] No hardcoded prices (grep "£[0-9]") ✓
- [ ] No fake functions remain ✓
- [ ] formatLLMResponse unchanged ✓
- [ ] All tests documented ✓

### External Validation
- [ ] Tested on iPhone ✓
- [ ] Tested on Android ✓
- [ ] Someone else tested ✓
- [ ] 24 hours stable ✓

SIGNED OFF BY: ________________
DATE: ________________
```

---

## 📊 Test Results Archive

Keep a record of all test results:

```markdown
# Test Results Log

## Migration Date: [DATE]

### Baseline Tests (Pre-Migration)
- Test 1 Price: ✅ £1,958
- Test 2 Greeting: ✅ Natural response
- Test 3 Budget: ✅ Found 2 products
- Test 4 Fabrics: ✅ Found 24 fabrics
- Test 5 Context: ✅ Remembered Alwinton

### Phase 1 (CSS)
- Time: [TIME]
- Issues: [None/List]
- Resolution: [N/A/Description]

### Phase 2 (Functions)
- Time: [TIME]
- Issues: [None/List]
- Resolution: [N/A/Description]

### Phase 3 (Visual)
- Time: [TIME]
- Issues: [None/List]
- Resolution: [N/A/Description]

### Phase 4 (Backend)
- Time: [TIME]
- Issues: [None/List]
- Resolution: [N/A/Description]

### Phase 5 (Cleanup)
- Time: [TIME]
- Issues: [None/List]
- Resolution: [N/A/Description]

### Final Verification
- All tests passed: [YES/NO]
- Total migration time: [HOURS]
- Production deployed: [TIME]
- First user test: [TIME]
- 24-hour check: [PASS/FAIL]
```

---

*This checklist represents 100% of tests needed for successful migration. Run every test, document every result.*