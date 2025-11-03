# 🏗️ S&S Price Tool - System Architecture

**Last Updated:** November 2, 2025

---

## 🎯 **Two-Phase System Overview**

This application operates in **two distinct phases**:

### **Phase 1: Data Generation (One-Time Setup)**
**Who:** Developer only
**Where:** Local machine
**When:** Initially, then quarterly for updates
**Tool:** `sku_discovery_tool.py`

```
Developer → Scraper → S&S Website/APIs → 4 JSON Files
(You)       (Local)   (Scrapes HTML &    (products.json,
                       Fabric API)         sizes.json,
                                          covers.json,
                                          fabrics.json)
```

**Process:**
1. Scraper makes GET requests to S&S category pages (sofas, beds, etc.)
2. Extracts product names, SKUs, and types from HTML
3. For each product, calls `/GetPDPFabrics` API to get fabric options
4. Builds 4 JSON "brain" files with all translation mappings
5. Takes 20-30 minutes to complete

### **Phase 2: Live Application (Production Use)**
**Who:** Salespeople
**Where:** Any device with browser
**When:** 24/7 after deployment
**Tool:** `index.html` + `main.py`

```
Salesperson → Frontend → Backend → S&S APIs → Backend → Frontend → Salesperson
(Phone)      (GitHub   (GCF)      (Sofa/Bed  (Simplify (Display  (Sees price)
              Pages)               APIs)       response) results)
```

**Process:**
1. User speaks/types query
2. Frontend sends to backend
3. Backend translates using JSON files (loaded in memory)
4. Backend calls correct S&S API
5. Backend simplifies response and caches
6. Frontend displays price + images + specs

---

## 📐 **High-Level Architecture (Live Application)**

```
┌─────────────────────────────────────────────────────────────┐
│                      SALESPERSON                             │
│             (iPhone, iPad, Android, Desktop)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Says/Types:
                     │ "Alwinton snuggler pacific"
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (index.html)                      │
│                   Hosted on: GitHub Pages                    │
│                   Cost: FREE                                │
├─────────────────────────────────────────────────────────────┤
│  • Voice Input (webkitSpeechRecognition)                    │
│  • Text Input (fallback for Firefox, etc.)                  │
│  • Display: Price, Images, Specs, Fabric Details            │
│  • Query History (localStorage)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /getPrice
                     │ {"query": "alwinton snuggler pacific"}
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (main.py)                               │
│              Hosted on: Google Cloud Functions              │
│              Cost: FREE (2M requests/month free tier)       │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Parse Query                                        │
│    "alwinton"  → Product: SKU "alw", Type "sofa"           │
│    "snuggler"  → Size: SKU "snu"                           │
│    (default)   → Cover: SKU "fit"                          │
│    "pacific"   → Fabric: SKU "sxp", Color "pac"            │
│                                                             │
│  Step 2: Load Translation Dictionaries                     │
│    products.json  ← All products with SKUs                 │
│    sizes.json     ← Size options per product               │
│    covers.json    ← Cover types per product                │
│    fabrics.json   ← Fabric/color options per product       │
│                                                             │
│  Step 3: Smart API Routing                                 │
│    IF type = "sofa/chair/footstool/dog_bed" → Sofa API    │
│    IF type = "bed" → Bed API                               │
│                                                             │
│  Step 4: Build Correct Payload Format                      │
│    Sofa API: querySku = "alwsnufitsxppac"                  │
│    Bed API: component SKUs separately                       │
│                                                             │
│  Step 5: Cache Check (5-minute TTL)                        │
│                                                             │
│  Step 6: Call S&S API                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Sofa API          │   │   Bed API           │
│   (S&S Internal)    │   │   (S&S Internal)    │
├─────────────────────┤   ├─────────────────────┤
│ /ProductExtend/     │   │ /Category/          │
│  ChangeProductSize  │   │  ProductPrice       │
│                     │   │                     │
│ Returns:            │   │ Returns:            │
│ • Price             │   │ • Price             │
│ • Images (carousel) │   │ • (No images)       │
│ • Specs             │   │ • Specs             │
│ • Nested JSON       │   │ • Flat JSON         │
└─────────────────────┘   └─────────────────────┘
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (main.py)                               │
│  Step 7: Simplify Response                                  │
│    Extract: price, images, specs, fabric details            │
│                                                             │
│  Step 8: Cache Result                                       │
│                                                             │
│  Step 9: Return to Frontend                                 │
│    {                                                        │
│      "productName": "Alwinton Snuggler",                   │
│      "fabricName": "Sussex Plain - Pacific",               │
│      "price": "£1,409",                                    │
│      "imageUrls": [...],                                   │
│      "specs": [...]                                        │
│    }                                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (index.html)                      │
│  Step 10: Display Results                                   │
│    • Show price (big & bold)                                │
│    • Show images (carousel)                                 │
│    • Show specs (collapsible)                               │
│    • Show fabric details (swatch, tier, description)        │
│    • Add to history                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 **Key Innovation: Smart API Routing**

S&S uses **two completely different APIs** for pricing:

### **API #1: Sofa API**
**Used For:** Sofas, Chairs, Footstools, Dog Beds, Sofa Beds, Snugglers

**Endpoint:**
```
POST https://sofasandstuff.com/ProductExtend/ChangeProductSize
```

**Payload Format:**
```json
{
  "sku": "alw",
  "querySku": "alwsnufitsxppac"
}
```
*Combined SKU string: product + size + cover + fabric + color*

**Response:**
- Nested JSON structure
- Includes `HeroImages` array (product photos)
- Returns specs in `ProductSizeAttributes`

---

### **API #2: Bed API**
**Used For:** Beds only

**Endpoint:**
```
POST https://sofasandstuff.com/Category/ProductPrice
```

**Payload Format:**
```json
{
  "productsku": "arl",
  "sizesku": "skb",
  "coversku": "fit",
  "fabricSku": "sxp",
  "colourSku": "pac"
}
```
*Component SKU parts sent separately*

**Response:**
- Flat JSON structure
- NO images included
- Returns specs in `ProductSizeAttributes`

---

## 🧠 **The "Brain": Translation Dictionaries**

Our backend uses 4 JSON files to translate natural language → SKUs:

### **products.json**
Maps product keywords to product data:
```json
{
  "alwinton": {
    "sku": "alw",
    "type": "sofa",
    "url": "/alwinton?sku=alw3sefitttpbis",
    "full_name": "Alwinton 3 Seater Sofa",
    "price": "2776"
  }
}
```

### **sizes.json**
Maps size keywords to size SKUs (nested by product):
```json
{
  "alw": {
    "snuggler": "snu",
    "3 seater": "3se",
    "2 seater": "2se"
  }
}
```

### **covers.json**
Maps cover keywords to cover SKUs (nested by product):
```json
{
  "alw": {
    "fitted": "fit",
    "loose": "lse"
  }
}
```

### **fabrics.json**
Maps fabric keywords to fabric data (nested by product):
```json
{
  "alw": {
    "pacific": {
      "fabric_sku": "sxp",
      "color_sku": "pac",
      "fabric_name": "Sussex Plain",
      "color_name": "Pacific",
      "tier": "Essentials",
      "swatch_url": "https://..."
    }
  }
}
```

---

## 🔍 **Query Processing Flow**

### Example: "Alwinton snuggler pacific"

```
Step 1: Parse Query
├─ Query: "alwinton snuggler pacific"
└─ Lowercase: "alwinton snuggler pacific"

Step 2: Find Product
├─ Search products.json for "alwinton"
├─ Match: "alwinton" → {"sku": "alw", "type": "sofa"}
└─ Result: product_sku = "alw", product_type = "sofa"

Step 3: Find Size
├─ Load sizes.json["alw"] → {snuggler: "snu", ...}
├─ Search for "snuggler" in query
├─ Match: "snuggler" → "snu"
└─ Result: size_sku = "snu"

Step 4: Find Cover
├─ Load covers.json["alw"] → {fitted: "fit", loose: "lse"}
├─ No cover keyword in query
├─ Default: "fit"
└─ Result: cover_sku = "fit"

Step 5: Find Fabric
├─ Load fabrics.json["alw"] → {pacific: {...}, waves: {...}}
├─ Search for "pacific" in query
├─ Match: "pacific" → {fabric_sku: "sxp", color_sku: "pac"}
└─ Result: fabric_sku = "sxp", color_sku = "pac"

Step 6: Route to API
├─ Check product_type: "sofa"
├─ Route: Sofa API ✅
└─ Build payload: querySku = "alw" + "snu" + "fit" + "sxp" + "pac"

Step 7: Call API
├─ POST /ProductExtend/ChangeProductSize
├─ Payload: {sku: "alw", querySku: "alwsnufitsxppac"}
└─ Response: {success: true, result: {...}}

Step 8: Simplify & Cache
├─ Extract: price, images, specs
├─ Cache key: md5("alwsnufitsxppac")
├─ TTL: 5 minutes
└─ Return simplified JSON to frontend

Step 9: Display
└─ Frontend shows: £1,409 + images + specs
```

---

## 💾 **Complete Data Flow (Both Phases)**

### **Phase 1: Data Generation (Scraper Flow)**

```
┌─────────────────────────────────────────────────────────────┐
│  Developer (Local Machine)                                   │
│  $ python3 sku_discovery_tool.py                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Scraper Process (sku_discovery_tool.py)                    │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Scrape Category Pages                              │
│    GET /sofas, /chairs, /beds, /mattresses, etc.           │
│         ↓                                                    │
│    Extract: product names, SKUs, types                      │
│         ↓                                                    │
│    Result: products.json (base structure)                   │
│                                                              │
│  Step 2: Scrape Size Options                                │
│    For each product:                                         │
│      GET /product-page                                       │
│      Parse size modal HTML                                   │
│         ↓                                                    │
│    Result: sizes.json                                        │
│                                                              │
│  Step 3: Scrape Cover Options                               │
│    For each product:                                         │
│      Parse cover options from size modal                     │
│         ↓                                                    │
│    Result: covers.json                                       │
│                                                              │
│  Step 4: Call Fabric API                                    │
│    For each product:                                         │
│      POST /GetPDPFabrics                                     │
│      Payload: {sku: "alw", type: "sofa"}                   │
│         ↓                                                    │
│    Receive: Array of fabrics with colors, tiers, swatches   │
│         ↓                                                    │
│    Result: fabrics.json (23 MB)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Time: 20-30 minutes
                     │ Output: 4 JSON files
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Local Disk                                                  │
│  ✓ products.json  (71 KB)  - 210 products                  │
│  ✓ sizes.json     (20 KB)  - Size mappings                 │
│  ✓ covers.json    (4.8 KB) - Cover options                 │
│  ✓ fabrics.json   (23 MB)  - Fabric data                   │
└─────────────────────────────────────────────────────────────┘
```

### **Phase 2: Live Application (Runtime Flow)**

```
┌───────────────┐
│  4 JSON Files │ (From Phase 1)
│  Ready for    │
│  deployment   │
└───────┬───────┘
        │
        │ Deployed with main.py to GCF
        │
        ▼
┌───────────────┐
│  Google Cloud │
│  Functions    │
│  Container    │
│               │
│  /workspace/  │
│  ├─ main.py   │
│  ├─ products  │
│  ├─ sizes     │
│  ├─ covers    │
│  └─ fabrics   │
└───────┬───────┘
        │
        │ Container starts → Loads JSON into RAM
        │
        ▼
┌───────────────┐
│  main.py      │
│  (Backend)    │
│               │
│  In-Memory:   │
│  • PRODUCT_   │
│    SKU_MAP    │
│  • SIZE_      │
│    SKU_MAP    │
│  • COVERS_    │
│    SKU_MAP    │
│  • FABRIC_    │
│    SKU_MAP    │
│  • Cache      │
│    (5-min TTL)│
└───────┬───────┘
        │
        │ Called by frontend on each user query
        │
        ▼
┌───────────────┐
│  index.html   │
│  (Frontend)   │
└───────────────┘
```

---

## ⚡ **Performance Optimizations**

### 1. **Caching (5-Minute TTL)**
- First query: ~2 seconds (API call)
- Repeat query: ~200ms (cache hit)
- Reduces load on S&S APIs

### 2. **Fuzzy Matching**
- Fast regex first (exact matches)
- Slow fuzzy matching second (85% similarity)
- Handles typos and variations

### 3. **Smart Defaults**
- Footstools/Dog Beds: auto-select first size
- Covers: default to "fit" if not specified

### 4. **Retry Logic**
- 3 retries with exponential backoff
- Handles temporary S&S server issues

---

## 🔒 **Security & Privacy**

### ✅ **What We Have**
- HTTPS everywhere (GCF + GitHub Pages)
- No user data stored
- No authentication required
- CORS enabled for frontend access

### 🔐 **Optional Enhancements** (Not Implemented)
- API key authentication
- Rate limiting per user
- Request logging for analytics

---

## 💰 **Cost Breakdown**

| Component | Provider | Tier | Cost |
|-----------|----------|------|------|
| Frontend | GitHub Pages | Free | $0/month |
| Backend | Google Cloud Functions | Free Tier (2M requests/month) | $0/month |
| Data | JSON files (3 MB total) | Free | $0/month |
| **TOTAL** | | | **$0/month** ✅ |

**Typical Usage:**
- ~5,000-10,000 queries/month
- Well within free tier
- No credit card charges expected

---

## 🌍 **Browser Compatibility**

| Browser | Voice | Text | Notes |
|---------|-------|------|-------|
| Chrome (Desktop) | ✅ | ✅ | Full support |
| Safari (Mac) | ✅ | ✅ | Full support |
| Safari (iOS) | ✅ | ✅ | Full support |
| Chrome (Android) | ✅ | ✅ | Full support |
| Edge (Chromium) | ✅ | ✅ | Full support |
| Firefox | ❌ | ✅ | No webkitSpeechRecognition |
| Samsung Internet | ❌ | ✅ | No webkitSpeechRecognition |

---

## 🔄 **Update Process**

### When S&S Adds New Products:

```
1. Run Scraper Locally (20-30 min)
   └─ Generates new JSON files

2. Re-deploy Backend Only
   └─ Uploads new JSON files to GCF

3. Frontend Automatically Uses New Data
   └─ No frontend update needed!
```

**Frequency:** Quarterly or as needed

---

## 🎯 **Why This Architecture?**

### ✅ **Pros**
1. **Serverless** - No server to maintain
2. **Free** - GitHub Pages + GCF free tier
3. **Scalable** - Handles 1 or 1,000 users
4. **Simple** - Just HTML + Python
5. **Fast** - Caching reduces latency
6. **Reliable** - Retry logic handles errors

### ❌ **Alternative Architectures (Why We Didn't Use Them)**

**React + Direct API Calls**
- ❌ CORS issues (can't call S&S APIs from browser)
- ❌ Exposes API logic to users
- ❌ More complex to maintain

**Traditional Server (Node.js/Flask)**
- ❌ Costs money to host
- ❌ Need to manage server
- ❌ Requires scaling configuration

**Mobile App (iOS/Android)**
- ❌ Requires app store approval
- ❌ Two codebases to maintain
- ❌ More expensive to develop

---

## 🎉 **You're All Set!**

This architecture is:
- ✅ Production-ready
- ✅ Cost-effective ($0/month)
- ✅ Scalable
- ✅ Easy to maintain
- ✅ Well-documented

**Next:** Follow README.md to deploy! 🚀
