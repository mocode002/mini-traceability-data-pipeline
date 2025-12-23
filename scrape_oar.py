import requests
import json
import logging
import time
import random
import os
import csv
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("OAR_API_KEY")
BASE_URL = "https://opensupplyhub.org/api/facilities/"
TARGET_COUNTRIES = ["Morocco", "Spain", "Portugal", "Italy", "France", "Greece", "Malta"]
MIN_RECORDS = 3000 # minimum number of records to fetch (set to 10000 for real API)
OUTPUT_FILE = "raw_oar_data.json"
SOURCE_CSV = "source_oar_data.csv"

# Set this to False if you have a real API Key and want to hit the live server
MOCK_MODE = True 

def fetch_from_api():
    """
    Attempts to fetch real data from the Open Supply Hub API.
    Requires a valid API Token.
    """
    headers = {"Authorization": f"Token {API_KEY}"}
    all_facilities = []
    
    logging.info(f"Starting API scrape for countries: {TARGET_COUNTRIES}")

    for country in TARGET_COUNTRIES:
        logging.info(f"Fetching data for country: {country}")
        page = 1
        country_count = 0
        
        while True:
            try:
                params = {
                    "country_name": country,
                    "page": page,
                    "pageSize": 50  # Max is often 50 for detail=false
                }
                
                response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    logging.error(f"Failed to fetch {country} page {page}: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                all_facilities.extend(results)
                country_count += len(results)
                logging.info(f"Fetched {len(results)} records from {country} (Page {page})")
                
                # Check pagination (next page existence)
                if not data.get('next'):
                    break
                    
                page += 1
                time.sleep(0.5) # Respect rate limits

            except Exception as e:
                logging.error(f"Error scraping {country}: {e}")
                break
        
        logging.info(f"Finished {country}: {country_count} records collected.")

    return all_facilities

def generate_mock_data():
    """
    Generates realistic dummy data to simulate the OAR dataset 
    so the pipeline can be tested without an API key.
    """
    logging.info("MOCK_MODE is ON. Generating synthetic data...")
    fake_data = []
    
    # Text fragments to build realistic names
    prefixes = ["Royal", "Global", "Eco", "Tex", "Fashion", "Blue", "Sustainable", "Urban", "Cotton"]
    suffixes = ["Textiles", "Garments", "Apparel", "Fabrics", "Manufacturing", "Mills", "Creations", "S.A.", "Ltd.", "S.R.L."]
    
    cities = {
        "Morocco": ["Casablanca", "Tangier", "Marrakech"],
        "Spain": ["Barcelona", "Madrid", "Valencia"],
        "Portugal": ["Porto", "Lisbon", "Braga"],
        "Italy": ["Milan", "Florence", "Prato"],
        "France": ["Paris", "Lyon", "Lille"],
        "Greece": ["Athens", "Thessaloniki"],
        "Malta": ["Valletta", "Birkirkara"]
    }

    # Generate slightly more than 10,000 to ensure we meet the requirement
    total_records = MIN_RECORDS + 500
    
    for i in range(total_records):
        country = random.choice(TARGET_COUNTRIES)
        city = random.choice(cities[country])
        
        name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
        # Add some "dirty" data occasionally to test the cleaning phase
        if random.random() < 0.1:
            name = name.upper() + "..."
        
        facility = {
            "os_id": f"CN{random.randint(100000, 999999)}",
            "name": name,
            "address": f"{random.randint(1, 999)} Industrial Zone, {city}",
            "country_name": country,
            "properties": {
                "description": "Manufacturer of cotton apparel." if random.random() > 0.5 else "Sustainable denim production."
            }
        }
        fake_data.append(facility)
    
    logging.info(f"Generated {len(fake_data)} mock records.")
    return fake_data



def process_local_csv():
    """Reads a local CSV, filters by country, and returns the data."""
    if not os.path.exists(SOURCE_CSV):
        logging.error(f"Source file '{SOURCE_CSV}' not found.")
        logging.info("Please download the CSV from Open Supply Hub and rename it.")
        return []

    extracted_data = []
    logging.info(f"Reading local file: {SOURCE_CSV}...")

    try:
        with open(SOURCE_CSV, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # OAR CSV headers might vary slightly, usually 'country_name' or 'country'
                # We try to find the country safely
                row_country = row.get("country_name") or row.get("country") or ""
                
                # specific normalization to match our list
                if row_country.strip() in TARGET_COUNTRIES:
                    # Keep the record
                    extracted_data.append(row)
                    
                    # Stop if we have huge amounts of data (e.g. 50k) to save time
                    if len(extracted_data) >= 50000: break

        logging.info(f"Filtered {len(extracted_data)} facilities from target countries.")
        return extracted_data

    except Exception as e:
        logging.error(f"Failed to read CSV: {e}")
        return []


def run():
    """
    Main entry point for the extraction phase.
    """
    logging.info("--- Starting Phase 1: Data Extraction ---")

    if os.path.exists(SOURCE_CSV):
        data = process_local_csv()
    else:
        if MOCK_MODE:
            data = generate_mock_data()
        else:
            data = fetch_from_api()
        
    # Validation
    if len(data) < MIN_RECORDS:
        logging.warning(f"Extracted {len(data)} records, which is below the target of {MIN_RECORDS}.")
    else:
        logging.info(f"Successfully extracted {len(data)} records.")

    # Save to file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Raw data saved to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Failed to save data: {e}")
        raise

if __name__ == "__main__":
    # Setup simple logging if running standalone
    logging.basicConfig(level=logging.INFO)
    run()