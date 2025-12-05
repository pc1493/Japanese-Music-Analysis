{{
    config(
        materialized='table'
    )
}}

WITH source AS (
    SELECT * FROM bronze_tracks
),

parsed AS (
    SELECT
        track_id,
        track_name,
        artist_id,
        artist_name,
        album_name,
        album_type,
        release_date,
        release_date_precision,
        -- Parse release year/month/day based on precision
        CASE
            WHEN release_date_precision = 'day' THEN TRY_CAST(release_date AS DATE)
            WHEN release_date_precision = 'month' THEN TRY_CAST(release_date || '-01' AS DATE)
            WHEN release_date_precision = 'year' THEN TRY_CAST(release_date || '-01-01' AS DATE)
            ELSE NULL
        END AS release_date_parsed,
        CASE
            WHEN release_date != '' THEN TRY_CAST(substr(release_date, 1, 4) AS INTEGER)
            ELSE NULL
        END AS release_year,
        popularity,
        duration_ms,
        -- Convert duration to minutes
        ROUND(CAST(duration_ms AS DOUBLE) / 60000, 2) AS duration_minutes,
        explicit,
        spotify_url,
        isrc,
        -- Parse available markets (convert JSON to proper array)
        CASE
            WHEN available_markets IS NOT NULL THEN CAST(json_extract_string(available_markets, '$') AS VARCHAR[])
            ELSE []
        END AS markets_array,
        source_playlist,
        loaded_at
    FROM source
)

SELECT
    track_id,
    track_name,
    artist_id,
    artist_name,
    album_name,
    album_type,
    release_date_parsed,
    release_year,
    popularity,
    duration_ms,
    duration_minutes,
    explicit,
    spotify_url,
    isrc,
    markets_array,
    -- Calculate market availability metrics
    CASE
        WHEN markets_array IS NOT NULL THEN len(markets_array)
        ELSE 0
    END AS market_count,
    -- Check if available in Japan
    CASE
        WHEN list_contains(markets_array, 'JP') THEN TRUE
        ELSE FALSE
    END AS available_in_japan,
    -- Check if globally available (>100 markets)
    CASE
        WHEN len(markets_array) > 100 THEN TRUE
        ELSE FALSE
    END AS globally_available,
    source_playlist,
    loaded_at
FROM parsed
WHERE track_id IS NOT NULL
