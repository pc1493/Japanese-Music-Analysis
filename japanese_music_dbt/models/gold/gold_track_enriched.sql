{{
    config(
        materialized='table'
    )
}}

SELECT
    t.track_id,
    t.track_name,
    t.artist_id,
    t.artist_name,
    a.is_japanese,
    a.popularity AS artist_popularity,
    a.genres_array,
    t.album_name,
    t.album_type,
    t.release_date_parsed,
    t.release_year,
    t.popularity AS track_popularity,
    t.duration_minutes,
    t.explicit,
    t.market_count,
    t.available_in_japan,
    t.globally_available,
    t.source_playlist,
    -- Audio features (will be NULL for most tracks)
    af.tempo,
    af.tempo_category,
    af.danceability,
    af.danceability_category,
    af.key_key,
    af.key_scale,
    af.loudness_mean,
    af.dynamic_complexity,
    -- Flag if audio features available
    CASE WHEN af.track_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_audio_features,
    t.spotify_url,
    t.loaded_at
FROM {{ ref('silver_tracks') }} t
LEFT JOIN {{ ref('silver_artists') }} a ON t.artist_id = a.artist_id
LEFT JOIN {{ ref('silver_audio_features') }} af ON t.track_id = af.track_id
