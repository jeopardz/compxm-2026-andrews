# Deploy BizSim on Railway

## Required configuration

Apply every SQL migration in `supabase/migrations/` in numeric order, then deploy
`supabase/functions/ls-webhook/index.ts` with JWT verification disabled. Configure:

- App variables: `AUTH_ENABLED=true`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
  `LEMONSQUEEZY_CHECKOUT_URL`, and a working `SUPPORT_EMAIL`.
- Recommended operations variables: `SENTRY_DSN`, `SENTRY_ENVIRONMENT=production`,
  `SENTRY_TRACES_SAMPLE_RATE=0.05`, and `LOG_LEVEL=INFO`.
- Edge Function secrets: `LS_SIGNING_SECRET`, `LS_STORE_ID`, `LS_VARIANT_IDS`,
  `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

`LS_VARIANT_IDS` is a comma-separated allowlist of paid BizSim variant IDs. Never
put the service-role key or signing secret in Streamlit secrets or source control.

## Railway

Connect the repository to Railway. The checked-in `railway.json` installs the root
`requirements.txt`, starts Streamlit on `$PORT`, and uses `/_stcore/health` for the
health check. Add the app variables above in Railway, deploy, then set the public
domain as the Lemon Squeezy checkout return URL.

## Release check

Run `python -m pytest sim/tests -q`, create two separate browser sessions, verify
their games never cross, and complete one Lemon Squeezy test purchase. Re-send the
same webhook and confirm it creates neither a second payment nor a second 30-day
grant. Revoke temporary Supabase deploy tokens before launch.

Verify the public `?legal=privacy`, `?legal=terms`, and `?legal=support` routes,
confirm the support inbox works, and configure an uptime check against
`/_stcore/health`. If Sentry is enabled, send a controlled test event before launch.
