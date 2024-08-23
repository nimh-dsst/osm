import pandas as pd
import matplotlib.pyplot as plt
import sys
import logging
from tabulate import tabulate
import argparse
import itertools

def setup_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s')

def get_acronym(name):
    return ''.join(word[0].upper() for word in name.split() if word[0].isupper())

def print_results_table(results, percentages, source_acronyms):
    table_data = []
    headers = ["Year"] + [f"{acr} (Count)" for acr in source_acronyms.values()] + [f"{acr} (%)" for acr in source_acronyms.values()]
    years = sorted(set(year for source_data in results.values() for year in source_data.keys()))
    
    for year in years:
        row = [year]
        for source in results.keys():
            row.append(results[source].get(year, 0))
        for source in percentages.keys():
            row.append(f"{percentages[source].get(year, 0):.2f}%")
        table_data.append(row)
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def create_plots_and_csv(results, percentages, source_acronyms, output_filename_base):
    # Prepare data for count plot and CSV
    count_data = {source_acronyms[source]: data for source, data in results.items()}
    count_df = pd.DataFrame(count_data).T  # Transpose the DataFrame
    count_df['Total'] = count_df.sum(axis=1)
    count_df = count_df.sort_values('Total', ascending=False)
    count_df = count_df.drop('Total', axis=1)
    
    # Write count data to CSV
    count_csv_filename = f'{output_filename_base}_count.csv'
    count_df.to_csv(count_csv_filename)
    logging.info(f"Count data has been saved to '{count_csv_filename}'")

    # Define line styles
    line_styles = ['-', '--', '-.', ':']
    style_cycler = itertools.cycle(line_styles)

    # Count plot
    plt.figure(figsize=(15, 10))
    for source in count_df.index:
        years = sorted(count_df.columns)
        counts = [count_df.loc[source, year] for year in years]
        plt.plot(years, counts, marker='o', label=source, linestyle=next(style_cycler))
    plt.xlabel('Year')
    plt.ylabel('Number of TRUE values in is_code_pred')
    plt.title('Funding Sources and Code Predictions Over Time (Count)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(f'{output_filename_base}_count.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Prepare data for percentage plot and CSV
    percentage_data = {source_acronyms[source]: {year: perc for year, perc in data.items() if 2015 <= year <= 2020} 
                       for source, data in percentages.items()}
    percentage_df = pd.DataFrame(percentage_data).T  # Transpose the DataFrame
    percentage_df['Total'] = percentage_df.sum(axis=1)
    percentage_df = percentage_df.sort_values('Total', ascending=False)
    percentage_df = percentage_df.drop('Total', axis=1)

    # Write percentage data to CSV
    percentage_csv_filename = f'{output_filename_base}_percentage_2015_2020.csv'
    percentage_df.to_csv(percentage_csv_filename)
    logging.info(f"Percentage data has been saved to '{percentage_csv_filename}'")

    # Reset style cycler
    style_cycler = itertools.cycle(line_styles)

    # Percentage plot (2015-2020)
    plt.figure(figsize=(15, 10))
    for source in percentage_df.index:
        years = sorted(percentage_df.columns)
        percentages = [percentage_df.loc[source, year] for year in years]
        plt.plot(years, percentages, marker='o', label=source, linestyle=next(style_cycler))
    plt.xlabel('Year')
    plt.ylabel('Percentage of TRUE values in is_code_pred')
    plt.title('Funding Sources and Code Predictions Over Time (Percentage, 2015-2020)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid(True)
    plt.xticks(range(2015, 2021))
    plt.savefig(f'{output_filename_base}_percentage_2015_2020.png', dpi=300, bbox_inches='tight')
    plt.close()

def main(csv_filename, log_level):
    setup_logging(log_level)

    logging.info(f"Reading file '{csv_filename}'")

    try:
        df = pd.read_csv(csv_filename, dtype={col: bool for col in range(1, 32)})
        logging.info(f"Successfully read CSV file. Shape: {df.shape}")
    except FileNotFoundError:
        logging.error(f"File '{csv_filename}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        logging.error(f"File '{csv_filename}' is empty.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {str(e)}")
        sys.exit(1)

    logging.debug("First few rows of the DataFrame:")
    logging.debug(df.head().to_string())

    logging.debug("Data types of columns:")
    logging.debug(df.dtypes)

    logging.debug(f"Unique values in 'year' column: {df['year'].unique()}")

    df['year_numeric'] = pd.to_numeric(df['year'], errors='coerce')
    logging.info(f"Unique years after numeric conversion: {sorted(df['year_numeric'].dropna().unique())}")

    if df['year_numeric'].isna().all():
        logging.warning("No valid numeric years found. Attempting to extract year from 'pmid'.")
        df['year_numeric'] = df['pmid'].astype(str).str[:4].astype(float)
        logging.info(f"Unique years extracted from 'pmid': {sorted(df['year_numeric'].dropna().unique())}")

    df = df.dropna(subset=['year_numeric'])
    df['year_numeric'] = df['year_numeric'].astype(int)  # Convert to integer
    logging.info(f"Shape after dropping NaN years: {df.shape}")

    if df.empty:
        logging.error("No valid data remaining after processing years. Please check the 'year' column in your CSV file.")
        sys.exit(1)

    funding_sources = df.columns[1:32]
    source_acronyms = {source: get_acronym(source) for source in funding_sources}
    logging.debug(f"Funding sources: {', '.join(source_acronyms.values())}")

    results = {source: {} for source in funding_sources}
    percentages = {source: {} for source in funding_sources}

    for year in df['year_numeric'].unique():
        year_data = df[df['year_numeric'] == year]
        logging.debug(f"Processing year {year}, {len(year_data)} rows")
        for source in funding_sources:
            total_count = year_data[source].sum()
            code_pred_count = year_data[year_data[source] & year_data['is_code_pred']].shape[0]
            results[source][int(year)] = code_pred_count
            percentages[source][int(year)] = (code_pred_count / total_count * 100) if total_count > 0 else 0
            logging.debug(f"{source_acronyms[source]} - {code_pred_count} TRUE values, {percentages[source][int(year)]:.2f}%")

    print("\nResults Table:")
    print_results_table(results, percentages, source_acronyms)

    if all(len(data) == 0 for data in results.values()):
        logging.warning("No data to plot. All counts are zero.")
    else:
        create_plots_and_csv(results, percentages, source_acronyms, 'funding_sources_code_predictions')
        logging.info("Graphs and CSV files have been saved.")

    logging.info(f"Total rows in DataFrame: {len(df)}")
    logging.info(f"Unique years: {sorted(df['year_numeric'].unique())}")
    logging.info("Funding sources summary:")
    for source in funding_sources:
        true_count = df[source].sum()
        code_pred_count = df[df[source] & df['is_code_pred']].shape[0]
        percentage = (code_pred_count / true_count * 100) if true_count > 0 else 0
        logging.info(f"  {source_acronyms[source]}: {code_pred_count} TRUE out of {true_count} ({percentage:.2f}%)")
    
    code_pred_count = df['is_code_pred'].sum()
    total_count = len(df)
    code_pred_percentage = (code_pred_count / total_count * 100) if total_count > 0 else 0
    logging.info(f"Total 'is_code_pred' TRUE values: {code_pred_count} out of {total_count} ({code_pred_percentage:.2f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze funding sources and code predictions from CSV data.")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("--log", default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    main(args.csv_file, args.log)
