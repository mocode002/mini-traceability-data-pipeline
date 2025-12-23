import logging
import sys
import time
import scrape_oar
import clean_companies
import clean_facilities
import relational_builder
import analytics_dashboards
import ai_module
import export_final

def setup_logging():
    """Configures logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("pipeline.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logging.info("=== Starting End-to-End Mini Traceability Data Pipeline ===")
    
    start_total_time = time.time()

    try:
        # --- PHASE 1: Data Extraction ---
        logging.info(">>> PHASE 1: Executing Data Extraction (scrape_oar)...")
        scrape_oar.run()
        logging.info("Phase 1 completed.")

        # --- PHASE 2: Company Cleaning ---
        logging.info(">>> PHASE 2: Executing Company Cleaning (clean_companies)...")
        clean_companies.run()
        logging.info("Phase 2 completed.")

        # --- PHASE 3: Facility Processing ---
        logging.info(">>> PHASE 3: Executing Facility Processing (clean_facilities)...")
        clean_facilities.run()
        logging.info("Phase 3 completed.")

        # --- PHASE 4: Relational Structuring ---
        logging.info(">>> PHASE 4: Building Relational Structure (relational_builder)...")
        relational_builder.run()
        logging.info("Phase 4 completed.")

        # --- PHASE 5: Analytics & Dashboards ---
        logging.info(">>> PHASE 5: Generating Analytics (analytics_dashboards)...")
        analytics_dashboards.run()
        logging.info("Phase 5 completed.")

        # --- PHASE 6: AI Module ---
        logging.info(">>> PHASE 6: Running AI Module (ai_module - Option C)...")
        ai_module.run()
        logging.info("Phase 6 completed.")

        # --- PHASE 7: Final Export ---
        logging.info(">>> PHASE 7: Exporting Final Data (export_final)...")
        export_final.run()
        logging.info("Phase 7 completed.")

        end_total_time = time.time()
        duration = end_total_time - start_total_time
        logging.info(f"=== Pipeline Finished Successfully in {duration:.2f} seconds ===")

    except Exception as e:
        logging.error(f"CRITICAL ERROR: Pipeline failed during execution.")
        logging.error(f"Error details: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()