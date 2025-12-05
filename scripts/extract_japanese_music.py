"""
Extract Japanese music from Spotify using hybrid approach:
1. Japanese-specific playlists (high confidence)
2. Artist genre filtering (j-pop, j-rock, anime, etc.)
3. Artist name pattern matching (Japanese characters)
4. Market availability checking

Loads data into DuckDB bronze layer:
- bronze_artists
- bronze_tracks
- bronze_audio_features (empty - API deprecated)
"""
import os
import sys
import time
import re
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

print(f"🎌 Japanese Music Data Extraction")
print(f"=" * 70)
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
    raw_json JSON,
    is_japanese INTEGER  -- 1 = Japanese, 0 = Not Japanese (DuckDB doesn't have native BOOLEAN in older versions)
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
    isrc VARCHAR,  -- IMPORTANT: For AcousticBrainz lookup
    available_markets JSON,  -- To check JP market availability
    loaded_at TIMESTAMP,
    raw_json JSON,
    source_playlist VARCHAR  -- Track which playlist this came from
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
# STEP 2: Helper Functions for Japanese Detection
# ============================================================================

def has_japanese_characters(text):
    """Check if text contains Japanese characters (Hiragana, Katakana, Kanji)"""
    if not text:
        return False
    # Unicode ranges for Japanese scripts
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
    return bool(japanese_pattern.search(text))

def has_japanese_genre(genres):
    """Check if artist has Japanese-related genres"""
    japanese_genres = [
        'j-pop', 'j-rock', 'j-rap', 'j-indie', 'j-dance',
        'city pop', 'shibuya-kei', 'anime', 'japanese r&b',
        'japanese rock', 'japanese hip hop', 'jpop', 'jrock',
        'visual kei', 'enka', 'kayokyoku'
    ]
    if not genres:
        return False
    return any(jgenre in genre.lower() for jgenre in japanese_genres for genre in genres)

def is_japanese_artist(artist_data):
    """Determine if artist is Japanese using multiple signals"""
    # Signal 1: Japanese characters in name
    has_jp_name = has_japanese_characters(artist_data.get('name', ''))

    # Signal 2: Japanese genre tags
    has_jp_genre = has_japanese_genre(artist_data.get('genres', []))

    # If either signal is true, consider Japanese
    return has_jp_name or has_jp_genre

# ============================================================================
# STEP 3: Extract from Japanese Playlists
# ============================================================================

# Initialize data structures
all_tracks = {}
all_artists = {}
loaded_at = datetime.now()

print("🔍 Searching for Japanese playlists...")

# Search for Japanese playlists instead of using hardcoded IDs
japanese_playlists = []
search_terms = ['Japan Top', 'J-Pop', 'Japanese Music', 'City Pop', 'Tokyo Hits', 'Anime Music']

for search_term in search_terms:
    try:
        results = sp.search(q=search_term, type='playlist', limit=5)
        for playlist in results['playlists']['items']:
            if playlist and playlist.get('id'):
                japanese_playlists.append((playlist['id'], playlist['name']))
        time.sleep(0.5)  # Rate limiting
    except Exception as e:
        print(f"  ⚠️ Error searching for '{search_term}': {e}")

print(f"✅ Found {len(japanese_playlists)} playlists to process\n")

if len(japanese_playlists) == 0:
    print("❌ No Japanese playlists found. Trying fallback approach...")
    # Fallback: Use genre-based artist search instead
    print("🔍 Searching for Japanese artists by genre...\n")

    japanese_genres = ['j-pop', 'j-rock', 'city pop', 'anime']
    for genre_query in japanese_genres:
        try:
            results = sp.search(q=f'genre:{genre_query}', type='artist', limit=50)
            print(f"  Found {len(results['artists']['items'])} artists for genre: {genre_query}")
            for artist in results['artists']['items']:
                if artist and artist.get('id'):
                    all_artists[artist['id']] = None  # Will fetch full details later
            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ Error searching genre '{genre_query}': {e}")

    # Skip playlist processing, go straight to artist fetching
    print(f"\n✅ Found {len(all_artists)} unique artists from genre search")
    print("📌 Skipping playlist extraction, using genre-based artist search instead\n")

# Only process playlists if we found any
if len(japanese_playlists) > 0:
    print("🎵 Extracting tracks from playlists...\n")

    for playlist_id, playlist_name in japanese_playlists:
        print(f"\n  📂 Processing: {playlist_name}")
        try:
            # Get playlist tracks (limit 100 per request, pagination if needed)
            results = sp.playlist_tracks(playlist_id, limit=100)
            track_count = 0

            while results:
                for item in results['items']:
                    if not item or not item.get('track'):
                        continue

                    track = item['track']
                    if not track or not track.get('id'):
                        continue

                    track_id = track['id']

                    # Skip duplicates
                    if track_id in all_tracks:
                        continue

                    # Extract track data
                    primary_artist = track['artists'][0] if track.get('artists') else {}

                    track_data = {
                        'track_id': track_id,
                        'track_name': track.get('name', ''),
                        'artist_id': primary_artist.get('id', ''),
                        'artist_name': primary_artist.get('name', ''),
                        'album_name': track['album'].get('name', '') if track.get('album') else '',
                        'album_type': track['album'].get('album_type', 'unknown') if track.get('album') else 'unknown',
                        'release_date': track['album'].get('release_date', '') if track.get('album') else '',
                        'release_date_precision': track['album'].get('release_date_precision', 'day') if track.get('album') else 'day',
                        'popularity': track.get('popularity', 0),
                        'duration_ms': track.get('duration_ms', 0),
                        'explicit': track.get('explicit', False),
                        'spotify_url': track.get('external_urls', {}).get('spotify', ''),
                        'isrc': track.get('external_ids', {}).get('isrc', ''),  # KEY for AcousticBrainz
                        'available_markets': json.dumps(track.get('available_markets', [])),
                        'source_playlist': playlist_name,
                        'raw_json': json.dumps(track)
                    }

                    all_tracks[track_id] = track_data
                    track_count += 1

                    # Collect artist ID for later lookup
                    if primary_artist.get('id'):
                        all_artists[primary_artist['id']] = None  # Will fetch full details later

                # Check if there are more pages
                if results['next']:
                    results = sp.next(results)
                else:
                    break

            print(f"    ✅ Found {track_count} unique tracks")

            # Rate limiting: be nice to Spotify API
            time.sleep(0.5)

        except Exception as e:
            print(f"    ⚠️  Error processing playlist '{playlist_name}': {e}")

print(f"\n✅ Total unique tracks from playlists: {len(all_tracks)}")
print(f"✅ Total unique artists to fetch: {len(all_artists)}")

# ============================================================================
# STEP 4: Fetch Full Artist Details
# ============================================================================

print(f"\n👤 Fetching full artist details...")

artists_loaded = 0
for artist_id in all_artists.keys():
    try:
        # Get full artist details
        full_artist = sp.artist(artist_id)

        # Check if artist is Japanese
        is_jp = is_japanese_artist(full_artist)

        artist_data = {
            'artist_id': full_artist['id'],
            'artist_name': full_artist['name'],
            'genres': json.dumps(full_artist.get('genres', [])),
            'popularity': full_artist.get('popularity', 0),
            'followers_total': full_artist.get('followers', {}).get('total', 0),
            'spotify_url': full_artist.get('external_urls', {}).get('spotify', ''),
            'image_url': full_artist['images'][0]['url'] if full_artist.get('images') else None,
            'is_japanese': is_jp,
            'raw_json': json.dumps(full_artist)
        }

        all_artists[artist_id] = artist_data
        artists_loaded += 1

        # Rate limiting
        if artists_loaded % 50 == 0:
            print(f"  Progress: {artists_loaded}/{len(all_artists)} artists fetched...")
            time.sleep(1)  # Extra pause every 50 requests

    except Exception as e:
        print(f"  ⚠️  Error fetching artist {artist_id}: {e}")
        all_artists[artist_id] = None  # Mark as failed

print(f"✅ Fetched {artists_loaded} artists\n")

# ============================================================================
# STEP 5: Load Artists to Bronze
# ============================================================================

print("📥 Loading artist data to bronze_artists...")

for artist_id, artist_data in all_artists.items():
    if artist_data is None:
        continue

    try:
        conn.execute("""
            INSERT OR REPLACE INTO bronze_artists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artist_data['artist_id'],
            artist_data['artist_name'],
            artist_data['genres'],
            artist_data['popularity'],
            artist_data['followers_total'],
            artist_data['spotify_url'],
            artist_data['image_url'],
            loaded_at,
            artist_data['raw_json'],
            artist_data['is_japanese']
        ))
    except Exception as e:
        print(f"  ⚠️  Error loading artist {artist_data.get('artist_name', 'Unknown')}: {e}")

print(f"✅ Loaded {len([a for a in all_artists.values() if a])} artists to bronze_artists\n")

# ============================================================================
# STEP 6: Load Tracks to Bronze
# ============================================================================

print("📥 Loading track data to bronze_tracks...")

tracks_loaded = 0
for track_id, track_data in all_tracks.items():
    try:
        conn.execute("""
            INSERT OR REPLACE INTO bronze_tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            track_data['track_id'],
            track_data['track_name'],
            track_data['artist_id'],
            track_data['artist_name'],
            track_data['album_name'],
            track_data['album_type'],
            track_data['release_date'],
            track_data['release_date_precision'],
            track_data['popularity'],
            track_data['duration_ms'],
            track_data['explicit'],
            track_data['spotify_url'],
            track_data['isrc'],
            track_data['available_markets'],
            loaded_at,
            track_data['raw_json'],
            track_data['source_playlist']
        ))
        tracks_loaded += 1
    except Exception as e:
        print(f"  ⚠️  Error loading track {track_data.get('track_name', 'Unknown')}: {e}")

print(f"✅ Loaded {tracks_loaded} tracks to bronze_tracks\n")

# ============================================================================
# STEP 7: Summary Statistics
# ============================================================================

print("=" * 70)
print("📊 Data Loading Summary")
print("=" * 70)

# Get counts
artist_count = conn.execute("SELECT COUNT(*) FROM bronze_artists").fetchone()[0]
japanese_artist_count = conn.execute("SELECT COUNT(*) FROM bronze_artists WHERE is_japanese = 1").fetchone()[0]
track_count = conn.execute("SELECT COUNT(*) FROM bronze_tracks").fetchone()[0]
tracks_with_isrc = conn.execute("SELECT COUNT(*) FROM bronze_tracks WHERE isrc IS NOT NULL AND isrc != ''").fetchone()[0]

print(f"Artists:          {artist_count:>6}")
print(f"  Japanese:       {japanese_artist_count:>6}")
print(f"Tracks:           {track_count:>6}")
print(f"  With ISRC:      {tracks_with_isrc:>6} (for AcousticBrainz lookup)")

# Show sample Japanese artists
print("\n" + "=" * 70)
print("🎤 Sample Japanese Artists")
print("=" * 70)
sample_artists = conn.execute("""
    SELECT artist_name, popularity, followers_total, is_japanese
    FROM bronze_artists
    WHERE is_japanese = 1
    ORDER BY popularity DESC
    LIMIT 10
""").fetchall()

for name, pop, followers, is_jp in sample_artists:
    jp_flag = "🎌" if is_jp else ""
    print(f"{jp_flag} {name:30} | Pop: {pop:3} | Followers: {followers:>10,}")

# Show sample tracks
print("\n" + "=" * 70)
print("🎵 Sample Tracks (with ISRC codes)")
print("=" * 70)
sample_tracks = conn.execute("""
    SELECT track_name, artist_name, isrc, source_playlist
    FROM bronze_tracks
    WHERE isrc IS NOT NULL AND isrc != ''
    ORDER BY popularity DESC
    LIMIT 10
""").fetchall()

for track, artist, isrc, playlist in sample_tracks:
    print(f"{track[:35]:35} | {artist[:20]:20} | ISRC: {isrc} | From: {playlist}")

print("\n" + "=" * 70)
print("✅ Bronze layer extraction complete!")
print("=" * 70)
print(f"\nDatabase location: {DB_PATH}")
print(f"\n📌 Next Steps:")
print(f"  1. Run: python scripts/enrich_acousticbrainz.py")
print(f"     (This will use ISRC codes to fetch audio features)")
print(f"  2. Query data using DBeaver or: python scripts/sql_interactive.py")
print(f"  3. Build Silver layer with dbt")

# Close connection
conn.close()

print("\n✨ Done! Your Japanese music data is ready for analysis.")
