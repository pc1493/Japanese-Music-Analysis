{{
    config(
        materialized='table'
    )
}}

-- This table focuses on the 63 tracks with audio features
WITH tracks_with_audio AS (
    SELECT
        t.track_id,
        t.track_name,
        t.artist_name,
        a.genres_array,
        t.popularity AS track_popularity,
        t.release_year,
        af.tempo,
        af.tempo_category,
        af.danceability,
        af.danceability_category,
        af.key_key,
        af.key_scale,
        af.loudness_mean,
        af.dynamic_complexity,
        af.onset_rate
    FROM {{ ref('silver_tracks') }} t
    INNER JOIN {{ ref('silver_audio_features') }} af ON t.track_id = af.track_id
    LEFT JOIN {{ ref('silver_artists') }} a ON t.artist_id = a.artist_id
)

SELECT
    track_id,
    track_name,
    artist_name,
    genres_array,
    track_popularity,
    release_year,
    tempo,
    tempo_category,
    danceability,
    danceability_category,
    key_key,
    key_scale,
    loudness_mean,
    dynamic_complexity,
    onset_rate,
    -- Classify track energy based on tempo and danceability
    CASE
        WHEN tempo > 140 AND danceability > 1.2 THEN 'High Energy'
        WHEN tempo > 120 OR danceability > 1.0 THEN 'Medium Energy'
        ELSE 'Low Energy'
    END AS energy_level,
    -- Classify by key scale
    CASE
        WHEN key_scale = 'major' THEN 'Major (Upbeat)'
        WHEN key_scale = 'minor' THEN 'Minor (Melancholic)'
        ELSE 'Unknown'
    END AS mood_indicator
FROM tracks_with_audio
