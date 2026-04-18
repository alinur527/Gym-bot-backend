create table if not exists public.users (
    telegram_id bigint primary key,
    height_cm numeric(5,2),
    weight_kg numeric(5,2),
    body_type text,
    registered_at timestamptz not null default timezone('utc', now()),
    constraint users_height_positive check (height_cm is null or height_cm > 0),
    constraint users_weight_positive check (weight_kg is null or weight_kg > 0),
    constraint users_body_type_check check (
        body_type is null or body_type in ('ectomorph', 'mesomorph', 'endomorph')
    )
);

create table if not exists public.workout_sessions (
    id bigserial primary key,
    user_telegram_id bigint not null references public.users (telegram_id) on delete cascade,
    workout_date date not null default current_date,
    title text,
    notes text,
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists workout_sessions_user_telegram_id_idx
    on public.workout_sessions (user_telegram_id);

create table if not exists public.workout_sets (
    id bigserial primary key,
    session_id bigint not null references public.workout_sessions (id) on delete cascade,
    exercise_name text not null,
    set_number integer not null,
    weight_kg numeric(6,2),
    reps integer not null,
    created_at timestamptz not null default timezone('utc', now()),
    constraint workout_sets_set_number_positive check (set_number > 0),
    constraint workout_sets_reps_positive check (reps > 0),
    constraint workout_sets_weight_positive check (weight_kg is null or weight_kg >= 0)
);

create index if not exists workout_sets_session_id_idx
    on public.workout_sets (session_id);
