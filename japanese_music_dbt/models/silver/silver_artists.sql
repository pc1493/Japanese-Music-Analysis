{{
    config(
        materialized='table'
    )
}}

WITH source AS (
    SELECT * FROM bronze_artists
),

parsed AS (
    SELECT
        artist_id,
        artist_name,
        -- Parse JSON genres array into proper array
        CASE
            WHEN genres IS NOT NULL THEN CAST(json_extract_string(genres, '$') AS VARCHAR[])
            ELSE []
        END AS genres_array,
        popularity,
        followers_total,
        spotify_url,
        image_url,
        is_japanese,
        loaded_at
    FROM source
)

SELECT
    artist_id,
    artist_name,
    genres_array,
    -- Calculate genre count
    CASE
        WHEN genres_array IS NOT NULL THEN len(genres_array)
        ELSE 0
    END AS genre_count,
    popularity,
    followers_total,
    -- Calculate follower-to-popularity ratio (hidden gems metric)
    CASE
        WHEN popularity > 0 THEN CAST(followers_total AS DOUBLE) / popularity
        ELSE 0
    END AS follower_popularity_ratio,
    spotify_url,
    image_url,
    CAST(is_japanese AS BOOLEAN) AS is_japanese,
    loaded_at
FROM parsed
WHERE artist_id IS NOT NULL
