{{
    config(
        materialized='table'
    )
}}

WITH source AS (
    SELECT * FROM bronze_acousticbrainz_features
)

SELECT
    track_id,
    isrc,
    mbid,
    tempo,
    bpm_histogram_first_peak,
    bpm_histogram_second_peak,
    danceability,
    onset_rate,
    loudness_mean,
    dynamic_complexity,
    key_key,
    key_scale,
    -- Categorize tempo into buckets
    CASE
        WHEN tempo < 80 THEN 'Slow (< 80 BPM)'
        WHEN tempo >= 80 AND tempo < 120 THEN 'Moderate (80-120 BPM)'
        WHEN tempo >= 120 AND tempo < 160 THEN 'Fast (120-160 BPM)'
        WHEN tempo >= 160 THEN 'Very Fast (160+ BPM)'
        ELSE 'Unknown'
    END AS tempo_category,
    -- Categorize danceability
    CASE
        WHEN danceability < 0.8 THEN 'Low'
        WHEN danceability >= 0.8 AND danceability < 1.2 THEN 'Medium'
        WHEN danceability >= 1.2 THEN 'High'
        ELSE 'Unknown'
    END AS danceability_category,
    loaded_at
FROM source
WHERE track_id IS NOT NULL
