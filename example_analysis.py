"""
Example Analysis Scripts
========================
This file demonstrates how to perform various analyses using the India Amenities data.
Run these examples to understand the capabilities of the system.
"""

import pandas as pd
import numpy as np
from india_amenities_dashboard import IndiaAmenitiesAnalyzer
import plotly.express as px


def example_1_identify_priority_states():
    """
    Example 1: Identify states with lowest access to basic amenities
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Identifying Priority States")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    # Get latest year data
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year]
    
    # Calculate average BNI by state
    state_bni = latest_data.groupby('State').agg({
        'BNI_Score': 'mean',
        'Population': 'sum',
        'Piped_Water_Access': 'mean',
        'Toilet_Access': 'mean',
        'Pucca_Housing': 'mean'
    }).round(2)
    
    # Get bottom 10 states
    priority_states = state_bni.nsmallest(10, 'BNI_Score')
    
    print(f"\n📊 Top 10 Priority States for Intervention ({latest_year}):\n")
    print(priority_states.to_string())
    
    print("\n💡 Insights:")
    print(f"   • Lowest BNI Score: {priority_states['BNI_Score'].min():.2f}")
    print(f"   • Highest BNI in bottom 10: {priority_states['BNI_Score'].max():.2f}")
    print(f"   • Total population in priority states: {priority_states['Population'].sum()/1000000:.1f}M")
    
    return priority_states


def example_2_rural_urban_disparity():
    """
    Example 2: Analyze rural-urban disparity in access to amenities
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Rural-Urban Disparity Analysis")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year]
    
    # Compare rural vs urban
    comparison = latest_data.groupby('Area_Type').agg({
        'BNI_Score': 'mean',
        'Piped_Water_Access': 'mean',
        'Toilet_Access': 'mean',
        'Pucca_Housing': 'mean',
        'Electricity_Access': 'mean',
        'LPG_Access': 'mean'
    }).round(2)
    
    print(f"\n📊 Rural vs Urban Access Rates ({latest_year}):\n")
    print(comparison.to_string())
    
    # Calculate gaps
    print("\n📏 Urban-Rural Gaps (percentage points):\n")
    gaps = comparison.loc['Urban'] - comparison.loc['Rural']
    for indicator, gap in gaps.items():
        print(f"   • {indicator:25s}: {gap:6.2f}%")
    
    # State with largest gap
    state_gaps = latest_data.pivot_table(
        values='BNI_Score',
        index='State',
        columns='Area_Type'
    )
    state_gaps['Gap'] = state_gaps['Urban'] - state_gaps['Rural']
    largest_gap_state = state_gaps['Gap'].idxmax()
    
    print(f"\n💡 Insights:")
    print(f"   • State with largest rural-urban gap: {largest_gap_state}")
    print(f"   • Gap size: {state_gaps.loc[largest_gap_state, 'Gap']:.2f}")
    
    return comparison


def example_3_progress_tracking():
    """
    Example 3: Track progress over time for key indicators
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Progress Tracking Over Time")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    # Calculate year-over-year improvements
    progress = df.groupby('Year').agg({
        'BNI_Score': 'mean',
        'Piped_Water_Access': 'mean',
        'Toilet_Access': 'mean',
        'Pucca_Housing': 'mean',
        'Electricity_Access': 'mean'
    }).round(2)
    
    print(f"\n📈 National Average Progress:\n")
    print(progress.to_string())
    
    # Calculate absolute improvements
    print(f"\n📊 Absolute Improvements (percentage points):\n")
    first_year = progress.index.min()
    last_year = progress.index.max()
    
    for indicator in progress.columns:
        improvement = progress.loc[last_year, indicator] - progress.loc[first_year, indicator]
        annual_rate = improvement / (last_year - first_year)
        print(f"   • {indicator:25s}: +{improvement:5.2f}% (+{annual_rate:.2f}% per year)")
    
    # Fastest improving states
    state_improvement = df.pivot_table(
        values='BNI_Score',
        index='State',
        columns='Year'
    )
    state_improvement['Total_Improvement'] = state_improvement[last_year] - state_improvement[first_year]
    fastest_improving = state_improvement.nlargest(5, 'Total_Improvement')
    
    print(f"\n🚀 Fastest Improving States (BNI Score):\n")
    print(fastest_improving[['Total_Improvement']].to_string())
    
    return progress


def example_4_calculate_intervention_needs():
    """
    Example 4: Calculate specific intervention needs (households requiring support)
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Intervention Needs Calculation")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    metrics, latest_data = analyzer.calculate_deprivation_metrics(df)
    
    print(f"\n🏠 Households Lacking Basic Amenities:\n")
    print(f"   • Without Safe Water:       {metrics['total_without_water']/1000000:8.2f} Million")
    print(f"   • Without Toilet:           {metrics['total_without_toilet']/1000000:8.2f} Million")
    print(f"   • Without Pucca Housing:    {metrics['total_without_housing']/1000000:8.2f} Million")
    print(f"   • Without Electricity:      {metrics['total_without_electricity']/1000000:8.2f} Million")
    print(f"   • Food Insecure:            {metrics['total_food_insecure']/1000000:8.2f} Million")
    
    # Budget estimation (example costs per household)
    cost_estimates = {
        'water': 15000,  # Rs. per household
        'toilet': 12000,
        'housing': 120000,
        'electricity': 5000
    }
    
    print(f"\n💰 Estimated Budget Requirements (in Crores):\n")
    print(f"   • Water Infrastructure:     ₹{(metrics['total_without_water'] * cost_estimates['water'])/10000000:10,.2f} Cr")
    print(f"   • Sanitation Facilities:    ₹{(metrics['total_without_toilet'] * cost_estimates['toilet'])/10000000:10,.2f} Cr")
    print(f"   • Housing Support:          ₹{(metrics['total_without_housing'] * cost_estimates['housing'])/10000000:10,.2f} Cr")
    print(f"   • Electricity Connection:   ₹{(metrics['total_without_electricity'] * cost_estimates['electricity'])/10000000:10,.2f} Cr")
    
    total_budget = (
        metrics['total_without_water'] * cost_estimates['water'] +
        metrics['total_without_toilet'] * cost_estimates['toilet'] +
        metrics['total_without_housing'] * cost_estimates['housing'] +
        metrics['total_without_electricity'] * cost_estimates['electricity']
    ) / 10000000
    
    print(f"\n   📊 Total Estimated Budget:  ₹{total_budget:10,.2f} Crores")
    
    return metrics


def example_5_state_level_deep_dive():
    """
    Example 5: Deep dive analysis for a specific state
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: State-Level Deep Dive (Example: Bihar)")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    target_state = 'Bihar'
    state_data = df[df['State'] == target_state]
    
    latest_year = state_data['Year'].max()
    latest = state_data[state_data['Year'] == latest_year]
    
    print(f"\n📊 {target_state} - Current Status ({latest_year}):\n")
    
    rural_data = latest[latest['Area_Type'] == 'Rural'].iloc[0]
    urban_data = latest[latest['Area_Type'] == 'Urban'].iloc[0]
    
    print(f"{'Indicator':<30} {'Rural':>10} {'Urban':>10} {'Gap':>10}")
    print("-" * 62)
    
    indicators = ['BNI_Score', 'Piped_Water_Access', 'Toilet_Access', 
                 'Pucca_Housing', 'Electricity_Access', 'LPG_Access']
    
    for indicator in indicators:
        rural_val = rural_data[indicator]
        urban_val = urban_data[indicator]
        gap = urban_val - rural_val
        print(f"{indicator:<30} {rural_val:>10.2f} {urban_val:>10.2f} {gap:>10.2f}")
    
    # Progress over time
    print(f"\n📈 {target_state} - Progress Over Time:\n")
    progress = state_data.groupby('Year')['BNI_Score'].mean()
    
    for year in progress.index:
        print(f"   • {year}: BNI = {progress[year]:.3f}")
    
    improvement = progress.iloc[-1] - progress.iloc[0]
    print(f"\n💡 Total BNI Improvement: +{improvement:.3f} ({improvement/progress.iloc[0]*100:.1f}%)")
    
    return state_data


def example_6_correlation_analysis():
    """
    Example 6: Correlation between amenities and socio-economic indicators
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Correlation Analysis")
    print("="*70)
    
    analyzer = IndiaAmenitiesAnalyzer()
    df = analyzer.generate_sample_data()
    
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year]
    
    # Calculate correlations
    variables = ['BNI_Score', 'MPCE_Rupees', 'Below_Poverty_Line', 
                'Piped_Water_Access', 'Toilet_Access', 'Food_Secure_Households']
    
    correlation_matrix = latest_data[variables].corr()
    
    print(f"\n📊 Correlation Matrix ({latest_year}):\n")
    print(correlation_matrix.round(3).to_string())
    
    # Key insights
    print(f"\n💡 Key Correlations with BNI Score:\n")
    bni_correlations = correlation_matrix['BNI_Score'].drop('BNI_Score').sort_values(ascending=False)
    
    for var, corr in bni_correlations.items():
        direction = "positive" if corr > 0 else "negative"
        strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
        print(f"   • {var:30s}: {corr:6.3f} ({strength} {direction})")
    
    return correlation_matrix


def run_all_examples():
    """
    Run all example analyses
    """
    print("\n" + "="*70)
    print("INDIA BASIC AMENITIES ANALYSIS - EXAMPLE ANALYSES")
    print("="*70)
    print("\nThis script demonstrates various analytical capabilities")
    print("of the India Amenities Dashboard system.\n")
    
    # Run all examples
    example_1_identify_priority_states()
    input("\nPress Enter to continue to next example...")
    
    example_2_rural_urban_disparity()
    input("\nPress Enter to continue to next example...")
    
    example_3_progress_tracking()
    input("\nPress Enter to continue to next example...")
    
    example_4_calculate_intervention_needs()
    input("\nPress Enter to continue to next example...")
    
    example_5_state_level_deep_dive()
    input("\nPress Enter to continue to next example...")
    
    example_6_correlation_analysis()
    
    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Launch the full dashboard: streamlit run india_amenities_dashboard.py")
    print("  2. Load your own data using data_loader.py")
    print("  3. Customize analyses for your specific needs")
    print("\n")


if __name__ == "__main__":
    run_all_examples()
