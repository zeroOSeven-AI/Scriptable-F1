import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Circuits"
CIRCUITS_FOLDER = os.path.join(BASE_DIR, "circuits_2026")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "circuits_link.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# FILE & DIRECTORY UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders and configurations."""
    if not os.path.exists(CIRCUITS_FOLDER):
        os.makedirs(CIRCUITS_FOLDER)
        print(f"[INFO] Created circuits directory at: {CIRCUITS_FOLDER}")

def load_stored_links():
    """Loads backup/override links from JSON file if it exists."""
    if os.path.exists(LINKS_JSON_PATH):
        try:
            with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[WARNING] Error reading {LINKS_JSON_PATH}. Starting with empty links mapping.")
    return {}

def save_links_to_json(links_dict):
    """Saves scraped or manual layout links to JSON file for future reference."""
    try:
        # Merge with existing data if present
        existing_data = load_stored_links()
        existing_data.update(links_dict)
        
        with open(LINKS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Circuit links successfully mapped and saved to {LINKS_JSON_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to save links to JSON: {e}")

# ==========================================
# NETWORK & DOWNLOAD CORE
# ==========================================
def fetch_page_html(url):
    """Fetches the raw HTML content of a given URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.text
        print(f"[ERROR] HTTP Status {response.status_code} for URL: {url}")
    except Exception as e:
        print(f"[EXCEPTION] Failed to connect to {url}: {e}")
    return None

def download_binary_file(url, destination_path):
    """Downloads an asset (image/track map) and stores it locally."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[SUCCESS] Downloaded asset to: {destination_path}")
            return True
        print(f"[ERROR] Failed to download asset from {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error during asset download: {e}")
    return False

# ==========================================
# PARSING & SCRAPING LOGIC
# ==========================================
def parse_circuit_elements(html_content, base_url):
    """Parses circuit details and map image URLs from raw HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    circuit_data = {}
    
    # Target elements on the Formula 1 race calendar overview page
    elements = soup.select('.event-item-wrapper') or soup.find_all('fieldset', class_='listing-item')
    
    for element in elements:
        try:
            place_tag = element.find('span', class_='event-place')
            if not place_tag:
                continue
                
            circuit_name = place_tag.text.strip().lower().replace(" ", "_")
            
            img_tag = element.find('img', class_='lazy') or element.find('img')
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src')
                if img_url:
                    full_img_url = urljoin(base_url, img_url)
                    circuit_data[circuit_name] = full_img_url
        except Exception as e:
            print(f"[WARNING] Skipping a component during parsing due to error: {e}")
            
    return circuit_data

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_circuit_scraper_pipeline():
    """Main execution orchestrator for the circuit scraper."""
    initialize_environment()
    
    target_url = "https://www.formula1.com/en/racing/2026.html"
    print(f"[START] Fetching schedule data from: {target_url}")
    
    html = fetch_page_html(target_url)
    if not html:
        print("[ABORT] Could not retrieve schedule overview page. Checking local JSON as fallback...")
        scraped_links = load_stored_links()
    else:
        scraped_links = parse_circuit_elements(html, target_url)
        if scraped_links:
            save_links_to_json(scraped_links)
    
    if not scraped_links:
        print("[FINISHED] No circuit maps found to process.")
        return

    print(f"\n[PROCESS] Processing {len(scraped_links)} track layouts...")
    for circuit_name, image_url in scraped_links.items():
        filename = f"{circuit_name}.png"
        full_dest_path = os.path.join(CIRCUITS_FOLDER, filename)
        
        print(f"[DOWNLOAD] Retrieving layout for: {circuit_name}")
        download_binary_file(image_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 CIRCUIT ASSET MANAGEMENT PIPELINE")
    print("==========================================")
    run_circuit_scraper_pipeline()
    print("==========================================")
