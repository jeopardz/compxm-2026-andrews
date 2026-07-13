# BizSim launch checklist

1. Run all files in `supabase/migrations/` in order.
2. Deploy `ls-webhook`; set `LS_SIGNING_SECRET`, `LS_STORE_ID`, and
   `LS_VARIANT_IDS` plus the Supabase service credentials.
3. Deploy the repository on Railway and set the four app variables listed in
   `DEPLOY.md`.
4. Test signup, demo limit, payment, automatic unlock, reload, rewind, and a second
   simultaneous user.
5. Revoke every temporary Supabase/GitHub deployment token before public launch.
