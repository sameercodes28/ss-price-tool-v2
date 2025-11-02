Product Requirements Document (PRD)

S&S Voice Price Check Tool (v2.0.0-alpha - Experimental)





Project:

S&S Voice Price Check Tool - v2

Status:

🚧 Experimental / Development

Parent:

v1.0.0 (Live in Production at ~/Desktop/SS-1)

Author:

Gemini & Sameer

Goal:

Experimental version of the voice price lookup tool for testing new features and improvements. Forked from v1.0.0 stable release.

1. Executive Summary

This is v2 of the price lookup tool, forked from v1.0.0 for experimental development. The core 3-part architecture (Frontend -> Backend -> S&S API) is inherited from v1. This version is deployed separately from v1 with its own infrastructure (GitHub repo, GCF project, GitHub Pages) to allow safe experimentation without affecting the stable v1 production deployment.

2. Core Architecture (Validated)

Our system consists of three decoupled components:

Frontend App (index.html):

A static, single-page web app.

Uses browser's webkitSpeechRecognition (voice) and a text input (fallback).

Host: GitHub Pages (Free).

Function: Sends the user's text query to our Backend Translator.

Backend Translator (main.py):

A serverless function that acts as a smart, caching proxy.

Host: Google Cloud Functions (Free Tier).

Function: Receives simple text, translates it into a complex S&S API request, gets the S&S response, simplifies it, and sends it back to the frontend.

S&S Internal APIs (The Data Source):

The undocumented, internal APIs used by sofasandstuff.com.

We do not control this, we only call it.

3. The "Brain": Scraped Data Files

The "translation" is powered by four JSON files, generated once by our scraper:

products.json: Maps keywords (e.g., "alwinton") to product data (sku, type, url).

sizes.json: Nested map of product_sku -> size_keyword -> size_sku.

covers.json: Nested map of product_sku -> cover_keyword -> cover_sku.

fabrics.json: Nested map of product_sku -> fabric_keyword -> fabric_data_object.

4. The Core Logic: 2-API Routing (Validated)

Our backend's most important job is to know which S&S API to call. Our validation has confirmed this logic:

Product Type

API Endpoint

Payload Format

Response

sofa, chair, footstool, dog_bed, sofa_bed, snuggler

/ProductExtend/ChangeProductSize

Combined SKU String



(querySku: "alwsnufitsxppac")

Nested JSON



(Includes HeroImages)

bed

/Category/ProductPrice

Component SKU Parts



(productsku: "arl", sizesku: "skb"...)

Flat JSON



(No Images)

5. Key Features (Production v1.0.0)

Feature

Description

Voice Query

User can tap a mic to speak their query.

Text Query (Fallback)

User can type their query. (Critical for Firefox, etc.)

Real-Time Pricing

Price is fetched live from the S&S API. Includes active discounts.

Product Image Carousel

For sofas/chairs/stools, the app displays the product in the exact fabric chosen.

Specifications Display

Shows frame, cushions, feet, etc., pulled directly from the API.

Fabric Details

Shows fabric tier, composition, and swatch, pulled from our data files.

Ambiguity Handling

If a query is vague (e.g., "alwinton blue"), the backend returns a helpful error with suggestions (e.g., "Did you mean: pacific, waves, or sky?").

Query History

The frontend saves the last 5 queries to localStorage for quick access.

Robustness

Backend uses a 5-minute cache to reduce API spam and Retry logic to handle temporary server errors.

6. Key Deployment Requirements (CRITICAL)

HTTPS is Mandatory: The browser's Speech Recognition API will not work if the frontend is hosted on http://.

Solution: GitHub Pages provides https:// automatically. This is a solved problem.

Backend URL: The index.html file must be edited to point to the correct, deployed Google Cloud Function URL.

Data Files: The 4 .json files must be uploaded in the same directory as main.py when deploying to Google Cloud Functions.

7. Testing Strategy

Phase A: Local Backend Test

Run sku_discovery_tool.py to get the 4 .json files.

Run functions-framework --target=http_entry_point --debug.

Use curl (in a new terminal) to test all product types:

Sofa: curl -X POST ... -d '{"query": "alwinton 3 seater pacific"}'

Chair: curl -X POST ... -d '{"query": "snape chair waves"}'

Bed: curl -X POST ... -d '{"query": "arles super king biscuit"}'

Footstool: curl -X POST ... -d '{"query": "porthallow footstool pacific"}'

Ambiguity: curl -X POST ... -d '{"query": "alwinton blue"}' (Expect error)

Failure: curl -X POST ... -d '{"query": "blahblah"}' (Expect error)

Phase B: Live E2E Test

Deploy the full backend to Google Cloud.

Go to the live GitHub Pages URL.

Run all the same test queries from Phase A using both the microphone and the text input.

8. Maintenance Plan

Quarterly (or as needed): Re-run the sku_discovery_tool.py script locally to find new products, sizes, and fabrics.

Deploy: Re-deploy the Google Cloud Function by uploading the 4 new JSON files and the (unchanged) main.py and requirements.txt.

If it Breaks: If the S&S API changes, the app will fail. The developer must use browser Dev Tools to find the new API path/payload, update main.py, and re-deploy.

9. Browser Compatibility

Browser

Voice (Mic)

Text Input

Chrome (Desktop/Android)

✅ Yes

✅ Yes

Safari (Mac/iOS)

✅ Yes

✅ Yes

Edge (Chromium)

✅ Yes

✅ Yes

Firefox

❌ No

✅ Yes

Samsung Internet

❌ No

✅ Yes

10. Deployment Checklist (Full-Scale)

[ ] Local: Create/clear sofa-price-tool folder.

[ ] Local: Save all 7 project files (main.py, sku_discovery_tool.py, index.html, 2x requirements.txt, 2x PRD/Handoff docs).

[ ] Local (Terminal): cd sofa-price-tool

[ ] Local (Terminal): python3 -m venv venv

[ ] Local (Terminal): source venv/bin/activate

[ ] Local (Terminal): pip install -r requirements_scraper.txt

[ ] Local (Terminal): pip install -r requirements.txt

[ ] Local (Terminal): python3 sku_discovery_tool.py (Wait 30-60 mins).

[ ] Local (Terminal): Verify products.json, sizes.json, covers.json, fabrics.json were created.

[ ] Local (Terminal): gcloud functions deploy sofa-prototype-api ... (the full deploy command).

[ ] Local (Browser): Wait for deploy. Copy the final Google Cloud URL.

[ ] Local (Editor): Open index.html and paste the full Google Cloud URL (with /getPrice) into the BACKEND_API_URL variable.

[ ] Local (Terminal): Push the final, edited index.html to your GitHub repo's main branch.

[ ] Live (Browser): Open your github.io URL, wait 60s for the cache to clear, and test with new queries.