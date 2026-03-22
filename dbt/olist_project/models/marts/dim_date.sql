WITH date_spine AS (

    SELECT
        generate_series(
            '2016-01-01'::date,
            '2018-12-31'::date,
            interval '1 day'
        )::date AS date_day

)

SELECT
    date_day AS date_id,

    -- basic
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    EXTRACT(DAY FROM date_day) AS day,

    -- names
    TO_CHAR(date_day, 'Month') AS month_name,
    TO_CHAR(date_day, 'Day') AS day_name,

    -- week
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(DOW FROM date_day) AS day_of_week,

    -- flags
    CASE WHEN EXTRACT(DOW FROM date_day) IN (0,6) THEN TRUE ELSE FALSE END AS is_weekend,

    -- useful formats
    TO_CHAR(date_day, 'YYYY-MM') AS year_month,
    TO_CHAR(date_day, 'YYYY-MM-DD') AS full_date

FROM date_spine