# v1 & v2 Setup Guide

**Last Updated:** November 2, 2025
**Status:** ✅ Complete - Both v1 and v2 are live and operational

---

## 🎯 Overview

You now have **two completely separate deployments** of the Sofas & Stuff Price Tool:

- **v1:** Stable, production-ready version (frozen, no experimental changes)
- **v2:** Experimental version for testing new features (safe to break)

Both versions run **independently** with separate infrastructure, so v2 experiments cannot affect v1.

---

## 📊 Complete Setup Summary

| Component | v1 (Stable) | v2 (Experimental) |
|-----------|-------------|-------------------|
| **Local Directory** | `~/Desktop/SS-1` | `~/Desktop/SS-2` |
| **GitHub Repo** | (Your existing repo) | https://github.com/sameercodes28/ss-price-tool-v2 |
| **Google Cloud Project** | `sofaproject-476903` | `sofa-project-v2` |
| **GCF Function Name** | `sofa-price-calculator` | `sofa-price-calculator-v2` |
| **Backend URL** | `https://europe-west2-sofaproject-476903.cloudfunctions.net/sofa-price-calculator` | `https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2` |
| **Frontend URL** | (Your v1 GitHub Pages) | https://sameercodes28.github.io/ss-price-tool-v2/ |
| **Status** | 🟢 Production (frozen) | 🟡 Experimental (active development) |
| **Purpose** | Stable fallback demo | Testing new features |

---

## 🛠️ Working with v1 (Stable)

### When to Work on v1
- Critical bug fixes only
- Minor improvements (v1.1, v1.2, etc.)
- Security patches
- Data updates (re-running scraper)

### How to Work on v1
```bash
# Switch to v1 directory
cd ~/Desktop/SS-1

# Make your changes (be conservative!)

# Test locally first
functions-framework --target=http_entry_point --debug

# Deploy to v1 GCF
gcloud config set project sofaproject-476903
gcloud functions deploy sofa-price-calculator \
  --gen2 \
  --runtime python312 \
  --entry-point http_entry_point \
  --trigger-http \
  --allow-unauthenticated \
  --region europe-west2 \
  --timeout 60s \
  --memory 512MB

# Commit changes
git add .
git commit -m "v1.1: Description of safe changes"
git push origin main
```

### ⚠️ Important v1 Rules
- **DO NOT** make experimental changes in v1
- **DO NOT** try radical new features in v1
- **ALWAYS** test locally before deploying
- **KEEP** v1 as your stable fallback

---

## 🚀 Working with v2 (Experimental)

### When to Work on v2
- Testing new features
- Trying different architectures
- Experimenting with improvements
- Adding risky changes
- Learning new techniques

### How to Work on v2
```bash
# Switch to v2 directory
cd ~/Desktop/SS-2

# Make ANY changes you want (experiment freely!)

# Test locally
functions-framework --target=http_entry_point --debug

# Deploy to v2 GCF
gcloud config set project sofa-project-v2
gcloud functions deploy sofa-price-calculator-v2 \
  --gen2 \
  --runtime python312 \
  --entry-point http_entry_point \
  --trigger-http \
  --allow-unauthenticated \
  --region europe-west2 \
  --timeout 60s \
  --memory 512MB

# Commit changes
git add .
git commit -m "v2: Description of experimental changes"
git push origin main
```

### ✅ v2 Freedoms
- **Feel free** to break things
- **Experiment** with radical changes
- **Try** new libraries and approaches
- **Don't worry** about stability
- **v1 is safe** if v2 fails

---

## 🔄 Common Workflows

### Scenario 1: Testing a New Feature

```bash
# Work in v2 (safe to experiment)
cd ~/Desktop/SS-2

# Make changes
# ... edit files ...

# Test locally
functions-framework --target=http_entry_point --debug
# In another terminal:
curl -X POST http://localhost:8080/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'

# Deploy to v2
gcloud config set project sofa-project-v2
gcloud functions deploy sofa-price-calculator-v2 ...

# Test live at: https://sameercodes28.github.io/ss-price-tool-v2/
```

### Scenario 2: Bug Fix in v1

```bash
# Work in v1 (careful, production!)
cd ~/Desktop/SS-1

# Fix the bug
# ... edit files ...

# Test thoroughly locally
functions-framework --target=http_entry_point --debug

# Deploy to v1 (production)
gcloud config set project sofaproject-476903
gcloud functions deploy sofa-price-calculator ...

# Tag as v1.1
git tag -a v1.1.0 -m "Bug fix: Description"
git push origin main --tags
```

### Scenario 3: Copying a Fix from v1 to v2

```bash
# If you fix a bug in v1 and want it in v2:
cd ~/Desktop/SS-1
# ... make fix ...

# Manually copy the fix to v2
cd ~/Desktop/SS-2
# ... apply same fix ...

# Or use diff/patch:
cd ~/Desktop
diff SS-1/main.py SS-2/main.py
# Manually merge the changes
```

### Scenario 4: v2 Succeeds → Promote to Production

```bash
# If v2 is ready to replace v1:

# Option A: Keep v1 as fallback, make v2 the new default
# - Update your main links to point to v2
# - Keep v1 running as backup

# Option B: Retire v1, promote v2
# - Copy v2 changes back to v1
# - Update v1 deployment
# - Delete v2 or keep for v3 experiments
```

---

## 🧪 Testing Both Versions

### Test v1
```bash
# Health check
curl https://europe-west2-sofaproject-476903.cloudfunctions.net/sofa-price-calculator/

# Price query
curl -X POST https://europe-west2-sofaproject-476903.cloudfunctions.net/sofa-price-calculator/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'

# Frontend
open "https://YOUR-V1-GITHUB-PAGES-URL"
```

### Test v2
```bash
# Health check
curl https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/

# Price query
curl -X POST https://europe-west2-sofa-project-v2.cloudfunctions.net/sofa-price-calculator-v2/getPrice \
  -H "Content-Type: application/json" \
  -d '{"query": "alwinton snuggler pacific"}'

# Frontend
open "https://sameercodes28.github.io/ss-price-tool-v2/"
```

---

## 💰 Cost Implications

**Good news:** Both v1 and v2 are still **FREE**!

- **v1 Free Tier:** 2M requests/month
- **v2 Free Tier:** 2M requests/month (separate quota)
- **Total Free Tier:** 4M requests/month combined

Unless you exceed 2M requests on **either** project individually, you won't be charged.

---

## 🚨 Important Reminders

### Before Working on v1
1. ✅ Are you sure this can't be tested in v2 first?
2. ✅ Have you tested locally?
3. ✅ Is this a safe, conservative change?
4. ✅ Do you have v1 as a backup (git history)?

### Before Working on v2
1. ✅ Are you in the right directory? (`~/Desktop/SS-2`)
2. ✅ Are you using the right gcloud project? (`sofa-project-v2`)
3. ✅ Remember: v1 is unaffected by anything you do here!

---

## 📂 Directory Structure

```
~/Desktop/
├── SS-1/                          # v1 (Stable - DO NOT EXPERIMENT)
│   ├── main.py
│   ├── index.html
│   ├── products.json
│   ├── sizes.json
│   ├── covers.json
│   ├── fabrics.json
│   ├── .git/                      # v1 git history
│   └── ... (all v1 files)
│
└── SS-2/                          # v2 (Experimental - GO WILD!)
    ├── main.py                    # Same as v1 initially
    ├── index.html                 # Points to v2 backend
    ├── products.json              # Same as v1 initially
    ├── sizes.json                 # Same as v1 initially
    ├── covers.json                # Same as v1 initially
    ├── fabrics.json               # Same as v1 initially
    ├── .git/                      # v2 git history (separate)
    ├── V1_V2_SETUP_GUIDE.md       # This file
    └── ... (all v2 files)
```

---

## 🎓 Quick Command Reference

### Check Which Project You're Using
```bash
gcloud config get-value project
# Should show: sofaproject-476903 (v1) or sofa-project-v2 (v2)
```

### Switch Projects
```bash
# Switch to v1
gcloud config set project sofaproject-476903

# Switch to v2
gcloud config set project sofa-project-v2
```

### List All Functions
```bash
# v1 functions
gcloud config set project sofaproject-476903
gcloud functions list

# v2 functions
gcloud config set project sofa-project-v2
gcloud functions list
```

### View Logs
```bash
# v1 logs
gcloud config set project sofaproject-476903
gcloud functions logs read sofa-price-calculator --limit=50

# v2 logs
gcloud config set project sofa-project-v2
gcloud functions logs read sofa-price-calculator-v2 --limit=50
```

---

## ✅ Setup Complete!

Your v1 and v2 setup is now complete. Here's what you have:

- ✅ v1 deployed and stable (your fallback demo)
- ✅ v2 deployed and ready for experimentation
- ✅ Separate infrastructure (repos, GCF projects, URLs)
- ✅ Complete isolation (v2 can't break v1)
- ✅ Free tier on both (4M requests/month total)

**You're ready to start experimenting with v2 while keeping v1 safe!**

---

## 🎯 Next Steps

1. **Test v2:** Open https://sameercodes28.github.io/ss-price-tool-v2/ and try a query
2. **Start Experimenting:** Make your first v2 change in `~/Desktop/SS-2`
3. **Document Your Goals:** Update `SS-2/README.md` with your v2 objectives
4. **Have Fun:** Break things, try new ideas, learn!

---

**Questions?** Check the README files in both v1 and v2 directories, or refer to the `.claude/context.md` files for detailed project state.

**Happy Coding!** 🚀
