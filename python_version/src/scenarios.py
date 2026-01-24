import pandas as pd
import numpy as np


def calculate_historical_growth_rates(df, columns):
    """
    Calculate historical growth rates for key drivers.
    
    Parameters
    ----------
    df : pd.DataFrame
        Historical data
    columns : list
        Column names to calculate growth for
        
    Returns
    -------
    dict
        Dictionary with growth statistics (mean, median, P25, P75) for each variable
    """
    growth_stats = {}
    
    for col in columns:
        if col in df.columns:
            # Calculate year-over-year growth rates
            growth = df[col].pct_change() * 100
            growth = growth.dropna()
            
            if len(growth) > 0:
                growth_stats[col] = {
                    'mean': growth.mean(),
                    'median': growth.median(),
                    'p25': growth.quantile(0.25),
                    'p50': growth.quantile(0.50),
                    'p75': growth.quantile(0.75),
                    'std': growth.std(),
                    'min': growth.min(),
                    'max': growth.max()
                }
    
    return growth_stats


def generate_scenario_assumptions(df, key_drivers):
    """
    Generate scenario assumptions for key drivers based on historical data.
    Conservative approach: cap growth rates at realistic levels (1-5% CAGR).
    
    Parameters
    ----------
    df : pd.DataFrame
        Historical data
    key_drivers : list
        List of key driver variable names
        
    Returns
    -------
    pd.DataFrame
        Scenario assumptions with growth rates for each driver
    """
    growth_stats = calculate_historical_growth_rates(df, key_drivers)
    
    scenario_data = []
    
    for driver, stats in growth_stats.items():
        # Conservative approach: cap all rates to avoid unrealistic extrapolation
        # Pessimistic: 1%
        pessimistic_rate = 1.0
        
        # Base: 3% (realistic for developing agriculture)
        base_rate = 3.0
        
        # Optimistic: 5% (still conservative but growth-oriented)
        optimistic_rate = 5.0
        
        scenario_data.append({
            'driver': driver,
            'pessimistic_rate': pessimistic_rate,
            'base_rate': base_rate,
            'optimistic_rate': optimistic_rate,
            'historical_mean': stats['mean'],
            'historical_std': stats['std']
        })
    
    return pd.DataFrame(scenario_data)


def project_future_values(df, driver, scenario_type, growth_rate, start_year=2025, end_year=2035):
    """
    Project future values for a driver based on growth rate.
    
    Parameters
    ----------
    df : pd.DataFrame
        Historical data
    driver : str
        Driver variable name
    scenario_type : str
        'pessimistic', 'base', or 'optimistic'
    growth_rate : float
        Annual growth rate (in %)
    start_year : int
        First projection year
    end_year : int
        Last projection year
        
    Returns
    -------
    pd.Series
        Projected values
    """
    # Get last historical value
    last_value = df[df['year'] == df['year'].max()][driver].values[0]
    last_year = df['year'].max()
    
    # Generate future years
    future_years = list(range(start_year, end_year + 1))
    n_years = len(future_years)
    
    # Project values with compound growth
    projected_values = []
    current_value = last_value
    
    for i in range(n_years):
        # Apply growth rate
        current_value = current_value * (1 + growth_rate / 100)
        projected_values.append(current_value)
    
    return pd.Series(projected_values, index=future_years, name=driver)


def generate_full_scenarios(df, key_drivers, start_year=2025, end_year=2030):
    """
    Generate complete scenario dataframes for all key drivers.
    
    Parameters
    ----------
    df : pd.DataFrame
        Historical data with 'year' column
    key_drivers : list
        List of key driver variable names
    start_year : int
        First projection year
    end_year : int
        Last projection year
        
    Returns
    -------
    dict
        Dictionary with 'pessimistic', 'base', 'optimistic' scenario dataframes
    """
    # Generate scenario assumptions
    assumptions = generate_scenario_assumptions(df, key_drivers)
    
    # Initialize scenario dataframes
    future_years = list(range(start_year, end_year + 1))
    
    scenarios = {
        'pessimistic': pd.DataFrame({'year': future_years}),
        'base': pd.DataFrame({'year': future_years}),
        'optimistic': pd.DataFrame({'year': future_years})
    }
    
    # Project each driver
    for _, row in assumptions.iterrows():
        driver = row['driver']
        
        for scenario_type in ['pessimistic', 'base', 'optimistic']:
            growth_rate = row[f'{scenario_type}_rate']
            projected = project_future_values(
                df, driver, scenario_type, growth_rate, start_year, end_year
            )
            scenarios[scenario_type][driver] = projected.values
    
    # For non-key drivers, use simple extrapolation (last value or linear trend)
    all_features = df.columns.drop(['year'])
    other_features = [f for f in all_features if f not in key_drivers and f != 'gross_output']
    
    for feature in other_features:
        if feature in df.columns:
            # Use last known value for all scenarios
            last_value = df[df['year'] == df['year'].max()][feature].values[0]
            
            for scenario_type in scenarios:
                scenarios[scenario_type][feature] = last_value
    
    return scenarios, assumptions


if __name__ == '__main__':
    from data_loader import load_data
    
    df = load_data()
    
    # Define key drivers
    key_drivers = [
        'investment_agri',
        'labor_productivity',
        'gov_support_index',
        'employment_total'
    ]
    
    print("Generating scenarios...")
    scenarios, assumptions = generate_full_scenarios(df, key_drivers)
    
    print("\nScenario assumptions:")
    print(assumptions)
    
    print("\nPessimistic scenario (first 5 years):")
    print(scenarios['pessimistic'].head())
    
    print("\nBase scenario (first 5 years):")
    print(scenarios['base'].head())
    
    print("\nOptimistic scenario (first 5 years):")
    print(scenarios['optimistic'].head())
