import csv
import logging
import os
import numpy as np

# Try importing the AI libraries
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# --- Configuration ---
INPUT_FILE = "cleaned_companies.csv"
OUTPUT_FILE = "ai_duplicates.csv"
SAMPLE_SIZE = 50  # Keep small for speed as per requirements
SIMILARITY_THRESHOLD = 0.85 # Cutoff for considering them duplicates

def load_sample_companies(limit):
    """Loads a small sample of companies for analysis."""
    companies = []
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
            # Take the top N (or random N)
            companies = all_rows[:limit]
    return companies

def run():
    logging.info("--- Starting Phase 6: AI Module (Duplicate Detection) ---")

    if not AI_AVAILABLE:
        logging.error("CRITICAL: 'sentence-transformers' or 'sklearn' not installed.")
        logging.error("Please run: pip install sentence-transformers scikit-learn")
        return

    # 1. Load Data
    companies = load_sample_companies(SAMPLE_SIZE)
    if not companies:
        logging.error("No company data found to analyze.")
        return
    
    names = [c["clean_name"] for c in companies]
    ids = [c["company_id"] for c in companies]
    
    logging.info(f"Loaded {len(names)} companies for embedding analysis.")

    # 2. Generate Embeddings
    logging.info("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    logging.info("Generating vector embeddings...")
    embeddings = model.encode(names)

    # 3. Calculate Similarity Matrix
    logging.info("Calculating cosine similarity...")
    similarity_matrix = cosine_similarity(embeddings)

    # 4. Find Duplicates
    duplicates = []
    # Iterate through the upper triangle of the matrix to avoid self-matches and double counting
    num_companies = len(names)
    for i in range(num_companies):
        for j in range(i + 1, num_companies):
            score = similarity_matrix[i][j]
            
            if score >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    "company_a_id": ids[i],
                    "company_a_name": names[i],
                    "company_b_id": ids[j],
                    "company_b_name": names[j],
                    "similarity_score": f"{score:.4f}"
                })

    # 5. Export Results
    logging.info(f"Found {len(duplicates)} potential duplicates.")
    
    keys = ["company_a_id", "company_a_name", "company_b_id", "company_b_name", "similarity_score"]
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(duplicates)
        
    logging.info(f"AI Analysis results saved to {OUTPUT_FILE}")
    logging.info("Phase 6 completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()