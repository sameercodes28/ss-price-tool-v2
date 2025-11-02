# Frontend Migration Quick Checklist

## ⚠️ CRITICAL WARNINGS

### Your New Design Has WRONG Data!
- **Alwinton 3 Seater Pacific shows £2,449** → Reality: **£1,958**
- **All responses are FAKE** → No backend connection
- **Follow-ups are hardcoded** → Should come from Grok

### What Will Break If Done Wrong
1. **LLM integration** - Must preserve `/chat` endpoint calls
2. **Real pricing** - Must remove ALL hardcoded prices
3. **Follow-up suggestions** - Must let Grok generate them
4. **Session management** - Must keep conversation history

---

## 📋 MIGRATION CHECKLIST

### ✅ PHASE A: Safety First (15 min)
```bash
cd /Users/sameerm4/Desktop/SS-2
```

- [ ] Create branch: `git checkout -b feature/ultra-fabric-ui`
- [ ] Backup current: `cp index.html index-v2-backup.html`
- [ ] Copy reference: `cp /Users/sameerm4/Desktop/index-improved-v3.html ./index-improved-reference.html`
- [ ] Commit backups: `git add . && git commit -m "Backup before UI migration"`
- [ ] Test backend:
```bash
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'
# Must return: {"price": "£1,958", ...}
```

---

### 🎨 PHASE B: Visual Only (1 hour)

- [ ] **Copy CSS (lines 36-1089 from new design)**
  - Keep: `.suggestions-section`, `.price-section`, `.opportunity-section`
  - Add: All Ultra Fabric Orb styles

- [ ] **Add Orb HTML**
```html
<div class="ultra-fabric-orb ultra-fabric-orb-small">
    <div class="ultra-fabric-sphere">
        <div class="fabric-depth-layer"></div>
        <div class="fabric-particles">
            <div class="fabric-particle"></div>
            <div class="fabric-particle"></div>
            <div class="fabric-particle"></div>
        </div>
    </div>
</div>
```

- [ ] **Test Visual**: Open index.html → Orb animates? Fonts load? Mobile works?

---

### 🔌 PHASE C: Backend Connection (2 hours)

- [ ] **MUST KEEP from v2:**
```javascript
const USE_LLM = true;
const BACKEND_API_URL = 'https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2';
let conversationHistory = [];
let currentSessionId = generateSessionId();

// ENTIRE formatLLMResponse function (lines 790-980)
// ENTIRE handleSuggestionClick function
```

- [ ] **Replace fake generateResponse with:**
```javascript
async function generateResponse(query) {
    try {
        conversationHistory.push({ role: "user", content: query });

        const response = await fetch(`${BACKEND_API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: conversationHistory,
                session_id: currentSessionId
            })
        });

        const data = await response.json();
        conversationHistory.push({ role: "assistant", content: data.response });

        // Use formatLLMResponse to parse Grok's response!
        const formatted = formatLLMResponse(data.response);
        // Add orb + formatted content
    } catch (error) {
        // Error handling
    }
}
```

- [ ] **DELETE these fake functions:**
  - `generateAlwintonResponse()`
  - `generateVelvetResponse()`
  - `generateChesterResponse()`
  - `generateBudgetResponse()`
  - `generateGenericResponse()`

---

### 🧹 PHASE D: Remove Hardcoded Data (1 hour)

- [ ] **Search and destroy ALL occurrences of:**
  - "£2,449" → Should not exist
  - "£1,850" → Unless from real API
  - "Grade C, £599" → Fabric prices must be real
  - Hardcoded follow-up arrays

- [ ] **Fix placeholder examples:**
```javascript
const placeholderExamples = [
    "Alwinton snuggler in Pacific",     // TESTED: £1,958
    "Aldingbourne snuggler in Waves",    // TESTED: £1,958
    "Rye snuggler in Pacific",           // TESTED: £1,482
    "Show me blue fabrics",              // TESTED: Works
    "Sofas under £2000"                  // TESTED: Works
];
```

---

### ✅ PHASE E: Testing (1 hour)

**Test Each of These IN ORDER:**

1. [ ] **Basic Load Test**
   - Page loads without errors?
   - Console shows no 404s?
   - Orb animates?

2. [ ] **Real Price Test**
   ```
   Type: "alwinton snuggler pacific"
   Expected: £1,958 (NOT £2,449!)
   ```

3. [ ] **Follow-up Test**
   ```
   After response, see 3-4 blue chips
   Click one → Sends that query
   ```

4. [ ] **Budget Search Test**
   ```
   Type: "sofas under 2000"
   Expected: Lists Midhurst, Petworth, etc.
   ```

5. [ ] **Fabric Search Test**
   ```
   Type: "show me blue fabrics"
   Expected: ~24 fabrics grouped by tier
   ```

6. [ ] **Conversation Memory Test**
   ```
   Query 1: "alwinton pricing"
   Query 2: "what about 2 seater?"
   Expected: Grok remembers context
   ```

7. [ ] **Error Handling Test**
   ```
   Disconnect WiFi → Try query
   Expected: Friendly error message
   ```

---

## 🚨 EMERGENCY ROLLBACK

If anything breaks:

```bash
# Option 1: Git rollback
git checkout main
git branch -D feature/ultra-fabric-ui

# Option 2: File restore
cp index-v2-backup.html index.html

# Option 3: Full reset
git checkout -- index.html
```

---

## ✅ DEFINITION OF DONE

### Must Work:
- [ ] Orb displays and animates
- [ ] Real Grok responses (7-10 seconds)
- [ ] Correct prices from API
- [ ] Follow-up suggestions from Grok
- [ ] All 3 tools work
- [ ] Error handling works
- [ ] Conversation history maintained

### Must NOT Exist:
- [ ] No "£2,449" anywhere
- [ ] No generateAlwintonResponse function
- [ ] No hardcoded follow-ups
- [ ] No pattern matching (if includes 'alwinton'))

---

## 📊 Quick Test Commands

```bash
# Test 1: Backend alive?
curl -I https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice

# Test 2: Correct price?
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}' | grep "1,958"

# Test 3: LLM working?
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}], "session_id": "test"}' \
  | jq .response
```

---

## 🎯 Success = All boxes checked + No hardcoded data remains

**Remember:** The new design is beautiful but currently shows WRONG prices. Your job is to keep the beauty but connect it to REAL data.