import json
import csv
import re
import hashlib
import logging
import os

# --- Configuration ---
INPUT_FILE = "raw_oar_data.json"
OUTPUT_FILE = "cleaned_companies.csv"

# Common legal suffixes to remove for cleaner names
LEGAL_SUFFIXES = [
    r"\bS\.?A\.?\b", r"\bS\.?R\.?L\.?\b", r"\bLtd\.?\b", r"\bInc\.?\b", 
    r"\bCo\.?\b", r"\bB\.?V\.?\b", r"\bGmbH\b", r"\bSpA\b", r"\bCorp\.?\b",
    r"\bLLC\b", r"\bLimited\b", r"\bS\.?L\.?\b"
]

def clean_name(name):
    """
    Normalizes company names by:
    1. Upper-casing
    2. Removing legal suffixes
    3. Removing punctuation and extra whitespace
    """
    if not name:
        return "UNKNOWN_COMPANY"
    
    # 1. Standardize case
    clean = name.upper().strip()
    
    # 2. Remove legal suffixes (using regex)
    for suffix in LEGAL_SUFFIXES:
        clean = re.sub(suffix, "", clean, flags=re.IGNORECASE)
    
    # 3. Remove punctuation (keep alphanumeric and spaces)
    clean = re.sub(r"[^\w\s]", "", clean)
    
    # 4. Collapse multiple spaces
    clean = re.sub(r"\s+", " ", clean).strip()
    
    return clean

def generate_company_id(name, country):
    """
    Generates a deterministic ID based on company name and country.
    Using MD5 is sufficient for this scope and ensures the same ID 
    is generated every time the script runs.
    """
    unique_string = f"{name}|{country}".encode('utf-8')
    return hashlib.md5(unique_string).hexdigest()[:12] # Shorten to 12 chars for readability

def run():
    logging.info("--- Starting Phase 2: Company Cleaning ---")
    
    if not os.path.exists(INPUT_FILE):
        logging.error(f"Input file {INPUT_FILE} not found. Run Phase 1 first.")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        logging.info(f"Loaded {len(raw_data)} raw records.")
        
        # Dictionary to handle deduplication: Key = (normalized_name, country)
        unique_companies = {}

        for record in raw_data:
            raw_name = record.get("name", "")
            country = record.get("country_name", "Unknown").strip().title() # Normalize country [cite: 48]
            
            cleaned_name = clean_name(raw_name)
            
            # Key for uniqueness
            comp_key = (cleaned_name, country)
            
            if comp_key not in unique_companies:
                # Generate ID
                comp_id = generate_company_id(cleaned_name, country)
                
                unique_companies[comp_key] = {
                    "company_id": comp_id,
                    "clean_name": cleaned_name,
                    "country": country,
                    "original_name_example": raw_name # Keep one original for reference
                }

        logging.info(f"identified {len(unique_companies)} unique companies from raw data.")

        # Save to CSV [cite: 50]
        fieldnames = ["company_id", "clean_name", "country", "original_name_example"]
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for comp in unique_companies.values():
                writer.writerow(comp)
                
        logging.info(f"Cleaned company table saved to {OUTPUT_FILE}")

    except Exception as e:
        logging.error(f"Error in Phase 2: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()