# Backend Setup - Missing Service Key ⚠️

## Issue Found

The backend `.env` file is missing the **SUPABASE_SERVICE_KEY**.

## What You Need To Do

1. Go to your Supabase project dashboard:
   https://supabase.com/dashboard/project/rparfsuukcqgfrtuogkl

2. Navigate to: **Settings** → **API** → **Project API keys**

3. Copy the **`service_role` key** (NOT the anon key)

4. Add it to `backend/.env`:

```bash
cd backend
nano .env  # or use your editor
```

Update the line:
```
SUPABASE_SERVICE_KEY=your-actual-service-role-key-here
```

The service key starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` and is different from the anon key.

**Why the service key?**
- Backend needs admin database access
- Bypasses Row Level Security (RLS)
- Required for the `supabase` client in `app/database.py`

## After Adding the Key

Test the backend:
```bash
cd backend
uv run uvicorn app.main:app --reload
```

Should start without errors.

## Current .env Status

✅ SUPABASE_URL - Set
✅ SUPABASE_KEY (anon) - Set  
❌ SUPABASE_SERVICE_KEY - **MISSING** ← Need this!
⚠️ DATABASE_URL - Not needed (using Supabase client)

