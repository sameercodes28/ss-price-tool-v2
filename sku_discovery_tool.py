import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fuzzywuzzy import process # For cleaning up keywords
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry # (Critique #1) Correct import

# --- Color Codes for Beautiful Logging ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(100)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 100}{Colors.END}\n")

def log_section(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 100}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'─' * 100}{Colors.END}")

def log_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def log_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def log_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def log_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def log_data(label, value):
    """Data field logging"""
    print(f"   {Colors.CYAN}{label}:{Colors.END} {value}")

# --- Setup: Session with Retries (Critique #6 Fix) ---
# We need this for the hundreds of API calls
session = requests.Session()
retry_strategy = Retry(
    total=5,                # More retries for a long-running scraper
    backoff_factor=1,       # Time to wait (1s, 2s, 4s, 8s, 16s)
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST", "GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# --- Config ---
BASE_URL = "https://sofasandstuff.com"
# API endpoints we discovered
FABRIC_API_URL = "https://sofasandstuff.com/ProductExtend/GetPDPFabrics"
# Headers to make us look like a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}
# Product categories to scrape (from website navigation) - ALL URLs TESTED
CATEGORIES = {
    "sofa": "/3-seater-sofas",              # ✅ Tested 2025-01
    "corner_sofa": "/corner-sofas",         # ✅ Tested 2025-01
    "snuggler": "/snuggler-sofa",           # ✅ Tested 2025-01
    "chaise_sofa": "/chaise-sofas",         # ✅ Confirmed 2025-01
    "sofa_bed": "/sofa-beds",               # ✅ Tested 2025-01
    "chair": "/armchairs",                  # ✅ Confirmed 2025-01
    "footstool": "/footstools",             # ✅ Tested 2025-01
    "dog_bed": "/bespoke-dog-beds",         # ✅ Tested 2025-01
    # Beds (by size - no /beds endpoint exists)
    "bed_super_king": "/super-king-bed",    # ✅ User provided 2025-01
    "bed_king": "/king-size-bed",           # ✅ User provided 2025-01
    "bed_double": "/double-bed",            # ✅ User provided 2025-01
    "bed_single": "/single-bed",            # ✅ User provided 2025-01
    # Mattresses (new product type)
    "mattress_super_king": "/super-king-mattress",  # ✅ User provided 2025-01
    "mattress_king": "/king-mattress",              # ✅ User provided 2025-01
    "mattress_double": "/double-mattress",          # ✅ User provided 2025-01
    "mattress_single": "/single-mattress"           # ✅ User provided 2025-01
}

# --- Helper Functions ---

def clean_keyword(name):
    """Removes junk and returns a clean keyword."""
    name = re.sub(r'\(.*\)', '', name) # Remove (anything in parens)
    name = name.strip().lower()
    return name

def extract_mattress_tensions(prod_soup):
    """
    Extract tension/firmness options for mattresses.
    FIXED: Reads from tension dropdown button and data-coversku attributes.
    Returns dict like: {'firm': 'fir', 'medium': 'med', 'extra firm': 'exf', 'soft': 'sft'}
    """
    tensions = {}
    
    # Strategy 1: Look for tension dropdown button (div.btn-tension-modal)
    tension_button = prod_soup.find('div', class_='btn-tension-modal')
    
    if tension_button:
        # Find associated dropdown menu
        dropdown_menu = prod_soup.find('div', class_='dropdown-menu', attrs={'aria-labelledby': 'dropdownMenuButton'})
        
        if dropdown_menu:
            dropdown_items = dropdown_menu.find_all('a', class_='dropdown-item')
            
            for item in dropdown_items:
                # Read SKU from data-coversku attribute
                tension_sku = item.get('data-coversku', '').strip().lower()
                tension_text = item.get_text(strip=True)
                
                if not tension_sku or not tension_text:
                    continue
                
                # Clean keyword
                keyword = clean_keyword(tension_text)
                
                # Store both keyword and SKU
                tensions[keyword] = tension_sku
                if tension_sku not in tensions:
                    tensions[tension_sku] = tension_sku
    
    # Strategy 2: Fallback - check size modal for SKUs
    if not tensions:
        size_modal = prod_soup.select_one("#size-change-modal")
        if size_modal:
            links = size_modal.select('a.product[href]')
            seen_skus = set()
            for link in links:
                href = link.get('href', '')
                sku_match = re.search(r'sku=([a-z]+)', href, re.IGNORECASE)
                if sku_match:
                    full_sku = sku_match.group(1).lower()
                    
                    # Check for all known tension codes
                    for tension_code in ['fir', 'med', 'sof', 'ext', 'exf', 'sft']:
                        if tension_code in full_sku and tension_code not in seen_skus:
                            seen_skus.add(tension_code)
                            
                            name_map = {
                                'fir': 'firm',
                                'med': 'medium',
                                'sof': 'soft',
                                'sft': 'soft',
                                'ext': 'extra firm',
                                'exf': 'extra firm'
                            }
                            
                            tension_name = name_map.get(tension_code, tension_code)
                            tensions[tension_name] = tension_code
                            tensions[tension_code] = tension_code
    
    return tensions

def get_soup(url):
    """Gets a BeautifulSoup object from a URL."""
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to get soup from {url}: {e}")
        return None

def find_products(soup, product_type):
    """Finds all product links on a category page."""
    products = []
    # This class name is the key to finding products
    product_items = soup.select('div.product-item') 
    
    for item in product_items:
        # The actual structure: <div.product-picture> -> <a> -> <img>
        a_tag = item.select_one('div.product-picture a[href]')
        if a_tag and a_tag.get('href'):
            # Get product name from image alt/title attribute
            img_tag = a_tag.select_one('img')
            full_name = ""
            if img_tag:
                full_name = img_tag.get('alt', img_tag.get('title', '')).strip()
            
            if not full_name:
                # Skip if we can't get a product name
                continue
                
            url_path = a_tag['href']
            
            # Use fuzzy matching to clean up product names vs. keywords
            # e.g., "Alwinton Sofa" vs "Alwinton"
            name_parts = clean_keyword(full_name).split()
            if not name_parts:
                # Skip products with no valid name
                continue
            base_name = name_parts[0]
            
            # (Critique #8 Fix) Create specific keywords for multi-word types
            final_keyword = ""
            product_name_lower = full_name.lower()
            
            # Normalize product types
            normalized_type = product_type
            if product_type.startswith("bed_"):
                normalized_type = "bed"
            elif product_type.startswith("mattress_"):
                normalized_type = "mattress"
            elif product_type == "sofa_bed" or "sofa bed" in product_name_lower:
                final_keyword = "sofa bed"
                normalized_type = "sofa_bed"
            elif product_type == "dog_bed" or "dog bed" in product_name_lower:
                final_keyword = "dog bed"
                normalized_type = "dog_bed"
            
            # If we haven't set a keyword yet, use the base name
            if not final_keyword:
                final_keyword = base_name # "alwinton", "arles"
            
            # Handle cases where the keyword might just be the type
            if final_keyword in ["sofa", "chair", "bed", "footstool", "mattress"]:
                 final_keyword = f"{product_name_lower} {normalized_type}"
            
            products.append({
                "keyword": final_keyword,
                "full_name": full_name,
                "url": url_path,
                "type": normalized_type  # Use normalized type (bed, mattress, etc.) not category key
            })
    return products

def discover_sizes_and_covers(product_soup):
    """
    Extract both sizes AND covers from the size-change-modal.
    Each <a class="product"> link has both data-sizesku AND data-coversku.
    Returns: (sizes_dict, covers_dict)
    """
    sizes = {}
    covers = {}
    
    # Look for the size modal
    modal = product_soup.select_one("#size-change-modal")
    if not modal:
        print(f"    [WARN] No size modal '#size-change-modal' found.")
        return sizes, covers
    
    # Find all product links inside the modal
    product_links = modal.select('a.product')
    if not product_links:
        print(f"    [WARN] No product links found in size modal.")
        return sizes, covers
    
    for link in product_links:
        size_sku = link.get('data-sizesku')
        cover_sku = link.get('data-coversku')
        
        # Get the name from <h6> tag or link text
        name_tag = link.select_one('h6')
        if name_tag:
            name = clean_keyword(name_tag.text)
        else:
            name = clean_keyword(link.text)
        
        # Add size
        if size_sku and name:
            sizes[name] = size_sku
            # Also add the SKU itself as a keyword
            if size_sku.lower() not in sizes:
                sizes[size_sku.lower()] = size_sku
        
        # Add cover (there might be duplicates, which is fine)
        if cover_sku:
            cover_name = "fitted" if cover_sku == "fit" else "loose" if cover_sku == "lse" else cover_sku
            if cover_name not in covers:
                covers[cover_name] = cover_sku
            if cover_sku.lower() not in covers:
                covers[cover_sku.lower()] = cover_sku
    
    return sizes, covers

def discover_fabrics_via_api(product_sku, size_sku, cover_sku):
    """
    Calls the GetPDPFabrics API to get all fabrics for one product.
    This is needed because fabrics are loaded dynamically via JavaScript,
    so they're not in the initial HTML that BeautifulSoup can see.
    
    Returns complete fabric data including:
    - Fabric and color SKUs
    - Fabric and color names
    - Collection/Tier (for pricing)
    - Swatch image URLs
    - Descriptions
    """
    fabric_map = {}
    payload = {
        'productSku': product_sku,  # FIXED: camelCase
        'sizeSku': size_sku,
        'coverSku': cover_sku
    }
    
    try:
        response = session.post(FABRIC_API_URL, data=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        fabrics = data.get('Value', {}).get('data', [])
        if not fabrics:
            return fabric_map
            
        for fabric in fabrics:
            color_name = clean_keyword(fabric.get('ColourName', ''))
            fabric_name = clean_keyword(fabric.get('FabricName', ''))
            
            if not color_name or not fabric.get('FabricSku') or not fabric.get('ColourSku'):
                continue

            # Complete fabric data structure
            fabric_data = {
                "fabric_sku": fabric.get('FabricSku'),
                "color_sku": fabric.get('ColourSku'),
                "fabric_name": fabric.get('FabricName'),  # Full name, not cleaned
                "color_name": fabric.get('ColourName'),    # Full name, not cleaned
                "collection": fabric.get('FabricCollectionName', 'Unknown'),
                "tier": fabric.get('FabricCollectionName', 'Unknown'),  # Tier = Collection for pricing
                "desc": fabric.get('ShortDescription', ''),
                "swatch_url": fabric.get('ColourImageUrl', ''),
                "full_image_url": fabric.get('FullImageUrl', ''),
                "fabric_id": fabric.get('FabricID', ''),
                "color_id": fabric.get('ColourID', ''),
            }
            
            # Add mapping for the color (lowercase keyword)
            if color_name not in fabric_map:
                fabric_map[color_name] = fabric_data
            
            # Add mapping for the fabric name (lowercase keyword)
            if fabric_name not in fabric_map:
                fabric_map[fabric_name] = fabric_data

        return fabric_map

    except requests.RequestException as e:
        print(f"    [ERROR] API call failed: {e}")
        return fabric_map
    except json.JSONDecodeError:
        print(f"    [ERROR] Failed to decode API response.")
        return fabric_map

def discover_fabrics_from_modal(product_soup):
    """
    Extract fabrics directly from the fabric modal HTML instead of calling the API.
    Much faster! Looks for <div class="colour-item"> with data attributes.
    """
    fabric_map = {}
    
    # The colour items might be deeply nested, so just search for them anywhere
    # They're unique enough that we don't need to specify a parent
    colour_items = product_soup.select('div.colour-item[data-fabricsku][data-coloursku]')
    
    if not colour_items:
        print(f"    [WARN] No colour items found on page.")
        return fabric_map
    
    for item in colour_items:
        fabric_sku = item.get('data-fabricsku')
        colour_sku = item.get('data-coloursku')
        fabric_name = item.get('data-fabricname', '')
        colour_name = item.get('data-colourname', '')
        
        if not fabric_sku or not colour_sku:
            continue
        
        # Clean up names
        fabric_name_clean = clean_keyword(fabric_name)
        colour_name_clean = clean_keyword(colour_name)
        
        # Get collection/tier info if available
        tier = item.get('data-fabriccollection', 'Unknown')
        
        fabric_data = {
            "fabric_sku": fabric_sku,
            "color_sku": colour_sku,
            "tier": tier,
            "desc": colour_name,  # Full name as description
            "swatch": ""  # We could extract image URL if needed
        }
        
        # Add mapping for the color name
        if colour_name_clean and colour_name_clean not in fabric_map:
            fabric_map[colour_name_clean] = fabric_data
        
        # Add mapping for the fabric name
        if fabric_name_clean and fabric_name_clean not in fabric_map:
            fabric_map[fabric_name_clean] = fabric_data
    
    return fabric_map


# --- Main Scraper Logic ---
def main():
    log_header("SOFAS & STUFF COMPLETE SCRAPER")
    log_info(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_info("This will scrape ALL products with complete data")
    log_info("Expected duration: 20-30 minutes\n")
    
    # Final dictionaries to be saved
    all_products = {}
    all_sizes = {}
    all_covers = {}
    all_fabrics = {}
    
    product_url_set = set() # To avoid duplicates
    
    # Statistics tracking
    stats = {
        'categories_scanned': 0,
        'products_found': 0,
        'products_processed': 0,
        'products_complete': 0,
        'sizes_found': 0,
        'fabrics_found': 0,
        'api_calls': 0,
        'api_failures': 0,
    }
    
    log_header("PHASE 1: DISCOVERING PRODUCTS")
    
    for product_type, category_path in CATEGORIES.items():
        url = urljoin(BASE_URL, category_path)
        log_section(f"Category: {product_type}")
        log_info(f"URL: {url}")
        
        soup = get_soup(url)
        if not soup:
            log_error(f"Failed to fetch category page")
            continue
        
        stats['categories_scanned'] += 1
        products_on_page = find_products(soup, product_type)
        category_count = len(products_on_page)
        stats['products_found'] += category_count
        
        log_success(f"Found {category_count} products")
        
        for prod in products_on_page:
            if prod["url"] not in product_url_set:
                product_url_set.add(prod["url"])
                # We use the first word as the primary lookup key
                key = prod["keyword"]
                if key in all_products:
                    # Handle keyword collisions (e.g. "Arles Sofa" and "Arles Bed")
                    # Use the normalized type from the product (bed, mattress, etc.)
                    key = f"{key} {prod['type']}"
                
                all_products[key] = {
                    "sku": "", # We'll find this in Phase 2
                    "url": prod["url"],
                    "full_name": prod["full_name"],
                    "type": prod["type"]
                }
        time.sleep(1.0) # Be polite
    
    log_section("Phase 1 Complete")
    log_info(f"📊 Categories scanned: {stats['categories_scanned']}")
    log_info(f"📊 Unique products found: {len(all_products)}")
    print()
    
    if len(all_products) == 0:
        log_error("FATAL: No products found!")
        return
            
    log_header(f"PHASE 2: EXTRACTING COMPLETE DATA ({len(all_products)} products)")
    log_info("This phase will take 20-30 minutes...")
    log_info("Extracting: SKU, Images, Prices, Sizes, Covers, Fabrics\n")
    
    for i, (keyword, prod) in enumerate(all_products.items()):
        
        full_url = urljoin(BASE_URL, prod["url"])
        log_section(f"Product {i+1}/{len(all_products)}: {prod['full_name'][:70]}")
        log_info(f"URL: {prod['url'][:70]}...")
        
        # Extract product SKU from the URL (more reliable than scraping the page!)
        # URL format: /Saltdean?sku=sal3sefitttpbis where "sal" is the product SKU
        sku_match = re.search(r'sku=([a-z]{3})', prod["url"], re.IGNORECASE)
        if sku_match:
            product_sku = sku_match.group(1).lower()
            prod["sku"] = product_sku
            log_success(f"SKU: {product_sku}")
        else:
            # Fallback: try to extract from page (less reliable - might get featured products)
            log_warning("No SKU in URL, attempting to scrape from page...")
            prod_soup = get_soup(full_url)
            if not prod_soup:
                log_error("Skipping product, could not fetch page")
                continue
                
            sku_tag = prod_soup.select_one('[data-basesku]')
            if sku_tag and sku_tag.get('data-basesku'):
                product_sku = sku_tag.get('data-basesku').strip().lower()
            else:
                sku_tag = prod_soup.select_one('[data-productsku]')
                if sku_tag and sku_tag.get('data-productsku'):
                    product_sku = sku_tag.get('data-productsku').strip().lower()
                    log_info("Using data-productsku as fallback")
                else:
                    log_error(f"Could not find SKU. Skipping.")
                    continue
            prod["sku"] = product_sku
            log_success(f"SKU from page: {product_sku}")
        
        # Now fetch the product page to get ALL data
        prod_soup = get_soup(full_url)
        if not prod_soup:
            log_error("Skipping product, could not fetch page")
            continue
        
        # Extract product images
        log_info("[1/5] Extracting product images...")
        main_image = None
        image_selectors = [
            'img.render-image',
            '.product-picture img',
            '[class*="product-image"]',
            'img[data-src]'
        ]
        
        for selector in image_selectors:
            img_tag = prod_soup.select_one(selector)
            if img_tag:
                main_image = img_tag.get('data-src') or img_tag.get('src')
                if main_image and 'loading.gif' not in main_image:
                    prod["main_image"] = main_image
                    log_data("Product image", main_image[:60] + "...")
                    break
        
        if not main_image:
            log_warning("No product image found")
        
        # Extract price from the page
        log_info("[2/5] Extracting price...")
        price = None
        price_selectors = ['.product-price .now', '.product-price', '[class*="price"]', '.now']
        
        for selector in price_selectors:
            price_tag = prod_soup.select_one(selector)
            if price_tag:
                price_text = price_tag.text.strip()
                # Extract number from price (e.g., "£2,707" -> "2707")
                price_match = re.search(r'£?([\d,]+)', price_text)
                if price_match:
                    price = price_match.group(1).replace(',', '')
                    prod["price"] = price
                    prod["price_display"] = price_text
                    log_data("Price", f"£{price}")
                    break
        
        if not price:
            log_warning("Could not find price")
            prod["price"] = None
        
        # 2. Find all Sizes AND Covers from the size modal
        log_info("[3/5] Extracting sizes and covers...")
        # Both are in the same modal as data attributes on each size option
        sizes, covers = discover_sizes_and_covers(prod_soup)
        
        if sizes:
            all_sizes[product_sku] = sizes
            log_data("Sizes", f"{len(sizes)} size options found")
            stats['sizes_found'] += 1
        
        if covers:
            all_covers[product_sku] = covers
            log_data("Covers", f"{len(covers)} cover types found")
            
        # 3. Get fabrics OR tensions (depending on product type)
        log_info("[4/5] Extracting fabrics/tensions...")
        
        # Mattresses have tensions (firmness), not fabrics
        if prod["type"] == "mattress":
            log_info("Mattress detected - extracting tensions instead of fabrics")
            tensions = extract_mattress_tensions(prod_soup)
            
            if tensions:
                all_fabrics[product_sku] = tensions  # Store under same key for simplicity
                log_data("Tensions", f"{len(tensions)} firmness options found")
                for tension_name, tension_sku in tensions.items():
                    log_info(f"   • {tension_name.title()}: {tension_sku}")
                stats['fabrics_found'] += 1
            else:
                log_warning("No tension options found for mattress")
                
        elif not sizes or not covers:
            log_warning("No sizes or covers found, cannot call fabric API")
        else:
            # Get the first available size and cover SKUs for the API call
            first_size_sku = next(iter(sizes.values()))
            first_cover_sku = next(iter(covers.values()))
            
            log_info(f"Calling API: product={product_sku}, size={first_size_sku}, cover={first_cover_sku}")
            fabrics = discover_fabrics_via_api(product_sku, first_size_sku, first_cover_sku)
            if fabrics:
                all_fabrics[product_sku] = fabrics
                log_data("Fabrics", f"{len(fabrics)} fabric options found")
                stats['fabrics_found'] += 1
            else:
                log_warning(f"No fabrics found for {product_sku}")
        
        # Data completeness check
        log_info("[5/5] Data completeness check...")
        has_sku = bool(prod.get("sku"))
        has_image = bool(prod.get("main_image"))
        has_price = bool(prod.get("price"))
        has_sizes = len(sizes) > 0
        has_fabrics_or_tensions = bool(all_fabrics.get(product_sku))
        
        completeness = sum([has_sku, has_image, has_price, has_sizes, has_fabrics_or_tensions])
        completeness_pct = (completeness / 5) * 100
        
        if completeness == 5:
            log_success(f"100% Complete - All data present!")
            stats['products_complete'] += 1
        elif completeness >= 4:
            log_warning(f"{completeness_pct:.0f}% Complete - Minor issues")
        else:
            log_error(f"{completeness_pct:.0f}% Complete - Major issues")
            
        stats['products_processed'] += 1
            
        # Be extra polite since we're hitting their API
        time.sleep(1.0) 

    # --- Phase 3: Saving all data to JSON files ---
    log_header("PHASE 3: SAVING DATA")
    log_info("Writing all data to JSON files...")
    
    try:
        with open("products.json", "w", encoding='utf-8') as f:
            json.dump(all_products, f, indent=4)
        log_success("Saved products.json")
        
        with open("sizes.json", "w", encoding='utf-8') as f:
            json.dump(all_sizes, f, indent=4)
        log_success("Saved sizes.json")
        
        with open("covers.json", "w", encoding='utf-8') as f:
            json.dump(all_covers, f, indent=4)
        log_success("Saved covers.json")
        
        with open("fabrics.json", "w", encoding='utf-8') as f:
            json.dump(all_fabrics, f, indent=4)
        log_success("Saved fabrics.json")
        
        # Print final statistics
        log_header("FINAL STATISTICS")
        log_data("Categories scanned", stats['categories_scanned'])
        log_data("Products found", stats['products_found'])
        log_data("Products processed", stats['products_processed'])
        log_data("Products 100% complete", stats['products_complete'])
        log_data("Sizes extracted", stats['sizes_found'])
        log_data("Fabrics extracted", stats['fabrics_found'])
        log_data("API calls made", stats['api_calls'])
        
        completeness_rate = (stats['products_complete'] / stats['products_processed'] * 100) if stats['products_processed'] > 0 else 0
        log_data("Completeness rate", f"{completeness_rate:.1f}%")
        
        log_success("\n🎉 All files saved! You are ready to deploy your price calculator!")
        
    except Exception as e:
        log_error(f"Failed to write JSON files: {e}")

if __name__ == "__main__":
    main()