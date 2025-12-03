# Project Status - Global Music Analytics

**Last Updated**: 2025-12-03
**Phase**: Week 1, Day 3 - Bronze Layer Development & API Learning ⚡

---

## ✅ Completed Tasks (Day 1-3)

### Day 1-2: Foundation & Setup
- [x] Created project structure with medallion architecture
- [x] Set up Python virtual environment with all dependencies
- [x] Configured dbt-core with DuckDB adapter
- [x] Created comprehensive documentation (README, SETUP_GUIDE)
- [x] Set up Git repository with proper .gitignore
- [x] Configured Spotify API credentials (.env)
- [x] Verified API connection with test script

### Day 3: Bronze Layer & API Discovery
- [x] **Built extraction script** (`scripts/extract_and_load_bronze.py`)
- [x] **Created DuckDB database** (`data/japanese_music.duckdb`)
- [x] **Populated bronze tables**:
  - `bronze_artists`: 37 artists loaded
  - `bronze_tracks`: 322 tracks loaded
  - `bronze_audio_features`: **0 records** (API deprecated Nov 27, 2024)
- [x] **Created SQL query tools**:
  - `query_bronze.py` - one-off queries
  - `sql_interactive.py` - interactive SQL session
  - `explore_data.ipynb` - Jupyter notebook
- [x] **Set up DBeaver** for visual database exploration
- [x] **Discovered Spotify API limitations**

---

## 🔍 Key Learnings from Day 3

### Critical Discovery: Audio Features API Deprecated ❌
**Problem**: Spotify deprecated the `/audio-features` endpoint on **November 27, 2024**
- Apps created before this date: Still have access
- Apps created after: **403 Forbidden** (our situation)
- **No official alternative** provided by Spotify

**Impact**: Cannot get audio characteristics (tempo, energy, danceability, acousticness, etc.)

**Resolution**: Pivoted project focus to metadata-based analysis instead of audio feature analysis

### Spotify API Rate Limits Discovered
**Rate Limiting**:
- Rolling **30-second window** (dynamic, not fixed per-second)
- Development mode: ~180 requests per 30 seconds (estimated)
- When exceeded: HTTP 429 with `Retry-After` header
- Extended quota mode: Higher limits (requires application)

**Search Endpoint Limits**:
- **50 results maximum** per request
- **2,000 total results maximum** via pagination (offset + limit ≤ 2000)
- Genre-based search is too restrictive (missed most artists)

### Better Extraction Strategy Identified
**Original approach** (too limited):
```python
# Only searched 5 genres × 10 artists = 37 unique artists
search_queries = ['genre:j-pop', 'genre:j-rock', 'genre:anime', 'city pop', 'japanese indie']
sp.search(q=query, type='artist', limit=10)  # Only 10! Should be 50
```

**New approach** (recommended):
```python
# Extract from Spotify's official curated playlists
# 50-100 playlists × 50 tracks each = 5,000-7,000 tracks
featured_playlists = sp.featured_playlists(limit=50)
regional_charts = sp.playlist('37i9dQZEVXbMDoHDwVN2tF')  # Global Top 50
```

**Benefits**:
- Actual listening data (not genre-filtered guesses)
- Global coverage (regional charts available)
- 5k-10k tracks in single 15-20 min extraction
- No genre tagging issues

---

## 🎯 Current Status: Redesigning Extraction Strategy

### What Works Now:
✅ DuckDB database operational (`data/japanese_music.duckdb`)
✅ Bronze table schemas created
✅ SQL query interface available (DBeaver + scripts)
✅ dbt project configured and ready
✅ Git repository active (https://github.com/pc1493/Japanese-Music-Analysis)

### What Needs Revision:
⚠️ **Extraction script needs rewrite** - Current approach too limited (37 artists)
⚠️ **Project scope pivoted** - "Japanese Music Analytics" → "Global Music Analytics"
⚠️ **Analysis questions need updating** - Cannot use audio features

---

## 📊 Revised Project Scope

### Original Plan:
- Focus: Japanese music only (J-Pop, J-Rock, City Pop, anime)
- Data: 50-100 artists, audio features analysis
- Questions: "What defines Japanese music sonically?"

### **New Plan (Global Music Analytics)**:
- **Focus**: Global music trends across regions and genres
- **Data**: 5,000-10,000 tracks from 1,500-2,500 artists worldwide
- **Source**: Spotify curated playlists + regional charts
- **Questions**:
  1. What are the most popular genres globally vs regionally?
  2. How does artist popularity correlate with follower counts?
  3. Which artists appear across multiple regional charts (global appeal)?
  4. What are the "hidden gems" (high engagement, low mainstream popularity)?
  5. How do release patterns differ by region/genre?

---

## 📋 Next Steps (Day 3-4 Continued)

### Immediate Priority:
1. **Rewrite extraction script** to use playlist-based approach
   - Target: 5,000-7,000 tracks
   - Extract from featured playlists + regional charts
   - Handle rate limiting gracefully
   - Estimated runtime: 15-20 minutes

2. **Re-populate bronze layer**
   - Clear existing limited data
   - Load new comprehensive dataset
   - Verify data quality

3. **Update documentation**
   - Revise README with new scope
   - Update analytics questions
   - Document API limitations discovered

4. **Push to GitHub**
   - Commit bronze layer work
   - Update project status
   - Tag milestone: "Day 3 - Bronze Layer Complete"

### After Bronze Layer Complete:
5. **Build Silver layer** (dbt transformations)
   - Clean and standardize artist data
   - Parse JSON fields (genres)
   - Create clean track dataset
   - Add data quality tests

6. **Build Gold layer** (analytics)
   - Artist popularity metrics
   - Genre trend analysis
   - Regional comparison tables
   - Hidden gems discovery

7. **Build Streamlit dashboard**
   - Interactive visualizations
   - Connect to Gold layer tables
   - Deploy locally, test with real data

---

## 🗂️ Current File Structure

```
Global Music Analysis/
├── ✅ README.md                         - Project overview
├── ✅ PROJECT_STATUS.md                 - This file (updated)
├── ✅ requirements.txt                  - Python dependencies
├── ✅ .gitignore                        - Git rules (protects .env)
├── ✅ .env                              - Spotify credentials (gitignored)
├── ✅ test_spotify.py                   - API connection test
├── ✅ open_duckdb.bat                   - Quick DuckDB CLI launcher
│
├── ✅ config/
│   └── ✅ .env.example                  - Template for credentials
│
├── ✅ data/
│   └── ✅ japanese_music.duckdb         - Database file (2.8 MB)
│       ├── bronze_artists (37 rows - TO REFRESH)
│       ├── bronze_tracks (322 rows - TO REFRESH)
│       └── bronze_audio_features (0 rows - deprecated)
│
├── ✅ docs/
│   └── ✅ SETUP_GUIDE.md                - Setup instructions
│
├── ✅ scripts/
│   ├── ✅ extract_and_load_bronze.py   - Extraction script (NEEDS REWRITE)
│   ├── ✅ query_bronze.py              - One-off SQL queries
│   ├── ✅ sql_interactive.py           - Interactive SQL session
│   └── ⬜ extract_from_playlists.py    - (TO BUILD - new approach)
│
├── ✅ japanese_music_dbt/               - dbt project
│   ├── ✅ dbt_project.yml               - dbt configuration
│   ├── ✅ profiles.yml                  - DuckDB connection
│   ├── ✅ README.md                     - dbt documentation
│   └── ✅ models/
│       ├── ✅ bronze/                   - Bronze models (schemas exist)
│       ├── ✅ silver/                   - Silver models (TO BUILD)
│       └── ✅ gold/                     - Gold models (TO BUILD)
│
├── ✅ explore_data.ipynb                - Jupyter exploration notebook
│
└── ⬜ dashboard/                        - Streamlit app (Week 2)
    └── app.py                          - (TO BUILD)
```

---

## 💡 Technical Architecture

### Database: DuckDB (Embedded Analytical DB)
- **Single file**: `data/japanese_music.duckdb` contains all data
- **No server**: Runs in-process, uses local CPU/RAM
- **Schemas**: Tables organized by naming convention:
  - `bronze_*` - Raw Spotify API data
  - `silver_*` - Cleaned, standardized data
  - `gold_*` - Analytics-ready aggregations

### Transformation: dbt-core
- **Manual execution**: `dbt run` triggered manually (no scheduler)
- **SQL-based**: Models written in SQL, compiled by dbt
- **Medallion layers**: Bronze → Silver → Gold pipeline
- **Testing**: Data quality tests built-in

### Extraction: Python + Spotipy
- **Direct to database**: API → DuckDB (no intermediate JSON files)
- **Rate limit aware**: Sleeps when hitting 429 errors
- **Idempotent**: Uses `INSERT OR REPLACE` to allow re-runs

### Visualization: Streamlit (Week 2)
- **Connects to Gold tables**: Queries DuckDB directly
- **Interactive dashboard**: User can filter/explore
- **Local deployment**: Runs on localhost for testing

---

## 📊 Week 1 Deliverables Checklist

- [x] **Day 1-2**: Setup & Foundation ✅
  - [x] Project structure created
  - [x] Virtual environment configured
  - [x] dbt initialized
  - [x] Documentation written
  - [x] Spotify API credentials configured
  - [x] Git repository set up

- [x] **Day 3**: Bronze Layer (In Progress) ⚡
  - [x] Spotify API credentials working
  - [x] Data exploration completed (discovered limitations)
  - [x] Initial extraction script written (needs improvement)
  - [ ] **Bronze layer populated with 5k-10k tracks** (NEXT TASK)
  - [ ] Data loaded and verified in DuckDB

- [ ] **Day 4-5**: Bronze Layer Completion
  - [ ] Rewrite extraction with playlist-based approach
  - [ ] Extract 5,000-10,000 tracks from global playlists
  - [ ] Verify data quality and completeness
  - [ ] Document data sources and extraction logic

- [ ] **Day 5-7**: Silver Layer
  - [ ] Write dbt silver models (cleaning/standardization)
  - [ ] Implement data quality tests
  - [ ] Run transformations and validate output
  - [ ] Document business rules

- [ ] **Day 8-10**: Gold Layer
  - [ ] Design analytics tables
  - [ ] Write dbt gold models (aggregations/metrics)
  - [ ] Create analysis views for dashboard
  - [ ] Test analytical queries

- [ ] **Day 11-14**: Dashboard & Documentation
  - [ ] Build Streamlit dashboard
  - [ ] Create visualizations
  - [ ] Generate dbt docs
  - [ ] Final README polish

---

## 🚀 How to Use This Project Right Now

### 1. Query the Database
**Option A: DBeaver GUI** (Recommended)
- Open DBeaver
- Connect to `data/japanese_music.duckdb`
- Browse tables visually, run queries in editor

**Option B: Interactive SQL Session**
```bash
venv\Scripts\activate
python scripts\sql_interactive.py
```

**Option C: DuckDB CLI**
```bash
duckdb data\japanese_music.duckdb
```

### 2. Re-run Extraction (Current Script)
```bash
venv\Scripts\activate
python scripts\extract_and_load_bronze.py
```
*Note: Will refresh existing 37 artists. New playlist-based script coming next.*

### 3. Test Spotify API
```bash
python test_spotify.py
```

---

## 🎓 What We Learned About Data Engineering

### 1. **API Discovery is Critical**
- Don't assume endpoints work - test first
- API limitations shape your entire project
- Have backup strategies when features deprecate

### 2. **Rate Limits Require Planning**
- Understand limits before designing extraction
- Batch requests where possible
- Build retry logic for production systems

### 3. **Data Volume Matters**
- 37 artists → No patterns visible
- 5,000 tracks → Real insights emerge
- Plan for meaningful sample sizes

### 4. **Scope Flexibility**
- "Japanese Music" → too narrow, hard to source
- "Global Music" → broader, easier data access
- Pivot when you hit roadblocks

### 5. **Medallion Architecture Works**
- Bronze: Store everything raw (no opinions yet)
- Silver: Clean once, use many times
- Gold: Purpose-built for specific questions

---

## 📝 Questions to Research Next

Before rebuilding extraction:
1. Which Spotify playlists should we target?
   - Global Top 50? Regional charts? Genre-specific?
2. How many playlists to extract? (50? 100?)
3. Should we prioritize recent data or historical diversity?
4. What metadata beyond tracks/artists do we want?
   - Album info? Release years? Market availability?

---

**Status**: Day 3 in progress | Bronze layer being revised | Ready to scale up data collection 🚀
