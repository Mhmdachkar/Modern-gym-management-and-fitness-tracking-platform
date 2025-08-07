#!/usr/bin/env python3
"""
Data Extractor for Gym Management System
Extracts actual data from database dump and creates CSV files for analysis
"""

import re
import json
import csv
import os
import pandas as pd
from collections import defaultdict

# Determine the correct path to the dump file
current_dir = os.getcwd()
if os.path.basename(current_dir) == 'phase1_database_exploration':
    DUMP_FILE = os.path.join('..', 'threesity_final.dump')
else:
    DUMP_FILE = 'threesity_final.dump'

# Key business tables to extract
KEY_TABLES = {
    'users': 'members',           # Members data
    'instructors': 'coaches',     # Coaches data  
    'subscriptions': 'subscriptions', # Subscriptions data
    'scheduled_sessions': 'sessions', # Sessions data
    'plans': 'plans',             # Membership plans
    'packages': 'packages'        # Training packages
}

def extract_table_schema(dump_text, table_name):
    """Extract table schema (column names) from CREATE TABLE statement"""
    try:
        pattern = rf"CREATE TABLE `{table_name}` \((.*?)\) ENGINE"
        match = re.search(pattern, dump_text, re.DOTALL)
        if match:
            schema_text = match.group(1)
            # Extract column names (everything before the first space)
            columns = []
            lines = schema_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('PRIMARY KEY') and not line.startswith('KEY') and not line.startswith('CONSTRAINT') and not line.startswith('UNIQUE'):
                    # Extract column name (first word)
                    parts = line.split()
                    if parts:
                        col_name = parts[0].strip('`')
                        if col_name and col_name not in ['PRIMARY', 'KEY', 'CONSTRAINT', 'UNIQUE']:
                            columns.append(col_name)
            return columns
    except Exception as e:
        print(f"Warning: Error extracting schema for {table_name}: {e}")
    return []

def extract_inserts(table_name, dump_text):
    """Extract all INSERT statements for a table and parse the data"""
    try:
        pattern = rf"INSERT INTO `{table_name}`.*?VALUES (.*?);"
        matches = re.findall(pattern, dump_text, re.DOTALL)
        rows = []
        
        for match in matches:
            # Split on '),(' but handle first and last parens
            values = re.findall(r'\((.*?)\)', match, re.DOTALL)
            for v in values:
                # Split on commas, but ignore commas inside quotes
                row = re.findall(r"(?:'[^']*'|[^,])+", v)
                row = [x.strip().strip("'") for x in row]
                rows.append(row)
        
        return rows
    except Exception as e:
        print(f"Warning: Error parsing table {table_name}: {e}")
        return []

def clean_data_value(value):
    """Clean and format data values"""
    if value == 'NULL' or value == '':
        return None
    # Remove extra quotes and clean up
    value = value.strip().strip("'\"")
    return value

def extract_table_data(dump_text, table_name, business_name):
    """Extract complete table data and create CSV file"""
    print(f"📊 Extracting {business_name} data from {table_name}...")
    
    # Get table schema
    columns = extract_table_schema(dump_text, table_name)
    if not columns:
        print(f"❌ Could not extract schema for {table_name}")
        return None
    
    print(f"   Schema columns: {columns}")
    
    # Extract data rows
    rows = extract_inserts(table_name, dump_text)
    if not rows:
        print(f"❌ No data found for {table_name}")
        return None
    
    print(f"   Rows found: {len(rows)}")
    
    # Clean and process data
    cleaned_rows = []
    for row in rows:
        cleaned_row = [clean_data_value(val) for val in row]
        cleaned_rows.append(cleaned_row)
    
    # Check if we have a column mismatch
    if cleaned_rows:
        actual_columns = len(cleaned_rows[0])
        expected_columns = len(columns)
        
        print(f"   Expected columns: {expected_columns}, Actual columns: {actual_columns}")
        
        if actual_columns != expected_columns:
            print(f"   ⚠️ Column mismatch detected! Adjusting...")
            # Use actual number of columns and generate generic names
            if actual_columns > expected_columns:
                # Add generic column names for extra columns
                for i in range(expected_columns, actual_columns):
                    columns.append(f"column_{i+1}")
            else:
                # Truncate columns list to match actual data
                columns = columns[:actual_columns]
    
    # Create DataFrame
    try:
        df = pd.DataFrame(cleaned_rows, columns=columns)
        
        # Save to CSV
        csv_filename = f"{business_name}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"✅ Saved {len(df)} rows to {csv_filename}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error creating DataFrame: {e}")
        print(f"   Sample row: {cleaned_rows[0] if cleaned_rows else 'No rows'}")
        return None

def main():
    """Main function to extract data from database dump"""
    print("🚀 Starting Data Extraction from Database Dump...")
    print(f"📁 Looking for dump file: {DUMP_FILE}")
    
    # Check if dump file exists
    if not os.path.exists(DUMP_FILE):
        print(f"❌ Error: File {DUMP_FILE} not found!")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for file: {os.path.abspath(DUMP_FILE)}")
        return
    
    try:
        print(f"📖 Reading dump file: {DUMP_FILE}")
        with open(DUMP_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            dump_text = f.read()
        print(f"✅ Successfully read {len(dump_text)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Create output directory
    output_dir = 'extracted_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    os.chdir(output_dir)
    print(f"📁 Created output directory: {output_dir}")
    
    extracted_data = {}
    
    # Extract data for each key table
    for table_name, business_name in KEY_TABLES.items():
        df = extract_table_data(dump_text, table_name, business_name)
        if df is not None:
            extracted_data[business_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'columns_list': list(df.columns),
                'sample_data': df.head(3).to_dict('records')
            }
    
    # Create metadata file
    metadata = {
        'extraction_date': pd.Timestamp.now().isoformat(),
        'source_file': DUMP_FILE,
        'tables_extracted': extracted_data,
        'total_tables': len(extracted_data)
    }
    
    with open('extraction_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DATA EXTRACTION SUMMARY:")
    print("="*60)
    
    total_rows = 0
    for business_name, info in extracted_data.items():
        rows = info['rows']
        total_rows += rows
        print(f"\n📋 {business_name.upper()}:")
        print(f"   Rows: {rows}")
        print(f"   Columns: {info['columns']}")
        print(f"   Columns: {', '.join(info['columns_list'])}")
    
    print(f"\n📊 Total rows extracted: {total_rows}")
    print(f"📁 CSV files created in: {output_dir}/")
    print(f"📄 Metadata saved to: extraction_metadata.json")
    
    print("\n✅ Data extraction complete!")
    print("🎯 Ready for Google Colab analysis!")
    
    # List created files
    print(f"\n📁 Files created:")
    for file in os.listdir('.'):
        if file.endswith('.csv') or file.endswith('.json'):
            size = os.path.getsize(file)
            print(f"   {file} ({size} bytes)")

if __name__ == '__main__':
    main()
