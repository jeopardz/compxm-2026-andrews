# BizSim SaaS status

The application, authentication, persistence, demo gate, payment webhook, scenario
pool and Railway configuration are implemented. Remediation is tracked in
`AUDIT_REPORT.md`.

## External launch actions

- Apply migration `0003_security_and_consistency.sql` (fresh projects apply 0001,
  0002, then 0003).
- Redeploy `ls-webhook` and set `LS_STORE_ID=428701` plus
  `LS_VARIANT_IDS=1893940` (verified from the public checkout on 14 July 2026).
- Configure a working `SUPPORT_EMAIL`, Sentry (or equivalent), and uptime checks.
- Deploy Railway and run the two-user and Lemon Squeezy production smoke tests.
- Revoke temporary deployment tokens and complete trademark review before launch.

Local verification: 189 tests pass, AppTest reports no exceptions, and all 60
scenarios pass validation with their recorded difficulty.
