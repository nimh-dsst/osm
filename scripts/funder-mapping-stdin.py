#!/usr/bin/env python3
"""
Funder Mapping Script for OpenSciMetrics (OSM)

This script processes biomedical research publications and maps funding information
to specific funder organizations. It reads funding data from CSV input and creates
a binary matrix indicating which funders were detected for each publication.

The script searches for funder names and acronyms across multiple funding-related
columns in the input data and generates a comprehensive funding matrix that can be
used for analysis of funding patterns in biomedical research.

Author: OpenSciMetrics Team
Usage: python funder-mapping-stdin.py [--log-level LEVEL] < input_data.csv
"""

import pandas as pd
import numpy as np
import logging
import sys
import re
import argparse
import os


def setup_logging(log_level):
    """
    Set up logging with the specified log level
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Raises:
        ValueError: If invalid log level is provided
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


# Initialize logger
logger = logging.getLogger(__name__)

# Load the funder reference database
# This CSV contains 32 major biomedical research funders with their names and acronyms
try:
    funders_df = pd.read_csv('biomedical_research_funders.csv')
    logger.info(f"Loaded {len(funders_df)} funder organizations from reference database")
except FileNotFoundError:
    logger.error("biomedical_research_funders.csv not found in current directory")
    sys.exit(1)

# Define the funding-related columns to search for funder information
# These columns typically contain funding acknowledgments and grant information
funding_columns = ['fund_text', 'fund_pmc_institute',
                   'fund_pmc_source', 'fund_pmc_anysource']


def validate_pmcid(indicators_df):
    """
    Validate that each PMCID is a positive integer
    
    PMCIDs (PubMed Central IDs) should be positive integers that uniquely
    identify publications in the PubMed Central database.
    
    Args:
        indicators_df (pd.DataFrame): Input dataframe containing PMCID column
    
    Returns:
        pd.DataFrame: Validated dataframe
    
    Raises:
        ValueError: If invalid PMCIDs are found
    """
    invalid_pmcids = []
    for index, pmcid in enumerate(indicators_df['pmcid'], start=1):
        if not pd.isna(pmcid) and (not isinstance(pmcid, (int, np.integer)) or pmcid <= 0):
            invalid_pmcids.append((index, str(pmcid)))
    
    if invalid_pmcids:
        for line_num, pmcid_value in invalid_pmcids:
            logger.error(f"Invalid PMCID at line {line_num}: '{pmcid_value}'")
        raise ValueError("Invalid PMCIDs found in the input. Please check the log for details.")
    
    logger.info(f"Validated {len(indicators_df)} PMCIDs")
    return indicators_df


def data_cleaning_processing(df):
    """
    Clean funding text data by removing special characters and symbols
    
    This preprocessing step helps improve matching accuracy by standardizing
    the text format and removing punctuation that might interfere with
    funder name detection.
    
    Args:
        df (pd.DataFrame): Input dataframe with funding columns
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    logger.info("Cleaning funding text data...")
    for col in funding_columns:
        if col in df.columns and df[col].dtype == 'object':  # Only process string columns
            # Remove special characters but keep alphanumeric and whitespace
            df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True)
    return df


def funder_mapping(indicators_df, funder_names, funder_acronyms):
    """
    Map funding information to specific funder organizations
    
    This function performs the core funder detection logic by:
    1. Searching for funder names (case-insensitive) in funding text
    2. Searching for funder acronyms (case-sensitive) in funding text
    3. Creating a binary matrix where each row is a publication and each
       column is a funder organization
    
    Args:
        indicators_df (pd.DataFrame): Input dataframe with funding information
        funder_names (list): List of funder organization names
        funder_acronyms (list): List of funder organization acronyms
    
    Returns:
        pd.DataFrame: Binary matrix with funder detection results
    
    Raises:
        Exception: If mapping process fails
    """
    try:
        logger.info(f"Starting funder mapping for {len(indicators_df)} publications")
        output_df = pd.DataFrame(indicators_df['pmcid'])

        # Process each funder organization
        for name, acronym in zip(funder_names, funder_acronyms):
            # Initialize a column for each funder with False
            output_df[name] = False

            # Search across all funding-related columns
            for column in funding_columns:
                if column in indicators_df.columns and indicators_df[column].dtype == 'object':
                    # Search for full funder name (case-insensitive)
                    name_matches = indicators_df[column].str.contains(name, case=False, na=False)
                    # Search for funder acronym (case-sensitive to avoid false positives)
                    acronym_matches = indicators_df[column].str.contains(acronym, case=True, na=False)
                    
                    # Combine matches using OR logic
                    output_df[name] = output_df[name] | name_matches | acronym_matches
                    
                    # Log detailed matches for debugging (only if INFO level is set)
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

        # Count total matches for summary
        total_matches = (output_df.iloc[:, 1:] == True).sum().sum()
        logger.info(f"Funder mapping complete. Found {total_matches} total funder matches across {len(funder_names)} organizations")
        
        return output_df

    except Exception as e:
        logger.error(f"Error mapping data: {e}")
        raise


def output_to_file(output_df: pd.DataFrame):
    """
    Convert True/False values to TRUE/FALSE strings and save to CSV file
    
    The output format uses uppercase TRUE/FALSE for compatibility with
    various data analysis tools and to make the binary nature explicit.
    
    Args:
        output_df (pd.DataFrame): Binary matrix with funder detection results
    """
    logger.info("Converting results to output format...")
    output = output_df.replace({True: 'TRUE', False: 'FALSE'})
    output_file = 'pmcid-funding-matrix.csv'
    output.to_csv(output_file, index=False)
    logger.info(f"Results saved to {output_file}")


def main():
    """
    Main function that orchestrates the funder mapping process
    
    The script expects CSV input from STDIN with the following required columns:
    - pmcid or pmcid_pmc: PubMed Central ID
    - fund_text: Funding acknowledgment text
    - fund_pmc_institute: Funding institute information
    - fund_pmc_source: Funding source information  
    - fund_pmc_anysource: Any funding source information
    
    Output:
    - pmcid-funding-matrix.csv: Binary matrix with funder detection results
    """
    parser = argparse.ArgumentParser(
        description='Map funding information in biomedical publications to specific funder organizations.',
        epilog="""
EXAMPLES:
  # Process a CSV file with default settings
  python funder-mapping-stdin.py < input_data.csv
  
  # Process with detailed logging
  python funder-mapping-stdin.py --log-level INFO < input_data.csv
  
  # Process with debug information
  python funder-mapping-stdin.py --log-level DEBUG < input_data.csv

INPUT FORMAT:
  The script expects CSV input from STDIN with these columns:
  - pmcid or pmcid_pmc: PubMed Central ID (positive integer)
  - fund_text: Funding acknowledgment text
  - fund_pmc_institute: Funding institute information
  - fund_pmc_source: Funding source information
  - fund_pmc_anysource: Any funding source information

OUTPUT FORMAT:
  Creates pmcid-funding-matrix.csv with:
  - One row per publication (PMCID)
  - One column per funder organization (32 total)
  - TRUE/FALSE values indicating funder detection

REQUIRED FILES:
  - biomedical_research_funders.csv: Reference database of funder organizations
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--log-level', default='ERROR', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: ERROR)')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    try:
        logger.info("Starting funder mapping process...")
        
        # Read input from STDIN
        logger.info("Reading input data from STDIN...")
        indicators_df = pd.read_csv(sys.stdin)
        logger.info(f"Read {len(indicators_df)} records from input")
        
        # Rename the first column to 'pmcid' if it's named 'pmcid_pmc'
        if 'pmcid_pmc' in indicators_df.columns:
            indicators_df = indicators_df.rename(columns={'pmcid_pmc': 'pmcid'})
            logger.info("Renamed 'pmcid_pmc' column to 'pmcid'")
        
        # Validate PMCIDs
        indicators_df = validate_pmcid(indicators_df)

        # Extract funder information from reference database
        funder_names = funders_df['Name'].tolist()
        funder_acronyms = funders_df['Acronym'].tolist()
        logger.info(f"Loaded {len(funder_names)} funder organizations for matching")

        # Clean the input data
        indicators_df = data_cleaning_processing(indicators_df)

        # Perform funder mapping
        output_df = funder_mapping(indicators_df, funder_names, funder_acronyms)

        # Save results
        output_to_file(output_df)
        
        logger.info("Funder mapping process completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
