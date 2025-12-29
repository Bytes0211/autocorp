#!/usr/bin/env python3
"""
Export Knowledge Base Data for Bedrock RAG
Exports auto parts, services, and service-parts data from Athena to JSON format
for use with Amazon Bedrock Knowledge Base.

Usage:
    python scripts/export_knowledge_base.py
"""

import json
import time
import boto3
import os
from datetime import datetime

# Configuration
ATHENA_DATABASE = "autocorp_dev"
ATHENA_WORKGROUP = "autocorp-workgroup-dev"
S3_OUTPUT_LOCATION = "s3://autocorp-datalake-dev/athena-results/"
KNOWLEDGE_BASE_OUTPUT = "knowledge-base-data"

# Initialize AWS clients
athena = boto3.client('athena', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

def execute_athena_query(query_string):
    """Execute Athena query and wait for results"""
    print(f"Executing query: {query_string[:100]}...")
    
    response = athena.start_query_execution(
        QueryString=query_string,
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        WorkGroup=ATHENA_WORKGROUP
    )
    
    query_execution_id = response['QueryExecutionId']
    print(f"Query execution ID: {query_execution_id}")
    
    # Wait for query to complete
    while True:
        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        
        print(f"Query status: {status}. Waiting...")
        time.sleep(2)
    
    if status != 'SUCCEEDED':
        error_msg = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
        raise Exception(f"Query failed with status {status}: {error_msg}")
    
    print(f"Query succeeded!")
    return query_execution_id

def get_query_results(query_execution_id):
    """Retrieve query results from Athena"""
    results = []
    paginator = athena.get_paginator('get_query_results')
    
    for page in paginator.paginate(QueryExecutionId=query_execution_id):
        # Skip header row (first row in first page)
        rows = page['ResultSet']['Rows']
        if not results:
            rows = rows[1:]  # Skip header
        
        for row in rows:
            results.append([col.get('VarCharValue', '') for col in row['Data']])
    
    return results

def export_auto_parts():
    """Export auto parts catalog to JSON"""
    print("\n=== Exporting Auto Parts ===")
    
    query = """
    SELECT 
        sku,
        name,
        price,
        description,
        vendor
    FROM autocorp_dev.auto_parts
    ORDER BY sku
    """
    
    query_id = execute_athena_query(query)
    results = get_query_results(query_id)
    
    parts = []
    for row in results:
        sku, name, price, description, vendor = row
        
        parts.append({
            "id": f"part-{sku}",
            "type": "auto_part",
            "sku": sku,
            "name": name,
            "vendor": vendor or "Unknown",
            "price": float(price) if price else 0.0,
            "description": description or f"{name} from {vendor}",
            "text": f"Auto Part: {name} (SKU: {sku}). Vendor: {vendor}. Price: ${price}. Description: {description or 'N/A'}"
        })
    
    print(f"Exported {len(parts)} auto parts")
    return parts

def export_services():
    """Export service catalog to JSON"""
    print("\n=== Exporting Services ===")
    
    query = """
    SELECT 
        serviceid,
        service,
        category,
        labor_cost,
        labor_minutes
    FROM autocorp_dev.service
    ORDER BY category, serviceid
    """
    
    query_id = execute_athena_query(query)
    results = get_query_results(query_id)
    
    services = []
    for row in results:
        serviceid, service, category, labor_cost, labor_minutes = row
        
        # Handle PostgreSQL money type (e.g., "$90.00")
        labor_cost_clean = labor_cost.replace('$', '').replace(',', '') if labor_cost else '0'
        labor_cost_float = float(labor_cost_clean)
        
        services.append({
            "id": f"service-{serviceid}",
            "type": "service",
            "serviceid": serviceid,
            "name": service,
            "category": category,
            "labor_cost": labor_cost_float,
            "labor_minutes": int(labor_minutes) if labor_minutes else 0,
            "text": f"Service: {service} (ID: {serviceid}). Category: {category}. Labor Cost: ${labor_cost_float:.2f} ({labor_minutes} minutes)."
        })
    
    print(f"Exported {len(services)} services")
    return services

def export_service_parts():
    """Export service-parts relationships to JSON"""
    print("\n=== Exporting Service-Parts Relationships ===")
    
    query = """
    SELECT 
        sp.serviceid,
        s.service,
        sp.sku,
        ap.name,
        sp.quantity
    FROM autocorp_dev.service_parts sp
    JOIN autocorp_dev.service s ON sp.serviceid = s.serviceid
    JOIN autocorp_dev.auto_parts ap ON sp.sku = ap.sku
    ORDER BY sp.serviceid, sp.sku
    """
    
    query_id = execute_athena_query(query)
    results = get_query_results(query_id)
    
    relationships = []
    for row in results:
        serviceid, service, sku, part_name, quantity = row
        
        relationships.append({
            "id": f"servicepart-{serviceid}-{sku}",
            "type": "service_part_relationship",
            "serviceid": serviceid,
            "service_name": service,
            "sku": sku,
            "part_name": part_name,
            "quantity": int(quantity) if quantity else 1,
            "text": f"The service '{service}' (ID: {serviceid}) requires {quantity}x {part_name} (SKU: {sku})."
        })
    
    print(f"Exported {len(relationships)} service-parts relationships")
    return relationships

def save_knowledge_base_data(parts, services, relationships):
    """Save all data to JSON files"""
    os.makedirs(KNOWLEDGE_BASE_OUTPUT, exist_ok=True)
    
    # Save auto parts
    with open(f"{KNOWLEDGE_BASE_OUTPUT}/auto_parts.json", 'w') as f:
        json.dump(parts, f, indent=2)
    print(f"Saved {len(parts)} parts to {KNOWLEDGE_BASE_OUTPUT}/auto_parts.json")
    
    # Save services
    with open(f"{KNOWLEDGE_BASE_OUTPUT}/services.json", 'w') as f:
        json.dump(services, f, indent=2)
    print(f"Saved {len(services)} services to {KNOWLEDGE_BASE_OUTPUT}/services.json")
    
    # Save relationships
    with open(f"{KNOWLEDGE_BASE_OUTPUT}/service_parts.json", 'w') as f:
        json.dump(relationships, f, indent=2)
    print(f"Saved {len(relationships)} relationships to {KNOWLEDGE_BASE_OUTPUT}/service_parts.json")
    
    # Create manifest
    manifest = {
        "export_date": datetime.now().isoformat(),
        "database": ATHENA_DATABASE,
        "workgroup": ATHENA_WORKGROUP,
        "statistics": {
            "auto_parts_count": len(parts),
            "services_count": len(services),
            "service_parts_relationships": len(relationships),
            "total_documents": len(parts) + len(services) + len(relationships)
        },
        "files": [
            "auto_parts.json",
            "services.json",
            "service_parts.json"
        ]
    }
    
    with open(f"{KNOWLEDGE_BASE_OUTPUT}/manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest to {KNOWLEDGE_BASE_OUTPUT}/manifest.json")
    
    return manifest

def main():
    """Main execution function"""
    print("="*60)
    print("Knowledge Base Data Export for Bedrock RAG")
    print("="*60)
    
    try:
        # Export all data
        parts = export_auto_parts()
        services = export_services()
        relationships = export_service_parts()
        
        # Save to files
        manifest = save_knowledge_base_data(parts, services, relationships)
        
        print("\n" + "="*60)
        print("Export Summary:")
        print("="*60)
        print(f"Auto Parts: {manifest['statistics']['auto_parts_count']}")
        print(f"Services: {manifest['statistics']['services_count']}")
        print(f"Service-Parts Relationships: {manifest['statistics']['service_parts_relationships']}")
        print(f"Total Documents: {manifest['statistics']['total_documents']}")
        print(f"\nData exported to: ./{KNOWLEDGE_BASE_OUTPUT}/")
        print("\nNext steps:")
        print("1. Review the JSON files in the knowledge-base-data directory")
        print("2. Upload to S3: aws s3 sync ./knowledge-base-data/ s3://autocorp-datalake-dev/knowledge-base/")
        print("3. Deploy Bedrock module: cd terraform && terraform apply -target=module.bedrock")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
