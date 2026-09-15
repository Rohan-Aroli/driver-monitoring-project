-- The user-entered Driver ID is not driver_metrics.id.
-- Keep the auto-generated primary key and allow IDs such as drv-f001-d001.
alter table public.driver_metrics
    alter column driver_id type text
    using driver_id::text;
