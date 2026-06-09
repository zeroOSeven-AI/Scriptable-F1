import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Setup headers to mimic a real browser browse
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"[INFO] Created folder: {folder_name}")

def download_image(url, folder, filename):
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        if response.status_code == 200:
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[SUCCESS] Downloaded: {filename}")
        else:
            print(f"[ERROR] Failed to download {filename} (Status code: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error downloading {filename}: {e}")

def scrape_f1_drivers():
    print("\n--- Scraping F1 Drivers ---")
    url = "https://www.formula1.com/en/drivers.html"
    folder = "f1_drivers"
    create_folder(folder)
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] Cannot access drivers page: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all driver containers (based on F1 website structure)
    drivers = soup.find_all('fieldset', class_='listing-item')
    
    if not drivers:
        # Fallback to alternative selector if layout changed slightly
        drivers = soup.select('.col-12 .listing-item')

    for driver in drivers:
        try:
            # Extract driver name
            first_name = driver.find('span', class_='fname').text.strip()
            last_name = driver.find('span', class_='lname').text.strip()
            driver_name = f"{first_name}_{last_name}".lower().replace(" ", "_")
            
            # Extract image URL
            img_tag = driver.find('img')
            if img_tag and 'src' in img_tag.attrs:
                img_url = img_tag['src']
                # Clean up URL if it's relative or has resizing parameters
                img_url = urljoin(url, img_url)
                
                filename = f"{driver_name}.png"
                download_image(img_url, folder, filename)
        except AttributeError:
            continue

def scrape_f1_circuits():
    print("\n--- Scraping F1 Circuits ---")
    url = "https://www.formula1.com/en/racing/2026.html" # Updated for the current 2026 season
    folder = "f1_circuits"
    create_folder(folder)
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] Cannot access circuits page: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all circuit cards
    circuits = soup.select('.event-item-wrapper')
    
    for circuit in circuits:
        try:
            # Extract country or circuit name
            country_tag = circuit.find('span', class_='event-place')
            if not country_tag:
                continue
                
            circuit_name = country_tag.text.strip().lower().replace(" ", "_")
            
            # Find the circuit outline image
            img_tag = circuit.find('img', class_='lazy') or circuit.find('img')
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src')
                if img_url:
                    img_url = urljoin(url, img_url)
                    filename = f"{circuit_name}.png"
                    download_image(img_url, folder, filename)
        except Exception as e:
            print(f"[WARNING] Skipping a circuit due to error: {e}")

if __name__ == "__main__":
    print("=== F1 Asset Downloader for Scriptable ===")
    scrape_f1_drivers()
    scrape_f1_circuits()
    print("\n=== Process Finished ===")
