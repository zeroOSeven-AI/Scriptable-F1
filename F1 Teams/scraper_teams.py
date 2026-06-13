import os
import json
import requests

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Teams"
LOGOS_FOLDER = os.path.join(BASE_DIR, "logos")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "teams_link.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# ENVIRONMENT & UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders."""
    os.makedirs(LOGOS_FOLDER, exist_ok=True)
    print(f"[INFO] Storage directory checked/created at: {LOGOS_FOLDER}")

def load_team_links():
    """Loads raw team logo links from JSON config."""
    if not os.path.exists(LINKS_JSON_PATH):
        print(f"[ERROR] Source file missing: {LINKS_JSON_PATH}")
        return {}
    
    try:
        with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("team_logos", data)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON configuration: {e}")
        return {}

def upgrade_url_to_600x600(url):
    """Upgrades the F1 CDN URL from 64px height to a high-res 600x600 center-cropped canvas."""
    if "c_fit,h_64" in url:
        return url.replace("c_fit,h_64", "c_fill,g_center,w_600,h_600")
    return url

def download_binary_file(url, destination_path):
    """Downloads the team logo asset."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        print(f"[ERROR] Failed to download: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error during download: {e}")
    return False

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_team_pipeline():
    """Main execution orchestrator for the team logo pipeline."""
    initialize_environment()
    raw_links = load_team_links()
    
    if not raw_links:
        print(f"[FINISHED] No team links found to process.")
        return

    print(f"\n[PIPELINE] Processing {len(raw_links)} team logos to high-res 600x600...")
    for team_key, logo_url in raw_links.items():
        # Nadogradi link na visoku rezoluciju prije skidanja
        high_res_url = upgrade_url_to_600x600(logo_url)
        
        filename = f"{team_key}.webp"
        full_dest_path = os.path.join(LOGOS_FOLDER, filename)
        
        print(f"[PROCESSING] Fetching Logo: {team_key} -> {filename}")
        download_binary_file(high_res_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 TEAM LOGO HIGH-RES PIPELINE v2")
    print("==========================================")
    run_team_pipeline()
    print("==========================================")
