{{
    config(
        materialized='table'
    )
}}

WITH artist_track_counts AS (
    SELECT
        artist_id,
        COUNT(DISTINCT track_id) AS track_count,
        AVG(popularity) AS avg_track_popularity,
        MAX(popularity) AS max_track_popularity,
        COUNT(DISTINCT CASE WHEN explicit THEN track_id END) AS explicit_track_count,
        COUNT(DISTINCT album_name) AS album_count,
        MIN(release_year) AS first_release_year,
        MAX(release_year) AS latest_release_year
    FROM {{ ref('silver_tracks') }}
    GROUP BY artist_id
)

SELECT
    a.artist_id,
    a.artist_name,
    a.genres_array,
    a.genre_count,
    a.popularity AS artist_popularity,
    a.followers_total,
    a.follower_popularity_ratio,
    a.is_japanese,
    -- Track metrics
    COALESCE(t.track_count, 0) AS track_count,
    COALESCE(t.avg_track_popularity, 0) AS avg_track_popularity,
    COALESCE(t.max_track_popularity, 0) AS max_track_popularity,
    COALESCE(t.explicit_track_count, 0) AS explicit_track_count,
    COALESCE(t.album_count, 0) AS album_count,
    t.first_release_year,
    t.latest_release_year,
    -- Career span in years
    CASE
        WHEN t.first_release_year IS NOT NULL AND t.latest_release_year IS NOT NULL
        THEN t.latest_release_year - t.first_release_year + 1
        ELSE NULL
    END AS career_span_years,
    -- Categorize artist by popularity
    CASE
        WHEN a.popularity >= 70 THEN 'Mainstream'
        WHEN a.popularity >= 40 THEN 'Mid-tier'
        WHEN a.popularity >= 20 THEN 'Emerging'
        ELSE 'Niche'
    END AS popularity_tier,
    -- Hidden gem score (high followers but lower popularity)
    CASE
        WHEN a.follower_popularity_ratio > 1000 AND a.popularity < 50 THEN TRUE
        ELSE FALSE
    END AS is_hidden_gem,
    a.spotify_url,
    a.loaded_at
FROM {{ ref('silver_artists') }} a
LEFT JOIN artist_track_counts t ON a.artist_id = t.artist_id
