# Supabase Declarative Migration Workflow

This document describes the proper workflow for managing database schema changes using Supabase's declarative migration approach.

## One-Time Setup (Manual - requires browser)

Since we're using Cursor in a non-TTY environment, you need to login manually **once**:

```bash
# In your local terminal (not Cursor):
cd /home/arnerustad/repos/americano_volleyball
npx supabase login
```

This opens a browser for authentication. After login, the token is saved and works in Cursor.

Link to remote project:
```bash
npx supabase link --project-ref rparfsuukcqgfrtuogkl
```

## Current Status

✅ **Production database** has the full schema with improvements applied
✅ **Local migrations** exist (manually written to match production)
⚠️ **Local Supabase** not yet running (need to start with `npx supabase start`)

## Declarative Workflow (For Future Changes)

### The Proper Way

**DON'T:** Write SQL migrations manually
**DO:** Make changes in production → Generate migration with `db diff`

### Step-by-Step Process

#### 1. Make Schema Changes in Production

Option A: Use Supabase Studio (GUI)
- Go to https://supabase.com/dashboard/project/rparfsuukcqgfrtuogkl
- Use Table Editor or SQL Editor to make changes

Option B: Use Supabase MCP (from Cursor)
```typescript
// Apply changes via MCP
mcp_supabase_apply_migration({
  name: "descriptive_name",
  query: "ALTER TABLE ... ADD COLUMN ..."
})
```

#### 2. Generate Migration from Production State

**This is the key step!** After making changes in production:

```bash
# Compare local state with production and generate migration
npx supabase db diff --use-migra <migration_name>

# Example:
npx supabase db diff --use-migra add_player_ratings
```

This command:
- Compares your local database (from last migration) with production
- Auto-generates SQL for the differences
- Creates a new migration file in `supabase/migrations/`

#### 3. Review the Generated Migration

Open the generated file in `supabase/migrations/` and verify:
- ✅ Changes are what you expect
- ✅ No unintended schema drift
- ✅ Indexes and constraints are included

#### 4. Apply Migration Locally

```bash
# Reset local database and apply all migrations from scratch
npx supabase db reset

# This runs:
# - All migrations in order
# - seed.sql data
```

#### 5. Test Locally

```bash
# Start local Supabase (if not running)
npx supabase start

# Access local Studio at http://localhost:54323
# Test your backend against local database
```

#### 6. Commit to Git

```bash
git add supabase/migrations/
git commit -m "feat: add migration for <description>"
git push
```

### Why This Approach?

✅ **No manual SQL** - Migrations are auto-generated
✅ **Production is source of truth** - What's in production becomes the migration
✅ **Catches everything** - Including indexes, constraints, RLS policies
✅ **No schema drift** - Local and production stay in sync
✅ **Reviewable** - See exactly what changed in Git diffs

## Daily Development Workflow

```bash
# Start local Supabase
npx supabase start

# Start backend (separate terminal)
cd backend && uv run uvicorn app.main:app --reload

# Start frontend (separate terminal)  
cd frontend && npm run dev
```

Access:
- Local Studio: http://localhost:54323
- Local API: http://localhost:54321  
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

## Troubleshooting

### "Access token not provided"

You need to login first (see One-Time Setup above).

### "Migration conflicts"

```bash
# Reset local database to match production exactly
npx supabase db pull --force
```

### "Changes not detected"

Ensure you've run `npx supabase db reset` recently to have the latest local state for comparison.

## Current State of Migrations

1. `20251016173151_initial_schema.sql` - Base schema (manually created to match production)
2. `20251016173238_add_timestamps_and_status.sql` - Improvements (manually created to match production)

**For all future changes:** Use the declarative workflow above!

