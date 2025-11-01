# API Integration Guide
## Connecting to Real Government Data Sources

This guide explains how to integrate the dashboard with actual Indian government data sources and APIs.

---

## 🌐 Available Data Sources

### 1. **India Open Data Portal (data.gov.in)**

#### Base Information:
- **URL**: https://data.gov.in/
- **Format**: JSON, CSV, XML
- **Authentication**: API Key required (free registration)
- **Update Frequency**: Varies by dataset

#### Getting API Key:
1. Visit https://data.gov.in/
2. Register for a free account
3. Navigate to "API" section
4. Generate your API key

#### Example Implementation:

```python
import requests
import pandas as pd

class OpenDataPortalAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.data.gov.in/resource/"
    
    def fetch_dataset(self, resource_id, filters=None):
        """
        Fetch dataset from Open Data Portal
        
        Parameters:
        - resource_id: Dataset identifier
        - filters: Dict of filter parameters
        """
        params = {
            'api-key': self.api_key,
            'format': 'json',
            'limit': 10000
        }
        
        if filters:
            params.update(filters)
        
        url = f"{self.base_url}{resource_id}"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['records'])
        else:
            print(f"Error: {response.status_code}")
            return None

# Usage
api = OpenDataPortalAPI(api_key='YOUR_API_KEY')
census_data = api.fetch_dataset(resource_id='census-housing-dataset-id')
```

### 2. **Census of India API**

#### Access Methods:
- **Direct Download**: Excel/CSV files from censusindia.gov.in
- **Bulk Download**: State-wise data tables
- **Web Scraping**: Automated extraction (respect robots.txt)

#### Example Implementation:

```python
import pandas as pd
import requests
from bs4 import BeautifulSoup

class CensusDataFetcher:
    def __init__(self):
        self.base_url = "https://censusindia.gov.in"
    
    def download_census_table(self, table_url, save_path):
        """
        Download Census table (Excel format)
        """
        response = requests.get(table_url)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Read Excel file
            df = pd.read_excel(save_path)
            return df
        return None
    
    def parse_housing_data(self, df):
        """
        Parse and standardize Census housing data
        """
        # Map Census columns to standard format
        column_mapping = {
            'State Name': 'State',
            'Total Households': 'Total_HH',
            'HH with Piped Water': 'Piped_Water_HH',
            'HH with Toilet': 'Toilet_HH',
            'HH with Electricity': 'Electricity_HH'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Calculate percentages
        df['Piped_Water_Access'] = (df['Piped_Water_HH'] / df['Total_HH']) * 100
        df['Toilet_Access'] = (df['Toilet_HH'] / df['Total_HH']) * 100
        df['Electricity_Access'] = (df['Electricity_HH'] / df['Total_HH']) * 100
        
        return df

# Usage
fetcher = CensusDataFetcher()
data = fetcher.download_census_table(
    'https://censusindia.gov.in/census.../HH-08.xlsx',
    'census_housing.xlsx'
)
processed = fetcher.parse_housing_data(data)
```

### 3. **MOSPI (Ministry of Statistics) API**

#### Information:
- **URL**: https://www.mospi.gov.in/
- **Data**: NSSO surveys, HCES data
- **Format**: Excel, PDF reports
- **Access**: Direct download, no API currently

#### Example Implementation:

```python
import pandas as pd
import requests

class MOSPIDataLoader:
    def __init__(self):
        self.base_url = "https://www.mospi.gov.in/sites/default/files/"
    
    def download_hces_report(self, report_url):
        """
        Download HCES report (Excel format)
        """
        response = requests.get(report_url)
        
        if response.status_code == 200:
            # Save file
            filename = report_url.split('/')[-1]
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Read data
            df = pd.read_excel(filename, sheet_name=0)
            return df
        return None
    
    def extract_mpce_data(self, df):
        """
        Extract MPCE (Monthly Per Capita Consumption Expenditure) data
        """
        # Clean and process MPCE data
        # (Actual implementation depends on file structure)
        return df

# Usage
loader = MOSPIDataLoader()
hces_data = loader.download_hces_report(
    'https://www.mospi.gov.in/sites/default/files/reports/HCES_2023-24.xlsx'
)
```

### 4. **NFHS (National Family Health Survey) Data**

#### Access:
- **Primary**: DHS Program website (dhsprogram.com)
- **Secondary**: rchiips.org/nfhs
- **Format**: CSV, DTA (Stata), SAV (SPSS)

#### Example Implementation:

```python
import pandas as pd
import requests

class NFHSDataLoader:
    def __init__(self):
        self.dhs_url = "https://dhsprogram.com/data/"
        self.nfhs_url = "http://rchiips.org/nfhs/factsheet_NFHS-5.shtml"
    
    def load_nfhs_csv(self, csv_path):
        """
        Load NFHS CSV data
        """
        df = pd.read_csv(csv_path)
        return df
    
    def extract_amenities_indicators(self, df):
        """
        Extract water, sanitation, housing indicators from NFHS
        """
        # Map NFHS variable names to standard format
        indicator_mapping = {
            'hv201': 'Water_Source',
            'hv205': 'Toilet_Type',
            'hv206': 'Electricity',
            'hv226': 'Cooking_Fuel'
        }
        
        # Create percentages
        # (Implementation depends on NFHS data structure)
        
        return df

# Usage
loader = NFHSDataLoader()
nfhs_data = loader.load_nfhs_csv('NFHS5_state_data.csv')
amenities = loader.extract_amenities_indicators(nfhs_data)
```

---

## 🔄 Automated Data Updates

### Setting Up Scheduled Updates

```python
import schedule
import time
from datetime import datetime

class AutoDataUpdater:
    def __init__(self):
        self.data_sources = {
            'census': CensusDataFetcher(),
            'mospi': MOSPIDataLoader(),
            'nfhs': NFHSDataLoader()
        }
        self.last_update = None
    
    def update_all_data(self):
        """
        Fetch latest data from all sources
        """
        print(f"Starting data update: {datetime.now()}")
        
        try:
            # Update Census data
            census_data = self.data_sources['census'].download_latest()
            
            # Update MOSPI data
            mospi_data = self.data_sources['mospi'].download_latest()
            
            # Update NFHS data
            nfhs_data = self.data_sources['nfhs'].download_latest()
            
            # Merge and save
            merged_data = self.merge_all_sources(census_data, mospi_data, nfhs_data)
            merged_data.to_csv('updated_amenities_data.csv', index=False)
            
            self.last_update = datetime.now()
            print(f"Update completed: {self.last_update}")
            
        except Exception as e:
            print(f"Update failed: {e}")
    
    def merge_all_sources(self, *dataframes):
        """
        Merge data from multiple sources
        """
        # Implementation for merging
        pass
    
    def schedule_daily_update(self, hour=2):
        """
        Schedule daily updates at specified hour
        """
        schedule.every().day.at(f"{hour:02d}:00").do(self.update_all_data)
        
        print(f"Scheduled daily updates at {hour}:00")
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

# Usage
updater = AutoDataUpdater()
updater.schedule_daily_update(hour=2)  # Update at 2 AM daily
```

---

## 📊 Real-Time Dashboard Integration

### Modifying the Dashboard for Live Data

```python
# In india_amenities_dashboard.py

import streamlit as st
from data_loader import IndiaDataLoader
from api_integration import OpenDataPortalAPI, CensusDataFetcher

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_live_data():
    """
    Load data from live sources with caching
    """
    # Initialize API connections
    odp_api = OpenDataPortalAPI(api_key=st.secrets["ODP_API_KEY"])
    census_fetcher = CensusDataFetcher()
    
    # Fetch latest data
    census_data = census_fetcher.download_latest()
    amenities_data = odp_api.fetch_dataset('amenities-dataset-id')
    
    # Merge and process
    loader = IndiaDataLoader()
    merged_data = loader.merge_multiple_sources({
        'census': census_data,
        'amenities': amenities_data
    })
    
    processed_data = loader.preprocess_amenities_data(merged_data)
    final_data = loader.calculate_bni_score(processed_data)
    
    return final_data

# In main():
# Replace:
# df = analyzer.generate_sample_data()
# With:
df = load_live_data()
```

---

## 🔐 Secure API Key Management

### Using Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml

[data_sources]
ODP_API_KEY = "your_open_data_portal_key"
CENSUS_USERNAME = "your_census_username"
CENSUS_PASSWORD = "your_census_password"

[database]
DB_HOST = "localhost"
DB_NAME = "amenities_db"
DB_USER = "admin"
DB_PASSWORD = "secure_password"
```

Access in code:

```python
import streamlit as st

api_key = st.secrets["data_sources"]["ODP_API_KEY"]
db_config = st.secrets["database"]
```

---

## 💾 Database Integration

### Connecting to PostgreSQL/MySQL

```python
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

class DatabaseConnector:
    def __init__(self, host, database, user, password):
        self.connection_string = f"postgresql://{user}:{password}@{host}/{database}"
        self.engine = create_engine(self.connection_string)
    
    def fetch_latest_data(self):
        """
        Fetch latest amenities data from database
        """
        query = """
        SELECT 
            state,
            year,
            area_type,
            piped_water_access,
            toilet_access,
            pucca_housing,
            electricity_access,
            bni_score
        FROM amenities_data
        WHERE year = (SELECT MAX(year) FROM amenities_data)
        ORDER BY state, area_type
        """
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def update_data(self, df):
        """
        Update database with new data
        """
        df.to_sql('amenities_data', self.engine, 
                 if_exists='append', index=False)
    
    def get_historical_trends(self, state, years=5):
        """
        Get historical trends for a specific state
        """
        query = f"""
        SELECT * FROM amenities_data
        WHERE state = '{state}'
        AND year >= (SELECT MAX(year) - {years} FROM amenities_data)
        ORDER BY year
        """
        
        df = pd.read_sql(query, self.engine)
        return df

# Usage
db = DatabaseConnector(
    host='localhost',
    database='india_amenities',
    user='admin',
    password='password'
)

latest_data = db.fetch_latest_data()
```

---

## 📝 Complete Integration Example

```python
# complete_integration.py

import streamlit as st
import pandas as pd
from api_integration import OpenDataPortalAPI, CensusDataFetcher, MOSPIDataLoader
from data_loader import IndiaDataLoader
from database_connector import DatabaseConnector

class IntegratedDataPipeline:
    def __init__(self):
        # Initialize all data sources
        self.odp_api = OpenDataPortalAPI(st.secrets["ODP_API_KEY"])
        self.census = CensusDataFetcher()
        self.mospi = MOSPIDataLoader()
        self.loader = IndiaDataLoader()
        self.db = DatabaseConnector(**st.secrets["database"])
    
    def fetch_all_sources(self):
        """
        Fetch data from all sources
        """
        sources = {}
        
        # Open Data Portal
        sources['odp'] = self.odp_api.fetch_dataset('amenities-id')
        
        # Census
        sources['census'] = self.census.download_latest()
        
        # MOSPI
        sources['mospi'] = self.mospi.download_hces_report('latest')
        
        return sources
    
    def process_pipeline(self):
        """
        Complete data processing pipeline
        """
        # 1. Fetch from all sources
        raw_data = self.fetch_all_sources()
        
        # 2. Merge sources
        merged = self.loader.merge_multiple_sources(raw_data)
        
        # 3. Preprocess
        processed = self.loader.preprocess_amenities_data(merged)
        
        # 4. Calculate BNI
        final = self.loader.calculate_bni_score(processed)
        
        # 5. Save to database
        self.db.update_data(final)
        
        # 6. Return for dashboard
        return final

# Usage in dashboard
@st.cache_data(ttl=86400)
def load_integrated_data():
    pipeline = IntegratedDataPipeline()
    return pipeline.process_pipeline()

# In main dashboard:
df = load_integrated_data()
```

---

## 🧪 Testing API Connections

```python
# test_api_connections.py

def test_all_connections():
    """
    Test connections to all data sources
    """
    print("Testing API Connections...")
    print("=" * 50)
    
    # Test Open Data Portal
    try:
        api = OpenDataPortalAPI('test_key')
        result = api.test_connection()
        print("✓ Open Data Portal: Connected")
    except:
        print("✗ Open Data Portal: Failed")
    
    # Test Census
    try:
        census = CensusDataFetcher()
        result = census.test_connection()
        print("✓ Census Website: Connected")
    except:
        print("✗ Census Website: Failed")
    
    # Test Database
    try:
        db = DatabaseConnector(**config)
        result = db.test_connection()
        print("✓ Database: Connected")
    except:
        print("✗ Database: Failed")
    
    print("=" * 50)

if __name__ == "__main__":
    test_all_connections()
```

---

## 📚 Additional Resources

- **Open Data Portal Docs**: https://data.gov.in/help/api
- **Census API Docs**: https://censusindia.gov.in/
- **MOSPI Data**: https://www.mospi.gov.in/
- **DHS API**: https://dhsprogram.com/data/API.cfm

---

**Note**: Always respect rate limits, terms of service, and data usage policies of each source.
