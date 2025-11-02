# 🔧 Technical Deep Dive: How Everything Works Together

**Last Updated:** November 2, 2025
**Purpose:** Complete technical explanation of the Sofas & Stuff Price Tool codebase

---

## Table of Contents

1. [How Google Cloud Functions Work](#1-how-google-cloud-functions-work)
2. [How main.py Executes](#2-how-mainpy-executes)
3. [How JSON Files Are Referenced](#3-how-json-files-are-referenced)
4. [Complete Query Flow: End-to-End](#4-complete-query-flow-end-to-end)
5. [The Smart 2-API Routing System](#5-the-smart-2-api-routing-system)
6. [Code Walkthrough: Line-by-Line](#6-code-walkthrough-line-by-line)
7. [Data Structures Deep Dive](#7-data-structures-deep-dive)
8. [Error Handling & Edge Cases](#8-error-handling--edge-cases)
9. [Performance & Optimization](#9-performance--optimization)

---

## 1. How Google Cloud Functions Work

### 1.1 What Happens When You Deploy

When you run this command:

```bash
gcloud functions deploy sofa-price-calculator \
  --entry-point http_entry_point \
  --runtime python312 \
  --region europe-west2
```

**Google Cloud does the following:**

#### Step 1: Packaging
```
Your Local Directory:
/Users/sameerm4/Desktop/SS-1/
├── main.py
├── requirements.txt
├── products.json
├── sizes.json
├── covers.json
└── fabrics.json

↓ [Zipped and uploaded]

Google Cloud Storage:
gs://your-bucket/sofa-price-calculator.zip
```

#### Step 2: Container Creation
Google creates a **Docker container** with:
- Python 3.12 runtime
- Your code files
- Installed dependencies

```
Container File System:
/workspace/
├── main.py                    ← Your backend code
├── requirements.txt
├── products.json              ← 71 KB
├── sizes.json                 ← 20 KB
├── covers.json                ← 4.8 KB
└── fabrics.json               ← 23 MB
```

#### Step 3: Dependency Installation
```bash
# Inside the container, Google runs:
pip install -r requirements.txt

# This installs:
- Flask
- functions-framework
- requests
- fuzzywuzzy
- python-Levenshtein
- urllib3
```

#### Step 4: URL Assignment
```
Your function gets a public URL:
https://europe-west2-sofaproject-476903.cloudfunctions.net/sofa-price-calculator

This URL is accessible worldwide, 24/7
```

---

### 1.2 Container Lifecycle

#### Cold Start (First Request or After Idle)
```
1. User makes HTTP request
   ↓
2. Google creates new container instance
   ↓
3. Python runtime starts
   ↓
4. main.py is loaded
   ↓
5. Lines 48-55 execute (load JSON files into RAM)
   ↓
6. Your function is ready to handle requests

Total time: 2-5 seconds
```

#### Warm Start (Subsequent Requests)
```
1. User makes HTTP request
   ↓
2. Existing container handles it
   ↓
3. JSON files already in RAM
   ↓
4. Function responds immediately

Total time: 200-500ms
```

#### Container Reuse
- Google keeps your container alive for ~15 minutes after last request
- Multiple requests can use the same container
- **This is why JSON files are only loaded once!**

---

## 2. How main.py Executes

### 2.1 Startup Phase (Happens Once Per Container)

Let's trace what happens when the container starts:

#### Lines 1-12: Imports
```python
import functions_framework  # ← Google Cloud Functions framework
import requests            # ← HTTP client for calling S&S APIs
import json               # ← JSON parsing
import os                 # ← File system operations
```

**What this does:**
- Loads all necessary Python libraries
- These are already installed from requirements.txt

---

#### Lines 14-24: HTTP Session Setup
```python
session = requests.Session()
retry_strategy = Retry(
    total=3,                # Retry failed requests 3 times
    backoff_factor=1,       # Wait 1s, 2s, 4s between retries
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
```

**What this does:**
- Creates a reusable HTTP client
- Configures automatic retries if S&S API is slow/down
- **This session object lives for the entire container lifetime**

---

#### Lines 26-29: Cache Setup
```python
response_cache = {}  # ← Empty dictionary to store responses
CACHE_TTL = 300     # ← 5 minutes in seconds
```

**What this does:**
- Creates an in-memory cache (just a Python dictionary)
- Sets cache expiration to 5 minutes
- **This cache is shared across all requests to this container**

---

#### Lines 36-46: JSON File Loader Function
```python
def load_json_file(filename):
    """Loads a JSON file from the same directory."""
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"[FATAL ERROR] {filename} not found.")
```

**How this works:**

1. `__file__` = `/workspace/main.py`
2. `os.path.dirname(__file__)` = `/workspace/`
3. `os.path.join("/workspace/", "products.json")` = `/workspace/products.json`
4. Opens the file and parses JSON into a Python dictionary
5. Returns the dictionary

---

#### Lines 48-55: **THE CRITICAL STARTUP** 🔑

```python
print("Loading translation dictionaries...")
PRODUCT_SKU_MAP = load_json_file("products.json")   # ← Loads 71 KB into RAM
SIZE_SKU_MAP = load_json_file("sizes.json")          # ← Loads 20 KB into RAM
COVERS_SKU_MAP = load_json_file("covers.json")       # ← Loads 4.8 KB into RAM
FABRIC_SKU_MAP = load_json_file("fabrics.json")      # ← Loads 23 MB into RAM
print("Dictionaries loaded successfully.")
```

**What's happening in RAM:**

```
Container Memory (512 MB total):
┌────────────────────────────────────────┐
│ Python Runtime:           ~50 MB       │
│ Libraries (Flask, etc):   ~30 MB       │
│                                        │
│ YOUR DATA (loaded once):               │
│   PRODUCT_SKU_MAP:        ~1 MB        │
│   SIZE_SKU_MAP:           ~50 KB       │
│   COVERS_SKU_MAP:         ~10 KB       │
│   FABRIC_SKU_MAP:         ~25 MB       │
│                                        │
│ Available for requests:   ~400 MB      │
└────────────────────────────────────────┘
```

**These dictionaries stay in RAM for the entire container lifetime!**

---

### 2.2 Per-Request Phase (Happens Every Time Someone Calls Your API)

#### Lines 363-383: The Entry Point

```python
@functions_framework.http  # ← This decorator tells GCF "this handles HTTP"
def http_entry_point(request):
    """Cloud Functions entry point that routes requests."""

    # Handle CORS preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # Handle the main /getPrice endpoint
    if request.path == '/getPrice' and request.method == 'POST':
        response_data, status_code = get_price_logic(request)  # ← Main logic
        response = jsonify(response_data)
        response.status_code = status_code
        return _add_cors_headers(response)

    # Handle the root path for a health check
    if request.path == '/' and request.method == 'GET':
        return _add_cors_headers(jsonify({"message": "Backend is ALIVE!"}))

    # Handle 404
    return _add_cors_headers(jsonify({"error": "Not Found"})), 404
```

**Request Routing:**

```
User Request → http_entry_point()
                      |
                      ├─ OPTIONS request? → Send CORS headers
                      |
                      ├─ POST /getPrice? → get_price_logic()
                      |
                      ├─ GET /? → Health check
                      |
                      └─ Anything else? → 404
```

---

## 3. How JSON Files Are Referenced

### 3.1 File System Structure in Google Cloud Functions

```
Google Cloud Container:
/workspace/
├── main.py              ← Your code runs from here
├── products.json        ← Same directory
├── sizes.json           ← Same directory
├── covers.json          ← Same directory
└── fabrics.json         ← Same directory

When main.py calls:
  load_json_file("products.json")

Python looks for:
  /workspace/products.json
```

---

### 3.2 How os.path.dirname(__file__) Works

```python
# When running locally:
__file__ = "/Users/sameerm4/Desktop/SS-1/main.py"
os.path.dirname(__file__) = "/Users/sameerm4/Desktop/SS-1"

# When running in Google Cloud Functions:
__file__ = "/workspace/main.py"
os.path.dirname(__file__) = "/workspace"

# Both work because JSON files are in the same directory!
```

---

### 3.3 Memory Layout After Loading

```python
# After line 51 executes:
PRODUCT_SKU_MAP = {
    "alwinton": {
        "sku": "alw",
        "type": "sofa",
        "full_name": "Alwinton 3 Seater Sofa",
        "url": "/alwinton?sku=alw3sefitttpbis",
        "price": "2776"
    },
    "snape": {
        "sku": "sna",
        "type": "chair",
        ...
    },
    # ... 208 more products
}

# This entire dictionary is now in RAM
# Accessible to ALL requests handled by this container
```

---

## 4. Complete Query Flow: End-to-End

Let's trace a real query: **"alwinton snuggler pacific"**

### 4.1 Frontend (index.html)

**User Action:**
```
1. User taps microphone button
2. Says "alwinton snuggler pacific"
3. Browser captures speech → text
```

**Code (index.html line ~188-220):**
```javascript
const BACKEND_API_URL = 'https://europe-west2-PROJECT.cloudfunctions.net/sofa-price-calculator/getPrice';

async function searchPrice() {
    const query = document.getElementById('searchInput').value;

    const response = await fetch(BACKEND_API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query})
    });

    const data = await response.json();
    displayResults(data);
}
```

**HTTP Request Sent:**
```http
POST /getPrice HTTP/1.1
Host: europe-west2-PROJECT.cloudfunctions.net
Content-Type: application/json

{
  "query": "alwinton snuggler pacific"
}
```

---

### 4.2 Backend (main.py) - Translation Process

#### Step 1: Entry Point (Line 364-376)

```python
def http_entry_point(request):
    if request.path == '/getPrice' and request.method == 'POST':
        response_data, status_code = get_price_logic(request)  # ← Goes here
        ...
```

#### Step 2: Parse Request (Line 144-154)

```python
def get_price_logic(request):
    data = request.get_json()           # ← {"query": "alwinton snuggler pacific"}
    query = data.get('query', '').lower()  # ← "alwinton snuggler pacific"

    print(f"--- New Query: '{query}' ---")
```

**Console Output:**
```
--- New Query: 'alwinton snuggler pacific' ---
```

---

#### Step 3: Find Product (Line 166-180)

```python
# Find Product (and its SKU and TYPE)
product_matches = find_best_matches(query, PRODUCT_SKU_MAP)
```

**What find_best_matches() does:**

```python
def find_best_matches(query, mapping, fuzziness=85):
    # query = "alwinton snuggler pacific"
    # mapping = PRODUCT_SKU_MAP (the entire dictionary)

    matches = []

    # Try regex first (fast)
    for keyword, value in mapping.items():
        # keyword = "alwinton"
        if re.search(r'\balwinton\b', query, re.IGNORECASE):
            # MATCH! "alwinton" found in query
            confidence = 100 + len("alwinton")  # 108
            matches.append(("alwinton", value, 108))

    return matches
```

**Result:**
```python
product_matches = [
    ("alwinton", {
        "sku": "alw",
        "type": "sofa",
        "full_name": "Alwinton 3 Seater Sofa"
    }, 108)
]

product_sku = "alw"
product_type = "sofa"
```

**Console Output:**
```
  [Match] Product: 'alwinton' -> SKU: 'alw', Type: 'sofa'
```

---

#### Step 4: Find Size (Line 183-195)

```python
# Find Size (based on the product_sku)
product_size_map = SIZE_SKU_MAP.get(product_sku, {})
# product_size_map = SIZE_SKU_MAP["alw"] = {
#     "snuggler": "snu",
#     "2 seater": "2se",
#     "3 seater": "3se",
#     "4 seater": "4se"
# }

size_matches = find_best_matches(query, product_size_map)
# Searches "alwinton snuggler pacific" for "snuggler", "2 seater", etc.
# Finds "snuggler"!

size_sku = "snu"
```

**Console Output:**
```
  [Match] Size: 'snuggler' -> SKU: 'snu'
```

---

#### Step 5: Find Cover (Line 198-209)

```python
# Find Cover (based on the product_sku)
product_cover_map = COVERS_SKU_MAP.get(product_sku, {})
# product_cover_map = COVERS_SKU_MAP["alw"] = {
#     "fitted": "fit",
#     "loose": "lse"
# }

cover_matches = find_best_matches(query, product_cover_map)
# Searches "alwinton snuggler pacific" for "fitted" or "loose"
# No match found

# Default to "fit"
cover_sku = "fit"
```

**Console Output:**
```
  [Info] No cover specified, defaulting to: 'fit'
```

---

#### Step 6: Find Fabric (Line 212-231)

```python
# Find Fabric (Search *only* within the product's available fabrics)
product_fabric_map = FABRIC_SKU_MAP.get(product_sku, {})
# product_fabric_map = FABRIC_SKU_MAP["alw"] = {
#     "pacific": {
#         "fabric_sku": "sxp",
#         "color_sku": "pac",
#         "fabric_name": "Sussex Plain",
#         "color_name": "Pacific",
#         "tier": "Essentials",
#         "swatch_url": "https://..."
#     },
#     "waves": {...},
#     "biscuit": {...}
# }

fabric_matches = find_best_matches(query, product_fabric_map)
# Searches "alwinton snuggler pacific" for fabric keywords
# Finds "pacific"!

fabric_match_data = {
    "fabric_sku": "sxp",
    "color_sku": "pac",
    "fabric_name": "Sussex Plain",
    "color_name": "Pacific",
    "tier": "Essentials",
    "swatch_url": "https://sofasandstuff.com/..."
}
```

**Console Output:**
```
  [Match] Fabric: 'pacific' -> SKU: 'sxp', Color: 'pac'
```

---

#### Step 7: Check Cache (Line 239-242)

```python
cache_key = get_cache_key(product_sku, size_sku, cover_sku,
                          fabric_match_data['fabric_sku'],
                          fabric_match_data['color_sku'])
# cache_key = md5("alwsnufitsxppac").hexdigest() = "a3f2..."

cached_response = get_from_cache(cache_key)
# First time? Returns None
# Repeat query within 5 min? Returns cached result
```

**Console Output (if cache miss):**
```
  [Cache MISS] for a3f2...
```

---

#### Step 8: Route to Correct API (Line 257-271)

```python
# Check product type: "sofa"
if product_type in ["sofa", "chair", "footstool", "dog_bed", "sofa_bed", "snuggler", "mattress"]:
    api_url = SOFA_API_URL
    # "https://sofasandstuff.com/ProductExtend/ChangeProductSize"

    # Build combined SKU
    query_sku = f"{product_sku}{size_sku}{cover_sku}{fabric_match_data['fabric_sku']}{fabric_match_data['color_sku']}"
    # query_sku = "alw" + "snu" + "fit" + "sxp" + "pac" = "alwsnufitsxppac"

    payload = {
        'sku': 'alw',
        'querySku': 'alwsnufitsxppac'
    }
```

**Console Output:**
```
  [API Call] Calling: https://sofasandstuff.com/ProductExtend/ChangeProductSize
             with payload: {'sku': 'alw', 'querySku': 'alwsnufitsxppac'}
```

---

#### Step 9: Call S&S API (Line 290-292)

```python
response = session.post(api_url, data=payload, headers=headers, timeout=10)
response.raise_for_status()  # Raises exception if 4xx/5xx error
price_data = response.json()
```

**HTTP Request to S&S:**
```http
POST /ProductExtend/ChangeProductSize HTTP/1.1
Host: sofasandstuff.com
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

sku=alw&querySku=alwsnufitsxppac
```

**S&S Response:**
```json
{
  "success": true,
  "result": {
    "ProductSkuRecord": {
      "ProductName": "Alwinton",
      "SizeName": "Snuggler",
      "FabricName": "Sussex Plain",
      "ColourName": "Pacific",
      "PriceText": "£1,409",
      "OldPriceText": null,
      "ProductSizeAttributes": [
        {"Label": "Frame", "Value": "Beech hardwood"},
        {"Label": "Cushions", "Value": "Fibre"}
      ]
    },
    "HeroImages": [
      {"ImageUrl": "assets/images/products/alw/sxp/pac/hero1.jpg"}
    ]
  }
}
```

---

#### Step 10: Parse & Simplify Response (Line 296-346)

```python
if price_data.get("success"):
    record = price_data.get("result", {}).get("ProductSkuRecord", {})
    images = price_data.get("result", {}).get('HeroImages', [])

    # Process images
    image_urls = []
    for img in images:
        img_url = img.get('ImageUrl', '').replace("\\", "/")
        # "assets/images/products/alw/sxp/pac/hero1.jpg"

        # URL encode and prepend base URL
        path_parts = img_url.split('/')
        encoded_parts = [quote(part, safe='') for part in path_parts]
        encoded_path = '/'.join(encoded_parts)
        image_urls.append("https://sofasandstuff.com/" + encoded_path)

    simplified_response = {
        "productName": "Alwinton Snuggler",
        "fabricName": "Sussex Plain - Pacific",
        "price": "£1,409",
        "oldPrice": None,
        "imageUrls": ["https://sofasandstuff.com/assets/images/products/alw/sxp/pac/hero1.jpg"],
        "specs": [
            {"Label": "Frame", "Value": "Beech hardwood"},
            {"Label": "Cushions", "Value": "Fibre"}
        ],
        "fabricDetails": {
            "tier": "Essentials",
            "description": "A robust plain fabric...",
            "swatchUrl": "https://..."
        }
    }
```

---

#### Step 11: Cache & Return (Line 349-350)

```python
set_to_cache(cache_key, simplified_response)
# Stores in response_cache["a3f2..."] = (current_time, simplified_response)

return simplified_response, 200
```

---

### 4.3 Backend Response to Frontend

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *

{
  "productName": "Alwinton Snuggler",
  "fabricName": "Sussex Plain - Pacific",
  "price": "£1,409",
  "oldPrice": null,
  "imageUrls": ["https://sofasandstuff.com/assets/images/products/alw/sxp/pac/hero1.jpg"],
  "specs": [
    {"Label": "Frame", "Value": "Beech hardwood"},
    {"Label": "Cushions", "Value": "Fibre"}
  ],
  "fabricDetails": {
    "tier": "Essentials",
    "description": "A robust plain fabric...",
    "swatchUrl": "https://..."
  }
}
```

---

### 4.4 Frontend Displays Result

**Code (index.html line ~250-320):**
```javascript
function displayResults(data) {
    // Show price
    document.getElementById('price').textContent = data.price;

    // Show product name
    document.getElementById('productName').textContent = data.productName;

    // Show fabric
    document.getElementById('fabricName').textContent = data.fabricName;

    // Show images in carousel
    data.imageUrls.forEach(url => {
        const img = document.createElement('img');
        img.src = url;
        carousel.appendChild(img);
    });

    // Show specs
    data.specs.forEach(spec => {
        const row = `<tr><td>${spec.Label}</td><td>${spec.Value}</td></tr>`;
        specsTable.innerHTML += row;
    });
}
```

**User sees:**
```
┌─────────────────────────────────────┐
│  Alwinton Snuggler                  │
│  Sussex Plain - Pacific             │
│                                     │
│  £1,409                             │
│                                     │
│  [Product Image]                    │
│                                     │
│  Specifications:                    │
│  Frame: Beech hardwood              │
│  Cushions: Fibre                    │
│                                     │
│  Fabric: Essentials Tier            │
└─────────────────────────────────────┘
```

---

## 5. The Smart 2-API Routing System

### 5.1 Why Two APIs?

Sofas & Stuff uses **completely different API endpoints** for different product types:

| Product Type | API Endpoint | Why? |
|--------------|--------------|------|
| Sofas, Chairs, Footstools, Dog Beds, Snugglers, Mattresses | `/ProductExtend/ChangeProductSize` | Product configurator page (changes options dynamically) |
| Beds | `/Category/ProductPrice` | Category/listing page (simpler payload) |

### 5.2 Key Differences

#### Sofa API
```python
# Payload
{
    'sku': 'alw',
    'querySku': 'alwsnufitsxppac'  # ← Combined string
}

# Response
{
    "success": true,
    "result": {
        "ProductSkuRecord": {...},  # ← Nested
        "HeroImages": [...]         # ← Images included
    }
}
```

#### Bed API
```python
# Payload
{
    'productsku': 'arl',
    'sizesku': 'skb',
    'coversku': 'fit',
    'fabricSku': 'sxp',
    'colourSku': 'pac'  # ← Separate components
}

# Response
{
    "ProductName": "...",
    "PriceText": "..."  # ← Flat structure, no images
}
```

### 5.3 Routing Logic (Line 257-285)

```python
if product_type in ["sofa", "chair", "footstool", "dog_bed", "sofa_bed", "snuggler", "mattress"]:
    api_url = SOFA_API_URL
    query_sku = f"{product_sku}{size_sku}{cover_sku}{fabric_match_data['fabric_sku']}{fabric_match_data['color_sku']}"
    payload = {'sku': product_sku, 'querySku': query_sku}

elif product_type == "bed":
    api_url = BED_API_URL
    payload = {
        'productsku': product_sku,
        'sizesku': size_sku,
        'coversku': cover_sku,
        'fabricSku': fabric_match_data['fabric_sku'],
        'colourSku': fabric_match_data['color_sku']
    }
```

---

## 6. Code Walkthrough: Line-by-Line

### Key Functions Explained

#### find_best_matches() (Line 77-108)

**Purpose:** Find all keywords in a query using regex and fuzzy matching

```python
def find_best_matches(query, mapping, fuzziness=85):
    """
    query = "alwinton snuggler pacific"
    mapping = {"alwinton": {...}, "snape": {...}}
    """
    matches = []

    # Step 1: Try exact regex matching (fast)
    for keyword, value in mapping.items():
        # \b = word boundary (matches "alwinton" but not "alwintonia")
        if re.search(r'\b' + re.escape(keyword) + r'\b', query, re.IGNORECASE):
            confidence = 100 + len(keyword)  # Longer keywords get higher score
            matches.append((keyword, value, confidence))

    if matches:
        matches.sort(key=lambda x: x[2], reverse=True)  # Sort by confidence
        return matches

    # Step 2: If no regex match, try fuzzy matching (slow but handles typos)
    best_fuzzy_match = process.extractOne(query, mapping.keys(), score_cutoff=85)
    # Example: "alwington" would match "alwinton" with score 90

    if best_fuzzy_match:
        keyword, score = best_fuzzy_match[0], best_fuzzy_match[1]
        value = mapping[keyword]
        matches.append((keyword, value, score))

    return matches
```

**Examples:**
```python
# Exact match
find_best_matches("alwinton snuggler pacific", PRODUCT_SKU_MAP)
→ [("alwinton", {...}, 108)]

# Fuzzy match (typo)
find_best_matches("alwington snugler pacfic", PRODUCT_SKU_MAP)
→ [("alwinton", {...}, 90)]  # Close enough!

# No match
find_best_matches("blahblah", PRODUCT_SKU_MAP)
→ []
```

---

#### get_cache_key() (Line 112-114)

**Purpose:** Create unique cache key for a specific product configuration

```python
def get_cache_key(product_sku, size_sku, cover_sku, fabric_sku, color_sku):
    return md5(f"{product_sku}{size_sku}{cover_sku}{fabric_sku}{color_sku}".encode()).hexdigest()

# Example:
get_cache_key("alw", "snu", "fit", "sxp", "pac")
→ "a3f2e1d8c5b4a7e9f6d3c2b1a0e8f7d6"

# Same configuration = same cache key
# Different configuration = different cache key
```

---

#### get_from_cache() (Line 116-124)

**Purpose:** Retrieve cached response if still valid

```python
def get_from_cache(cache_key):
    if cache_key in response_cache:
        cached_time, cached_data = response_cache[cache_key]

        # Check if cache is still fresh (< 5 minutes old)
        if (time.time() - cached_time) < CACHE_TTL:
            return cached_data  # Cache HIT

    return None  # Cache MISS
```

**Example Timeline:**
```
10:00:00 - User queries "alwinton snuggler pacific"
           → API call made
           → Response cached with timestamp 10:00:00

10:02:00 - Same query again
           → time.time() = 10:02:00
           → cached_time = 10:00:00
           → Difference = 120 seconds < 300 seconds
           → Return cached response ✅

10:06:00 - Same query again
           → time.time() = 10:06:00
           → cached_time = 10:00:00
           → Difference = 360 seconds > 300 seconds
           → Cache expired, make new API call ❌
```

---

## 7. Data Structures Deep Dive

### 7.1 products.json Structure

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

**Why this structure?**
- **Key = keyword:** Fast lookup using `PRODUCT_SKU_MAP.get("alwinton")`
- **sku:** Needed for API calls
- **type:** Determines which API to use (sofa vs bed)
- **url:** For reference (not used by backend)
- **full_name:** For display and error messages
- **price:** Base price (might be outdated, we get real-time from API)

---

### 7.2 sizes.json Structure

```json
{
  "alw": {
    "snuggler": "snu",
    "2 seater": "2se",
    "3 seater": "3se",
    "4 seater": "4se"
  },
  "sna": {
    "chair": "cha"
  }
}
```

**Why nested by product SKU?**
- Different products have different sizes
- "snuggler" only exists for sofas, not chairs
- **O(1) lookup:** `SIZE_SKU_MAP["alw"]["snuggler"]` → `"snu"`

---

### 7.3 covers.json Structure

```json
{
  "alw": {
    "fitted": "fit",
    "loose": "lse"
  },
  "pts": {
    "off": "off"
  }
}
```

**Special Cases:**
- Most sofas/chairs have "fitted" and "loose"
- Mattresses always use "off" (no cover option)
- Beds have various cover types

---

### 7.4 fabrics.json Structure (Most Complex!)

```json
{
  "alw": {
    "pacific": {
      "fabric_sku": "sxp",
      "color_sku": "pac",
      "fabric_name": "Sussex Plain",
      "color_name": "Pacific",
      "tier": "Essentials",
      "swatch_url": "https://sofasandstuff.com/...",
      "desc": "A robust plain fabric..."
    },
    "waves": {
      "fabric_sku": "sxp",
      "color_sku": "wav",
      ...
    }
  }
}
```

**Why so detailed?**
- **fabric_sku + color_sku:** Needed for API call
- **fabric_name + color_name:** Display to user
- **tier:** Pricing tier (Essentials, Premium, Luxury)
- **swatch_url:** Show fabric image to user
- **desc:** Fabric description for user

**Size:** 23 MB because:
- 95 products
- Each has 50-200 fabric/color combinations
- Each combination has full metadata

---

## 8. Error Handling & Edge Cases

### 8.1 Product Not Found

```python
product_matches = find_best_matches(query, PRODUCT_SKU_MAP)
if not product_matches:
    return {"error": "Product not found. Try 'Alwinton' or 'Dog Bed'."}, 400
```

**Example:**
```
Query: "blahblah"
Response: {"error": "Product not found. Try 'Alwinton' or 'Dog Bed'."}
```

---

### 8.2 Ambiguous Fabric

```python
fabric_matches = find_best_matches(query, product_fabric_map)

if len(fabric_matches) > 1 and fabric_matches[0][2] < 100:
    if fabric_matches[0][2] - fabric_matches[1][2] < 10:
        suggestions = [m[0] for m in fabric_matches[:3]]
        return {"error": f"Ambiguous fabric. Did you mean: {', '.join(suggestions)}?"}, 400
```

**Example:**
```
Query: "alwinton snuggler blue"
Matches: "light blue" (score 85), "dark blue" (score 83), "sky blue" (score 82)
Response: {"error": "Ambiguous fabric. Did you mean: light blue, dark blue, sky blue?"}
```

---

### 8.3 API Timeout

```python
try:
    response = session.post(api_url, data=payload, headers=headers, timeout=10)
except requests.exceptions.Timeout:
    return {"error": "Request timed out. The S&S server may be slow."}, 504
```

---

### 8.4 Invalid SKU Combination

```python
except requests.exceptions.RequestException as e:
    return {"error": f"API request failed. Built an invalid SKU? (Query: {query})"}, 502
```

**Example:**
```
Query: "alwinton snuggler pacific"
Built SKU: "alwsnufitsxppac"
S&S API returns 404
Response: {"error": "API request failed. Built an invalid SKU? (Query: alwinton snuggler pacific)"}
```

---

## 9. Performance & Optimization

### 9.1 Caching Strategy

```
First Query:
  User → Backend → S&S API (2 seconds)
                 ↓
              Cache for 5 min

Repeat Query within 5 min:
  User → Backend → Cache (200ms) ✅ 10x faster!

Repeat Query after 5 min:
  User → Backend → S&S API (2 seconds)
                 ↓
              Cache refreshed
```

**Why 5 minutes?**
- Prices don't change often
- Reduces load on S&S servers
- Fast responses for repeat queries

---

### 9.2 Fuzzy Matching Performance

```python
# Fast path (regex) - O(n) where n = number of keywords
for keyword, value in mapping.items():
    if re.search(r'\b' + re.escape(keyword) + r'\b', query, re.IGNORECASE):
        matches.append(...)

# Slow path (fuzzy matching) - O(n*m) where m = query length
# Only runs if regex finds nothing
best_fuzzy_match = process.extractOne(query, mapping.keys(), score_cutoff=85)
```

**Performance:**
- Regex: ~1ms for 210 products
- Fuzzy: ~50ms for 210 products
- **Optimization:** Try regex first, only use fuzzy if needed

---

### 9.3 Memory Usage

```
Total Memory: 512 MB (configured in deployment)

Breakdown:
  - Python runtime: ~50 MB
  - Libraries: ~30 MB
  - JSON data: ~26 MB
  - Cache (max): ~10 MB (stores ~50 responses)
  - Request processing: ~50 MB
  - Available: ~346 MB

Why 512MB is enough:
  - JSON files loaded once
  - Cache has TTL (prevents growth)
  - Each request uses minimal memory
```

---

### 9.4 Cold Start Optimization

```
Cold Start (container creation):
  1. Create container: ~500ms
  2. Load Python runtime: ~1000ms
  3. Install dependencies: ~0ms (pre-installed)
  4. Load main.py: ~100ms
  5. Load JSON files: ~500ms
  Total: ~2-3 seconds

Optimization:
  - Use Python 3.12 (faster startup)
  - Keep JSON files small (✓ only 26 MB)
  - Minimize dependencies (✓ only 6 packages)
```

---

## Summary

### Complete Data Flow

```
1. User speaks/types query
   ↓
2. Frontend sends POST /getPrice
   ↓
3. Backend receives request → http_entry_point()
   ↓
4. Parse query → get_price_logic()
   ↓
5. Look up in PRODUCT_SKU_MAP (loaded in RAM)
   ↓
6. Look up in SIZE_SKU_MAP (loaded in RAM)
   ↓
7. Look up in COVERS_SKU_MAP (loaded in RAM)
   ↓
8. Look up in FABRIC_SKU_MAP (loaded in RAM)
   ↓
9. Check cache (in RAM)
   ↓
10. Build API payload
   ↓
11. Call S&S API
   ↓
12. Parse response
   ↓
13. Cache response (in RAM)
   ↓
14. Return simplified JSON
   ↓
15. Frontend displays price + images + specs
```

### Key Takeaways

1. **JSON files are loaded once** when container starts
2. **All lookups happen in RAM** (dictionaries, not database)
3. **Caching reduces API calls** by 90%+
4. **Smart routing** handles different product types automatically
5. **Fuzzy matching** handles typos and variations
6. **Error handling** provides helpful messages

---

**This system is designed to be:**
- ✅ Fast (200-500ms response time)
- ✅ Reliable (retries, error handling)
- ✅ Cost-effective ($0/month on free tier)
- ✅ Maintainable (re-scrape quarterly)
- ✅ Scalable (handles 1 or 1000 users)
