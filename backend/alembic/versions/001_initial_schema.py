"""Initial schema with all tables and seed data.

Revision ID: 001
Revises:
Create Date: 2026-03-08
"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Product seed data — copied from backend/seed_products.py
PRODUCTS = [
    {"name": "Samsung 65\" QLED 4K Smart TV", "category": "TV", "current_price": 997.99, "original_price": 997.99, "image_url": "https://picsum.photos/seed/samsung-65-qled-4k-smart-tv/400/300"},
    {"name": "LG 55\" OLED evo C4 Smart TV", "category": "TV", "current_price": 1296.99, "original_price": 1296.99, "image_url": "https://picsum.photos/seed/lg-55-oled-evo-c4-smart-tv/400/300"},
    {"name": "Sony 75\" Bravia XR 4K TV", "category": "TV", "current_price": 1798.00, "original_price": 1798.00, "image_url": "https://picsum.photos/seed/sony-75-bravia-xr-4k-tv/400/300"},
    {"name": "TCL 50\" Class S4 4K LED Smart TV", "category": "TV", "current_price": 219.99, "original_price": 219.99, "image_url": "https://picsum.photos/seed/tcl-50-class-s4-4k-led-smart-tv/400/300"},
    {"name": "Hisense 65\" U8N Mini-LED ULED 4K TV", "category": "TV", "current_price": 899.99, "original_price": 899.99, "image_url": "https://picsum.photos/seed/hisense-65-u8n-mini-led-uled-4k-tv/400/300"},
    {"name": "Vizio 43\" V-Series 4K Smart TV", "category": "TV", "current_price": 178.00, "original_price": 178.00, "image_url": "https://picsum.photos/seed/vizio-43-v-series-4k-smart-tv/400/300"},
    {"name": "Samsung 55\" The Frame QLED 4K TV", "category": "TV", "current_price": 1277.99, "original_price": 1277.99, "image_url": "https://picsum.photos/seed/samsung-55-the-frame-qled-4k-tv/400/300"},
    {"name": "LG 48\" C4 OLED Gaming TV", "category": "TV", "current_price": 1096.99, "original_price": 1096.99, "image_url": "https://picsum.photos/seed/lg-48-c4-oled-gaming-tv/400/300"},
    {"name": "MacBook Air 15\" M3 Chip 16GB", "category": "Laptop", "current_price": 1299.00, "original_price": 1299.00, "image_url": "https://picsum.photos/seed/macbook-air-15-m3-chip-16gb/400/300"},
    {"name": "MacBook Pro 14\" M3 Pro 18GB", "category": "Laptop", "current_price": 1999.00, "original_price": 1999.00, "image_url": "https://picsum.photos/seed/macbook-pro-14-m3-pro-18gb/400/300"},
    {"name": "Dell XPS 14 Intel Ultra 7", "category": "Laptop", "current_price": 1399.99, "original_price": 1399.99, "image_url": "https://picsum.photos/seed/dell-xps-14-intel-ultra-7/400/300"},
    {"name": "Lenovo ThinkPad X1 Carbon Gen 12", "category": "Laptop", "current_price": 1549.00, "original_price": 1549.00, "image_url": "https://picsum.photos/seed/lenovo-thinkpad-x1-carbon-gen-12/400/300"},
    {"name": "HP Spectre x360 14\" 2-in-1", "category": "Laptop", "current_price": 1449.99, "original_price": 1449.99, "image_url": "https://picsum.photos/seed/hp-spectre-x360-14-2-in-1/400/300"},
    {"name": "ASUS ROG Zephyrus G14 RTX 4060", "category": "Laptop", "current_price": 1399.99, "original_price": 1399.99, "image_url": "https://picsum.photos/seed/asus-rog-zephyrus-g14-rtx-4060/400/300"},
    {"name": "Acer Swift Go 14 OLED", "category": "Laptop", "current_price": 849.99, "original_price": 849.99, "image_url": "https://picsum.photos/seed/acer-swift-go-14-oled/400/300"},
    {"name": "Lenovo IdeaPad Slim 5 16\"", "category": "Laptop", "current_price": 629.99, "original_price": 629.99, "image_url": "https://picsum.photos/seed/lenovo-ideapad-slim-5-16/400/300"},
    {"name": "Samsung Galaxy Book4 Pro 16\"", "category": "Laptop", "current_price": 1449.99, "original_price": 1449.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-book4-pro-16/400/300"},
    {"name": "Sony WH-1000XM5 Wireless Headphones", "category": "Headphones", "current_price": 348.00, "original_price": 348.00, "image_url": "https://picsum.photos/seed/sony-wh-1000xm5-wireless-headphones/400/300"},
    {"name": "Apple AirPods Max USB-C", "category": "Headphones", "current_price": 499.00, "original_price": 499.00, "image_url": "https://picsum.photos/seed/apple-airpods-max-usb-c/400/300"},
    {"name": "Bose QuietComfort Ultra Headphones", "category": "Headphones", "current_price": 379.00, "original_price": 379.00, "image_url": "https://picsum.photos/seed/bose-quietcomfort-ultra-headphones/400/300"},
    {"name": "Sennheiser Momentum 4 Wireless", "category": "Headphones", "current_price": 299.95, "original_price": 299.95, "image_url": "https://picsum.photos/seed/sennheiser-momentum-4-wireless/400/300"},
    {"name": "Sony WH-1000XM4 Headphones", "category": "Headphones", "current_price": 228.00, "original_price": 228.00, "image_url": "https://picsum.photos/seed/sony-wh-1000xm4-headphones/400/300"},
    {"name": "Beats Studio Pro Wireless", "category": "Headphones", "current_price": 249.99, "original_price": 249.99, "image_url": "https://picsum.photos/seed/beats-studio-pro-wireless/400/300"},
    {"name": "JBL Tune 770NC Wireless", "category": "Headphones", "current_price": 79.95, "original_price": 79.95, "image_url": "https://picsum.photos/seed/jbl-tune-770nc-wireless/400/300"},
    {"name": "Audio-Technica ATH-M50xBT2", "category": "Headphones", "current_price": 179.00, "original_price": 179.00, "image_url": "https://picsum.photos/seed/audio-technica-ath-m50xbt2/400/300"},
    {"name": "Apple AirPods Pro 2nd Gen USB-C", "category": "Earbuds", "current_price": 189.99, "original_price": 189.99, "image_url": "https://picsum.photos/seed/apple-airpods-pro-2nd-gen-usb-c/400/300"},
    {"name": "Samsung Galaxy Buds3 Pro", "category": "Earbuds", "current_price": 249.99, "original_price": 249.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-buds3-pro/400/300"},
    {"name": "Sony WF-1000XM5 Earbuds", "category": "Earbuds", "current_price": 278.00, "original_price": 278.00, "image_url": "https://picsum.photos/seed/sony-wf-1000xm5-earbuds/400/300"},
    {"name": "Bose QuietComfort Ultra Earbuds", "category": "Earbuds", "current_price": 279.00, "original_price": 279.00, "image_url": "https://picsum.photos/seed/bose-quietcomfort-ultra-earbuds/400/300"},
    {"name": "Google Pixel Buds Pro 2", "category": "Earbuds", "current_price": 229.00, "original_price": 229.00, "image_url": "https://picsum.photos/seed/google-pixel-buds-pro-2/400/300"},
    {"name": "Jabra Elite 10 Gen 2", "category": "Earbuds", "current_price": 279.99, "original_price": 279.99, "image_url": "https://picsum.photos/seed/jabra-elite-10-gen-2/400/300"},
    {"name": "Sonos Era 300 Spatial Audio Speaker", "category": "Speakers", "current_price": 449.00, "original_price": 449.00, "image_url": "https://picsum.photos/seed/sonos-era-300-spatial-audio-speaker/400/300"},
    {"name": "JBL Charge 5 Portable Speaker", "category": "Speakers", "current_price": 149.95, "original_price": 149.95, "image_url": "https://picsum.photos/seed/jbl-charge-5-portable-speaker/400/300"},
    {"name": "Bose SoundLink Flex Bluetooth Speaker", "category": "Speakers", "current_price": 119.00, "original_price": 119.00, "image_url": "https://picsum.photos/seed/bose-soundlink-flex-bluetooth-speaker/400/300"},
    {"name": "Apple HomePod 2nd Gen", "category": "Speakers", "current_price": 299.00, "original_price": 299.00, "image_url": "https://picsum.photos/seed/apple-homepod-2nd-gen/400/300"},
    {"name": "Marshall Stanmore III Bluetooth Speaker", "category": "Speakers", "current_price": 379.99, "original_price": 379.99, "image_url": "https://picsum.photos/seed/marshall-stanmore-iii-bluetooth-speaker/400/300"},
    {"name": "Sonos Roam 2 Portable Speaker", "category": "Speakers", "current_price": 179.00, "original_price": 179.00, "image_url": "https://picsum.photos/seed/sonos-roam-2-portable-speaker/400/300"},
    {"name": "Apple iPad Air 13\" M2 256GB", "category": "Tablet", "current_price": 799.00, "original_price": 799.00, "image_url": "https://picsum.photos/seed/apple-ipad-air-13-m2-256gb/400/300"},
    {"name": "Samsung Galaxy Tab S9 FE 128GB", "category": "Tablet", "current_price": 349.99, "original_price": 349.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-tab-s9-fe-128gb/400/300"},
    {"name": "Apple iPad 10th Gen 64GB", "category": "Tablet", "current_price": 349.00, "original_price": 349.00, "image_url": "https://picsum.photos/seed/apple-ipad-10th-gen-64gb/400/300"},
    {"name": "Samsung Galaxy Tab S10 Ultra", "category": "Tablet", "current_price": 1199.99, "original_price": 1199.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-tab-s10-ultra/400/300"},
    {"name": "Lenovo Tab P12 128GB", "category": "Tablet", "current_price": 289.99, "original_price": 289.99, "image_url": "https://picsum.photos/seed/lenovo-tab-p12-128gb/400/300"},
    {"name": "Apple iPad Pro 13\" M4 256GB", "category": "Tablet", "current_price": 1299.00, "original_price": 1299.00, "image_url": "https://picsum.photos/seed/apple-ipad-pro-13-m4-256gb/400/300"},
    {"name": "Apple iPhone 16 Pro 256GB", "category": "Phone", "current_price": 1099.00, "original_price": 1099.00, "image_url": "https://picsum.photos/seed/apple-iphone-16-pro-256gb/400/300"},
    {"name": "Samsung Galaxy S25 Ultra 256GB", "category": "Phone", "current_price": 1299.99, "original_price": 1299.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-s25-ultra-256gb/400/300"},
    {"name": "Google Pixel 9 Pro 128GB", "category": "Phone", "current_price": 999.00, "original_price": 999.00, "image_url": "https://picsum.photos/seed/google-pixel-9-pro-128gb/400/300"},
    {"name": "Apple iPhone 16 128GB", "category": "Phone", "current_price": 799.00, "original_price": 799.00, "image_url": "https://picsum.photos/seed/apple-iphone-16-128gb/400/300"},
    {"name": "Samsung Galaxy S25 128GB", "category": "Phone", "current_price": 799.99, "original_price": 799.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-s25-128gb/400/300"},
    {"name": "Google Pixel 9 128GB", "category": "Phone", "current_price": 799.00, "original_price": 799.00, "image_url": "https://picsum.photos/seed/google-pixel-9-128gb/400/300"},
    {"name": "OnePlus 13 256GB", "category": "Phone", "current_price": 899.99, "original_price": 899.99, "image_url": "https://picsum.photos/seed/oneplus-13-256gb/400/300"},
    {"name": "PlayStation 5 Slim Console", "category": "Gaming", "current_price": 449.99, "original_price": 449.99, "image_url": "https://picsum.photos/seed/playstation-5-slim-console/400/300"},
    {"name": "Xbox Series X 1TB Console", "category": "Gaming", "current_price": 499.99, "original_price": 499.99, "image_url": "https://picsum.photos/seed/xbox-series-x-1tb-console/400/300"},
    {"name": "Nintendo Switch OLED Model", "category": "Gaming", "current_price": 349.99, "original_price": 349.99, "image_url": "https://picsum.photos/seed/nintendo-switch-oled-model/400/300"},
    {"name": "Steam Deck OLED 512GB", "category": "Gaming", "current_price": 549.00, "original_price": 549.00, "image_url": "https://picsum.photos/seed/steam-deck-oled-512gb/400/300"},
    {"name": "Meta Quest 3 128GB VR Headset", "category": "Gaming", "current_price": 499.99, "original_price": 499.99, "image_url": "https://picsum.photos/seed/meta-quest-3-128gb-vr-headset/400/300"},
    {"name": "Razer DeathAdder V3 Pro Mouse", "category": "Gaming", "current_price": 149.99, "original_price": 149.99, "image_url": "https://picsum.photos/seed/razer-deathadder-v3-pro-mouse/400/300"},
    {"name": "SteelSeries Arctis Nova Pro Wireless Headset", "category": "Gaming", "current_price": 349.99, "original_price": 349.99, "image_url": "https://picsum.photos/seed/steelseries-arctis-nova-pro-wireless-headset/400/300"},
    {"name": "ASUS ROG Swift 27\" 1440p 180Hz Monitor", "category": "Gaming", "current_price": 599.99, "original_price": 599.99, "image_url": "https://picsum.photos/seed/asus-rog-swift-27-1440p-180hz-monitor/400/300"},
    {"name": "Dyson V15 Detect Cordless Vacuum", "category": "Home", "current_price": 749.99, "original_price": 749.99, "image_url": "https://picsum.photos/seed/dyson-v15-detect-cordless-vacuum/400/300"},
    {"name": "iRobot Roomba j9+ Self-Emptying Robot Vacuum", "category": "Home", "current_price": 599.99, "original_price": 599.99, "image_url": "https://picsum.photos/seed/irobot-roomba-j9-self-emptying-robot-vacuum/400/300"},
    {"name": "Amazon Echo Show 10 3rd Gen", "category": "Home", "current_price": 249.99, "original_price": 249.99, "image_url": "https://picsum.photos/seed/amazon-echo-show-10-3rd-gen/400/300"},
    {"name": "Google Nest Learning Thermostat 4th Gen", "category": "Home", "current_price": 279.99, "original_price": 279.99, "image_url": "https://picsum.photos/seed/google-nest-learning-thermostat-4th-gen/400/300"},
    {"name": "Ring Video Doorbell Pro 2", "category": "Home", "current_price": 219.99, "original_price": 219.99, "image_url": "https://picsum.photos/seed/ring-video-doorbell-pro-2/400/300"},
    {"name": "Philips Hue Starter Kit 4-Pack", "category": "Home", "current_price": 179.99, "original_price": 179.99, "image_url": "https://picsum.photos/seed/philips-hue-starter-kit-4-pack/400/300"},
    {"name": "Ninja Creami Ice Cream Maker", "category": "Home", "current_price": 199.99, "original_price": 199.99, "image_url": "https://picsum.photos/seed/ninja-creami-ice-cream-maker/400/300"},
    {"name": "KitchenAid Artisan 5-Quart Stand Mixer", "category": "Home", "current_price": 379.99, "original_price": 379.99, "image_url": "https://picsum.photos/seed/kitchenaid-artisan-5-quart-stand-mixer/400/300"},
    {"name": "Breville Barista Express Espresso Machine", "category": "Home", "current_price": 599.95, "original_price": 599.95, "image_url": "https://picsum.photos/seed/breville-barista-express-espresso-machine/400/300"},
    {"name": "Apple Watch Ultra 2 49mm", "category": "Fitness", "current_price": 799.00, "original_price": 799.00, "image_url": "https://picsum.photos/seed/apple-watch-ultra-2-49mm/400/300"},
    {"name": "Garmin Forerunner 265 GPS Watch", "category": "Fitness", "current_price": 399.99, "original_price": 399.99, "image_url": "https://picsum.photos/seed/garmin-forerunner-265-gps-watch/400/300"},
    {"name": "Fitbit Charge 6 Fitness Tracker", "category": "Fitness", "current_price": 139.95, "original_price": 139.95, "image_url": "https://picsum.photos/seed/fitbit-charge-6-fitness-tracker/400/300"},
    {"name": "Peloton Bike+ Indoor Exercise Bike", "category": "Fitness", "current_price": 2495.00, "original_price": 2495.00, "image_url": "https://picsum.photos/seed/peloton-bike-indoor-exercise-bike/400/300"},
    {"name": "Theragun Pro Plus Massage Gun", "category": "Fitness", "current_price": 449.00, "original_price": 449.00, "image_url": "https://picsum.photos/seed/theragun-pro-plus-massage-gun/400/300"},
    {"name": "Whoop 4.0 Fitness Band", "category": "Fitness", "current_price": 239.00, "original_price": 239.00, "image_url": "https://picsum.photos/seed/whoop-4-0-fitness-band/400/300"},
    {"name": "Samsung Galaxy Watch Ultra 47mm", "category": "Fitness", "current_price": 649.99, "original_price": 649.99, "image_url": "https://picsum.photos/seed/samsung-galaxy-watch-ultra-47mm/400/300"},
    {"name": "Oura Ring Gen 3 Heritage", "category": "Fitness", "current_price": 299.00, "original_price": 299.00, "image_url": "https://picsum.photos/seed/oura-ring-gen-3-heritage/400/300"},
    {"name": "Sony Alpha a7 IV Mirrorless Camera", "category": "Camera", "current_price": 2298.00, "original_price": 2298.00, "image_url": "https://picsum.photos/seed/sony-alpha-a7-iv-mirrorless-camera/400/300"},
    {"name": "Canon EOS R6 Mark II Body", "category": "Camera", "current_price": 2299.00, "original_price": 2299.00, "image_url": "https://picsum.photos/seed/canon-eos-r6-mark-ii-body/400/300"},
    {"name": "GoPro HERO13 Black", "category": "Camera", "current_price": 349.99, "original_price": 349.99, "image_url": "https://picsum.photos/seed/gopro-hero13-black/400/300"},
    {"name": "DJI Mini 4 Pro Drone", "category": "Camera", "current_price": 759.00, "original_price": 759.00, "image_url": "https://picsum.photos/seed/dji-mini-4-pro-drone/400/300"},
    {"name": "Fujifilm X-T5 Mirrorless Camera", "category": "Camera", "current_price": 1699.00, "original_price": 1699.00, "image_url": "https://picsum.photos/seed/fujifilm-x-t5-mirrorless-camera/400/300"},
    {"name": "Insta360 X4 360 Action Camera", "category": "Camera", "current_price": 499.99, "original_price": 499.99, "image_url": "https://picsum.photos/seed/insta360-x4-360-action-camera/400/300"},
]


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Products table
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("current_price", sa.Float, nullable=False),
        sa.Column("original_price", sa.Float, nullable=True),
        sa.Column("image_url", sa.Text, nullable=True),
    )

    # Tracked items table
    op.create_table(
        "tracked_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_price", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_tracked_items_user_id", "tracked_items", ["user_id"])

    # Price history table
    op.create_table(
        "price_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Alerts table
    op.create_table(
        "alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tracked_item_id", UUID(as_uuid=True), sa.ForeignKey("tracked_items.id"), nullable=False),
        sa.Column("old_price", sa.Float, nullable=False),
        sa.Column("new_price", sa.Float, nullable=False),
        sa.Column("email_sent", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Seed products
    products_table = sa.table(
        "products",
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("current_price", sa.Float),
        sa.column("original_price", sa.Float),
        sa.column("image_url", sa.Text),
    )
    op.bulk_insert(products_table, PRODUCTS)


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("price_history")
    op.drop_table("tracked_items")
    op.drop_table("products")
    op.drop_table("users")
