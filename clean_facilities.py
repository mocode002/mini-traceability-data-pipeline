import json
import csv
import logging
import os
import hashlib
import re

# --- Configuration ---
INPUT_FILE = "raw_oar_data.json"
OUTPUT_FACILITIES = "cleaned_facilities.csv"
OUTPUT_RELATION = "company_facilities.csv"

# --- Reusing Logic from Phase 2 for Consistency ---
# In a production environment, these would be in a shared 'utils.py' module.
# We include them here to ensure this file can run standalone.

LEGAL_SUFFIXES = [
    r"\bS\.?A\.?\b", r"\bS\.?R\.?L\.?\b", r"\bLtd\.?\b", r"\bInc\.?\b", 
    r"\bCo\.?\b", r"\bB\.?V\.?\b", r"\bGmbH\b", r"\bSpA\b", r"\bCorp\.?\b",
    r"\bLLC\b", r"\bLimited\b", r"\bS\.?L\.?\b"
]

def clean_name(name):
    if not name: return "UNKNOWN"
    clean = name.upper().strip()
    for suffix in LEGAL_SUFFIXES:
        clean = re.sub(suffix, "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"[^\w\s]", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def generate_company_id(name, country):
    unique_string = f"{name}|{country}".encode('utf-8')
    return hashlib.md5(unique_string).hexdigest()[:12]

def clean_text(text):
    """Simple text cleaner for addresses and descriptions."""
    if not text:
        return ""
    return str(text).replace("\n", " ").replace("\r", "").strip()

def run():
    logging.info("--- Starting Phase 3: Facility Processing ---")
    
    if not os.path.exists(INPUT_FILE):
        logging.error(f"Input file {INPUT_FILE} not found. Run Phase 1 first.")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        logging.info(f"Loaded {len(raw_data)} raw records for processing.")
        
        facilities = []
        company_facility_links = []
        
        # Track seen IDs to prevent duplicate facility entries if raw data has overlap
        seen_facility_ids = set()

        for record in raw_data:
            # 1. Extract Basic Info
            raw_name = record.get("name", "")
            country = record.get("country_name", "Unknown").strip().title()
            address = clean_text(record.get("address", ""))
            
            # 2. Identify/Generate Facility ID
            # Ideally use the OAR ID (os_id). If missing, generate a hash.
            facility_id = record.get("os_id")
            if not facility_id:
                # Fallback ID generation
                f_str = f"{raw_name}|{address}|{country}".encode('utf-8')
                facility_id = "GEN-" + hashlib.md5(f_str).hexdigest()[:8]
            
            if facility_id in seen_facility_ids:
                continue
            seen_facility_ids.add(facility_id)

            # 3. Determine Parent Company ID
            # We apply the EXACT same logic as Phase 2 to ensure the IDs match.
            cleaned_comp_name = clean_name(raw_name)
            company_id = generate_company_id(cleaned_comp_name, country)
            
            # 4. Prepare Records
            
            # Facility Record
            facilities.append({
                "facility_id": facility_id,
                "name": clean_text(raw_name),
                "address": address,
                "country": country
            })
            
            # Link Record (Many-to-Many potential, but here it's effectively 1-to-1 or Many-to-1)
            company_facility_links.append({
                "company_id": company_id,
                "facility_id": facility_id
            })

        # 5. Save Facilities Table
        logging.info(f"Saving {len(facilities)} facilities...")
        with open(OUTPUT_FACILITIES, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["facility_id", "name", "address", "country"])
            writer.writeheader()
            writer.writerows(facilities)

        # 6. Save Link Table
        logging.info(f"Saving {len(company_facility_links)} relational links...")
        with open(OUTPUT_RELATION, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["company_id", "facility_id"])
            writer.writeheader()
            writer.writerows(company_facility_links)
            
        logging.info("Phase 3 completed successfully.")

    except Exception as e:
        logging.error(f"Error in Phase 3: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()