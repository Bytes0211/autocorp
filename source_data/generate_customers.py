from faker import Faker
import csv
import os

# Initialize Faker
fake = Faker()

# Configuration
num_customers = 100000
output_file = 'customers.csv'
batch_size = 10000  # Batch size for memory-efficient generation

# Validate num_customers
if num_customers > 100000:
    raise ValueError("num_customers cannot be greater than 100000")


def generate_customer():
    """Generator function that yields customer dictionaries one at a time."""
    while True:
        yield {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip': fake.zipcode()
        }


# Generate customers and write to CSV
print(f"Generating {num_customers:,} customers...")

# Check if file exists to determine mode
file_exists = os.path.exists(output_file)
file_mode = 'a' if file_exists else 'w'

with open(output_file, file_mode, newline='', encoding='utf-8') as csvfile:
    fieldnames = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Only write header if creating new file
    if not file_exists:
        writer.writeheader()
    
    # Use generator for memory-efficient customer creation
    customer_generator = generate_customer()
    for i in range(num_customers):
        writer.writerow(next(customer_generator))
        
        # Progress indicator and flush every batch
        if (i + 1) % batch_size == 0:
            csvfile.flush()
            print(f"Generated {i + 1:,} customers...")

# Count total rows in the file (excluding header)
# with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
#     total_rows = sum(1 for _ in csv.reader(csvfile)) - 1  # Subtract 1 for header

print(f"Done! {num_customers:,} customers saved to {output_file}")
# print(f"Total rows in {output_file}: {total_rows:,}")
