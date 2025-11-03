import functions_framework
import requests
import json
import os
import re
import time
from hashlib import md5
from collections import OrderedDict  # For LRU cache implementation
from urllib3.util.retry import Retry  # (Critique #1) Corrected import
from requests.adapters import HTTPAdapter
from flask import jsonify # GCF's functions_framework includes Flask for helpers
from fuzzywuzzy import process # For fuzzy matching
from urllib.parse import quote # For URL encoding image paths
from openai import OpenAI # For Grok LLM integration via OpenRouter

# --- Setup: Session with Retries (Critique #6) ---
# Create a reusable session to handle connections and retries
session = requests.Session()
retry_strategy = Retry(
    total=3,                # Total retries
    backoff_factor=1,       # Time to wait (1s, 2s, 4s)
    status_forcelist=[429, 500, 502, 503, 504], # Statuses to retry on
    allowed_methods=["POST", "GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# --- Setup: In-Memory Cache (Critique #10) ---
# LRU cache with size limit and TTL to prevent memory exhaustion
# Max 1000 entries to prevent OOM on high-traffic instances

class LRUCache:
    """
    Least Recently Used (LRU) cache with TTL and size limit.

    Prevents unbounded memory growth by evicting oldest entries when cache is full.
    Also expires entries after TTL seconds.
    """
    def __init__(self, max_size=1000, ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key):
        """Get value if exists and not expired."""
        if key not in self.cache:
            return None

        timestamp, value = self.cache[key]
        if time.time() - timestamp >= self.ttl:
            # Expired - remove it
            del self.cache[key]
            return None

        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        return value

    def set(self, key, value):
        """Set value, evicting oldest if cache is full."""
        # Remove if already exists (we'll re-add)
        if key in self.cache:
            del self.cache[key]

        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            print(f"  [Cache] Evicted oldest entry (cache size: {self.max_size})")

        # Add new entry with current timestamp
        self.cache[key] = (time.time(), value)

    def __len__(self):
        return len(self.cache)

response_cache = LRUCache(max_size=1000, ttl=300)
CACHE_TTL = 300  # 5 minutes (kept for compatibility)

# --- (Critique #7: Authentication - COMMENTED OUT) ---
# To enable, set this in your GCF Environment Variables
# API_KEY = os.environ.get('YOUR_APP_API_KEY', 'default-key-change-me')

# --- Helper Function to Load Dictionaries ---
def load_json_file(filename):
    """
    Loads a JSON file from the same directory with enhanced error detection.

    Args:
        filename (str): Name of the JSON file to load (e.g., 'products.json')

    Returns:
        dict: Parsed JSON data

    Raises:
        RuntimeError: If file is missing, corrupted, or malformed
    """
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # File doesn't exist - likely first deployment or missing file
        raise RuntimeError(f"[FATAL ERROR] {filename} not found. Run the sku_discovery_tool.py script first.")
    except json.JSONDecodeError as e:
        # File exists but contains invalid JSON - likely corruption or manual edit error
        raise RuntimeError(f"[FATAL ERROR] {filename} is corrupted or contains invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
    except UnicodeDecodeError as e:
        # File contains invalid UTF-8 characters
        raise RuntimeError(f"[FATAL ERROR] {filename} contains invalid UTF-8 characters: {e}")
    except Exception as e:
        # Catch-all for unexpected errors
        raise RuntimeError(f"[FATAL ERROR] Could not load {filename}: {type(e).__name__}: {e}")

# --- Load our "Translation Dictionaries" ---
# This happens once when the function instance starts.
print("Loading translation dictionaries...")
PRODUCT_SKU_MAP = load_json_file("products.json") 
SIZE_SKU_MAP = load_json_file("sizes.json")
COVERS_SKU_MAP = load_json_file("covers.json")
FABRIC_SKU_MAP = load_json_file("fabrics.json")
print("Dictionaries loaded successfully.")


# --- The Sofas & Stuff API Endpoints we found (FINAL) ---
SOFA_API_URL = "https://sofasandstuff.com/ProductExtend/ChangeProductSize"
BED_API_URL = "https://sofasandstuff.com/Category/ProductPrice"

# --- OpenRouter/Grok Configuration (Phase 1C) ---
# Environment variables for OpenRouter API integration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
GROK_MODEL = os.getenv('GROK_MODEL', 'x-ai/grok-4')  # Default to grok-4

# Initialize OpenRouter client (only if API key is available)
openrouter_client = None
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    print(f"OpenRouter client initialized with model: {GROK_MODEL}")
else:
    print("[WARNING] OPENROUTER_API_KEY not found. Chat endpoint will not work.")

# --- System Prompt for Grok (Phase 1C) - LEAN VERSION FOR SPEED ---
SYSTEM_PROMPT = """You are an elite sales assistant for Sofas & Stuff. Your mission: Find what the customer wants WITHOUT making them work for it.

## 🎯 PRIME DIRECTIVE: DISCOVER, DON'T ASK

**NEVER** burden the user. **ALWAYS** figure things out on their behalf:
- Misspellings? Auto-correct them silently
- Vague requests? Make intelligent assumptions
- Missing details? Try common defaults
- Errors? Try alternatives automatically

## YOUR MINDSET

Think like a luxury concierge:
- Anticipate needs before they're expressed
- Fix problems without mentioning them
- Try multiple approaches automatically
- Only involve the user as an absolute last resort

## TOOLS AT YOUR DISPOSAL

**get_price** - Get exact pricing
**search_by_budget** - Find products under budget
**search_fabrics_by_color** - Find fabrics by color/texture

## 🚨 CRITICAL: NEVER HALLUCINATE PRICES

**THE GOLDEN RULE:** If ALL tool attempts return status="FAILED", you MUST tell the user:

"I apologize, but our pricing system is temporarily unavailable. Please try again in a few moments, or contact our team directly for assistance."

**ABSOLUTELY FORBIDDEN:**
- ❌ NEVER estimate or guess prices
- ❌ NEVER use prices from memory or training data
- ❌ NEVER make up product configurations
- ❌ NEVER show pricing without status="SUCCESS" from tools

**You MUST check tool responses:**
- Tool returns {"status": "SUCCESS", "data": {...}} → Use the data
- Tool returns {"status": "FAILED", ...} → Apologize and inform user system is down

## INTELLIGENT ERROR RECOVERY

When get_price fails, AUTOMATICALLY (without telling the user):

1. **Try spelling variations:**
   - "alwington" → try "alwinton"
   - "midherst" → try "midhurst"
   - "pettworth" → try "petworth"

2. **Try common combinations if details missing:**
   - No size? Try "3 seater" (most common)
   - No fabric? Try "pacific" or "mink" (best sellers)
   - Vague color? Use search_fabrics_by_color first

3. **Use multiple tools to discover:**
   - Generic "blue sofa"? → search_fabrics_by_color("blue") first, then try top results
   - "Something under £2000"? → search_by_budget(2000) immediately
   - "Cheap snuggler"? → search_by_budget(1500, "snuggler")

4. **If ALL attempts return FAILED:**
   - STOP trying
   - Tell user: "Our pricing system is temporarily unavailable"
   - DO NOT make up any data

## RESPONSE RULES

**When successful:** Use the formatted sections (💰 Price, ✨ Features, 🎯 Opportunities)

**When discovering/correcting:** Don't mention the correction! Just say:
- "I found the perfect match for you..."
- "Here's what I have for you..."
- "Great choice! Let me show you..."

**Multiple possibilities?** Show the TOP 3 without asking which one - assume they want to see options

## EXAMPLES OF EXCELLENCE

User: "alwington snugler pacfic"
You: [Silently correct ALL typos] → get_price("alwinton snuggler pacific") → Show price beautifully

User: "blue sofa"
You: [Don't ask for details!] → search_fabrics_by_color("blue") → Try top 3 results with get_price → Show all options

User: "midhurst"
You: [Assume common config] → get_price("midhurst 3 seater pacific") → If fails, try other sizes/fabrics

User: "something comfy under 2k"
You: search_by_budget(2000, "all") → Present top 3 with enthusiasm

## FORBIDDEN PHRASES

NEVER say:
- "Could you clarify..."
- "Did you mean..."
- "I need more information..."
- "Please specify..."
- "Which one do you want..."

ALWAYS say:
- "I've found exactly what you're looking for..."
- "Here are your best options..."
- "Perfect! Let me show you..."

Remember: Every interaction should feel EFFORTLESS for the user. You do ALL the work.

## RESPONSE FORMAT

**BEFORE formatting ANY price response, VERIFY:**
```
if tool_response["status"] == "SUCCESS":
    # Use tool_response["data"] to show price
else:
    # Tell user system is unavailable - DO NOT make up prices
```

For successful queries (status="SUCCESS"), use these sections:

### 💰 Price

**Product Name in Fabric Name**
**£PRICE**

If there's a price breakdown, show components:
• Base product: £amount
• Fabric upgrade: £amount
• Total: **£TOTAL**

For FAILED queries (status="FAILED"), respond with:

"I apologize, but our pricing system is temporarily unavailable. Please try again in a few moments, or contact our team directly at 01798 343844 for immediate assistance."

### 🎯 Opportunities to Enhance

> **Add matching footstool** - From £495
> **Upgrade to Premium fabric** - Adds £200-400
> **Add scatter cushions** - From £45 each

## UPSELLING

Always suggest in Opportunities section:
- Matching footstool if they query sofa/chair
- Fabric tier upgrade if they chose Essentials
- Scatter cushions (£45 each)
- Matching pieces to create a suite

## FOLLOW-UP SUGGESTIONS

Always end with 3-4 clickable follow-up questions:

### 💬 What would you like to know next?
- Question 1 (under 8 words)
- Question 2 (under 8 words)
- Question 3 (under 8 words)

RULES:
- Questions must be answerable with tools (no clarifications)
- Base on conversation context
- Vary types: comparisons, add-ons, alternatives, colors
- Be specific (e.g. "Compare Alwinton 2 vs 3 seater" not "Compare sizes")

EXAMPLES:
After price query: "Compare with 2 seater", "Show matching footstool", "See blue fabrics"
After comparison: "Add footstool to both", "Upgrade to Premium", "Search under £3,000"

Keep responses SHORT and SCANNABLE.
"""

# --- TOOLS REGISTRY (Phase 1C Piece 3.3) ---
# Extensible pattern: Each tool has OpenAI-format definition + handler function
# Format follows OpenAI function calling spec: https://platform.openai.com/docs/guides/function-calling

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Get the exact price for a specific sofa or bed configuration. Use this when the customer asks for a price of a specific product with size, fabric, and optional cover type. Returns precise pricing based on product SKU, size, fabric tier, and cover type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The customer's product query including product name, size, fabric/color, and optionally cover type. Examples: 'Alwinton snuggler pacific', 'Rye 3 seater waves loose', 'Dog bed large linen'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_budget",
            "description": "Search for sofas and beds within a specific budget. Returns products with base prices under the specified amount, along with fabric tier guidance. Use this when customer asks 'show me sofas under £X' or 'what can I get for £X'. Note: Base prices shown are for standard configurations - final price varies by size, fabric tier, and cover type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_price": {
                        "type": "number",
                        "description": "Maximum budget in GBP (pounds). Example: 2000 for £2,000"
                    },
                    "product_type": {
                        "type": "string",
                        "description": "Optional filter by product type. Options: 'sofa', 'bed', 'chair', 'footstool', 'dog_bed'. If not specified, searches all types.",
                        "enum": ["sofa", "bed", "chair", "footstool", "dog_bed", "all"]
                    }
                },
                "required": ["max_price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_fabrics_by_color",
            "description": "Search for fabric options by color. Returns fabrics matching the specified color across all products (or a specific product if provided). Use this when customer asks 'show me blue fabrics' or 'what fabrics do you have in grey'. Returns fabric names, colors, tiers, and swatch images.",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "description": "The color to search for. Examples: 'blue', 'grey', 'red', 'green', 'beige', 'white', 'black'"
                    },
                    "product_name": {
                        "type": "string",
                        "description": "Optional: Limit search to fabrics available for a specific product. Example: 'Alwinton', 'Rye', 'Saltdean'. If not provided, searches all fabrics across all products."
                    }
                },
                "required": ["color"]
            }
        }
    }
]

def get_price_tool_handler(query):
    """
    Tool handler wrapper for get_price.

    Takes query string directly (not Flask request) and calls existing get_price_logic.
    Returns: (result_dict, status_code)

    This wrapper allows Grok to call get_price as a tool without needing Flask request object.
    """
    # Create a mock request object with the query
    class MockRequest:
        def __init__(self, query):
            self._json = {"query": query}
            self.headers = {"User-Agent": "Grok-LLM-Tool"}

        def get_json(self):
            return self._json

    mock_request = MockRequest(query)

    # Call existing get_price_logic
    result, status_code = get_price_logic(mock_request)

    print(f"  [Tool:get_price] Query: '{query}' -> Status: {status_code}")

    return result, status_code

def search_by_budget_handler(max_price, product_type="all"):
    """
    Tool handler for search_by_budget.

    Searches all products and returns those with base prices under the specified budget.

    Args:
        max_price (int/float): Maximum budget in GBP
        product_type (str): Optional filter - 'sofa', 'bed', 'chair', 'footstool', 'dog_bed', or 'all'

    Returns:
        (result_dict, status_code)
    """
    print(f"  [Tool:search_by_budget] Budget: £{max_price}, Type: {product_type}")

    try:
        # Validate inputs
        max_price = float(max_price)
        if max_price <= 0:
            return {"error": "Budget must be greater than £0"}, 400

        # Filter products by budget and type
        matching_products = []

        for product_name, product_data in PRODUCT_SKU_MAP.items():
            # Skip if product doesn't match type filter
            if product_type != "all" and product_data.get("type") != product_type:
                continue

            # Check if base price is within budget
            base_price = int(product_data.get("price", 999999))
            if base_price <= max_price:
                matching_products.append({
                    "name": product_data.get("full_name", product_name),
                    "base_price": base_price,
                    "price_display": product_data.get("price_display", f"£{base_price:,}"),
                    "type": product_data.get("type", "unknown"),
                    "sku": product_data.get("sku")
                })

        # Sort by price (ascending)
        matching_products.sort(key=lambda x: x["base_price"])

        # Limit results to top 20 to avoid overwhelming response
        if len(matching_products) > 20:
            matching_products = matching_products[:20]
            truncated = True
        else:
            truncated = False

        print(f"  [Tool:search_by_budget] Found {len(matching_products)} products under £{max_price}")

        # Build response
        if not matching_products:
            return {
                "message": f"No products found under £{max_price:,.0f}",
                "suggestion": "Try increasing your budget or check our full range starting from £1,500",
                "count": 0
            }, 200

        return {
            "count": len(matching_products),
            "products": matching_products,
            "truncated": truncated,
            "fabric_tier_guidance": {
                "note": "Prices shown are base prices for standard configurations. Final price varies by:",
                "factors": ["Size (snuggler, 2-seater, 3-seater, etc.)", "Fabric tier (Essentials, Premium, Luxury)", "Cover type (fit, loose, slipcover)"],
                "tier_impact": "Essentials fabrics stay close to base price. Premium adds some cost. Luxury significantly increases price."
            },
            "next_steps": "Ask customer which product interests them, then use get_price for exact pricing with their preferred size and fabric."
        }, 200

    except ValueError as e:
        print(f"  [ERROR] Invalid max_price: {e}")
        return {"error": "Invalid budget amount. Please provide a numeric value."}, 400
    except Exception as e:
        print(f"  [ERROR] search_by_budget failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Search failed. Please try again."}, 500

def search_fabrics_by_color_handler(color, product_name=None):
    """
    Tool handler for search_fabrics_by_color.

    Searches for fabrics matching the specified color, optionally filtered by product.

    Args:
        color (str): Color to search for (e.g., 'blue', 'grey', 'red')
        product_name (str, optional): Limit search to this product's fabrics

    Returns:
        (result_dict, status_code)
    """
    print(f"  [Tool:search_fabrics_by_color] Color: '{color}', Product: {product_name or 'all'}")

    try:
        color_lower = color.lower().strip()
        if not color_lower:
            return {"error": "Color cannot be empty"}, 400

        # If product_name provided, find its SKU
        target_product_sku = None
        if product_name:
            product_name_lower = product_name.lower().strip()
            # Find matching product
            for keyword, product_data in PRODUCT_SKU_MAP.items():
                if keyword == product_name_lower or product_data.get("full_name", "").lower().find(product_name_lower) >= 0:
                    target_product_sku = product_data.get("sku")
                    print(f"  [Tool:search_fabrics_by_color] Limiting to product SKU: {target_product_sku}")
                    break

            if not target_product_sku:
                return {
                    "error": f"Product '{product_name}' not found",
                    "suggestion": "Try searching without specifying a product, or check the product name"
                }, 404

        # Search for matching fabrics
        matching_fabrics = []
        seen_fabrics = set()  # Track unique fabric+color combinations

        # Determine which products to search
        products_to_search = {}
        if target_product_sku:
            products_to_search = {target_product_sku: FABRIC_SKU_MAP.get(target_product_sku, {})}
        else:
            products_to_search = FABRIC_SKU_MAP

        # Search through fabrics
        for product_sku, fabric_map in products_to_search.items():
            for fabric_keyword, fabric_data in fabric_map.items():
                color_name = fabric_data.get("color_name", "")

                # Check if color matches
                if color_lower in color_name.lower():
                    # Create unique key to avoid duplicates
                    unique_key = f"{fabric_data.get('fabric_sku')}-{fabric_data.get('color_sku')}"

                    if unique_key not in seen_fabrics:
                        seen_fabrics.add(unique_key)
                        matching_fabrics.append({
                            "fabric_name": fabric_data.get("fabric_name", "Unknown"),
                            "color_name": color_name,
                            "tier": fabric_data.get("tier", "Unknown"),
                            "collection": fabric_data.get("collection", ""),
                            "description": fabric_data.get("desc", "")[:200] + "..." if len(fabric_data.get("desc", "")) > 200 else fabric_data.get("desc", ""),
                            "swatch_url": fabric_data.get("swatch_url", ""),
                            "fabric_sku": fabric_data.get("fabric_sku"),
                            "color_sku": fabric_data.get("color_sku")
                        })

        # Sort by tier (Essentials first, then Premium, then Luxury) and then by fabric name
        tier_order = {"Essentials": 1, "Premium": 2, "Luxury": 3}
        matching_fabrics.sort(key=lambda x: (tier_order.get(x["tier"], 99), x["fabric_name"], x["color_name"]))

        # Limit results to 30 to avoid overwhelming response
        if len(matching_fabrics) > 30:
            matching_fabrics = matching_fabrics[:30]
            truncated = True
        else:
            truncated = False

        print(f"  [Tool:search_fabrics_by_color] Found {len(matching_fabrics)} unique fabrics matching '{color}'")

        # Build response
        if not matching_fabrics:
            return {
                "message": f"No {color} fabrics found" + (f" for {product_name}" if product_name else ""),
                "suggestion": "Try a different color name (blue, grey, red, green, beige, etc.) or check our full fabric range",
                "count": 0
            }, 200

        # Group by tier for better presentation
        by_tier = {"Essentials": [], "Premium": [], "Luxury": []}
        for fabric in matching_fabrics:
            tier = fabric["tier"]
            if tier in by_tier:
                by_tier[tier].append(fabric)

        return {
            "count": len(matching_fabrics),
            "fabrics": matching_fabrics,
            "grouped_by_tier": by_tier,
            "truncated": truncated,
            "context": f"Showing {color} fabrics" + (f" for {product_name}" if product_name else " across all products"),
            "next_steps": "Show customer the options by tier. When they choose a fabric, use get_price to calculate exact pricing with their product and size."
        }, 200

    except Exception as e:
        print(f"  [ERROR] search_fabrics_by_color failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": "Fabric search failed. Please try again."}, 500

# --- CORS Helper (Critique #9) ---
def _build_cors_preflight_response():
    """Builds a response for a CORS preflight (OPTIONS) request."""
    response = jsonify({'message': 'CORS preflight OK'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response, 200

def _add_cors_headers(response):
    """Adds CORS headers to a standard response."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# --- Search Helper (Critique #5) ---
def find_best_matches(query, mapping, fuzziness=85):
    """
    Finds all matching keywords from a mapping in the query using regex and fuzzy matching.
    Returns a list of tuples: [(keyword, value, confidence_score), ...]
    """
    matches = []
    if not mapping:
        return matches
    
    # 1. Try simple regex first (fast)
    for keyword, value in mapping.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', query, re.IGNORECASE):
            confidence = 100 + len(keyword) # Prioritize exact matches
            matches.append((keyword, value, confidence))

    if matches:
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

    # 2. If no regex match, try fuzzy matching (slower)
    # Extract the "best" fuzzy match
    # process.extractOne returns (match_string, score, key)
    best_fuzzy_match = process.extractOne(query, mapping.keys(), score_cutoff=fuzziness)
    
    if best_fuzzy_match:
        keyword, score = best_fuzzy_match[0], best_fuzzy_match[1]
        value = mapping[keyword]
        print(f"  [Fuzzy Match] Found '{keyword}' with score {score}")
        matches.append((keyword, value, score))

    matches.sort(key=lambda x: x[2], reverse=True)
    return matches


# --- Cache Helpers (Critique #10) ---
def get_cache_key(product_sku, size_sku, cover_sku, fabric_sku, color_sku):
    """(Critique #10 Fix) Creates a unique cache key including product_sku."""
    return md5(f"{product_sku}{size_sku}{cover_sku}{fabric_sku}{color_sku}".encode()).hexdigest()

def get_from_cache(cache_key):
    """Checks cache for a valid, non-expired key."""
    cached_data = response_cache.get(cache_key)
    if cached_data:
        print(f"  [Cache HIT] Returning cached response for {cache_key}")
        return cached_data
    print(f"  [Cache MISS] for {cache_key}")
    return None

def set_to_cache(cache_key, data):
    """Sets a response in the cache."""
    try:
        response_cache.set(cache_key, data)
        print(f"  [Cache] Stored response (total entries: {len(response_cache)})")
    except Exception as e:
        # Non-fatal - log warning but don't crash if cache fails
        print(f"  [WARNING] Cache write failed: {e}")

# --- Main Logic Function ---
def get_price_logic(request):
    """
    This is the core logic. It's no longer a Flask route,
    just a pure function called by the entry point.
    It returns (data_dictionary, status_code)
    """
    
    # --- (Critique #7: Authentication - COMMENTED OUT) ---
    # auth_header = request.headers.get('Authorization')
    # if not auth_header or auth_header != f"Bearer {API_KEY}":
    #     return {"error": "Unauthorized"}, 401
    
    # 1. Get the query from the frontend app
    # CRITICAL: Wrap get_json() in try/catch to prevent crashes on malformed requests
    try:
        data = request.get_json()
    except (ValueError, TypeError) as e:
        print(f"  [ERROR] Invalid JSON in request: {e}")
        return {"error": "Invalid request format. Please check your request body."}, 400

    if not data:
        return {"error": "No JSON payload received"}, 400

    query = data.get('query', '').lower()
    user_agent = request.headers.get('User-Agent', 'Mozilla/5.0')

    if not query:
        return {"error": "No query provided"}, 400

    print(f"--- New Query: '{query}' ---")

    # --- 2. Translation Logic (Ambiguity Check - Critique #5) ---
    
    product_sku = None
    product_name = None
    product_type = None 
    size_sku = None
    cover_sku = None
    fabric_match_data = None
    
    # Find Product (and its SKU and TYPE)
    product_matches = find_best_matches(query, PRODUCT_SKU_MAP)
    if not product_matches:
        print(f"  [Error] No product match found for query: {query}")
        return {"error": f"Product not found. Please try a product name like 'Alwinton' or 'Dog Bed'."}, 400
    
    # Check for ambiguity
    if len(product_matches) > 1 and product_matches[0][2] == product_matches[1][2]:
         suggestions = [m[1]["full_name"] for m in product_matches[:3]]
         print(f"  [Error] Ambiguous product: {suggestions}")
         return {"error": f"Ambiguous product. Did you mean: {', '.join(suggestions)}?"}, 400
    
    product_name_keyword, product_data = product_matches[0][0], product_matches[0][1]
    product_sku = product_data["sku"]
    product_type = product_data["type"] # This is "sofa", "bed", "chair", etc.
    print(f"  [Match] Product: '{product_name_keyword}' -> SKU: '{product_sku}', Type: '{product_type}'")

    # Find Size (based on the product_sku)
    product_size_map = SIZE_SKU_MAP.get(product_sku, {})
    size_matches = find_best_matches(query, product_size_map)
    if not size_matches:
         # For products like footstools, they might not say a size.
         if product_type in ["footstool", "dog_bed"] and product_size_map:
             size_sku = list(product_size_map.values())[0] # Default to first size
             print(f"  [Info] No size specified, defaulting to first available: '{size_sku}'")
         else:
            print(f"  [Error] No size match for {product_sku}. Map: {product_size_map}")
            return {"error": f"Could not find a size for '{product_data['full_name']}'. Try 'snuggler', '3 seater', etc."}, 400
    else:
        size_sku = size_matches[0][1] # [1] is the SKU
        print(f"  [Match] Size: '{size_matches[0][0]}' -> SKU: '{size_sku}'")

    # Find Cover (based on the product_sku)
    product_cover_map = COVERS_SKU_MAP.get(product_sku, {})
    cover_matches = find_best_matches(query, product_cover_map)
    if cover_matches:
        cover_sku = cover_matches[0][1]
        print(f"  [Match] Cover: '{cover_matches[0][0]}' -> SKU: '{cover_sku}'")
    else:
        # (Critique #11) Smart Default
        cover_sku = "fit" # Default to 'fit'
        if product_cover_map and "fit" not in product_cover_map.values():
             # If 'fit' isn't valid, just grab the first available one
             cover_sku = list(product_cover_map.values())[0]
        print(f"  [Info] No cover specified, defaulting to: '{cover_sku}'")
        
    # Find Fabric (Search *only* within the product's available fabrics)
    product_fabric_map = FABRIC_SKU_MAP.get(product_sku, {})
    if not product_fabric_map:
        print(f"  [Error] No fabric dictionary found for product SKU: {product_sku}")
        return {"error": f"No fabrics seem to be available for '{product_data['full_name']}'."}, 404

    fabric_matches = find_best_matches(query, product_fabric_map)
    if not fabric_matches:
         print(f"  [Error] No fabric match for query: {query}")
         return {"error": f"Fabric not found for '{product_data['full_name']}'. Try a specific color like 'pacific' or 'waves'."}, 400
    
    # Ambiguity check for fabrics (e.g., "blue" matching "light blue" and "dark blue")
    if len(fabric_matches) > 1 and fabric_matches[0][2] < 100: # Check if it wasn't an exact match
        # Check if top matches are too close to call
        if fabric_matches[0][2] - fabric_matches[1][2] < 10: # If scores are very close
            suggestions = [m[0] for m in fabric_matches[:3]]
            print(f"  [Error] Ambiguous fabric: {suggestions}")
            return {"error": f"Ambiguous fabric. Did you mean: {', '.join(suggestions)}?"}, 400
        
    fabric_match_data = fabric_matches[0][1] # [1] is the fabric data dict
    print(f"  [Match] Fabric: '{fabric_matches[0][0]}' -> SKU: '{fabric_match_data['fabric_sku']}', Color: '{fabric_match_data['color_sku']}'")

    # (Critique #13) Validate fabric_match_data
    if not fabric_match_data or 'fabric_sku' not in fabric_match_data or 'color_sku' not in fabric_match_data:
        print(f"  [Error] Invalid fabric data found: {fabric_match_data}")
        return {"error": f"Invalid fabric data found for '{product_data['full_name']}'"}, 500
        
    # --- 3. Check Cache (Critique #10) ---
    cache_key = get_cache_key(product_sku, size_sku, cover_sku, fabric_match_data['fabric_sku'], fabric_match_data['color_sku'])
    cached_response = get_from_cache(cache_key)
    if cached_response:
        return cached_response, 200

    # --- 4. Build the API Payload (ROUTING LOGIC) ---
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://sofasandstuff.com/{product_data["url"]}',
        'User-Agent': user_agent 
    }
    
    api_url = ""
    payload = {}
    
    # (Critique #7 - Verified) Dog bed is correctly routed
    # FIXED: Mattresses use the sofa API endpoint with query SKU format
    if product_type in ["sofa", "chair", "footstool", "dog_bed", "sofa_bed", "snuggler", "mattress"]:
        api_url = SOFA_API_URL
        
        if product_type == "mattress":
            # Mattress query SKU: product + size + tension + off + off
            # Example: ptskibexfoffoff = pts + kib + exf + off + off
            query_sku = f"{product_sku}{size_sku}{fabric_match_data['fabric_sku']}offoff"
        else:
            # Standard sofa query SKU: product + size + cover + fabric + color
            query_sku = f"{product_sku}{size_sku}{cover_sku}{fabric_match_data['fabric_sku']}{fabric_match_data['color_sku']}"
        
        payload = {
            'sku': product_sku,
            'querySku': query_sku
        }
        
    elif product_type == "bed":
        api_url = BED_API_URL
        payload = {
            'productsku': product_sku,
            'sizesku': size_sku,
            'coversku': cover_sku,
            'fabricSku': fabric_match_data['fabric_sku'],
            'colourSku': fabric_match_data['color_sku']
        }
    
    else:
        print(f"  [Error] Unknown product type: {product_type}")
        return {"error": f"Unknown product type: {product_type}"}, 500

    try:
        # --- 5. Call the S&S Price API (Critique #6) ---
        print(f"  [API Call] Calling: {api_url} with payload: {payload}")
        response = session.post(api_url, data=payload, headers=headers, timeout=10) # 10-second timeout
        response.raise_for_status() 
        price_data = response.json()
        
        # --- 6. Parse and Simplify the Response ---
        record = {}
        image_urls = []
        
        if product_type == "bed":
             record = price_data
             # Note: Bed API has no 'HeroImages' in its response
        else:
            # All other types use the Sofa API structure
            if price_data.get("success"):
                record = price_data.get("result", {}).get("ProductSkuRecord", {})
                # FIXED: HeroImages are at result level, not inside ProductSkuRecord
                images = price_data.get("result", {}).get('HeroImages', [])
                if images: 
                    for img in images:
                        img_url = img.get('ImageUrl', '').replace("\\", "/")
                        if img_url:
                            # Handle both relative and absolute paths
                            if img_url.startswith('http'):
                                image_urls.append(img_url)
                            else:
                                # Remove leading 'assets/' if present
                                img_url = img_url.lstrip('/')
                                if img_url.startswith('assets/'):
                                    img_url = img_url[7:]  # Remove 'assets/'
                                
                                # Split path into components and encode each part
                                # This handles spaces and special characters properly
                                path_parts = img_url.split('/')
                                encoded_parts = [quote(part, safe='') for part in path_parts]
                                encoded_path = '/'.join(encoded_parts)
                                
                                image_urls.append("https://sofasandstuff.com/" + encoded_path)
            
        if not record:
             return {"error": "S&S API returned empty response."}, 500

        full_name = f"{record.get('ProductName', '')} {record.get('SizeName', '')}"
        fabric_name = f"{record.get('FabricName', '')} - {record.get('ColourName', '')}"
        
        simplified_response = {
            "productName": full_name,
            "fabricName": fabric_name,
            "price": record.get('PriceText', 'N/A'),
            "oldPrice": record.get('OldPriceText', None),
            "imageUrls": image_urls,
            "specs": record.get('ProductSizeAttributes', []),
            "fabricDetails": {
                "tier": fabric_match_data.get('tier', 'Unknown'),
                "description": fabric_match_data.get('desc', ''),
                "swatchUrl": fabric_match_data.get('swatch_url', '')
            }
        }
        
        # 9. Set to Cache and Return
        set_to_cache(cache_key, simplified_response)
        return simplified_response, 200

    except requests.exceptions.Timeout:
        print(f"[ERROR] API Request Timed Out. URL: {api_url}")
        return {"error": "Request timed out. The S&S server may be slow."}, 504
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request Failed. URL: {api_url}, Payload: {payload}, Error: {e}")
        return {"error": f"API request failed. Built an invalid SKU? (Query: {query})"}, 502
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500

# --- Chat Handler for Grok LLM (Phase 1C: Piece 3.2) ---
def chat_handler(request):
    """
    Handles /chat endpoint for Grok LLM conversations.

    Expects JSON body:
    {
        "messages": [{"role": "user", "content": "..."}],
        "session_id": "optional-session-id"
    }

    Returns:
    {
        "response": "...",
        "metadata": {"tokens": 123, "session_id": "..."}
    }
    """
    try:
        # Check if OpenRouter client is initialized
        if not openrouter_client:
            return {
                "error": "Chat service unavailable. OpenRouter API key not configured.",
                "fallback": "Please use the /getPrice endpoint for direct product queries."
            }, 503

        # Parse request body
        # CRITICAL: Wrap get_json() in try/catch to prevent crashes on malformed requests
        try:
            data = request.get_json()
        except (ValueError, TypeError) as e:
            print(f"  [ERROR] Invalid JSON in chat request: {e}")
            return {"error": "Invalid request format. Please check your JSON body."}, 400

        if not data:
            return {"error": "No JSON body provided"}, 400

        messages = data.get('messages', [])
        session_id = data.get('session_id', 'no-session')

        if not messages:
            return {"error": "No messages provided. Expected 'messages' array in JSON body."}, 400

        # Validate messages format
        if not isinstance(messages, list):
            return {"error": "'messages' must be an array"}, 400

        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                return {"error": "Each message must have 'role' and 'content' fields"}, 400

        print(f"[Chat] Processing {len(messages)} messages for session: {session_id}")

        # Build conversation with system prompt
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]

        total_tokens = 0
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        # Tool calling loop: Keep calling Grok until no more tool calls
        while iteration < max_iterations:
            iteration += 1
            print(f"[Chat] Iteration {iteration}: Calling Grok...")

            # Call Grok with tools
            response = openrouter_client.chat.completions.create(
                model=GROK_MODEL,
                messages=conversation,
                tools=TOOLS,
                temperature=0.1  # Low temperature for precise, deterministic responses
            )

            # Track tokens
            if response.usage:
                total_tokens += response.usage.total_tokens

            assistant_message = response.choices[0].message

            # Check if Grok wants to call tools
            if assistant_message.tool_calls:
                print(f"[Chat] Grok requested {len(assistant_message.tool_calls)} tool call(s)")

                # Add assistant's tool call message to conversation
                conversation.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args_json = tool_call.function.arguments

                    print(f"  [Tool] Executing: {tool_name} with args: {tool_args_json}")

                    # Parse arguments
                    import json
                    try:
                        tool_args = json.loads(tool_args_json)
                    except json.JSONDecodeError as e:
                        print(f"  [ERROR] Failed to parse tool arguments: {e}")
                        tool_result = {"error": "Invalid tool arguments"}
                        tool_status = 400
                    else:
                        # Route to correct tool handler
                        if tool_name == "get_price":
                            query = tool_args.get("query", "")
                            tool_result, tool_status = get_price_tool_handler(query)
                        elif tool_name == "search_by_budget":
                            max_price = tool_args.get("max_price", 0)
                            product_type = tool_args.get("product_type", "all")
                            tool_result, tool_status = search_by_budget_handler(max_price, product_type)
                        elif tool_name == "search_fabrics_by_color":
                            color = tool_args.get("color", "")
                            product_name = tool_args.get("product_name")
                            tool_result, tool_status = search_fabrics_by_color_handler(color, product_name)
                        else:
                            tool_result = {"error": f"Unknown tool: {tool_name}"}
                            tool_status = 400

                    # Add tool result to conversation with explicit success/failure marker
                    # CRITICAL: Include status so Grok knows if tool succeeded or failed
                    if tool_status >= 400:
                        # FAILURE - Mark clearly so Grok NEVER makes up data
                        tool_response = {
                            "status": "FAILED",
                            "error": tool_result.get("error", "Unknown error"),
                            "status_code": tool_status,
                            "CRITICAL_WARNING": "DO NOT MAKE UP OR ESTIMATE DATA. Tell user the system is temporarily unavailable."
                        }
                    else:
                        # SUCCESS - Include actual data
                        tool_response = {
                            "status": "SUCCESS",
                            "data": tool_result,
                            "status_code": tool_status
                        }

                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_response)
                    })

                    print(f"  [Tool] Result status: {tool_status}")

                # Continue loop to get Grok's response based on tool results
                continue

            else:
                # No tool calls - Grok has final response
                print(f"[Chat] Grok returned final response (no tool calls)")
                final_response = assistant_message.content or ""

                print(f"[Chat] Session: {session_id}, Total Tokens: {total_tokens}, Model: {GROK_MODEL}")

                # Return response
                return {
                    "response": final_response,
                    "metadata": {
                        "tokens": total_tokens,
                        "session_id": session_id,
                        "model": GROK_MODEL,
                        "iterations": iteration
                    }
                }, 200

        # Max iterations reached
        print(f"[WARNING] Max iterations ({max_iterations}) reached for session: {session_id}")
        return {
            "error": "Maximum tool calling iterations reached. Please try rephrasing your question.",
            "metadata": {
                "tokens": total_tokens,
                "session_id": session_id
            }
        }, 500

    except Exception as e:
        print(f"[ERROR] Chat handler failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": "Chat request failed. Please try again or use /getPrice for direct queries.",
            "details": str(e)
        }, 500

# --- Google Cloud Functions Entry Point (Critique #2, #9) ---
@functions_framework.http
def http_entry_point(request):
    """Cloud Functions entry point that routes requests."""
    
    # Handle CORS preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # Handle the /chat endpoint (Phase 1C: Grok LLM conversations)
    if request.path == '/chat' and request.method == 'POST':
        response_data, status_code = chat_handler(request)
        response = jsonify(response_data)
        response.status_code = status_code
        return _add_cors_headers(response)

    # Handle the main /getPrice endpoint (Phase 1.5: Direct keyword matching)
    if request.path == '/getPrice' and request.method == 'POST':
        response_data, status_code = get_price_logic(request)
        response = jsonify(response_data)
        response.status_code = status_code
        return _add_cors_headers(response)

    # Handle the root path for a health check
    if request.path == '/' and request.method == 'GET':
        return _add_cors_headers(jsonify({"message": "Sofas & Stuff Backend Translator is ALIVE!"}))

    # Handle 404
    return _add_cors_headers(jsonify({"error": "Not Found"})), 404