# Data Pipeline

This component contains the data engineering workflow for the Zepto AI Capstone project.

## Pipeline Workflow

1. Collect book/product data from the source website.
2. Store the raw scraped data.
3. Clean and transform the dataset.
4. Convert prices from GBP to INR.
5. Validate missing values and data quality.
6. Load the processed data into SQLite.
7. Perform SQL joins for relational analysis.
8. Validate SQL results against the corresponding pandas transformation.

## Data Quality

The completed dataset contained 100 records and six final fields:

- title
- price_gbp
- price_inr
- rating
- in_stock
- category

The final data-quality validation reported no missing values in these fields.

## Database

The pipeline uses SQLite for structured storage and SQL JOIN operations.

The SQL JOIN output was validated against the equivalent pandas merge operation.