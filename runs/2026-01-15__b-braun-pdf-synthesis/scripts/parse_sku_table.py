#!/usr/bin/env python3
"""Parse the SKU table from Jennifer Gotto's email HTML."""

from pathlib import Path
from bs4 import BeautifulSoup
import re
import csv

def main():
    html_path = Path(__file__).parent.parent / 'tmp' / 'jen_email_sku_list.html'
    html = html_path.read_text(encoding='utf-8')
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    products = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            volume = cells[0].get_text(strip=True)
            solution_type = cells[1].get_text(strip=True)
            sku = cells[2].get_text(strip=True)
            description = cells[3].get_text(strip=True)
            ndc = cells[4].get_text(strip=True)
            
            # Validate NDC format (XX-XXXX-XX or XXXXX-XXX-XX)
            if re.match(r'^\d{5}-\d{3}-\d{2}$', ndc):
                products.append({
                    'volume': volume,
                    'solution_type': solution_type,
                    'sku': sku,
                    'description': description,
                    'ndc': ndc
                })
    
    print(f"Found {len(products)} products with valid NDCs\n")
    
    # Analyze NDC prefixes to identify manufacturers
    ndc_prefixes = {}
    for p in products:
        prefix = p['ndc'].split('-')[0]
        if prefix not in ndc_prefixes:
            ndc_prefixes[prefix] = []
        ndc_prefixes[prefix].append(p)
    
    print("NDC Prefixes (labeler codes):")
    for prefix, items in sorted(ndc_prefixes.items()):
        print(f"  {prefix}: {len(items)} products")
    
    print("\n" + "=" * 80)
    print("PRODUCT LIST")
    print("=" * 80)
    
    # Print header
    print(f"{'Volume':<12} {'SKU':<8} {'NDC':<14} {'Description'}")
    print("-" * 80)
    
    for p in products:
        print(f"{p['volume']:<12} {p['sku']:<8} {p['ndc']:<14} {p['description'][:50]}")
    
    # Save to CSV
    csv_path = Path(__file__).parent.parent / 'exports' / 'jen_sku_list.csv'
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['volume', 'solution_type', 'sku', 'description', 'ndc'])
        writer.writeheader()
        writer.writerows(products)
    
    print(f"\n\nSaved to: {csv_path}")
    
    # Also save just NDCs
    ndc_path = Path(__file__).parent.parent / 'tmp' / 'jen_ndcs.txt'
    with open(ndc_path, 'w') as f:
        for p in products:
            # Write as 11-digit format (remove hyphens)
            ndc_clean = p['ndc'].replace('-', '')
            f.write(ndc_clean + '\n')
    print(f"Saved NDCs (11-digit) to: {ndc_path}")
    
    # Save with hyphens too
    ndc_path_hyphen = Path(__file__).parent.parent / 'tmp' / 'jen_ndcs_hyphenated.txt'
    with open(ndc_path_hyphen, 'w') as f:
        for p in products:
            f.write(p['ndc'] + '\n')
    print(f"Saved NDCs (hyphenated) to: {ndc_path_hyphen}")


if __name__ == "__main__":
    main()
