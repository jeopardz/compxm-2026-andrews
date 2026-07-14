# CompMastery launch checklist

1. Run all files in `supabase/migrations/` in order.
2. Deploy `ls-webhook`; set `LS_SIGNING_SECRET`, `LS_STORE_ID`, and
   `LS_VARIANT_IDS` plus the Supabase service credentials.
3. Deploy the repository on Streamlit Community Cloud and set the app secrets listed
   in `DEPLOY.md`.
4. Verify Privacy, Terms and Support routes and configure a real `SUPPORT_EMAIL`.
5. Configure Sentry or equivalent error alerting and an external uptime check.
6. Test signup, demo limit, payment, automatic unlock, reload, rewind, and a second
   simultaneous user.
7. Revoke every temporary Supabase/GitHub deployment token before public launch.
