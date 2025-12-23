# End-to-End Mini Traceability Data Pipeline (OAR Edition)

## Project Overview
This project is an end-to-end data pipeline designed to scrape, clean, structure, and analyze supply chain data from the Open Apparel Registry (OAR). It was built as part of the technical assessment for the Data Science Intern position at CommonShare.

The pipeline is fully automated, modular, and orchestrated via a central script.

## Structure
* **Phase 1 (`scrape_oar.py`):** Extracts data (supports both Live API and Mock Data generation).
* **Phase 2 (`clean_companies.py`):** Normalizes company names and generates deterministic IDs.
* **Phase 3 (`clean_facilities.py`):** Processes facility details and links them to companies.
* **Phase 4 (`relational_builder.py`):** Validates referential integrity between tables.
* **Phase 5 (`analytics_dashboards.py`):** Generates visualizations for country and facility distributions.
* **Phase 6 (`ai_module.py`):** **Option C** - Detects duplicates using Vector Embeddings (BERT/MiniLM).
* **Phase 7 (`export_final.py`):** Packages the final deliverables and summary report.
* **Orchestrator (`main.py`):** Runs the entire sequence.

## Data Extraction Strategy & Limitations
This project implements a flexible data extraction module (`scrape_oar.py`) that adapts to available resources:

1.  **Local CSV Mode (Preferred):** * The Open Supply Hub limits free accounts to **5,000 downloaded records per year**.
    * I have downloaded the available data for the target regions.
    * **Note:** Because of this strict limit, the filtered dataset contains approx **3,700 records** for the target countries (Morocco, Spain, Portugal, Italy, France, Greece, Malta), which is below the theoretical 10k target. The pipeline threshold (`MIN_RECORDS`) has been adjusted to `3000` to accommodate this real-world constraint while preserving data integrity.

2.  **Mock Data Mode:**  Included as a fallback. If no CSV is present, the script generates 10,000+ synthetic records to demonstrate the pipeline's ability to scale to higher volumes.

3.  **Live API Mode:**  Fully implemented but requires an API Token.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mocode002/mini-traceability-data-pipeline.git
    cd mini-traceability-data-pipeline
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

    *Note: The AI module requires `sentence-transformers`, which will download the `all-MiniLM-L6-v2` model (approx 80MB) on the first run.*


3.  **Environment Configuration (.env):**
    Create a `.env` file in the root directory.
    * If using the **Live API**, add your key:
        ```ini
        OAR_API_KEY=your_api_token_here
        ```
    * If using **CSV Mode** , place your `source_oar_data.csv` in the root folder. No API key is required.

## How to Run

To execute the full pipeline from start to finish:

```bash
python main.py
```

The pipeline will log its progress to the console and to `pipeline.log`.

## Outputs

After execution, a folder named `final_delivery/` will be created containing:

* **Cleaned Datasets:** `cleaned_companies.csv`, `cleaned_facilities.csv`, `company_facilities.csv`.
* **AI Analysis:** `ai_duplicates.csv` (Pairs of companies identified as potential duplicates via cosine similarity).
* **Analytics:** Charts showing companies by country and facilities distribution.
* **Report:** `summary_report.txt` with execution statistics.

## Technical Design Notes

### AI Module (Duplicate Detection)

For the entity resolution task, I utilized **Sentence-BERT (all-MiniLM-L6-v2)** to generate dense vector embeddings of company names.

* **Why Cosine Similarity?** Given the requirement to analyze a small sample set (50 companies), an exact k-NN search using Scikit-Learn's cosine similarity matrix was chosen for its simplicity and precision.
* **Scalability Note:** For a production environment involving millions of records, I would transition to **FAISS (Facebook AI Similarity Search)** to utilize approximate nearest neighbor indexing (HNSW) for better performance.

---

**Author:** Mohamed Bouroua
**Date:** December 2025
