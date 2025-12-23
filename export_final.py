import csv
import json
import logging
import os
import shutil
from datetime import datetime

# --- Configuration ---
FILES_TO_EXPORT = {
    "companies": "cleaned_companies.csv",
    "facilities": "cleaned_facilities.csv",
    "relations": "company_facilities.csv",
    "ai_results": "ai_duplicates.csv",
    "analytics_img1": "analytics_output/companies_by_country.png",
    "analytics_img2": "analytics_output/facilities_distribution.png"
}

EXPORT_DIR = "final_delivery"
REPORT_FILE = "summary_report.txt"

def get_file_stats(filename):
    """Returns the number of records (rows) in a CSV file."""
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r', encoding='utf-8') as f:
        # Subtract 1 for header
        return max(0, sum(1 for line in f) - 1)

def run():
    logging.info("--- Starting Phase 7: Final Export & Reporting ---")
    
    # 1. Prepare Export Directory
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        logging.info(f"Created export directory: {EXPORT_DIR}")

    # 2. Copy Files to Final Destination
    for key, filepath in FILES_TO_EXPORT.items():
        if os.path.exists(filepath):
            # Extract just the filename (e.g., 'cleaned_companies.csv')
            basename = os.path.basename(filepath)
            dest = os.path.join(EXPORT_DIR, basename)
            shutil.copy2(filepath, dest)
            logging.info(f"Exported: {basename}")
        else:
            logging.warning(f"File missing, skipped export: {filepath}")

    # 3. Calculate Statistics
    total_companies = get_file_stats(FILES_TO_EXPORT["companies"])
    total_facilities = get_file_stats(FILES_TO_EXPORT["facilities"])
    
    avg_facilities = 0
    if total_companies > 0:
        avg_facilities = total_facilities / total_companies

    # 4. Generate Summary Report
    report_path = os.path.join(EXPORT_DIR, REPORT_FILE)
    
    report_content = [
        "COMMONSHARE DATA SCIENCE INTERN PROJECT",
        "FINAL DELIVERY REPORT",
        "=======================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "--- PIPELINE STATISTICS ---",
        f"Total Unique Companies Processed: {total_companies}",
        f"Total Facilities Processed:       {total_facilities}",
        f"Average Facilities per Company:   {avg_facilities:.2f}",
        "",
        "--- AI MODULE RESULTS ---",
        f"Duplicate Detection Run:          Yes",
        f"AI Results File:                  ai_duplicates.csv",
        "",
        "--- EXPORTED FILES ---",
    ]
    
    for key, filepath in FILES_TO_EXPORT.items():
        if os.path.exists(filepath):
             report_content.append(f"- {os.path.basename(filepath)}")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_content))

    logging.info(f"Summary report generated at: {report_path}")
    logging.info("Phase 7 completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()