#!/usr/bin/env python3
"""
ERD Generator for Gym Management System
Phase 1: Database Understanding & Exploration
"""

import json
import os
from datetime import datetime

def load_schema_data():
    """Load the schema data from our previous analysis"""
    try:
        with open('schema_report.json', 'r') as f:
            schema_data = json.load(f)
        return schema_data
    except FileNotFoundError:
        print("❌ schema_report.json not found. Please run database_analyzer.py first.")
        return None

def generate_erd_mermaid(schema_data):
    """Generate ERD in Mermaid format"""
    mermaid_code = """# Gym Management System - Entity Relationship Diagram

```mermaid
erDiagram
"""
    
    # Add entities (tables)
    for table_name, table_info in schema_data['tables'].items():
        mermaid_code += f"    {table_name} {{\n"
        
        # Add columns
        for column in table_info['columns']:
            col_name = column['name']
            col_def = column['definition']
            
            # Determine if it's a primary key
            if col_name in table_info['primary_keys']:
                mermaid_code += f"        {col_name} PK {col_def}\n"
            else:
                mermaid_code += f"        {col_name} {col_def}\n"
        
        mermaid_code += "    }\n\n"
    
    # Add relationships
    for table_name, table_info in schema_data['tables'].items():
        for fk in table_info['foreign_keys']:
            mermaid_code += f"    {table_name} ||--o{{ {fk['references_table']} : \"{fk['column']} -> {fk['references_column']}\"\n"
    
    mermaid_code += "```\n"
    return mermaid_code

def generate_erd_text(schema_data):
    """Generate ERD in text format"""
    erd_text = """# Gym Management System - Entity Relationship Diagram

## Database Overview
- **Total Tables**: {total_tables}
- **Total Columns**: {total_columns}
- **Primary Keys**: {total_pks}
- **Foreign Keys**: {total_fks}

## Entity Relationships

""".format(
        total_tables=schema_data['total_tables'],
        total_columns=schema_data['summary']['total_columns'],
        total_pks=schema_data['summary']['total_primary_keys'],
        total_fks=schema_data['summary']['total_foreign_keys']
    )
    
    # Group tables by business entities
    business_entities = {
        'Members': [],
        'Coaches': [],
        'Subscriptions': [],
        'Sessions': [],
        'Plans': [],
        'System': []
    }
    
    for table_name in schema_data['tables'].keys():
        table_lower = table_name.lower()
        if 'user' in table_lower or 'member' in table_lower:
            business_entities['Members'].append(table_name)
        elif 'instructor' in table_lower or 'coach' in table_lower:
            business_entities['Coaches'].append(table_name)
        elif 'subscription' in table_lower:
            business_entities['Subscriptions'].append(table_name)
        elif 'session' in table_lower:
            business_entities['Sessions'].append(table_name)
        elif 'plan' in table_lower or 'package' in table_lower:
            business_entities['Plans'].append(table_name)
        else:
            business_entities['System'].append(table_name)
    
    # Generate entity descriptions
    for entity_type, tables in business_entities.items():
        if tables:
            erd_text += f"### {entity_type}\n"
            for table_name in tables:
                table_info = schema_data['tables'][table_name]
                erd_text += f"- **{table_name}** ({len(table_info['columns'])} columns)\n"
                if table_info['primary_keys']:
                    erd_text += f"  - Primary Keys: {', '.join(table_info['primary_keys'])}\n"
                if table_info['foreign_keys']:
                    erd_text += f"  - Foreign Keys: {len(table_info['foreign_keys'])} relationships\n"
            erd_text += "\n"
    
    # Add relationship details
    erd_text += "## Key Relationships\n\n"
    for table_name, table_info in schema_data['tables'].items():
        if table_info['foreign_keys']:
            erd_text += f"### {table_name}\n"
            for fk in table_info['foreign_keys']:
                erd_text += f"- `{fk['column']}` → `{fk['references_table']}.{fk['references_column']}`\n"
            erd_text += "\n"
    
    return erd_text

def generate_erd_summary(schema_data):
    """Generate a summary ERD focusing on key business entities"""
    summary = """# Gym Management System - Key Entity Relationships

## Core Business Entities

### 1. Members (Users)
- **users** - Main user/member table
- **group_user** - User group associations

### 2. Coaches (Instructors)
- **instructors** - Coach/trainer profiles

### 3. Subscriptions & Plans
- **subscriptions** - Member subscriptions
- **packages** - Training packages
- **plans** - Membership plans

### 4. Sessions
- **scheduled_sessions** - Booked training sessions

## Key Relationships

```
users (1) ←→ (many) subscriptions
users (1) ←→ (many) scheduled_sessions
instructors (1) ←→ (many) scheduled_sessions
packages (1) ←→ (many) scheduled_sessions
plans (1) ←→ (many) subscriptions
```

## Data Volume Summary
- **339** registered users
- **7** active instructors
- **525** subscription records
- **33** scheduled sessions
- **25** training packages
- **8** membership plans

## Business Flow
1. Users register in the `users` table
2. Users subscribe to `plans` or purchase `packages`
3. Subscriptions are recorded in the `subscriptions` table
4. Users book sessions with instructors via `scheduled_sessions`
5. Sessions are linked to specific packages and instructors
"""
    return summary

def main():
    """Main function to generate ERD"""
    print("🔗 Generating Entity Relationship Diagram...")
    
    # Load schema data
    schema_data = load_schema_data()
    if not schema_data:
        return
    
    # Generate different ERD formats
    mermaid_erd = generate_erd_mermaid(schema_data)
    text_erd = generate_erd_text(schema_data)
    summary_erd = generate_erd_summary(schema_data)
    
    # Save ERD files
    try:
        # Save Mermaid ERD
        with open('erd_mermaid.md', 'w', encoding='utf-8') as f:
            f.write(mermaid_erd)
        
        # Save Text ERD
        with open('erd_text.md', 'w', encoding='utf-8') as f:
            f.write(text_erd)
        
        # Save Summary ERD
        with open('erd_summary.md', 'w', encoding='utf-8') as f:
            f.write(summary_erd)
        
        print("✅ ERD files generated successfully!")
        print("📁 Generated files:")
        print("  - erd_mermaid.md (Mermaid format)")
        print("  - erd_text.md (Detailed text format)")
        print("  - erd_summary.md (Business summary)")
        
    except Exception as e:
        print(f"❌ Error saving ERD files: {e}")

if __name__ == "__main__":
    main() 