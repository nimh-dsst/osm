import pandas as pd
import numpy as np
import logging
import sys
import re
import argparse


def setup_logging(log_level):
    """Set up logging with the specified log level"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


logger = logging.getLogger(__name__)

funders_df = pd.read_csv('biomedical_research_funders.csv')

funding_columns = ['fund_text', 'fund_pmc_institute',
                   'fund_pmc_source', 'fund_pmc_anysource']

def validate_pmcid(indicators_df):
    """Validate that each PMCID is a positive integer"""
    invalid_pmcids = []
    for index, pmcid in enumerate(indicators_df['pmcid'], start=1):
        if not pd.isna(pmcid) and (not isinstance(pmcid, (int, np.integer)) or pmcid <= 0):
            invalid_pmcids.append((index, str(pmcid)))
    
    if invalid_pmcids:
        for line_num, pmcid_value in invalid_pmcids:
            logger.error(f"Invalid PMCID at line {line_num}: '{pmcid_value}'")
        raise ValueError("Invalid PMCIDs found in the input. Please check the log for details.")
    
    return indicators_df

def data_cleaning_processing(df):
    """Removes spaces and symbols"""
    for col in funding_columns:
        if df[col].dtype == 'object':  # Only process string columns
            df[col] = df[col].str.replace('[^\w\s]', '', regex=True)
    return df

def funder_mapping(indicators_df, funder_names, funder_acronyms):
    """map founder and return a new df with new mapping"""
    try:
        output_df = pd.DataFrame(indicators_df['pmcid'])

        # Check for funder matches and populate the output DataFrame
        for name, acronym in zip(funder_names, funder_acronyms):
            # Initialize a column for each funder with False
            output_df[name] = False

            # Update the column if any of the funding information columns contain the funder name
            for column in funding_columns:
                if indicators_df[column].dtype == 'object':  # Only process string columns
                    name_matches = indicators_df[column].str.contains(name, case=False, na=False)
                    acronym_matches = indicators_df[column].str.contains(acronym, case=True, na=False)
                    
                    output_df[name] = output_df[name] | name_matches | acronym_matches
                    
                    if name_matches.any():
                        matched_rows = indicators_df.loc[name_matches]
                        for _, row in matched_rows.iterrows():
                            match = re.search(name, str(row[column]), re.IGNORECASE)
                            if match:
                                logger.info(f"PMCID {row['pmcid']}: Found {name} in {column}: {match.group()}")
                    
                    if acronym_matches.any():
                        matched_rows = indicators_df.loc[acronym_matches]
                        for _, row in matched_rows.iterrows():
                            match = re.search(acronym, str(row[column]))
                            if match:
                                logger.info(f"PMCID {row['pmcid']}: Found {acronym} in {column}: {match.group()}")

        return output_df

    except Exception as e:
        logger.error(f"Error mapping data: {e}")
        raise

def output_to_file(output_df: pd.DataFrame):
    """Convert True/False to TRUE/FALSE and save to file"""
    output = output_df.replace({True: 'TRUE', False: 'FALSE'})
    output.to_csv('pmcid-funding-matrix.csv', index=False)

def main():
    parser = argparse.ArgumentParser(description='Process funding data.')
    parser.add_argument('--log-level', default='ERROR', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: ERROR)')
    args = parser.parse_args()
    try:
        # Read input from STDIN
        indicators_df = pd.read_csv(sys.stdin)
        
        # Rename the first column to 'pmcid' if it's named 'pmcid_pmc'
        if 'pmcid_pmc' in indicators_df.columns:
            indicators_df = indicators_df.rename(columns={'pmcid_pmc': 'pmcid'})
        
        # Validate PMCIDs
        indicators_df = validate_pmcid(indicators_df)

        funder_names = funders_df['Name'].tolist()
        funder_acronyms = funders_df['Acronym'].tolist()

        indicators_df = data_cleaning_processing(indicators_df)

        output_df = funder_mapping(indicators_df, funder_names, funder_acronyms)

        output_to_file(output_df)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
