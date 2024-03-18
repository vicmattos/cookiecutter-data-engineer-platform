
{{ config(
    materialized='view',
    tags=["randuser"],
) }}

SELECT
    split_part(full_name, ' ', 1) as first_name,
    split_part(full_name, ' ', 2) as last_name,
    to_date(date_of_birth, 'YYYY-MM-DD') as birth_day,
    email
FROM stg_randuser.users
