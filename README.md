# Sofas & Stuff Voice Price Check Tool - v2 (Experimental)

**Version:** 2.0.0-alpha
**Status:** 🚧 Experimental / Development
**Parent Project:** [v1.0.0](https://github.com/YOUR_USERNAME/ss-price-tool-v1) (Stable)
**Last Updated:** November 2, 2025

> **⚠️ IMPORTANT:** This is v2 experimental development. The stable v1 is deployed separately and remains unaffected by changes here.

A voice-enabled price lookup tool for Sofas & Stuff salespeople. This v2 branch is for experimenting with new features and improvements.

---

## 🎯 v2 Goals

*(Document your v2 objectives here as you develop)*

- [ ] New feature 1
- [ ] New feature 2
- [ ] Performance improvements
- [ ] Architecture changes

---

## 🔗 Related Projects

- **v1 Stable:** [ss-price-tool-v1](https://github.com/YOUR_USERNAME/ss-price-tool-v1) - Production deployment
- **v2 Experimental:** This repository - Active development

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
curl -X POST http://localhost:8080/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'
```

Expected: JSON with price ~£1,409

### 3. Deploy Backend (v2 GCF)
```bash
# Make sure you're using the v2 Google Cloud project
gcloud config set project YOUR-V2-PROJECT-ID

gcloud functions deploy sofa-price-calculator-v2 \
  --gen2 \
  --runtime python312 \
  --entry-point http_entry_point \
  --trigger-http \
  --allow-unauthenticated \
  --region europe-west2 \
  --timeout 60s \
  --memory 512MB
```

### 4. Update & Deploy Frontend
Edit `index.html` line 187 with your v2 backend URL:
```javascript
const BACKEND_API_URL = 'https://YOUR-V2-GCF-URL/getPrice';
```

Push to GitHub and enable GitHub Pages.

**Done!** Your v2 app is live at `https://USERNAME.github.io/ss-price-tool-v2/`

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

*(Document what's different as you develop v2)*

- 🆕 New feature X
- 🔧 Changed architecture Y
- ⚡ Performance improvement Z

---

## 🚨 Deployment Info

### v2 Deployments (Separate from v1)
- **Backend:** `sofa-price-calculator-v2` (Different GCF function)
- **Frontend:** `https://USERNAME.github.io/ss-price-tool-v2/` (Different GitHub Pages URL)
- **Google Cloud Project:** `YOUR-V2-PROJECT-ID` (Separate project)

### v1 Deployments (Untouched)
- **Backend:** `sofa-price-calculator` (Original GCF function)
- **Frontend:** `https://USERNAME.github.io/ss-price-tool-v1/` (Original GitHub Pages URL)
- **Google Cloud Project:** `sofaproject-476903` (Original project)

---

## 🧪 Testing

Run the same tests as v1, but against v2 endpoints:

```bash
curl -X POST https://YOUR-V2-GCF-URL/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'
```

---

## 📝 Notes

- This is forked from v1.0.0 (stable)
- Changes here do NOT affect v1
- v1 continues to run in production
- If v2 succeeds, it can replace v1 in the future
- If v2 fails, delete this repo and continue with v1

---

**Built with ❤️ for Sofas & Stuff**
**v2 Experimental Branch - Forked from v1.0.0**
