#!/usr/bin/env python3
"""
Data Profiler for Gym Management System
Phase 1: Database Understanding & Exploration
"""

import re
import json
import os
from collections import defaultdict, Counter

# Determine the correct path to the dump file
current_dir = os.getcwd()
if os.path.basename(current_dir) == 'phase1_database_exploration':
    # We're in the phase1_database_exploration directory, go up one level
    DUMP_FILE = os.path.join('..', 'threesity_final.dump')
else:
    # We're in the root directory
    DUMP_FILE = 'threesity_final.dump'

KEY_TABLES = [
    'users', 'group_user', 'instructors', 'subscriptions',
    'scheduled_sessions', 'packages', 'plans'
]

def extract_inserts(table, dump_text):
    """Helper to parse INSERT statements for a table"""
    try:
        pattern = rf"INSERT INTO `{table}`.*?VALUES (.*?);"
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
        print(f"Warning: Error parsing table {table}: {e}")
        return []

def main():
    """Main function to profile the database"""
    print("🔍 Starting Data Profiling...")
    
    # Check if dump file exists
    if not os.path.exists(DUMP_FILE):
        print(f"❌ Error: File {DUMP_FILE} not found!")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for file: {os.path.abspath(DUMP_FILE)}")
        print(f"Available files in current directory: {[f for f in os.listdir('.') if f.endswith('.dump')]}")
        if os.path.exists('..'):
            print(f"Available files in parent directory: {[f for f in os.listdir('..') if f.endswith('.dump')]}")
        return
    
    try:
        print(f"📖 Reading dump file: {DUMP_FILE}")
        with open(DUMP_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            dump_text = f.read()
        print(f"✅ Successfully read {len(dump_text)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    profile = {}
    print("\n📊 Profiling tables...")
    
    for table in KEY_TABLES:
        print(f"  Analyzing {table}...")
        rows = extract_inserts(table, dump_text)
        profile[table] = {
            'row_count': len(rows),
            'example_rows': rows[:3] if rows else [],
        }
        print(f"    Found {len(rows)} rows")

    # Create output directory if it doesn't exist
    output_dir = 'phase1_database_exploration'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save summary
    try:
        output_file = f'{output_dir}/data_profile.json'
        with open(output_file, 'w') as f:
            json.dump(profile, f, indent=2)
        print(f"\n✅ Data profile saved to {output_file}")
    except Exception as e:
        print(f"❌ Error saving data profile: {e}")

    # Print readable report
    print("\n" + "="*50)
    print("DATA PROFILE SUMMARY:")
    print("="*50)
    
    total_rows = 0
    for table, info in profile.items():
        row_count = info['row_count']
        total_rows += row_count
        print(f"\n📋 Table: {table}")
        print(f"   Rows: {row_count}")
        if info['example_rows']:
            print(f"   Example row: {info['example_rows'][0][:100]}...")
        else:
            print(f"   No data found")
    
    print(f"\n📊 Total rows across all tables: {total_rows}")
    print("\n✅ Data profiling complete!")

if __name__ == '__main__':
    main()