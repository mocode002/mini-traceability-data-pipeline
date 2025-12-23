import csv
import logging
import os

# --- Configuration ---
FILE_COMPANIES = "cleaned_companies.csv"
FILE_FACILITIES = "cleaned_facilities.csv"
FILE_LINKS = "company_facilities.csv"

def load_ids(filename, id_column):
    """
    Helper to load a set of IDs from a CSV file.
    Returns a set of strings.
    """
    if not os.path.exists(filename):
        logging.error(f"Missing file: {filename}")
        return set()
    
    ids = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if id_column in row and row[id_column]:
                    ids.add(row[id_column])
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")
    return ids

def run():
    logging.info("--- Starting Phase 4: Relational Structuring & Validation ---")
    
    # 1. Load all IDs into sets for O(1) lookup speed
    logging.info("Loading IDs from tables...")
    company_ids = load_ids(FILE_COMPANIES, "company_id")
    facility_ids = load_ids(FILE_FACILITIES, "facility_id")
    
    if not company_ids or not facility_ids:
        logging.error("Critical: Companies or Facilities tables are empty or missing.")
        return

    # 2. Validate Links
    logging.info("Validating relationships in link table...")
    
    valid_links = 0
    orphaned_links = 0
    linked_companies = set()
    linked_facilities = set()

    if os.path.exists(FILE_LINKS):
        with open(FILE_LINKS, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c_id = row.get("company_id")
                f_id = row.get("facility_id")
                
                # Check 1: Does the company exist?
                c_exists = c_id in company_ids
                # Check 2: Does the facility exist?
                f_exists = f_id in facility_ids
                
                if c_exists and f_exists:
                    valid_links += 1
                    linked_companies.add(c_id)
                    linked_facilities.add(f_id)
                else:
                    orphaned_links += 1
                    # In a real scenario, you might log the specific broken link here
    else:
        logging.error(f"Link table {FILE_LINKS} not found!")
        return

    # 3. Calculate Orphans (Entities with no links)
    orphaned_companies = len(company_ids) - len(linked_companies)
    orphaned_facilities = len(facility_ids) - len(linked_facilities)

    # 4. Report Results
    logging.info("--- Validation Report ---")
    logging.info(f"Total Companies: {len(company_ids)}")
    logging.info(f"Total Facilities: {len(facility_ids)}")
    logging.info(f"Valid Relationships: {valid_links}")
    
    if orphaned_links > 0:
        logging.warning(f"Found {orphaned_links} broken links (references to non-existent IDs).")
    else:
        logging.info("Integrity Check Passed: No broken links found.")
        
    logging.info(f"Companies without facilities: {orphaned_companies}")
    logging.info(f"Facilities without companies: {orphaned_facilities}")
    
    logging.info("Phase 4 completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()