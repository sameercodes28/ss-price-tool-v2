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

# Import error code system (v2.5.0)
from error_codes import create_error_response, ERROR_CODES

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

    Args:
        max_size (int): Maximum number of entries before eviction (default: 1000)
        ttl (int): Time-to-live in seconds before entries expire (default: 300)
    """
    def __init__(self, max_size=1000, ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key):
        """
        Get value from cache if it exists and hasn't expired.

        Automatically removes expired entries. Marks accessed entries as
        recently used (LRU ordering).

        Args:
            key (str): Cache key to retrieve

        Returns:
            Any: Cached value if found and not expired, None otherwise
        """
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
        """
        Store value in cache, evicting oldest entry if at capacity.

        If key already exists, it's removed and re-added (updates timestamp).
        If cache is full, evicts the least recently used entry.

        Args:
            key (str): Cache key to store
            value (Any): Value to cache

        Side effects:
            Prints log message when evicting old entries
        """
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

# --- Setup: Rate Limiting (v2.5.0 Phase 4) ---
class RateLimiter:
    """
    Sliding window rate limiter to protect against abuse and cost overruns.

    Tracks requests per session and globally. Uses sliding window to prevent
    burst attacks and accidental infinite loops from causing runaway costs.

    Limits:
        - Per session: 30 requests per minute
        - Global: 200 requests per minute
    """
    def __init__(self, per_session_limit=30, global_limit=200, window_seconds=60):
        self.per_session_limit = per_session_limit
        self.global_limit = global_limit
        self.window_seconds = window_seconds
        self.session_requests = {}  # session_id -> [timestamps]
        self.global_requests = []   # [timestamps]

    def _clean_old_requests(self, request_list, current_time):
        """Remove requests older than the time window."""
        cutoff_time = current_time - self.window_seconds
        return [ts for ts in request_list if ts > cutoff_time]

    def is_allowed(self, session_id):
        """
        Check if request is allowed for this session.

        Args:
            session_id (str): Session identifier

        Returns:
            tuple: (allowed: bool, reason: str, retry_after: int)
                - allowed: True if request should be processed
                - reason: "session" or "global" if rate limited
                - retry_after: Seconds until rate limit resets
        """
        current_time = time.time()

        # Clean up old global requests
        self.global_requests = self._clean_old_requests(self.global_requests, current_time)

        # Check global limit
        if len(self.global_requests) >= self.global_limit:
            oldest_request = min(self.global_requests)
            retry_after = int(self.window_seconds - (current_time - oldest_request))
            return (False, "global", retry_after)

        # Clean up old session requests
        if session_id in self.session_requests:
            self.session_requests[session_id] = self._clean_old_requests(
                self.session_requests[session_id], current_time
            )
        else:
            self.session_requests[session_id] = []

        # Check session limit
        if len(self.session_requests[session_id]) >= self.per_session_limit:
            oldest_request = min(self.session_requests[session_id])
            retry_after = int(self.window_seconds - (current_time - oldest_request))
            return (False, "session", retry_after)

        # Allow request - record it
        self.global_requests.append(current_time)
        self.session_requests[session_id].append(current_time)

        return (True, None, 0)

rate_limiter = RateLimiter(per_session_limit=30, global_limit=200, window_seconds=60)

# --- (Critique #7: Authentication - COMMENTED OUT) ---
# To enable, set this in your GCF Environment Variables
# API_KEY = os.environ.get('YOUR_APP_API_KEY', 'default-key-change-me')

# --- Request ID Tracing (v2.5.0 Phase 3) ---
def get_request_id(request):
    """
    Extract request ID from X-Request-ID header for tracing.
    Returns shortened version for logging (last 8 chars).

    Args:
        request: Flask/Functions Framework request object

    Returns:
        str: Request ID (truncated to last 8 chars) or 'unknown'
    """
    request_id = request.headers.get('X-Request-ID', 'unknown')
    if request_id != 'unknown' and len(request_id) > 8:
        return request_id[-8:]  # Last 8 chars for brevity
    return request_id

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

# --- xAI/Grok Configuration ---
# Environment variables for xAI API integration (direct, not via OpenRouter)
XAI_API_KEY = os.getenv('XAI_API_KEY')
GROK_MODEL = os.getenv('GROK_MODEL', 'grok-4-fast')  # Default to grok-4-fast

# Initialize xAI client (only if API key is available)
openrouter_client = None  # Keep variable name for backward compatibility
if XAI_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=XAI_API_KEY
    )
    print(f"xAI client initialized with model: {GROK_MODEL}")
else:
    print("[WARNING] XAI_API_KEY not found. Chat endpoint will not work.")

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
   - No fabric? Try "two tone plain biscuit" (standard base configuration for most products)
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

## CRITICAL: BUDGET SEARCH FORMATTING

When presenting results from search_by_budget:

**NEVER invent or guess fabric names!** The tool returns base prices without fabric details.

WRONG ❌:
"Midhurst Sofa in V&A Collection Botanical Collage All Over - £1,937"

CORRECT ✅:
"Midhurst Sofa - £1,937"
or
"Midhurst 3 Seater - £1,937 (base configuration)"

Add a note: "Prices shown are base for standard configurations—exact price depends on fabric choice."

If user wants a specific product, use get_price tool to show exact pricing with fabric details.

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

**For multi-product responses (search_by_budget results):**
Show each product using the SAME format - NO #### headers:

### 💰 Price

**Product 1 Name in Fabric**
**£PRICE**

Brief description in 1-2 sentences.

**Product 2 Name in Fabric**
**£PRICE**

Brief description in 1-2 sentences.

**🚨 CRITICAL: Budget Search Fabric Rules**

The search_by_budget tool returns ONLY product names and base prices. It does NOT include fabric details.

**NEVER invent or guess fabric names!**

If the tool returns:
```
{
  "products": [
    {"name": "Midhurst 3 Seater", "base_price": 1937}
  ]
}
```

WRONG ❌:
"Midhurst 3 Seater in V&A Collection Botanical Collage All Over - £1,937"

CORRECT ✅:
"Midhurst 3 Seater - £1,937 (base configuration)"

Add a note at the end: "Prices shown are base for standard configurations—exact price depends on fabric choice."

If user wants specific fabric pricing, use get_price tool with exact product/fabric combination.

For FAILED queries (status="FAILED"), respond with:

"I apologize, but our pricing system is temporarily unavailable. Please try again in a few moments."

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

## FABRIC SEARCH FORMATTING

When presenting results from search_fabrics_by_color, format each fabric as:

**[Fabric Name]** in [Color Name]
_[Description]_
[View swatch]([swatch_url])

EXAMPLE:
**House Wool** in Navy
_Premium wool blend with subtle texture, perfect for high-traffic family homes_
[View swatch](https://sofasandstuff.com/...)

RULES:
- Fabric name MUST be in **bold**
- Description in _italics_
- Swatch link MUST be clickable hyperlink with "View swatch" as the text
- Group by tier (Essentials, Premium, Luxury) if showing multiple
- Keep descriptions concise (under 30 words)

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
    """
    Builds response for CORS preflight OPTIONS request.

    Preflight requests are sent by browsers before actual requests
    to verify CORS permissions.

    Returns:
        tuple: (Flask Response object, 200 status code)
               Response includes CORS headers allowing all origins
    """
    response = jsonify({'message': 'CORS preflight OK'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Request-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response, 200

def _add_cors_headers(response):
    """
    Adds CORS headers to Flask response to allow cross-origin requests.

    Args:
        response (Flask Response): Response object to modify

    Returns:
        Flask Response: Same response object with CORS headers added
    """
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# --- Search Helper (Critique #5) ---
def find_best_matches(query, mapping, fuzziness=85):
    """
    Finds matching keywords from a mapping using regex and fuzzy matching.

    First attempts exact regex word-boundary matching for speed. If no exact
    matches, falls back to fuzzy string matching with configurable threshold.

    Args:
        query (str): Search query to match against (case-insensitive)
        mapping (dict): Dictionary mapping keywords to values
        fuzziness (int): Minimum fuzzy match score (0-100, default: 85)

    Returns:
        list: Tuples of (keyword, value, confidence_score) sorted by confidence desc.
              Empty list if no matches found.

    Side effects:
        Prints fuzzy match info when fuzzy matching is used
    """
    matches = []
    if not mapping:
        return matches
    
    # 1. Try exact and prefix matching (fast and precise)
    for keyword, value in mapping.items():
        # Exact match with word boundaries
        if re.search(r'\b' + re.escape(keyword) + r'\b', query, re.IGNORECASE):
            confidence = 100 + len(keyword)
            matches.append((keyword, value, confidence))
        # Prefix match: query contains start of keyword (e.g., "3 seater" matches "3 seater sofa")
        # This allows "3 seater" to match "3 seater sofa" without fuzzy matching
        elif re.search(r'\b' + re.escape(keyword), query, re.IGNORECASE):
            # Lower confidence for prefix matches
            confidence = 90 + len(keyword)
            matches.append((keyword, value, confidence))

    if matches:
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches

    # 2. NO FUZZY MATCHING - Causes dangerous errors like 3-seater→4-seater
    # Grok handles typo correction at the LLM layer
    # If no exact match, return empty list and let Grok try alternative queries
    print(f"  [No Exact Match] Query '{query}' found no exact matches in mapping")
    return matches


# --- Cache Helpers (Critique #10) ---
def get_cache_key(product_sku, size_sku, cover_sku, fabric_sku, color_sku):
    """
    Creates unique MD5 hash cache key from SKU components.

    Combines all SKU components into a single string and returns MD5 hash.
    This ensures each unique combination of product/size/cover/fabric/color
    gets a unique cache key.

    Args:
        product_sku (str): Product SKU identifier
        size_sku (str): Size SKU identifier
        cover_sku (str): Cover/upholstery SKU identifier
        fabric_sku (str): Fabric SKU identifier
        color_sku (str): Color SKU identifier

    Returns:
        str: 32-character MD5 hexadecimal hash
    """
    return md5(f"{product_sku}{size_sku}{cover_sku}{fabric_sku}{color_sku}".encode()).hexdigest()

def get_from_cache(cache_key):
    """
    Retrieves cached pricing response if available and not expired.

    Args:
        cache_key (str): MD5 hash cache key from get_cache_key()

    Returns:
        dict or None: Cached response data if found and not expired, None otherwise

    Side effects:
        Prints cache HIT or MISS log message
    """
    cached_data = response_cache.get(cache_key)
    if cached_data:
        print(f"  [Cache HIT] Returning cached response for {cache_key}")
        return cached_data
    print(f"  [Cache MISS] for {cache_key}")
    return None

def set_to_cache(cache_key, data):
    """
    Stores pricing response in cache with error handling.

    Attempts to store data in cache. If caching fails, logs warning
    but doesn't raise exception (non-fatal error).

    Args:
        cache_key (str): MD5 hash cache key from get_cache_key()
        data (dict): Response data to cache

    Side effects:
        Prints cache storage log or warning on failure
        May evict old entries if cache is full (see LRUCache.set)
    """
    try:
        response_cache.set(cache_key, data)
        print(f"  [Cache] Stored response (total entries: {len(response_cache)})")
    except Exception as e:
        # Non-fatal - log warning but don't crash if cache fails
        print(f"  [WARNING] Cache write failed: {e}")

# --- Main Logic Function ---
def get_price_logic(request):
    """
    Core pricing logic for /getPrice endpoint.

    Extracts product/size/fabric from natural language query, translates to SKUs,
    fetches price from S&S API, and returns structured response. Uses fuzzy matching
    for product names and caching for performance.

    Args:
        request (Flask Request): Request object with JSON body containing:
            - query (str): Natural language pricing query (e.g., "alwinton snuggler pacific")

    Returns:
        tuple: (response_dict, status_code)
            - response_dict: Pricing data or error response with error_code
            - status_code (int): HTTP status code (200, 400, 500, 502, 504)

    Side effects:
        - Prints request ID and query logs
        - Caches successful responses
        - Makes external API calls to sofasandstuff.com

    Error codes:
        E2006: Invalid JSON format
        E2007: Missing required field (query)
        E2001: Product not found
        E2002: Ambiguous product match
        E2003: Fabric not found
        E2004: Size not valid
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
        return create_error_response("E2006"), 400

    if not data:
        return create_error_response("E2007", details={"field": "JSON body"}), 400

    query = data.get('query', '').lower()
    user_agent = request.headers.get('User-Agent', 'Mozilla/5.0')
    request_id = get_request_id(request)

    if not query:
        return create_error_response("E2007", details={"field": "query"}), 400

    print(f"[{request_id}] --- New Query: '{query}' ---")

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
        print(f"[{request_id}]  [Error] No product match found for query: {query}")
        return create_error_response("E2001"), 400

    # Check for ambiguity
    if len(product_matches) > 1 and product_matches[0][2] == product_matches[1][2]:
         suggestions = [m[1]["full_name"] for m in product_matches[:3]]
         print(f"[{request_id}]  [Error] Ambiguous product: {suggestions}")
         return create_error_response(
             "E2002",
             custom_user_message=f"Multiple products match. Did you mean: {', '.join(suggestions)}?",
             details={"options": suggestions}
         ), 400

    product_name_keyword, product_data = product_matches[0][0], product_matches[0][1]
    product_sku = product_data["sku"]
    product_type = product_data["type"] # This is "sofa", "bed", "chair", etc.
    print(f"[{request_id}]  [Match] Product: '{product_name_keyword}' -> SKU: '{product_sku}', Type: '{product_type}'")

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
            return create_error_response("E2003"), 400
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
        return create_error_response(
            "E2004",
            custom_user_message=f"No fabrics available for '{product_data['full_name']}'."
        ), 404

    fabric_matches = find_best_matches(query, product_fabric_map)
    if not fabric_matches:
         print(f"  [Error] No fabric match for query: {query}")
         return create_error_response("E2004"), 400

    # Ambiguity check for fabrics (e.g., "blue" matching "light blue" and "dark blue")
    if len(fabric_matches) > 1 and fabric_matches[0][2] < 100: # Check if it wasn't an exact match
        # Check if top matches are too close to call
        if fabric_matches[0][2] - fabric_matches[1][2] < 10: # If scores are very close
            suggestions = [m[0] for m in fabric_matches[:3]]
            print(f"  [Error] Ambiguous fabric: {suggestions}")
            return create_error_response(
                "E2005",
                custom_user_message=f"Multiple fabrics match. Did you mean: {', '.join(suggestions)}?",
                details={"options": suggestions}
            ), 400
        
    fabric_match_data = fabric_matches[0][1] # [1] is the fabric data dict
    print(f"  [Match] Fabric: '{fabric_matches[0][0]}' -> SKU: '{fabric_match_data['fabric_sku']}', Color: '{fabric_match_data['color_sku']}'")

    # (Critique #13) Validate fabric_match_data
    if not fabric_match_data or 'fabric_sku' not in fabric_match_data or 'color_sku' not in fabric_match_data:
        print(f"  [Error] Invalid fabric data found: {fabric_match_data}")
        return create_error_response("E3004", details={"product": product_data['full_name']}), 500
        
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
    Handles conversational pricing queries via Grok LLM with tool calling.

    Processes natural language conversations, allowing Grok LLM to call internal
    tools (get_price, search_by_budget, search_fabrics_by_color) to answer pricing
    questions. Supports multi-turn conversations and maintains session history.

    Args:
        request (Flask Request): Request object with JSON body containing:
            - messages (list): Array of message dicts with 'role' and 'content'
            - session_id (str, optional): Session identifier for tracking

    Returns:
        tuple: (response_dict, status_code)
            - response_dict: Contains 'response' (LLM message) and 'metadata'
            - status_code (int): HTTP status code (200, 400, 503)

    Side effects:
        - Calls OpenRouter API (Grok LLM)
        - May trigger tool calls that fetch prices or search products
        - Prints request ID and chat processing logs
        - Token usage logged in metadata

    Error codes:
        E1006: OpenRouter/Grok unavailable
        E2006: Invalid JSON format
        E2007: Missing required field (messages)

    Example request body:
        {"messages": [{"role": "user", "content": "How much is alwinton?"}],
         "session_id": "abc123"}

    Example response:
        {"response": "The Alwinton 3-seater in Pacific fabric costs £1,095",
         "metadata": {"tokens": 245, "session_id": "abc123"}}
    """
    try:
        # Check if OpenRouter client is initialized
        if not openrouter_client:
            return create_error_response(
                "E1006",
                details={"fallback_endpoint": "/getPrice"}
            ), 503

        # Parse request body
        # CRITICAL: Wrap get_json() in try/catch to prevent crashes on malformed requests
        try:
            data = request.get_json()
        except (ValueError, TypeError) as e:
            print(f"  [ERROR] Invalid JSON in chat request: {e}")
            return create_error_response("E2006"), 400

        if not data:
            return create_error_response("E2007", details={"field": "JSON body"}), 400

        messages = data.get('messages', [])
        session_id = data.get('session_id', 'no-session')
        request_id = get_request_id(request)

        if not messages:
            return create_error_response("E2007", details={"field": "messages array"}), 400

        # Validate messages format
        if not isinstance(messages, list):
            return {"error": "'messages' must be an array"}, 400

        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                return {"error": "Each message must have 'role' and 'content' fields"}, 400

        print(f"[{request_id}] [Chat] Processing {len(messages)} messages for session: {session_id}")

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
def main(request):
    """
    Google Cloud Functions HTTP entry point - routes all requests.

    Main routing function that handles all HTTP requests to the Cloud Function.
    Routes to appropriate handlers based on path and method, handles CORS,
    and provides health check endpoint.

    Supported endpoints:
        - OPTIONS * : CORS preflight (all paths)
        - GET / : Health check
        - POST /chat : Grok LLM conversational interface
        - POST /getPrice : Direct keyword-based pricing

    Args:
        request (Flask Request): Incoming HTTP request from Google Cloud Functions

    Returns:
        Flask Response: JSON response with appropriate status code and CORS headers

    Response codes:
        200: Successful request
        400: Client error (invalid input, missing fields)
        404: Unknown endpoint
        500: Server error
        503: Service unavailable (OpenRouter down)
        504: Request timeout
    """

    # Handle CORS preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # Rate limiting check (v2.5.0 Phase 4)
    # Extract session_id for rate limiting (from request body or headers)
    session_id = 'no-session'
    if request.method == 'POST':
        try:
            data = request.get_json(silent=True)
            if data:
                session_id = data.get('session_id', 'no-session')
        except:
            pass  # Use default if parsing fails

    # Check rate limit
    allowed, reason, retry_after = rate_limiter.is_allowed(session_id)
    if not allowed:
        print(f"[Rate Limit] Blocked {session_id} ({reason} limit exceeded, retry after {retry_after}s)")
        error_response = create_error_response(
            "E1007",
            details={
                "limit_type": reason,
                "retry_after_seconds": retry_after,
                "session_id": session_id
            }
        )
        response = jsonify(error_response)
        response.status_code = 429
        response.headers['Retry-After'] = str(retry_after)
        return _add_cors_headers(response)

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

    # Handle the root path and /health for health checks
    if (request.path == '/' or request.path == '/health') and request.method == 'GET':
        # Comprehensive health check for monitoring systems
        health_data = {
            "status": "healthy",
            "service": "Sofas & Stuff Pricing API",
            "version": "v2.5.0",
            "timestamp": int(time.time()),

            # Cache status
            "cache": {
                "entries": len(response_cache),
                "max_size": response_cache.max_size,
                "ttl_seconds": response_cache.ttl,
                "usage_percent": round((len(response_cache) / response_cache.max_size) * 100, 1)
            },

            # Rate limiter status
            "rate_limiter": {
                "active_sessions": len(rate_limiter.session_requests),
                "global_requests_in_window": len(rate_limiter.global_requests),
                "per_session_limit": rate_limiter.per_session_limit,
                "global_limit": rate_limiter.global_limit,
                "window_seconds": rate_limiter.window_seconds
            },

            # Service availability
            "services": {
                "openrouter_llm": "available" if openrouter_client else "unavailable",
                "price_api": "available"  # Always available (direct S&S API)
            },

            # Endpoints
            "endpoints": {
                "chat": "/chat",
                "price": "/getPrice",
                "health": "/health"
            }
        }

        return _add_cors_headers(jsonify(health_data))

    # Handle 404
    return _add_cors_headers(jsonify({"error": "Not Found"})), 404