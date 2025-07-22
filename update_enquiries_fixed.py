#!/usr/bin/env python3
"""
Update dashboard with Salesforce enquiry data - Fixed version
"""

import csv
import re
from collections import Counter

def parse_salesforce_enquiries(filename):
    """Parse Salesforce enquiry export and count by model"""
    enquiries = []
    
    with open(filename, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        lines = content.strip().split('\n')
        
        # Find where the actual data starts (after headers)
        data_start = False
        for i, line in enumerate(lines):
            if 'Make Car' in line and 'Model car' in line:
                data_start = True
                continue
            
            if data_start and line.strip():
                # Parse CSV line
                try:
                    row = list(csv.reader([line]))[0]
                    if len(row) >= 6:  # Need price and reg columns
                        make = row[1].strip() if row[1] else ''
                        model = row[3].strip() if row[3] else ''
                        price = row[4].strip() if row[4] else ''
                        reg = row[5].strip() if row[5] else ''
                        
                        # Skip empty or header rows
                        if make and model and make not in ['', 'Filtered By', 'This Weeks Sales Report', 'Total']:
                            enquiries.append({
                                'make': make,
                                'model': model,
                                'price': price,
                                'reg': reg
                            })
                except:
                    continue
    
    # Group enquiries by normalized model name
    model_groups = {}
    
    for enq in enquiries:
        make = enq['make']
        model = enq['model']
        
        # Normalize and create display names
        make_lower = make.lower()
        model_lower = model.lower()
        
        # Determine normalized model name
        if 'ferrari' in make_lower:
            if 'roma' in model_lower:
                norm_model = 'Ferrari Roma'
            else:
                norm_model = f'Ferrari {model}'
        elif 'lamborghini' in make_lower:
            if 'urus' in model_lower:
                norm_model = 'Lamborghini Urus'
            elif 'huracan' in model_lower:
                norm_model = 'Lamborghini Huracán'
            else:
                norm_model = f'Lamborghini {model}'
        elif 'mercedes' in make_lower:
            if 'g63' in model_lower or 'amg g63' in model_lower:
                norm_model = 'Mercedes G63 AMG'
            elif 'vito' in model_lower:
                norm_model = 'Mercedes Vito'
            elif 'sprinter' in model_lower:
                norm_model = 'Mercedes Sprinter'
            else:
                norm_model = f'Mercedes {model}'
        elif 'mclaren' in make_lower:
            if '720' in model:
                norm_model = 'McLaren 720S'
            elif '570' in model:
                norm_model = 'McLaren 570GT'
            else:
                norm_model = f'McLaren {model}'
        elif 'porsche' in make_lower:
            if 'gt3' in model_lower:
                norm_model = 'Porsche 911 GT3'
            elif '718' in model:
                norm_model = 'Porsche 718 GT4'
            else:
                norm_model = f'Porsche {model}'
        elif 'audi' in make_lower:
            # Group all A8 enquiries together
            if 'a8' in model_lower:
                norm_model = 'Audi A8'
            elif 'r8' in model_lower:
                norm_model = 'Audi R8'
            elif 'rs5' in model_lower:
                norm_model = 'Audi RS5'
            elif 'rsq8' in model_lower:
                norm_model = 'Audi RSQ8'
            else:
                norm_model = f'Audi {model}'
        elif 'rolls' in make_lower:
            norm_model = f'Rolls-Royce {model}'
        elif 'land rover' in make_lower:
            norm_model = f'Land Rover {model}'
        elif 'ariel' in make_lower:
            norm_model = f'Ariel {model}'
        else:
            norm_model = f'{make} {model}'
        
        # Group enquiries
        if norm_model not in model_groups:
            model_groups[norm_model] = []
        model_groups[norm_model].append(enq)
    
    # Count and get representative price/reg for each model
    model_data = []
    for model, enqs in model_groups.items():
        # Get a representative price (prefer non-empty)
        price = ''
        reg = ''
        for enq in enqs:
            if enq['price'] and not price:
                price = enq['price']
            if enq['reg'] and not reg:
                reg = enq['reg']
        
        model_data.append({
            'model': model,
            'count': len(enqs),
            'price': price,
            'reg': reg
        })
    
    # Sort by count descending
    model_data.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"Found {len(enquiries)} total enquiries")
    print(f"Top models: {[(m['model'], m['count']) for m in model_data[:4]]}")
    
    # Return top 4 models with data
    return model_data[:4]

def update_dashboard_enquiries(enquiry_data):
    """Update the dashboard HTML with new enquiry data"""
    
    # Read current dashboard
    with open('dashboard_v3_final.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate new enquiry HTML
    enquiry_html = ""
    for data in enquiry_data:
        model = data['model']
        count = data['count']
        price = data['price']
        reg = data['reg']
        # Determine brand badge
        badge = 'badge-ferrari' if 'Ferrari' in model else \
                'badge-lamborghini' if 'Lamborghini' in model else \
                'badge-mercedes' if 'Mercedes' in model else \
                'badge-mclaren' if 'McLaren' in model else \
                'badge-audi' if 'Audi' in model else \
                'badge-porsche' if 'Porsche' in model else \
                'badge-bentley' if 'Bentley' in model else \
                'badge-rolls' if 'Rolls' in model else \
                'badge-land-rover' if 'Land Rover' in model else \
                'badge-ariel' if 'Ariel' in model else \
                'badge-bmw'
        
        brand_tag = 'FER' if 'Ferrari' in model else \
                   'LAM' if 'Lamborghini' in model else \
                   'MB' if 'Mercedes' in model else \
                   'MCL' if 'McLaren' in model else \
                   'AUD' if 'Audi' in model else \
                   'POR' if 'Porsche' in model else \
                   'BEN' if 'Bentley' in model else \
                   'RR' if 'Rolls' in model else \
                   'LR' if 'Land Rover' in model else \
                   'ARI' if 'Ariel' in model else \
                   'BMW'
        
        # Extract just the model name (remove brand prefix)
        display_model = model
        for brand in ['Ferrari ', 'Lamborghini ', 'Mercedes ', 'McLaren ', 'Audi ', 'Porsche ', 'Bentley ', 'Rolls-Royce ', 'Land Rover ', 'Ariel ']:
            if model.startswith(brand):
                display_model = model[len(brand):]
                break
        
        # Format price for display
        price_display = ''
        if price:
            # Clean up price format
            price_display = price.replace('GBP', '£').strip()
        else:
            price_display = '-'
        
        # Use reg if available, otherwise show dash
        reg_display = reg if reg else '-'
        
        # Get badge background color
        badge_colors = {
            'badge-ferrari': '#DC0000',
            'badge-lamborghini': '#FFC500',
            'badge-mercedes': '#00D2BE',
            'badge-mclaren': '#FF8700',
            'badge-audi': '#BB0A30',
            'badge-porsche': '#000000',
            'badge-bentley': '#154734',
            'badge-rolls': '#6B3AA9',
            'badge-land-rover': '#005A2B',
            'badge-ariel': '#FF6B00',
            'badge-bmw': '#0066CC'
        }
        badge_color = badge_colors.get(badge, '#6B7280')
        text_color = 'white' if badge not in ['badge-lamborghini', 'badge-mercedes'] else '#000'
        
        enquiry_html += f'''
                    <div class="enquiry-item" style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #F5F5F5; border-radius: 8px; margin-bottom: 8px;">
                        <div class="brand-badge" style="width: 36px; height: 24px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; background: {badge_color}; color: {text_color}; flex-shrink: 0;">{brand_tag}</div>
                        <div style="flex: 1; display: flex; align-items: center; gap: 16px; font-size: 0.875rem;">
                            <span style="font-weight: 600; min-width: 120px;">{display_model}</span>
                            <span style="color: #6B7280; min-width: 80px;">{reg_display}</span>
                            <span style="color: #6B7280; text-align: right; min-width: 60px;">-</span>
                            <span style="font-weight: 500; text-align: right; flex: 1;">{price_display}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px; margin-left: auto;">
                            <span style="font-size: 1.25rem; font-weight: 700; color: #FB923C;">{count}</span>
                            <span style="font-size: 0.75rem; color: #6B7280;">enquiries</span>
                        </div>
                    </div>'''
    
    # Find and replace the enquiries section
    pattern = r'(<div class="enquiries-list">)(.*?)(</div>\s*</div>\s*<!--\s*Low Stock\s*-->)'
    replacement = f'\\1{enquiry_html}\n                \\3'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Save updated dashboard
    with open('dashboard_v3_final.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n✓ Updated enquiries section with {len(enquiry_data)} top models:")
    for data in enquiry_data:
        price_info = f" @ {data['price']}" if data['price'] else ""
        reg_info = f" ({data['reg']})" if data['reg'] else ""
        print(f"  - {data['model']}: {data['count']} enquiries{price_info}{reg_info}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        # If no argument, try default filename
        filename = 'enquiries.csv'
    else:
        filename = sys.argv[1]
    
    try:
        enquiry_counts = parse_salesforce_enquiries(filename)
        if enquiry_counts:
            update_dashboard_enquiries(enquiry_counts)
        else:
            print("❌ No valid enquiry data found in CSV")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()