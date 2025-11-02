# Changelog - v2 (Experimental)

All notable changes to the **v2 experimental** version of the Sofas & Stuff Voice Price Tool will be documented in this file.

> **Note:** This is the v2 changelog. For v1 stable release history, see [v1 repository](https://github.com/sameercodes28/SS).

---

## [2.0.0-alpha] - 2025-11-02 ✅ DEPLOYED

### Initial v2 Release
This is the initial experimental release, forked from v1.0.0 stable.

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
- ✅ README.md updated for v2 experimental status
- ✅ V1_V2_SETUP_GUIDE.md created
- ✅ .claude/context.md initialized for v2
- ✅ .claude/instructions.md updated for v2
- ✅ PRD.md updated to reflect v2 experimental status

### Technical
- Backend: Python 3.12, Google Cloud Functions (Gen 2)
- Frontend: Vanilla JavaScript, TailwindCSS
- Deployment: europe-west2 region, 512MB memory, 60s timeout
- Monthly cost: $0 (within free tier, separate from v1)

---

## v2 Development Goals

Track your v2 experimental features here as you develop them:

### Planned Features
- [ ] (Document your v2 goals here)
- [ ] (Add new experimental features)
- [ ] (Try new architectures)

### Completed Features
- [x] v2 infrastructure setup
- [x] Separate deployment from v1
- [x] Bug fix: onclick handler syntax error

---

## Relationship to v1

**v1 (Stable):** Production release at ~/Desktop/SS-1
**v2 (Experimental):** This version - safe to break things!

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
Document your v2 experimental enhancements here:
- [ ] (Add your v2 ideas)
- [ ] (Try new features)
- [ ] (Experiment with improvements)

---

**Last Updated:** November 2, 2025
