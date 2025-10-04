"""
=============================================================================
GEO ANALYTICS DASHBOARD - STREAMLIT APPLICATION
Step 13: Interactive Regional Distribution & Demand Analysis Dashboard
=============================================================================

Features:
- Interactive map visualizations with filtering
- Regional performance metrics and KPIs
- Demand pattern analysis with drill-down
- Market penetration insights
- Expansion planning recommendations
- Export capabilities for reports

Usage:
    streamlit run geo_dashboard.py

Author: Gym Analytics Team
Date: October 2025
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import base64
from io import BytesIO
import os
from pathlib import Path

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Geo Analytics Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 10px;
        border-bottom: 3px solid #ff7f0e;
    }
    h2 {
        color: #2c3e50;
        margin-top: 20px;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

# Resolve project paths robustly
# This file lives at: <repo>/phase4_data/dashboards/geo_analytics/geo_dashboard.py
# So parents[2] points to <repo>/phase4_data
PHASE4_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PHASE4_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed_datasets"

@st.cache_data
def load_processed_data():
    """Load all processed data from Colab analysis"""
    try:
        # Build file paths
        processed_paths = {
            'member_distribution': PROCESSED_DIR / 'processed_member_distribution.csv',
            'demand_analysis': PROCESSED_DIR / 'processed_demand_analysis.csv',
            'accessibility': PROCESSED_DIR / 'processed_accessibility_metrics.csv',
            'market_penetration': PROCESSED_DIR / 'processed_market_penetration.csv',
            'expansion_recommendations': PROCESSED_DIR / 'expansion_recommendations.csv',
            'summary_json': PROCESSED_DIR / 'geo_analytics_summary.json',
        }

        base_paths = {
            'member_geo': DATA_DIR / 'member_geo_data.csv',
            'facilities': DATA_DIR / 'facility_locations_data.csv',
            'market_data': DATA_DIR / 'market_analysis_data.csv',
        }

        # Read CSVs
        data = {}
        data['member_distribution'] = pd.read_csv(processed_paths['member_distribution'])
        data['demand_analysis'] = pd.read_csv(processed_paths['demand_analysis'])
        data['accessibility'] = pd.read_csv(processed_paths['accessibility'])
        data['market_penetration'] = pd.read_csv(processed_paths['market_penetration'])
        data['expansion_recommendations'] = pd.read_csv(processed_paths['expansion_recommendations'])
        data['member_geo'] = pd.read_csv(base_paths['member_geo'])
        data['facilities'] = pd.read_csv(base_paths['facilities'])
        data['market_data'] = pd.read_csv(base_paths['market_data'])
        
        with open(processed_paths['summary_json'], 'r', encoding='utf-8') as f:
            data['summary'] = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please run the Google Colab analysis notebook first to generate processed data files.")
        return None

@st.cache_data
def load_html_map(filename):
    """Load HTML map file"""
    try:
        # Resolve against processed directory if not absolute
        fpath = Path(filename)
        if not fpath.is_absolute():
            fpath = PROCESSED_DIR / fpath

        if fpath.exists():
            with open(fpath, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        st.warning(f"Could not load map: {filename}")
        return None

def display_html_map(html_content, height=600):
    """Display HTML map in Streamlit using components"""
    if html_content:
        st.components.v1.html(html_content, height=height, scrolling=True)
    else:
        st.info("📝 Map file not found. Please run the Google Colab notebook first to generate interactive maps.")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_download_link(df, filename, link_text):
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.0f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.1f}%"

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_member_distribution_map(member_df, facility_df):
    """Create interactive member distribution map"""
    center_lat = member_df['latitude'].mean()
    center_lng = member_df['longitude'].mean()
    
    fig = go.Figure()
    
    # Add member scatter
    fig.add_trace(go.Scattermapbox(
        lat=member_df['latitude'],
        lon=member_df['longitude'],
        mode='markers',
        marker=dict(
            size=8,
            color=member_df['membership_tier'].map({'premium': 'gold', 'standard': 'blue', 'basic': 'gray'}),
            opacity=0.7
        ),
        text=member_df.apply(lambda x: f"Member {x['member_id']}<br>Tier: {x['membership_tier']}<br>Distance: {x['distance_to_gym_km']:.1f}km", axis=1),
        name='Members'
    ))
    
    # Add facilities
    fig.add_trace(go.Scattermapbox(
        lat=facility_df['latitude'],
        lon=facility_df['longitude'],
        mode='markers',
        marker=dict(
            size=20,
            color='red',
            symbol='star'
        ),
        text=facility_df.apply(lambda x: f"<b>{x['facility_name']}</b><br>Capacity: {x['capacity']}<br>Members: {x['current_members']}", axis=1),
        name='Facilities'
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lng),
            zoom=11
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True
    )
    
    return fig

def create_demand_heatmap(demand_df):
    """Create demand intensity heatmap"""
    fig = px.bar(
        demand_df.sort_values('demand_intensity', ascending=False).head(15),
        x='zip_code',
        y='demand_intensity',
        color='demand_intensity',
        color_continuous_scale='Reds',
        title='Demand Intensity by Zip Code (Top 15)',
        labels={'demand_intensity': 'Demand Score', 'zip_code': 'Zip Code'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

def create_accessibility_analysis(accessibility_df):
    """Create accessibility metrics visualization"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Distance to Gym', 'Average Travel Time'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Distance chart
    fig.add_trace(
        go.Bar(
            x=accessibility_df['zip_code'],
            y=accessibility_df['distance_to_gym_km_mean'],
            name='Distance (km)',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # Travel time chart
    fig.add_trace(
        go.Bar(
            x=accessibility_df['zip_code'],
            y=accessibility_df['travel_time_minutes_mean'],
            name='Time (min)',
            marker_color='lightcoral'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig

def create_market_penetration_chart(penetration_df):
    """Create market penetration visualization"""
    top_penetration = penetration_df.nlargest(10, 'penetration_rate')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_penetration['zip_code'].astype(str),
        y=top_penetration['penetration_rate'],
        name='Penetration Rate',
        marker_color='steelblue',
        text=top_penetration['penetration_rate'].round(2),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Market Penetration Rate by Zip Code (per 1000 population)',
        xaxis_title='Zip Code',
        yaxis_title='Members per 1000 Population',
        height=400,
        showlegend=False
    )
    
    return fig

def create_expansion_priority_map(expansion_df, member_df):
    """Create expansion opportunities visualization"""
    # Get top 10 expansion opportunities
    top_expansion = expansion_df.nlargest(10, 'expansion_score')
    
    # Get approximate coordinates from member data or use defaults
    coords_map = member_df.groupby('zip_code').agg({
        'latitude': 'mean',
        'longitude': 'mean'
    }).to_dict()
    
    top_expansion['lat'] = top_expansion['zip_code'].map(coords_map.get('latitude', {}))
    top_expansion['lng'] = top_expansion['zip_code'].map(coords_map.get('longitude', {}))
    
    # Fill missing coordinates
    top_expansion['lat'].fillna(member_df['latitude'].mean(), inplace=True)
    top_expansion['lng'].fillna(member_df['longitude'].mean(), inplace=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=top_expansion['lat'],
        lon=top_expansion['lng'],
        mode='markers+text',
        marker=dict(
            size=top_expansion['expansion_score'] / 5,
            color=top_expansion['expansion_score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Expansion<br>Score")
        ),
        text=top_expansion['zip_code'].astype(str),
        textposition='top center',
        customdata=top_expansion[['zip_code', 'population', 'expansion_score', 'expansion_priority']],
        hovertemplate='<b>Zip: %{customdata[0]}</b><br>' +
                      'Population: %{customdata[1]:,}<br>' +
                      'Score: %{customdata[2]:.1f}<br>' +
                      'Priority: %{customdata[3]}<extra></extra>'
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=top_expansion['lat'].mean(), lon=top_expansion['lng'].mean()),
            zoom=10
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        title='Top 10 Expansion Opportunities'
    )
    
    return fig

def create_competitor_analysis(market_df):
    """Create competitor density analysis"""
    fig = px.scatter(
        market_df,
        x='population',
        y='competitor_density',
        size='fitness_interest_score',
        color='expansion_priority',
        hover_data=['zip_code', 'median_income'],
        title='Market Landscape: Population vs Competitor Density',
        labels={
            'population': 'Population',
            'competitor_density': 'Competitor Density',
            'expansion_priority': 'Priority'
        },
        color_discrete_map={'high': 'red', 'medium': 'orange', 'low': 'green'}
    )
    
    fig.update_layout(height=500)
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.title("🗺️ Geo Analytics Dashboard")
    st.markdown("### Regional Distribution & Demand Analysis")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading geo analytics data..."):
        data = load_processed_data()
    
    if data is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters & Options")
    
    # Facility filter
    facilities_list = ['All'] + data['facilities']['facility_name'].tolist()
    selected_facility = st.sidebar.selectbox("Select Facility", facilities_list)
    
    # Membership tier filter
    tier_list = ['All'] + data['member_geo']['membership_tier'].unique().tolist()
    selected_tier = st.sidebar.selectbox("Select Membership Tier", tier_list)
    
    # Priority filter
    priority_list = ['All'] + data['market_penetration']['expansion_priority'].unique().tolist()
    selected_priority = st.sidebar.selectbox("Expansion Priority", priority_list)
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Last Updated: {data['summary']['analysis_date']}")
    
    # Apply filters
    filtered_members = data['member_geo'].copy()
    if selected_facility != 'All':
        filtered_members = filtered_members[filtered_members['preferred_facility'] == selected_facility]
    if selected_tier != 'All':
        filtered_members = filtered_members[filtered_members['membership_tier'] == selected_tier]
    
    # ========================================================================
    # TAB NAVIGATION
    # ========================================================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🗺️ Member Distribution",
        "🔥 Demand Analysis",
        "🚦 Accessibility",
        "🎯 Market Penetration",
        "🚀 Expansion Planning"
    ])
    
    # ========================================================================
    # TAB 1: OVERVIEW
    # ========================================================================
    
    with tab1:
        st.header("Executive Summary")
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Members",
                f"{data['summary']['total_members']:,}",
                help="Total active gym members"
            )
        
        with col2:
            st.metric(
                "Facilities",
                data['summary']['total_facilities'],
                help="Number of gym locations"
            )
        
        with col3:
            st.metric(
                "Avg Distance",
                f"{data['summary']['avg_distance_km']:.2f} km",
                help="Average distance to gym"
            )
        
        with col4:
            st.metric(
                "Avg Travel Time",
                f"{data['summary']['avg_travel_time']:.1f} min",
                help="Average travel time to gym"
            )
        
        with col5:
            st.metric(
                "Coverage Area",
                f"{data['summary']['unique_zip_codes']} zips",
                help="Number of zip codes served"
            )
        
        st.markdown("---")
        
        # Quick insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Key Insights")
            
            utilization = data['summary']['avg_utilization'] * 100
            if utilization > 85:
                st.markdown(f"""
                <div class="warning-box">
                <b>⚠️ High Facility Utilization</b><br>
                Average utilization at {utilization:.1f}% - consider capacity expansion
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                <b>✅ Healthy Facility Utilization</b><br>
                Average utilization at {utilization:.1f}%
                </div>
                """, unsafe_allow_html=True)
            
            underserved_pct = (data['summary']['underserved_members'] / data['summary']['total_members']) * 100
            st.markdown(f"""
            <div class="insight-box">
            <b>🚨 Underserved Members:</b> {data['summary']['underserved_members']} ({underserved_pct:.1f}%)<br>
            Members with high travel time/distance who may benefit from new facilities
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="success-box">
            <b>🎯 Top Expansion Target:</b> Zip {data['summary']['top_expansion_zip']}<br>
            Highest potential for new facility based on market analysis
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🏆 Performance Highlights")
            
            # Top performing facility
            top_facility = data['facilities'].nlargest(1, 'utilization_rate').iloc[0]
            st.markdown(f"""
            <div class="insight-box">
            <b>🏢 Best Performing Facility:</b> {top_facility['facility_name']}<br>
            Utilization: {top_facility['utilization_rate']*100:.1f}% | Market Share: {top_facility['market_share']*100:.1f}%
            </div>
            """, unsafe_allow_html=True)
            
            # Member tier distribution
            tier_counts = data['member_geo']['membership_tier'].value_counts()
            premium_pct = (tier_counts.get('premium', 0) / len(data['member_geo'])) * 100
            st.markdown(f"""
            <div class="insight-box">
            <b>💎 Premium Members:</b> {tier_counts.get('premium', 0)} ({premium_pct:.1f}%)<br>
            Strong premium membership base
            </div>
            """, unsafe_allow_html=True)
            
            # High frequency users
            high_freq = (data['member_geo']['visit_frequency'] == 'high').sum()
            high_freq_pct = (high_freq / len(data['member_geo'])) * 100
            st.markdown(f"""
            <div class="success-box">
            <b>🔥 High-Frequency Users:</b> {high_freq} ({high_freq_pct:.1f}%)<br>
            Members visiting regularly (high engagement)
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Geographic distribution overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📍 Member Distribution by Tier")
            tier_dist = data['member_geo']['membership_tier'].value_counts().reset_index()
            tier_dist.columns = ['Tier', 'Count']
            
            fig = px.pie(
                tier_dist,
                values='Count',
                names='Tier',
                color='Tier',
                color_discrete_map={'premium': 'gold', 'standard': 'silver', 'basic': 'lightgray'},
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🚗 Transportation Mode Distribution")
            transport_dist = data['member_geo']['transportation_mode'].value_counts().reset_index()
            transport_dist.columns = ['Mode', 'Count']
            
            fig = px.bar(
                transport_dist,
                x='Mode',
                y='Count',
                color='Mode',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 2: MEMBER DISTRIBUTION
    # ========================================================================
    
    with tab2:
        st.header("Member Distribution Mapping")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Interactive Member Map")
            fig = create_member_distribution_map(filtered_members, data['facilities'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Display Folium map if available
            st.markdown("### 📌 Detailed Folium Map")
            map_html = load_html_map('member_distribution_map.html')
            display_html_map(map_html, height=600)
        
        with col2:
            st.markdown("### 📊 Distribution Statistics")
            
            zip_stats = filtered_members.groupby('zip_code').agg({
                'member_id': 'count',
                'distance_to_gym_km': 'mean',
                'travel_time_minutes': 'mean'
            }).rename(columns={'member_id': 'Members'}).round(2)
            
            zip_stats = zip_stats.sort_values('Members', ascending=False)
            
            st.dataframe(
                zip_stats.style.background_gradient(subset=['Members'], cmap='Blues'),
                height=400
            )
            
            st.markdown("### 🎯 Top Zip Codes")
            top_5 = zip_stats.head(5)
            for idx, (zip_code, row) in enumerate(top_5.iterrows(), 1):
                st.markdown(f"""
                **#{idx}. Zip {zip_code}**  
                Members: {row['Members']:.0f} | Avg Distance: {row['distance_to_gym_km']:.1f}km
                """)
            
            # Download button
            st.markdown("---")
            st.markdown(create_download_link(
                data['member_distribution'],
                'member_distribution.csv',
                '📥 Download Distribution Data'
            ), unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 3: DEMAND ANALYSIS
    # ========================================================================
    
    with tab3:
        st.header("Demand Pattern Analysis")
        
        # Demand intensity heatmap
        st.markdown("### 🔥 Demand Intensity by Region")
        fig = create_demand_heatmap(data['demand_analysis'])
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Visit Frequency Distribution")
            freq_data = filtered_members['visit_frequency'].value_counts().reset_index()
            freq_data.columns = ['Frequency', 'Count']
            
            fig = px.funnel(
                freq_data,
                x='Count',
                y='Frequency',
                color='Frequency',
                color_discrete_map={'high': 'darkgreen', 'medium': 'orange', 'low': 'lightcoral'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Tier Performance by Demand")
            tier_demand = filtered_members.groupby('membership_tier').agg({
                'member_id': 'count',
                'visit_frequency': lambda x: (x == 'high').sum()
            }).rename(columns={'member_id': 'Total', 'visit_frequency': 'High Frequency'})
            
            tier_demand['Engagement Rate %'] = (tier_demand['High Frequency'] / tier_demand['Total'] * 100).round(1)
            
            st.dataframe(
                tier_demand.style.background_gradient(subset=['Engagement Rate %'], cmap='RdYlGn'),
                height=200
            )
            
            st.markdown("### 🎯 Demand Insights")
            top_demand_zip = data['demand_analysis'].nlargest(1, 'demand_intensity').iloc[0]
            st.info(f"""
            **Highest Demand:** Zip {top_demand_zip['zip_code']}  
            Demand Score: {top_demand_zip['demand_intensity']:.1f}  
            Premium Ratio: {top_demand_zip['premium_ratio']*100:.1f}%
            """)
        
        # Demand table
        st.markdown("### 📊 Detailed Demand Analysis")
        display_demand = data['demand_analysis'].sort_values('demand_intensity', ascending=False)
        display_demand['demand_intensity'] = display_demand['demand_intensity'].round(2)
        display_demand['high_freq_ratio'] = (display_demand['high_freq_ratio'] * 100).round(1)
        display_demand['premium_ratio'] = (display_demand['premium_ratio'] * 100).round(1)
        
        st.dataframe(
            display_demand.style.background_gradient(subset=['demand_intensity'], cmap='Reds'),
            height=300
        )
        
        st.markdown(create_download_link(
            data['demand_analysis'],
            'demand_analysis.csv',
            '📥 Download Demand Data'
        ), unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 4: ACCESSIBILITY ANALYSIS
    # ========================================================================
    
    with tab4:
        st.header("Accessibility & Travel Analysis")
        
        # Accessibility metrics
        st.markdown("### 🚦 Accessibility Metrics by Zip Code")
        fig = create_accessibility_analysis(data['accessibility'])
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📏 Distance Distribution")
            fig = px.histogram(
                filtered_members,
                x='distance_to_gym_km',
                nbins=20,
                color='membership_tier',
                title='Member Distance to Gym Distribution',
                labels={'distance_to_gym_km': 'Distance (km)', 'count': 'Members'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ Travel Time Distribution")
            fig = px.histogram(
                filtered_members,
                x='travel_time_minutes',
                nbins=20,
                color='membership_tier',
                title='Member Travel Time Distribution',
                labels={'travel_time_minutes': 'Travel Time (min)', 'count': 'Members'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Underserved analysis
        st.markdown("### 🚨 Underserved Areas")
        
        distance_threshold = filtered_members['distance_to_gym_km'].quantile(0.75)
        time_threshold = filtered_members['travel_time_minutes'].quantile(0.75)
        
        underserved = filtered_members[
            (filtered_members['distance_to_gym_km'] > distance_threshold) |
            (filtered_members['travel_time_minutes'] > time_threshold)
        ]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Underserved Members", len(underserved))
        with col2:
            st.metric("Distance Threshold", f"{distance_threshold:.2f} km")
        with col3:
            st.metric("Time Threshold", f"{time_threshold:.1f} min")
        
        if len(underserved) > 0:
            underserved_zips = underserved['zip_code'].value_counts().head(10).reset_index()
            underserved_zips.columns = ['Zip Code', 'Underserved Members']
            
            fig = px.bar(
                underserved_zips,
                x='Zip Code',
                y='Underserved Members',
                color='Underserved Members',
                color_continuous_scale='Reds',
                title='Top 10 Underserved Zip Codes'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Accessibility map
        st.markdown("### 🗺️ Accessibility Map")
        map_html = load_html_map('accessibility_analysis_map.html')
        display_html_map(map_html, height=600)
        
        st.markdown(create_download_link(
            data['accessibility'],
            'accessibility_metrics.csv',
            '📥 Download Accessibility Data'
        ), unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 5: MARKET PENETRATION
    # ========================================================================
    
    with tab5:
        st.header("Market Penetration Analysis")
        
        # Penetration chart
        st.markdown("### 🎯 Current Market Penetration")
        fig = create_market_penetration_chart(data['market_penetration'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Competitor analysis
        st.markdown("### ⚔️ Competitive Landscape")
        fig = create_competitor_analysis(data['market_data'])
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Penetration Metrics")
            
            penetration_summary = data['market_penetration'].agg({
                'population': 'sum',
                'current_members': 'sum',
                'penetration_rate': 'mean',
                'current_share_pct': 'mean'
            })
            
            st.metric("Total Addressable Market", f"{penetration_summary['population']:,.0f}")
            st.metric("Current Members", f"{penetration_summary['current_members']:.0f}")
            st.metric("Avg Penetration Rate", f"{penetration_summary['penetration_rate']:.2f} per 1K")
            st.metric("Avg Market Share", f"{penetration_summary['current_share_pct']:.1f}%")
        
        with col2:
            st.markdown("### 🏆 Top Penetrated Markets")
            
            top_penetration = data['market_penetration'].nlargest(5, 'penetration_rate')[
                ['zip_code', 'current_members', 'penetration_rate']
            ]
            
            for idx, row in top_penetration.iterrows():
                st.markdown(f"""
                **Zip {row['zip_code']}**  
                Members: {row['current_members']:.0f} | Rate: {row['penetration_rate']:.2f}/1K
                """)
        
        # Opportunity analysis
        st.markdown("### 💎 Untapped Opportunities")
        
        low_penetration = data['market_penetration'][
            (data['market_penetration']['current_members'] == 0) & 
            (data['market_penetration']['fitness_interest_score'] > 0.75)
        ].sort_values('opportunity_score', ascending=False).head(10)
        
        if len(low_penetration) > 0:
            st.dataframe(
                low_penetration[['zip_code', 'population', 'median_income', 'fitness_interest_score', 
                                 'competitor_density', 'opportunity_score', 'expansion_priority']].style.background_gradient(
                    subset=['opportunity_score'], cmap='YlGn'
                ),
                height=300
            )
        else:
            st.success("All high-potential markets have been penetrated!")
        
        st.markdown(create_download_link(
            data['market_penetration'],
            'market_penetration.csv',
            '📥 Download Penetration Data'
        ), unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 6: EXPANSION PLANNING
    # ========================================================================
    
    with tab6:
        st.header("Strategic Expansion Planning")
        
        # Filter expansion recommendations
        filtered_expansion = data['expansion_recommendations'].copy()
        if selected_priority != 'All':
            filtered_expansion = filtered_expansion[
                filtered_expansion['expansion_priority'] == selected_priority.lower()
            ]
        
        # Key expansion metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Expansion Candidates",
                len(filtered_expansion),
                help="Number of recommended expansion locations"
            )
        
        with col2:
            total_pop = filtered_expansion['population'].sum()
            st.metric(
                "Total Market Size",
                f"{total_pop:,.0f}",
                help="Combined population of expansion areas"
            )
        
        with col3:
            avg_income = filtered_expansion['median_income'].mean()
            st.metric(
                "Avg Income",
                format_currency(avg_income),
                help="Average median income in expansion areas"
            )
        
        with col4:
            avg_fitness = filtered_expansion['fitness_interest_score'].mean()
            st.metric(
                "Avg Fitness Score",
                f"{avg_fitness:.2f}",
                help="Average fitness interest score"
            )
        
        st.markdown("---")
        
        # Expansion opportunity map
        st.markdown("### 🗺️ Expansion Opportunity Map")
        fig = create_expansion_priority_map(filtered_expansion, data['member_geo'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Display Folium map
        st.markdown("### 📌 Detailed Expansion Map")
        map_html = load_html_map('expansion_opportunities_map.html')
        display_html_map(map_html, height=600)
        
        # Top recommendations
        st.markdown("### 🎯 Top 10 Expansion Recommendations")
        
        top_10 = filtered_expansion.nlargest(10, 'expansion_score')
        
        for idx, row in top_10.iterrows():
            with st.expander(f"#{idx+1} - Zip Code {row['zip_code']} (Score: {row['expansion_score']:.1f})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📍 Location Details**")
                    st.write(f"City: {row['city']}, {row['state']}")
                    st.write(f"Population: {row['population']:,}")
                    st.write(f"Median Income: {format_currency(row['median_income'])}")
                    st.write(f"Age 18-35: {row['age_18_35_pct']*100:.1f}%")
                
                with col2:
                    st.markdown("**📊 Market Analysis**")
                    st.write(f"Fitness Interest: {row['fitness_interest_score']:.2f}")
                    st.write(f"Competitor Density: {row['competitor_density']:.2f}")
                    st.write(f"Market Potential: {row['market_potential']}")
                    st.write(f"Priority: {row['expansion_priority'].upper()}")
                
                with col3:
                    st.markdown("**💰 Financial Projections**")
                    
                    # Estimate potential members
                    potential_members = row['population'] * row['fitness_interest_score'] * 0.02
                    st.write(f"Potential Members: {potential_members:.0f}")
                    
                    # Revenue estimate
                    avg_revenue_per_member = 600  # Annual
                    estimated_revenue = potential_members * avg_revenue_per_member
                    st.write(f"Est. Annual Revenue: {format_currency(estimated_revenue)}")
                    
                    # ROI calculation
                    facility_cost = 500000
                    roi_years = facility_cost / estimated_revenue if estimated_revenue > 0 else 999
                    st.write(f"Payback Period: {roi_years:.1f} years")
                    
                    # Market share estimate
                    market_share_est = (potential_members / (row['population'] * 0.1)) * 100
                    st.write(f"Est. Market Share: {market_share_est:.1f}%")
        
        # Detailed expansion table
        st.markdown("### 📊 Detailed Expansion Analysis")
        
        display_expansion = filtered_expansion.sort_values('expansion_score', ascending=False)
        
        # Format columns for display
        display_cols = display_expansion[[
            'zip_code', 'city', 'state', 'population', 'median_income', 
            'fitness_interest_score', 'competitor_density', 'expansion_score', 
            'expansion_priority'
        ]].copy()
        
        display_cols['median_income'] = display_cols['median_income'].apply(lambda x: f"${x:,.0f}")
        display_cols['fitness_interest_score'] = display_cols['fitness_interest_score'].round(2)
        display_cols['competitor_density'] = display_cols['competitor_density'].round(2)
        display_cols['expansion_score'] = display_cols['expansion_score'].round(1)
        
        st.dataframe(
            display_cols.style.background_gradient(subset=['expansion_score'], cmap='RdYlGn'),
            height=400
        )
        
        # Strategic recommendations
        st.markdown("### 💡 Strategic Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="success-box">
            <h4>🚀 Immediate Actions (0-3 months)</h4>
            <ul>
                <li>Conduct site surveys for top 3 expansion locations</li>
                <li>Launch targeted marketing in high-priority zip codes</li>
                <li>Analyze facility capacity constraints</li>
                <li>Develop partnership opportunities with local businesses</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>📅 Short-Term (3-6 months)</h4>
            <ul>
                <li>Secure real estate in top expansion location</li>
                <li>Begin facility design and permitting process</li>
                <li>Implement shuttle service for underserved areas</li>
                <li>Launch pre-opening membership drive</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
            <h4>🎯 Medium-Term (6-12 months)</h4>
            <ul>
                <li>Open first new facility location</li>
                <li>Expand capacity at high-utilization facilities</li>
                <li>Evaluate performance of new location</li>
                <li>Plan second-phase expansion based on results</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
            <h4>📈 Long-Term (12+ months)</h4>
            <ul>
                <li>Roll out multi-location expansion strategy</li>
                <li>Optimize facility network for maximum coverage</li>
                <li>Develop franchise or partnership model</li>
                <li>Establish market leadership in key regions</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Priority breakdown
        st.markdown("### 🎯 Expansion Priority Breakdown")
        
        priority_summary = filtered_expansion.groupby('expansion_priority').agg({
            'zip_code': 'count',
            'population': 'sum',
            'expansion_score': 'mean',
            'fitness_interest_score': 'mean',
            'median_income': 'mean'
        }).round(2)
        
        priority_summary.columns = ['Count', 'Total Population', 'Avg Score', 'Avg Fitness Interest', 'Avg Income']
        
        st.dataframe(
            priority_summary.style.background_gradient(subset=['Avg Score'], cmap='RdYlGn'),
            height=150
        )
        
        # Download expansion recommendations
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(create_download_link(
                data['expansion_recommendations'],
                'expansion_recommendations.csv',
                '📥 Download Full Expansion Report'
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_download_link(
                top_10,
                'top_10_expansion_opportunities.csv',
                '📥 Download Top 10 Opportunities'
            ), unsafe_allow_html=True)
        
        with col3:
            # Create executive summary
            executive_summary = pd.DataFrame({
                'Metric': [
                    'Total Expansion Candidates',
                    'High Priority Locations',
                    'Total Addressable Population',
                    'Average Expansion Score',
                    'Estimated New Members (Year 1)',
                    'Estimated Revenue Potential',
                    'Recommended Investment'
                ],
                'Value': [
                    len(filtered_expansion),
                    len(filtered_expansion[filtered_expansion['expansion_priority'] == 'high']),
                    f"{filtered_expansion['population'].sum():,}",
                    f"{filtered_expansion['expansion_score'].mean():.1f}",
                    f"{(filtered_expansion['population'].sum() * filtered_expansion['fitness_interest_score'].mean() * 0.02):.0f}",
                    format_currency(filtered_expansion['population'].sum() * filtered_expansion['fitness_interest_score'].mean() * 0.02 * 600),
                    format_currency(len(filtered_expansion[filtered_expansion['expansion_priority'] == 'high']) * 500000)
                ]
            })
            
            st.markdown(create_download_link(
                executive_summary,
                'expansion_executive_summary.csv',
                '📥 Download Executive Summary'
            ), unsafe_allow_html=True)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p><b>Geo Analytics Dashboard</b> | Step 13: Regional Distribution & Demand Analysis</p>
        <p>For questions or support, contact the Analytics Team</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()