"""
Japanese Music Analytics Dashboard

A Streamlit dashboard visualizing Japanese music trends from Spotify data
using a medallion architecture (Bronze -> Silver -> Gold) with DuckDB and dbt.
"""

import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Japanese Music Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
DB_PATH = Path(__file__).parent.parent / "data" / "japanese_music.duckdb"

@st.cache_resource
def get_db_connection():
    """Create a cached DuckDB connection"""
    return duckdb.connect(str(DB_PATH), read_only=True)

@st.cache_data
def load_data(query):
    """Execute query and return DataFrame"""
    conn = get_db_connection()
    return conn.execute(query).df()

# Sidebar
st.sidebar.title("🎵 Japanese Music Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "👤 Artist Explorer", "🎸 Genre Analysis", "🎼 Audio Features", "📈 Insights"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    """
    This dashboard analyzes **Japanese music** from Spotify using:
    - **2,266 tracks** from 876 artists
    - **63 tracks** with audio features
    - **Medallion architecture**: Bronze → Silver → Gold
    - **Tech stack**: DuckDB + dbt + Streamlit
    """
)

# Main content
if page == "📊 Overview":
    st.title("📊 Japanese Music Overview")
    st.markdown("High-level statistics and trends across the dataset")

    # Load overview data
    overview_query = """
    SELECT
        COUNT(DISTINCT artist_id) as total_artists,
        COUNT(DISTINCT CASE WHEN is_japanese THEN artist_id END) as japanese_artists,
        COUNT(DISTINCT track_id) as total_tracks,
        COUNT(DISTINCT CASE WHEN has_audio_features THEN track_id END) as tracks_with_audio
    FROM main_gold.gold_track_enriched
    """
    overview = load_data(overview_query)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Artists", f"{overview['total_artists'][0]:,}")
    with col2:
        st.metric("Japanese Artists", f"{overview['japanese_artists'][0]:,}",
                 f"{overview['japanese_artists'][0]/overview['total_artists'][0]*100:.1f}%")
    with col3:
        st.metric("Total Tracks", f"{overview['total_tracks'][0]:,}")
    with col4:
        st.metric("Enriched Tracks", f"{overview['tracks_with_audio'][0]:,}",
                 f"{overview['tracks_with_audio'][0]/overview['total_tracks'][0]*100:.1f}%")

    st.markdown("---")

    # Popularity tier distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Artist Popularity Tiers")
        tier_query = """
        SELECT
            popularity_tier,
            COUNT(*) as artist_count
        FROM main_gold.gold_artist_metrics
        GROUP BY popularity_tier
        ORDER BY
            CASE popularity_tier
                WHEN 'Mainstream' THEN 1
                WHEN 'Mid-tier' THEN 2
                WHEN 'Emerging' THEN 3
                WHEN 'Niche' THEN 4
            END
        """
        tier_data = load_data(tier_query)

        fig = px.pie(tier_data, values='artist_count', names='popularity_tier',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Japanese vs Non-Japanese")
        jp_query = """
        SELECT
            CASE WHEN is_japanese THEN 'Japanese' ELSE 'Non-Japanese' END as category,
            COUNT(*) as count
        FROM main_gold.gold_artist_metrics
        GROUP BY is_japanese
        """
        jp_data = load_data(jp_query)

        fig = px.pie(jp_data, values='count', names='category',
                    color_discrete_map={'Japanese': '#FF6B6B', 'Non-Japanese': '#4ECDC4'})
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    # Release year distribution
    st.subheader("Track Releases Over Time")
    year_query = """
    SELECT
        release_year,
        COUNT(*) as track_count
    FROM main_gold.gold_track_enriched
    WHERE release_year IS NOT NULL AND release_year >= 1990
    GROUP BY release_year
    ORDER BY release_year
    """
    year_data = load_data(year_query)

    fig = px.bar(year_data, x='release_year', y='track_count',
                labels={'release_year': 'Year', 'track_count': 'Number of Tracks'},
                color='track_count', color_continuous_scale='Blues')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

elif page == "👤 Artist Explorer":
    st.title("👤 Artist Explorer")
    st.markdown("Explore artist metrics, hidden gems, and career insights")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        japanese_filter = st.selectbox("Artist Type", ["All", "Japanese Only", "Non-Japanese Only"])
    with col2:
        tier_filter = st.multiselect("Popularity Tier",
                                     ["Mainstream", "Mid-tier", "Emerging", "Niche"],
                                     default=["Mainstream", "Mid-tier", "Emerging", "Niche"])
    with col3:
        min_tracks = st.slider("Minimum Track Count", 0, 50, 0)

    # Build query
    where_clauses = []
    if japanese_filter == "Japanese Only":
        where_clauses.append("is_japanese = TRUE")
    elif japanese_filter == "Non-Japanese Only":
        where_clauses.append("is_japanese = FALSE")

    if tier_filter:
        tier_list = "', '".join(tier_filter)
        where_clauses.append(f"popularity_tier IN ('{tier_list}')")

    if min_tracks > 0:
        where_clauses.append(f"track_count >= {min_tracks}")

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    artists_query = f"""
    SELECT
        artist_name,
        artist_popularity as popularity,
        followers_total as followers,
        track_count as tracks,
        genre_count as genres,
        popularity_tier as tier,
        CASE WHEN is_hidden_gem THEN 'Yes' ELSE 'No' END as hidden_gem,
        ROUND(follower_popularity_ratio, 0) as follower_pop_ratio,
        career_span_years as career_span
    FROM main_gold.gold_artist_metrics
    WHERE {where_clause}
    ORDER BY artist_popularity DESC
    LIMIT 100
    """
    artists_df = load_data(artists_query)

    # Top artists table
    st.subheader(f"Top Artists ({len(artists_df)} shown)")
    st.dataframe(
        artists_df,
        column_config={
            "artist_name": "Artist",
            "popularity": st.column_config.ProgressColumn("Popularity", format="%d", min_value=0, max_value=100),
            "followers": st.column_config.NumberColumn("Followers", format="%d"),
            "tracks": st.column_config.NumberColumn("Tracks", format="%d"),
            "genres": st.column_config.NumberColumn("Genres", format="%d"),
            "tier": "Tier",
            "hidden_gem": "Hidden Gem",
            "follower_pop_ratio": st.column_config.NumberColumn("F/P Ratio", format="%.0f"),
            "career_span": st.column_config.NumberColumn("Career (years)", format="%d"),
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # Hidden gems
    st.subheader("💎 Hidden Gems (High Followers, Lower Popularity)")
    gems_query = """
    SELECT
        artist_name,
        artist_popularity as popularity,
        followers_total as followers,
        track_count as tracks,
        ROUND(follower_popularity_ratio, 0) as ratio
    FROM main_gold.gold_artist_metrics
    WHERE is_hidden_gem = TRUE
    ORDER BY follower_popularity_ratio DESC
    LIMIT 10
    """
    gems_df = load_data(gems_query)

    if len(gems_df) > 0:
        st.dataframe(gems_df, hide_index=True, use_container_width=True)
    else:
        st.info("No hidden gems found with current filters")

    # Scatter plot
    st.subheader("Artist Popularity vs Followers")
    scatter_query = """
    SELECT
        artist_name,
        artist_popularity,
        followers_total,
        popularity_tier,
        track_count
    FROM main_gold.gold_artist_metrics
    WHERE track_count > 0
    """
    scatter_df = load_data(scatter_query)

    fig = px.scatter(scatter_df,
                    x='artist_popularity',
                    y='followers_total',
                    color='popularity_tier',
                    size='track_count',
                    hover_data=['artist_name'],
                    labels={'artist_popularity': 'Popularity Score',
                           'followers_total': 'Followers',
                           'popularity_tier': 'Tier'},
                    color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_yaxes(type="log")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🎸 Genre Analysis":
    st.title("🎸 Genre Analysis")
    st.markdown("Explore genre trends, popularity, and Japanese representation")

    # Top genres
    st.subheader("Top Genres by Artist Count")
    genre_query = """
    SELECT
        genre,
        artist_count,
        ROUND(avg_popularity, 1) as avg_popularity,
        japanese_artist_count,
        ROUND(pct_japanese, 1) as pct_japanese
    FROM main_gold.gold_genre_analysis
    ORDER BY artist_count DESC
    LIMIT 20
    """
    genre_df = load_data(genre_query)

    fig = px.bar(genre_df, x='artist_count', y='genre', orientation='h',
                color='avg_popularity',
                labels={'artist_count': 'Number of Artists', 'genre': 'Genre', 'avg_popularity': 'Avg Popularity'},
                color_continuous_scale='Viridis')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Genre details table
    st.subheader("Genre Statistics")
    st.dataframe(
        genre_df,
        column_config={
            "genre": "Genre",
            "artist_count": st.column_config.NumberColumn("Artists", format="%d"),
            "avg_popularity": st.column_config.ProgressColumn("Avg Popularity", format="%.1f", min_value=0, max_value=100),
            "japanese_artist_count": st.column_config.NumberColumn("Japanese Artists", format="%d"),
            "pct_japanese": st.column_config.ProgressColumn("% Japanese", format="%.1f%%", min_value=0, max_value=100),
        },
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # Japanese representation by genre
    st.subheader("Japanese Artist Representation by Genre")
    jp_genre_df = genre_df.nlargest(15, 'artist_count')

    fig = px.bar(jp_genre_df, x='genre', y=['japanese_artist_count', 'artist_count'],
                labels={'value': 'Artist Count', 'genre': 'Genre'},
                barmode='group',
                color_discrete_map={'japanese_artist_count': '#FF6B6B', 'artist_count': '#4ECDC4'})
    fig.update_layout(legend_title_text='Type')
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🎼 Audio Features":
    st.title("🎼 Audio Features Analysis")
    st.markdown(f"Deep dive into the **63 tracks** with AcousticBrainz audio features")

    # Load audio insights
    audio_query = """
    SELECT
        track_name,
        artist_name,
        track_popularity,
        tempo,
        tempo_category,
        danceability,
        danceability_category,
        key_key,
        key_scale,
        energy_level,
        mood_indicator,
        loudness_mean,
        dynamic_complexity
    FROM main_gold.gold_audio_insights
    """
    audio_df = load_data(audio_query)

    if len(audio_df) == 0:
        st.warning("No audio features available")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Avg Tempo", f"{audio_df['tempo'].mean():.0f} BPM")
        with col2:
            st.metric("Avg Danceability", f"{audio_df['danceability'].mean():.2f}")
        with col3:
            most_common_key = audio_df['key_key'].mode()[0] if len(audio_df['key_key']) > 0 else 'N/A'
            st.metric("Most Common Key", most_common_key)
        with col4:
            major_pct = (audio_df['key_scale'] == 'major').sum() / len(audio_df) * 100
            st.metric("Major Key %", f"{major_pct:.0f}%")

        st.markdown("---")

        # Tempo distribution
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Tempo Distribution")
            fig = px.histogram(audio_df, x='tempo', nbins=20,
                             labels={'tempo': 'Tempo (BPM)', 'count': 'Track Count'},
                             color_discrete_sequence=['#FF6B6B'])
            st.plotly_chart(fig, use_container_width=True)

            # Tempo categories
            tempo_cat = audio_df['tempo_category'].value_counts().reset_index()
            tempo_cat.columns = ['category', 'count']
            fig = px.pie(tempo_cat, values='count', names='category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Danceability Distribution")
            fig = px.histogram(audio_df, x='danceability', nbins=20,
                             labels={'danceability': 'Danceability', 'count': 'Track Count'},
                             color_discrete_sequence=['#4ECDC4'])
            st.plotly_chart(fig, use_container_width=True)

            # Danceability categories
            dance_cat = audio_df['danceability_category'].value_counts().reset_index()
            dance_cat.columns = ['category', 'count']
            fig = px.pie(dance_cat, values='count', names='category', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Energy and mood
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Energy Levels")
            energy = audio_df['energy_level'].value_counts().reset_index()
            energy.columns = ['level', 'count']
            fig = px.bar(energy, x='level', y='count',
                        color='level',
                        labels={'level': 'Energy Level', 'count': 'Track Count'},
                        color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Mood (Key Scale)")
            mood = audio_df['mood_indicator'].value_counts().reset_index()
            mood.columns = ['mood', 'count']
            fig = px.bar(mood, x='mood', y='count',
                        color='mood',
                        labels={'mood': 'Mood', 'count': 'Track Count'},
                        color_discrete_map={'Major (Upbeat)': '#FFD93D', 'Minor (Melancholic)': '#6C63FF'})
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Tempo vs Danceability scatter
        st.subheader("Tempo vs Danceability")
        fig = px.scatter(audio_df, x='tempo', y='danceability',
                        color='energy_level',
                        size='track_popularity',
                        hover_data=['track_name', 'artist_name'],
                        labels={'tempo': 'Tempo (BPM)', 'danceability': 'Danceability'},
                        color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

        # Track list
        st.subheader("Enriched Tracks")
        st.dataframe(
            audio_df[['track_name', 'artist_name', 'tempo', 'danceability', 'key_key', 'key_scale', 'energy_level']],
            column_config={
                "track_name": "Track",
                "artist_name": "Artist",
                "tempo": st.column_config.NumberColumn("Tempo (BPM)", format="%.0f"),
                "danceability": st.column_config.NumberColumn("Danceability", format="%.2f"),
                "key_key": "Key",
                "key_scale": "Scale",
                "energy_level": "Energy"
            },
            hide_index=True,
            use_container_width=True
        )

elif page == "📈 Insights":
    st.title("📈 Key Insights")
    st.markdown("Interesting patterns and discoveries from the data")

    # Career longevity
    st.subheader("🏆 Longest Careers")
    career_query = """
    SELECT
        artist_name,
        first_release_year,
        latest_release_year,
        career_span_years,
        track_count
    FROM main_gold.gold_artist_metrics
    WHERE career_span_years IS NOT NULL AND career_span_years > 1
    ORDER BY career_span_years DESC
    LIMIT 10
    """
    career_df = load_data(career_query)

    fig = px.bar(career_df, x='career_span_years', y='artist_name', orientation='h',
                color='track_count',
                labels={'career_span_years': 'Career Span (Years)', 'artist_name': 'Artist'},
                color_continuous_scale='Greens')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Most prolific artists
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📀 Most Prolific Artists")
        prolific_query = """
        SELECT
            artist_name,
            track_count,
            album_count,
            artist_popularity
        FROM main_gold.gold_artist_metrics
        ORDER BY track_count DESC
        LIMIT 10
        """
        prolific_df = load_data(prolific_query)
        st.dataframe(prolific_df, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("🌟 Genre Specialists")
        specialist_query = """
        SELECT
            artist_name,
            genre_count,
            artist_popularity,
            track_count
        FROM main_gold.gold_artist_metrics
        WHERE genre_count = 1 AND track_count >= 3
        ORDER BY artist_popularity DESC
        LIMIT 10
        """
        specialist_df = load_data(specialist_query)
        st.dataframe(specialist_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Market availability
    st.subheader("🌍 Global vs Regional Tracks")
    market_query = """
    SELECT
        CASE
            WHEN globally_available THEN 'Global (100+ markets)'
            WHEN available_in_japan THEN 'Japan Available'
            ELSE 'Limited Availability'
        END as availability,
        COUNT(*) as track_count,
        ROUND(AVG(track_popularity), 1) as avg_popularity
    FROM main_gold.gold_track_enriched
    GROUP BY
        CASE
            WHEN globally_available THEN 'Global (100+ markets)'
            WHEN available_in_japan THEN 'Japan Available'
            ELSE 'Limited Availability'
        END
    """
    market_df = load_data(market_query)

    fig = px.bar(market_df, x='availability', y='track_count',
                color='avg_popularity',
                labels={'availability': 'Market Availability', 'track_count': 'Track Count', 'avg_popularity': 'Avg Popularity'},
                text='track_count',
                color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

    # Explicit vs clean
    st.subheader("🎤 Explicit vs Clean Content")
    explicit_query = """
    SELECT
        CASE WHEN explicit THEN 'Explicit' ELSE 'Clean' END as content_type,
        COUNT(*) as track_count,
        ROUND(AVG(track_popularity), 1) as avg_popularity
    FROM main_gold.gold_track_enriched
    GROUP BY explicit
    """
    explicit_df = load_data(explicit_query)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(explicit_df, values='track_count', names='content_type',
                    color_discrete_map={'Explicit': '#E63946', 'Clean': '#06FFA5'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(explicit_df, hide_index=True, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### Tech Stack")
st.sidebar.code("Python | DuckDB | dbt | Streamlit", language="text")
st.sidebar.markdown("Built with [Claude Code](https://claude.com/claude-code)")
