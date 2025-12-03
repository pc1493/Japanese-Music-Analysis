"""
Interactive SQL query tool for bronze layer exploration.

Usage:
    python scripts/query_bronze.py

Or run specific query:
    python scripts/query_bronze.py "SELECT * FROM bronze_artists LIMIT 5"
"""
import duckdb
import sys

DB_PATH = 'data/japanese_music.duckdb'

def run_query(query):
    """Execute a SQL query and display results"""
    conn = duckdb.connect(DB_PATH, read_only=True)
    try:
        result = conn.execute(query).df()
        print(result.to_string())
        print(f"\nRows returned: {len(result)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def show_sample_queries():
    """Display helpful sample queries"""
    print("=" * 60)
    print("📊 Sample Queries for Bronze Layer Exploration")
    print("=" * 60)
    print("""
1. Count records in each table:
   SELECT 'Artists' as table_name, COUNT(*) as count FROM bronze_artists
   UNION ALL
   SELECT 'Tracks', COUNT(*) FROM bronze_tracks
   UNION ALL
   SELECT 'Audio Features', COUNT(*) FROM bronze_audio_features;

2. Top 10 most popular artists:
   SELECT artist_name, popularity, followers_total, JSON_EXTRACT(genres, '$') as genres
   FROM bronze_artists
   ORDER BY popularity DESC
   LIMIT 10;

3. Top 10 most popular tracks:
   SELECT track_name, artist_name, popularity, album_name
   FROM bronze_tracks
   ORDER BY popularity DESC
   LIMIT 10;

4. Audio feature summary:
   SELECT
       AVG(danceability) as avg_dance,
       AVG(energy) as avg_energy,
       AVG(valence) as avg_happiness,
       AVG(tempo) as avg_tempo
   FROM bronze_audio_features;

5. Tracks with audio features (joined):
   SELECT
       t.track_name,
       t.artist_name,
       t.popularity,
       af.energy,
       af.danceability,
       af.valence,
       af.tempo
   FROM bronze_tracks t
   JOIN bronze_audio_features af ON t.track_id = af.track_id
   ORDER BY t.popularity DESC
   LIMIT 10;

6. Genre distribution:
   SELECT
       genre,
       COUNT(*) as artist_count
   FROM bronze_artists,
   UNNEST(JSON_EXTRACT(genres, '$')) as genre
   GROUP BY genre
   ORDER BY artist_count DESC;

7. Release year distribution:
   SELECT
       SUBSTRING(release_date, 1, 4) as year,
       COUNT(*) as track_count,
       AVG(popularity) as avg_popularity
   FROM bronze_tracks
   WHERE release_date != ''
   GROUP BY year
   ORDER BY year DESC;

8. Find tracks with high energy but low popularity (hidden gems):
   SELECT
       t.track_name,
       t.artist_name,
       t.popularity,
       af.energy,
       af.danceability,
       af.valence
   FROM bronze_tracks t
   JOIN bronze_audio_features af ON t.track_id = af.track_id
   WHERE t.popularity < 50
     AND af.energy > 0.7
   ORDER BY af.energy DESC
   LIMIT 10;
""")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run query from command line argument
        query = ' '.join(sys.argv[1:])
        print(f"Running query: {query}\n")
        run_query(query)
    else:
        # Interactive mode
        show_sample_queries()
        print("\n" + "=" * 60)
        print("Enter your SQL query (or 'exit' to quit):")
        print("=" * 60)

        while True:
            try:
                query = input("\nSQL> ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                if query:
                    run_query(query)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break
