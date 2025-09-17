#!/usr/bin/env python3
import sys
import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

indicators_df = pd.read_parquet(sys.argv[2] if sys.argv[0].startswith('python') else sys.argv[1])
funders_df = pd.read_csv('biomedical_research_funders.csv')

funding_columns = ['fund_text', 'fund_pmc_institute',
                   'fund_pmc_source', 'fund_pmc_anysource']


def data_cleaning_processing():
    """Removes spaces and symbols"""
    for col in funding_columns:
        indicators_df[col] = indicators_df[col].str.replace(
            r'[^\w\s]', '', regex=True)  # Remove punctuation


def funder_mapping(funder_names, funder_acronyms):
    """map founder and return a new df with new mapping"""
    try:
        output_df = pd.DataFrame(indicators_df['pmid'])
        output_df['funder'] = '['

        # Check for funder matches and populate the output DataFrame
        for idx, name in enumerate(funder_names):
            output_df[name] = name
            logging.info(f"Mapping {name}")
            # Update the column if any of the funding information columns contain the funder name
            output_df[name + '_f'] = False
            for column in funding_columns:
                output_df[name + '_f'] = (output_df[name + '_f'] 
                                          | indicators_df[column].str.contains(name, case=False, na=False)
                                          | indicators_df[column].str.contains(f'\\b{funder_acronyms[idx]}\\b', case=True, na=False))

            output_df['funder'] += output_df[name].where(output_df[name + '_f'], '') + ','
            output_df = output_df.drop(columns=[name, name + '_f'])

        output_df['funder'] = output_df['funder'].str.rstrip(',')
        output_df['funder'] += ']'
        return output_df

    except Exception as e:
        logger.error(f"Error mapping data {e}")


def output_to_file(output_df: pd.DataFrame):
    output = output_df.replace({True: 'TRUE', False: 'FALSE'})
    output_file = sys.argv[3] if sys.argv[0].startswith('python') else sys.argv[2]
    output.to_csv(output_file, index=False) 


def main():
    try:
        funder_names = funders_df['Name'].tolist()
        funder_acronyms = funders_df['Acronym'].tolist()

        data_cleaning_processing()

        output_df = funder_mapping(funder_names, funder_acronyms)

        output_to_file(output_df)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
