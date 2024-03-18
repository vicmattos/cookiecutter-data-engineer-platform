
{{ config(tags=["randuser"]) }}


WITH years_old as (
    SELECT EXTRACT( YEAR FROM AGE(CURRENT_DATE, birth_day)) as old
    FROM {{ ref('randuser_users') }}
)

SELECT round(avg(old))
FROM years_old
