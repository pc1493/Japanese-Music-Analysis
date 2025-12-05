import duckdb

conn = duckdb.connect('data/japanese_music.duckdb')

print('=' * 70)
print('Enrichment Verification')
print('=' * 70)

ab_count = conn.execute('SELECT COUNT(*) FROM bronze_acousticbrainz_features').fetchone()[0]
print(f'Tracks with audio features: {ab_count}')

mapping_count = conn.execute('SELECT COUNT(*) FROM bronze_isrc_mbid_mapping').fetchone()[0]
print(f'ISRC mappings: {mapping_count}')

success_count = conn.execute("SELECT COUNT(*) FROM bronze_isrc_mbid_mapping WHERE lookup_status = 'success'").fetchone()[0]
print(f'Successful lookups: {success_count}')

print('\n' + '=' * 70)
print('Sample Enriched Tracks')
print('=' * 70)

rows = conn.execute('''
    SELECT t.track_name, t.artist_name, a.tempo, a.danceability
    FROM bronze_tracks t
    JOIN bronze_acousticbrainz_features a ON t.track_id = a.track_id
    LIMIT 10
''').fetchall()

for track, artist, tempo, dance in rows:
    # Handle Unicode encoding for console
    track_safe = track[:30].encode('ascii', 'replace').decode('ascii')
    artist_safe = artist[:20].encode('ascii', 'replace').decode('ascii')
    print(f'{track_safe:30} | {artist_safe:20} | {tempo:.1f} BPM | Dance: {dance:.2f}')

conn.close()
print('\n' + '=' * 70)
print('Enrichment complete!')
print('=' * 70)
