# Supabase to Coolify VPS PostgreSQL Migration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace dead Supabase instance with Coolify-managed PostgreSQL and self-hosted OAuth via Authlib.

**Architecture:** Backend switches from Supabase Python SDK to SQLAlchemy + asyncpg for database, Authlib for OAuth (Google/GitHub), and PyJWT for cookie-based sessions. Frontend drops `@supabase/supabase-js` entirely — auth becomes backend-driven with httpOnly cookies, API calls use `credentials: 'include'` instead of Bearer tokens.

**Tech Stack:** SQLAlchemy (async), asyncpg, Alembic, Authlib, PyJWT, httpx

**Design doc:** `docs/plans/2026-03-08-supabase-to-postgres-design.md`

---

## Task 1: Database Foundation — SQLAlchemy, Models, Alembic

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/config.py`
- Rewrite: `backend/app/db.py`
- Create: `backend/app/models/tables.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/001_initial_schema.py`

### Step 1: Update requirements.txt

Replace `supabase>=2.0.0` with new dependencies:

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
httpx>=0.27.0
pydantic-settings>=2.0.0
openai>=1.0.0
resend>=0.8.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.30.0
alembic>=1.14.0
authlib>=1.4.0
pyjwt>=2.10.0
itsdangerous>=2.2.0
```

### Step 2: Update config.py

Replace Supabase settings with new config:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    resend_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dealhunter"

    # Auth
    jwt_secret: str = "change-me-in-production"
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    # App Config
    demo_alert_email: str = "alerts@kliuiev.com"
    frontend_url: str = "https://deals.kliuiev.com"

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### Step 3: Rewrite db.py

Replace Supabase client with SQLAlchemy async engine:

```python
"""Async database engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Yield an async database session."""
    async with async_session() as session:
        yield session
```

### Step 4: Create SQLAlchemy models

Create `backend/app/models/tables.py`:

```python
"""SQLAlchemy table models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tracked_items: Mapped[list["TrackedItem"]] = relationship(back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    original_price: Mapped[float] = mapped_column(Float, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)


class TrackedItem(Base):
    __tablename__ = "tracked_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="tracked_items")
    product: Mapped["Product"] = relationship()
    alerts: Mapped[list["Alert"]] = relationship(back_populates="tracked_item")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracked_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracked_items.id"), nullable=False)
    old_price: Mapped[float] = mapped_column(Float, nullable=False)
    new_price: Mapped[float] = mapped_column(Float, nullable=False)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tracked_item: Mapped["TrackedItem"] = relationship(back_populates="alerts")
```

Also create `backend/app/models/__init__.py` (empty file).

### Step 5: Set up Alembic

Create `backend/alembic.ini`:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `backend/alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.models.tables import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = get_settings().database_url
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(get_settings().database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

Create `backend/alembic/script.py.mako`:

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

Create `backend/alembic/versions/__init__.py` (empty).

### Step 6: Create initial migration

Create `backend/alembic/versions/001_initial_schema.py`:

```python
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
```

### Step 7: Update main.py to add DB lifecycle

Add startup/shutdown events to `backend/app/main.py`:

```python
from app.db import engine

# ... after app creation ...

@app.on_event("startup")
async def startup():
    # Verify DB connectivity
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT 1"))


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
```

Also register the new auth router (created in Task 3):

```python
from app.routers import chat, products, alerts, analytics, demo, auth
# ...
app.include_router(auth.router)
```

### Step 8: Verify locally

```bash
cd backend
pip install -r requirements.txt
```

Ensure `DATABASE_URL` is set in `.env` pointing to a local or Coolify Postgres instance. Run:

```bash
cd backend && alembic upgrade head
```

Expected: tables created, products seeded.

### Step 9: Commit

```bash
git add backend/requirements.txt backend/app/config.py backend/app/db.py \
  backend/app/models/ backend/alembic.ini backend/alembic/
git commit -m "feat: add SQLAlchemy + Alembic database foundation

Replace Supabase SDK with SQLAlchemy async engine, asyncpg,
and Alembic migrations. Initial migration creates all tables
and seeds product catalog."
```

---

## Task 2: Migrate Products Service to SQLAlchemy

**Files:**
- Rewrite: `backend/app/services/products.py`
- Modify: `backend/app/routers/products.py`

### Step 1: Rewrite products.py

Replace all Supabase query builder calls with SQLAlchemy. Key changes:
- All functions become `async` (were sync with Supabase SDK)
- Accept `AsyncSession` parameter instead of calling `get_db()`
- Use SQLAlchemy `select()`, `insert()`, `update()` statements

```python
"""Product service for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tables import Product, TrackedItem, PriceHistory


async def search_products(session: AsyncSession, name: str, limit: int = 5) -> list[dict]:
    """Search products by name (case-insensitive partial match)."""
    skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
    words = [w for w in name.split() if w.lower() not in skip_words]

    if len(words) > 1:
        pattern = "%" + "%".join(words) + "%"
    else:
        pattern = f"%{name}%"

    stmt = select(Product).where(Product.name.ilike(pattern)).limit(limit)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows and len(words) > 1:
        for word in words:
            if len(word) > 2:
                stmt = select(Product).where(Product.name.ilike(f"%{word}%")).limit(limit)
                result = await session.execute(stmt)
                rows = result.scalars().all()
                if rows:
                    break

    return [_product_to_dict(p) for p in rows]


async def search_catalog(
    session: AsyncSession,
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
) -> list[dict]:
    """Search the product catalog by name, category, and/or price range."""
    stmt = select(Product)
    filters = []

    pattern = None
    if query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        if len(words) > 1:
            pattern = "%" + "%".join(words) + "%"
        else:
            pattern = f"%{query}%"
        filters.append(Product.name.ilike(pattern))

    if category:
        filters.append(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        filters.append(Product.current_price >= min_price)
    if max_price is not None:
        filters.append(Product.current_price <= max_price)

    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    rows = result.scalars().all()

    # Word-by-word fallback if name query returned nothing
    if not rows and query:
        skip_words = {"inch", "inches", "the", "a", "an", "for", "with"}
        words = [w for w in query.split() if w.lower() not in skip_words]
        for word in words:
            if len(word) > 2:
                fallback_filters = [Product.name.ilike(f"%{word}%")]
                if category:
                    fallback_filters.append(Product.category.ilike(f"%{category}%"))
                if min_price is not None:
                    fallback_filters.append(Product.current_price >= min_price)
                if max_price is not None:
                    fallback_filters.append(Product.current_price <= max_price)
                stmt2 = select(Product).where(*fallback_filters).limit(limit)
                result = await session.execute(stmt2)
                rows = result.scalars().all()
                if rows:
                    break

    return [_product_to_dict(p) for p in rows]


async def get_product_categories(session: AsyncSession) -> list[str]:
    """Get all distinct product categories."""
    stmt = select(Product.category).distinct()
    result = await session.execute(stmt)
    return sorted(row[0] for row in result.all())


async def get_products_by_category(
    session: AsyncSession, category: str, max_price: Optional[float] = None, limit: int = 10
) -> list[dict]:
    """Get products by category with optional max price filter."""
    stmt = select(Product).where(Product.category.ilike(f"%{category}%"))
    if max_price:
        stmt = stmt.where(Product.current_price <= max_price)
    stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return [_product_to_dict(p) for p in result.scalars().all()]


async def create_tracked_item(
    session: AsyncSession, product_id: UUID, target_price: float, user_id: str
) -> dict:
    """Create a tracked item for a product."""
    item = TrackedItem(product_id=product_id, user_id=user_id, target_price=target_price)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return {"id": str(item.id), "product_id": str(item.product_id), "target_price": item.target_price}


async def get_tracked_item_by_product_id(
    session: AsyncSession, product_id: UUID, user_id: str | None = None
) -> Optional[dict]:
    """Check if a product is already being tracked."""
    stmt = select(TrackedItem).where(TrackedItem.product_id == product_id)
    if user_id:
        stmt = stmt.where(TrackedItem.user_id == user_id)
    stmt = stmt.limit(1)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        return None
    return {"id": str(item.id), "product_id": str(item.product_id), "target_price": item.target_price}


async def update_tracked_item_target_price(session: AsyncSession, item_id: str, target_price: float) -> dict:
    """Update the target price for an existing tracked item."""
    stmt = update(TrackedItem).where(TrackedItem.id == item_id).values(target_price=target_price)
    await session.execute(stmt)
    await session.commit()
    return {"id": item_id, "target_price": target_price}


async def get_tracked_items(session: AsyncSession, user_id: str | None = None) -> list[dict]:
    """Get all tracked items with product details."""
    stmt = select(TrackedItem).options(selectinload(TrackedItem.product))
    if user_id:
        stmt = stmt.where(TrackedItem.user_id == user_id)
    result = await session.execute(stmt)
    items = result.scalars().all()
    return [
        {
            "id": str(item.id),
            "product_id": str(item.product_id),
            "user_id": str(item.user_id),
            "target_price": item.target_price,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "products": _product_to_dict(item.product) if item.product else None,
        }
        for item in items
    ]


async def get_product_by_id(session: AsyncSession, product_id: UUID) -> Optional[dict]:
    """Get a single product by ID."""
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    return _product_to_dict(product) if product else None


async def get_price_history(session: AsyncSession, product_id: UUID, limit: int = 90) -> list[dict]:
    """Get price history for a product, ordered by date ascending."""
    stmt = (
        select(PriceHistory.price, PriceHistory.created_at)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.created_at.asc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [{"price": row.price, "created_at": row.created_at.isoformat()} for row in result.all()]


def _product_to_dict(p: Product) -> dict:
    """Convert a Product model to dict matching the old Supabase format."""
    return {
        "id": str(p.id),
        "name": p.name,
        "category": p.category,
        "current_price": p.current_price,
        "original_price": p.original_price,
        "image_url": p.image_url,
    }
```

### Step 2: Update products router

Make all endpoints async-aware with DB sessions via `Depends`:

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_session
from app.services.products import (
    get_tracked_items,
    get_products_by_category,
    get_price_history,
    search_catalog,
    get_product_categories,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/search")
async def search_products_endpoint(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    try:
        products = await search_catalog(
            session, query=q, category=category,
            min_price=min_price, max_price=max_price, limit=min(limit, 50),
        )
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def list_categories(session: AsyncSession = Depends(get_session)):
    try:
        categories = await get_product_categories(session)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracked")
async def list_tracked(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        items = await get_tracked_items(session, user_id=str(user.id))
        return {"tracked_items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}/price-history")
async def product_price_history(
    product_id: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        history = await get_price_history(session, product_id)
        return {"price_history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    session: AsyncSession = Depends(get_session),
):
    try:
        if category:
            products = await get_products_by_category(session, category, max_price)
        else:
            from app.services.products import search_catalog
            products = await search_catalog(session)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: Commit

```bash
git add backend/app/services/products.py backend/app/routers/products.py
git commit -m "feat: migrate products service from Supabase to SQLAlchemy

All product queries now use async SQLAlchemy sessions.
Functions accept AsyncSession parameter via FastAPI Depends."
```

---

## Task 3: Auth System — JWT, Cookies, OAuth Router

**Files:**
- Rewrite: `backend/app/auth.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`

### Step 1: Rewrite auth.py

Replace Supabase JWT verification with PyJWT cookie-based auth:

```python
"""Authentication: JWT cookie verification and user extraction."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import get_settings
from app.db import get_session
from app.models.tables import User


class AuthenticatedUser:
    """Lightweight user object returned from auth dependency."""
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AuthenticatedUser:
    """Extract and verify user from auth_token cookie."""
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Verify user still exists
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return AuthenticatedUser(id=str(user.id), email=user.email)
```

### Step 2: Create OAuth router

Create `backend/app/routers/auth.py`:

```python
"""OAuth authentication router using Authlib."""

import logging
from datetime import datetime, timedelta, timezone

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import get_settings
from app.db import get_session
from app.models.tables import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()

oauth = OAuth()

# Register Google
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Register GitHub
oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


def _create_jwt(user_id: str) -> str:
    """Create a signed JWT token for the user."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _set_auth_cookie(response: RedirectResponse, token: str) -> RedirectResponse:
    """Set httpOnly auth cookie on the response."""
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )
    return response


@router.get("/google")
async def google_login(request: Request):
    """Redirect to Google OAuth."""
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback/google", name="google_callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error("Google OAuth error: %s", e)
        return RedirectResponse(f"{settings.frontend_url}/login?error=oauth_failed")

    userinfo = token.get("userinfo", {})
    email = userinfo.get("email")
    if not email:
        return RedirectResponse(f"{settings.frontend_url}/login?error=no_email")

    user = await _get_or_create_user(session, email)
    jwt_token = _create_jwt(str(user.id))
    response = RedirectResponse(f"{settings.frontend_url}/app")
    return _set_auth_cookie(response, jwt_token)


@router.get("/github")
async def github_login(request: Request):
    """Redirect to GitHub OAuth."""
    redirect_uri = str(request.url_for("github_callback"))
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/callback/github", name="github_callback")
async def github_callback(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle GitHub OAuth callback."""
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        logger.error("GitHub OAuth error: %s", e)
        return RedirectResponse(f"{settings.frontend_url}/login?error=oauth_failed")

    # GitHub doesn't return email in token — fetch from API
    resp = await oauth.github.get("user/emails", token=token)
    emails = resp.json()
    primary = next((e["email"] for e in emails if e.get("primary")), None)
    if not primary:
        primary = next((e["email"] for e in emails if e.get("verified")), None)
    if not primary:
        return RedirectResponse(f"{settings.frontend_url}/login?error=no_email")

    user = await _get_or_create_user(session, primary)
    jwt_token = _create_jwt(str(user.id))
    response = RedirectResponse(f"{settings.frontend_url}/app")
    return _set_auth_cookie(response, jwt_token)


@router.get("/me")
async def get_me(request: Request, session: AsyncSession = Depends(get_session)):
    """Return current user info from auth cookie. Used by frontend to check auth state."""
    token = request.cookies.get("auth_token")
    if not token:
        return JSONResponse({"user": None}, status_code=200)

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return JSONResponse({"user": None}, status_code=200)

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return JSONResponse({"user": None}, status_code=200)

    return {"user": {"id": str(user.id), "email": user.email}}


@router.post("/logout")
async def logout():
    """Clear auth cookie."""
    response = JSONResponse({"success": True})
    response.delete_cookie("auth_token", path="/")
    return response


async def _get_or_create_user(session: AsyncSession, email: str) -> User:
    """Find existing user by email or create a new one."""
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(email=email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### Step 3: Update main.py

Add auth router, session middleware (required by Authlib), and DB lifecycle:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import sqlalchemy as sa

from app.routers import chat, products, alerts, analytics, demo, auth
from app.config import get_settings
from app.db import engine

settings = get_settings()

app = FastAPI(
    title="DealHunter API",
    description="AI-powered deal tracking assistant",
    version="0.1.0",
)

# Session middleware (required by Authlib OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://deals.kliuiev.com",
        "https://dealhunter.kliuiev.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(products.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(demo.router)


@app.on_event("startup")
async def startup():
    async with engine.connect() as conn:
        await conn.execute(sa.text("SELECT 1"))


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "DealHunter API", "version": "0.1.0"}
```

**Important:** `SessionMiddleware` must come BEFORE `CORSMiddleware` in the middleware stack (FastAPI middleware order is LIFO, so add SessionMiddleware first in the code).

### Step 4: Commit

```bash
git add backend/app/auth.py backend/app/routers/auth.py backend/app/main.py
git commit -m "feat: add cookie-based JWT auth and OAuth router

Replace Supabase auth with Authlib OAuth (Google/GitHub).
Backend-driven flow: redirect to provider -> callback ->
issue JWT in httpOnly cookie -> redirect to frontend."
```

---

## Task 4: Migrate Remaining Routers — Alerts, Analytics, Demo, Chat

**Files:**
- Rewrite: `backend/app/routers/alerts.py`
- Rewrite: `backend/app/routers/analytics.py`
- Rewrite: `backend/app/routers/demo.py`
- Modify: `backend/app/routers/chat.py`
- Modify: `backend/app/services/llm.py`

### Step 1: Rewrite alerts.py

```python
"""Alerts router with simulate functionality."""

import logging
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.config import get_settings
from app.db import get_session
from app.models.schemas import SimulateRequest
from app.models.tables import Alert, TrackedItem, Product, PriceHistory
from app.services.email import send_price_alert
from app.services.products import get_tracked_items

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])
settings = get_settings()


@router.post("/simulate")
async def simulate_price_drop(
    request: SimulateRequest | None = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Simulate a price drop for demo purposes."""
    items = await get_tracked_items(session, user_id=user.id)

    if not items:
        raise HTTPException(status_code=404, detail="No tracked items found. Track a product first!")

    item = None
    if request and request.item_id:
        item = next((i for i in items if i["id"] == str(request.item_id)), None)
    if not item:
        item = items[0]

    product = item.get("products", {})
    product_id = item.get("product_id")
    target_price = item.get("target_price")

    if not product_id or target_price is None:
        raise HTTPException(status_code=400, detail="Invalid tracked item data")

    old_price = product.get("current_price", target_price + 100)
    recipient_email = request.email if request and request.email else settings.demo_alert_email

    price_drop = random.uniform(10, 50)
    new_price = target_price - price_drop

    # Update product price
    await session.execute(
        update(Product).where(Product.id == product_id).values(current_price=new_price)
    )

    # Add to price history
    session.add(PriceHistory(product_id=product_id, price=new_price))

    # Send email alert
    email_sent = False
    email_error = None
    try:
        email_sent = await send_price_alert(
            to_email=recipient_email,
            product_name=product.get("name", "Unknown Product"),
            old_price=old_price, new_price=new_price, target_price=target_price,
        )
    except Exception as e:
        email_error = str(e)
        logger.error("Email send failed: %s", e)

    # Create alert record
    session.add(Alert(
        tracked_item_id=item["id"], old_price=old_price,
        new_price=new_price, email_sent=email_sent,
    ))
    await session.commit()

    return {
        "success": True,
        "message": f"Price dropped to ${new_price:.2f}!",
        "product_name": product.get("name", "Unknown Product"),
        "product_id": product_id,
        "old_price": old_price, "new_price": new_price,
        "target_price": target_price,
        "email_sent": email_sent,
        "email_recipient": recipient_email,
        "email_error": email_error,
    }


@router.get("")
async def get_alerts(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all triggered alerts with product names for current user."""
    try:
        stmt = (
            select(Alert)
            .join(TrackedItem)
            .join(Product, TrackedItem.product_id == Product.id)
            .where(TrackedItem.user_id == user.id)
            .options(selectinload(Alert.tracked_item).selectinload(TrackedItem.product))
            .order_by(Alert.created_at.desc())
        )
        result = await session.execute(stmt)
        alerts_list = result.scalars().all()

        alerts = []
        for alert in alerts_list:
            product_name = "Unknown Product"
            if alert.tracked_item and alert.tracked_item.product:
                product_name = alert.tracked_item.product.name

            alerts.append({
                "id": str(alert.id),
                "product_name": product_name,
                "old_price": alert.old_price,
                "new_price": alert.new_price,
                "email_sent": alert.email_sent,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
            })

        return {"alerts": alerts}
    except Exception as e:
        logger.error("Error fetching alerts: %s", e)
        return {"alerts": []}
```

### Step 2: Rewrite analytics.py

```python
"""Analytics router for dashboard summary metrics."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.db import get_session
from app.models.tables import Alert, TrackedItem, Product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get aggregated dashboard metrics."""
    total_items = 0
    total_alerts = 0
    total_savings = 0.0
    best_deal = None

    try:
        # Count tracked items
        count_stmt = select(func.count()).select_from(TrackedItem).where(TrackedItem.user_id == user.id)
        result = await session.execute(count_stmt)
        total_items = result.scalar() or 0

        # Get alerts for user
        alerts_stmt = (
            select(Alert)
            .join(TrackedItem)
            .where(TrackedItem.user_id == user.id)
            .options(selectinload(Alert.tracked_item).selectinload(TrackedItem.product))
        )
        result = await session.execute(alerts_stmt)
        alerts = result.scalars().all()
        total_alerts = len(alerts)

        for alert in alerts:
            old_price = alert.old_price or 0
            new_price = alert.new_price or 0
            savings = old_price - new_price
            if savings > 0:
                total_savings += savings

            if old_price > 0:
                pct_drop = ((old_price - new_price) / old_price) * 100
                if pct_drop > 0 and (best_deal is None or pct_drop > best_deal["pct_drop"]):
                    product_name = "Unknown Product"
                    if alert.tracked_item and alert.tracked_item.product:
                        product_name = alert.tracked_item.product.name
                    best_deal = {
                        "product_name": product_name,
                        "old_price": old_price,
                        "new_price": new_price,
                        "pct_drop": round(pct_drop, 1),
                    }

    except Exception as e:
        logger.error("Error fetching analytics summary: %s", e)

    return {
        "total_items": total_items,
        "total_alerts": total_alerts,
        "total_savings": round(total_savings, 2),
        "best_deal": best_deal,
    }
```

### Step 3: Rewrite demo.py

```python
"""Demo router for reset functionality."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_session
from app.models.tables import Alert, TrackedItem, Product, PriceHistory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/reset")
async def reset_demo(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Reset demo by clearing this user's tracked items and alerts."""
    try:
        # Get this user's tracked item IDs
        stmt = select(TrackedItem.id).where(TrackedItem.user_id == user.id)
        result = await session.execute(stmt)
        user_item_ids = [row[0] for row in result.all()]

        if user_item_ids:
            # Delete alerts for this user's tracked items
            await session.execute(
                delete(Alert).where(Alert.tracked_item_id.in_(user_item_ids))
            )
            # Delete this user's tracked items
            await session.execute(
                delete(TrackedItem).where(TrackedItem.user_id == user.id)
            )

        # Reset ALL product prices to original values
        stmt = select(Product).where(Product.original_price.is_not(None))
        result = await session.execute(stmt)
        products = result.scalars().all()
        for product in products:
            product.current_price = product.original_price

        # Clear price history
        await session.execute(delete(PriceHistory))

        await session.commit()
        return {"success": True, "message": "Demo reset complete"}

    except Exception as e:
        logger.error("Demo reset failed: %s", e)
        raise HTTPException(status_code=500, detail="Failed to reset demo")
```

### Step 4: Update chat.py and llm.py

The chat router and LLM service need to pass DB sessions through to product service calls.

**chat.py** — Add session dependency, pass to `get_tool_response`:

The main change: `get_tool_response` now needs a `session` parameter. Update the `generate_stream` and endpoints to pass it through.

```python
# In chat.py, add session dependency to both endpoints:
from app.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# generate_stream gets session parameter
async def generate_stream(message: str, session_id: str, user_id: str, session: AsyncSession):
    # ... same logic, but pass session to get_tool_response:
    tool_result = await get_tool_response(tool_call["name"], tool_call["arguments"], user_id=user_id, session=session)
    # ...

@router.post("")
async def chat(
    request: ChatMessage,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return StreamingResponse(
        generate_stream(request.message, request.session_id, user_id=user.id, session=session),
        # ... same headers ...
    )

@router.post("/sync")
async def chat_sync(
    request: ChatMessage,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # ... pass session to get_tool_response ...
```

**llm.py** — Add session parameter to `get_tool_response`, pass to all product service calls:

```python
# All product service imports are already there.
# Add session parameter:

async def get_tool_response(
    tool_name: str, tool_args: dict, user_id: str | None = None, session=None
) -> str:
    # Replace all product service calls with await + session:
    # e.g. search_catalog(...) becomes await search_catalog(session, ...)
    # e.g. search_products(...) becomes await search_products(session, ...)
    # etc.
```

Full rewrite of the tool dispatch in `get_tool_response` — same logic, just add `session` as first arg to every product service call and `await` each one.

### Step 5: Commit

```bash
git add backend/app/routers/alerts.py backend/app/routers/analytics.py \
  backend/app/routers/demo.py backend/app/routers/chat.py backend/app/services/llm.py
git commit -m "feat: migrate alerts, analytics, demo, chat to SQLAlchemy

All routers now use async SQLAlchemy sessions.
Supabase query builder fully removed from backend."
```

---

## Task 5: Frontend Auth — Replace Supabase with Cookie Auth

**Files:**
- Delete: `frontend/src/lib/supabase.ts`
- Rewrite: `frontend/src/components/providers/AuthProvider.tsx`
- Rewrite: `frontend/src/app/login/page.tsx`
- Delete or simplify: `frontend/src/app/auth/callback/page.tsx`
- Modify: `frontend/src/components/layout/Header.tsx`

### Step 1: Delete supabase.ts

Remove `frontend/src/lib/supabase.ts`.

### Step 2: Rewrite AuthProvider

Replace Supabase session listener with a `GET /auth/me` call:

```tsx
"use client"

import { createContext, useContext, useEffect, useState } from "react"

interface AppUser {
  id: string
  email: string
}

interface AuthContextType {
  user: AppUser | null
  loading: boolean
  signOut: () => Promise<void>
  refreshAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signOut: async () => {},
  refreshAuth: async () => {},
})

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL
  if (typeof window !== "undefined") return `http://${window.location.hostname}:8000`
  return "http://localhost:8000"
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AppUser | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const res = await fetch(`${getApiUrl()}/auth/me`, { credentials: "include" })
      const data = await res.json()
      setUser(data.user || null)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const signOut = async () => {
    try {
      await fetch(`${getApiUrl()}/auth/logout`, {
        method: "POST",
        credentials: "include",
      })
    } catch {
      // Ignore errors
    }
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signOut, refreshAuth: checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

### Step 3: Rewrite login page

Replace Supabase OAuth calls with simple links to backend:

```tsx
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Target } from "lucide-react"
import { useAuth } from "@/components/providers/AuthProvider"

const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL
  if (typeof window !== "undefined") return `http://${window.location.hostname}:8000`
  return "http://localhost:8000"
}

export default function LoginPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      router.replace("/app")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-950">
        <div className="size-8 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-500" />
      </div>
    )
  }

  const apiUrl = getApiUrl()

  return (
    <div className="flex min-h-screen flex-col bg-zinc-950">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 size-96 rounded-full bg-emerald-500/10 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 size-96 rounded-full bg-teal-500/10 blur-[120px]" />
      </div>

      <div className="relative flex flex-1 items-center justify-center px-4">
        <div className="w-full max-w-sm space-y-8">
          <div className="flex flex-col items-center gap-3">
            <div className="relative flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
              <Target className="size-7 text-white" strokeWidth={2.5} />
              <div className="absolute inset-0 rounded-2xl bg-emerald-500/20 blur-md" />
            </div>
            <div className="text-center">
              <h1 className="text-2xl font-bold tracking-tight text-white">
                DealHunter
                <span className="ml-1 bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                  AI
                </span>
              </h1>
              <p className="mt-1 text-sm text-zinc-400">
                Sign in to track prices and get alerts
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <a
              href={`${apiUrl}/auth/google`}
              className="flex w-full items-center justify-center gap-3 rounded-md border border-zinc-700 bg-zinc-900/50 px-4 py-3 text-sm font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:bg-zinc-800 hover:text-white"
            >
              <svg className="size-5" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Continue with Google
            </a>

            <a
              href={`${apiUrl}/auth/github`}
              className="flex w-full items-center justify-center gap-3 rounded-md border border-zinc-700 bg-zinc-900/50 px-4 py-3 text-sm font-medium text-zinc-300 transition-colors hover:border-zinc-600 hover:bg-zinc-800 hover:text-white"
            >
              <svg className="size-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              Continue with GitHub
            </a>
          </div>

          <p className="text-center text-xs text-zinc-600">
            By signing in, you agree to our Terms of Service
          </p>
        </div>
      </div>
    </div>
  )
}
```

### Step 4: Simplify or delete auth callback page

The backend now handles the OAuth callback and redirects to `/app` directly. The `/auth/callback` page is no longer needed. Delete `frontend/src/app/auth/callback/page.tsx` or replace with a simple redirect:

```tsx
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function AuthCallback() {
  const router = useRouter()
  useEffect(() => { router.replace("/app") }, [router])
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950">
      <div className="size-8 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-500" />
    </div>
  )
}
```

### Step 5: Update Header signOut

In `Header.tsx`, the `signOut` function already comes from `useAuth()`. Since we updated the AuthProvider, signOut now calls `POST /auth/logout` and clears the cookie. The Header component itself needs no changes — it uses `useAuth()` which still returns `user` and `signOut`.

However, the Header accesses `user?.user_metadata?.avatar_url` and `user?.user_metadata?.full_name` which are Supabase-specific. Update to use the new simpler user shape:

```tsx
// Replace these lines in Header.tsx:
const avatarUrl = user?.user_metadata?.avatar_url
const displayName =
    user?.user_metadata?.full_name ||
    user?.user_metadata?.name ||
    user?.email?.split("@")[0] ||
    "User"

// With:
const displayName = user?.email?.split("@")[0] || "User"
```

And remove the avatar image since we no longer have it (minimal `users` table). Replace the avatar with the initial-letter fallback that's already in the component.

### Step 6: Commit

```bash
git add -A frontend/src/lib/supabase.ts frontend/src/components/providers/AuthProvider.tsx \
  frontend/src/app/login/page.tsx frontend/src/app/auth/callback/page.tsx \
  frontend/src/components/layout/Header.tsx
git commit -m "feat: replace frontend Supabase auth with cookie-based auth

AuthProvider now checks /auth/me on mount. Login page uses
simple links to backend OAuth endpoints. Supabase client removed."
```

---

## Task 6: Frontend API Calls — Remove accessToken, Use Credentials

**Files:**
- Modify: `frontend/src/app/app/page.tsx`
- Modify: `frontend/src/components/chat/ChatInterface.tsx`
- Modify: `frontend/src/components/dashboard/TrackedItems.tsx`
- Modify: `frontend/src/components/dashboard/AnalyticsSummary.tsx`
- Modify: `frontend/src/components/dashboard/PriceAlerts.tsx`
- Modify: `frontend/src/components/dashboard/SimulateButton.tsx`

### Key Change

Every `fetch()` call currently does:
```js
const headers = {}
if (accessToken) {
  headers["Authorization"] = `Bearer ${accessToken}`
}
fetch(url, { headers })
```

Replace with:
```js
fetch(url, { credentials: "include" })
```

The `auth_token` cookie is sent automatically. No more `accessToken` prop drilling.

### Step 1: Update app/page.tsx

Remove all `session?.access_token` references. Remove `getAuthHeaders` function. Remove `accessToken` prop from all child components.

Key changes:
- Remove `session` from `useAuth()` destructure (no longer exists)
- Remove `getAuthHeaders` callback
- Pass `credentials: "include"` in the demo reset fetch
- Remove `accessToken` prop from `AnalyticsSummary`, `ChatInterface`, `TrackedItems`, `PriceAlerts`

### Step 2: Update all dashboard components

For each component (`ChatInterface.tsx`, `TrackedItems.tsx`, `AnalyticsSummary.tsx`, `PriceAlerts.tsx`, `SimulateButton.tsx`):

1. Remove `accessToken` from props interface
2. Remove `accessToken` from destructured props
3. Replace all `headers["Authorization"] = \`Bearer ${accessToken}\`` with just `credentials: "include"` in the fetch options
4. For POST requests, keep `Content-Type` header but add `credentials: "include"`

Example pattern:
```js
// Before:
const headers: Record<string, string> = {}
if (accessToken) {
  headers["Authorization"] = `Bearer ${accessToken}`
}
const response = await fetch(url, { headers })

// After:
const response = await fetch(url, { credentials: "include" })

// For POST:
const response = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify(data),
})
```

### Step 3: Commit

```bash
git add frontend/src/app/app/page.tsx \
  frontend/src/components/chat/ChatInterface.tsx \
  frontend/src/components/dashboard/TrackedItems.tsx \
  frontend/src/components/dashboard/AnalyticsSummary.tsx \
  frontend/src/components/dashboard/PriceAlerts.tsx \
  frontend/src/components/dashboard/SimulateButton.tsx
git commit -m "refactor: replace Bearer token auth with cookie credentials

Remove accessToken prop drilling from all components.
All fetch calls now use credentials: 'include' for
automatic cookie-based authentication."
```

---

## Task 7: Cleanup and Deployment Prep

**Files:**
- Modify: `frontend/package.json` (remove @supabase/supabase-js)
- Modify: `frontend/Dockerfile` (remove Supabase build args)
- Modify: `backend/Dockerfile` (add Alembic migration step)
- Modify: `docker-compose.yml` (update env vars, add postgres service)
- Modify: `.env.example`
- Delete: `backend/seed_products.py` (seed data now in migration)
- Delete: `backend/migrations/` (replaced by alembic)

### Step 1: Remove Supabase from frontend

```bash
cd frontend && npm uninstall @supabase/supabase-js
```

### Step 2: Update frontend Dockerfile

Remove Supabase build args:

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

### Step 3: Update backend Dockerfile

Add Alembic migration run and copy alembic config:

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Step 4: Update docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: dealhunter
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/dealhunter
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RESEND_API_KEY=${RESEND_API_KEY}
      - JWT_SECRET=${JWT_SECRET:-local-dev-secret}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID:-}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET:-}
      - FRONTEND_URL=${FRONTEND_URL:-http://localhost:3000}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

volumes:
  pgdata:
```

### Step 5: Update .env.example

```
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dealhunter

# Auth
JWT_SECRET=change-me-in-production
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Email (Resend)
RESEND_API_KEY=re_...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### Step 6: Clean up old files

```bash
rm backend/seed_products.py
rm -rf backend/migrations/
```

### Step 7: Commit

```bash
git add -A
git commit -m "chore: cleanup Supabase, update Docker and env config

Remove Supabase SDK, old migrations, seed script.
Backend Dockerfile runs Alembic on startup.
docker-compose includes local Postgres service.
Updated .env.example with new variables."
```

---

## Task 8: Coolify Deployment

**No code changes — infrastructure setup only.**

### Step 1: Create Postgres database in Coolify

Either use existing Coolify Postgres (`acg0w8cggk0w0w4sssk88s4o`) or create a new one for Deal Hunter.

If creating new: create database `dealhunter` on the existing Postgres instance.

### Step 2: Set backend env vars in Coolify

For backend app `awc0oowgkccc4wgc4000gcgc`, set:

```
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/dealhunter
JWT_SECRET=<generate-random-32-char-string>
GOOGLE_CLIENT_ID=<from-google-console>
GOOGLE_CLIENT_SECRET=<from-google-console>
GITHUB_CLIENT_ID=<from-github-settings>
GITHUB_CLIENT_SECRET=<from-github-settings>
```

Remove old vars: `SUPABASE_URL`, `SUPABASE_KEY`

### Step 3: Set up OAuth providers

**Google:**
1. Go to Google Cloud Console > APIs & Services > Credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Authorized redirect URI: `https://api-deals.kliuiev.com/auth/callback/google`

**GitHub:**
1. Go to GitHub > Settings > Developer settings > OAuth Apps
2. Create new app
3. Authorization callback URL: `https://api-deals.kliuiev.com/auth/callback/github`

### Step 4: Update frontend env vars in Coolify

For frontend app `nc44gkwk84swoggkk4ogokow`:
- Keep: `NEXT_PUBLIC_API_URL=https://api-deals.kliuiev.com`
- Remove: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Step 5: Push and verify

```bash
git push origin main
```

Wait for Coolify auto-deploy, then run `/verify-app` to check.

### Step 6: Update CLAUDE.md

Update the project CLAUDE.md to reflect new env vars and remove Supabase references.

---

## Task Summary

| Task | Description | Dependencies |
|------|-------------|-------------|
| 1 | Database foundation (SQLAlchemy, models, Alembic) | None |
| 2 | Migrate products service | Task 1 |
| 3 | Auth system (JWT, OAuth router) | Task 1 |
| 4 | Migrate remaining routers | Tasks 2, 3 |
| 5 | Frontend auth (AuthProvider, login) | Task 3 |
| 6 | Frontend API calls (remove accessToken) | Task 5 |
| 7 | Cleanup and deployment prep | Tasks 4, 6 |
| 8 | Coolify deployment | Task 7 |

**Parallelizable:** Tasks 2 and 3 can run in parallel (both depend only on Task 1). Tasks 5 and 4 can partially overlap.
