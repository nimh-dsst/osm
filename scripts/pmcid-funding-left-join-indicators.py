import csv
import sys
import argparse
from collections import defaultdict

# Increase the CSV field size limit
csv.field_size_limit(sys.maxsize)

def chunk_iterator(reader, chunk_size=10000):
    """Yield chunks of the CSV reader."""
    chunk = []
    for i, row in enumerate(reader, 1):
        chunk.append(row)
        if i % chunk_size == 0:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def process_right_file(right_file):
    right_data = defaultdict(list)
    with open(right_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for chunk in chunk_iterator(reader):
            for row in chunk:
                right_data[row['pmcid_pmc']].append({
                    'pmid': row.get('pmid', ''),
                    'is_data_pred': row.get('is_data_pred', ''),
                    'is_code_pred': row.get('is_code_pred', ''),
                    'dataset': row.get('dataset', '')
                })
    return right_data

def left_join_csv(left_file, right_file, output_file):
    print("Processing right file...")
    right_data = process_right_file(right_file)
    print("Right file processed.")

    print("Starting left join...")
    with open(left_file, 'r', newline='', encoding='utf-8') as left, \
         open(output_file, 'w', newline='', encoding='utf-8') as out:
        left_reader = csv.DictReader(left)
        
        output_fieldnames = left_reader.fieldnames + ['pmid', 'is_data_pred', 'is_code_pred', 'dataset']
        
        writer = csv.DictWriter(out, fieldnames=output_fieldnames)
        writer.writeheader()

        total_rows = 0
        for chunk in chunk_iterator(left_reader):
            for row in chunk:
                total_rows += 1
                output_row = row.copy()
                right_rows = right_data.get(row['pmcid'], [{}])
                
                # Use the first matching row from the right file
                right_row = right_rows[0]
                
                output_row['pmid'] = right_row.get('pmid', '')
                output_row['is_data_pred'] = right_row.get('is_data_pred', '')
                output_row['is_code_pred'] = right_row.get('is_code_pred', '')
                output_row['dataset'] = right_row.get('dataset', '')
                
                writer.writerow(output_row)

            if total_rows % 100000 == 0:
                print(f"Processed {total_rows} rows...")

    print(f"Left join completed. Total rows processed: {total_rows}")

def main():
    parser = argparse.ArgumentParser(description='Left join two large CSV files based on pmcid and pmcid_pmc fields.')
    parser.add_argument('left_file', help='Path to the left CSV file')
    parser.add_argument('right_file', help='Path to the right CSV file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    
    args = parser.parse_args()
    
    try:
        left_join_csv(args.left_file, args.right_file, args.output_file)
        print(f"Output written to {args.output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
