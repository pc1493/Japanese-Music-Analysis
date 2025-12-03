"""
Test script to verify Spotify API connection
Run this after setting up your .env file with Spotify credentials
"""
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

def test_spotify_connection():
    """Test connection to Spotify API"""
    print("🎵 Testing Spotify API Connection...\n")

    # Check if credentials are set
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not client_id or client_id == 'your_client_id_here':
        print("❌ SPOTIFY_CLIENT_ID not set in .env file")
        print("   Please copy config/.env.example to .env and add your credentials")
        return False

    if not client_secret or client_secret == 'your_client_secret_here':
        print("❌ SPOTIFY_CLIENT_SECRET not set in .env file")
        print("   Please copy config/.env.example to .env and add your credentials")
        return False

    try:
        # Set up Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Test search for a popular Japanese artist
        print("Testing with search for 'YOASOBI'...")
        results = sp.search(q='artist:YOASOBI', type='artist', limit=1)

        if results['artists']['items']:
            artist = results['artists']['items'][0]
            print(f"\n✅ Successfully connected to Spotify API!")
            print(f"\nTest Results:")
            print(f"  Artist: {artist['name']}")
            print(f"  Followers: {artist['followers']['total']:,}")
            print(f"  Popularity: {artist['popularity']}/100")
            print(f"  Genres: {', '.join(artist['genres']) if artist['genres'] else 'N/A'}")
            print(f"  Spotify ID: {artist['id']}")
            print(f"\n✨ Your Spotify API is working correctly!")
            return True
        else:
            print("❌ Search returned no results (unexpected)")
            return False

    except Exception as e:
        print(f"\n❌ Error connecting to Spotify API:")
        print(f"   {str(e)}")
        print("\nCommon issues:")
        print("  1. Check your Client ID and Client Secret are correct")
        print("  2. Make sure there are no extra spaces or quotes in .env file")
        print("  3. Verify your Spotify app is active at https://developer.spotify.com/dashboard")
        return False

if __name__ == "__main__":
    success = test_spotify_connection()

    if success:
        print("\n" + "="*60)
        print("Next steps:")
        print("  1. Start exploring Japanese artists and genres")
        print("  2. Run scripts to extract data from Spotify")
        print("  3. Load data into DuckDB bronze layer")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Setup instructions:")
        print("  1. Go to https://developer.spotify.com/dashboard")
        print("  2. Create an app (or use existing)")
        print("  3. Copy Client ID and Client Secret")
        print("  4. Copy config/.env.example to .env")
        print("  5. Paste your credentials into .env")
        print("  6. Run this script again")
        print("="*60)
