# India Basic Amenities Analysis Dashboard

## 🎯 Overview

A comprehensive web-based dashboard designed to help the Government of India analyze and visualize areas, communities, and populations lacking basic amenities including **food, water, and shelter**. This tool enables data-driven decision-making for policy interventions and resource allocation.

## 📊 Key Features

### 1. **Multi-Dimensional Analysis**
- **Water Access**: Piped water, safe drinking water, water within premises
- **Sanitation**: Toilet access, septic tank facilities, open defecation rates
- **Housing**: Pucca housing, electricity access, LPG for cooking
- **Food Security**: Food-secure households, malnutrition indicators
- **Economic Indicators**: MPCE (Monthly Per Capita Consumption Expenditure), poverty rates

### 2. **Comprehensive Visualizations**
- **Interactive Maps**: State-wise choropleth maps for any indicator
- **Trend Analysis**: Multi-year trends for top and bottom performing states
- **Heatmaps**: BNI (Bare Necessities Index) progress across states
- **Rural-Urban Comparisons**: Gap analysis and disparity trends
- **Priority Area Identification**: Automatic flagging of areas needing intervention

### 3. **Government Decision Support**
- **Priority Area Detection**: Identifies regions with BNI below threshold
- **Resource Allocation Guidance**: Highlights specific amenity gaps
- **Trend Monitoring**: Tracks progress of government schemes
- **Equity Analysis**: Monitors improvements in vulnerable populations

### 4. **Data Export & Reporting**
- CSV export functionality
- Customizable data filters
- Statistical summaries
- Correlation analysis

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download Files
```bash
# Create a project directory
mkdir india_amenities_analysis
cd india_amenities_analysis

# Copy the following files to this directory:
# - india_amenities_dashboard.py
# - data_loader.py
# - requirements.txt
# - README.md
```

### Step 2: Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 3: Run the Dashboard
```bash
# Launch the Streamlit web application
streamlit run india_amenities_dashboard.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

## 📁 File Structure

```
india_amenities_analysis/
│
├── india_amenities_dashboard.py    # Main dashboard application
├── data_loader.py                   # Data loading and preprocessing module
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
└── data/                           # Data directory (create as needed)
    ├── census_data.csv
    ├── nsso_hces_data.xlsx
    └── nfhs_data.csv
```

## 📖 Usage Guide

### Dashboard Navigation

#### **Tab 1: Overview**
- View key metrics (households without water, sanitation, housing, etc.)
- Identify top and bottom performing states
- Visualize deprivation distribution hierarchy

#### **Tab 2: Geographic Analysis**
- Interactive state-wise maps for any indicator
- BNI progress heatmap across all states and years
- Visual comparison of geographic disparities

#### **Tab 3: Trends**
- Temporal analysis of any indicator
- Multi-dimensional trend comparison
- Year-over-year improvement tracking

#### **Tab 4: Priority Areas**
- Automatic identification of areas needing intervention
- Specific amenity gap analysis
- Evidence-based recommendations for policymakers

#### **Tab 5: Rural-Urban Gap**
- Disparity analysis between rural and urban areas
- Gap evolution over time
- State-wise rural-urban comparison

#### **Tab 6: Detailed Data**
- Data explorer with filtering capabilities
- CSV export functionality
- Statistical summaries and correlation analysis

### Using Real Data

#### Option 1: Load from CSV Files
```python
from data_loader import IndiaDataLoader

loader = IndiaDataLoader()

# Load your data
census_data = loader.load_census_data('data/census_data.csv')
nsso_data = loader.load_nsso_hces_data('data/hces_data.xlsx')

# Preprocess
processed_data = loader.preprocess_amenities_data(census_data)
data_with_bni = loader.calculate_bni_score(processed_data)
```

#### Option 2: Connect to Government APIs
Modify `data_loader.py` to add API endpoints:
```python
# Example: India Open Data Portal
dataset = loader.load_from_open_data_portal('your-dataset-id')
```

## 📊 Data Sources

The dashboard is designed to work with data from:

1. **Census of India**
   - Website: https://censusindia.gov.in
   - Data: Housing conditions, household amenities
   - Format: Excel/CSV

2. **NSSO (National Sample Survey Office)**
   - Website: https://www.mospi.gov.in
   - Data: Household Consumption Expenditure Survey (HCES)
   - Format: Excel/CSV

3. **NFHS (National Family Health Survey)**
   - Website: http://rchiips.org/nfhs/
   - Data: Health, nutrition, water, sanitation
   - Format: Excel/CSV/DTA

4. **India Open Data Portal**
   - Website: https://data.gov.in
   - Data: Various government datasets
   - Format: CSV/JSON/API

## 🧮 Calculations & Methodology

### Bare Necessities Index (BNI)

The BNI is calculated as a weighted average of key indicators:

```
BNI = (Water_Access × 0.30) + 
      (Sanitation × 0.20) + 
      (Housing × 0.15) + 
      (Electricity × 0.15) + 
      (Clean_Fuel × 0.10) + 
      (Food_Security × 0.10)
```

**Scale**: 0 to 1 (0 = worst access, 1 = best access)

**Interpretation**:
- BNI < 0.5: Priority area (needs immediate intervention)
- BNI 0.5-0.7: Medium access (targeted improvements needed)
- BNI > 0.7: Good access (maintain and enhance)

### Deprivation Metrics

For each amenity, the number of deprived households is calculated as:

```
Deprived_HH = (Total_Population / Avg_HH_Size) × (100 - Access_Rate) / 100
```

where `Avg_HH_Size` = 5 (typical Indian household size)

## 🎨 Customization

### Adding New Indicators

1. Modify the data generation in `india_amenities_dashboard.py`:
```python
record = {
    'State': state,
    'Year': year,
    # ... existing indicators ...
    'New_Indicator': value,  # Add your indicator here
}
```

2. Include in BNI calculation:
```python
self.data['BNI_Score'] = (
    # ... existing weights ...
    self.data['New_Indicator'] * weight +
) / 100
```

### Changing Visualization Colors

Modify color schemes in plotting functions:
```python
color_continuous_scale='RdYlGn'  # Red-Yellow-Green
# or
color_continuous_scale='Viridis'  # Purple-Yellow
```

### Adjusting Priority Thresholds

Change the default BNI threshold:
```python
bni_threshold = st.sidebar.slider(
    "BNI Threshold", 
    0.0, 1.0, 
    0.5,  # Change default value here
    0.05
)
```

## 🔧 Advanced Features

### Statistical Analysis
- **Correlation Analysis**: Identify relationships between indicators
- **Trend Analysis**: Track improvements over time
- **Gap Analysis**: Measure rural-urban disparities

### Performance Calculations
```python
# Calculate deprivation metrics
metrics = analyzer.calculate_deprivation_metrics(df)

# Identify priority areas
priority_areas = analyzer.identify_priority_areas(df, threshold=0.5)

# Analyze rural-urban gaps
gap_analysis = analyzer.analyze_rural_urban_gap(df)
```

## 📱 Deployment

### Local Deployment
Already covered in Installation section above.

### Cloud Deployment

#### Option 1: Streamlit Cloud (Free)
1. Push code to GitHub repository
2. Visit https://streamlit.io/cloud
3. Connect your GitHub repo
4. Deploy with one click

#### Option 2: AWS/Azure/GCP
```bash
# Example for AWS EC2
# 1. Launch EC2 instance
# 2. Install dependencies
# 3. Run streamlit with public access
streamlit run india_amenities_dashboard.py --server.port 80 --server.address 0.0.0.0
```

## 🤝 Contributing

To extend or improve this dashboard:

1. **Add new data sources**: Modify `data_loader.py`
2. **Add new visualizations**: Extend `IndiaAmenitiesAnalyzer` class
3. **Improve calculations**: Update BNI or other metric calculations
4. **Enhance UI**: Modify Streamlit layout and styling

## 📞 Support & Contact

For technical issues or feature requests:
- Review the code comments for detailed documentation
- Check data format requirements in `data_loader.py`
- Ensure all dependencies are properly installed

## 📄 License

Developed for Government of India usage. Adapt and extend as needed for official government analysis and reporting.

## 🙏 Acknowledgments

Data methodologies based on:
- Economic Survey of India 2020-21 (Bare Necessities Index)
- Census of India (Housing and Amenity indicators)
- NSSO surveys (Consumption patterns)
- NFHS reports (Health and nutrition data)

---

**Version**: 1.0  
**Last Updated**: 2025  
**Developed for**: Ministry of Statistics & Programme Implementation, Government of India
