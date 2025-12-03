# Japanese Music Analytics - dbt Project

## Overview
This dbt project transforms raw Spotify API data about Japanese music into analytics-ready datasets using a medallion architecture (Bronze → Silver → Gold).

## Architecture

### Medallion Layers

**Bronze Layer** (`models/bronze/`)
- Raw data from Spotify API with minimal transformation
- Full audit trail (load timestamps, source info)
- Tables:
  - `bronze_artists` - Raw artist data
  - `bronze_tracks` - Raw track data
  - `bronze_audio_features` - Raw audio feature data

**Silver Layer** (`models/silver/`)
- Cleaned and standardized data
- Data quality rules applied
- Type casting and validation
- Tables:
  - `silver_artists` - Cleaned artist data
  - `silver_tracks` - Cleaned track data
  - `silver_audio_features` - Standardized audio features

**Gold Layer** (`models/gold/`)
- Business logic applied
- Aggregations and metrics
- Analytics-ready for dashboard
- Tables:
  - `gold_artist_popularity_trends` - Artist metrics over time
  - `gold_audio_feature_analysis` - Audio feature aggregations
  - `gold_genre_trends` - Genre growth patterns
  - `gold_hidden_gems` - Discovery metrics

## Setup

1. **Install dependencies** (from parent directory):
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure profile**:
   - Profile is pre-configured in `profiles.yml`
   - Database: DuckDB at `../data/japanese_music.duckdb`

3. **Test connection**:
   ```bash
   cd japanese_music_dbt
   dbt debug --profiles-dir .
   ```

## Usage

```bash
# Run all models
dbt run --profiles-dir .

# Run specific layer
dbt run --profiles-dir . --select bronze
dbt run --profiles-dir . --select silver
dbt run --profiles-dir . --select gold

# Run tests
dbt test --profiles-dir .

# Generate documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Data Sources
- Spotify Web API (via Python extraction scripts)
- Focus: Japanese music (J-Pop, J-Rock, anime soundtracks, City Pop)

## Tech Stack
- **Transformation**: dbt-core with dbt-duckdb adapter
- **Database**: DuckDB (local analytical database)
- **Source**: Spotify Web API via Spotipy

## Key Questions Answered
1. How has J-Pop vs J-Rock popularity evolved?
2. What audio features define successful Japanese tracks?
3. Which Japanese artists are breaking into international markets?
4. What are the "hidden gems" in Japanese music?

## Project Structure
```
japanese_music_dbt/
├── models/
│   ├── bronze/         # Raw data models
│   ├── silver/         # Cleaned data models
│   └── gold/           # Analytics models
├── tests/              # Custom data tests
├── macros/             # Reusable SQL macros
└── dbt_project.yml     # Project configuration
```
