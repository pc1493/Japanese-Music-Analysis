# Setup Guide - Japanese Music Analytics Project

## Prerequisites
- Python 3.10+ installed
- Git installed
- Spotify account (free tier is fine)
- Text editor or IDE (VS Code recommended)

## Step-by-Step Setup

### 1. Spotify Developer Account Setup

1. **Create a Spotify App**:
   - Go to https://developer.spotify.com/dashboard
   - Log in with your Spotify account
   - Click "Create an App"
   - Fill in:
     - App name: "Japanese Music Analytics"
     - App description: "Personal project analyzing Japanese music data"
     - Check the terms of service box
   - Click "Create"

2. **Get Your Credentials**:
   - On your app dashboard, you'll see:
     - **Client ID**: Copy this
     - **Client Secret**: Click "Show Client Secret" and copy it
   - Keep these safe - you'll need them in the next step

3. **Configure the Project**:
   ```bash
   # Copy the example env file
   cp config/.env.example .env

   # Edit .env file with your credentials
   # Replace 'your_client_id_here' with your actual Client ID
   # Replace 'your_client_secret_here' with your actual Client Secret
   ```

### 2. Virtual Environment (Already Done ✅)

The virtual environment is already set up. To activate it:

**Windows**:
```bash
venv\Scripts\activate
```

**Mac/Linux**:
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Verify Installation

Test that everything is installed correctly:

```bash
# Check Python packages
pip list

# Check dbt installation
cd japanese_music_dbt
dbt --version

# Test dbt connection to DuckDB
dbt debug --profiles-dir .
```

Expected output from `dbt debug`:
```
Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]

Required dependencies:
 - git [OK found]

Connection:
  database: main
  schema: main
  path: ../data/japanese_music.duckdb
  Connection test: [OK connection ok]
```

### 4. Test Spotify API Connection

Create a simple test script:

```python
# test_spotify.py
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Test search for a Japanese artist
results = sp.search(q='artist:YOASOBI', type='artist', limit=1)
if results['artists']['items']:
    artist = results['artists']['items'][0]
    print(f"✅ Successfully connected to Spotify API!")
    print(f"Test search found: {artist['name']}")
    print(f"Followers: {artist['followers']['total']:,}")
else:
    print("❌ No results found")
```

Run it:
```bash
python test_spotify.py
```

### 5. Understand the Project Structure

```
Your Project/
├── data/                   # Where your data will be stored
│   └── japanese_music.duckdb (will be created when you run dbt)
│
├── scripts/                # Python scripts for data extraction
│   └── (You'll create these next)
│
├── japanese_music_dbt/     # Your dbt project
│   ├── models/
│   │   ├── bronze/        # Raw data from API
│   │   ├── silver/        # Cleaned data
│   │   └── gold/          # Analytics-ready data
│   ├── profiles.yml       # Database connection config
│   └── dbt_project.yml    # dbt configuration
│
├── config/
│   └── .env               # Your Spotify credentials (DO NOT COMMIT)
│
└── requirements.txt       # All Python packages needed
```

## Common Issues & Solutions

### Issue: `dbt: command not found`
**Solution**: Make sure your virtual environment is activated
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Issue: `Spotify API 401 Unauthorized`
**Solution**:
1. Check your `.env` file has correct credentials
2. No extra spaces or quotes around credentials
3. Client Secret is visible (not hidden) when you copied it

### Issue: `ModuleNotFoundError: No module named 'spotipy'`
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt
```

### Issue: DuckDB file locked
**Solution**:
1. Close any other programs accessing the database
2. Close dbt docs if running
3. Restart your terminal

## What to Do Next

Now that setup is complete, you're ready to:

1. **Explore Spotify API**: Test different search queries to understand the data
2. **Plan your data extraction**: Decide which artists/genres to focus on
3. **Write extraction scripts**: Create Python scripts to fetch data
4. **Populate bronze layer**: Load raw data into DuckDB

See the main [README.md](../README.md) for the full project roadmap and timeline.

## Helpful Commands Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# dbt commands (run from japanese_music_dbt/ directory)
dbt run --profiles-dir .              # Run all models
dbt run --profiles-dir . --select bronze  # Run only bronze layer
dbt test --profiles-dir .             # Run all tests
dbt docs generate --profiles-dir .   # Generate documentation
dbt docs serve --profiles-dir .      # View documentation in browser

# Python scripts (run from project root)
python scripts/extract_artists.py    # Extract artist data
python scripts/load_to_bronze.py     # Load data to DuckDB
```

## Getting Help

- **Spotify API Documentation**: https://developer.spotify.com/documentation/web-api
- **dbt Documentation**: https://docs.getdbt.com/
- **DuckDB Documentation**: https://duckdb.org/docs/
- **Spotipy Documentation**: https://spotipy.readthedocs.io/

Happy analyzing! 🎵
