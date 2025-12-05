{{
    config(
        materialized='table'
    )
}}

WITH genre_exploded AS (
    SELECT
        artist_id,
        artist_name,
        popularity,
        followers_total,
        is_japanese,
        UNNEST(genres_array) AS genre
    FROM {{ ref('silver_artists') }}
    WHERE len(genres_array) > 0
)

SELECT
    genre,
    COUNT(DISTINCT artist_id) AS artist_count,
    AVG(popularity) AS avg_popularity,
    SUM(followers_total) AS total_followers,
    COUNT(DISTINCT CASE WHEN is_japanese THEN artist_id END) AS japanese_artist_count,
    -- Percentage of artists that are Japanese
    ROUND(
        CAST(COUNT(DISTINCT CASE WHEN is_japanese THEN artist_id END) AS DOUBLE)
        / NULLIF(COUNT(DISTINCT artist_id), 0) * 100,
        1
    ) AS pct_japanese,
    -- Average popularity rank within genre
    ROUND(AVG(popularity), 1) AS avg_popularity_score
FROM genre_exploded
GROUP BY genre
HAVING COUNT(DISTINCT artist_id) >= 2  -- Only genres with 2+ artists
ORDER BY artist_count DESC
