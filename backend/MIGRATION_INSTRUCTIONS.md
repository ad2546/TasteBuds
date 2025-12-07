# TasteSync Data Migration Guide

## Step 1: ✅ Export Data (COMPLETED)

Your development data has been exported successfully:

```
✓ 105 users
✓ 102 taste DNA profiles
✓ 1,500 twin relationships
✓ 872 saved restaurants
✓ 1,284 interaction logs
✓ 4 challenges
✓ 8 user challenges
```

All data is saved in `migration_data/` folder (1.4 MB total).

## Step 2: Get Production Database URL

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click on your PostgreSQL database service
3. Scroll down to "Connections" section
4. Copy the **Internal Database URL** or **External Database URL**

It should look like:
```
postgres://username:password@hostname.region.render.com/database_name
```

## Step 3: Import to Production

Once you have the DATABASE_URL, run:

```bash
# Option 1: Provide URL directly
python migrate_to_prod.py --import-data --prod-url 'postgres://your-url-here'

# Option 2: Set as environment variable
export PROD_DATABASE_URL='postgres://your-url-here'
python migrate_to_prod.py --import-data
```

## Step 4: Verify Production Data

After import, verify everything was migrated:

```bash
python migrate_to_prod.py --verify-prod --prod-url 'postgres://your-url-here'
```

## Important Notes

⚠️ **CAUTION**: The import script will **TRUNCATE** (clear) all existing production tables before importing. Make sure you have a backup if there's any important data in production.

✅ The script preserves:
- User IDs (important for authentication)
- All relationships and foreign keys
- Timestamps and metadata

## Troubleshooting

### If you get connection errors:
- Make sure you're using the **External Database URL** from Render
- Check that your IP is allowed (Render PostgreSQL allows all IPs by default)

### If you get authentication errors:
- Verify the URL is correct and includes password
- Make sure the database exists on Render

### If you get table errors:
- Ensure you've run migrations on production first:
  ```bash
  # Set DATABASE_URL to production
  export DATABASE_URL='postgres://your-url-here'
  alembic upgrade head
  ```

## After Migration

1. Update your frontend `.env` on Netlify to use production API
2. Test login with one of the migrated users
3. Verify taste twins are showing correctly
4. Check that recommendations work

## Rollback

If something goes wrong, you can:
1. Re-run migrations: `alembic downgrade base && alembic upgrade head`
2. Re-import from the exported JSON files (they're preserved)
