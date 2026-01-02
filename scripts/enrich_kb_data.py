#!/usr/bin/env python3
"""
Enrich AutoCorp data with natural language descriptions for better semantic search.

This script transforms structured JSON data into semantically rich text that
improves embedding quality and retrieval scores.
"""

import json
import psycopg2
from typing import List, Dict

# Database connection
DB_CONFIG = {
    'dbname': 'autocorp',
    'user': 'scotton',
    'host': 'localhost'
}

def parse_currency(value) -> float:
    """Convert currency string or numeric value to float."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove currency symbols, commas, and spaces
        cleaned = value.replace('$', '').replace(',', '').strip()
        return float(cleaned)
    return float(value)

def create_enriched_part_text(part: Dict) -> str:
    """
    Transform part data into rich, natural language description.
    
    Example output:
    "The [Part Name] is an automotive part available from [Vendor] for $[Price].
    This part is commonly needed for [use cases]. SKU: [SKU]. 
    Keywords: [related terms]"
    """
    name = part['name']
    sku = part['sku']
    vendor = part['vendor']
    price = part['price']
    
    # Add semantic context based on part type
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


def get_use_cases_for_part(part_name: str) -> str:
    """Add semantic context about when/why this part is needed."""
    use_case_map = {
        'battery': 'vehicle starting issues, dead battery replacement, electrical system upgrades',
        'brake': 'brake repairs, safety inspections, brake system maintenance, stopping problems',
        'oil': 'routine maintenance, oil changes, engine lubrication, preventive service',
        'filter': 'engine maintenance, air quality, fluid filtration, regular service intervals',
        'tire': 'tire replacement, seasonal changes, tread wear, vehicle safety',
        'spark plug': 'engine tune-ups, misfiring engine, poor fuel economy, starting problems',
        'alternator': 'charging system problems, battery not charging, electrical issues',
        'starter': 'engine won\'t start, starting problems, ignition system repairs',
        'radiator': 'cooling system repairs, overheating problems, engine temperature issues',
        'sensor': 'diagnostic trouble codes, check engine light, system monitoring',
        'belt': 'routine maintenance, squealing noises, accessory drive system',
        'pump': 'fluid circulation, system pressure, component replacement',
        'gasket': 'leak repairs, engine rebuilds, seal replacement',
        'fluid': 'system maintenance, fluid changes, level top-offs',
    }
    
    part_lower = part_name.lower()
    for keyword, use_case in use_case_map.items():
        if keyword in part_lower:
            return use_case
    
    return 'vehicle repairs and maintenance'


def get_keywords_for_part(part_name: str) -> str:
    """Generate related keywords for better semantic matching."""
    keyword_map = {
        'battery': 'car battery, dead battery, battery replacement, charging, electrical',
        'brake': 'braking, stopping, brake pads, rotors, brake system, safety',
        'oil': 'motor oil, lubricant, oil change, engine oil, maintenance',
        'filter': 'air filter, oil filter, cabin filter, filtration, maintenance',
        'tire': 'tires, wheels, tread, rubber, tire pressure, alignment',
        'spark plug': 'ignition, combustion, plugs, tune-up, engine performance',
        'sensor': 'diagnostic, monitoring, detection, electronic, computer',
        'belt': 'serpentine belt, timing belt, drive belt, accessories',
        'fluid': 'liquid, coolant, transmission fluid, brake fluid, hydraulic',
    }
    
    part_lower = part_name.lower()
    for keyword, synonyms in keyword_map.items():
        if keyword in part_lower:
            return synonyms
    
    return part_name.lower()


def categorize_part(part_name: str) -> str:
    """Categorize part into a system category."""
    categories = {
        'electrical': ['battery', 'alternator', 'starter', 'sensor', 'switch', 'relay'],
        'engine': ['oil', 'spark plug', 'gasket', 'piston', 'valve', 'manifold'],
        'braking': ['brake', 'rotor', 'caliper', 'brake pad'],
        'cooling': ['radiator', 'coolant', 'thermostat', 'fan', 'hose'],
        'fuel': ['fuel pump', 'fuel filter', 'injector'],
        'suspension': ['shock', 'strut', 'spring', 'bushing'],
        'exhaust': ['muffler', 'catalytic', 'exhaust', 'pipe'],
        'transmission': ['transmission', 'clutch', 'gear'],
    }
    
    part_lower = part_name.lower()
    for category, keywords in categories.items():
        if any(kw in part_lower for kw in keywords):
            return category
    
    return 'general automotive'


def create_enriched_service_text(service: Dict) -> str:
    """
    Transform service data into rich, natural language description.
    
    Example output:
    "We offer [Service Name] service in our [Category] department.
    This service addresses [problems]. Labor cost is $[X] and takes approximately
    [Y] minutes. Common reasons customers need this: [reasons]."
    """
    name = service['name']
    category = service['category']
    labor_cost = service['labor_cost']
    labor_minutes = service['labor_minutes']
    service_id = service['serviceid']
    
    # Add semantic context
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


def get_problems_for_service(service_name: str) -> str:
    """Describe what problems this service solves."""
    problem_map = {
        'brake': 'poor braking performance, squealing noises, reduced stopping power, safety concerns',
        'battery': 'car won\'t start, dead battery, weak starting, electrical problems',
        'oil': 'engine wear prevention, maintaining lubrication, extending engine life',
        'tire': 'uneven wear, vibration, poor handling, safety issues',
        'alignment': 'vehicle pulling, uneven tire wear, steering problems',
        'inspection': 'safety compliance, pre-purchase evaluation, maintenance planning',
        'diagnostic': 'check engine light, performance issues, unknown problems',
        'fluid': 'system maintenance, preventing damage, ensuring proper operation',
        'belt': 'accessory failure, squealing noises, preventing breakdowns',
        'coolant': 'overheating, engine temperature regulation, cooling system health',
    }
    
    service_lower = service_name.lower()
    for keyword, problems in problem_map.items():
        if keyword in service_lower:
            return problems
    
    return 'vehicle maintenance and repair needs'


def get_customer_reasons(service_name: str) -> str:
    """Explain why customers typically request this service."""
    reason_map = {
        'brake': 'hearing squealing sounds, feeling vibration when braking, brake warning light',
        'battery': 'car won\'t start, dim lights, electrical issues',
        'oil': 'routine maintenance schedule, oil change reminder, engine protection',
        'tire': 'seasonal tire change, new tire installation, tire damage',
        'alignment': 'after hitting a pothole, uneven tire wear noticed, steering wheel off-center',
        'inspection': 'annual safety check, buying/selling vehicle, registration renewal',
        'diagnostic': 'warning lights on, strange noises, performance problems',
        'fluid': 'scheduled maintenance, fluid leak noticed, color change in fluid',
    }
    
    service_lower = service_name.lower()
    for keyword, reasons in reason_map.items():
        if keyword in service_lower:
            return reasons
    
    return 'maintaining vehicle reliability and safety'


def create_enriched_service_part_text(service_part: Dict) -> str:
    """
    Transform service-part mapping into rich description.
    
    Example:
    "The [Service Name] service requires [Part Name] as a component.
    This part is essential because [reason]. Quantity needed: [X]."
    """
    service_name = service_part.get('service_name', 'Unknown Service')
    part_name = service_part.get('part_name', 'Unknown Part')
    quantity = service_part.get('quantity', 1)
    
    text = f"""The {service_name} service requires {part_name} as a component. """
    
    if quantity > 1:
        text += f"This service uses {quantity} units of this part. "
    
    text += f"When booking {service_name}, {part_name} is included as a necessary material. "
    text += f"Service: {service_name}. Part: {part_name}. Quantity: {quantity}."
    
    return text


def fetch_and_enrich_parts(conn) -> List[Dict]:
    """Fetch parts from database and enrich with semantic text."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sku, name, vendor, price
        FROM auto_parts
        ORDER BY name
    """)
    
    enriched_parts = []
    for row in cursor.fetchall():
        part = {
            'id': f'part-{row[0]}',
            'type': 'auto_part',
            'sku': row[0],
            'name': row[1],
            'vendor': row[2],
            'price': parse_currency(row[3]),
        }
        part['text'] = create_enriched_part_text(part)
        enriched_parts.append(part)
    
    cursor.close()
    return enriched_parts


def fetch_and_enrich_services(conn) -> List[Dict]:
    """Fetch services from database and enrich with semantic text."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT serviceid, service, category, labor_cost, labor_minutes
        FROM service
        ORDER BY service
    """)
    
    enriched_services = []
    for row in cursor.fetchall():
        service = {
            'id': f'service-{row[0]}',
            'type': 'service',
            'serviceid': row[0],
            'name': row[1],
            'category': row[2],
            'labor_cost': parse_currency(row[3]),
            'labor_minutes': int(row[4]),
        }
        service['text'] = create_enriched_service_text(service)
        enriched_services.append(service)
    
    cursor.close()
    return enriched_services


def fetch_and_enrich_service_parts(conn) -> List[Dict]:
    """Fetch service-part mappings and enrich with semantic text."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sp.serviceid, s.service, sp.sku, ap.name, sp.quantity
        FROM service_parts sp
        JOIN service s ON sp.serviceid = s.serviceid
        JOIN auto_parts ap ON sp.sku = ap.sku
        ORDER BY s.service, ap.name
    """)
    
    enriched_mappings = []
    for row in cursor.fetchall():
        mapping = {
            'id': f'servicepart-{row[0]}-{row[2]}',
            'type': 'service_part_mapping',
            'serviceid': row[0],
            'service_name': row[1],
            'sku': row[2],
            'part_name': row[3],
            'quantity': int(row[4]),
        }
        mapping['text'] = create_enriched_service_part_text(mapping)
        enriched_mappings.append(mapping)
    
    cursor.close()
    return enriched_mappings


def main():
    """Generate enriched knowledge base files."""
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    print("Enriching auto parts data...")
    parts = fetch_and_enrich_parts(conn)
    # Write as JSONL (one JSON object per line) for proper Bedrock parsing
    with open('auto_parts_enriched.jsonl', 'w') as f:
        for part in parts:
            f.write(json.dumps(part) + '\n')
    print(f"✅ Created auto_parts_enriched.jsonl ({len(parts)} parts)")
    
    print("Enriching services data...")
    services = fetch_and_enrich_services(conn)
    with open('services_enriched.jsonl', 'w') as f:
        for service in services:
            f.write(json.dumps(service) + '\n')
    print(f"✅ Created services_enriched.jsonl ({len(services)} services)")
    
    print("Enriching service-part mappings...")
    mappings = fetch_and_enrich_service_parts(conn)
    with open('service_parts_enriched.jsonl', 'w') as f:
        for mapping in mappings:
            f.write(json.dumps(mapping) + '\n')
    print(f"✅ Created service_parts_enriched.jsonl ({len(mappings)} mappings)")
    
    conn.close()
    
    print("\n" + "="*60)
    print("Sample enriched part:")
    print("="*60)
    print(parts[0]['text'])
    
    print("\n" + "="*60)
    print("Sample enriched service:")
    print("="*60)
    print(services[0]['text'])
    
    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("1. Upload enriched JSONL files:")
    print("   aws s3 cp auto_parts_enriched.jsonl s3://autocorp-datalake-dev/knowledge-base/")
    print("   aws s3 cp services_enriched.jsonl s3://autocorp-datalake-dev/knowledge-base/")
    print("   aws s3 cp service_parts_enriched.jsonl s3://autocorp-datalake-dev/knowledge-base/")
    print("")
    print("2. Remove old JSON array files (if they exist):")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/auto_parts_enriched.json")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/services_enriched.json")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/service_parts_enriched.json")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/auto_parts.json")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/services.json")
    print("   aws s3 rm s3://autocorp-datalake-dev/knowledge-base/service_parts.json")
    print("")
    print("3. Re-ingest knowledge base:")
    print("   aws bedrock-agent start-ingestion-job --knowledge-base-id UQSLM6QEVT --data-source-id GWCPMZICOY --region us-east-1")


if __name__ == '__main__':
    main()
