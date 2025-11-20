from faker import Faker
import random
import string
import csv

fake = Faker()

def generate_sku(length=16):
    """Generate alphanumeric SKU of given length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_auto_part():
    return {
        "sku": generate_sku(16),
        "name": fake.text(max_nb_chars=24).strip().replace("\n", " "),
        "description": fake.text(max_nb_chars=500).strip().replace("\n", " "),
        "inventory_date": fake.date_between(start_date="-2y", end_date="today"),
        "price": round(random.uniform(5.0, 500.0), 2)
    }

if __name__ == "__main__":
    # Generate 50 auto parts (adjust as needed)
    auto_parts = [generate_auto_part() for _ in range(50)]

    # Write to CSV file
    with open("auto-parts.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["sku", "name", "description", "inventory_date", "price"])
        writer.writeheader()
        writer.writerows(auto_parts)

    print("CSV file 'auto-parts.csv' has been created with", len(auto_parts), "records.")
