# BizSim Audit Report — Remediation Result

**Status:** Code remediation complete. Production rollout is still required before
launch.

## Verification baseline

- `python -m pytest sim/tests -q`: **189 passed**
- Streamlit AppTest: **0 exceptions**
- Scenario gauntlet: **60/60 valid**, **0 difficulty mismatches**
- Generated Board Queries: **2,640 checked**, **0 duplicate visible options**
- Legacy-brand scan under `sim/`: **0 hits**
- `python -m pip check`: **no broken requirements**
- `git diff --check`: **clean** (line-ending notices only)
- Secret scan: no service-role key, signing-secret value or access token found

## Closed findings

### Critical — 2/2 remediated

- **CR-1 session isolation:** the mutable Supabase client now lives in each
  Streamlit `session_state`; logout destroys it. A two-session regression test
  proves separate clients are created.
- **CR-2 payment atomicity:** payment and entitlement processing moved to the
  transactional `process_ls_order` RPC in migration 0003. It serializes retries and
  simultaneous purchases, repairs a legacy payment missing its entitlement, and
  deduplicates both payment reference and entitlement source.

### High — 7/7 remediated

- **H-1:** webhook requires configured Lemon Squeezy store and variant allowlists.
- **H-2:** Board Queries unlock only after their round; stale future sets/results
  are discarded during hydration.
- **H-3:** generated questions are stored in `games.board_queries`, hydrated with
  the game, and persisted immediately when graded.
- **H-4:** demo consumption is a locked server-side profile flag. Game creation is
  an authenticated RPC; deleting a game never restores demo allowance.
- **H-5:** Finance UI exposes current-debt borrowing and preserves it in decisions
  and projected cash flow.
- **H-6:** cumulative score components are bounded at zero and at their maxima.
- **H-7:** root production dependencies, `Procfile`, `railway.json`, health check,
  Railway instructions and current launch checklist are present.

### Medium — 9/9 remediated

- **M-1:** formatted numeric distractors are made visibly unique; the full pool
  regression scan found zero duplicates.
- **M-2:** projected cash includes actual bond capacity, stock issue/buyback caps,
  capacity-sale proceeds and current-debt borrowing.
- **M-3:** valid zero values for dividend, AR/AP, capacity, recruiting and training
  survive reload and remain zero in controls.
- **M-4:** game headers use an expected revision timestamp before snapshot writes;
  stale tabs fail without overwriting the newer tab. Rewind/reset claim the
  revision before destructive timeline changes.
- **M-5:** Pydantic bounds reject forged finance, HR, TQM, marketing, production and
  round values before the engine runs; segment-specific MTBF remains engine-clamped.
- **M-6:** checkout custom data and email use URL encoding.
- **M-7:** Data API calls use ISO UTC timestamps; SQL functions use database
  timestamps inside RPCs.
- **M-8:** legacy product names were removed from runtime source, comments and tests;
  obsolete clone/parity planning documents were removed.
- **M-9:** stockout allocation records sales by actual buyer segment, and market
  reporting uses that exact allocation.

### Low / operational — 4/4 remediated in code

- Persistent refresh-cookie login is enabled and its dependency is installed.
- Authentication screens return safe public errors instead of raw provider errors.
- Deployment/status documentation was replaced with the current workflow.
- Dashboard newspaper mastheads were removed; the canonical masthead remains in
  Market Report.

## Required production rollout

These are external operations, not unresolved code findings:

1. Apply `supabase/migrations/0003_security_and_consistency.sql` to the live project.
2. Redeploy `supabase/functions/ls-webhook/index.ts`; set `LS_STORE_ID` and
   `LS_VARIANT_IDS` alongside the existing secrets.
3. Run the live two-user isolation/concurrent-tab test and resend one paid webhook
   to verify idempotency and entitlement repair against real Supabase.
4. Verify refresh-cookie login across a real browser reload, complete one Lemon
   Squeezy test purchase, then revoke temporary deployment tokens before launch.

Until those four rollout checks pass, the repository is locally verified but the
currently deployed service must not be described as fully remediated.
