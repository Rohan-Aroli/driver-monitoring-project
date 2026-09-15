-- Store the user-entered Driver ID in driver_metrics.id.
-- Existing metric rows are preserved as text IDs.
alter table public.driver_metrics
    alter column id drop identity if exists;

alter table public.driver_metrics
    alter column id type text
    using id::text;

create sequence if not exists public.driver_metrics_id_seq;

alter sequence public.driver_metrics_id_seq
    owned by public.driver_metrics.id;

alter table public.driver_metrics
    alter column id set default nextval('public.driver_metrics_id_seq')::text;

select setval(
    'public.driver_metrics_id_seq',
    coalesce(
        (select max(id::bigint) from public.driver_metrics where id ~ '^[0-9]+$'),
        0
    )
);
