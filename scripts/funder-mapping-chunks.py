import pandas as pd
import numpy as np
import logging
import sys
import re

# still need to test this version and modify logging AGT 2024-08-23

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

funders_df = pd.read_csv('biomedical_research_funders.csv')

funding_columns = ['fund_text', 'fund_pmc_institute',
                   'fund_pmc_source', 'fund_pmc_anysource']

def validate_pmcid(pmcid):
    """Validate that a PMCID is a positive integer"""
    return pd.notna(pmcid) and isinstance(pmcid, (int, np.integer)) and pmcid > 0

def data_cleaning_processing(df):
    """Removes spaces and symbols"""
    for col in funding_columns:
        if df[col].dtype == 'object':  # Only process string columns
            df[col] = df[col].str.replace('[^\w\s]', '', regex=True)
    return df

def funder_mapping(chunk, funder_names, funder_acronyms):
    """Map funders for a chunk of data"""
    output_chunk = pd.DataFrame(chunk['pmcid'])
    
    for name, acronym in zip(funder_names, funder_acronyms):
        output_chunk[name] = False
        for column in funding_columns:
            if chunk[column].dtype == 'object':
                name_matches = chunk[column].str.contains(name, case=False, na=False)
                acronym_matches = chunk[column].str.contains(acronym, case=False, na=False)
                
                output_chunk[name] |= name_matches | acronym_matches
                
                if name_matches.any():
                    matched_rows = chunk.loc[name_matches]
                    for _, row in matched_rows.iterrows():
                        match = re.search(name, str(row[column]), re.IGNORECASE)
                        if match:
                            logger.info(f"PMCID {row['pmcid']}: Found {name} in {column}: {match.group()}")
                
                if acronym_matches.any():
                    matched_rows = chunk.loc[acronym_matches]
                    for _, row in matched_rows.iterrows():
                        match = re.search(acronym, str(row[column]), re.IGNORECASE)
                        if match:
                            logger.info(f"PMCID {row['pmcid']}: Found {acronym} in {column}: {match.group()}")
    
    return output_chunk

def process_chunks(chunk_size=10000):
    funder_names = funders_df['Name'].tolist()
    funder_acronyms = funders_df['Acronym'].tolist()
    
    output_chunks = []
    invalid_pmcids = []

    for chunk in pd.read_csv(sys.stdin, chunksize=chunk_size):
        if 'pmcid_pmc' in chunk.columns:
            chunk = chunk.rename(columns={'pmcid_pmc': 'pmcid'})
        
        # Validate PMCIDs
        invalid_mask = ~chunk['pmcid'].apply(validate_pmcid)
        if invalid_mask.any():
            invalid_pmcids.extend(chunk.loc[invalid_mask, 'pmcid'].tolist())
        
        chunk = chunk[~invalid_mask]
        
        if not chunk.empty:
            chunk = data_cleaning_processing(chunk)
            output_chunk = funder_mapping(chunk, funder_names, funder_acronyms)
            output_chunks.append(output_chunk)
    
    if invalid_pmcids:
        for pmcid in invalid_pmcids:
            logger.error(f"Invalid PMCID: '{pmcid}'")
        raise ValueError("Invalid PMCIDs found in the input. Please check the log for details.")
    
    return pd.concat(output_chunks, ignore_index=True)

def output_to_file(output_df: pd.DataFrame):
    """Convert True/False to TRUE/FALSE and save to file"""
    output = output_df.replace({True: 'TRUE', False: 'FALSE'})
    output.to_csv('pmcid-funding-matrix.csv', index=False)

def main():
    try:
        output_df = process_chunks()
        output_to_file(output_df)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
