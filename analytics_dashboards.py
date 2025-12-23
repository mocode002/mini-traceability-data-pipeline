import csv
import logging
import os
import matplotlib.pyplot as plt
from collections import Counter

# --- Configuration ---
FILE_COMPANIES = "cleaned_companies.csv"
FILE_LINKS = "company_facilities.csv"
OUTPUT_DIR = "analytics_output"

def load_data():
    """Loads necessary data for analytics."""
    companies = []
    links = []
    
    if os.path.exists(FILE_COMPANIES):
        with open(FILE_COMPANIES, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            companies = list(reader)
            
    if os.path.exists(FILE_LINKS):
        with open(FILE_LINKS, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            links = list(reader)
            
    return companies, links

def plot_companies_by_country(companies):
    """Generates a bar chart of companies per country."""
    if not companies:
        logging.warning("No company data to plot.")
        return

    # Count frequencies
    countries = [c['country'] for c in companies if c.get('country')]
    counts = Counter(countries)
    
    # Sort for better visualization
    sorted_data = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_data)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color='skyblue', edgecolor='black')
    
    plt.title('Number of Companies by Country', fontsize=14)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}', ha='center', va='bottom')

    output_path = os.path.join(OUTPUT_DIR, "companies_by_country.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logging.info(f"Saved chart: {output_path}")

def plot_facilities_per_company(links):
    """Generates a histogram of facilities count per company."""
    if not links:
        logging.warning("No link data to plot.")
        return

    # Count facilities per company
    company_counts = Counter([l['company_id'] for l in links])
    facility_counts = list(company_counts.values())

    plt.figure(figsize=(10, 6))
    plt.hist(facility_counts, bins=range(1, max(facility_counts) + 2), 
             color='lightgreen', edgecolor='black', align='left')
    
    plt.title('Distribution of Facilities per Company', fontsize=14)
    plt.xlabel('Number of Facilities', fontsize=12)
    plt.ylabel('Number of Companies', fontsize=12)
    plt.yscale('log') # Log scale helps if there's a huge skew
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    output_path = os.path.join(OUTPUT_DIR, "facilities_distribution.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logging.info(f"Saved chart: {output_path}")

def run():
    logging.info("--- Starting Phase 5: Analytics & Dashboards ---")
    
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    companies, links = load_data()
    
    if not companies or not links:
        logging.error("Missing data files. Cannot generate analytics.")
        return

    logging.info("Generating Companies by Country chart...")
    plot_companies_by_country(companies)
    
    logging.info("Generating Facilities per Company chart...")
    plot_facilities_per_company(links)
    
    logging.info("Phase 5 completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()