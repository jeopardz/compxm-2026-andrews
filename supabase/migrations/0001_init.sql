-- SaaS schema for the business-simulation exam trainer.
-- Apply with the Supabase MCP (apply_migration) or the SQL editor.
-- Idempotent-ish: uses "if not exists" where possible so a re-run is safe.
--
-- Data isolation ("จำค่าของใครของมัน") is enforced by Row Level Security, not by
-- app code — even a buggy client cannot read another user's games.

-- ------------------------------------------------------------------
-- profiles: one row per auth user (populated by the trigger below)
-- ------------------------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text,
  created_at timestamptz not null default now()
);

-- ------------------------------------------------------------------
-- entitlements: one row per purchase; grants full access for a window
-- ------------------------------------------------------------------
create table if not exists public.entitlements (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  plan text not null check (plan in ('full_30d','full_90d','comp')),
  starts_at timestamptz not null default now(),
  expires_at timestamptz not null,
  source text,                          -- 'lemonsqueezy:<order_id>' | 'manual:<note>'
  created_at timestamptz not null default now()
);
create index if not exists entitlements_user_expiry_idx
  on public.entitlements (user_id, expires_at desc);

-- ------------------------------------------------------------------
-- games: one per playthrough (a user can hold several = replay/reset)
-- ------------------------------------------------------------------
create table if not exists public.games (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  label text not null default 'My Game',
  scenario text not null default 'exam-a',   -- scenario id (see sim/data/scenarios.py)
  current_round int not null default 0,
  status text not null default 'active' check (status in ('active','completed')),
  bsc_history jsonb not null default '[]',
  board_results jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists games_user_updated_idx
  on public.games (user_id, updated_at desc);

-- ------------------------------------------------------------------
-- game_snapshots: full board + pending decisions per round (Rewind)
-- state_json  = GameState.model_dump()
-- pending_json = RoundDecision.model_dump() | null
-- ------------------------------------------------------------------
create table if not exists public.game_snapshots (
  game_id uuid not null references public.games(id) on delete cascade,
  round int not null,
  state_json jsonb not null,
  pending_json jsonb,
  schema_version int not null default 1,
  saved_at timestamptz not null default now(),
  primary key (game_id, round)
);

-- ------------------------------------------------------------------
-- payments: audit trail; provider_ref unique so webhook re-sends dedupe
-- ------------------------------------------------------------------
create table if not exists public.payments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.profiles(id),
  amount numeric,
  currency text default 'USD',
  provider text not null default 'lemonsqueezy',
  provider_ref text unique,
  status text not null default 'paid',
  raw jsonb,
  created_at timestamptz not null default now()
);

-- ==================================================================
-- Row Level Security
-- ==================================================================
alter table public.profiles       enable row level security;
alter table public.entitlements   enable row level security;
alter table public.games          enable row level security;
alter table public.game_snapshots enable row level security;
alter table public.payments       enable row level security;

-- profiles: a user sees/edits only their own row
drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

-- entitlements: read-only to the owner; INSERT/UPDATE only via service_role
-- (the Lemon Squeezy webhook Edge Function), which bypasses RLS.
drop policy if exists "read own entitlements" on public.entitlements;
create policy "read own entitlements" on public.entitlements
  for select using (auth.uid() = user_id);

-- games: full CRUD on your own games
drop policy if exists "own games" on public.games;
create policy "own games" on public.games
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- game_snapshots: reachable only through a game you own
drop policy if exists "own snapshots" on public.game_snapshots;
create policy "own snapshots" on public.game_snapshots
  for all
  using (exists (select 1 from public.games g
                 where g.id = game_id and g.user_id = auth.uid()))
  with check (exists (select 1 from public.games g
                      where g.id = game_id and g.user_id = auth.uid()));

-- payments: read-only to the owner; writes only via service_role
drop policy if exists "read own payments" on public.payments;
create policy "read own payments" on public.payments
  for select using (auth.uid() = user_id);

-- ==================================================================
-- Auto-create a profile row when a user signs up
-- ==================================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
