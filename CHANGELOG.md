# Changelog

All notable changes to the Sofas & Stuff Voice Price Tool will be documented in this file.

## [1.0.0] - 2025-11-02 ✅ DEPLOYED

### Deployment Status
- ✅ Backend deployed to Google Cloud Functions
- ✅ Frontend deployed to GitHub Pages
- ✅ Production URL configured in frontend (index.html:187)
- ✅ All systems operational

### Added
- Complete working v1 of voice-enabled price lookup tool
- Support for 210 products across 9 product types
- Natural language query processing with fuzzy matching
- Smart 2-API routing system (Sofa API vs Bed API)
- In-memory caching (5-minute TTL)
- Retry logic for failed API requests
- Ambiguity detection with helpful suggestions
- Mattress support with tension options
- Comprehensive documentation (README, TECHNICAL_GUIDE, ARCHITECTURE)

### Fixed
- Fabric swatch URL bug (main.py:344) - changed from `swatch` to `swatch_url`
- Mattress routing now correctly uses Sofa API with special SKU format
- Image URL encoding for paths with spaces

### Data
- Generated 4 JSON files from web scraper:
  - products.json: 210 products (71 KB)
  - sizes.json: 95 products with size mappings (20 KB)
  - covers.json: 95 products with cover options (4.8 KB)
  - fabrics.json: 95 products with fabric data (23 MB)
- Total data coverage: 95 products with complete data (100% of scraped products)

### Technical
- Backend: Python 3.12, Google Cloud Functions (Gen 2)
- Frontend: Vanilla JavaScript, TailwindCSS
- Deployment: europe-west2 region, 512MB memory, 60s timeout
- Monthly cost: $0 (within free tier)

---

## Maintenance Log

### Quarterly Data Refresh
**Next scheduled:** 2026-02-01

When to re-scrape:
- S&S adds new products
- Fabric/color options change
- Quarterly maintenance (recommended)

### Future Enhancements
- [ ] Add authentication for internal use
- [ ] Implement analytics/logging
- [ ] Add product search suggestions
- [ ] Support for bundles/packages
