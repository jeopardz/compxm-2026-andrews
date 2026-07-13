-- Pre-validated scenario pool (see scripts/build_scenario_pool.py + sim/data/scenario_pool.json).
-- Every row here has passed the full validation gauntlet, so any scenario the app
-- serves is guaranteed playable to the end of round 4.

create table if not exists public.scenarios (
  id text primary key,                    -- generation id, e.g. 'gen-42-hard'
  seed int not null,
  target_difficulty text not null,        -- difficulty targeted during generation
  difficulty text not null,               -- difficulty the validator MEASURED (shown to user)
  avg_bsc numeric,
  final_stock numeric,
  cumulative_profit numeric,
  active boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists scenarios_active_difficulty_idx
  on public.scenarios (active, difficulty);

-- Any authenticated user may read the (non-secret) scenario catalogue.
alter table public.scenarios enable row level security;
drop policy if exists "read scenarios" on public.scenarios;
create policy "read scenarios" on public.scenarios
  for select using (auth.role() = 'authenticated');
-- Writes only via service_role (the pool loader), which bypasses RLS.
