# Day 8 — Setup Tasks

## 1. UptimeRobot (5 min)

Keeps the Render backend from sleeping.

1. Sign up at https://uptimerobot.com (free)
2. Dashboard -> Add New Monitor
3. Type: HTTPS
4. URL: https://coreknow.onrender.com/api/health
5. Interval: 5 minutes
6. Save

Done. Backend will always be warm.

## 2. Supabase backups (already on by default)

Free tier includes daily backups for 7 days.
Paid tier includes 30-day PITR.

Verify: Supabase Dashboard -> Database -> Backups

## 3. Real email sending (optional, 10 min)

Currently password reset codes are shown in-app (dev mode).
To send real emails:

1. Sign up at https://resend.com (free tier: 100 emails/day)
2. Verify your domain OR use their test domain
3. Copy your API key
4. In Render: Environment -> add key
   RESEND_API_KEY = re_xxxxx
5. In your domain settings, whitelist resend.com

Then update the `/api/auth/forgot-password` endpoint to call Resend API.

## 4. Verify rate limiting is working

Test with:

```
for i in {1..25}; do
  curl -s -o /dev/null -w '%{http_code}\n' https://coreknow.onrender.com/api/health
done
```

First 20 should return 200. Then 429s if you're hitting a limited endpoint.
Note: /api/health has a 200/min limit, so it will still pass most requests.

## 5. Change default passwords on all keys

Rotate these before public launch:

- GitHub PAT (github.com/settings/tokens)
- Supabase service_role key (Supabase -> Settings -> API)
- DeepSeek API key (platform.deepseek.com)
- Paystack secret key (paystack.com -> Settings)
- Render account password

Update each in Render Environment tab.
