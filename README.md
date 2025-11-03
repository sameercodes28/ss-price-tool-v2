# Sofas & Stuff Voice Price Check Tool - v2

**Version:** 2.3.1 (Hallucination-Proof)
**Status:** 🚀 **PRODUCTION** - Intelligent LLM-Powered Assistant (Hallucination-Safe)
**Parent Project:** [v1.0.0 (Stable)](https://github.com/sameercodes28/SS) (v1 repository)
**Last Updated:** November 3, 2025

> **⚠️ IMPORTANT:** This is v2 production development. The stable v1 is deployed separately and remains unaffected by changes here.

> **🚀 PRODUCTION:** v2 features a superior AI assistant powered by Grok-4 with automatic error correction, intelligent defaults, and effortless user experience. The system auto-corrects misspellings, makes smart assumptions, and never burdens users with clarifications.

An AI-powered conversational assistant for Sofas & Stuff salespeople. This v2 version uses Grok-4 LLM to provide intelligent product recommendations, pricing, and fabric searches through natural conversation.

---

## 🎯 v2 Goals & Features

### ✅ Phase 1C Complete - LLM Integration (Grok-4)
- [x] Natural language conversation interface
- [x] **get_price** tool - Precise pricing for any product + fabric + variant
- [x] **search_by_budget** tool - Find all products under budget with fabric tier guidance
- [x] **search_fabrics_by_color** tool - Search fabrics by color name
- [x] Session-based conversation tracking (session_id support)
- [x] Multi-turn conversation context (maintains conversation history)
- [x] OpenRouter API integration for Grok-4 access
- [x] Feature flag architecture (can toggle LLM on/off)

### 🎭 Demo Polish Phase
- [ ] Real-time streaming responses (eliminate loading dots)
- [ ] Markdown formatting for better readability
- [x] Follow-up question suggestions (Perplexity-style chips) ✅ Completed
- [ ] Clickable product/fabric links to sofasandstuff.com
- [x] Temperature optimization (0.1 for precise responses) ✅ Completed

### 🔮 Future Phases
- [ ] **Phase 1B:** Session storage backend (Firestore/Redis)
- [ ] **Phase 1D:** Add-ons pricing (cushions, feet, delivery)
- [ ] **Phase 2:** Voice input/output integration
- [ ] **Phase 3:** Memory system (customer preferences, past quotes)

---

## 🔗 Related Projects

- **v1 Stable:** [SS-1](https://github.com/sameercodes28/SS) - Production deployment (separate repo)
- **v2 Production Development:** This repository - Active development

---

## 🚀 Quick Start (v2)

### Prerequisites
- Python 3.10+ installed
- Google Cloud account (separate project from v1)
- GitHub account (for frontend hosting)
- All 4 JSON files generated (inherited from v1)

### 1. Clone & Setup
```bash
cd ~/Desktop/SS-2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Test Locally
```bash
functions-framework --target=http_entry_point --debug
```

In a new terminal:
```bash
# Test legacy /getPrice endpoint
curl -X POST http://localhost:8080/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'

# Test LLM /chat endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "How much is an alwinton snuggler in pacific?"}], "session_id": "test-session"}'
```

Expected:
- /getPrice → JSON with price ~£1,958
- /chat → Natural language response with pricing details

### 3. Set Up Environment Variables
Create a `.env` file (not committed to git):
```bash
OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
GROK_MODEL=x-ai/grok-4
```

Get your OpenRouter API key from: https://openrouter.ai/settings/keys

### 4. Deploy Backend (v2 GCF)
```bash
# Make sure you're using the v2 Google Cloud project
gcloud config set project sofa-project-v2

gcloud functions deploy sofa-price-calculator-v2 \
  --gen2 \
  --runtime python312 \
  --entry-point http_entry_point \
  --trigger-http \
  --allow-unauthenticated \
  --region europe-west2 \
  --timeout 60s \
  --memory 512MB \
  --set-env-vars OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE,GROK_MODEL=x-ai/grok-4
```

### 5. Update & Deploy Frontend
Edit `index.html` line 340 with your v2 backend URL:
```javascript
const BACKEND_API_URL = 'https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2';
```

Push to GitHub and enable GitHub Pages.

**Done!** Your v2 app is live at `https://britishmade.ai/`

---

## 📖 Documentation

*(Inherited from v1, update as v2 diverges)*

- **[README.md](README.md)** - This file (v2 specific)
- **[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)** - Complete technical deep dive
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/PRD.md](docs/PRD.md)** - Product requirements

---

## 🎯 Development Workflow

### Making Changes to v2
```bash
cd ~/Desktop/SS-2
# Make your changes
git add .
git commit -m "v2: Add new feature"
git push origin main

# Deploy to v2 GCF (separate from v1)
gcloud functions deploy sofa-price-calculator-v2 ...
```

### Keeping v1 Stable
- **Do NOT** make changes in `~/Desktop/SS-1`
- v1 remains frozen and deployed separately
- v1 serves as your fallback if v2 experiments fail

---

## 🔄 Syncing Bug Fixes from v1

If you fix a bug in v1 and want it in v2:
```bash
# Manually copy the fix from SS-1 to SS-2
# Or use git cherry-pick if you set up git remotes
```

---

## 💡 Key Differences from v1

### 🤖 LLM Integration (Phase 1C)
- **Conversational Interface:** Natural language chat instead of keyword matching
- **Tool Calling:** Grok-4 LLM decides which tools to call based on conversation context
- **Multi-Turn Context:** Maintains conversation history across multiple messages
- **Session Management:** Session IDs track individual conversations (storage coming in Phase 1B)
- **OpenRouter API:** Uses OpenRouter proxy for Grok-4 access
- **Feature Flags:** `USE_LLM` toggle allows fallback to v1 logic

### 🛠️ New Backend Endpoints
- `/chat` - LLM-powered conversational endpoint (Phase 1C)
- `/getPrice` - Legacy direct matching endpoint (inherited from v1, still works)

### 🎨 Frontend Changes
- Dual-path architecture: LLM mode vs. Direct matching mode
- Conversation history tracking in browser
- Session ID generation and management
- Support for tool-based responses (pricing, budgets, fabrics)

---

## 🚨 Deployment Info

### v2 Deployments (Separate from v1)
- **Backend:** `https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2`
- **Frontend:** `https://britishmade.ai/`
- **Telemetry:** `https://britishmade.ai/telemetry.html` (Password: SOFAS25)
- **Google Cloud Project:** `sofa-project-v2` (Separate project)
- **OpenRouter API:** Proxies requests to Grok-4 via OpenAI-compatible SDK

### v1 Deployments (Untouched)
- **Backend:** `sofa-price-calculator` (Original GCF function)
- **Frontend:** `https://sameercodes28.github.io/SS/` (Original GitHub Pages URL)
- **Google Cloud Project:** `sofaproject-476903` (Original project)

---

## 🧪 Testing

### Test Legacy /getPrice Endpoint
```bash
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'
```
Expected: `{"price": "£1,958", ...}`

### Test LLM /chat Endpoint
```bash
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "How much is an alwinton snuggler in pacific?"}],
    "session_id": "test-session"
  }'
```
Expected: Natural language response with pricing details and metadata (tokens, iterations, model)

### Frontend Testing
Visit: https://britishmade.ai/

Try these queries:
- "How much is an alwinton snuggler in pacific?" (get_price tool)
- "What sofas can I get for under £2,000?" (search_by_budget tool)
- "Show me all blue fabrics" (search_fabrics_by_color tool)

---

## 📝 Notes

- This is forked from v1.0.0 (stable)
- Changes here do NOT affect v1
- v1 continues to run in production
- If v2 succeeds, it can replace v1 in the future
- If v2 fails, delete this repo and continue with v1

---

**Built with ❤️ for Sofas & Stuff**
**v2 Production Development - Forked from v1.0.0**
