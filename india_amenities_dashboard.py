"""
India Basic Amenities Analysis Dashboard
=========================================
A comprehensive web-based dashboard to analyze and visualize areas, communities, 
and populations lacking basic amenities (food, water, and shelter) in India.

This program helps government officials understand:
- State-wise access to basic amenities
- Rural vs Urban disparities
- Income group inequalities
- Trends over time
- Priority areas for intervention
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="India Basic Amenities Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-left: 5px solid #2196f3;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


class IndiaAmenitiesAnalyzer:
    """
    Comprehensive analyzer for Indian basic amenities data.
    Handles data generation, analysis, and visualization.
    """
    
    def __init__(self):
        """Initialize the analyzer with sample data structure."""
        self.data = None
        self.states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 
            'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
            'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
            'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi'
        ]
        
    def generate_sample_data(self):
        """
        Generate comprehensive sample data based on actual India survey structures.
        In production, this would load from Census, NSSO, or NFHS data sources.
        """
        np.random.seed(42)
        
        data_records = []
        
        for state in self.states:
            for area_type in ['Rural', 'Urban']:
                for year in [2012, 2018, 2023]:
                    # Base access rates (improve over time)
                    base_improvement = (year - 2012) * 3
                    
                    # Urban areas have better access
                    urban_bonus = 20 if area_type == 'Urban' else 0
                    
                    # State-specific variations
                    state_factor = np.random.uniform(0.8, 1.2)
                    
                    record = {
                        'State': state,
                        'Year': year,
                        'Area_Type': area_type,
                        'Population': np.random.randint(500000, 5000000),
                        
                        # Water Access Indicators (%)
                        'Piped_Water_Access': min(95, max(20, 45 + base_improvement + urban_bonus + np.random.randint(-10, 10)) * state_factor),
                        'Safe_Drinking_Water': min(98, max(30, 60 + base_improvement + urban_bonus + np.random.randint(-8, 8)) * state_factor),
                        'Water_Within_Premises': min(92, max(25, 50 + base_improvement + urban_bonus + np.random.randint(-12, 12)) * state_factor),
                        
                        # Sanitation Indicators (%)
                        'Toilet_Access': min(98, max(20, 40 + base_improvement * 2 + urban_bonus + np.random.randint(-10, 10)) * state_factor),
                        'Septic_Tank_Access': min(90, max(15, 35 + base_improvement + urban_bonus + np.random.randint(-8, 8)) * state_factor),
                        'Open_Defecation': max(2, 40 - base_improvement * 2 - urban_bonus + np.random.randint(-5, 5)),
                        
                        # Housing Indicators (%)
                        'Pucca_Housing': min(95, max(30, 55 + base_improvement + urban_bonus + np.random.randint(-10, 10)) * state_factor),
                        'Electricity_Access': min(99, max(50, 70 + base_improvement + urban_bonus + np.random.randint(-5, 5)) * state_factor),
                        'LPG_Access': min(95, max(15, 30 + base_improvement * 1.5 + urban_bonus + np.random.randint(-10, 10)) * state_factor),
                        
                        # Food Security Indicators
                        'Food_Secure_Households': min(95, max(40, 65 + base_improvement + np.random.randint(-8, 8)) * state_factor),
                        'Malnourished_Children': max(5, 35 - base_improvement - np.random.randint(0, 5)),
                        
                        # Economic Indicators
                        'MPCE_Rupees': max(1500, 2500 + (year - 2012) * 300 + (500 if area_type == 'Urban' else 0) + np.random.randint(-200, 200)),
                        'Below_Poverty_Line': max(5, 25 - base_improvement/2 + np.random.randint(-3, 3)),
                        
                        # Composite Index (BNI - Bare Necessities Index)
                        'BNI_Score': None  # Will be calculated
                    }
                    
                    data_records.append(record)
        
        self.data = pd.DataFrame(data_records)
        
        # Calculate BNI Score (0-1 scale)
        self.data['BNI_Score'] = (
            self.data['Piped_Water_Access'] * 0.15 +
            self.data['Safe_Drinking_Water'] * 0.15 +
            self.data['Toilet_Access'] * 0.20 +
            self.data['Pucca_Housing'] * 0.15 +
            self.data['Electricity_Access'] * 0.15 +
            self.data['LPG_Access'] * 0.10 +
            self.data['Food_Secure_Households'] * 0.10
        ) / 100
        
        return self.data
    
    def calculate_deprivation_metrics(self, df):
        """Calculate households lacking each amenity."""
        metrics = {}
        
        latest_year = df['Year'].max()
        latest_data = df[df['Year'] == latest_year].copy()
        
        # Calculate absolute numbers of deprived households
        latest_data['HH_Without_Water'] = (latest_data['Population'] / 5) * (100 - latest_data['Safe_Drinking_Water']) / 100
        latest_data['HH_Without_Toilet'] = (latest_data['Population'] / 5) * (100 - latest_data['Toilet_Access']) / 100
        latest_data['HH_Without_Pucca_House'] = (latest_data['Population'] / 5) * (100 - latest_data['Pucca_Housing']) / 100
        latest_data['HH_Without_Electricity'] = (latest_data['Population'] / 5) * (100 - latest_data['Electricity_Access']) / 100
        latest_data['HH_Food_Insecure'] = (latest_data['Population'] / 5) * (100 - latest_data['Food_Secure_Households']) / 100
        
        metrics['total_without_water'] = latest_data['HH_Without_Water'].sum()
        metrics['total_without_toilet'] = latest_data['HH_Without_Toilet'].sum()
        metrics['total_without_housing'] = latest_data['HH_Without_Pucca_House'].sum()
        metrics['total_without_electricity'] = latest_data['HH_Without_Electricity'].sum()
        metrics['total_food_insecure'] = latest_data['HH_Food_Insecure'].sum()
        metrics['total_population'] = latest_data['Population'].sum()
        
        return metrics, latest_data
    
    def identify_priority_areas(self, df, threshold=0.5):
        """Identify areas with BNI below threshold - priority for intervention."""
        latest_year = df['Year'].max()
        priority_areas = df[(df['Year'] == latest_year) & (df['BNI_Score'] < threshold)].copy()
        priority_areas = priority_areas.sort_values('BNI_Score')
        
        return priority_areas[['State', 'Area_Type', 'BNI_Score', 'Population', 
                               'Piped_Water_Access', 'Toilet_Access', 
                               'Pucca_Housing', 'Electricity_Access', 'LPG_Access']]
    
    def analyze_rural_urban_gap(self, df):
        """Analyze disparities between rural and urban areas."""
        latest_year = df['Year'].max()
        comparison = df[df['Year'] == latest_year].groupby('Area_Type').agg({
            'BNI_Score': 'mean',
            'Piped_Water_Access': 'mean',
            'Toilet_Access': 'mean',
            'Pucca_Housing': 'mean',
            'Electricity_Access': 'mean',
            'LPG_Access': 'mean',
            'Food_Secure_Households': 'mean',
            'Population': 'sum'
        }).round(2)
        
        return comparison
    
    def plot_india_map(self, df, metric, year):
        """Create India state-wise choropleth map."""
        data_year = df[df['Year'] == year].groupby('State')[metric].mean().reset_index()
        
        fig = px.choropleth(
            data_year,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='State',
            color=metric,
            color_continuous_scale='RdYlGn',
            title=f'{metric.replace("_", " ")} by State ({year})',
            hover_data={'State': True, metric: ':.2f'}
        )
        
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
        
        return fig
    
    def plot_trend_analysis(self, df, metric, top_n=10):
        """Plot trends over time for top/bottom states."""
        latest_year = df['Year'].max()
        
        # Get top and bottom states based on latest year
        latest_data = df[df['Year'] == latest_year].groupby('State')[metric].mean().reset_index()
        top_states = latest_data.nlargest(top_n//2, metric)['State'].tolist()
        bottom_states = latest_data.nsmallest(top_n//2, metric)['State'].tolist()
        selected_states = top_states + bottom_states
        
        trend_data = df[df['State'].isin(selected_states)].groupby(['State', 'Year'])[metric].mean().reset_index()
        
        fig = px.line(
            trend_data,
            x='Year',
            y=metric,
            color='State',
            markers=True,
            title=f'Trend Analysis: {metric.replace("_", " ")} (Top & Bottom {top_n//2} States)',
            labels={metric: metric.replace("_", " ")},
            height=500
        )
        
        fig.update_layout(hovermode='x unified')
        
        return fig
    
    def plot_rural_urban_comparison(self, df):
        """Compare rural vs urban access across amenities."""
        latest_year = df['Year'].max()
        comparison = df[df['Year'] == latest_year].groupby('Area_Type').agg({
            'Piped_Water_Access': 'mean',
            'Toilet_Access': 'mean',
            'Pucca_Housing': 'mean',
            'Electricity_Access': 'mean',
            'LPG_Access': 'mean'
        }).round(2)
        
        fig = go.Figure()
        
        amenities = comparison.columns.tolist()
        
        fig.add_trace(go.Bar(
            name='Rural',
            x=amenities,
            y=comparison.loc['Rural'].values,
            marker_color='#ff7f0e'
        ))
        
        fig.add_trace(go.Bar(
            name='Urban',
            x=amenities,
            y=comparison.loc['Urban'].values,
            marker_color='#1f77b4'
        ))
        
        fig.update_layout(
            title='Rural vs Urban Access to Basic Amenities (%)',
            xaxis_title='Amenity',
            yaxis_title='Access Rate (%)',
            barmode='group',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def plot_bni_heatmap(self, df):
        """Create heatmap of BNI scores across states and years."""
        pivot_data = df.groupby(['State', 'Year'])['BNI_Score'].mean().reset_index()
        pivot_table = pivot_data.pivot(index='State', columns='Year', values='BNI_Score')
        
        fig = px.imshow(
            pivot_table,
            labels=dict(x="Year", y="State", color="BNI Score"),
            x=pivot_table.columns,
            y=pivot_table.index,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title='Bare Necessities Index (BNI) Heatmap: State-wise Progress'
        )
        
        fig.update_layout(height=800)
        
        return fig
    
    def plot_deprivation_sunburst(self, df):
        """Create sunburst chart showing deprivation hierarchy."""
        latest_year = df['Year'].max()
        latest_data = df[df['Year'] == latest_year].copy()
        
        # Create hierarchy data
        sunburst_data = []
        
        for _, row in latest_data.iterrows():
            state = row['State']
            area = row['Area_Type']
            pop = row['Population']
            
            # Add to hierarchy
            sunburst_data.append({
                'State': state,
                'Area': f"{state} - {area}",
                'Category': f"{state} - {area} - Water",
                'Value': pop * (100 - row['Safe_Drinking_Water']) / 100
            })
            sunburst_data.append({
                'State': state,
                'Area': f"{state} - {area}",
                'Category': f"{state} - {area} - Sanitation",
                'Value': pop * (100 - row['Toilet_Access']) / 100
            })
            sunburst_data.append({
                'State': state,
                'Area': f"{state} - {area}",
                'Category': f"{state} - {area} - Housing",
                'Value': pop * (100 - row['Pucca_Housing']) / 100
            })
        
        df_sunburst = pd.DataFrame(sunburst_data)
        
        # Get top 10 areas by total deprivation
        top_areas = df_sunburst.groupby('Area')['Value'].sum().nlargest(10).index.tolist()
        df_sunburst = df_sunburst[df_sunburst['Area'].isin(top_areas)]
        
        fig = px.sunburst(
            df_sunburst,
            path=['State', 'Area', 'Category'],
            values='Value',
            title='Deprivation Hierarchy: Top 10 Areas by Population Lacking Amenities',
            height=700
        )
        
        return fig


# Streamlit App Implementation
def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">🏠 India Basic Amenities Analysis Dashboard</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>📊 Purpose:</b> This dashboard helps government officials identify areas, communities, and populations 
    lacking basic amenities (water, sanitation, housing, food) to prioritize interventions and allocate resources effectively.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = IndiaAmenitiesAnalyzer()
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Data loading
    with st.spinner("Loading and analyzing data..."):
        df = analyzer.generate_sample_data()
    
    st.sidebar.success(f"✅ Data loaded: {len(df):,} records")
    
    # Year selection
    available_years = sorted(df['Year'].unique())
    selected_year = st.sidebar.selectbox("📅 Select Year", available_years, 
                                         index=len(available_years)-1)
    
    # State filter
    all_states_option = ['All States'] + analyzer.states
    selected_state = st.sidebar.selectbox("🗺️ Select State", all_states_option)
    
    # Area type filter
    area_filter = st.sidebar.radio("🏘️ Area Type", ['All', 'Rural', 'Urban'])
    
    # BNI threshold for priority areas
    bni_threshold = st.sidebar.slider("🎯 BNI Threshold for Priority Areas", 
                                      0.0, 1.0, 0.5, 0.05)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About BNI")
    st.sidebar.info("""
    **Bare Necessities Index (BNI)**: A composite index measuring access to:
    - Water (30%)
    - Sanitation (20%)
    - Housing (15%)
    - Electricity (15%)
    - Clean Cooking Fuel (10%)
    - Food Security (10%)
    
    Range: 0 (worst) to 1 (best)
    """)
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_state != 'All States':
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if area_filter != 'All':
        filtered_df = filtered_df[filtered_df['Area_Type'] == area_filter]
    
    # Main content - Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "🗺️ Geographic Analysis", 
        "📈 Trends", 
        "🎯 Priority Areas",
        "👥 Rural-Urban Gap",
        "📑 Detailed Data"
    ])
    
    # TAB 1: Overview
    with tab1:
        st.header("Key Metrics Overview")
        
        # Calculate metrics
        metrics, latest_data = analyzer.calculate_deprivation_metrics(df)
        
        # Display key metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="🚰 Without Safe Water",
                value=f"{metrics['total_without_water']/1000000:.2f}M",
                delta=f"{(metrics['total_without_water']/metrics['total_population']*100):.1f}% of pop.",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                label="🚽 Without Toilet",
                value=f"{metrics['total_without_toilet']/1000000:.2f}M",
                delta=f"{(metrics['total_without_toilet']/metrics['total_population']*100):.1f}% of pop.",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                label="🏠 Without Pucca House",
                value=f"{metrics['total_without_housing']/1000000:.2f}M",
                delta=f"{(metrics['total_without_housing']/metrics['total_population']*100):.1f}% of pop.",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                label="⚡ Without Electricity",
                value=f"{metrics['total_without_electricity']/1000000:.2f}M",
                delta=f"{(metrics['total_without_electricity']/metrics['total_population']*100):.1f}% of pop.",
                delta_color="inverse"
            )
        
        with col5:
            st.metric(
                label="🍽️ Food Insecure",
                value=f"{metrics['total_food_insecure']/1000000:.2f}M",
                delta=f"{(metrics['total_food_insecure']/metrics['total_population']*100):.1f}% of pop.",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Multi-dimensional analysis
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Top 10 States by BNI Score")
            top_states = df[df['Year'] == selected_year].groupby('State')['BNI_Score'].mean().nlargest(10).reset_index()
            fig = px.bar(top_states, x='BNI_Score', y='State', orientation='h',
                        color='BNI_Score', color_continuous_scale='Greens',
                        title=f'Top Performing States ({selected_year})')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_b:
            st.subheader("Bottom 10 States by BNI Score")
            bottom_states = df[df['Year'] == selected_year].groupby('State')['BNI_Score'].mean().nsmallest(10).reset_index()
            fig = px.bar(bottom_states, x='BNI_Score', y='State', orientation='h',
                        color='BNI_Score', color_continuous_scale='Reds',
                        title=f'States Needing Priority ({selected_year})')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Sunburst visualization
        st.subheader("Deprivation Distribution Hierarchy")
        fig_sunburst = analyzer.plot_deprivation_sunburst(df)
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # TAB 2: Geographic Analysis
    with tab2:
        st.header("Geographic Distribution of Basic Amenities")
        
        # Metric selection for map
        map_metric = st.selectbox(
            "Select metric to visualize",
            ['BNI_Score', 'Piped_Water_Access', 'Toilet_Access', 
             'Pucca_Housing', 'Electricity_Access', 'LPG_Access',
             'Food_Secure_Households']
        )
        
        try:
            fig_map = analyzer.plot_india_map(filtered_df, map_metric, selected_year)
            st.plotly_chart(fig_map, use_container_width=True)
        except Exception as e:
            st.warning("⚠️ Map visualization requires geojson data. Showing alternative visualization.")
            
            # Alternative: bar chart by state
            state_data = filtered_df[filtered_df['Year'] == selected_year].groupby('State')[map_metric].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(state_data, x='State', y=map_metric, 
                        color=map_metric,
                        color_continuous_scale='RdYlGn',
                        title=f'{map_metric.replace("_", " ")} by State')
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # BNI Heatmap
        st.subheader("BNI Progress Heatmap (All States, All Years)")
        fig_heatmap = analyzer.plot_bni_heatmap(df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # TAB 3: Trends
    with tab3:
        st.header("Temporal Trends Analysis")
        
        trend_metric = st.selectbox(
            "Select metric for trend analysis",
            ['BNI_Score', 'Piped_Water_Access', 'Toilet_Access', 
             'Pucca_Housing', 'Electricity_Access', 'LPG_Access'],
            key='trend_metric'
        )
        
        fig_trend = analyzer.plot_trend_analysis(filtered_df, trend_metric)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Year-over-year improvement
        st.subheader("Year-over-Year Improvement Analysis")
        
        yoy_data = df.groupby(['Year', 'Area_Type']).agg({
            'BNI_Score': 'mean',
            'Piped_Water_Access': 'mean',
            'Toilet_Access': 'mean',
            'Pucca_Housing': 'mean'
        }).reset_index()
        
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('BNI Score', 'Water Access', 
                                         'Sanitation', 'Housing'))
        
        for area in ['Rural', 'Urban']:
            area_data = yoy_data[yoy_data['Area_Type'] == area]
            
            fig.add_trace(go.Scatter(x=area_data['Year'], y=area_data['BNI_Score'],
                                    mode='lines+markers', name=f'{area} - BNI',
                                    legendgroup=area), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=area_data['Year'], y=area_data['Piped_Water_Access'],
                                    mode='lines+markers', name=f'{area} - Water',
                                    legendgroup=area, showlegend=False), row=1, col=2)
            
            fig.add_trace(go.Scatter(x=area_data['Year'], y=area_data['Toilet_Access'],
                                    mode='lines+markers', name=f'{area} - Toilet',
                                    legendgroup=area, showlegend=False), row=2, col=1)
            
            fig.add_trace(go.Scatter(x=area_data['Year'], y=area_data['Pucca_Housing'],
                                    mode='lines+markers', name=f'{area} - Housing',
                                    legendgroup=area, showlegend=False), row=2, col=2)
        
        fig.update_layout(height=700, title_text="Multi-dimensional Trend Comparison")
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: Priority Areas
    with tab4:
        st.header("🎯 Priority Areas for Government Intervention")
        
        st.info(f"Areas with BNI Score below {bni_threshold} are identified as priority areas needing immediate attention.")
        
        priority_areas = analyzer.identify_priority_areas(df, threshold=bni_threshold)
        
        if len(priority_areas) > 0:
            st.subheader(f"📍 {len(priority_areas)} Priority Areas Identified")
            
            # Display priority areas table
            priority_display = priority_areas.copy()
            priority_display['Population_Millions'] = (priority_display['Population'] / 1000000).round(2)
            priority_display = priority_display.drop('Population', axis=1)
            
            # Color coding
            def highlight_low_access(val):
                if isinstance(val, (int, float)):
                    if val < 50:
                        return 'background-color: #ffcdd2'
                    elif val < 70:
                        return 'background-color: #fff9c4'
                    else:
                        return 'background-color: #c8e6c9'
                return ''
            
            styled_df = priority_display.style.applymap(
                highlight_low_access,
                subset=['BNI_Score', 'Piped_Water_Access', 'Toilet_Access', 
                       'Pucca_Housing', 'Electricity_Access', 'LPG_Access']
            )
            
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Priority visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(priority_areas, 
                               x='BNI_Score', 
                               y='Population',
                               color='Area_Type',
                               size='Population',
                               hover_data=['State'],
                               title='Priority Areas: BNI vs Population',
                               labels={'Population': 'Population Size'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Amenity gap analysis
                amenity_gaps = priority_areas[['State', 'Area_Type', 
                                              'Piped_Water_Access', 'Toilet_Access',
                                              'Pucca_Housing', 'Electricity_Access']].copy()
                amenity_gaps['Water_Gap'] = 100 - amenity_gaps['Piped_Water_Access']
                amenity_gaps['Toilet_Gap'] = 100 - amenity_gaps['Toilet_Access']
                amenity_gaps['Housing_Gap'] = 100 - amenity_gaps['Pucca_Housing']
                amenity_gaps['Electricity_Gap'] = 100 - amenity_gaps['Electricity_Access']
                
                gap_summary = amenity_gaps[['Water_Gap', 'Toilet_Gap', 
                                           'Housing_Gap', 'Electricity_Gap']].mean()
                
                fig = go.Figure(data=[
                    go.Bar(x=gap_summary.index, y=gap_summary.values,
                          marker_color='indianred')
                ])
                fig.update_layout(title='Average Amenity Gaps in Priority Areas (%)',
                                xaxis_title='Amenity', yaxis_title='Gap (%)',
                                height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Key Recommendations")
            
            worst_water = priority_areas.nsmallest(3, 'Piped_Water_Access')[['State', 'Area_Type', 'Piped_Water_Access']]
            worst_sanitation = priority_areas.nsmallest(3, 'Toilet_Access')[['State', 'Area_Type', 'Toilet_Access']]
            worst_housing = priority_areas.nsmallest(3, 'Pucca_Housing')[['State', 'Area_Type', 'Pucca_Housing']]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🚰 Water Priority**")
                for idx, row in worst_water.iterrows():
                    st.write(f"• {row['State']} ({row['Area_Type']}): {row['Piped_Water_Access']:.1f}%")
            
            with col2:
                st.markdown("**🚽 Sanitation Priority**")
                for idx, row in worst_sanitation.iterrows():
                    st.write(f"• {row['State']} ({row['Area_Type']}): {row['Toilet_Access']:.1f}%")
            
            with col3:
                st.markdown("**🏠 Housing Priority**")
                for idx, row in worst_housing.iterrows():
                    st.write(f"• {row['State']} ({row['Area_Type']}): {row['Pucca_Housing']:.1f}%")
        
        else:
            st.success("✅ No priority areas identified with current threshold. Consider adjusting the threshold.")
    
    # TAB 5: Rural-Urban Gap
    with tab5:
        st.header("Rural-Urban Disparity Analysis")
        
        # Comparison metrics
        comparison = analyzer.analyze_rural_urban_gap(df)
        
        st.subheader("Access Rates Comparison")
        st.dataframe(comparison.style.format("{:.2f}"), use_container_width=True)
        
        # Visual comparison
        fig_comparison = analyzer.plot_rural_urban_comparison(df)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Gap analysis over time
        st.subheader("Rural-Urban Gap Evolution")
        
        gap_data = df.pivot_table(
            values=['BNI_Score', 'Piped_Water_Access', 'Toilet_Access'],
            index='Year',
            columns='Area_Type',
            aggfunc='mean'
        )
        
        gap_metrics = pd.DataFrame({
            'Year': gap_data.index,
            'BNI_Gap': gap_data['BNI_Score']['Urban'] - gap_data['BNI_Score']['Rural'],
            'Water_Gap': gap_data['Piped_Water_Access']['Urban'] - gap_data['Piped_Water_Access']['Rural'],
            'Toilet_Gap': gap_data['Toilet_Access']['Urban'] - gap_data['Toilet_Access']['Rural']
        })
        
        fig = px.line(gap_metrics, x='Year', 
                     y=['BNI_Gap', 'Water_Gap', 'Toilet_Gap'],
                     title='Urban-Rural Gap Over Time (Urban minus Rural %)',
                     labels={'value': 'Gap (percentage points)', 'variable': 'Metric'})
        fig.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # State-wise gap analysis
        st.subheader("State-wise Rural-Urban Gap")
        
        latest_gap = df[df['Year'] == selected_year].pivot_table(
            values='BNI_Score',
            index='State',
            columns='Area_Type',
            aggfunc='mean'
        )
        latest_gap['Gap'] = latest_gap['Urban'] - latest_gap['Rural']
        latest_gap = latest_gap.sort_values('Gap', ascending=False).reset_index()
        
        fig = px.bar(latest_gap, x='State', y='Gap',
                    color='Gap', color_continuous_scale='RdYlGn_r',
                    title=f'Rural-Urban BNI Gap by State ({selected_year})')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 6: Detailed Data
    with tab6:
        st.header("Detailed Data Explorer")
        
        st.subheader("Filter and Download Data")
        
        # Show filtered data
        display_df = filtered_df[filtered_df['Year'] == selected_year].copy()
        
        # Column selection
        available_columns = display_df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display",
            available_columns,
            default=['State', 'Area_Type', 'BNI_Score', 'Piped_Water_Access', 
                    'Toilet_Access', 'Pucca_Housing', 'Population']
        )
        
        if selected_columns:
            st.dataframe(display_df[selected_columns], use_container_width=True, height=400)
            
            # Download button
            csv = display_df[selected_columns].to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name=f"india_amenities_{selected_year}_{area_filter}.csv",
                mime="text/csv"
            )
        
        # Statistical summary
        st.subheader("Statistical Summary")
        
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        summary_stats = display_df[numeric_cols].describe().T
        
        st.dataframe(summary_stats.style.format("{:.2f}"), use_container_width=True)
        
        # Correlation analysis
        st.subheader("Correlation Analysis")
        
        correlation_vars = ['BNI_Score', 'Piped_Water_Access', 'Toilet_Access',
                           'Pucca_Housing', 'Electricity_Access', 'LPG_Access',
                           'MPCE_Rupees', 'Below_Poverty_Line']
        
        corr_matrix = display_df[correlation_vars].corr()
        
        fig = px.imshow(corr_matrix,
                       text_auto='.2f',
                       color_continuous_scale='RdBu_r',
                       aspect='auto',
                       title='Correlation Matrix of Key Indicators')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📚 Data Sources & References
    
    This dashboard is designed to work with:
    - **Census of India** - Housing and Amenities Data
    - **NSSO (National Sample Survey Office)** - Household Consumption Expenditure Survey
    - **NFHS (National Family Health Survey)** - Health and Nutrition Data
    - **Economic Survey** - Bare Necessities Index
    
    **Note**: This version uses simulated data for demonstration. In production, connect to official 
    government data sources via APIs or direct database connections.
    
    ---
    **Developed for Government of India | Ministry of Statistics & Programme Implementation**
    """)


if __name__ == "__main__":
    main()
