# Changelog - v2

All notable changes to the **v2** version of the Sofas & Stuff Voice Price Tool will be documented in this file.

> **Note:** This is the v2 changelog. For v1 stable release history, see [v1 repository](https://github.com/sameercodes28/SS).

---

## [2.1.0] - 2025-11-02 🎭 DEMO STAGE - Phase 1C Complete

### LLM Integration - Grok-4 Conversational Agent
This release adds full AI chat agent capabilities powered by xAI's Grok-4 model via OpenRouter API.

### 🚀 Major Features Added

#### 1. Conversational Chat Interface (`/chat` endpoint)
- Natural language conversation with Grok-4 LLM
- Multi-turn conversation support with context tracking
- Session-based conversation management (session_id parameter)
- OpenRouter API integration using OpenAI-compatible SDK
- Conversation history maintained in browser (client-side)

#### 2. Tool Calling System (3 Tools)
**get_price** - Precise pricing for any product configuration
- Inputs: Natural language query (e.g., "alwinton snuggler pacific")
- Returns: Exact price, product details, fabric info, variant info
- Example: £1,958 for Alwinton Snuggler in Pacific fabric

**search_by_budget** - Find products under a budget
- Inputs: max_price (e.g., 2000), optional product_type filter
- Returns: All matching products sorted by price
- Includes fabric tier guidance (Tier 1-6 price ranges)
- Example: Found Midhurst £1,937 and Petworth £1,941 under £2,000

**search_fabrics_by_color** - Search fabrics by color name
- Inputs: color (e.g., "blue"), optional product_name filter
- Returns: All matching fabrics grouped by tier
- Deduplicated by unique fabric-color combinations
- Example: Found 24 blue fabrics across 6 tiers

#### 3. Feature Flag Architecture
- `USE_LLM` feature flag in frontend (line 345)
- Dual-path support: LLM mode (/chat) vs Direct matching mode (/getPrice)
- Can toggle between AI agent and v1 logic without code changes
- Fallback mechanism ensures v1 functionality always available

### 🛠️ Technical Implementation

#### Backend Changes (main.py)
- Lines 78-93: SYSTEM_PROMPT defining agent behavior and tool usage
- Lines 95-235: TOOLS schema (OpenAI function calling format)
- Lines 285-330: get_price tool handler with MockRequest pattern
- Lines 354-454: search_by_budget tool handler with fabric tier logic
- Lines 456-568: search_fabrics_by_color tool handler with deduplication
- Lines 845-1009: /chat endpoint with conversation loop (max 5 iterations)
- Environment variables: OPENROUTER_API_KEY, GROK_MODEL (x-ai/grok-4)

#### Frontend Changes (index.html)
- Lines 345-346: USE_LLM feature flag
- Lines 354-376: Session management (generateSessionId, resetConversation)
- Lines 354-376: conversationHistory array tracking full conversation
- Lines 597-742: Dual-path sendMessage() with LLM and non-LLM logic
- Lines 743-790: handleChatResponse() parsing tool-based responses
- Console logging for metadata (tokens, iterations, model)

### 📊 Test Results (All Passed ✅)

**Baseline Test:** /getPrice still works (no breakage)
```bash
curl .../getPrice -d '{"query": "alwinton snuggler pacific"}'
→ {"price": "£1,958", ...} ✅
```

**Test 1:** Greeting
```bash
curl .../chat -d '{"messages": [{"role": "user", "content": "Hello"}], "session_id": "test"}'
→ Natural greeting response (3,861 tokens) ✅
```

**Test 2:** get_price tool
```bash
curl .../chat -d '{"messages": [{"role": "user", "content": "How much is alwinton snuggler pacific?"}], ...}'
→ £1,958 with full details (8,812 tokens, 2 iterations) ✅
```

**Test 3:** search_by_budget tool
```bash
curl .../chat -d '{"messages": [{"role": "user", "content": "What sofas under £2,000?"}], ...}'
→ Found 2 matching sofas (8,420 tokens, 2 iterations) ✅
```

**Test 4:** search_fabrics_by_color tool
```bash
curl .../chat -d '{"messages": [{"role": "user", "content": "Show me blue fabrics"}], ...}'
→ Found 24 blue fabrics (11,908 tokens, 2 iterations) ✅
```

### 🎯 Deployment Details
- **Status:** ✅ LIVE AND FUNCTIONAL
- **Backend:** Deployed to GCF with OpenRouter API key
- **Frontend:** Deployed to GitHub Pages with USE_LLM=true
- **Git Tag:** `demo-ready-phase-1c-complete`
- **Branch:** Merged `feature/grok-llm` → `main`

### 📝 Documentation Updates
- ✅ .claude/context.md - Added Phase 1C session summary
- ✅ README.md - Updated with Demo Stage notice and features
- ✅ CHANGELOG.md - This entry
- ✅ TECHNICAL_GUIDE.md - Updated with LLM architecture

### 🔮 Known Limitations (To Be Addressed in Demo Polish Phase)
- Temperature not set (defaults to 1.0, needs 0.1 for precise responses)
- Responses are plain text paragraphs (needs markdown formatting)
- No follow-up question suggestions (planned: Perplexity-style chips)
- No clickable product/fabric links (URLs available in data, needs integration)
- No real-time streaming (uses loading dots, planned: SSE streaming)

### 🎭 Demo Polish Phase - Planned Next
- [ ] Piece 1: Set temperature=0.1 for deterministic responses
- [ ] Piece 2: Markdown formatting for better readability
- [ ] Piece 3: Follow-up question suggestions as clickable chips
- [ ] Piece 4: Clickable product/fabric links to sofasandstuff.com
- [ ] Piece 5: Real-time streaming responses via SSE

---

## [2.0.0] - 2025-11-02 ✅ DEPLOYED

### Initial v2 Release
This is the initial v2 production release, forked from v1.0.0 stable.

### Deployment Status
- ✅ v2 backend deployed to Google Cloud Functions (separate project)
- ✅ v2 frontend deployed to GitHub Pages (separate repo)
- ✅ v2 backend URL configured in frontend (index.html:187)
- ✅ All v2 systems operational
- ✅ v1 remains unaffected and continues running

### Infrastructure
- **GitHub Repo:** https://github.com/sameercodes28/ss-price-tool-v2
- **Google Cloud Project:** `sofa-project-v2` (separate from v1)
- **Backend GCF:** `sofa-price-calculator-v2`
- **Frontend URL:** https://sameercodes28.github.io/ss-price-tool-v2/
- **Backend URL:** https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2

### Inherited from v1.0.0
- Complete working voice-enabled price lookup tool
- Support for 210 products across 9 product types
- Natural language query processing with fuzzy matching
- Smart 2-API routing system (Sofa API vs Bed API)
- In-memory caching (5-minute TTL)
- Retry logic for failed API requests
- Ambiguity detection with helpful suggestions
- Mattress support with tension options
- All 4 JSON data files (26 MB total)

### Fixed in v2 Initial Release
- JavaScript syntax error in onclick handler (index.html:462)
  - Changed `button.onclick = ()D =>` to `button.onclick = () =>`
  - This bug was in v1.0.0, fixed during v2 setup
  - Also applied fix to v1 as v1.0.1

### Documentation (v2 Specific)
- ✅ README.md updated for v2 production development
- ✅ V1_V2_SETUP_GUIDE.md created
- ✅ .claude/context.md initialized for v2
- ✅ .claude/instructions.md updated for v2
- ✅ PRD.md updated to reflect v2 production development status

### Technical
- Backend: Python 3.12, Google Cloud Functions (Gen 2)
- Frontend: Vanilla JavaScript, TailwindCSS
- Deployment: europe-west2 region, 512MB memory, 60s timeout
- Monthly cost: $0 (within free tier, separate from v1)

---

## v2 Development Goals

Track your v2 features here as you develop them:

### Planned Features
- [ ] (Document your v2 goals here)
- [ ] (Add new features incrementally)
- [ ] (Improve architecture step-by-step)

### Completed Features
- [x] v2 infrastructure setup
- [x] Separate deployment from v1
- [x] Bug fix: onclick handler syntax error

---

## Relationship to v1

**v1 (Stable):** Production release at ~/Desktop/SS-1
**v2 (Production Development):** This version - built incrementally with thorough testing

Changes in v2 do NOT affect v1. Both versions run independently with separate:
- GitHub repositories
- Google Cloud projects
- Deployment URLs
- Documentation

---

## Maintenance Log

### Data Inherited from v1
v2 currently uses the same JSON data files as v1:
- products.json: 210 products (71 KB)
- sizes.json: 95 products with size mappings (20 KB)
- covers.json: 95 products with cover options (4.8 KB)
- fabrics.json: 95 products with fabric data (23 MB)

### Future v2-Specific Enhancements
Document your v2 enhancements here:
- [ ] (Add your v2 ideas)
- [ ] (Develop new features incrementally)
- [ ] (Implement improvements step-by-step)

---

**Last Updated:** November 2, 2025
