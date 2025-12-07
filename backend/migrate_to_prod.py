"""
Migration script to move data from SQLite (dev) to PostgreSQL (production).

Usage:
    python migrate_to_prod.py --export  # Export data from SQLite to JSON files
    python migrate_to_prod.py --import  # Import JSON files to PostgreSQL
    python migrate_to_prod.py --prod-url "postgresql://..."  # Set production URL and import

This script exports all data from the development SQLite database and imports it
into the production PostgreSQL database on Render.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings


# Tables to migrate in order (respecting foreign key dependencies)
TABLES_ORDER = [
    "users",
    "taste_dna",
    "twin_relationships",
    "saved_restaurants",
    "interaction_logs",
    "image_searches",
    "date_night_pairings",
    "challenges",
    "user_challenges",
    "user_achievements",
]


async def export_table_data(session: AsyncSession, table_name: str) -> List[Dict[str, Any]]:
    """Export all data from a table."""
    print(f"  Exporting {table_name}...")

    # Get column names
    result = await session.execute(text(f"PRAGMA table_info({table_name})"))
    columns = [row[1] for row in result.fetchall()]

    # Get all rows
    result = await session.execute(text(f"SELECT * FROM {table_name}"))
    rows = result.fetchall()

    # Convert to list of dicts
    data = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            row_dict[col] = value
        data.append(row_dict)

    print(f"    ✓ Exported {len(data)} rows from {table_name}")
    return data


async def export_all_data():
    """Export all data from SQLite to JSON files."""
    print("\n=== EXPORTING DATA FROM SQLITE ===\n")

    # Create SQLite engine
    settings = get_settings()
    settings.use_sqlite = True  # Force SQLite
    engine = create_async_engine(settings.database_url, echo=False)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create export directory
    export_dir = Path("migration_data")
    export_dir.mkdir(exist_ok=True)

    async with async_session() as session:
        for table_name in TABLES_ORDER:
            try:
                data = await export_table_data(session, table_name)

                # Save to JSON file
                filepath = export_dir / f"{table_name}.json"
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=2, default=str)

            except Exception as e:
                print(f"    ✗ Error exporting {table_name}: {e}")

    await engine.dispose()

    print(f"\n✓ All data exported to {export_dir}/")
    print(f"\nNext step: Run with --import to import to production database")


async def import_table_data(session: AsyncSession, table_name: str, data: List[Dict[str, Any]]):
    """Import data into a table."""
    if not data:
        print(f"    - Skipping {table_name} (no data)")
        return

    print(f"  Importing {table_name}...")

    try:
        # Get column names from first row
        columns = list(data[0].keys())

        # Clear existing data (careful!)
        await session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

        # Build INSERT statement
        placeholders = ", ".join([f":{col}" for col in columns])
        cols_str = ", ".join(columns)
        insert_sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        # Insert all rows with type conversions
        for row in data:
            # Convert types for PostgreSQL compatibility
            converted_row = {}
            for key, value in row.items():
                if value is None:
                    converted_row[key] = None
                # Convert datetime strings to datetime objects
                elif isinstance(value, str) and ('created_at' in key or 'updated_at' in key or 'completed_at' in key or '_date' in key):
                    try:
                        converted_row[key] = datetime.fromisoformat(value)
                    except:
                        converted_row[key] = value
                # Convert integer booleans (0/1) to actual booleans for specific fields
                elif key in ['quiz_completed', 'active', 'completed'] and isinstance(value, int):
                    converted_row[key] = bool(value)
                else:
                    converted_row[key] = value

            await session.execute(text(insert_sql), converted_row)

        await session.commit()
        print(f"    ✓ Imported {len(data)} rows into {table_name}")

    except Exception as e:
        await session.rollback()
        print(f"    ✗ Error importing {table_name}: {e}")
        raise


async def import_all_data(prod_database_url: str):
    """Import all data from JSON files to PostgreSQL."""
    print("\n=== IMPORTING DATA TO POSTGRESQL ===\n")
    print(f"Target database: {prod_database_url[:50]}...\n")

    # Create PostgreSQL engine
    engine = create_async_engine(prod_database_url, echo=False)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Check export directory
    export_dir = Path("migration_data")
    if not export_dir.exists():
        print("✗ Error: migration_data directory not found. Run --export first.")
        return

    async with async_session() as session:
        for table_name in TABLES_ORDER:
            filepath = export_dir / f"{table_name}.json"

            if not filepath.exists():
                print(f"  - Skipping {table_name} (file not found)")
                continue

            try:
                # Load data from JSON
                with open(filepath, "r") as f:
                    data = json.load(f)

                # Import to PostgreSQL
                await import_table_data(session, table_name, data)

            except Exception as e:
                print(f"    ✗ Error processing {table_name}: {e}")

    await engine.dispose()

    print("\n✓ All data imported to production database!")


async def verify_data(database_url: str, db_name: str):
    """Verify data counts in database."""
    print(f"\n=== VERIFYING DATA IN {db_name} ===\n")

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        for table_name in TABLES_ORDER:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"  {table_name}: {count} rows")
            except Exception as e:
                print(f"  {table_name}: Error - {e}")

    await engine.dispose()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate data from SQLite to PostgreSQL")
    parser.add_argument("--export", action="store_true", help="Export data from SQLite")
    parser.add_argument("--import-data", action="store_true", help="Import data to PostgreSQL")
    parser.add_argument("--verify-dev", action="store_true", help="Verify dev database")
    parser.add_argument("--verify-prod", action="store_true", help="Verify prod database")
    parser.add_argument("--prod-url", type=str, help="Production database URL")

    args = parser.parse_args()

    if args.export:
        asyncio.run(export_all_data())

    elif args.verify_dev:
        settings = get_settings()
        settings.use_sqlite = True
        asyncio.run(verify_data(settings.database_url, "DEVELOPMENT (SQLite)"))

    elif args.verify_prod:
        prod_url = args.prod_url or os.getenv("PROD_DATABASE_URL")
        if not prod_url:
            print("✗ Error: Provide --prod-url or set PROD_DATABASE_URL environment variable")
            sys.exit(1)

        # Convert to async URL
        if prod_url.startswith("postgres://"):
            prod_url = prod_url.replace("postgres://", "postgresql+asyncpg://")
        elif prod_url.startswith("postgresql://"):
            prod_url = prod_url.replace("postgresql://", "postgresql+asyncpg://")

        asyncio.run(verify_data(prod_url, "PRODUCTION (PostgreSQL)"))

    elif args.import_data:
        prod_url = args.prod_url or os.getenv("PROD_DATABASE_URL")
        if not prod_url:
            print("\n✗ Error: Production database URL required")
            print("\nProvide it with:")
            print("  python migrate_to_prod.py --import-data --prod-url 'postgresql://...'")
            print("  OR")
            print("  export PROD_DATABASE_URL='postgresql://...'")
            print("  python migrate_to_prod.py --import-data")
            sys.exit(1)

        # Convert to async URL
        if prod_url.startswith("postgres://"):
            prod_url = prod_url.replace("postgres://", "postgresql+asyncpg://")
        elif prod_url.startswith("postgresql://"):
            prod_url = prod_url.replace("postgresql://", "postgresql+asyncpg://")

        asyncio.run(import_all_data(prod_url))

    else:
        parser.print_help()
        print("\n" + "="*60)
        print("MIGRATION WORKFLOW:")
        print("="*60)
        print("\n1. Export data from development SQLite:")
        print("   python migrate_to_prod.py --export")
        print("\n2. Verify export:")
        print("   python migrate_to_prod.py --verify-dev")
        print("\n3. Get your production DATABASE_URL from Render:")
        print("   https://dashboard.render.com/")
        print("\n4. Import to production PostgreSQL:")
        print("   python migrate_to_prod.py --import-data --prod-url 'postgresql://...'")
        print("\n5. Verify production:")
        print("   python migrate_to_prod.py --verify-prod --prod-url 'postgresql://...'")
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
