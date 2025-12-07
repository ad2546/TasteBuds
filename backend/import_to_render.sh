#!/bin/bash

# Simple script to import data to Render production database
# This script helps you import the exported migration data

echo ""
echo "======================================"
echo "TasteSync Production Data Import"
echo "======================================"
echo ""

# Check if migration_data exists
if [ ! -d "migration_data" ]; then
    echo "❌ Error: migration_data directory not found!"
    echo ""
    echo "Run this first:"
    echo "  python migrate_to_prod.py --export"
    exit 1
fi

echo "✓ Found migration data"
echo ""

# Prompt for production DATABASE_URL
if [ -z "$PROD_DATABASE_URL" ]; then
    echo "Please enter your Render PostgreSQL DATABASE_URL:"
    echo "(Find it at: https://dashboard.render.com/ → Your Database → Connections)"
    echo ""
    read -p "DATABASE_URL: " PROD_DATABASE_URL
    echo ""
fi

if [ -z "$PROD_DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL is required"
    exit 1
fi

# Confirm before proceeding
echo "⚠️  WARNING: This will CLEAR all existing data in production and replace it with:"
echo ""
echo "  • 105 users"
echo "  • 102 taste DNA profiles"
echo "  • 1,500 twin relationships"
echo "  • 872 saved restaurants"
echo "  • 1,284 interaction logs"
echo "  • 4 challenges"
echo "  • 8 user challenges"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Import cancelled"
    exit 0
fi

echo ""
echo "Starting import..."
echo ""

# Activate virtual environment and run import
source venv/bin/activate
export PROD_DATABASE_URL="$PROD_DATABASE_URL"
python migrate_to_prod.py --import-data

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ Import completed successfully!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Verify data: python migrate_to_prod.py --verify-prod --prod-url '$PROD_DATABASE_URL'"
    echo "2. Test your production app at: https://tastebuds-nzx0.onrender.com"
    echo "3. Try logging in with a test user"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ Import failed"
    echo "======================================"
    echo ""
    echo "Check the error messages above for details."
    echo ""
fi
