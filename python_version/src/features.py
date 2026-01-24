import pandas as pd
import numpy as np


def create_lagged_features(df, columns, lags=[1, 2]):
    """
    Create lagged features for specified columns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with time series data
    columns : list
        Column names to create lags for
    lags : list, default=[1, 2]
        Number of periods to lag
        
    Returns
    -------
    pd.DataFrame
        Dataframe with added lagged columns
    """
    df_lagged = df.copy()
    
    for col in columns:
        if col in df.columns:
            for lag in lags:
                df_lagged[f'{col}_lag{lag}'] = df[col].shift(lag)
    
    return df_lagged


def create_growth_rates(df, columns):
    """
    Calculate year-over-year growth rates.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    columns : list
        Columns to calculate growth rates for
        
    Returns
    -------
    pd.DataFrame
        Dataframe with added growth rate columns
    """
    df_growth = df.copy()
    
    for col in columns:
        if col in df.columns:
            df_growth[f'{col}_growth'] = df[col].pct_change() * 100
    
    return df_growth


def create_indexed_features(df, columns, base_year=2015):
    """
    Create indexed features with base year = 100.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    columns : list
        Columns to index
    base_year : int, default=2015
        Base year for indexation
        
    Returns
    -------
    pd.DataFrame
        Dataframe with indexed columns
    """
    df_indexed = df.copy()
    
    base_values = df[df['year'] == base_year][columns].iloc[0]
    
    for col in columns:
        if col in df.columns:
            df_indexed[f'{col}_index'] = (df[col] / base_values[col]) * 100
    
    return df_indexed


def generate_all_features(df, feature_columns):
    """
    Generate all feature engineering transformations.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with raw data
    feature_columns : list
        List of base feature columns
        
    Returns
    -------
    pd.DataFrame
        Dataframe with all engineered features
    """
    df_features = df.copy()
    
    # Create lags for key variables
    key_vars = ['investment_agri', 'labor_productivity', 'employment_total', 'gross_output']
    df_features = create_lagged_features(df_features, key_vars, lags=[1, 2])
    
    # Create growth rates
    growth_vars = ['gross_output', 'investment_agri', 'labor_productivity', 'net_profit']
    df_features = create_growth_rates(df_features, growth_vars)
    
    # Create indexed features
    index_vars = ['gross_output', 'investment_agri', 'labor_productivity']
    df_features = create_indexed_features(df_features, index_vars, base_year=2015)
    
    return df_features


if __name__ == '__main__':
    from data_loader import load_data, get_feature_columns
    
    df = load_data()
    features = get_feature_columns()
    
    df_enhanced = generate_all_features(df, features)
    print("\nEnhanced dataset shape:", df_enhanced.shape)
    print("\nNew columns created:")
    new_cols = [c for c in df_enhanced.columns if c not in df.columns]
    print(new_cols)
