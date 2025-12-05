# Japanese Music Analytics Project

## Overview
A **complete data engineering portfolio project** analyzing Japanese music trends using Spotify data. Built with modern data stack (DuckDB + dbt + Streamlit) implementing medallion architecture to demonstrate production-ready analytics skills.

**Project Type**: Portfolio / Learning Project
**Status**: ✅ **COMPLETE** - Full pipeline built (Bronze → Silver → Gold + Dashboard)
**Live Dashboard**: Run with `streamlit run dashboard/app.py`

## 🎯 Project Goals
1. ✅ **Extract and enrich** Japanese music data from Spotify (2,266 tracks, 876 artists)
2. ✅ **Build production-ready** medallion architecture with dbt transformations
3. ✅ **Create interactive dashboard** with meaningful insights and visualizations
4. ✅ **Demonstrate data engineering** best practices for portfolio/employers

---

## 📊 Dataset Summary

| Metric | Count | Details |
|--------|-------|---------|
| **Artists** | 876 | 533 Japanese (61%), 343 non-Japanese |
| **Tracks** | 2,266 | Extracted from curated Spotify playlists |
| **Genres** | 150+ | From j-pop to city pop to anime soundtracks |
| **Audio Features** | 63 tracks | Via AcousticBrainz (ISRC→MBID lookup) |
| **Time Range** | 1970s-2024 | Focus on recent releases (2010+) |

---

## 🛠️ Tech Stack (100% Free & Local)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | Spotify Web API | Extract artist/track metadata (2,266 tracks) |
| **Enrichment** | AcousticBrainz API | Audio features (tempo, danceability, key) |
| **Database** | DuckDB 1.1.3 | Embedded analytical database (no server) |
| **Transformation** | dbt-core 1.7.9 | SQL-based data transformations (7 models) |
| **Orchestration** | Python 3.10+ | Custom extraction scripts with parallel processing |
| **Visualization** | Streamlit + Plotly | Interactive multi-page dashboard |
| **Version Control** | Git + GitHub | Code repository and collaboration |

**All tools run 100% locally** - no cloud services, no costs, no deployment needed.

---

## 🏗️ Project Structure

```
Japanese-Music-Analysis/
├── data/
│   └── japanese_music.duckdb          # DuckDB database (contains all layers)
│       ├── Bronze: 5 tables (raw data)
│       ├── Silver: 3 tables (cleaned)
│       └── Gold: 4 tables (analytics)
│
├── scripts/                            # Python extraction & enrichment
│   ├── extract_japanese_music.py      # Main extraction (hybrid approach)
│   ├── enrich_acousticbrainz_parallel.py  # Parallel audio feature enrichment
│   ├── enrich_acousticbrainz.py       # Sequential version (baseline)
│   ├── sql_interactive.py             # Interactive SQL REPL
│   └── test_spotify.py                # API connection test
│
├── japanese_music_dbt/                 # dbt transformation project
│   ├── models/
│   │   ├── silver/                    # 3 cleaned models
│   │   │   ├── silver_artists.sql
│   │   │   ├── silver_tracks.sql
│   │   │   └── silver_audio_features.sql
│   │   └── gold/                      # 4 analytics models
│   │       ├── gold_artist_metrics.sql
│   │       ├── gold_genre_analysis.sql
│   │       ├── gold_track_enriched.sql
│   │       └── gold_audio_insights.sql
│   ├── profiles.yml                   # DuckDB connection config
│   └── dbt_project.yml                # Project configuration
│
├── dashboard/
│   └── app.py                          # Streamlit dashboard (5 pages)
│
├── docs/
│   ├── SETUP_GUIDE.md                  # Installation instructions
│   └── PROJECT_STATUS.md               # Detailed progress log
│
├── requirements.txt                    # Python dependencies
├── .env                                # Spotify API credentials (gitignored)
├── .gitignore                          # Protects sensitive files
└── README.md                           # This file
```

---

## 🗄️ Medallion Architecture

### **Bronze Layer** (Raw Data - 5 tables)
Stores data exactly as received from APIs with full audit trail.

- `bronze_artists` - 876 rows (artist metadata, genres, popularity, followers)
- `bronze_tracks` - 2,266 rows (track info, ISRC codes, market availability)
- `bronze_acousticbrainz_features` - 63 rows (tempo, danceability, key)
- `bronze_isrc_mbid_mapping` - 2,096 rows (ISRC→MBID lookup cache)
- `bronze_audio_features` - 0 rows (Spotify API deprecated Nov 2024)

**Characteristics**:
- No transformations, store raw JSON
- `loaded_at` timestamps for audit trail
- Idempotent with `INSERT OR REPLACE`

### **Silver Layer** (Cleaned Data - 3 tables)
Clean, deduplicate, and standardize for downstream consumption.

- `silver_artists` - Parsed genres array, calculated follower/popularity ratio
- `silver_tracks` - Standardized dates, market arrays, duration conversion
- `silver_audio_features` - Categorized tempo (slow/moderate/fast), danceability levels

**Transformations**:
- Parse JSON → typed arrays
- Handle null values with business rules
- Cast types (dates, booleans)
- Data quality validated

### **Gold Layer** (Analytics-Ready - 4 tables)
Business logic applied, aggregations optimized for dashboard queries.

- `gold_artist_metrics` - KPIs, popularity tiers, hidden gems, career span
- `gold_genre_analysis` - Genre aggregations with artist counts & popularity
- `gold_track_enriched` - Complete track dataset (joins artists + audio features)
- `gold_audio_insights` - Energy levels, mood indicators (63 enriched tracks)

---

## 📈 Analytics Dashboard

### **5 Interactive Pages**:

1. **📊 Overview** - Key metrics, popularity tiers, release timeline
2. **👤 Artist Explorer** - Artist table with filters, hidden gems, scatter plots
3. **🎸 Genre Analysis** - Top genres, popularity by genre, Japanese representation
4. **🎼 Audio Features** - Tempo/danceability distributions, energy levels, key analysis
5. **📈 Insights** - Career longevity, prolific artists, market availability

### **Run the Dashboard**:
```bash
# From project root
streamlit run dashboard/app.py

# Dashboard opens at http://localhost:8501
```

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+
- Spotify Developer Account (free - [create here](https://developer.spotify.com/dashboard))
- Git installed

### **Setup Steps**

```bash
# 1. Clone repository
git clone https://github.com/pc1493/Japanese-Music-Analysis.git
cd Japanese-Music-Analysis

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up Spotify credentials
# Copy .env.example to .env and add your Client ID & Secret
# Get credentials from https://developer.spotify.com/dashboard

# 5. Test API connection
python test_spotify.py

# 6. Run the dashboard (uses existing data)
streamlit run dashboard/app.py
```

### **Re-run Data Pipeline** (Optional)

```bash
# Extract data from Spotify (2,266 tracks, 876 artists)
python scripts/extract_japanese_music.py

# Enrich with audio features (parallel, ~3.5 min)
python scripts/enrich_acousticbrainz_parallel.py

# Run dbt transformations (Silver + Gold layers)
cd japanese_music_dbt
dbt run --profiles-dir .

# View results
streamlit run ../dashboard/app.py
```

---

## 🎯 Key Insights Discovered

### **1. Artist Landscape**
- **533 Japanese artists** (61% of dataset) vs 343 non-Japanese
- **Popularity tiers**: 28% Mainstream (70+), 35% Mid-tier, 24% Emerging, 13% Niche
- **Hidden gems**: 12 artists with high follower/popularity ratio (undervalued)

### **2. Genre Trends**
- **Top genres**: j-pop, j-rock, anime, city pop, japanese r&b
- **Genre diversity**: Some artists have 10+ genre tags vs single-genre specialists
- **Japanese dominance**: 80%+ in j-pop, j-rock, city pop genres

### **3. Audio Characteristics** (63 enriched tracks)
- **Tempo range**: 80-180 BPM (average: ~110 BPM)
- **Danceability**: Medium to High (0.8-1.5 range)
- **Key preference**: Major keys slightly favored over minor
- **Energy levels**: Mix of high-energy dance tracks and slower ballads

### **4. Market Availability**
- **Global tracks**: 45% available in 100+ markets
- **Japan-specific**: 30% only available in select Asian markets
- **Popularity correlation**: Globally available tracks perform better

---

## 🔧 Technical Highlights

### **Performance Optimizations**
- **Parallel enrichment**: 34x faster (3.5 min vs 2 hours) using ThreadPoolExecutor
- **10 concurrent API requests** to MusicBrainz/AcousticBrainz
- **Thread-safe database writes** with lock mechanisms
- **Batch processing** (100 tracks per batch) for progress tracking

### **Data Quality**
- **Hybrid Japanese detection**: Name patterns (Unicode regex) + genre tags
- **ISRC→MBID lookup**: 2,096 mappings cached for future enrichment
- **2.8% match rate** for audio features (expected due to AcousticBrainz cutoff in 2022)
- **Idempotent pipeline**: Re-runnable without duplicates

### **dbt Best Practices**
- **Incremental models** ready for future updates
- **Modular SQL** with CTEs for readability
- **Type casting** for JSON → arrays, dates, booleans
- **Documentation** in schema.yml files

---

## 📚 Learning Outcomes

This project demonstrates:

✅ **Modern data stack** proficiency (DuckDB, dbt, Streamlit)
✅ **Medallion architecture** implementation (Bronze → Silver → Gold)
✅ **API integration** with rate limiting and parallel processing
✅ **Data quality** practices (idempotency, validation, testing)
✅ **SQL transformation** skills via dbt
✅ **Problem-solving** (API deprecation workarounds, performance optimization)
✅ **Documentation** and project organization for collaboration

---

## 🔄 Data Pipeline Flow

```
1. EXTRACT (Python)
   Spotify API → scripts/extract_japanese_music.py
   - Hybrid detection: Playlist search + genre-based fallback
   - 2,266 tracks from 16 curated playlists
   - Stores ISRC codes for enrichment
   ↓

2. ENRICH (Python - Parallel)
   MusicBrainz + AcousticBrainz → scripts/enrich_acousticbrainz_parallel.py
   - ISRC → MBID lookup (MusicBrainz)
   - MBID → Audio features (AcousticBrainz)
   - 10 concurrent workers, 3.5 min runtime
   - 63 tracks matched (2.8%)
   ↓

3. LOAD (Python)
   → DuckDB bronze tables (INSERT OR REPLACE)
   - bronze_artists, bronze_tracks, bronze_acousticbrainz_features
   - Full raw JSON stored for future analysis
   ↓

4. TRANSFORM (dbt)
   Bronze → Silver → Gold
   - Silver: Parse JSON, clean nulls, standardize types
   - Gold: Business logic, aggregations, joins
   - 7 models total, ~0.5 sec runtime
   ↓

5. VISUALIZE (Streamlit)
   Gold tables → Interactive dashboard
   - 5 pages: Overview, Artists, Genres, Audio, Insights
   - Plotly charts: bar, scatter, pie, histogram
   - Real-time filtering and exploration
```

---

## 📊 Sample Queries

```sql
-- Top 10 most popular Japanese artists
SELECT artist_name, artist_popularity, followers_total, track_count
FROM gold_artist_metrics
WHERE is_japanese = TRUE
ORDER BY artist_popularity DESC
LIMIT 10;

-- Genre breakdown with Japanese representation
SELECT genre, artist_count, avg_popularity, pct_japanese
FROM gold_genre_analysis
ORDER BY artist_count DESC
LIMIT 20;

-- Tracks with audio features (tempo > 140 BPM)
SELECT track_name, artist_name, tempo, danceability, energy_level
FROM gold_audio_insights
WHERE tempo > 140
ORDER BY tempo DESC;

-- Hidden gems (high followers, lower popularity)
SELECT artist_name, followers_total, artist_popularity,
       follower_popularity_ratio
FROM gold_artist_metrics
WHERE is_hidden_gem = TRUE
ORDER BY follower_popularity_ratio DESC;
```

---

## 🐛 Known Limitations

1. **Spotify Audio Features API deprecated** (Nov 27, 2024)
   - Alternative: AcousticBrainz (limited to pre-2022 tracks)
   - Only 63/2,266 tracks (2.8%) have audio features

2. **Genre tagging inconsistency**
   - Some artists lack genre tags entirely
   - Multi-genre artists may span 10+ genres

3. **ISRC availability**
   - 1 track missing ISRC out of 2,266
   - ISRC standard not universal before 2000s

4. **Market availability data**
   - Changes over time (licensing agreements)
   - Snapshot from extraction date only

---

## 🤝 Contributing

This is a portfolio project, but feedback is welcome!

- Report issues: [GitHub Issues](https://github.com/pc1493/Japanese-Music-Analysis/issues)
- Suggest features: Open a discussion
- Fork and extend: MIT License (see LICENSE)

---

## 📜 License & Attribution

**Code**: MIT License (see LICENSE file)
**Data Source**: Spotify Web API
**API Documentation**: https://developer.spotify.com/documentation/web-api
**AcousticBrainz**: https://acousticbrainz.org (archived project)

All data extracted via official APIs with proper authentication. No data redistribution.

---

## 🔗 Links

- **GitHub Repository**: https://github.com/pc1493/Japanese-Music-Analysis
- **Spotify Developer Dashboard**: https://developer.spotify.com/dashboard
- **DuckDB Docs**: https://duckdb.org/docs/
- **dbt Core Docs**: https://docs.getdbt.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

**Built with ❤️ as a data engineering learning project**
**Tech Stack**: Python • DuckDB • dbt • Streamlit • Plotly
**Powered by**: [Claude Code](https://claude.com/claude-code)
