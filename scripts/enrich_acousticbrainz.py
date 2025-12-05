"""
Enrich Spotify track data with AcousticBrainz audio features using ISRC lookups.

Process:
1. Read tracks with ISRC codes from bronze_tracks
2. Lookup ISRC in MusicBrainz to get MBID (MusicBrainz ID)
3. Fetch audio features from AcousticBrainz using MBID
4. Store results in bronze_acousticbrainz_features table

Note: AcousticBrainz stopped collecting in 2022, so only older tracks will have data.
Expected match rate: 30-50%
"""
import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import duckdb
import json

# Load environment variables
load_dotenv()

# DuckDB connection
DB_PATH = 'data/japanese_music.duckdb'
conn = duckdb.connect(DB_PATH)

print(f"🎼 AcousticBrainz Audio Features Enrichment")
print(f"=" * 70)
print(f"Database: {DB_PATH}")
print(f"Timestamp: {datetime.now()}\n")

# ============================================================================
# STEP 1: Create Bronze AcousticBrainz Table
# ============================================================================

print("📊 Creating bronze_acousticbrainz_features table...")

conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_acousticbrainz_features (
    track_id VARCHAR,  -- Spotify track ID
    isrc VARCHAR,
    mbid VARCHAR,  -- MusicBrainz ID
    tempo FLOAT,
    bpm_histogram_first_peak FLOAT,
    bpm_histogram_second_peak FLOAT,
    danceability FLOAT,
    onset_rate FLOAT,
    loudness_mean FLOAT,
    dynamic_complexity FLOAT,
    key_key VARCHAR,  -- Changed from INTEGER to VARCHAR (can be note name like "C#", "F#")
    key_scale VARCHAR,  -- "major" or "minor"
    loaded_at TIMESTAMP,
    raw_json JSON,
    PRIMARY KEY (track_id, mbid)  -- Allow multiple MBIDs per track
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_isrc_mbid_mapping (
    isrc VARCHAR PRIMARY KEY,
    mbid VARCHAR,
    track_name VARCHAR,
    artist_name VARCHAR,
    lookup_status VARCHAR,  -- 'success', 'not_found', 'error'
    looked_up_at TIMESTAMP
)
""")

print("✅ Tables created/verified\n")

# ============================================================================
# STEP 2: Fetch Tracks with ISRC Codes
# ============================================================================

print("🔍 Fetching tracks with ISRC codes from bronze_tracks...")

tracks_with_isrc = conn.execute("""
    SELECT track_id, track_name, artist_name, isrc
    FROM bronze_tracks
    WHERE isrc IS NOT NULL AND isrc != ''
    ORDER BY popularity DESC  -- Start with popular tracks (more likely to have data)
""").fetchall()

print(f"✅ Found {len(tracks_with_isrc)} tracks with ISRC codes\n")

if len(tracks_with_isrc) == 0:
    print("❌ No tracks with ISRC codes found. Run extract_japanese_music.py first.")
    conn.close()
    sys.exit(0)

# ============================================================================
# STEP 3: Helper Functions for API Calls
# ============================================================================

def lookup_isrc_in_musicbrainz(isrc):
    """
    Lookup ISRC in MusicBrainz to get MBID (MusicBrainz ID)
    Returns: list of MBIDs (can be multiple recordings per ISRC)
    """
    url = f"https://musicbrainz.org/ws/2/isrc/{isrc}"
    params = {
        'fmt': 'json',
        'inc': 'artist-credits'
    }
    headers = {
        'User-Agent': 'JapaneseMusicAnalytics/1.0 (educational project)'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            recordings = data.get('recordings', [])
            if recordings:
                # Return list of (mbid, title, artist) tuples
                results = []
                for rec in recordings:
                    mbid = rec.get('id')
                    title = rec.get('title', '')
                    artist = rec.get('artist-credit', [{}])[0].get('name', '') if rec.get('artist-credit') else ''
                    results.append((mbid, title, artist))
                return results
            else:
                return []
        elif response.status_code == 404:
            return []  # ISRC not found
        else:
            print(f"    ⚠️  MusicBrainz error {response.status_code} for ISRC {isrc}")
            return None  # Error
    except Exception as e:
        print(f"    ⚠️  MusicBrainz lookup failed for ISRC {isrc}: {e}")
        return None

def fetch_acousticbrainz_features(mbid):
    """
    Fetch audio features from AcousticBrainz using MBID
    Returns: dict with audio features or None
    """
    url = f"https://acousticbrainz.org/api/v1/{mbid}/low-level"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Extract key features
            rhythm = data.get('rhythm', {})
            tonal = data.get('tonal', {})

            features = {
                'tempo': rhythm.get('bpm', 0.0),
                'bpm_histogram_first_peak': rhythm.get('bpm_histogram_first_peak_bpm', {}).get('mean', 0.0),
                'bpm_histogram_second_peak': rhythm.get('bpm_histogram_second_peak_bpm', {}).get('mean', 0.0),
                'danceability': rhythm.get('danceability', 0.0),
                'onset_rate': rhythm.get('onset_rate', 0.0),
                'loudness_mean': data.get('lowlevel', {}).get('loudness', {}).get('mean', 0.0),
                'dynamic_complexity': data.get('lowlevel', {}).get('dynamic_complexity', 0.0),
                'key_key': str(tonal.get('key_key', 'unknown')),  # Convert to string
                'key_scale': str(tonal.get('key_scale', 'unknown')),  # Convert to string
                'raw_json': json.dumps(data)
            }
            return features
        elif response.status_code == 404:
            return None  # No data for this MBID
        else:
            print(f"    ⚠️  AcousticBrainz error {response.status_code} for MBID {mbid}")
            return None
    except Exception as e:
        print(f"    ⚠️  AcousticBrainz fetch failed for MBID {mbid}: {e}")
        return None

# ============================================================================
# STEP 4: Process Tracks - ISRC → MBID → Audio Features
# ============================================================================

print("🔄 Processing tracks (ISRC → MusicBrainz → AcousticBrainz)...")
print("   This may take a while due to rate limiting (10 req per 10 sec)...\n")

loaded_at = datetime.now()
processed_count = 0
success_count = 0
not_found_count = 0
error_count = 0

for track_id, track_name, artist_name, isrc in tracks_with_isrc:
    processed_count += 1

    # Check if we already looked up this ISRC
    existing = conn.execute("""
        SELECT lookup_status FROM bronze_isrc_mbid_mapping WHERE isrc = ?
    """, (isrc,)).fetchone()

    if existing:
        if processed_count % 10 == 0:
            print(f"  Progress: {processed_count}/{len(tracks_with_isrc)} | Success: {success_count} | Not found: {not_found_count}")
        continue  # Skip already processed

    print(f"  [{processed_count}/{len(tracks_with_isrc)}] {track_name[:40]:40} | ISRC: {isrc}")

    # Step 1: ISRC → MBID lookup
    mbid_results = lookup_isrc_in_musicbrainz(isrc)

    if mbid_results is None:
        # Error occurred
        conn.execute("""
            INSERT OR REPLACE INTO bronze_isrc_mbid_mapping VALUES (?, ?, ?, ?, ?, ?)
        """, (isrc, None, track_name, artist_name, 'error', loaded_at))
        error_count += 1
        time.sleep(1)  # Rate limit: be nice
        continue

    if len(mbid_results) == 0:
        # ISRC not found in MusicBrainz
        conn.execute("""
            INSERT OR REPLACE INTO bronze_isrc_mbid_mapping VALUES (?, ?, ?, ?, ?, ?)
        """, (isrc, None, track_name, artist_name, 'not_found', loaded_at))
        not_found_count += 1
        time.sleep(1)
        continue

    # Step 2: For each MBID, fetch audio features
    found_features = False
    for mbid, mb_title, mb_artist in mbid_results:
        # Fetch AcousticBrainz features
        features = fetch_acousticbrainz_features(mbid)

        if features:
            # Success! Store features
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO bronze_acousticbrainz_features VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track_id,
                    isrc,
                    mbid,
                    features['tempo'],
                    features['bpm_histogram_first_peak'],
                    features['bpm_histogram_second_peak'],
                    features['danceability'],
                    features['onset_rate'],
                    features['loudness_mean'],
                    features['dynamic_complexity'],
                    features['key_key'],
                    features['key_scale'],
                    loaded_at,
                    features['raw_json']
                ))

                # Record successful mapping
                conn.execute("""
                    INSERT OR REPLACE INTO bronze_isrc_mbid_mapping VALUES (?, ?, ?, ?, ?, ?)
                """, (isrc, mbid, track_name, artist_name, 'success', loaded_at))

                print(f"    ✅ Found features! Tempo: {features['tempo']:.1f} BPM, Danceability: {features['danceability']:.2f}")
                found_features = True
                success_count += 1
                break  # Stop after first successful match

            except Exception as e:
                print(f"    ⚠️  Error storing features: {e}")

        time.sleep(1)  # Rate limit: 1 sec between requests

    if not found_features:
        # MBID found but no AcousticBrainz data
        conn.execute("""
            INSERT OR REPLACE INTO bronze_isrc_mbid_mapping VALUES (?, ?, ?, ?, ?, ?)
        """, (isrc, mbid_results[0][0] if mbid_results else None, track_name, artist_name, 'no_ab_data', loaded_at))
        not_found_count += 1

    # Progress update every 10 tracks
    if processed_count % 10 == 0:
        print(f"\n  Progress: {processed_count}/{len(tracks_with_isrc)} | Success: {success_count} | Not found: {not_found_count}\n")

    # Rate limiting: MusicBrainz allows ~10 req per 10 sec
    time.sleep(1.5)

# ============================================================================
# STEP 5: Summary Statistics
# ============================================================================

print("\n" + "=" * 70)
print("📊 AcousticBrainz Enrichment Summary")
print("=" * 70)

ab_count = conn.execute("SELECT COUNT(DISTINCT track_id) FROM bronze_acousticbrainz_features").fetchone()[0]
mapping_count = conn.execute("SELECT COUNT(*) FROM bronze_isrc_mbid_mapping").fetchone()[0]
success_mapping = conn.execute("SELECT COUNT(*) FROM bronze_isrc_mbid_mapping WHERE lookup_status = 'success'").fetchone()[0]

print(f"Total tracks processed:        {processed_count:>6}")
print(f"Tracks with audio features:    {ab_count:>6} ({ab_count/len(tracks_with_isrc)*100:.1f}%)")
print(f"ISRC lookups performed:        {mapping_count:>6}")
print(f"  Successful:                  {success_mapping:>6}")
print(f"  Not found:                   {not_found_count:>6}")
print(f"  Errors:                      {error_count:>6}")

# Show sample enriched tracks
print("\n" + "=" * 70)
print("🎵 Sample Enriched Tracks (with Audio Features)")
print("=" * 70)

sample_enriched = conn.execute("""
    SELECT
        t.track_name,
        t.artist_name,
        a.tempo,
        a.danceability,
        a.key_scale
    FROM bronze_tracks t
    JOIN bronze_acousticbrainz_features a ON t.track_id = a.track_id
    ORDER BY t.popularity DESC
    LIMIT 10
""").fetchall()

for track, artist, tempo, dance, key in sample_enriched:
    print(f"{track[:35]:35} | {artist[:20]:20} | {tempo:>6.1f} BPM | Dance: {dance:.2f} | Key: {key}")

print("\n" + "=" * 70)
print("✅ AcousticBrainz enrichment complete!")
print("=" * 70)

if ab_count == 0:
    print("\n⚠️  No tracks matched with AcousticBrainz data.")
    print("   This is expected for:")
    print("   - Tracks released after 2022 (AcousticBrainz stopped collecting)")
    print("   - Very new or obscure tracks")
    print("   - Tracks with incorrect/missing ISRC codes")
    print("\n   You can still proceed with Silver layer using Spotify metadata only.")
else:
    print(f"\n✅ {ab_count} tracks now have enhanced audio features!")
    print(f"\n📌 Next Steps:")
    print(f"  1. Query enriched data: python scripts/sql_interactive.py")
    print(f"  2. Build Silver layer with dbt to combine Spotify + AcousticBrainz data")

# Close connection
conn.close()

print("\n✨ Done! Your data is now enriched with audio features.")
