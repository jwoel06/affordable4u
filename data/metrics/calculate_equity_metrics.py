#!/usr/bin/env python3
"""
Equity Metrics Calculator for College ROI Datathon
Calculates all social good metrics and exports for Tableau
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

def load_and_merge_data():
    """Load and merge the two datasets"""
    print("Loading datasets...")
    
    # Load data
    college = pd.read_csv('/mnt/user-data/uploads/College_Results_View_2021_Data_Dump_for_Export_xlsx_-_College_Results_View_2021_Data_.csv')
    afford = pd.read_csv('/mnt/user-data/uploads/Affordability_Gap_Data_AY2022-23_2_17_25_xlsx_-_Affordability_latest_02-17-25_1.csv')
    
    # Merge on institution name
    merged = pd.merge(
        college,
        afford,
        on='Institution Name',
        how='inner',
        suffixes=('', '_afford')
    )
    
    print(f"Merged {len(merged)} institutions")
    return merged

def calculate_basic_metrics(df):
    """Calculate basic financial and demographic metrics"""
    print("Calculating basic metrics...")
    
    # Basic financials
    df['earnings_10yr'] = df['Median Earnings of Students Working and Not Enrolled 10 Years After Entry']
    df['median_debt'] = df['Median Debt of Completers']
    df['net_price'] = df['Net Price']
    df['total_cost_4yr'] = df['net_price'] * 4
    
    # Basic ROI
    df['basic_roi'] = (df['earnings_10yr'] * 10 - df['median_debt']) / (df['total_cost_4yr'] + 1)
    df['payback_years'] = df['median_debt'] / (df['earnings_10yr'] - 15000 + 1)  # Assume $15k living expenses
    
    # Demographics
    df['black_pct'] = df['Percent of Black or African American Undergraduates']
    df['latino_pct'] = df['Percent of Latino Undergraduates'] 
    df['native_pct'] = df['Percent of American Indian or Alaska Native Undergraduates']
    df['asian_pct'] = df['Percent of Asian Undergraduates']
    df['white_pct'] = df['Percent of White Undergraduates']
    
    # URM percentage
    df['urm_pct'] = df['black_pct'] + df['latino_pct'] + df['native_pct']
    
    # Economic indicators
    df['pell_pct'] = df['Percent of First-Time, Full-Time Undergraduates Awarded Pell Grants']
    
    # Affordability
    df['work_hours_needed'] = df['Weekly Hours to Close Gap']
    df['affordability_gap'] = df['Affordability Gap (net price minus income earned working 10 hrs at min wage)']
    df['parent_afford_gap'] = df['Student Parent Affordability Gap: Center-Based Care']
    
    return df

def calculate_graduation_equity_metrics(df):
    """Calculate racial equity in graduation rates"""
    print("Calculating graduation equity metrics...")
    
    # Map graduation rate columns
    grad_cols = {
        'black_grad': "Bachelor's Degree Graduation Rate Within 6 Years - Black, Non-Latino",
        'latino_grad': "Bachelor's Degree Graduation Rate Within 6 Years - Latino",
        'white_grad': "Bachelor's Degree Graduation Rate Within 6 Years - White Non-Latino",
        'asian_grad': "Bachelor's Degree Graduation Rate Within 6 Years - Asian",
        'overall_grad': "Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total"
    }
    
    # Add available graduation rates
    for key, col in grad_cols.items():
        if col in df.columns:
            df[key] = df[col]
    
    # Calculate graduation gaps (negative = URM graduates less)
    if 'white_grad' in df.columns:
        df['black_white_grad_gap'] = df['black_grad'] - df['white_grad']
        df['latino_white_grad_gap'] = df['latino_grad'] - df['white_grad']
        
        # URM average graduation rate (weighted by enrollment)
        df['urm_grad_rate'] = (
            (df['black_grad'] * df['black_pct'] + 
             df['latino_grad'] * df['latino_pct']) /
            (df['black_pct'] + df['latino_pct'] + 0.001)
        )
        
        # Overall equity gap
        df['overall_equity_gap'] = df['urm_grad_rate'] - df['white_grad']
        
        # Racial equity score (100 = perfect equity)
        df['racial_equity_score'] = 100 - abs(df['overall_equity_gap'])
        df['racial_equity_score'] = df['racial_equity_score'].clip(0, 100)
        
        # Disparate impact ratio (legal threshold = 0.8)
        df['disparate_impact_ratio'] = df['urm_grad_rate'] / (df['white_grad'] + 0.001)
        
        # Categorize equity status
        df['equity_status'] = pd.cut(
            df['disparate_impact_ratio'],
            bins=[0, 0.6, 0.8, 0.95, 1.05, 999],
            labels=['Severe Disparity', 'Actionable Disparity', 
                   'Approaching Equity', 'Equitable', 'URM Outperforming']
        )
        
        # Flag schools needing intervention
        df['needs_intervention'] = (df['disparate_impact_ratio'] < 0.8).astype(int)
    
    return df

def calculate_economic_mobility_metrics(df):
    """Calculate economic mobility and social impact metrics"""
    print("Calculating economic mobility metrics...")
    
    # Pell graduation success
    df['pell_grad_6yr'] = df['Percent Full-time, First-time, Pell Grant Recipients Receiving an Award - 6 Years']
    
    # Economic mobility index
    df['economic_mobility_index'] = (
        (df['pell_pct'] / 100) *  # Access for low-income
        (df['pell_grad_6yr'] / (df['overall_grad'] + 0.001)) *  # Relative success
        (df['earnings_10yr'] / df['earnings_10yr'].median()) *  # Relative earnings
        (df['median_debt'].median() / (df['median_debt'] + 1))  # Inverse debt burden
    )
    
    # Mobility percentile
    df['mobility_percentile'] = df['economic_mobility_index'].rank(pct=True) * 100
    
    # Low-income value score
    df['low_income_value'] = (
        df['earnings_10yr'] - df['median_debt']
    ) * (df['pell_pct'] / 100)
    
    return df

def calculate_affordability_metrics(df):
    """Calculate true affordability metrics"""
    print("Calculating affordability metrics...")
    
    # Affordability score (100 = very affordable)
    df['affordability_score'] = np.where(
        df['work_hours_needed'].notna(),
        100 * (20 / (df['work_hours_needed'] + 1)),  # 20 hrs/week is sustainable
        50
    )
    df['affordability_score'] = df['affordability_score'].clip(0, 100)
    
    # Parent affordability score
    df['parent_hours_needed'] = df['Student Parent Affordability Gap: Center-Based Care'] / (15 * 52)  # $15/hr min wage
    df['parent_affordability_score'] = 100 * (15 / (df['parent_hours_needed'] + 1))
    df['parent_affordability_score'] = df['parent_affordability_score'].clip(0, 100)
    
    # Affordability categories
    df['afford_category'] = pd.cut(
        df['work_hours_needed'],
        bins=[0, 10, 20, 30, 999],
        labels=['Very Affordable', 'Affordable', 'Challenging', 'Unsustainable']
    )
    
    # Crisis flag
    df['affordability_crisis'] = (df['work_hours_needed'] > 30).astype(int)
    
    return df

def calculate_msi_metrics(df):
    """Calculate Minority Serving Institution metrics"""
    print("Calculating MSI metrics...")
    
    # MSI flags
    df['is_hbcu'] = (df['HBCU'] == 'X').astype(int)
    df['is_hsi'] = (df['HSI'] == 'X').astype(int)
    df['is_tribal'] = (df['TRIBAL'] == 'X').astype(int)
    df['is_pbi'] = (df['PBI'] == 'X').astype(int)
    
    # Any MSI
    df['is_msi'] = (
        df['is_hbcu'] | df['is_hsi'] | 
        df['is_tribal'] | df['is_pbi']
    ).astype(int)
    
    # MSI excellence scores
    df['hbcu_excellence'] = df['is_hbcu'] * df['black_grad'] * df['basic_roi']
    df['hsi_excellence'] = df['is_hsi'] * df['latino_grad'] * df['basic_roi']
    
    return df

def calculate_composite_scores(df):
    """Calculate final composite equity-value scores"""
    print("Calculating composite scores...")
    
    # Normalize components to 0-100
    scaler = MinMaxScaler(feature_range=(0, 100))
    
    # ROI score
    roi_values = df[['basic_roi']].fillna(0)
    df['roi_score'] = scaler.fit_transform(roi_values)
    
    # Debt score (inverted - lower is better)
    debt_values = df[['median_debt']].fillna(df['median_debt'].median())
    df['debt_score'] = 100 - scaler.fit_transform(debt_values)
    
    # Earnings score
    earnings_values = df[['earnings_10yr']].fillna(df['earnings_10yr'].median())
    df['earnings_score'] = scaler.fit_transform(earnings_values)
    
    # Work hours score (inverted - fewer is better)
    hours_values = df[['work_hours_needed']].fillna(40)
    df['hours_score'] = 100 - scaler.fit_transform(hours_values)
    
    # === Main Composite Score ===
    # Equity-Adjusted Value Score (weighs social good heavily)
    df['equity_value_score'] = (
        df['roi_score'] * 0.15 +           # Basic ROI: 15%
        df['debt_score'] * 0.10 +          # Low debt: 10%
        df['earnings_score'] * 0.15 +      # Good outcomes: 15%
        df['racial_equity_score'].fillna(50) * 0.25 +  # Racial equity: 25%
        df['mobility_percentile'].fillna(50) * 0.20 +  # Economic mobility: 20%
        df['affordability_score'] * 0.15   # True affordability: 15%
    )
    
    # Alternative scoring for schools without graduation data
    df['basic_equity_score'] = (
        df['roi_score'] * 0.25 +
        df['debt_score'] * 0.20 +
        df['earnings_score'] * 0.25 +
        df['affordability_score'] * 0.30
    )
    
    # Use alternative if main score is missing
    df['final_equity_score'] = df['equity_value_score'].fillna(df['basic_equity_score'])
    
    # Rank schools
    df['equity_rank'] = df['final_equity_score'].rank(ascending=False, method='min')
    
    return df

def identify_special_categories(df):
    """Identify special categories of schools"""
    print("Identifying special school categories...")
    
    # Equity Champions
    df['equity_champion'] = (
        (abs(df['overall_equity_gap']) < 5) & 
        (df['pell_pct'] > 40) &
        (df['work_hours_needed'] < 20)
    ).astype(int)
    
    # Hidden Gems
    df['hidden_gem'] = (
        (df['median_debt'] < df['median_debt'].quantile(0.25)) &
        (df['earnings_10yr'] > df['earnings_10yr'].quantile(0.75)) &
        (df['racial_equity_score'] > 80) &
        (df['work_hours_needed'] < 20)
    ).astype(int)
    
    # Crisis Schools
    df['crisis_school'] = (
        ((df['work_hours_needed'] > 35) | 
         (df['disparate_impact_ratio'] < 0.6) |
         (df['median_debt'] > df['earnings_10yr']))
    ).astype(int)
    
    # High Impact Schools (serve many URM students well)
    df['high_impact'] = (
        (df['urm_pct'] > 50) &
        (df['overall_grad'] > 50) &
        (df['earnings_10yr'] > 35000)
    ).astype(int)
    
    return df

def create_tableau_export(df):
    """Create clean export for Tableau"""
    print("Preparing Tableau export...")
    
    # Select columns for Tableau
    tableau_cols = [
        # Identifiers
        'Institution Name', 'State Abbreviation', 'Institution Type', 'Sector Name',
        
        # Demographics
        'urm_pct', 'black_pct', 'latino_pct', 'asian_pct', 'white_pct', 'pell_pct',
        
        # Outcomes
        'earnings_10yr', 'median_debt', 'net_price', 'basic_roi', 'payback_years',
        
        # Graduation equity
        'black_grad', 'latino_grad', 'white_grad', 'overall_grad',
        'black_white_grad_gap', 'latino_white_grad_gap', 'overall_equity_gap',
        'racial_equity_score', 'disparate_impact_ratio', 'equity_status',
        
        # Economic mobility
        'economic_mobility_index', 'mobility_percentile', 'low_income_value',
        
        # Affordability
        'work_hours_needed', 'affordability_gap', 'affordability_score',
        'parent_afford_gap', 'parent_affordability_score', 'afford_category',
        
        # MSI status
        'is_msi', 'is_hbcu', 'is_hsi', 'hbcu_excellence', 'hsi_excellence',
        
        # Composite scores
        'equity_value_score', 'final_equity_score', 'equity_rank',
        
        # Categories
        'equity_champion', 'hidden_gem', 'crisis_school', 'high_impact',
        'needs_intervention', 'affordability_crisis',
        
        # Additional context
        'Total Enrollment', 'Control of Institution',
        'City', 'Latitude', 'Longitude'  # For mapping
    ]
    
    # Keep only available columns
    available_cols = [col for col in tableau_cols if col in df.columns]
    tableau_df = df[available_cols].copy()
    
    # Clean institution names
    tableau_df['Institution Name'] = tableau_df['Institution Name'].str.strip()
    
    # Round numeric columns for cleaner display
    numeric_cols = tableau_df.select_dtypes(include=[np.number]).columns
    tableau_df[numeric_cols] = tableau_df[numeric_cols].round(2)
    
    return tableau_df

def generate_insights(df):
    """Generate key insights for presentation"""
    print("\n" + "="*60)
    print("KEY INSIGHTS FOR PRESENTATION")
    print("="*60)
    
    # Clean data for insights
    clean_df = df.dropna(subset=['earnings_10yr', 'median_debt', 'net_price'])
    
    print("\n📊 EQUITY GAPS:")
    if 'disparate_impact_ratio' in df.columns:
        severe = (df['disparate_impact_ratio'] < 0.6).sum()
        actionable = ((df['disparate_impact_ratio'] >= 0.6) & (df['disparate_impact_ratio'] < 0.8)).sum()
        equitable = (df['disparate_impact_ratio'] >= 0.95).sum()
        
        print(f"  - {severe} schools show SEVERE disparate impact (<60% rule)")
        print(f"  - {actionable} schools need intervention (60-80% rule)")
        print(f"  - Only {equitable} schools are truly equitable (>95%)")
    
    print("\n💰 AFFORDABILITY CRISIS:")
    if 'work_hours_needed' in df.columns:
        print(f"  - Median work hours needed: {df['work_hours_needed'].median():.0f} hrs/week")
        crisis = (df['work_hours_needed'] > 30).sum()
        print(f"  - {crisis} schools require >30 hrs/week (unsustainable)")
        parent_crisis = (df['parent_afford_gap'] > 30000).sum()
        print(f"  - {parent_crisis} schools have >$30k parent affordability gap")
    
    print("\n🏆 TOP EQUITY CHAMPIONS:")
    if 'equity_champion' in df.columns:
        champions = df[df['equity_champion'] == 1]
        print(f"  - {len(champions)} schools identified as equity champions")
        if len(champions) > 0:
            top_champion = champions.nlargest(1, 'final_equity_score').iloc[0]
            print(f"  - #1: {top_champion['Institution Name']}")
    
    print("\n💎 HIDDEN GEMS:")
    if 'hidden_gem' in df.columns:
        gems = df[df['hidden_gem'] == 1]
        print(f"  - {len(gems)} hidden gem schools found")
        if len(gems) > 0:
            top_gem = gems.nlargest(1, 'final_equity_score').iloc[0]
            print(f"  - Example: {top_gem['Institution Name']}")
            print(f"    Debt: ${top_gem['median_debt']:,.0f}, Earnings: ${top_gem['earnings_10yr']:,.0f}")
    
    print("\n🎓 MSI PERFORMANCE:")
    if 'is_msi' in df.columns:
        msi_schools = df[df['is_msi'] == 1]
        non_msi = df[df['is_msi'] == 0]
        
        if len(msi_schools) > 0:
            print(f"  - {len(msi_schools)} MSIs in dataset")
            print(f"  - MSI avg debt: ${msi_schools['median_debt'].median():,.0f}")
            print(f"  - Non-MSI avg debt: ${non_msi['median_debt'].median():,.0f}")
            
            if 'racial_equity_score' in df.columns:
                print(f"  - MSI avg equity score: {msi_schools['racial_equity_score'].mean():.1f}")
                print(f"  - Non-MSI avg equity score: {non_msi['racial_equity_score'].mean():.1f}")

def main():
    """Main execution function"""
    print("Starting Equity Metrics Calculation...")
    print("="*60)
    
    # Load data
    df = load_and_merge_data()
    
    # Calculate all metrics
    df = calculate_basic_metrics(df)
    df = calculate_graduation_equity_metrics(df)
    df = calculate_economic_mobility_metrics(df)
    df = calculate_affordability_metrics(df)
    df = calculate_msi_metrics(df)
    df = calculate_composite_scores(df)
    df = identify_special_categories(df)
    
    # Create Tableau export
    tableau_df = create_tableau_export(df)
    
    # Save files
    print("\nSaving files...")
    
    # Main Tableau file
    tableau_df.to_csv('/mnt/user-data/outputs/tableau_equity_metrics.csv', index=False)
    print("  ✓ tableau_equity_metrics.csv - Main file for Tableau")
    
    # Top schools for different categories
    categories = {
        'equity_champions': df[df['equity_champion'] == 1].nlargest(50, 'final_equity_score'),
        'hidden_gems': df[df['hidden_gem'] == 1].nlargest(50, 'final_equity_score'),
        'crisis_schools': df[df['crisis_school'] == 1].nlargest(50, 'urm_pct'),
        'top_msi': df[df['is_msi'] == 1].nlargest(50, 'final_equity_score'),
        'top_overall': df.nlargest(100, 'final_equity_score')
    }
    
    for name, data in categories.items():
        if len(data) > 0:
            data.to_csv(f'/mnt/user-data/outputs/{name}.csv', index=False)
            print(f"  ✓ {name}.csv - {len(data)} schools")
    
    # Generate insights
    generate_insights(df)
    
    print("\n" + "="*60)
    print("✅ COMPLETE! Files ready for Tableau import")
    print("="*60)
    print("\nNext steps:")
    print("1. Import tableau_equity_metrics.csv into Tableau")
    print("2. Create visualizations from the guide")
    print("3. Use category files for focused dashboards")
    print("4. Add calculated fields from the guide")

if __name__ == "__main__":
    main()
