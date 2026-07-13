-- BizSim SaaS security and consistency hardening.
alter table public.profiles add column if not exists demo_game_consumed boolean not null default false;
alter table public.games add column if not exists board_queries jsonb not null default '{}';

update public.profiles p set demo_game_consumed = true
where exists (select 1 from public.games g where g.user_id = p.id);

delete from public.entitlements a using public.entitlements b
where a.source is not null and a.source = b.source
  and (a.created_at, a.id) > (b.created_at, b.id);
create unique index if not exists entitlements_source_unique_idx
  on public.entitlements (source) where source is not null;

drop policy if exists "own profile" on public.profiles;
drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles for select using (auth.uid() = id);

drop policy if exists "own games" on public.games;
drop policy if exists "read own games" on public.games;
drop policy if exists "update own games" on public.games;
drop policy if exists "delete own games" on public.games;
create policy "read own games" on public.games for select using (auth.uid() = user_id);
create policy "update own games" on public.games for update
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "delete own games" on public.games for delete using (auth.uid() = user_id);

create or replace function public.create_game(p_label text, p_scenario text, p_state_json jsonb)
returns uuid language plpgsql security definer set search_path = public, pg_temp as $$
declare
  v_uid uuid := auth.uid(); v_consumed boolean; v_full boolean; v_game_id uuid;
begin
  if v_uid is null then raise exception 'authentication required'; end if;
  select demo_game_consumed into v_consumed from public.profiles where id = v_uid for update;
  if not found then raise exception 'profile not found'; end if;
  select exists(select 1 from public.entitlements
    where user_id = v_uid and expires_at > statement_timestamp()) into v_full;
  if v_consumed and not v_full then raise exception 'demo game already consumed'; end if;
  insert into public.games (user_id, label, scenario)
  values (v_uid, left(coalesce(nullif(trim(p_label), ''), 'My Game'), 80), p_scenario)
  returning id into v_game_id;
  insert into public.game_snapshots (game_id, round, state_json, pending_json, schema_version)
  values (v_game_id, 0, p_state_json, null, 1);
  if not v_full then update public.profiles set demo_game_consumed = true where id = v_uid; end if;
  return v_game_id;
end; $$;
revoke all on function public.create_game(text,text,jsonb) from public;
grant execute on function public.create_game(text,text,jsonb) to authenticated;

create or replace function public.update_game_header(
  p_game_id uuid, p_expected_updated_at timestamptz, p_current_round int,
  p_status text, p_bsc_history jsonb, p_board_results jsonb, p_board_queries jsonb
) returns timestamptz language plpgsql security invoker set search_path = public, pg_temp as $$
declare v_updated_at timestamptz;
begin
  update public.games set current_round = p_current_round, status = p_status,
    bsc_history = coalesce(p_bsc_history, '[]'::jsonb),
    board_results = coalesce(p_board_results, '{}'::jsonb),
    board_queries = coalesce(p_board_queries, '{}'::jsonb), updated_at = clock_timestamp()
  where id = p_game_id and user_id = auth.uid()
    and (p_expected_updated_at is null or updated_at = p_expected_updated_at)
  returning updated_at into v_updated_at;
  return v_updated_at;
end; $$;
revoke all on function public.update_game_header(uuid,timestamptz,int,text,jsonb,jsonb,jsonb) from public;
grant execute on function public.update_game_header(uuid,timestamptz,int,text,jsonb,jsonb,jsonb) to authenticated;

create or replace function public.process_ls_order(
  p_user_id uuid, p_order_id text, p_amount numeric, p_currency text, p_raw jsonb
) returns boolean language plpgsql security definer set search_path = public, pg_temp as $$
declare v_source text := 'lemonsqueezy:' || p_order_id; v_owner uuid; v_base timestamptz;
begin
  if p_order_id is null or p_order_id = '' then raise exception 'order id required'; end if;
  perform pg_advisory_xact_lock(hashtext('ls:' || p_order_id));
  perform pg_advisory_xact_lock(hashtext('ls-user:' || p_user_id::text));
  if not exists (select 1 from public.profiles where id = p_user_id) then raise exception 'unknown user'; end if;
  insert into public.payments (user_id, provider, provider_ref, amount, currency, status, raw)
  values (p_user_id, 'lemonsqueezy', p_order_id, p_amount,
    upper(coalesce(p_currency, 'USD')), 'paid', p_raw)
  on conflict (provider_ref) do nothing;
  select user_id into v_owner from public.payments where provider_ref = p_order_id;
  if v_owner is distinct from p_user_id then raise exception 'order owner mismatch'; end if;
  if exists (select 1 from public.entitlements where source = v_source) then return false; end if;
  select expires_at into v_base from public.entitlements
    where user_id = p_user_id and expires_at > statement_timestamp()
    order by expires_at desc limit 1 for update;
  v_base := greatest(coalesce(v_base, statement_timestamp()), statement_timestamp());
  insert into public.entitlements (user_id, plan, starts_at, expires_at, source)
  values (p_user_id, 'full_30d', statement_timestamp(), v_base + interval '30 days', v_source)
  on conflict (source) where source is not null do nothing;
  return true;
end; $$;
revoke all on function public.process_ls_order(uuid,text,numeric,text,jsonb) from public;
grant execute on function public.process_ls_order(uuid,text,numeric,text,jsonb) to service_role;
