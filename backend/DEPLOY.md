# CoreKnow Backend - Deploy to Render

## Step 1 - Get keys

- SUPABASE_URL = https://mzxbndfmeuewmbhwiotc.supabase.co
- SUPABASE_SERVICE_KEY = (from Supabase dashboard)
- DEEPSEEK_API_KEY = (from DeepSeek)

## Step 2 - Render

1. Go to https://render.com
2. New Web Service
3. Connect GitHub repo: darkmoorltd-jpg/coreknow
4. Root directory: backend
5. Runtime: Python 3
6. Build: pip install -r requirements.txt
7. Start: uvicorn main:app --host 0.0.0.0 --port $PORT

## Step 3 - Env vars

Add in Render dashboard:
- SUPABASE_URL
- SUPABASE_SERVICE_KEY
- DEEPSEEK_API_KEY

## Step 4 - Test

Open: https://coreknow-api.onrender.com/api/health
Should return: {ok: true}