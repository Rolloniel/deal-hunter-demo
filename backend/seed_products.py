"""Seed the Supabase products table with a realistic product catalog."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from app.db import get_db

PRODUCTS = [
    # === TVs ===
    {"name": "Samsung 65\" QLED 4K Smart TV", "category": "TV", "current_price": 997.99, "original_price": 997.99, "image_url": None},
    {"name": "LG 55\" OLED evo C4 Smart TV", "category": "TV", "current_price": 1296.99, "original_price": 1296.99, "image_url": None},
    {"name": "Sony 75\" Bravia XR 4K TV", "category": "TV", "current_price": 1798.00, "original_price": 1798.00, "image_url": None},
    {"name": "TCL 50\" Class S4 4K LED Smart TV", "category": "TV", "current_price": 219.99, "original_price": 219.99, "image_url": None},
    {"name": "Hisense 65\" U8N Mini-LED ULED 4K TV", "category": "TV", "current_price": 899.99, "original_price": 899.99, "image_url": None},
    {"name": "Vizio 43\" V-Series 4K Smart TV", "category": "TV", "current_price": 178.00, "original_price": 178.00, "image_url": None},
    {"name": "Samsung 55\" The Frame QLED 4K TV", "category": "TV", "current_price": 1277.99, "original_price": 1277.99, "image_url": None},
    {"name": "LG 48\" C4 OLED Gaming TV", "category": "TV", "current_price": 1096.99, "original_price": 1096.99, "image_url": None},

    # === Laptops ===
    {"name": "MacBook Air 15\" M3 Chip 16GB", "category": "Laptop", "current_price": 1299.00, "original_price": 1299.00, "image_url": None},
    {"name": "MacBook Pro 14\" M3 Pro 18GB", "category": "Laptop", "current_price": 1999.00, "original_price": 1999.00, "image_url": None},
    {"name": "Dell XPS 14 Intel Ultra 7", "category": "Laptop", "current_price": 1399.99, "original_price": 1399.99, "image_url": None},
    {"name": "Lenovo ThinkPad X1 Carbon Gen 12", "category": "Laptop", "current_price": 1549.00, "original_price": 1549.00, "image_url": None},
    {"name": "HP Spectre x360 14\" 2-in-1", "category": "Laptop", "current_price": 1449.99, "original_price": 1449.99, "image_url": None},
    {"name": "ASUS ROG Zephyrus G14 RTX 4060", "category": "Laptop", "current_price": 1399.99, "original_price": 1399.99, "image_url": None},
    {"name": "Acer Swift Go 14 OLED", "category": "Laptop", "current_price": 849.99, "original_price": 849.99, "image_url": None},
    {"name": "Lenovo IdeaPad Slim 5 16\"", "category": "Laptop", "current_price": 629.99, "original_price": 629.99, "image_url": None},
    {"name": "Samsung Galaxy Book4 Pro 16\"", "category": "Laptop", "current_price": 1449.99, "original_price": 1449.99, "image_url": None},

    # === Headphones ===
    {"name": "Sony WH-1000XM5 Wireless Headphones", "category": "Headphones", "current_price": 348.00, "original_price": 348.00, "image_url": None},
    {"name": "Apple AirPods Max USB-C", "category": "Headphones", "current_price": 499.00, "original_price": 499.00, "image_url": None},
    {"name": "Bose QuietComfort Ultra Headphones", "category": "Headphones", "current_price": 379.00, "original_price": 379.00, "image_url": None},
    {"name": "Sennheiser Momentum 4 Wireless", "category": "Headphones", "current_price": 299.95, "original_price": 299.95, "image_url": None},
    {"name": "Sony WH-1000XM4 Headphones", "category": "Headphones", "current_price": 228.00, "original_price": 228.00, "image_url": None},
    {"name": "Beats Studio Pro Wireless", "category": "Headphones", "current_price": 249.99, "original_price": 249.99, "image_url": None},
    {"name": "JBL Tune 770NC Wireless", "category": "Headphones", "current_price": 79.95, "original_price": 79.95, "image_url": None},
    {"name": "Audio-Technica ATH-M50xBT2", "category": "Headphones", "current_price": 179.00, "original_price": 179.00, "image_url": None},

    # === Earbuds ===
    {"name": "Apple AirPods Pro 2nd Gen USB-C", "category": "Earbuds", "current_price": 189.99, "original_price": 189.99, "image_url": None},
    {"name": "Samsung Galaxy Buds3 Pro", "category": "Earbuds", "current_price": 249.99, "original_price": 249.99, "image_url": None},
    {"name": "Sony WF-1000XM5 Earbuds", "category": "Earbuds", "current_price": 278.00, "original_price": 278.00, "image_url": None},
    {"name": "Bose QuietComfort Ultra Earbuds", "category": "Earbuds", "current_price": 279.00, "original_price": 279.00, "image_url": None},
    {"name": "Google Pixel Buds Pro 2", "category": "Earbuds", "current_price": 229.00, "original_price": 229.00, "image_url": None},
    {"name": "Jabra Elite 10 Gen 2", "category": "Earbuds", "current_price": 279.99, "original_price": 279.99, "image_url": None},

    # === Speakers ===
    {"name": "Sonos Era 300 Spatial Audio Speaker", "category": "Speakers", "current_price": 449.00, "original_price": 449.00, "image_url": None},
    {"name": "JBL Charge 5 Portable Speaker", "category": "Speakers", "current_price": 149.95, "original_price": 149.95, "image_url": None},
    {"name": "Bose SoundLink Flex Bluetooth Speaker", "category": "Speakers", "current_price": 119.00, "original_price": 119.00, "image_url": None},
    {"name": "Apple HomePod 2nd Gen", "category": "Speakers", "current_price": 299.00, "original_price": 299.00, "image_url": None},
    {"name": "Marshall Stanmore III Bluetooth Speaker", "category": "Speakers", "current_price": 379.99, "original_price": 379.99, "image_url": None},
    {"name": "Sonos Roam 2 Portable Speaker", "category": "Speakers", "current_price": 179.00, "original_price": 179.00, "image_url": None},

    # === Tablets ===
    {"name": "Apple iPad Air 13\" M2 256GB", "category": "Tablet", "current_price": 799.00, "original_price": 799.00, "image_url": None},
    {"name": "Samsung Galaxy Tab S9 FE 128GB", "category": "Tablet", "current_price": 349.99, "original_price": 349.99, "image_url": None},
    {"name": "Apple iPad 10th Gen 64GB", "category": "Tablet", "current_price": 349.00, "original_price": 349.00, "image_url": None},
    {"name": "Samsung Galaxy Tab S10 Ultra", "category": "Tablet", "current_price": 1199.99, "original_price": 1199.99, "image_url": None},
    {"name": "Lenovo Tab P12 128GB", "category": "Tablet", "current_price": 289.99, "original_price": 289.99, "image_url": None},
    {"name": "Apple iPad Pro 13\" M4 256GB", "category": "Tablet", "current_price": 1299.00, "original_price": 1299.00, "image_url": None},

    # === Phones ===
    {"name": "Apple iPhone 16 Pro 256GB", "category": "Phone", "current_price": 1099.00, "original_price": 1099.00, "image_url": None},
    {"name": "Samsung Galaxy S25 Ultra 256GB", "category": "Phone", "current_price": 1299.99, "original_price": 1299.99, "image_url": None},
    {"name": "Google Pixel 9 Pro 128GB", "category": "Phone", "current_price": 999.00, "original_price": 999.00, "image_url": None},
    {"name": "Apple iPhone 16 128GB", "category": "Phone", "current_price": 799.00, "original_price": 799.00, "image_url": None},
    {"name": "Samsung Galaxy S25 128GB", "category": "Phone", "current_price": 799.99, "original_price": 799.99, "image_url": None},
    {"name": "Google Pixel 9 128GB", "category": "Phone", "current_price": 799.00, "original_price": 799.00, "image_url": None},
    {"name": "OnePlus 13 256GB", "category": "Phone", "current_price": 899.99, "original_price": 899.99, "image_url": None},

    # === Gaming ===
    {"name": "PlayStation 5 Slim Console", "category": "Gaming", "current_price": 449.99, "original_price": 449.99, "image_url": None},
    {"name": "Xbox Series X 1TB Console", "category": "Gaming", "current_price": 499.99, "original_price": 499.99, "image_url": None},
    {"name": "Nintendo Switch OLED Model", "category": "Gaming", "current_price": 349.99, "original_price": 349.99, "image_url": None},
    {"name": "Steam Deck OLED 512GB", "category": "Gaming", "current_price": 549.00, "original_price": 549.00, "image_url": None},
    {"name": "Meta Quest 3 128GB VR Headset", "category": "Gaming", "current_price": 499.99, "original_price": 499.99, "image_url": None},
    {"name": "Razer DeathAdder V3 Pro Mouse", "category": "Gaming", "current_price": 149.99, "original_price": 149.99, "image_url": None},
    {"name": "SteelSeries Arctis Nova Pro Wireless Headset", "category": "Gaming", "current_price": 349.99, "original_price": 349.99, "image_url": None},
    {"name": "ASUS ROG Swift 27\" 1440p 180Hz Monitor", "category": "Gaming", "current_price": 599.99, "original_price": 599.99, "image_url": None},

    # === Home & Smart Home ===
    {"name": "Dyson V15 Detect Cordless Vacuum", "category": "Home", "current_price": 749.99, "original_price": 749.99, "image_url": None},
    {"name": "iRobot Roomba j9+ Self-Emptying Robot Vacuum", "category": "Home", "current_price": 599.99, "original_price": 599.99, "image_url": None},
    {"name": "Amazon Echo Show 10 3rd Gen", "category": "Home", "current_price": 249.99, "original_price": 249.99, "image_url": None},
    {"name": "Google Nest Learning Thermostat 4th Gen", "category": "Home", "current_price": 279.99, "original_price": 279.99, "image_url": None},
    {"name": "Ring Video Doorbell Pro 2", "category": "Home", "current_price": 219.99, "original_price": 219.99, "image_url": None},
    {"name": "Philips Hue Starter Kit 4-Pack", "category": "Home", "current_price": 179.99, "original_price": 179.99, "image_url": None},
    {"name": "Ninja Creami Ice Cream Maker", "category": "Home", "current_price": 199.99, "original_price": 199.99, "image_url": None},
    {"name": "KitchenAid Artisan 5-Quart Stand Mixer", "category": "Home", "current_price": 379.99, "original_price": 379.99, "image_url": None},
    {"name": "Breville Barista Express Espresso Machine", "category": "Home", "current_price": 599.95, "original_price": 599.95, "image_url": None},

    # === Fitness ===
    {"name": "Apple Watch Ultra 2 49mm", "category": "Fitness", "current_price": 799.00, "original_price": 799.00, "image_url": None},
    {"name": "Garmin Forerunner 265 GPS Watch", "category": "Fitness", "current_price": 399.99, "original_price": 399.99, "image_url": None},
    {"name": "Fitbit Charge 6 Fitness Tracker", "category": "Fitness", "current_price": 139.95, "original_price": 139.95, "image_url": None},
    {"name": "Peloton Bike+ Indoor Exercise Bike", "category": "Fitness", "current_price": 2495.00, "original_price": 2495.00, "image_url": None},
    {"name": "Theragun Pro Plus Massage Gun", "category": "Fitness", "current_price": 449.00, "original_price": 449.00, "image_url": None},
    {"name": "Whoop 4.0 Fitness Band", "category": "Fitness", "current_price": 239.00, "original_price": 239.00, "image_url": None},
    {"name": "Samsung Galaxy Watch Ultra 47mm", "category": "Fitness", "current_price": 649.99, "original_price": 649.99, "image_url": None},
    {"name": "Oura Ring Gen 3 Heritage", "category": "Fitness", "current_price": 299.00, "original_price": 299.00, "image_url": None},

    # === Cameras ===
    {"name": "Sony Alpha a7 IV Mirrorless Camera", "category": "Camera", "current_price": 2298.00, "original_price": 2298.00, "image_url": None},
    {"name": "Canon EOS R6 Mark II Body", "category": "Camera", "current_price": 2299.00, "original_price": 2299.00, "image_url": None},
    {"name": "GoPro HERO13 Black", "category": "Camera", "current_price": 349.99, "original_price": 349.99, "image_url": None},
    {"name": "DJI Mini 4 Pro Drone", "category": "Camera", "current_price": 759.00, "original_price": 759.00, "image_url": None},
    {"name": "Fujifilm X-T5 Mirrorless Camera", "category": "Camera", "current_price": 1699.00, "original_price": 1699.00, "image_url": None},
    {"name": "Insta360 X4 360° Action Camera", "category": "Camera", "current_price": 499.99, "original_price": 499.99, "image_url": None},
]


def seed():
    """Insert products into Supabase, skipping duplicates by name."""
    db = get_db()

    # Get existing product names to avoid duplicates
    existing = db.table("products").select("name").execute()
    existing_names = {p["name"] for p in existing.data}

    new_products = [p for p in PRODUCTS if p["name"] not in existing_names]

    if not new_products:
        print(f"All {len(PRODUCTS)} products already exist. Nothing to seed.")
        return

    # Insert in batches of 20
    inserted = 0
    for i in range(0, len(new_products), 20):
        batch = new_products[i : i + 20]
        result = db.table("products").insert(batch).execute()
        inserted += len(result.data)
        print(f"  Inserted batch {i // 20 + 1}: {len(result.data)} products")

    print(f"Seeded {inserted} new products ({len(existing_names)} already existed).")
    print(f"Total catalog: {len(existing_names) + inserted} products across {len(set(p['category'] for p in PRODUCTS))} categories.")


if __name__ == "__main__":
    seed()
