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

# --- Google Cloud Functions Entry Point (Critique #2, #9) ---
@functions_framework.http
def http_entry_point(request):
    """Cloud Functions entry point that routes requests."""
    
    # Handle CORS preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    # Handle the main /getPrice endpoint
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