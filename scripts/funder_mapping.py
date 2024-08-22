import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


indicators_df = pd.read_csv('indicators_all.csv')
funders_df = pd.read_csv('biomedical_research_funders.csv')

funding_columns = ['fund_text', 'fund_pmc_institute',
                   'fund_pmc_source', 'fund_pmc_anysource']


def data_cleaning_processing():
    """Removes spaces and symbols"""
    for col in funding_columns:
        indicators_df[col] = indicators_df[col].str.replace(
            '[^\w\s]', '', regex=True)  # Remove punctuation


def founder_mapping(funder_names_acronyms):
    """map founder and return a new df with new mapping"""
    try:
        output_df = pd.DataFrame(indicators_df['pmid'])

        # Check for funder matches and populate the output DataFrame
        for names_acronyms in funder_names_acronyms:
            # Initialize a column for each funder with False
            output_df[names_acronyms] = False

            # Update the column if any of the funding information columns contain the funder name
            for column in funding_columns:
                output_df[names_acronyms] = output_df[names_acronyms] | indicators_df[column].str.contains(
                    names_acronyms, case=False, na=False)

        return output_df

    except Exception as e:
        logger.error(f"Error mapping data {e}")


def output_to_file(output_df: pd.DataFrame):
    """Convert True/False to  TRUE/FALSE and save to file"""
    output = output_df.replace({True: 'TRUE', False: 'FALSE'})
    output.to_csv('pmid-funding-matrix.csv', index=False)


def main():
    try:
        funder_names_set = set(funders_df['Name'].tolist())
        funder_acronyms = set(funders_df['Acronym'].tolist())

        funder_names_acronyms = funder_names_set.union(funder_acronyms)

        data_cleaning_processing()

        output_df = founder_mapping(funder_names_acronyms)

        output_to_file(output_df)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
