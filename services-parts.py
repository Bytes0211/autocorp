#!/usr/bin/env python3
"""
Generate service-parts.csv by matching services from auto-service.csv
with parts from auto-parts.csv using fuzzy string matching.
"""

import csv
from thefuzz import fuzz
from pathlib import Path


def load_services(filepath):
    """Load services from auto-service.csv"""
    services = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            services.append({
                'serviceid': row['ServiceID'],
                'service': row['Service']
            })
    return services


def load_parts(filepath):
    """Load parts from auto-parts.csv"""
    parts = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parts.append({
                'part_name': row['part_name'],
                'sku': row['sku']
            })
    return parts


def find_matching_parts(service_text, parts, threshold=60):
    """
    Find parts that fuzzy match the service description.
    Returns list of (sku, score) tuples for matches above threshold.
    """
    matches = []
    
    for part in parts:
        # Use partial ratio for better substring matching
        score = fuzz.partial_ratio(service_text.lower(), part['part_name'].lower())
        
        if score >= threshold:
            matches.append((part['sku'], score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def generate_service_parts(services, parts, threshold=60):
    """
    Generate service-parts mappings.
    Returns list of dicts with id, serviceid, sku.
    """
    mappings = []
    mapping_id = 1
    
    for service in services:
        matches = find_matching_parts(service['service'], parts, threshold)
        
        for sku, score in matches:
            mappings.append({
                'id': mapping_id,
                'serviceid': service['serviceid'],
                'sku': sku
            })
            mapping_id += 1
    
    return mappings


def write_service_parts(mappings, filepath):
    """Write service-parts mappings to CSV"""
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'serviceid', 'sku'])
        writer.writeheader()
        writer.writerows(mappings)


def main():
    # File paths
    service_file = Path('auto-service.csv')
    parts_file = Path('auto-parts.csv')
    output_file = Path('service-parts.csv')
    
    # Load data
    print(f"Loading services from {service_file}...")
    services = load_services(service_file)
    print(f"Loaded {len(services)} services")
    
    print(f"Loading parts from {parts_file}...")
    parts = load_parts(parts_file)
    print(f"Loaded {len(parts)} parts")
    
    # Generate mappings
    print("Generating service-parts mappings with fuzzy matching...")
    mappings = generate_service_parts(services, parts, threshold=60)
    print(f"Generated {len(mappings)} mappings")
    
    # Write output
    print(f"Writing mappings to {output_file}...")
    write_service_parts(mappings, output_file)
    print("Done!")


if __name__ == '__main__':
    main()
