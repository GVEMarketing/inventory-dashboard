#!/usr/bin/env python3
"""
Simple script to update GVE dashboard with new inventory CSV
Usage: python update_inventory.py inventory.csv
"""

import sys
import re
from datetime import datetime

def update_dashboard(csv_file_path):
    # Read the new CSV data
    with open(csv_file_path, 'r') as f:
        new_csv_data = f.read().strip()
    
    # Read the current dashboard
    with open('dashboard_v3_final.html', 'r') as f:
        dashboard_content = f.read()
    
    # Find and replace the CSV data section
    pattern = r'const csvData = `([^`]+)`'
    replacement = f'const csvData = `{new_csv_data}`'
    
    updated_content = re.sub(pattern, replacement, dashboard_content, flags=re.DOTALL)
    
    # Save the updated dashboard
    with open('dashboard_v3_final.html', 'w') as f:
        f.write(updated_content)
    
    print(f"✓ Dashboard updated with {len(new_csv_data.splitlines())} vehicles")
    print(f"✓ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_inventory.py inventory.csv")
        sys.exit(1)
    
    update_dashboard(sys.argv[1])