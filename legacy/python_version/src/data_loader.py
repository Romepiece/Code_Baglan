import pandas as pd
import os


def load_data(filepath='data/processed/agro_dataset_ml.csv'):
    """
    Load prepared agricultural dataset.
    
    Parameters
    ----------
    filepath : str
        Path to the CSV file with prepared data
        
    Returns
    -------
    pd.DataFrame
        Loaded and sorted dataset
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Convert gov_support_index to numeric if it's object type
    if df['gov_support_index'].dtype == 'object':
        df['gov_support_index'] = pd.to_numeric(df['gov_support_index'], errors='coerce')
    
    # Sort by year
    df = df.sort_values('year').reset_index(drop=True)
    
    # Basic checks
    print(f"Dataset shape: {df.shape}")
    print(f"Period: {df['year'].min()} - {df['year'].max()}")
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    
    # Verify target variable exists
    if 'gross_output' not in df.columns:
        raise ValueError("Target variable 'gross_output' not found in dataset")
    
    return df


def get_feature_columns():
    """
    Return list of feature columns as specified in the project.
    
    Returns
    -------
    list
        Feature column names
    """
    return [
        'employment_total',
        'employment_women',
        'labor_productivity',
        'investment_agri',
        'profitability',
        'net_profit',
        'agri_land_area_mha',
        'agri_gdp_share',
        'gov_support_index',
        'poverty_rate',
        'undernourishment_rate',
        'youth_neet_rate',
        'women_land_share',
        'rural_internet_share'
    ]


if __name__ == '__main__':
    df = load_data()
    print("\nAvailable columns:")
    print(df.columns.tolist())
