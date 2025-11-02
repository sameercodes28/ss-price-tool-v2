# Knowledge Base - SS Price Tool v2

**Purpose:** Complete knowledge capture for session continuity
**Last Updated:** 2025-11-02
**Status:** PIECE 3 complete ✅ | PIECE 4 ready to implement ⏳

---

## 🎯 Critical Success Factors

### 1. Debug-First Methodology

**Always add debug logging BEFORE implementing:**
```javascript
console.log('[SECTION] Action:', details);
```

**Why:** In TOTAL price formatting, 20+ minutes of debugging became 5 minutes with logs.

**Apply to:**
- New parsing logic
- Response formatting
- URL generation
- Any LLM output processing

### 2. Test URLs Before Using

**Example from today:**
- imageURLs from API: ❌ HTTP 404 (broken)
- Product URLs with SKU: ✅ HTTP 200 (working)

**Always:**
```bash
curl -I "https://url-to-test" 2>&1 | head -5
```

### 3. Same Patterns = Low Risk

**Pattern identified:** Adding fields to `simplified_response`

**Already doing:**
```python
"imageUrls": image_urls,  # Exists since v1
```

**Safe to add:**
```python
"productUrl": product_url,  # Same pattern!
```

---

## 🧪 Proven Patterns

### Pattern 1: Adding Response Fields

**Location:** main.py `get_price_logic()` function

**Template:**
```python
# Build the data
new_field_value = f"..."

# Add to response
simplified_response = {
    # ... existing fields ...
    "newField": new_field_value,  # Add here
}
```

**Examples:**
- imageUrls (existing)
- productUrl (ready to add)
- fabricDetails (existing)

**Risk:** 🟢 Very Low - Dictionary addition only

### Pattern 2: Frontend Section Detection

**Location:** index.html `formatResponse()` function

**Template:**
```javascript
// Detect section
if (line.startsWith('### 💬')) {
    console.log('[SECTION] Detected');
    if (currentSection === 'previous') html += '</div>';
    currentSection = 'new_section';
    continue;
}

// Process section content
if (currentSection === 'new_section') {
    // Extract and process data
    const data = line.substring(1).trim();
    collection.push(data);
    continue;
}

// Render at end
if (collection.length > 0) {
    html += '<div class="section">';
    collection.forEach(item => {
        html += `<div class="item">${item}</div>`;
    });
    html += '</div>';
}
```

**Examples:**
- Price section (green)
- Features section (checkmarks)
- Opportunities section (purple)
- Suggestions section (blue chips) ← Just implemented!

**Risk:** 🟢 Low - Isolated section handling

### Pattern 3: SYSTEM_PROMPT Instructions

**Location:** main.py `SYSTEM_PROMPT` variable

**Template:**
```python
## NEW FEATURE

[Clear instructions for Grok]

### Format:
[Expected output format with examples]

RULES:
- Rule 1 with specifics
- Rule 2 with examples
- Rule 3 with edge cases

EXAMPLES:
[Show 2-3 concrete examples]
```

**Examples:**
- TOTAL price formatting
- Follow-up suggestions
- Product links (ready to add)

**Risk:** 🟡 Medium - Grok may not always follow, needs testing

---

## 📊 Validated Data Points

### SKU Construction (Working ✅)

**Format:** `product + size + cover + fabric + color`

**Example:**
```
alw + snu + fit + ttp + pac = alwsnufitttpac
```

**Code Location:** main.py:655
```python
query_sku = f"{product_sku}{size_sku}{cover_sku}{fabric_match_data['fabric_sku']}{fabric_match_data['color_sku']}"
```

**Validated:** ✅ Used successfully for S&S API calls

### Product URL Format (Tested ✅)

**Format:** `https://sofasandstuff.com/[slug]?sku=[querySku]`

**Example:**
```
https://sofasandstuff.com/alwinton?sku=alwsnufitttpac
```

**Testing Results:**
- HTTP Status: 200 OK ✅
- Configuration: Auto-loads with exact specs ✅
- Price Match: £1,958 matches tool quote ✅

**Code to Generate:**
```python
product_url = f"https://sofasandstuff.com/{product_name_keyword}?sku={query_sku}"
```

### Image URLs (Broken ❌)

**Format:** Various paths under sofasandstuff.com/images/...

**Testing Results:**
- HTTP Status: 404 Not Found ❌
- Same issue as v1 ❌
- Images show wrong fabrics even in API ❌

**Conclusion:** Do NOT use imageUrls for any feature

---

## 🎨 UI Design Patterns

### Color Schemes (Established)

**Green = Pricing:**
```css
.total-price {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    color: #047857;
}
```

**Purple = Upselling:**
```css
.opportunities-section {
    background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
    border: 2px solid #a855f7;
}
```

**Blue = Interactive:**
```css
.suggestions-section {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #0ea5e9;
}
```

**Pattern:** Each section has distinct color for easy recognition

### Typography Hierarchy

**Product Names:**
```css
.product-name {
    font-size: 1.375rem;  /* 22px */
    font-weight: 700;
}
```

**Total Price (Largest):**
```css
.total-price {
    font-size: 2.5rem;  /* 40px */
    font-weight: 800;
}
```

**Regular Text:**
```css
.response-text {
    font-size: 0.875rem;  /* 14px */
}
```

### Interactive Elements

**Touch-Friendly Minimum:**
```css
min-height: 44px;  /* Apple HIG recommendation */
```

**Hover Effects:**
```css
transition: all 0.2s ease;
transform: translateY(-2px);  /* Lift on hover */
```

**Active States:**
```css
transform: translateY(0);  /* Reset on click */
```

---

## 🔧 Deployment Procedures

### Backend Deployment (GCF v2)

**Command:**
```bash
gcloud functions deploy sofa-price-calculator-v2 \
  --gen2 \
  --runtime=python311 \
  --region=europe-west2 \
  --source=. \
  --entry-point=http_entry_point \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=120s
```

**Time:** 2-3 minutes
**Verification:** curl test to /getPrice endpoint

### Frontend Deployment (GitHub Pages)

**Command:**
```bash
git add index.html
git commit -m "Description"
git push
```

**Time:** 1-2 minutes for GitHub Pages to update
**Verification:** Hard refresh browser (Cmd+Shift+R)

### Testing Order (Important!)

1. **Backend first** - Deploy, test with curl
2. **Verify response** - Check new fields present
3. **Frontend second** - Only after backend confirmed working
4. **Live test** - Check on actual site

**Why:** Avoids debugging frontend when backend is broken

---

## 📈 Performance Benchmarks

### Grok-4-fast Response Times

**Typical:** 5-7 seconds
**With tools:** 6-8 seconds (get_price call adds 1s)
**Timeout:** 120 seconds (GCF limit)

**Why fast:** Switched from Grok-4 (120s) to Grok-4-fast (7s) = 16x improvement

### Frontend Parsing

**Typical:** <100ms
**With debug logs:** ~150ms
**Negligible impact on UX**

### GitHub Pages

**CDN:** Cloudflare
**Cache:** Can take 1-2 minutes to clear
**Hard refresh:** Cmd+Shift+R bypasses cache

---

## 🐛 Common Issues & Solutions

### Issue 1: Regex Not Matching LLM Output

**Symptom:** Expected content not rendering

**Debug:**
```javascript
console.log('Line:', line);
console.log('Match:', line.match(/pattern/));
```

**Common Cause:** LLM puts markdown syntax in different position

**Example:**
```
Expected: TOTAL: **£2,609**
Actual:   **TOTAL: £2,609**
```

**Solution:** Make regex flexible with `\*\*?` for optional bold

### Issue 2: Section Not Closing

**Symptom:** Styles bleeding into next section

**Debug:**
```javascript
console.log('[SECTION] Entering:', newSection);
console.log('[SECTION] Closing:', currentSection);
```

**Solution:** Close ALL possible previous sections:
```javascript
if (currentSection === 'price') html += '</div>';
if (currentSection === 'breakdown') html += '</ul></div></div>';
```

### Issue 3: Browser Caching

**Symptom:** Changes not showing despite deployment

**Not the cause:** Usually the regex/parsing logic!

**Quick test:**
```javascript
console.log('[DEBUG] Parser version: 2025-11-02');
```

**Solution:** Check console logs FIRST before blaming cache

---

## 💾 Data Structures

### Tool Result Format (get_price)

```json
{
    "productName": "Alwinton Snuggler",
    "fabricName": "Sussex Plain - Pacific",
    "price": "£1,958",
    "oldPrice": "£2,304",
    "imageUrls": ["..."],  // ❌ Broken - returns 404
    "specs": [...],
    "fabricDetails": {
        "tier": "Essentials",
        "description": "...",
        "swatchUrl": "..."
    }
}
```

**Ready to add:**
```json
{
    "productUrl": "https://sofasandstuff.com/alwinton?sku=alwsnufitttpac"  // ✅ Works!
}
```

### Grok Response Format

**Markdown with sections:**
```markdown
### 💰 Price
**Product Name** in **Fabric**
~~£old~~ → **£new** *(Save £amount!)*

### ✨ Key Features
• Feature 1
• Feature 2

### 🎯 Opportunities to Enhance
> **Option 1** - Details
> **Option 2** - Details

### 💬 What would you like to know next?
- Suggestion 1
- Suggestion 2
- Suggestion 3
```

---

## 🎓 Lessons Learned Repository

### Lesson 1: Don't Assume LLM Format

**Date:** Previous session (TOTAL price bug)
**Problem:** Assumed `TOTAL: **£amount**`, got `**TOTAL: £amount**`
**Time Lost:** 20+ minutes without debug logs
**Time With Logs:** 5 minutes
**Takeaway:** Always add console.log FIRST

### Lesson 2: Test External URLs

**Date:** 2025-11-02 (this session)
**Problem:** Assumed imageURLs would work
**Discovery:** They return 404, same as v1
**Saved:** Hours of implementation on broken feature
**Takeaway:** curl test before implementing

### Lesson 3: Same Patterns = Safe

**Date:** 2025-11-02 (this session)
**Observation:** imageUrls already in response
**Insight:** Adding productUrl uses same pattern
**Confidence:** High (risk assessment: 2/10)
**Takeaway:** Reuse proven patterns

### Lesson 4: User Skepticism is Valuable

**Date:** 2025-11-02 (this session)
**User asked:** "Didn't I capture imageURLs somewhere?"
**Result:** Testing revealed they're broken
**Impact:** Changed implementation approach
**Takeaway:** Validate user concerns with testing

---

## 🚀 Ready-to-Use Code Snippets

### Snippet 1: Add Field to Backend Response

```python
# In get_price_logic() at line ~735

# Build the URL
product_url = f"https://sofasandstuff.com/{product_name_keyword}?sku={query_sku}"

# Add to response (just one line!)
simplified_response = {
    "productName": full_name,
    "fabricName": fabric_name,
    "price": record.get('PriceText', 'N/A'),
    "oldPrice": record.get('OldPriceText', None),
    "imageUrls": image_urls,
    "productUrl": product_url,  # ← ADD THIS LINE
    "specs": record.get('ProductSizeAttributes', []),
    "fabricDetails": {
        "tier": fabric_match_data.get('tier', 'Unknown'),
        "description": fabric_match_data.get('desc', ''),
        "swatchUrl": fabric_match_data.get('swatch_url', '')
    }
}
```

### Snippet 2: Frontend Product Link Detection

```javascript
// In formatResponse() function

// Detect product name (bold text at start of line)
if (line.startsWith('**') && line.includes('**')) {
    const productMatch = line.match(/\*\*([^*]+)\*\*/);
    if (productMatch) {
        const productName = productMatch[1];

        // If we have productUrl from response, use it
        if (currentProductUrl) {
            const linkedName = `<a href="${currentProductUrl}" target="_blank" class="product-link">${escapeHtml(productName)}</a>`;
            line = line.replace(`**${productName}**`, linkedName);
        }
    }
}
```

### Snippet 3: CSS for Product Links

```css
.product-link {
    color: #0369a1;
    font-weight: 700;
    text-decoration: underline;
    text-decoration-color: #38bdf8;
    text-decoration-thickness: 2px;
    text-underline-offset: 3px;
    transition: all 0.2s ease;
}

.product-link:hover {
    color: #0ea5e9;
    text-decoration-color: #0ea5e9;
    transform: translateY(-1px);
}

.product-link:active {
    transform: translateY(0);
}
```

### Snippet 4: Test Backend Changes

```bash
# Test get_price endpoint
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}' \
  | python3 -m json.tool

# Check specific field
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}' \
  | jq .productUrl

# Expected output:
# "https://sofasandstuff.com/alwinton?sku=alwsnufitttpac"
```

### Snippet 5: SYSTEM_PROMPT Addition

```python
## PRODUCT LINKS

When showing a product price, make the product name clickable:

### Format:
**[Product Name](productUrl)** in **Fabric**

Use the `productUrl` field from the tool result.

EXAMPLE:
**[Alwinton Snuggler](https://sofasandstuff.com/alwinton?sku=alwsnufitttpac)** in **Sussex Plain - Pacific**
```

---

## 📁 File Map

### Backend Files:
```
main.py
├── Line 566: product_name_keyword extraction
├── Line 655: query_sku construction ← ALREADY BUILT!
├── Line 723-735: simplified_response ← ADD productUrl here
├── Line 140-160: SYSTEM_PROMPT follow-up suggestions
└── Line 695-715: imageUrls handling (reference pattern)
```

### Frontend Files:
```
index.html
├── Line 150-162: Product name CSS
├── Line 195-234: Total price CSS
├── Line 301-348: Suggestions CSS ← Just added!
├── Line 802: suggestions array initialization
├── Line 831-837: Suggestions section detection
├── Line 931-947: Suggestion bullet extraction
├── Line 967-978: Suggestions rendering
└── Line 988-998: Suggestion click handler
```

### Documentation Files:
```
.claude/
├── context.md (Lines 1429-1591: PIECE 4 planning)
├── instructions.md (Auto-loads context.md)
└── KNOWLEDGE_BASE.md (This file!)

/tmp/
├── PIECE_4_ANALYSIS.md (Implementation options)
├── PIECE_4_URL_VALIDATION.md (Testing results)
├── SESSION_SUMMARY_2025-11-02.md (Session overview)
└── RESUME_HERE_2025-11-02.md (Quick start guide)
```

---

## 🎯 Next Session Checklist

### Before Starting:

- [ ] Read `/tmp/RESUME_HERE_2025-11-02.md` (5 min)
- [ ] Review `.claude/context.md` lines 1429-1591 (10 min)
- [ ] Check live site still working (2 min)
- [ ] Pull latest from GitHub (1 min)

### Ready to Code:

**Say:** "Let's implement PIECE 4 product links"

**I will:**
1. Show you the exact code change (3 lines)
2. Deploy to GCF v2 (3 min)
3. Test with curl (2 min)
4. Update frontend (15 min)
5. Test on live site (5 min)

**Total:** 1-1.5 hours

---

## 📞 Quick Commands Reference

```bash
# Deploy backend
gcloud functions deploy sofa-price-calculator-v2 --gen2 --runtime=python311 --region=europe-west2 --source=. --entry-point=http_entry_point --trigger-http --allow-unauthenticated --timeout=120s

# Test backend
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice -H "Content-Type: application/json" -d '{"query": "alwinton snuggler pacific"}' | jq .

# Deploy frontend
git add index.html && git commit -m "Add product links" && git push

# Open live site
open https://sameercodes28.github.io/ss-price-tool-v2/

# Check GCF logs
gcloud functions logs read sofa-price-calculator-v2 --region=europe-west2 --limit=50
```

---

## 💡 Pro Tips

### Tip 1: Always Use jq for JSON

**Bad:**
```bash
curl ... | cat
```

**Good:**
```bash
curl ... | python3 -m json.tool
# or
curl ... | jq .
```

### Tip 2: Debug with Console, Not Deployment

**Add this to every new feature:**
```javascript
console.log('[FEATURE_NAME] Step:', details);
```

**Remove after confirming it works**

### Tip 3: Test URLs Independently

**Before using in code:**
```bash
curl -I "https://url-to-test" 2>&1 | head -5
```

**Saves hours of debugging broken URLs**

### Tip 4: Git Commit Often

**After each working state:**
```bash
git add .
git commit -m "Clear description of what works"
git push
```

**Easy rollback if next change breaks**

### Tip 5: Document While Coding

**Update .claude/context.md as you go:**
- When you discover something
- When you fix a bug
- When you complete a feature

**Don't wait until end of session!**

---

## 🎉 Success Metrics

### PIECE 3 (Completed):
- **Time:** 2 hours
- **Risk:** 3/10
- **Bugs:** 0
- **User Satisfaction:** "Working great!"

### PIECE 4 (Ready):
- **Planning Time:** 1 hour
- **URLs Tested:** ✅ Verified
- **Risk:** 2/10
- **Estimated Time:** 1-1.5 hours

---

**All knowledge captured. Ready for next session! 🚀**

**Last Updated:** 2025-11-02
**Next Update:** After PIECE 4 implementation
