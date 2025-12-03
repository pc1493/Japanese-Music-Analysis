# Global Music Analytics Project

## Overview
A data engineering portfolio project analyzing global music trends using Spotify data. Built with medallion architecture (Bronze → Silver → Gold) using DuckDB, dbt, and Streamlit to showcase modern data stack proficiency.

**Project Type**: Portfolio / Learning Project
**Timeline**: 2 weeks
**Status**: Week 1, Day 3 - Bronze Layer Development

## Project Goals
1. **Extract and analyze** 5,000-10,000 tracks from global Spotify playlists
2. **Build production-ready** medallion architecture with proper data quality checks
3. **Create interactive dashboard** with meaningful insights about music trends
4. **Demonstrate data engineering** best practices for portfolio/employers

## Tech Stack (100% Free & Local)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | Spotify Web API + Spotipy | Extract artist and track metadata |
| **Database** | DuckDB | Local embedded analytical database |
| **Transformation** | dbt-core + dbt-duckdb | SQL-based data transformations |
| **Orchestration** | Python scripts (manual) | Data extraction and loading |
| **Visualization** | Streamlit + Plotly | Interactive dashboard |
| **Database GUI** | DBeaver Community | Visual database exploration |
| **Version Control** | GitHub | Code repository and portfolio showcase |

All tools run **100% locally** on your machine. No cloud services, no costs.

---

## Key Analytics Questions

### Popularity & Trends
- What are the most popular genres globally vs. regionally?
- How does artist popularity correlate with follower counts?
- Which artists appear across multiple regional charts (global appeal)?
- How do release patterns differ by region and genre?

### Discovery & Hidden Gems
- What tracks have high engagement but low mainstream popularity?
- Which genres are growing fastest in different regions?
- Can we identify artists breaking into multiple markets?

### Metadata Analysis
- What's the distribution of explicit vs. clean content by genre?
- How do album types (single, album, compilation) affect popularity?
- What release date precision patterns exist (day/month/year)?

---

## Project Structure

```
global-music-analytics/
├── data/
│   └── japanese_music.duckdb      # DuckDB database (2.8 MB currently)
│       ├── bronze_artists         # Raw artist data (37 rows → scaling to 2,500)
│       ├── bronze_tracks          # Raw track data (322 rows → scaling to 10,000)
│       └── bronze_audio_features  # (0 rows - API deprecated Nov 2024)
│
├── scripts/                       # Python extraction scripts
│   ├── extract_and_load_bronze.py # Current: Genre-based search (limited)
│   ├── extract_from_playlists.py  # Next: Playlist-based extraction (TBD)
│   ├── query_bronze.py            # One-off SQL queries via CLI
│   └── sql_interactive.py         # Interactive SQL session
│
├── japanese_music_dbt/            # dbt project
│   ├── models/
│   │   ├── bronze/                # Raw data schemas (exists)
│   │   ├── silver/                # Cleaned data models (to build)
│   │   └── gold/                  # Analytics models (to build)
│   ├── profiles.yml               # DuckDB connection config
│   └── dbt_project.yml            # dbt configuration
│
├── dashboard/                     # Streamlit dashboard (Week 2)
│   └── app.py                     # (To build)
│
├── docs/
│   ├── SETUP_GUIDE.md             # Step-by-step setup instructions
│   └── PROJECT_STATUS.md          # Detailed progress tracking
│
├── config/
│   └── .env.example               # Spotify API credentials template
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Protects .env and sensitive files
├── .env                           # Spotify credentials (gitignored)
├── test_spotify.py                # API connection test
├── explore_data.ipynb             # Jupyter notebook for exploration
└── README.md                      # This file
```

---

## Medallion Architecture

### Bronze Layer (Raw Data)
**Purpose**: Store raw data exactly as received from Spotify API
**Status**: ✅ Tables created, initial data loaded (needs scaling)

**Tables**:
- `bronze_artists` - Artist metadata (ID, name, genres, popularity, followers, URLs)
- `bronze_tracks` - Track information (ID, name, artist, album, release date, popularity, duration)
- `bronze_audio_features` - *Empty* (API deprecated Nov 27, 2024 - 403 errors)

**Characteristics**:
- No transformations, store raw JSON
- Full audit trail with `loaded_at` timestamps
- Uses `INSERT OR REPLACE` for idempotency

### Silver Layer (Cleaned & Standardized)
**Purpose**: Clean, deduplicate, and standardize data
**Status**: ⬜ To be built with dbt

**Planned Tables**:
- `silver_artists` - Cleaned artist data with parsed genres array
- `silver_tracks` - Standardized tracks with proper date typing

**Transformations**:
- Parse JSON fields (genres) into arrays
- Handle null values with business rules
- Cast types properly (dates, integers)
- Remove duplicates
- Data quality tests (not null, unique, accepted values)

### Gold Layer (Analytics-Ready)
**Purpose**: Business logic applied, aggregations for dashboard
**Status**: ⬜ To be built with dbt

**Planned Tables**:
- `gold_artist_popularity_metrics` - Aggregated artist stats
- `gold_genre_trends` - Genre popularity by region
- `gold_hidden_gems` - High-quality, low-popularity tracks
- `gold_regional_charts` - Cross-regional artist presence

---

## Data Pipeline Flow

```
1. EXTRACT (Python)
   Spotify API → scripts/extract_from_playlists.py
   ↓

2. LOAD (Python)
   → DuckDB bronze tables (INSERT OR REPLACE)
   ↓

3. TRANSFORM (dbt)
   Bronze → Silver → Gold
   ↓

4. VISUALIZE (Streamlit)
   Gold tables → Interactive dashboard
```

**Manual Orchestration**: Each step triggered manually via command line (no scheduler)

---

## How to Use This Project

### Prerequisites
- Python 3.10+
- Spotify Developer Account (free)
- Git installed
- DBeaver (optional, for visual database access)

### Setup Instructions

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed setup steps.

**Quick Start**:
```bash
# 1. Clone repository
git clone https://github.com/pc1493/Japanese-Music-Analysis.git
cd Japanese-Music-Analysis

# 2. Activate virtual environment (already set up)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Set up Spotify credentials
# Copy .env.example to .env and add your API keys from
# https://developer.spotify.com/dashboard

# 4. Test Spotify connection
python test_spotify.py

# 5. Extract data (current script - limited to 37 artists)
python scripts/extract_and_load_bronze.py

# 6. Query the database
python scripts/sql_interactive.py
# Or open DBeaver and connect to data/japanese_music.duckdb
```

### Running dbt Transformations (After Silver/Gold models built)
```bash
cd japanese_music_dbt

# Run all models
dbt run --profiles-dir .

# Run specific layer
dbt run --profiles-dir . --select silver
dbt run --profiles-dir . --select gold

# Run tests
dbt test --profiles-dir .

# Generate documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

---

## Current Status & Learnings (Day 3)

### ✅ What's Working
- DuckDB database operational with bronze tables
- Spotify API connected and authenticated
- SQL query tools available (DBeaver, interactive Python session)
- dbt project configured and ready
- Git repository active with proper .gitignore

### ⚠️ Blockers Discovered
1. **Audio Features API Deprecated** (Nov 27, 2024)
   - Cannot get tempo, energy, danceability, etc.
   - 403 Forbidden for apps created after cutoff
   - No official alternative provided by Spotify
   - **Resolution**: Pivot to metadata-based analysis

2. **Genre-Based Search Too Limited**
   - Only returned 37 unique artists
   - Many artists lack genre tags
   - Max 50 results per search, 2,000 total via pagination
   - **Resolution**: Switch to playlist-based extraction

### 📊 API Limits Learned
- **Rate Limit**: ~180 requests per 30 seconds (rolling window)
- **Search Results**: Max 50 per request, 2,000 total with pagination
- **Playlist Tracks**: 50-100 tracks per curated playlist
- **Estimation**: 5,000-10,000 tracks = 15-20 min extraction time

### 🔄 Next Steps
1. Rewrite extraction script using playlist-based approach
2. Extract 5,000-10,000 tracks from Spotify's curated/regional playlists
3. Build dbt Silver layer for data cleaning
4. Build dbt Gold layer for analytics
5. Create Streamlit dashboard

---

## Learning Outcomes

This project demonstrates:
- **Modern data stack** proficiency (DuckDB, dbt, Python)
- **Medallion architecture** implementation
- **API integration** with rate limiting and error handling
- **Data quality** practices (tests, validation, idempotency)
- **SQL transformation** skills via dbt
- **Problem-solving** (pivoting when APIs deprecate, finding alternative strategies)
- **Documentation** and project organization for team collaboration

---

## Data Sources & Attribution

**Data Source**: Spotify Web API
**License**: Data used for educational/portfolio purposes only
**API Documentation**: https://developer.spotify.com/documentation/web-api

All data is extracted via official Spotify API with proper authentication. No data is redistributed or stored publicly.

---

## Repository
GitHub: https://github.com/pc1493/Japanese-Music-Analysis

---

## References & Resources

**Spotify API**:
- [Rate Limits Documentation](https://developer.spotify.com/documentation/web-api/concepts/rate-limits)
- [Search Endpoint Reference](https://developer.spotify.com/documentation/web-api/reference/search)
- [Recommendations API](https://developer.spotify.com/documentation/web-api/reference/get-recommendations)

**Tools**:
- [DuckDB Documentation](https://duckdb.org/docs/)
- [dbt-core Documentation](https://docs.getdbt.com/)
- [DBeaver DuckDB Setup](https://duckdb.org/docs/stable/guides/sql_editors/dbeaver)
- [Spotipy Library](https://spotipy.readthedocs.io/)

---

**Built with ❤️ as a data engineering learning project**
