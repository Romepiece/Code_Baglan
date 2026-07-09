"""
Time series models for agricultural forecasting.

Includes ARIMA for univariate time series forecasting.
"""

import warnings
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

warnings.filterwarnings('ignore')


def fit_arima(df, target_col='gross_output', order=(1, 1, 1)):
    """
    Fit ARIMA model to univariate time series.
    
    Parameters
    ----------
    df : pd.DataFrame
        Time series data with 'year' column
    target_col : str, default='gross_output'
        Target variable column name
    order : tuple, default=(1, 1, 1)
        (p, d, q) ARIMA order
        p: AR lags
        d: Differencing
        q: MA lags
        
    Returns
    -------
    dict
        Model results
    """
    # Extract time series
    ts = df[target_col].values
    
    try:
        # Fit ARIMA
        model = ARIMA(ts, order=order)
        results = model.fit()
        
        # In-sample predictions
        predictions = results.fittedvalues
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        rmse = np.sqrt(mean_squared_error(ts, predictions))
        mae = mean_absolute_error(ts, predictions)
        
        # Simple R² calculation for time series
        ss_res = np.sum((ts - predictions) ** 2)
        ss_tot = np.sum((ts - np.mean(ts)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'model': results,
            'predictions': predictions,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'aic': results.aic,
            'bic': results.bic,
            'order': order,
            'summary': results.summary()
        }
    
    except Exception as e:
        print(f"ARIMA fitting failed with order {order}: {e}")
        return None


def auto_arima_search(df, target_col='gross_output', max_p=3, max_d=2, max_q=3):
    """
    Simple grid search for best ARIMA order (not statsmodels auto_arima).
    
    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    target_col : str
        Target variable
    max_p, max_d, max_q : int
        Maximum values for p, d, q
        
    Returns
    -------
    dict
        Best model result and order
    """
    best_aic = np.inf
    best_order = None
    best_result = None
    
    ts = df[target_col].values
    
    # Grid search
    for p in range(0, max_p + 1):
        for d in range(0, max_d + 1):
            for q in range(0, max_q + 1):
                try:
                    model = ARIMA(ts, order=(p, d, q))
                    results = model.fit()
                    
                    if results.aic < best_aic:
                        best_aic = results.aic
                        best_order = (p, d, q)
                        best_result = results
                
                except Exception:
                    continue
    
    if best_result is None:
        print("Auto ARIMA search failed")
        return None
    
    # Fit best model again for full result
    result = fit_arima(df, target_col, order=best_order)
    
    if result:
        result['best_order'] = best_order
        result['aic'] = best_aic
    
    return result


def forecast_arima(model_result, steps=5):
    """
    Generate forecast using fitted ARIMA model.
    
    Parameters
    ----------
    model_result : dict
        Result from fit_arima
    steps : int
        Number of steps to forecast
        
    Returns
    -------
    np.ndarray
        Forecast values
    """
    model_obj = model_result['model']
    
    # Use forecast() method directly
    try:
        forecast_result = model_obj.get_forecast(steps=steps)
        forecast_values = forecast_result.predicted_mean.values
    except Exception as e:
        # Fallback: use fcast from model
        try:
            forecast_values = model_obj.fcast(steps=steps)
        except Exception:
            # Last resort: use simple naive forecast
            print(f"   Warning: ARIMA forecast method failed ({e}), using last value")
            forecast_values = np.full(steps, model_obj.fittedvalues[-1])
    
    return forecast_values


def predict_arima_scenarios(df, target_col='gross_output', end_year=2030):
    """
    Generate ARIMA predictions as baseline (single scenario).
    
    This provides a univariate forecast independent of other factors.
    
    Parameters
    ----------
    df : pd.DataFrame
        Historical data
    target_col : str
        Target variable
    end_year : int
        Last forecast year
        
    Returns
    -------
    tuple
        (forecast dataframe, model result)
    """
    # Find best ARIMA order
    arima_result = auto_arima_search(df, target_col)
    
    if arima_result is None:
        # Fallback to (1,1,1)
        arima_result = fit_arima(df, target_col, order=(1, 1, 1))
    
    if arima_result is None:
        return None, None
    
    # Forecast
    last_year = df['year'].max()
    n_steps = end_year - last_year
    
    if n_steps <= 0:
        print(f"Error: end_year ({end_year}) must be after last_year ({last_year})")
        return None, None
    
    forecast_values = forecast_arima(arima_result, steps=n_steps)
    
    # Create forecast dataframe
    forecast_years = list(range(last_year + 1, end_year + 1))
    
    arima_forecast = pd.DataFrame({
        'year': forecast_years,
        'arima_forecast': forecast_values
    })
    
    return arima_forecast, arima_result


if __name__ == '__main__':
    from data_loader import load_data
    
    df = load_data()
    df_clean = df.dropna()
    
    print("Testing ARIMA models...")
    
    # Auto search
    print("\nAuto ARIMA search (grid)...")
    result = auto_arima_search(df_clean)
    
    if result:
        print(f"Best order: {result['best_order']}")
        print(f"AIC: {result['aic']:.2f}")
        print(f"R²: {result['r2']:.4f}")
        print(f"\n{result['summary']}")
        
        # Forecast
        print("\n\nForecasting to 2030...")
        arima_fc, _ = predict_arima_scenarios(df_clean, end_year=2030)
        print(arima_fc)
