"""
Interactive SQL session for querying the bronze layer.
Run this to get a persistent SQL prompt without typing 'python query_bronze.py' each time.
"""
import duckdb
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'japanese_music.duckdb'

def interactive_session():
    """Start an interactive SQL session"""
    print("🎵 Japanese Music Analytics - Interactive SQL Session")
    print("=" * 60)
    print(f"Connected to: {DB_PATH}")
    print("\nAvailable tables:")
    print("  - bronze_artists")
    print("  - bronze_tracks")
    print("  - bronze_audio_features")
    print("\nTips:")
    print("  - Type your SQL query and press Enter")
    print("  - Type 'exit' or 'quit' to close")
    print("  - Type 'tables' to see table counts")
    print("  - Type 'help' for sample queries")
    print("=" * 60)
    print()

    conn = duckdb.connect(str(DB_PATH))

    while True:
        try:
            # Get user input
            query = input("SQL> ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break

            if query.lower() == 'tables':
                result = conn.execute("""
                    SELECT 'Artists' as table_name, COUNT(*) as count FROM bronze_artists
                    UNION ALL
                    SELECT 'Tracks', COUNT(*) FROM bronze_tracks
                    UNION ALL
                    SELECT 'Audio Features', COUNT(*) FROM bronze_audio_features
                """).df()
                print(result.to_string(index=False))
                print()
                continue

            if query.lower() == 'help':
                print("\nSample Queries:")
                print("-" * 60)
                print("-- Count records")
                print("SELECT COUNT(*) FROM bronze_artists;")
                print()
                print("-- Top 10 artists by popularity")
                print("SELECT artist_name, popularity, followers_total")
                print("FROM bronze_artists ORDER BY popularity DESC LIMIT 10;")
                print()
                print("-- Search for specific artist")
                print("SELECT * FROM bronze_artists WHERE artist_name LIKE '%Ado%';")
                print()
                print("-- Tracks by a specific artist")
                print("SELECT track_name, popularity, album_name")
                print("FROM bronze_tracks WHERE artist_name = 'RADWIMPS';")
                print()
                print("-- Join artists and tracks")
                print("SELECT a.artist_name, COUNT(t.track_id) as track_count")
                print("FROM bronze_artists a")
                print("LEFT JOIN bronze_tracks t ON a.artist_id = t.artist_id")
                print("GROUP BY a.artist_name ORDER BY track_count DESC;")
                print("-" * 60)
                print()
                continue

            # Execute query
            result = conn.execute(query).df()

            if len(result) == 0:
                print("(No results)\n")
            else:
                print(result.to_string())
                print(f"\nRows: {len(result)}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

    conn.close()

if __name__ == "__main__":
    try:
        interactive_session()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
