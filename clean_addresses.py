#!/usr/bin/env python3
"""
Script to clean and fix addresses.csv file for proper Athena loading
"""

import csv
import pandas as pd
import re

def clean_addresses_csv(input_file, output_file):
    """
    Clean the addresses CSV file to handle:
    1. Multi-line addresses
    2. Embedded commas and quotes
    3. Inconsistent formatting
    """
    print(f"Processing {input_file}...")
    
    # First, let's examine the problematic file structure
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count actual records by counting how many times we see AddressID patterns
    address_id_pattern = r'[A-Z]{2}-\d{5}'
    address_ids = re.findall(address_id_pattern, content)
    print(f"Found {len(address_ids)} address ID patterns in the file")
    
    cleaned_records = []
    
    try:
        # Try to read with pandas using proper CSV parsing
        df = pd.read_csv(input_file, 
                        quotechar='"',
                        escapechar='\\',
                        skipinitialspace=True,
                        on_bad_lines='skip')
        
        print(f"Pandas successfully read {len(df)} records")
        
        # Clean up the data
        for col in df.columns:
            if df[col].dtype == 'object':
                # Remove extra quotes, underscores, and normalize text
                df[col] = df[col].astype(str).str.replace(r'["\']', '', regex=True)
                df[col] = df[col].str.replace('_', ' ', regex=False)
                df[col] = df[col].str.replace('\n', ' ', regex=False)
                df[col] = df[col].str.strip()
        
        # Save cleaned data
        df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"Cleaned data saved to {output_file} with {len(df)} records")
        
        return len(df)
        
    except Exception as e:
        print(f"Error processing with pandas: {e}")
        
        # Fallback: Manual parsing
        print("Attempting manual parsing...")
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                # Read line by line and reconstruct proper records
                lines = f.readlines()
                
            header = lines[0].strip()
            current_record = ""
            records = []
            
            for line in lines[1:]:
                line = line.strip()
                
                # Check if this line starts with an AddressID pattern
                if re.match(address_id_pattern, line):
                    # Save previous record if exists
                    if current_record:
                        records.append(current_record)
                    current_record = line
                else:
                    # Continuation of previous record
                    if current_record:
                        current_record += " " + line.replace('"', '').replace('\n', ' ')
            
            # Add the last record
            if current_record:
                records.append(current_record)
            
            # Write cleaned records
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                f.write(header + '\n')
                for record in records:
                    f.write(record + '\n')
            
            print(f"Manual parsing completed. Saved {len(records)} records to {output_file}")
            return len(records)
            
        except Exception as e2:
            print(f"Manual parsing also failed: {e2}")
            return 0

if __name__ == "__main__":
    input_file = "addresses_raw.csv"
    output_file = "addresses_cleaned.csv"
    
    record_count = clean_addresses_csv(input_file, output_file)
    print(f"\nSummary:")
    print(f"- Input file: {input_file}")
    print(f"- Output file: {output_file}")
    print(f"- Records processed: {record_count}")