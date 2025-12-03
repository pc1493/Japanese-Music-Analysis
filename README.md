# Japanese Music Analytics Project

## Overview
A data engineering project analyzing Japanese music (J-Pop, J-Rock, anime soundtracks, City Pop) using Spotify data. Built with a medallion architecture to showcase data engineering and analytics skills.

## Project Goals
1. Answer interesting questions about Japanese music trends using real data
2. Build a production-ready medallion architecture (Bronze → Silver → Gold)
3. Create an interactive dashboard that tells a compelling data story
4. Demonstrate data engineering best practices for portfolio/employers

## Tech Stack (100% Free)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | Spotify Web API + Spotipy | Extract artist, track, and audio feature data |
| **Database** | DuckDB | Local analytical database (fast, SQL-based) |
| **Transformation** | dbt-core + dbt-duckdb | SQL-based data transformations |
| **Orchestration** | Python scripts | Data extraction and loading |
| **Dashboard** | Streamlit | Interactive visualizations and storytelling |
| **Version Control** | GitHub | Code repository and portfolio showcase |

## Key Questions to Answer

**Trend & Popularity Analysis:**
- How has J-Pop vs J-Rock popularity evolved over the last decade?
- Which Japanese artists are breaking into international markets?
- What audio features (tempo, energy, danceability) define successful Japanese tracks?
- Are there seasonal patterns in Japanese music releases?

**Audio DNA Analysis:**
- What's the "sound signature" of City Pop vs modern J-Pop?
- How do anime soundtrack artists compare to mainstream artists?
- Which artists have the most diverse sound across their discography?

**Discovery & Hidden Gems:**
- What are the high-quality tracks with low popularity?
- Which Japanese subgenres are growing fastest?
- Can we predict which indie artists might break out?

## Project Structure

```
japanese-music-analytics/
├── data/                          # DuckDB database and raw files
│   ├── bronze/                    # Raw data from API
│   ├── silver/                    # Cleaned data
│   ├── gold/                      # Analytics-ready data
│   └── japanese_music.duckdb      # DuckDB database
│
├── scripts/                       # Python extraction scripts
│   ├── extract_artists.py         # Fetch artist data from Spotify
│   ├── extract_tracks.py          # Fetch track data
│   ├── extract_audio_features.py  # Fetch audio features
│   └── load_to_bronze.py          # Load data into DuckDB
│
├── japanese_music_dbt/            # dbt project
│   ├── models/
│   │   ├── bronze/                # Raw data models
│   │   ├── silver/                # Cleaned data models
│   │   └── gold/                  # Analytics models
│   ├── tests/                     # Data quality tests
│   └── dbt_project.yml
│
├── dashboard/                     # Streamlit dashboard
│   ├── app.py                     # Main dashboard application
│   └── utils/                     # Helper functions
│
├── docs/                          # Documentation
│   └── architecture_diagram.png
│
├── config/                        # Configuration files
│   └── .env.example               # Spotify API credentials template
│
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md
```

## Medallion Architecture

### Bronze Layer (Raw Data)
- **Purpose**: Store raw data exactly as received from Spotify API
- **Characteristics**: Minimal transformation, full audit trail, JSON-like structure
- **Tables**:
  - `bronze_artists` - Raw artist metadata
  - `bronze_tracks` - Raw track information
  - `bronze_audio_features` - Raw audio feature data

### Silver Layer (Cleaned & Standardized)
- **Purpose**: Clean, deduplicate, and standardize data
- **Characteristics**: Type casting, null handling, standardized formats
- **Tables**:
  - `silver_artists` - Cleaned artist data
  - `silver_tracks` - Cleaned track data with proper typing
  - `silver_audio_features` - Validated audio features

### Gold Layer (Analytics-Ready)
- **Purpose**: Business logic applied, ready for visualization
- **Characteristics**: Aggregations, metrics, denormalized for performance
- **Tables**:
  - `gold_artist_popularity_trends` - Time-series popularity metrics
  - `gold_audio_feature_analysis` - Audio feature aggregations by genre
  - `gold_genre_trends` - Genre growth and patterns
  - `gold_hidden_gems` - Discovery recommendations

## Setup Instructions

### 1. Clone and Setup Environment

```bash
cd "Japanese Music Analysis"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Spotify API Credentials

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Copy Client ID and Client Secret
4. Create `.env` file:

```bash
cp config/.env.example .env
# Edit .env with your credentials
```

### 3. Run Data Extraction (Week 1)

```bash
# Extract data from Spotify API
python scripts/extract_artists.py
python scripts/extract_tracks.py
python scripts/extract_audio_features.py

# Load into DuckDB bronze layer
python scripts/load_to_bronze.py
```

### 4. Run dbt Transformations (Week 1-2)

```bash
cd japanese_music_dbt

# Test dbt connection
dbt debug --profiles-dir .

# Run bronze → silver → gold transformations
dbt run --profiles-dir .

# Run data quality tests
dbt test --profiles-dir .

# Generate documentation
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

### 5. Launch Dashboard (Week 2)

```bash
# From project root
streamlit run dashboard/app.py
```

## Development Workflow

1. **Extract**: Python scripts fetch data from Spotify API → Save to JSON
2. **Load**: Python scripts load JSON → DuckDB bronze tables
3. **Transform**: dbt models transform bronze → silver → gold
4. **Test**: dbt tests validate data quality at each layer
5. **Visualize**: Streamlit dashboard reads from gold layer

## 2-Week Timeline

### Week 1: Data Foundation
- **Day 1-2**: Setup, API exploration, finalize questions ✅
- **Day 3-4**: Bronze layer (raw data extraction and loading)
- **Day 5-7**: Silver layer (cleaning and standardization)

### Week 2: Analytics & Presentation
- **Day 8-10**: Gold layer (business logic and aggregations)
- **Day 11-12**: Streamlit dashboard development
- **Day 13-14**: Polish, deploy, documentation, demo video

## Current Status

✅ Project structure created
✅ Virtual environment setup
✅ Dependencies installed
✅ dbt project initialized with medallion architecture
⬜ Spotify API configuration
⬜ Data extraction scripts
⬜ Bronze layer population
⬜ Silver layer transformations
⬜ Gold layer analytics
⬜ Dashboard development

## Next Steps

1. Set up Spotify API credentials (`.env` file)
2. Write data extraction scripts
3. Test API connection and explore available data
4. Refine specific questions based on data availability

## Skills Demonstrated

- **Data Engineering**: Medallion architecture, data pipeline design
- **SQL & Transformations**: dbt models with testing
- **Python**: API integration, data extraction, automation
- **Data Modeling**: Dimensional modeling concepts
- **Data Quality**: Testing and validation at each layer
- **Visualization**: Interactive dashboard with Streamlit
- **Documentation**: Clear architecture and setup instructions

## License

MIT License - Feel free to use this project as a template for your own data engineering portfolio projects!

## Contact

Created for portfolio demonstration. Questions? Open an issue or reach out via LinkedIn.
