import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


indicators_df = pd.read_csv('indicators_all.csv')
funders_df = pd.read_csv('biomedical_research_funders.csv')

funding_columns = ['fund_text', 'fund_pmc_institute', 'fund_pmc_source', 'fund_pmc_anysource']


def data_cleaning_processing():
    """Removes spaces and symbols as well as convert to lowercase"""
    for col in funding_columns:
        indicators_df[col] = indicators_df[col].astype(str).str.lower()  # Convert to lowercase
        indicators_df[col] = indicators_df[col].str.replace('[^\w\s]', '', regex=True)  # Remove punctuation


def founder_mapping(funder_names_set):
    """map founder and return a new df with new mapping"""
    try:
        output_df = pd.DataFrame(indicators_df['pmid'])

        # Check for funder matches and populate the output DataFrame
        for funder_name in funder_names_set:
            # Initialize a column for each funder with False
            output_df[funder_name] = False

            # Update the column if any of the funding information columns contain the funder name
            for column in funding_columns:
                output_df[funder_name] = output_df[funder_name] | indicators_df[column].str.contains(funder_name, na=False)
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

        data_cleaning_processing()

        output_df = founder_mapping(funder_names_set)

        output_to_file(output_df)
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        raise e


if __name__ == "__main__":
    main()
