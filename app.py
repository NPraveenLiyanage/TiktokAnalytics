import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title=" TikTok Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #ff0050, #00f2ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the TikTok data"""
    try:
        df = pd.read_csv('tiktokdata.csv')
        
        # Convert createTime to datetime if it's a timestamp
        if 'createTime' in df.columns:
            df['createTime'] = pd.to_datetime(df['createTime'], unit='s', errors='coerce')
        
        # Extract hashtags from description
        def extract_hashtags(text):
            if pd.isna(text):
                return []
            hashtags = re.findall(r'#(\w+)', str(text))
            return hashtags
        
        df['hashtags'] = df['desc'].apply(extract_hashtags)
        df['hashtag_count'] = df['hashtags'].apply(len)
        
        # Calculate engagement rate
        df['engagement_rate'] = (df['stats_diggCount'] + df['stats_commentCount'] + df['stats_shareCount']) / df['stats_playCount'].replace(0, 1) * 100
        
        # Create performance categories
        def categorize_performance(row):
            if row['stats_playCount'] > df['stats_playCount'].quantile(0.75):
                return 'High Performance'
            elif row['stats_playCount'] > df['stats_playCount'].quantile(0.25):
                return 'Medium Performance'
            else:
                return 'Low Performance'
        
        df['performance_category'] = df.apply(categorize_performance, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def create_kpi_metrics(df):
    """Create KPI metrics section"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_videos = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Videos</h4>
            <h4>{total_videos:,}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_plays = df['stats_playCount'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h4>Avg Views</h4>
            <h4>{avg_plays:,.0f}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_engagement = df['engagement_rate'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h4>Avg Engagement</h4>
            <h4>{avg_engagement:.1f}%</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_likes = df['stats_diggCount'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Likes</h4>
            <h4>{total_likes:,}</h4>
        </div>
        """, unsafe_allow_html=True)

def create_performance_overview(df):
    """Create performance overview charts"""
    st.subheader("🎯 Performance Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance distribution pie chart
        perf_counts = df['performance_category'].value_counts()
        fig_pie = px.pie(
            values=perf_counts.values,
            names=perf_counts.index,
            title="Content Performance Distribution",
            color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1'],
            hole=0.4
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Engagement vs Views scatter plot
        fig_scatter = px.scatter(
            df,
            x='stats_playCount',
            y='engagement_rate',
            size='stats_diggCount',
            color='performance_category',
            hover_data=['author_nickname', 'hashtag_count'],
            title="Engagement Rate vs Views",
            color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1'],
            log_x=True
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def create_engagement_analysis(df):
    """Create engagement analysis charts"""
    st.subheader("💬 Engagement Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Engagement metrics comparison
        engagement_data = df[['stats_diggCount', 'stats_commentCount', 'stats_shareCount']].mean()
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=['Likes', 'Comments', 'Shares'],
                y=engagement_data.values,
                marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1'],
                text=[f'{val:,.0f}' for val in engagement_data.values],
                textposition='auto'
            )
        ])
        fig_bar.update_layout(
            title="Average Engagement Metrics",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Top performing content
        top_videos = df.nlargest(10, 'stats_playCount')[['author_nickname', 'stats_playCount', 'engagement_rate']]
        
        fig_top = px.bar(
            top_videos,
            x='stats_playCount',
            y='author_nickname',
            color='engagement_rate',
            orientation='h',
            title="Top 10 Videos by Views",
            color_continuous_scale='viridis'
        )
        fig_top.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_top, use_container_width=True)

def create_hashtag_analysis(df, hashtag_filter):
    """Create hashtag analysis"""
    st.subheader("🏷️ Hashtag Performance Analysis")
    
    # Filter by hashtag if provided
    if hashtag_filter:
        mask = df['desc'].str.contains(hashtag_filter, case=False, na=False)
        filtered_df = df[mask]
        
        if len(filtered_df) > 0:
            st.markdown(f"""
            <div class="insight-box">
                <h3>📊 Results for #{hashtag_filter}</h3>
                <p><strong>Videos found:</strong> {len(filtered_df)}</p>
                <p><strong>Average views:</strong> {filtered_df['stats_playCount'].mean():,.0f}</p>
                <p><strong>Average engagement:</strong> {filtered_df['engagement_rate'].mean():.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show filtered results
            col1, col2 = st.columns(2)
            
            with col1:
                fig_filtered_views = px.histogram(
                    filtered_df,
                    x='stats_playCount',
                    title=f'View Distribution for #{hashtag_filter}',
                    nbins=20,
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_filtered_views.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_filtered_views, use_container_width=True)
            
            with col2:
                fig_filtered_eng = px.box(
                    filtered_df,
                    y='engagement_rate',
                    title=f'Engagement Rate for #{hashtag_filter}',
                    color_discrete_sequence=['#4ecdc4']
                )
                fig_filtered_eng.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_filtered_eng, use_container_width=True)
        else:
            st.warning(f"No videos found with hashtag #{hashtag_filter}")
    
    # Overall hashtag analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Hashtag count vs performance
        fig_hashtag_perf = px.scatter(
            df,
            x='hashtag_count',
            y='stats_playCount',
            size='engagement_rate',
            color='performance_category',
            title="Hashtag Count vs Performance",
            color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1'],
            log_y=True
        )
        fig_hashtag_perf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_hashtag_perf, use_container_width=True)
    
    with col2:
        # Optimal hashtag count analysis
        hashtag_performance = df.groupby('hashtag_count').agg({
            'stats_playCount': 'mean',
            'engagement_rate': 'mean',
            'author_nickname': 'count'
        }).reset_index()
        hashtag_performance = hashtag_performance[hashtag_performance['author_nickname'] >= 5]  # Filter for statistical significance
        
        fig_optimal = px.line(
            hashtag_performance,
            x='hashtag_count',
            y='stats_playCount',
            title="Optimal Hashtag Count Analysis",
            markers=True,
            line_shape='spline'
        )
        fig_optimal.update_traces(line_color='#45b7d1', marker_color='#ff6b6b')
        fig_optimal.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_optimal, use_container_width=True)

def create_author_insights(df):
    """Create author performance insights"""
    st.subheader("👥 Creator Performance Insights")
    
    # Top creators by different metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        top_creators_views = df.groupby('author_nickname')['stats_playCount'].sum().nlargest(10)
        # Create DataFrame for proper plotting
        creators_views_df = pd.DataFrame({
            'author': top_creators_views.index,
            'total_views': top_creators_views.values
        })
        
        fig_creators_views = px.bar(
            creators_views_df,
            x='total_views',
            y='author',
            orientation='h',
            title="Top Creators by Total Views",
            color='total_views',
            color_continuous_scale='plasma'
        )
        fig_creators_views.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_creators_views, use_container_width=True)
    
    with col2:
        top_creators_engagement = df.groupby('author_nickname')['engagement_rate'].mean().nlargest(10)
        # Create DataFrame for proper plotting
        creators_eng_df = pd.DataFrame({
            'author': top_creators_engagement.index,
            'avg_engagement': top_creators_engagement.values
        })
        
        fig_creators_eng = px.bar(
            creators_eng_df,
            x='avg_engagement',
            y='author',
            orientation='h',
            title="Top Creators by Avg Engagement",
            color='avg_engagement',
            color_continuous_scale='viridis'
        )
        fig_creators_eng.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_creators_eng, use_container_width=True)
    
    with col3:
        creator_consistency = df.groupby('author_nickname').agg({
            'stats_playCount': ['mean', 'std'],
            'engagement_rate': 'mean'
        }).reset_index()
        creator_consistency.columns = ['author_nickname', 'avg_views', 'std_views', 'avg_engagement']
        creator_consistency['consistency_score'] = creator_consistency['avg_views'] / (creator_consistency['std_views'] + 1)
        top_consistent = creator_consistency.nlargest(10, 'consistency_score')
        
        fig_consistency = px.bar(
            top_consistent,
            x='consistency_score',
            y='author_nickname',
            orientation='h',
            title="Most Consistent Creators",
            color='avg_engagement',
            color_continuous_scale='cividis'
        )
        fig_consistency.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_consistency, use_container_width=True)

def create_insights_recommendations(df):
    """Generate actionable insights and recommendations"""
    st.subheader("💡 AI-Powered Insights & Recommendations")
    
    # Calculate key insights
    optimal_hashtags = df.groupby('hashtag_count')['engagement_rate'].mean().idxmax()
    best_perf_category = df.groupby('performance_category')['engagement_rate'].mean().idxmax()
    avg_engagement_by_hashtags = df.groupby('hashtag_count')['engagement_rate'].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <h3>🎯 Key Insights</h3>
            <p><strong>Optimal Hashtag Count:</strong> {optimal_hashtags} hashtags per post</p>
            <p><strong>Best Performance Category:</strong> {best_perf_category}</p>
            <p><strong>Engagement Sweet Spot:</strong> Videos with {optimal_hashtags} hashtags get {avg_engagement_by_hashtags[optimal_hashtags]:.1f}% engagement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Top performing hashtags
        all_hashtags = []
        for hashtag_list in df['hashtags']:
            all_hashtags.extend(hashtag_list)
        
        if all_hashtags:
            hashtag_counts = pd.Series(all_hashtags).value_counts().head(10)
            # Create DataFrame for proper plotting
            trending_df = pd.DataFrame({
                'hashtag': [f"#{tag}" for tag in hashtag_counts.index],
                'count': hashtag_counts.values
            })
            
            fig_trending = px.bar(
                trending_df,
                x='count',
                y='hashtag',
                orientation='h',
                title="Trending Hashtags",
                color='count',
                color_continuous_scale='rainbow'
            )
            fig_trending.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            st.plotly_chart(fig_trending, use_container_width=True)

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">📱 TikTok Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("Failed to load data. Please check your CSV file.")
        return
    
    # Sidebar filters
    st.sidebar.markdown('<div class="sidebar-content"><h2>🎛️ Dashboard Controls</h2></div>', unsafe_allow_html=True)
    
    # Hashtag search
    hashtag_filter = st.sidebar.text_input('🔍 Search Hashtag (without #)', value="", help="Enter hashtag to filter content")
    
    # Performance filter
    performance_filter = st.sidebar.multiselect(
        '📊 Filter by Performance',
        options=df['performance_category'].unique(),
        default=df['performance_category'].unique()
    )
    
    # Author filter
    top_authors = df['author_nickname'].value_counts().head(20).index.tolist()
    author_filter = st.sidebar.multiselect(
        '👤 Filter by Creator',
        options=top_authors,
        default=[]
    )
    
    # Apply filters
    filtered_df = df[df['performance_category'].isin(performance_filter)]
    if author_filter:
        filtered_df = filtered_df[filtered_df['author_nickname'].isin(author_filter)]
    
    # Display dashboard sections
    create_kpi_metrics(filtered_df)
    st.markdown("---")
    
    create_performance_overview(filtered_df)
    st.markdown("---")
    
    create_engagement_analysis(filtered_df)
    st.markdown("---")
    
    create_hashtag_analysis(filtered_df, hashtag_filter)
    st.markdown("---")
    
    create_author_insights(filtered_df)
    st.markdown("---")
    
    create_insights_recommendations(filtered_df)
    
    # Raw data viewer
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)

if __name__ == "__main__":
    main()