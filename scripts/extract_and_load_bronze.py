"""
Extract Japanese music data from Spotify API and load into DuckDB bronze layer.

This script:
1. Searches for Japanese artists (j-pop, j-rock, city pop, anime)
2. Gets top tracks for each artist
3. Gets audio features for all tracks
4. Loads everything into DuckDB bronze tables
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import duckdb
import json

# Load environment variables
load_dotenv()

# Spotify API setup
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

if not client_id or not client_secret:
    print("❌ Error: Spotify credentials not found in .env file")
    sys.exit(1)

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

# DuckDB connection
DB_PATH = 'data/japanese_music.duckdb'
conn = duckdb.connect(DB_PATH)

print(f"🎵 Japanese Music Data Extraction")
print(f"=" * 60)
print(f"Database: {DB_PATH}")
print(f"Timestamp: {datetime.now()}\n")

# ============================================================================
# STEP 1: Create Bronze Tables
# ============================================================================

print("📊 Creating bronze layer tables...")

conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_artists (
    artist_id VARCHAR PRIMARY KEY,
    artist_name VARCHAR,
    genres JSON,
    popularity INTEGER,
    followers_total INTEGER,
    spotify_url VARCHAR,
    image_url VARCHAR,
    loaded_at TIMESTAMP,
    raw_json JSON
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_tracks (
    track_id VARCHAR PRIMARY KEY,
    track_name VARCHAR,
    artist_id VARCHAR,
    artist_name VARCHAR,
    album_name VARCHAR,
    album_type VARCHAR,
    release_date VARCHAR,
    release_date_precision VARCHAR,
    popularity INTEGER,
    duration_ms INTEGER,
    explicit BOOLEAN,
    spotify_url VARCHAR,
    loaded_at TIMESTAMP,
    raw_json JSON
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_audio_features (
    track_id VARCHAR PRIMARY KEY,
    danceability FLOAT,
    energy FLOAT,
    key INTEGER,
    loudness FLOAT,
    mode INTEGER,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    duration_ms INTEGER,
    time_signature INTEGER,
    loaded_at TIMESTAMP
)
""")

print("✅ Bronze tables created/verified\n")

# ============================================================================
# STEP 2: Search for Japanese Artists
# ============================================================================

print("🔍 Searching for Japanese artists...")

# Search queries for different Japanese music genres
search_queries = [
    'genre:j-pop',
    'genre:j-rock',
    'genre:anime',
    'city pop',
    'japanese indie',
]

artists_dict = {}  # Use dict to avoid duplicates

for query in search_queries:
    print(f"  Searching: {query}")
    try:
        results = sp.search(q=query, type='artist', limit=10)
        for artist in results['artists']['items']:
            if artist['id'] not in artists_dict:
                artists_dict[artist['id']] = artist
                print(f"    Found: {artist['name']}")
    except Exception as e:
        print(f"    ⚠️  Error searching '{query}': {e}")

print(f"\n✅ Found {len(artists_dict)} unique artists\n")

# ============================================================================
# STEP 3: Extract Artist Data and Load to Bronze
# ============================================================================

print("📥 Loading artist data to bronze_artists...")

loaded_at = datetime.now()
artists_loaded = 0

for artist_id, artist in artists_dict.items():
    try:
        # Get full artist details (includes more accurate data)
        full_artist = sp.artist(artist_id)

        conn.execute("""
            INSERT OR REPLACE INTO bronze_artists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_artist['id'],
            full_artist['name'],
            json.dumps(full_artist.get('genres', [])),
            full_artist.get('popularity', 0),
            full_artist.get('followers', {}).get('total', 0),
            full_artist.get('external_urls', {}).get('spotify', ''),
            full_artist['images'][0]['url'] if full_artist.get('images') else None,
            loaded_at,
            json.dumps(full_artist)
        ))
        artists_loaded += 1

    except Exception as e:
        print(f"  ⚠️  Error loading artist {artist.get('name', 'Unknown')}: {e}")

print(f"✅ Loaded {artists_loaded} artists\n")

# ============================================================================
# STEP 4: Extract Tracks for Each Artist
# ============================================================================

print("🎵 Extracting top tracks for each artist...")

tracks_dict = {}
tracks_loaded = 0

for artist_id in artists_dict.keys():
    try:
        # Get artist's top tracks
        top_tracks = sp.artist_top_tracks(artist_id, country='JP')

        for track in top_tracks['tracks']:
            if track['id'] not in tracks_dict:
                tracks_dict[track['id']] = track

                # Extract primary artist
                primary_artist = track['artists'][0]

                conn.execute("""
                    INSERT OR REPLACE INTO bronze_tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track['id'],
                    track['name'],
                    primary_artist['id'],
                    primary_artist['name'],
                    track['album']['name'],
                    track['album'].get('album_type', 'unknown'),
                    track['album'].get('release_date', ''),
                    track['album'].get('release_date_precision', 'day'),
                    track.get('popularity', 0),
                    track.get('duration_ms', 0),
                    track.get('explicit', False),
                    track.get('external_urls', {}).get('spotify', ''),
                    loaded_at,
                    json.dumps(track)
                ))
                tracks_loaded += 1

    except Exception as e:
        print(f"  ⚠️  Error getting tracks for artist {artist_id}: {e}")

print(f"✅ Loaded {tracks_loaded} tracks\n")

# ============================================================================
# STEP 5: Extract Audio Features for All Tracks
# ============================================================================

print("🎼 Extracting audio features for tracks...")

track_ids = list(tracks_dict.keys())
audio_features_loaded = 0

# Spotify API allows batch requests of up to 100 tracks
batch_size = 100

for i in range(0, len(track_ids), batch_size):
    batch = track_ids[i:i + batch_size]

    try:
        audio_features_batch = sp.audio_features(batch)

        for af in audio_features_batch:
            if af:  # Some tracks might not have audio features
                conn.execute("""
                    INSERT OR REPLACE INTO bronze_audio_features VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    af['id'],
                    af.get('danceability', 0.0),
                    af.get('energy', 0.0),
                    af.get('key', 0),
                    af.get('loudness', 0.0),
                    af.get('mode', 0),
                    af.get('speechiness', 0.0),
                    af.get('acousticness', 0.0),
                    af.get('instrumentalness', 0.0),
                    af.get('liveness', 0.0),
                    af.get('valence', 0.0),
                    af.get('tempo', 0.0),
                    af.get('duration_ms', 0),
                    af.get('time_signature', 4),
                    loaded_at
                ))
                audio_features_loaded += 1

    except Exception as e:
        print(f"  ⚠️  Error getting audio features for batch: {e}")

print(f"✅ Loaded {audio_features_loaded} audio features\n")

# ============================================================================
# STEP 6: Verify Data
# ============================================================================

print("=" * 60)
print("📊 Data Loading Summary")
print("=" * 60)

# Get counts
artist_count = conn.execute("SELECT COUNT(*) FROM bronze_artists").fetchone()[0]
track_count = conn.execute("SELECT COUNT(*) FROM bronze_tracks").fetchone()[0]
audio_feature_count = conn.execute("SELECT COUNT(*) FROM bronze_audio_features").fetchone()[0]

print(f"Artists:        {artist_count:>6}")
print(f"Tracks:         {track_count:>6}")
print(f"Audio Features: {audio_feature_count:>6}")

# Show sample data
print("\n" + "=" * 60)
print("🎤 Sample Artists")
print("=" * 60)
sample_artists = conn.execute("""
    SELECT artist_name, popularity, followers_total, JSON_EXTRACT(genres, '$') as genres
    FROM bronze_artists
    ORDER BY popularity DESC
    LIMIT 5
""").fetchall()

for name, pop, followers, genres in sample_artists:
    print(f"{name:30} | Pop: {pop:3} | Followers: {followers:>10,} | {genres}")

print("\n" + "=" * 60)
print("🎵 Sample Tracks")
print("=" * 60)
sample_tracks = conn.execute("""
    SELECT track_name, artist_name, popularity, album_name
    FROM bronze_tracks
    ORDER BY popularity DESC
    LIMIT 5
""").fetchall()

for track, artist, pop, album in sample_tracks:
    print(f"{track[:30]:30} | {artist[:20]:20} | Pop: {pop:3}")

print("\n" + "=" * 60)
print("✅ Bronze layer extraction complete!")
print("=" * 60)
print(f"\nDatabase location: {DB_PATH}")
print("\nYou can now query the data using DuckDB CLI or Python:")
print(f"  python -c \"import duckdb; conn = duckdb.connect('{DB_PATH}'); print(conn.execute('SELECT * FROM bronze_artists LIMIT 5').df())\"")

# Close connection
conn.close()

print("\n✨ Done! Your data is ready for exploration.")
