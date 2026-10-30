-- 峽谷鬼影計時賽：排行榜＋鬼影資料表
-- 在 Supabase → SQL Editor → New query 整份貼上，按 Run。
-- 會新建 canyon_scores，不會動到原本的 flip_scores / flight_scores。
-- 之前跑過舊版也沒關係，直接再跑一次這份就會自動升級。

create table if not exists public.canyon_scores (
  id          bigserial primary key,
  board       text        not null check (char_length(board) between 1 and 60),
  name        text        not null check (char_length(name) between 1 and 12),
  score       numeric(7,1) not null,
  flight      numeric(7,1) not null check (flight between 15 and 600),
  rings       smallint    not null,           -- 答對題數
  total       smallint    not null default 3, -- 總題數
  -- 鬼影：每 0.1 秒一筆 [x, y, z, roll] 的整數陣列，最多 180 秒
  ghost       jsonb       check (ghost is null or (jsonb_typeof(ghost) = 'array' and jsonb_array_length(ghost) <= 7200)),
  created_at  timestamptz not null default now()
);

-- 舊版升級：補上「總題數」欄位，拿掉舊的檢查條件
alter table public.canyon_scores add column if not exists total smallint not null default 3;
alter table public.canyon_scores drop constraint if exists canyon_scores_rings_check;
alter table public.canyon_scores drop constraint if exists canyon_score_rule;
alter table public.canyon_scores drop constraint if exists canyon_rings_ok;

-- 題數要合理，成績一定要等於「飛行時間＋每答錯一題加 5 秒」，亂送的數字會被擋下
alter table public.canyon_scores add constraint canyon_rings_ok
  check (total between 1 and 20 and rings between 0 and total);
alter table public.canyon_scores add constraint canyon_score_rule
  check (score = flight + (total - rings) * 5);

create index if not exists canyon_scores_board_score
  on public.canyon_scores (board, score, created_at);

alter table public.canyon_scores enable row level security;

-- 只開放「讀取」和「新增一筆」，沒有開放修改和刪除
drop policy if exists "canyon read"   on public.canyon_scores;
drop policy if exists "canyon insert" on public.canyon_scores;
create policy "canyon read"   on public.canyon_scores for select to anon using (true);
create policy "canyon insert" on public.canyon_scores for insert to anon with check (true);

grant select, insert on public.canyon_scores to anon;
grant usage, select on sequence public.canyon_scores_id_seq to anon;
