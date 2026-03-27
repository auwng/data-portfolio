import os
import sys
import glob
import pandas as pd
from sodapy import Socrata
from dotenv import load_dotenv
from tqdm import tqdm
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler('/Users/audriswong/data-portfolio/projects/seattle-checkouts/ingest.log'),
        logging.StreamHandler()
    ]
)

load_dotenv('/Users/audriswong/data-portfolio/projects/seattle-checkouts/.env')

CHECKPOINT_DIR = '/Users/audriswong/data-portfolio/projects/seattle-checkouts/data/raw/checkpoints'

def fetch_with_retry(client, dataset_id, where, limit, offset, max_retries=8):
    wait = 2
    for attempt in range(max_retries):
        try:
            batch = client.get(dataset_id,
                               where=where,
                               limit=limit,
                               offset=offset)
            return batch
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"❌ Failed after {max_retries} attempts at offset {offset}: {e}")
                raise
            logging.warning(f"⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
            wait *= 2

def ingest_remaining_by_year():
    client = Socrata("data.seattle.gov",
                     os.getenv("SEATTLE_API_TOKEN"),
                     timeout=240)

    years_to_check = [2025]

    for year in years_to_check:
        logging.info(f"📅 Checking year {year}...")

        # Get total rows for this year from API
        count_result = client.get("tmmm-ytt6",
                                   select="count(*)",
                                   where=f"checkoutyear={year}")
        year_total = int(count_result[0]['count'])

        # Count already saved rows
        existing_files = glob.glob(f'{CHECKPOINT_DIR}/year_{year}_batch_*.parquet')
        rows_already_saved = sum(len(pd.read_parquet(f)) for f in existing_files)
        logging.info(f"   {rows_already_saved:,} already saved of {year_total:,} total")

        # Already complete — skip
        if rows_already_saved >= year_total:
            logging.info(f"✅ Year {year} already complete — skipping")
            continue

        offset = 0
        batch_size = 10000

        with tqdm(total=year_total, initial=rows_already_saved,
                  unit="rows", desc=str(year)) as progress_bar:
            while True:
                checkpoint_file = f'{CHECKPOINT_DIR}/year_{year}_batch_{offset}.parquet'

                if os.path.exists(checkpoint_file):
                    offset += batch_size
                    continue

                batch = fetch_with_retry(client,
                                         dataset_id="tmmm-ytt6",
                                         where=f"checkoutyear={year}",
                                         limit=batch_size,
                                         offset=offset)
                if not batch:
                    break

                pd.DataFrame.from_records(batch).to_parquet(checkpoint_file)
                progress_bar.update(len(batch))
                offset += batch_size
                time.sleep(5)

        # Verify year is complete after fetching
        existing_files = glob.glob(f'{CHECKPOINT_DIR}/year_{year}_batch_*.parquet')
        rows_saved = sum(len(pd.read_parquet(f)) for f in existing_files)

        if rows_saved < year_total:
            logging.error(f"❌ Year {year} incomplete: {rows_saved:,} of {year_total:,}")
            return False

        logging.info(f"✅ Year {year} complete: {rows_saved:,} rows")

    return True

if __name__ == "__main__":
    success = ingest_remaining_by_year()
    if success:
        logging.info("🎉 All years complete!")
        sys.exit(0)   # success — bash loop stops
    else:
        logging.error("❌ Ingestion incomplete — will retry")
        sys.exit(1)   # failure — bash loop retries