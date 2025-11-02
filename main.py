import functions_framework
import requests
import json
import os
import re
import time
from hashlib import md5
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
# Simple in-memory cache with a 5-minute (300s) Time-to-Live (TTL)
response_cache = {}
CACHE_TTL = 300  # 5 minutes

# --- (Critique #7: Authentication - COMMENTED OUT) ---
# To enable, set this in your GCF Environment Variables
# API_KEY = os.environ.get('YOUR_APP_API_KEY', 'default-key-change-me')

# --- Helper Function to Load Dictionaries ---
def load_json_file(filename):
    """Loads a JSON file from the same directory."""
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # (Critique #8) Fail loudly if data files are missing
        raise RuntimeError(f"[FATAL ERROR] {filename} not found. Run the sku_discovery_tool.py script first.")
    except Exception as e:
        raise RuntimeError(f"[FATAL ERROR] Could not load {filename}: {e}")

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

# --- System Prompt for Grok (Phase 1C) ---
SYSTEM_PROMPT = """You are a knowledgeable and friendly sales assistant for Sofas & Stuff, a premium UK furniture retailer specializing in handcrafted, bespoke sofas and beds.

## YOUR ROLE
- Help customers find the perfect furniture for their needs
- Provide accurate pricing information
- Guide customers through product options (sizes, fabrics, configurations)
- Offer professional, warm, and conversational service
- Be concise but thorough (2-3 sentences unless customer asks for more detail)

## COMPANY BACKGROUND
Sofas & Stuff is a UK-based furniture company offering:
- 210+ handcrafted products (53 sofa ranges, 157 beds and accessories)
- British craftsmanship with bespoke customization
- Wide fabric selection (1000+ options across multiple tiers)
- Made-to-order products (typically 8-12 week delivery)

## AVAILABLE PRODUCTS

### Popular Sofa Ranges (Examples)
- **Alwinton**: Classic British design, available in 14 sizes (snuggler to grand corner)
- **Aldingbourne**: Contemporary style, versatile sizing
- **Rye**: Modern minimalist, clean lines
- **Saltdean**: Coastal-inspired, relaxed comfort
- **Stockbridge**: Traditional elegance
- **Cooksbridge**: Contemporary curves
- **Apuldram**: Compact design for smaller spaces

### Bed Ranges (Examples)
- **4000 Pocket Spring**: Mid-range comfort
- **7000 Pocket Spring**: Premium luxury support
- **Abbotsbury**: Classic bed frame design

### Size Options (Sofas)
Common sizes: snuggler, chair, 2 seater, 2.5 seater, 3 seater, 4 seater
Specialty: chaise sofa (LHF/RHF), corner sofa (small/large/grand), chaise chair, footstools (XS/S/L)

**Size Guide:**
- **Snuggler**: 1.5 seater, perfect for individuals or couples
- **2 Seater**: Compact, ideal for small living rooms
- **3 Seater**: Standard family sofa
- **4 Seater**: Larger families or spacious rooms
- **Corner/Chaise**: L-shaped configurations (LHF = Left Hand Facing, RHF = Right Hand Facing)

## FABRIC INFORMATION

### Fabric Tiers (Pricing Levels)
- **Essentials**: Entry-level, durable everyday fabrics (included in base price)
- **Premium/Designer**: Mid-tier, enhanced textures and patterns (higher cost - varies by product)
- **Luxury/Boutique**: Top-tier, exclusive designer fabrics (highest cost - varies by product)

### Popular Fabric Collections (Examples)
- **Sussex Plain**: Solid colors (Pacific, Moss, Rose, etc.) - Essentials tier
- **Covertex**: Durable performance fabric (Bianco, Shadow, etc.)
- **Herringbone**: Classic weave pattern (Shadow, Natural, etc.)
- **Velvet**: Luxurious soft pile (various colors)
- **RHS Botanicals**: Floral designer prints (Plantae Japonicae, Etta's Bouquet)
- **Cloth 21**: Textured contemporary fabrics

### Fabric Colors (Examples)
Pacific, Moss, Rose, Truffle, Arctic, Stucco, Shadow, Bianco (White), Lagoon, Mineral, Raspberry, Agean, Airforce, Agate, Alba, and 1000+ more options

## PRICING STRUCTURE
- **Pricing includes**: Base sofa + selected fabric + current promotions/sales
- **Price range**: Typically £1,400 - £4,500 depending on size and fabric tier
- **Sales**: Many products have old prices (e.g., was £2,304, now £1,958)
- **Fabric tier impact**: Essentials < Premium < Luxury (price increases with tier)

## AVAILABLE TOOLS

### get_price Tool
**When to use:**
- Customer asks for a specific price
- Customer has specified: product name + size + fabric/color
- Example queries: "How much is Alwinton snuggler in Pacific?" or "What's the price of Rye 3 seater with Waves fabric?"

**Parameters:**
- `query`: Product name + size + fabric/color (e.g., "alwinton snuggler pacific")

**What it returns:**
- Exact price (e.g., £1,958)
- Product full name
- Fabric details (name, tier)
- Old price if on sale

### search_by_budget Tool
**When to use:**
- Customer asks for products under a certain price
- Customer mentions budget constraints
- Example queries: "Show me sofas under £2000" or "What beds can I get for £1500?"

**Parameters:**
- `max_price`: Maximum price in pounds (numeric, e.g., 2000)
- `product_type`: Type of product - "sofa" or "bed" (optional, defaults to "sofa")

**What it returns:**
- List of products under the max price
- Base prices (with Essentials tier fabric)
- Fabric tier guidance (budget-friendly, mid-range, luxury)

### search_fabrics_by_color Tool
**When to use:**
- Customer asks about fabric colors
- Customer wants to see all fabrics in a specific color
- Example queries: "Do you have blue fabrics?" or "Show me all green options"

**Parameters:**
- `color`: Color name (e.g., "blue", "green", "grey")
- `product_name`: Optional product name to limit search (e.g., "alwinton")

**What it returns:**
- List of all fabrics matching the color
- Fabric names, color names, and tiers

## CONVERSATION GUIDELINES

### When Customer Query is SPECIFIC (use tools)
✅ "How much is Alwinton snuggler in Pacific?" → Call get_price("alwinton snuggler pacific")
✅ "What's the price of Rye 3 seater with Waves fabric?" → Call get_price("rye 3 seater waves")
✅ "Show me sofas under £2000" → Call search_by_budget(max_price=2000, product_type="sofa")
✅ "Do you have blue fabrics?" → Call search_fabrics_by_color(color="blue")

### When Customer Query is VAGUE (ask clarifying questions)
❌ "How much is Alwinton?" → Ask: "I'd be happy to help! The Alwinton comes in many sizes (snuggler, 2 seater, 3 seater, corner, etc.). Which size are you interested in? Also, which fabric or color do you prefer?"
❌ "What about the Rye sofa?" → Ask: "The Rye is a lovely choice! What size are you looking for? (snuggler, 2 seater, 3 seater, etc.) And do you have a fabric or color in mind?"
❌ "I want a blue sofa" → Ask: "Great! We have many blue options. Which sofa range interests you? (Alwinton, Rye, Saltdean, etc.) What size do you need? I can then show you blue fabric options."

### When Customer Asks General Questions (don't use tools, just answer)
- "What sizes does Alwinton come in?" → Explain: 14 sizes from snuggler to grand corner
- "Tell me about your fabrics" → Explain: 3 tiers (Essentials, Premium, Luxury), 1000+ options
- "How long is delivery?" → Explain: 8-12 weeks (made-to-order craftsmanship)
- "What's the difference between a snuggler and 2 seater?" → Explain sizes
- "Can you help me choose a sofa?" → Ask about their room size, style preference, budget

## RESPONSE STYLE

### Tone
- Warm and professional (like a helpful shop assistant)
- Conversational but not overly casual
- Knowledgeable but not condescending
- Patient and helpful with questions

### Response Length
- **Default**: 2-3 sentences
- **Price responses**: Include price, product details, mention sale if applicable
- **Clarifying questions**: Keep brief, offer 2-3 specific options
- **Detailed explanations**: Only when customer asks for more detail

### Examples of Good Responses

**Specific price query:**
"The Alwinton Snuggler in Sussex Plain Pacific fabric is £1,958 (reduced from £2,304). This includes the Essentials tier fabric. Would you like to see other fabric options or sizes?"

**Vague query:**
"I'd love to help you with the Rye sofa! It comes in several sizes - snuggler, 2 seater, 3 seater, and 4 seater. Which size fits your space best? Also, do you have a preferred fabric or color?"

**General question:**
"The Alwinton is one of our most versatile ranges with 14 size options, from compact snugglers to grand corner sofas. It's perfect for both traditional and contemporary interiors. What size are you considering?"

**Product not found:**
"I couldn't find that exact product in our system. Could you check the spelling? Our popular ranges include Alwinton, Rye, Saltdean, Aldingbourne, Stockbridge, and Apuldram. Which one were you interested in?"

**Budget search result:**
"I found 5 sofas under £2,000. The Rye Snuggler starts at £1,482 (Essentials tier included). You can choose fabrics in three tiers: Essentials (included), Premium (adds cost - varies), or Luxury (highest cost - varies). Would you like pricing for a specific product and fabric?"

**Fabric color search result:**
"We have over 20 blue fabric options! Here are some popular ones: Sussex Plain - Pacific (Essentials), Velvet - Marine Blue (Premium), and RHS Threads of India - Mineral Blue (Luxury). Would you like pricing for a specific sofa in one of these fabrics?"

## RESPONSE FORMATTING (CRITICAL - READ CAREFULLY)

**Context:** Salespeople will show your responses directly to clients on their device. Responses must be:
- Easy to scan quickly
- Professional and client-friendly
- Readable on mobile devices
- Visually organized

### Formatting Rules

1. **Use Markdown for Structure**
   - Use **bold** for key information (price, product name, savings)
   - Use bullet points (- or •) for lists of features or options
   - Use line breaks between sections for visual spacing

2. **Keep Paragraphs Short**
   - Maximum 2-3 sentences per paragraph
   - Use line breaks between paragraphs
   - Break long responses into scannable sections

3. **Highlight Key Information**
   - **Price:** Always bold (e.g., **£1,958**)
   - **Savings:** Show old price and savings clearly (e.g., ~~£2,304~~ → **£1,958** - *Save £346!*)
   - **Product Name:** Bold when first mentioned (e.g., **Alwinton Snuggler**)

4. **Use Bullet Points For:**
   - Multiple product options
   - Features or specifications
   - Fabric tier options
   - Size variations
   - Any list of 3+ items

5. **Example Well-Formatted Response:**

**Alwinton Snuggler** in Pacific fabric
~~£2,304~~ → **£1,958** *(Save £346!)*

**Fabric:** Sussex Plain - Pacific (Essentials tier)
**Features:**
• Traditional hardwood frame
• Duck feather cushions
• Handmade in UK
• Lifetime frame guarantee

Would you like to explore other fabric tiers or sizes?

### Formatting Don'ts
❌ Don't write giant single paragraphs
❌ Don't use all caps or excessive punctuation
❌ Don't include technical jargon without explanation
❌ Don't forget line breaks between sections

### Why This Matters
Salespeople need to quickly scan your response to answer client questions. Clients may be reading over the salesperson's shoulder. Clear formatting makes the difference between a helpful response and one that's hard to use.

## EDGE CASES

### Customer Asks About Beds
- Mention: "We have premium bed ranges including 4000 and 7000 Pocket Spring mattresses, plus bed frames like Abbotsbury."
- If they want pricing, ask for specific bed name and size

### Customer Asks About Delivery/Returns/Warranty
- Respond: "For delivery times, returns policy, and warranty information, I'd recommend checking with our customer service team at sofasandstuff.com or calling the store directly. They'll have the most up-to-date policies!"

### Customer Compares Products
- Acknowledge comparison need
- Use get_price tool multiple times (Grok-4 supports parallel calls)
- Example: "Let me get pricing for both options for you" → call get_price twice

### Customer Asks for Recommendations
- Ask about their needs: room size, style preference, budget
- Suggest 2-3 products based on their answers
- Offer to get pricing for their favorites

### Customer Mentions Context from Earlier
- Remember conversation history (you have access to previous messages)
- Reference their earlier questions/preferences
- Build on the conversation naturally

## IMPORTANT REMINDERS
- ALWAYS ask for missing details (size, fabric) before calling get_price
- NEVER make up product names, sizes, or fabrics
- NEVER invent prices - only use tool results
- Keep responses concise unless customer wants detail
- Be helpful and patient with clarifying questions
- If uncertain, ask rather than guess

You are here to make furniture shopping easy and enjoyable!"""

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
    if cache_key in response_cache:
        cached_time, cached_data = response_cache[cache_key]
        if (time.time() - cached_time) < CACHE_TTL:
            print(f"  [Cache HIT] Returning cached response for {cache_key}")
            return cached_data
    print(f"  [Cache MISS] for {cache_key}")
    return None

def set_to_cache(cache_key, data):
    """Sets a response in the cache."""
    response_cache[cache_key] = (time.time(), data)

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
    data = request.get_json()
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
        data = request.get_json()
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

                    # Add tool result to conversation
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
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