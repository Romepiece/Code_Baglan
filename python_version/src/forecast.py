"""
Main forecasting pipeline - entry point for the project.

This module orchestrates:
1. Data loading and preparation
2. Model training (econometric and ML)
3. Scenario generation
4. Forecasting with all models across all scenarios
5. Saving results (tables and figures)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import project modules
from data_loader import load_data, get_feature_columns
from econometrics import fit_ols, fit_ardl, fit_dynamic_diff_model
from ml_models import time_split_data, fit_linear_regression, fit_ridge, fit_lasso, fit_elastic_net
from scenarios import generate_full_scenarios
from time_series import predict_arima_scenarios

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Output directories
OUTPUT_DIR = Path('python_version/outputs')
TABLES_DIR = OUTPUT_DIR / 'tables'
FIGURES_DIR = OUTPUT_DIR / 'figures'


def prepare_data_for_models(df, feature_cols):
    """
    Prepare clean data for modeling (drop NaN).
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data
    feature_cols : list
        Feature column names
        
    Returns
    -------
    pd.DataFrame
        Cleaned dataframe
    """
    # Select relevant columns
    model_cols = ['year', 'gross_output'] + feature_cols
    df_clean = df[model_cols].copy()
    
    # Drop rows with NaN
    df_clean = df_clean.dropna()
    
    return df_clean


def train_all_models(df, feature_cols):
    """
    Train all econometric and ML models.
    
    Parameters
    ----------
    df : pd.DataFrame
        Training data
    feature_cols : list
        Feature column names
        
    Returns
    -------
    dict
        Dictionary of trained models
    """
    models = {}
    
    print("Training models...")
    
    # Prepare data
    X = df[feature_cols]
    y = df['gross_output']
    
    # Time-based split for ML models
    X_train, X_test, y_train, y_test = time_split_data(
        df, 'gross_output', feature_cols
    )
    
    # 1. OLS
    print("  - OLS")
    try:
        models['OLS'] = fit_ols(X, y)
    except Exception as e:
        print(f"    OLS failed: {e}")
    
    # 2. Linear Regression
    print("  - Linear Regression")
    try:
        models['LinearRegression'] = fit_linear_regression(X_train, X_test, y_train, y_test)
    except Exception as e:
        print(f"    Linear Regression failed: {e}")
    
    # 3. Ridge
    print("  - Ridge")
    try:
        models['Ridge'] = fit_ridge(X_train, X_test, y_train, y_test, alpha=1.0)
    except Exception as e:
        print(f"    Ridge failed: {e}")
    
    # 4. Lasso
    print("  - Lasso")
    try:
        models['Lasso'] = fit_lasso(X_train, X_test, y_train, y_test, alpha=0.1)
    except Exception as e:
        print(f"    Lasso failed: {e}")
    
    # 5. ElasticNet
    print("  - ElasticNet")
    try:
        models['ElasticNet'] = fit_elastic_net(X_train, X_test, y_train, y_test, alpha=0.5, l1_ratio=0.5)
    except Exception as e:
        print(f"    ElasticNet failed: {e}")
    
    print(f"\nTrained {len(models)} models successfully.")
    
    return models


def forecast_scenarios(models, scenarios, feature_cols):
    """
    Generate forecasts for all scenarios using all models.
    
    Parameters
    ----------
    models : dict
        Trained models
    scenarios : dict
        Scenario dataframes
    feature_cols : list
        Feature column names
        
    Returns
    -------
    pd.DataFrame
        Forecasts with columns: year, scenario, model, gross_output_pred
    """
    forecast_results = []
    
    for scenario_name, scenario_df in scenarios.items():
        print(f"\nForecasting {scenario_name} scenario...")
        
        # Ensure all feature columns are present
        X_future = scenario_df[feature_cols].copy()
        
        for model_name, model_result in models.items():
            try:
                # Get predictions based on model type
                if model_name == 'OLS':
                    # OLS from statsmodels
                    import statsmodels.api as sm
                    X_const = sm.add_constant(X_future)
                    predictions = model_result['model'].predict(X_const)
                else:
                    # sklearn models
                    predictions = model_result['model'].predict(X_future)
                
                # Store results
                for i, year in enumerate(scenario_df['year']):
                    forecast_results.append({
                        'year': year,
                        'scenario': scenario_name,
                        'model': model_name,
                        'gross_output_pred': predictions[i]
                    })
            
            except Exception as e:
                print(f"  Warning: {model_name} forecast failed for {scenario_name}: {e}")
    
    return pd.DataFrame(forecast_results)


def save_results(models, scenarios, forecast_df, assumptions_df, historical_df):
    """
    Save all results to CSV files.
    
    Parameters
    ----------
    models : dict
        Trained models
    scenarios : dict
        Scenario dataframes
    forecast_df : pd.DataFrame
        Forecast results
    assumptions_df : pd.DataFrame
        Scenario assumptions
    historical_df : pd.DataFrame
        Historical data
    """
    print("\nSaving results...")
    
    # 1. Model coefficients
    coef_list = []
    for model_name, model_result in models.items():
        if 'coefficients' in model_result:
            coef_df = model_result['coefficients'].copy()
            coef_df['model'] = model_name
            coef_list.append(coef_df)
    
    if coef_list:
        coef_combined = pd.concat(coef_list, ignore_index=True)
        coef_combined.to_csv(TABLES_DIR / 'model_coefficients.csv', index=False)
        print(f"  Saved: {TABLES_DIR / 'model_coefficients.csv'}")
    
    # 2. Model metrics
    metrics_list = []
    for model_name, model_result in models.items():
        if 'metrics' in model_result:
            metrics = model_result['metrics']
            metrics['model'] = model_name
            metrics_list.append(metrics)
        elif 'r2' in model_result:
            # For OLS
            metrics_list.append({
                'model': model_name,
                'r2': model_result['r2'],
                'adj_r2': model_result.get('adj_r2', np.nan)
            })
    
    if metrics_list:
        metrics_df = pd.DataFrame(metrics_list)
        metrics_df.to_csv(TABLES_DIR / 'model_metrics.csv', index=False)
        print(f"  Saved: {TABLES_DIR / 'model_metrics.csv'}")
    
    # 3. Scenario assumptions
    assumptions_df.to_csv(TABLES_DIR / 'scenario_assumptions.csv', index=False)
    print(f"  Saved: {TABLES_DIR / 'scenario_assumptions.csv'}")
    
    # 4. Scenario forecasts
    forecast_df.to_csv(TABLES_DIR / 'scenario_forecasts.csv', index=False)
    print(f"  Saved: {TABLES_DIR / 'scenario_forecasts.csv'}")


def create_visualizations(historical_df, forecast_df):
    """
    Create and save all required visualizations.
    
    Parameters
    ----------
    historical_df : pd.DataFrame
        Historical data
    forecast_df : pd.DataFrame
        Forecast results
    """
    print("\nCreating visualizations...")
    
    # 1. Historical target
    plt.figure(figsize=(10, 6))
    plt.plot(historical_df['year'], historical_df['gross_output'], 
             marker='o', linewidth=2, markersize=8)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Gross Output (млн тенге)', fontsize=12)
    plt.title('Historical Gross Output (2015-2024)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'target_history.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'target_history.png'}")
    
    # 2. Scenario forecasts by model (using Ridge as key model)
    plt.figure(figsize=(12, 7))
    
    # Plot historical
    plt.plot(historical_df['year'], historical_df['gross_output'], 
             'o-', color='black', linewidth=2, markersize=8, label='Historical')
    
    # Plot forecasts for Ridge model
    key_model = 'Ridge' if 'Ridge' in forecast_df['model'].unique() else forecast_df['model'].unique()[0]
    colors = {'pessimistic': 'red', 'base': 'blue', 'optimistic': 'green'}
    
    for scenario in ['pessimistic', 'base', 'optimistic']:
        scenario_data = forecast_df[
            (forecast_df['model'] == key_model) & 
            (forecast_df['scenario'] == scenario)
        ]
        if len(scenario_data) > 0:
            plt.plot(scenario_data['year'], scenario_data['gross_output_pred'],
                    '--', color=colors[scenario], linewidth=2, 
                    label=f'{scenario.capitalize()} ({key_model})')
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Gross Output (млн тенге)', fontsize=12)
    plt.title(f'Scenario Forecasts - {key_model} Model', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'scenario_forecasts_by_model.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'scenario_forecasts_by_model.png'}")
    
    # 3. Compare models (base scenario)
    plt.figure(figsize=(12, 7))
    
    # Historical
    plt.plot(historical_df['year'], historical_df['gross_output'], 
             'o-', color='black', linewidth=2, markersize=8, label='Historical')
    
    # Base scenario for all models
    base_data = forecast_df[forecast_df['scenario'] == 'base']
    
    for i, model in enumerate(base_data['model'].unique()):
        model_data = base_data[base_data['model'] == model]
        plt.plot(model_data['year'], model_data['gross_output_pred'],
                '--', linewidth=2, label=model)
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Gross Output (млн тенге)', fontsize=12)
    plt.title('Model Comparison - Base Scenario', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'scenario_compare_models.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {FIGURES_DIR / 'scenario_compare_models.png'}")
    
    # 4. Coefficients overview
    try:
        coef_df = pd.read_csv(TABLES_DIR / 'model_coefficients.csv')
        
        # Select key model for visualization
        key_model = 'OLS' if 'OLS' in coef_df['model'].unique() else coef_df['model'].unique()[0]
        coef_plot = coef_df[coef_df['model'] == key_model].copy()
        coef_plot = coef_plot[coef_plot['variable'] != 'intercept']
        coef_plot = coef_plot.sort_values('coefficient')
        
        plt.figure(figsize=(10, 8))
        plt.barh(coef_plot['variable'], coef_plot['coefficient'])
        plt.xlabel('Coefficient Value', fontsize=12)
        plt.ylabel('Variable', fontsize=12)
        plt.title(f'Coefficients Overview - {key_model} Model', fontsize=14, fontweight='bold')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'coefficients_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved: {FIGURES_DIR / 'coefficients_overview.png'}")
    except Exception as e:
        print(f"  Warning: Could not create coefficients plot: {e}")


def main():
    """
    Main pipeline execution.
    """
    print("="*60)
    print("AGRICULTURAL FORECASTING PIPELINE")
    print("="*60)
    
    # Load data
    print("\n1. Loading data...")
    df = load_data()
    feature_cols = get_feature_columns()
    
    # Prepare data
    print("\n2. Preparing data...")
    df_clean = prepare_data_for_models(df, feature_cols)
    print(f"   Clean dataset: {df_clean.shape}")
    
    # Select subset of features to avoid overfitting (small dataset)
    selected_features = [
        'investment_agri',
        'labor_productivity',
        'employment_total',
        'gov_support_index',
        'profitability',
        'net_profit'
    ]
    print(f"   Using {len(selected_features)} features")
    
    # Train models
    print("\n3. Training models...")
    models = train_all_models(df_clean, selected_features)
    
    # Generate scenarios
    print("\n4. Generating scenarios...")
    key_drivers = [
        'investment_agri',
        'labor_productivity',
        'gov_support_index',
        'employment_total'
    ]
    
    scenarios, assumptions = generate_full_scenarios(df_clean, key_drivers, end_year=2030)
    
    # Ensure all features are in scenarios (fill missing with last known values)
    for scenario_name, scenario_df in scenarios.items():
        for feature in selected_features:
            if feature not in scenario_df.columns:
                last_value = df_clean[feature].iloc[-1]
                scenarios[scenario_name][feature] = last_value
    
    # Forecast
    print("\n5. Forecasting...")
    forecast_df = forecast_scenarios(models, scenarios, selected_features)
    
    # Add ARIMA forecast
    print("\n6. Adding ARIMA time series forecast...")
    arima_result = predict_arima_scenarios(df_clean, end_year=2030)
    
    if arima_result is not None and arima_result[0] is not None:
        arima_fc, arima_model = arima_result
        
        # Add ARIMA forecasts to main forecast dataframe
        for scenario_name in ['pessimistic', 'base', 'optimistic']:
            arima_df = arima_fc.copy()
            arima_df['scenario'] = scenario_name
            arima_df['model'] = 'ARIMA'
            arima_df['gross_output_pred'] = arima_df['arima_forecast']
            arima_df = arima_df[['year', 'scenario', 'model', 'gross_output_pred']]
            forecast_df = pd.concat([forecast_df, arima_df], ignore_index=True)
        
        print(f"   ARIMA order: {arima_model['order']}")
        print(f"   ARIMA R²: {arima_model['r2']:.4f}")
    else:
        print("   ARIMA forecast skipped (not converged)")
    
    # Save results
    print("\n7. Saving results...")
    save_results(models, scenarios, forecast_df, assumptions, df_clean)
    
    # Create visualizations
    print("\n8. Creating visualizations...")
    create_visualizations(df_clean, forecast_df)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nResults saved to:")
    print(f"  Tables: {TABLES_DIR}")
    print(f"  Figures: {FIGURES_DIR}")


if __name__ == '__main__':
    main()
