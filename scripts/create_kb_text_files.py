#!/usr/bin/env python3
"""
Create individual text files for Bedrock Knowledge Base.

This script generates separate .txt files for each auto part, service, and 
service-part mapping. This format works better with Bedrock's chunking strategies
than large JSONL files.
"""

import json
import os
import psycopg2
from pathlib import Path

# Database connection
DB_CONFIG = {
    'dbname': 'autocorp',
    'user': 'scotton',
    'host': 'localhost'
}

OUTPUT_DIR = Path('knowledge-base-files')


def parse_currency(value) -> float:
    """Convert currency string or numeric value to float."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace('$', '').replace(',', '').strip()
        return float(cleaned)
    return float(value)


def create_enriched_part_text(part: dict) -> str:
    """Create enriched text for auto part."""
    from enrich_kb_data import (
        get_use_cases_for_part, 
        get_keywords_for_part,
        categorize_part
    )
    
    name = part['name']
    sku = part['sku']
    vendor = part['vendor']
    price = part['price']
    
    use_cases = get_use_cases_for_part(name)
    keywords = get_keywords_for_part(name)
    category = categorize_part(name)
    
    text = f"""The {name} is an automotive {category} part. """
    
    if use_cases:
        text += f"This part is typically needed for {use_cases}. "
    
    text += f"Available from {vendor} for ${price:.2f}. "
    
    if keywords:
        text += f"Related terms: {keywords}. "
    
    text += f"Product SKU: {sku}. "
    text += f"Part identifier: {name} ({sku})."
    
    return text


def create_enriched_service_text(service: dict) -> str:
    """Create enriched text for service."""
    from enrich_kb_data import get_problems_for_service, get_customer_reasons
    
    name = service['name']
    category = service['category']
    labor_cost = service['labor_cost']
    labor_minutes = service['labor_minutes']
    service_id = service['serviceid']
    
    problems = get_problems_for_service(name)
    reasons = get_customer_reasons(name)
    
    text = f"""We offer {name} service in our {category} department. """
    
    if problems:
        text += f"This service addresses {problems}. "
    
    hours = labor_minutes / 60
    if hours >= 1:
        text += f"Labor cost is ${labor_cost:.2f} and takes approximately {hours:.1f} hours. "
    else:
        text += f"Labor cost is ${labor_cost:.2f} and takes approximately {labor_minutes} minutes. "
    
    if reasons:
        text += f"Common reasons customers need this service: {reasons}. "
    
    text += f"Service category: {category}. "
    text += f"Service ID: {service_id}."
    
    return text


def create_enriched_service_part_text(service_part: dict) -> str:
    """Create enriched text for service-part mapping."""
    service_name = service_part.get('service_name', 'Unknown Service')
    part_name = service_part.get('part_name', 'Unknown Part')
    quantity = service_part.get('quantity', 1)
    
    text = f"""The {service_name} service requires {part_name} as a component. """
    
    if quantity > 1:
        text += f"This service uses {quantity} units of this part. "
    
    text += f"When booking {service_name}, {part_name} is included as a necessary material. "
    text += f"Service: {service_name}. Part: {part_name}. Quantity: {quantity}."
    
    return text


def sanitize_filename(name: str) -> str:
    """Create safe filename from part/service name."""
    # Replace invalid characters
    safe = name.lower()
    safe = safe.replace('/', '-')
    safe = safe.replace(' ', '-')
    safe = safe.replace('(', '')
    safe = safe.replace(')', '')
    safe = ''.join(c for c in safe if c.isalnum() or c in '-_')
    return safe[:100]  # Limit length


def main():
    """Generate individual text files for knowledge base."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    print(f"Creating output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / 'parts').mkdir(exist_ok=True)
    (OUTPUT_DIR / 'services').mkdir(exist_ok=True)
    (OUTPUT_DIR / 'mappings').mkdir(exist_ok=True)
    
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Generate part files
    print("Creating auto parts files...")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sku, name, vendor, price
        FROM auto_parts
        ORDER BY name
    """)
    
    part_count = 0
    for row in cursor.fetchall():
        part = {
            'sku': row[0],
            'name': row[1],
            'vendor': row[2],
            'price': parse_currency(row[3]),
        }
        
        text = create_enriched_part_text(part)
        filename = f"{sanitize_filename(part['name'])}-{part['sku']}.txt"
        filepath = OUTPUT_DIR / 'parts' / filename
        
        with open(filepath, 'w') as f:
            f.write(text)
        
        part_count += 1
    
    cursor.close()
    print(f"✅ Created {part_count} part files")
    
    # Generate service files
    print("Creating service files...")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT serviceid, service, category, labor_cost, labor_minutes
        FROM service
        ORDER BY service
    """)
    
    service_count = 0
    for row in cursor.fetchall():
        service = {
            'serviceid': row[0],
            'name': row[1],
            'category': row[2],
            'labor_cost': parse_currency(row[3]),
            'labor_minutes': int(row[4]),
        }
        
        text = create_enriched_service_text(service)
        filename = f"{sanitize_filename(service['name'])}-{service['serviceid']}.txt"
        filepath = OUTPUT_DIR / 'services' / filename
        
        with open(filepath, 'w') as f:
            f.write(text)
        
        service_count += 1
    
    cursor.close()
    print(f"✅ Created {service_count} service files")
    
    # Generate service-part mapping files
    print("Creating service-part mapping files...")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.serviceid, s.service, sp.sku, ap.name, sp.quantity
        FROM service_parts sp
        JOIN service s ON sp.serviceid = s.serviceid
        JOIN auto_parts ap ON sp.sku = ap.sku
        ORDER BY s.service, ap.name
    """)
    
    mapping_count = 0
    for row in cursor.fetchall():
        mapping = {
            'serviceid': row[0],
            'service_name': row[1],
            'sku': row[2],
            'part_name': row[3],
            'quantity': int(row[4]),
        }
        
        text = create_enriched_service_part_text(mapping)
        filename = f"{sanitize_filename(mapping['service_name'])}-{sanitize_filename(mapping['part_name'])}-{mapping['serviceid']}.txt"
        filepath = OUTPUT_DIR / 'mappings' / filename
        
        with open(filepath, 'w') as f:
            f.write(text)
        
        mapping_count += 1
    
    cursor.close()
    conn.close()
    
    print(f"✅ Created {mapping_count} mapping files")
    
    total = part_count + service_count + mapping_count
    print(f"\n{'='*60}")
    print(f"Total files created: {total}")
    print(f"  Parts: {part_count}")
    print(f"  Services: {service_count}")
    print(f"  Mappings: {mapping_count}")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"1. Upload files to S3:")
    print(f"   aws s3 sync {OUTPUT_DIR}/ s3://autocorp-datalake-dev/knowledge-base/")
    print(f"")
    print(f"2. Remove old JSONL files:")
    print(f"   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/auto_parts_enriched.jsonl")
    print(f"   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/services_enriched.jsonl")
    print(f"   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/service_parts_enriched.jsonl")
    print(f"")
    print(f"3. Re-ingest knowledge base:")
    print(f"   aws bedrock-agent start-ingestion-job --knowledge-base-id UQSLM6QEVT --data-source-id 87BPR89BUO --region us-east-1")


if __name__ == '__main__':
    main()
