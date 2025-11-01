"""
Data Loader Module for India Basic Amenities Analysis
======================================================
This module handles loading data from various official sources:
- Census of India
- NSSO Surveys
- NFHS Data
- Open Government Data Portal
"""

import pandas as pd
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')


class IndiaDataLoader:
    """
    Loads and preprocesses data from official Indian government sources.
    """
    
    def __init__(self):
        """Initialize data loader with source URLs."""
        self.sources = {
            'census_2011': 'https://censusindia.gov.in/census.website/data/census-tables',
            'open_data_portal': 'https://data.gov.in/',
            'mospi': 'https://www.mospi.gov.in/',
            'nfhs': 'http://rchiips.org/nfhs/'
        }
        
    def load_census_data(self, filepath_or_url):
        """
        Load Census of India data.
        
        Parameters:
        -----------
        filepath_or_url : str
            Path to local file or URL to Census data
            
        Returns:
        --------
        pd.DataFrame
            Processed Census data
        """
        try:
            # Try reading as CSV
            df = pd.read_csv(filepath_or_url)
            print(f"✓ Successfully loaded Census data: {len(df)} records")
            return df
        except Exception as e:
            print(f"✗ Error loading Census data: {e}")
            return None
    
    def load_nsso_hces_data(self, filepath_or_url):
        """
        Load NSSO Household Consumption Expenditure Survey data.
        
        Parameters:
        -----------
        filepath_or_url : str
            Path to NSSO HCES data file
            
        Returns:
        --------
        pd.DataFrame
            HCES data
        """
        try:
            # NSSO data often comes in Excel format
            df = pd.read_excel(filepath_or_url)
            print(f"✓ Successfully loaded NSSO data: {len(df)} records")
            return df
        except:
            try:
                df = pd.read_csv(filepath_or_url)
                print(f"✓ Successfully loaded NSSO data: {len(df)} records")
                return df
            except Exception as e:
                print(f"✗ Error loading NSSO data: {e}")
                return None
    
    def load_nfhs_data(self, filepath_or_url):
        """
        Load National Family Health Survey data.
        
        Parameters:
        -----------
        filepath_or_url : str
            Path to NFHS data file
            
        Returns:
        --------
        pd.DataFrame
            NFHS data
        """
        try:
            df = pd.read_csv(filepath_or_url)
            print(f"✓ Successfully loaded NFHS data: {len(df)} records")
            return df
        except Exception as e:
            print(f"✗ Error loading NFHS data: {e}")
            return None
    
    def load_from_open_data_portal(self, dataset_id):
        """
        Load data from India's Open Government Data Portal.
        
        Parameters:
        -----------
        dataset_id : str
            Dataset identifier from data.gov.in
            
        Returns:
        --------
        pd.DataFrame
            Data from portal
        """
        try:
            # Construct API URL (example structure)
            api_url = f"https://api.data.gov.in/resource/{dataset_id}"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                df = pd.read_json(StringIO(response.text))
                print(f"✓ Successfully loaded data from portal: {len(df)} records")
                return df
            else:
                print(f"✗ API request failed with status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error loading from Open Data Portal: {e}")
            return None
    
    def preprocess_amenities_data(self, df, source_type='census'):
        """
        Preprocess and standardize amenities data from various sources.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw data
        source_type : str
            Type of source ('census', 'nsso', 'nfhs')
            
        Returns:
        --------
        pd.DataFrame
            Processed and standardized data
        """
        if df is None:
            return None
        
        processed_df = df.copy()
        
        # Standardize column names
        column_mapping = {
            # Water indicators
            'piped_water': 'Piped_Water_Access',
            'safe_water': 'Safe_Drinking_Water',
            'water_access': 'Water_Within_Premises',
            
            # Sanitation indicators
            'toilet': 'Toilet_Access',
            'latrine': 'Toilet_Access',
            'septic_tank': 'Septic_Tank_Access',
            
            # Housing indicators
            'pucca_house': 'Pucca_Housing',
            'electricity': 'Electricity_Access',
            'lpg': 'LPG_Access',
            
            # Geographic
            'state_name': 'State',
            'district': 'District',
            'area': 'Area_Type'
        }
        
        # Apply column mapping (case-insensitive)
        for old_name, new_name in column_mapping.items():
            matching_cols = [col for col in processed_df.columns if old_name.lower() in col.lower()]
            if matching_cols:
                processed_df.rename(columns={matching_cols[0]: new_name}, inplace=True)
        
        # Ensure numeric types for indicator columns
        numeric_columns = ['Piped_Water_Access', 'Safe_Drinking_Water', 'Toilet_Access',
                          'Pucca_Housing', 'Electricity_Access', 'LPG_Access']
        
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
        
        # Remove rows with too many missing values
        processed_df = processed_df.dropna(thresh=len(processed_df.columns) * 0.5)
        
        print(f"✓ Data preprocessed: {len(processed_df)} records retained")
        
        return processed_df
    
    def calculate_bni_score(self, df):
        """
        Calculate Bare Necessities Index (BNI) score.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Data with amenity indicators
            
        Returns:
        --------
        pd.DataFrame
            Data with BNI_Score column added
        """
        if df is None:
            return None
        
        result_df = df.copy()
        
        # Define weights (based on Economic Survey methodology)
        weights = {
            'Piped_Water_Access': 0.15,
            'Safe_Drinking_Water': 0.15,
            'Toilet_Access': 0.20,
            'Pucca_Housing': 0.15,
            'Electricity_Access': 0.15,
            'LPG_Access': 0.10,
            'Food_Secure_Households': 0.10
        }
        
        # Calculate BNI
        result_df['BNI_Score'] = 0
        
        for indicator, weight in weights.items():
            if indicator in result_df.columns:
                result_df['BNI_Score'] += result_df[indicator].fillna(0) * weight
        
        # Normalize to 0-1 scale
        result_df['BNI_Score'] = result_df['BNI_Score'] / 100
        
        print(f"✓ BNI Score calculated successfully")
        
        return result_df
    
    def merge_multiple_sources(self, dataframes_dict):
        """
        Merge data from multiple sources.
        
        Parameters:
        -----------
        dataframes_dict : dict
            Dictionary with source names as keys and dataframes as values
            
        Returns:
        --------
        pd.DataFrame
            Merged dataset
        """
        if not dataframes_dict:
            return None
        
        # Start with first dataframe
        merged_df = list(dataframes_dict.values())[0].copy()
        
        # Merge with others
        for name, df in list(dataframes_dict.items())[1:]:
            try:
                merged_df = pd.merge(
                    merged_df, 
                    df, 
                    on=['State', 'Year', 'Area_Type'], 
                    how='outer',
                    suffixes=('', f'_{name}')
                )
                print(f"✓ Merged {name} data")
            except Exception as e:
                print(f"✗ Could not merge {name}: {e}")
        
        return merged_df
    
    def export_processed_data(self, df, output_path):
        """
        Export processed data to CSV.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Data to export
        output_path : str
            Path for output file
        """
        try:
            df.to_csv(output_path, index=False)
            print(f"✓ Data exported to {output_path}")
        except Exception as e:
            print(f"✗ Error exporting data: {e}")


# Example usage
if __name__ == "__main__":
    print("India Data Loader Module")
    print("=" * 50)
    
    loader = IndiaDataLoader()
    
    print("\nAvailable data sources:")
    for name, url in loader.sources.items():
        print(f"  • {name}: {url}")
    
    print("\nUsage Examples:")
    print("-" * 50)
    
    print("""
# Example 1: Load Census data
census_data = loader.load_census_data('path/to/census_data.csv')

# Example 2: Load NSSO HCES data
hces_data = loader.load_nsso_hces_data('path/to/hces_data.xlsx')

# Example 3: Preprocess data
processed_data = loader.preprocess_amenities_data(census_data, source_type='census')

# Example 4: Calculate BNI scores
data_with_bni = loader.calculate_bni_score(processed_data)

# Example 5: Merge multiple sources
merged_data = loader.merge_multiple_sources({
    'census': census_data,
    'nsso': hces_data
})

# Example 6: Export processed data
loader.export_processed_data(data_with_bni, 'processed_amenities_data.csv')
    """)
