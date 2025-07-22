#!/usr/bin/env python3
"""
Update dashboard HTML with new inventory data from CSV
"""

import csv
import re
import sys

def update_dashboard(csv_file_path):
    """Update the dashboard HTML with new CSV data"""
    
    # Read the new CSV data
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        new_csv_data = f.read().strip()
    
    # Read the current dashboard
    with open('dashboard_v3_final.html', 'r', encoding='utf-8') as f:
        dashboard_content = f.read()
    
    # Find and replace the CSV data
    pattern = r'const csvData = `([^`]+)`'
    replacement = f'const csvData = `{new_csv_data}`'
    
    updated_content = re.sub(pattern, replacement, dashboard_content, flags=re.DOTALL)
    
    # Save the updated dashboard
    with open('dashboard_v3_final.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    # Count vehicles for confirmation
    vehicle_count = len(new_csv_data.split('\n'))
    print(f"✓ Dashboard updated successfully with {vehicle_count} vehicles")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_inventory.py <csv_file>")
        sys.exit(1)
    
    update_dashboard(sys.argv[1])