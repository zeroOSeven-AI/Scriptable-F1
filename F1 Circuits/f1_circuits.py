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
# JSON & FILE UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders."""
    if not os.path.exists(CIRCUITS_FOLDER):
        os.makedirs(CIRCUITS_FOLDER)
        print(f"[INFO] Created circuits directory at: {CIRCUITS_FOLDER}")

def load_json_config():
    """Loads the entire configuration from the JSON file."""
    if not os.path.exists(LINKS_JSON_PATH):
        default_data = {
            "scraper_sources": {
                "circuits_page_2026": "https://www.formula1.com/en/racing/2026.html"
            },
            "direct_circuit_maps": {}
        }
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(LINKS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    
    try:
        with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON configuration: {e}")
        return {"scraper_sources": {}, "direct_circuit_maps": {}}

# ==========================================
# NETWORK & DOWNLOAD CORE
# ==========================================
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
# PARSING & SCRAPING LOGIC (FALLBACK)
# ==========================================
def scrape_fallback_maps(url):
    """Fallback parser to try and find maps from the main F1 HTML page."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted = []
        
        # Tražimo bilo koje slike koje sadrže riječ 'track' ili 'circuit' u linku
        for img in soup.find_all('img'):
            src = img.get('data-src') or img.get('src') or img.get('data-original')
            if src and ('track' in src or 'circuit' in src) and not src.endswith('.svg'):
                # Pokušavamo izvući ime staze iz samog URL-a slike
                filename_part = src.split('/')[-1].split('.')[0].lower()
                clean_name = filename_part.replace('2026track', '').replace('detailed', '')
                if not clean_name:
                    clean_name = "unknown_circuit"
                
                full_url = urljoin(url, src)
                extracted.append((clean_name, full_url))
        return extracted
    except Exception as e:
        print(f"[WARNING] Fallback scraper encountered an issue: {e}")
        return []

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_circuit_scraper_pipeline():
    """Main execution orchestrator for the circuit scraper."""
    initialize_environment()
    config = load_json_config()
    
    direct_maps = config.get("direct_circuit_maps", {})
    sources = config.get("scraper_sources", {})
    
    all_assets_to_download = {}

    # 1. FAZA: Učitaj fiksne linkove iz JSON-a (Ovo povlači tvoj novi link za Španjolsku!)
    if direct_maps:
        print(f"[PROCESS] Found {len(direct_maps)} direct map URLs in JSON.")
        for name, url in direct_maps.items():
            all_assets_to_download[name] = url

    # 2. FAZA: Pokreni scraper za ostale karte kao dodatak
    target_url = sources.get("circuits_page_2026")
    if target_url:
        print(f"[START] Running fallback scraper on: {target_url}")
        scraped_assets = scrape_fallback_maps(target_url)
        for name, url in scraped_assets:
            if name not in all_assets_to_download: # JSON ima prednost pred scraperom
                all_assets_to_download[name] = url

    # 3. FAZA: Preuzimanje slika na disk
    if not all_assets_to_download:
        print("[FINISHED] No circuit maps available to download.")
        return

    print(f"\n[DOWNLOAD] Starting download of {len(all_assets_to_download)} layouts...")
    for circuit_name, image_url in all_assets_to_download.items():
        # Ako je link .webp spremamo kao .webp, ako je .png kao .png
        ext = "webp" if "webp" in image_url.lower() else "png"
        filename = f"{circuit_name}.{ext}"
        full_dest_path = os.path.join(CIRCUITS_FOLDER, filename)
        
        print(f"[PROCESSING] Layout for: {circuit_name}")
        download_binary_file(image_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 CIRCUIT ASSET MANAGEMENT PIPELINE v2")
    print("==========================================")
    run_circuit_scraper_pipeline()
    print("==========================================")
