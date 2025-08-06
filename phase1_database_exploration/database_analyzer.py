#!/usr/bin/env python3
"""
Database Analyzer for Gym Management System
Phase 1: Database Understanding & Exploration
"""

import re
import json
from datetime import datetime
import os

# Try to import pandas, but don't fail if it's not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available, some features may be limited")

from collections import defaultdict

class DatabaseAnalyzer:
    def __init__(self, dump_file_path):
        self.dump_file_path = dump_file_path
        self.tables = {}
        self.relationships = []
        self.schema_info = {}
        
    def analyze_dump_structure(self):
        """Analyze the database dump file to extract schema information"""
        print("🔍 Analyzing database dump structure...")
        
        # Check if file exists
        if not os.path.exists(self.dump_file_path):
            print(f"❌ Error: File {self.dump_file_path} not found!")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Looking for file: {os.path.abspath(self.dump_file_path)}")
            return None
        
        try:
            with open(self.dump_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
            
        # Extract table creation statements for MySQL format
        table_pattern = r'CREATE TABLE `(\w+)`\s*\((.*?)\)\s*ENGINE='
        table_matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"📊 Found {len(table_matches)} tables in the database")
        
        for table_name, table_body in table_matches:
            self._parse_table_structure(table_name, table_body)
            
        # Extract data insertion statements
        insert_pattern = r'INSERT INTO.*?;'
        inserts = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"📈 Found {len(inserts)} data insertion statements")
        
        # Extract foreign key relationships
        fk_pattern = r'FOREIGN KEY.*?REFERENCES.*?;'
        foreign_keys = re.findall(fk_pattern, content, re.DOTALL | re.IGNORECASE)
        
        print(f"🔗 Found {len(foreign_keys)} foreign key relationships")
        
        return {
            'tables': self.tables,
            'relationships': foreign_keys,
            'total_inserts': len(inserts)
        }
    
    def _parse_table_structure(self, table_name, table_body):
        """Parse individual table structure"""
        table_info = {
            'name': table_name,
            'columns': [],
            'primary_keys': [],
            'foreign_keys': []
        }
        
        # Split table body into lines and process each line
        lines = [line.strip() for line in table_body.split('\n') if line.strip()]
        
        for line in lines:
            # Skip comments and empty lines
            if line.startswith('--') or not line:
                continue
                
            # Extract column definitions for MySQL format
            # Pattern to match: `column_name` data_type [constraints]
            col_match = re.match(r'^`(\w+)`\s+([^,\n]+)', line, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1)
                col_def = col_match.group(2).strip()
                
                # Check for primary key
                if 'PRIMARY KEY' in col_def.upper():
                    table_info['primary_keys'].append(col_name)
                
                # Check for foreign key
                if 'REFERENCES' in col_def.upper():
                    fk_match = re.search(r'REFERENCES\s+`(\w+)`\s*\(`(\w+)`\)', col_def, re.IGNORECASE)
                    if fk_match:
                        table_info['foreign_keys'].append({
                            'column': col_name,
                            'references_table': fk_match.group(1),
                            'references_column': fk_match.group(2)
                        })
                
                table_info['columns'].append({
                    'name': col_name,
                    'definition': col_def
                })
            
            # Also check for separate PRIMARY KEY and FOREIGN KEY declarations
            elif 'PRIMARY KEY' in line.upper():
                pk_match = re.search(r'PRIMARY KEY\s*\(`(\w+)`\)', line, re.IGNORECASE)
                if pk_match:
                    table_info['primary_keys'].append(pk_match.group(1))
            
            elif 'FOREIGN KEY' in line.upper():
                fk_match = re.search(r'FOREIGN KEY\s*\(`(\w+)`\)\s*REFERENCES\s+`(\w+)`\s*\(`(\w+)`\)', line, re.IGNORECASE)
                if fk_match:
                    table_info['foreign_keys'].append({
                        'column': fk_match.group(1),
                        'references_table': fk_match.group(2),
                        'references_column': fk_match.group(3)
                    })
        
        self.tables[table_name] = table_info
    
    def generate_schema_report(self):
        """Generate a comprehensive schema report"""
        print("\n📋 Generating Schema Report...")
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'database_name': 'Gym Management System',
            'total_tables': len(self.tables),
            'tables': self.tables,
            'summary': {}
        }
        
        # Generate summary statistics
        total_columns = sum(len(table['columns']) for table in self.tables.values())
        total_primary_keys = sum(len(table['primary_keys']) for table in self.tables.values())
        total_foreign_keys = sum(len(table['foreign_keys']) for table in self.tables.values())
        
        report['summary'] = {
            'total_columns': total_columns,
            'total_primary_keys': total_primary_keys,
            'total_foreign_keys': total_foreign_keys,
            'average_columns_per_table': round(total_columns / len(self.tables), 2) if self.tables else 0
        }
        
        return report
    
    def identify_key_entities(self):
        """Identify key business entities in the gym management system"""
        print("\n🎯 Identifying Key Business Entities...")
        
        key_entities = {
            'members': [],
            'coaches': [],
            'subscriptions': [],
            'sessions': [],
            'plans': [],
            'payments': [],
            'equipment': [],
            'classes': []
        }
        
        # Map table names to business entities
        entity_mapping = {
            'member': 'members',
            'user': 'members',
            'client': 'members',
            'coach': 'coaches',
            'trainer': 'coaches',
            'instructor': 'coaches',
            'subscription': 'subscriptions',
            'membership': 'subscriptions',
            'plan': 'plans',
            'package': 'plans',
            'session': 'sessions',
            'workout': 'sessions',
            'class': 'classes',
            'course': 'classes',
            'payment': 'payments',
            'billing': 'payments',
            'equipment': 'equipment',
            'machine': 'equipment'
        }
        
        for table_name in self.tables.keys():
            table_lower = table_name.lower()
            for keyword, entity_type in entity_mapping.items():
                if keyword in table_lower:
                    key_entities[entity_type].append(table_name)
                    break
        
        return key_entities

def main():
    """Main analysis function"""
    print("🏋️‍♂️ Gym Management System Database Analysis")
    print("=" * 50)
    
    # Determine the correct path to the dump file
    # Check if we're in the phase1_database_exploration directory
    current_dir = os.getcwd()
    if os.path.basename(current_dir) == 'phase1_database_exploration':
        # We're in the phase1_database_exploration directory, go up one level
        dump_file_path = os.path.join('..', 'threesity_final.dump')
    else:
        # We're in the root directory
        dump_file_path = 'threesity_final.dump'
    
    # Initialize analyzer
    analyzer = DatabaseAnalyzer(dump_file_path)
    
    # Analyze database structure
    analysis_result = analyzer.analyze_dump_structure()
    
    if analysis_result is None:
        print("❌ Analysis failed. Please check the dump file path and try again.")
        return
    
    # Generate schema report
    schema_report = analyzer.generate_schema_report()
    
    # Identify key entities
    key_entities = analyzer.identify_key_entities()
    
    # Create output directory if it doesn't exist
    output_dir = 'phase1_database_exploration'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save results
    try:
        with open(f'{output_dir}/schema_report.json', 'w') as f:
            json.dump(schema_report, f, indent=2)
        
        with open(f'{output_dir}/key_entities.json', 'w') as f:
            json.dump(key_entities, f, indent=2)
        
        print(f"✅ Results saved to {output_dir}/ directory")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
    
    # Print summary
    print("\n📊 ANALYSIS SUMMARY:")
    print(f"• Total Tables: {schema_report['total_tables']}")
    print(f"• Total Columns: {schema_report['summary']['total_columns']}")
    print(f"• Total Primary Keys: {schema_report['summary']['total_primary_keys']}")
    print(f"• Total Foreign Keys: {schema_report['summary']['total_foreign_keys']}")
    
    print("\n🎯 KEY BUSINESS ENTITIES:")
    for entity_type, tables in key_entities.items():
        if tables:
            print(f"• {entity_type.title()}: {', '.join(tables)}")
    
    print("\n✅ Analysis complete! Check the 'phase1_database_exploration/' directory for detailed reports.")

if __name__ == "__main__":
    main() 