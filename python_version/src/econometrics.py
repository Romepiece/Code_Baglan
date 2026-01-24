import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.ardl import ARDL


def fit_ols(X, y):
    """
    Fit OLS regression model.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        Target variable
        
    Returns
    -------
    dict
        Dictionary with model results, coefficients, predictions
    """
    # Add constant
    X_const = sm.add_constant(X)
    
    # Fit model
    model = sm.OLS(y, X_const).fit()
    
    # Extract coefficients
    coefficients = pd.DataFrame({
        'variable': model.params.index,
        'coefficient': model.params.values,
        'std_err': model.bse.values,
        'p_value': model.pvalues.values
    })
    
    return {
        'model': model,
        'coefficients': coefficients,
        'predictions': model.fittedvalues,
        'r2': model.rsquared,
        'adj_r2': model.rsquared_adj,
        'summary': model.summary()
    }


def fit_ardl(df, target_col, exog_cols, lags=1, order=None):
    """
    Fit ARDL (Autoregressive Distributed Lag) model.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with all variables
    target_col : str
        Name of target variable
    exog_cols : list
        List of exogenous variable names
    lags : int or dict, default=1
        Number of lags for target variable
    order : dict, optional
        Lags for exogenous variables
        
    Returns
    -------
    dict
        Dictionary with model results, coefficients, predictions
    """
    # Prepare data
    y = df[target_col]
    X = df[exog_cols]
    
    # Set default order if not specified
    if order is None:
        order = {col: 1 for col in exog_cols}
    
    # Fit ARDL model
    try:
        model = ARDL(y, X, lags=lags, order=order).fit()
        
        # Extract coefficients
        coefficients = pd.DataFrame({
            'variable': model.params.index,
            'coefficient': model.params.values,
            'std_err': model.bse.values,
            'p_value': model.pvalues.values
        })
        
        return {
            'model': model,
            'coefficients': coefficients,
            'predictions': model.fittedvalues,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'summary': model.summary()
        }
    except Exception as e:
        print(f"ARDL fitting failed: {e}")
        return None


def fit_dynamic_diff_model(df, target_col, exog_cols):
    """
    Fit dynamic model in differences (approximation to ECM).
    
    This is NOT a strict ECM/cointegration model, but a simpler
    dynamic specification in first differences.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    target_col : str
        Target variable name
    exog_cols : list
        Exogenous variable names
        
    Returns
    -------
    dict
        Dictionary with model results, coefficients, predictions
    """
    # Calculate first differences
    df_diff = df.copy()
    df_diff[f'{target_col}_diff'] = df_diff[target_col].diff()
    
    for col in exog_cols:
        if col in df_diff.columns:
            df_diff[f'{col}_diff'] = df_diff[col].diff()
    
    # Remove first row with NaN
    df_diff = df_diff.dropna()
    
    # Prepare variables
    y = df_diff[f'{target_col}_diff']
    X_cols = [f'{col}_diff' for col in exog_cols if f'{col}_diff' in df_diff.columns]
    X = df_diff[X_cols]
    
    # Add lagged target (dynamic component)
    if len(df_diff) > 1:
        X[f'{target_col}_lag1'] = df[target_col].shift(1).loc[df_diff.index]
    
    # Remove any remaining NaN
    combined = pd.concat([y, X], axis=1).dropna()
    y = combined[f'{target_col}_diff']
    X = combined.drop(columns=[f'{target_col}_diff'])
    
    # Fit OLS on differences
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit()
    
    # Extract coefficients
    coefficients = pd.DataFrame({
        'variable': model.params.index,
        'coefficient': model.params.values,
        'std_err': model.bse.values,
        'p_value': model.pvalues.values
    })
    
    return {
        'model': model,
        'coefficients': coefficients,
        'predictions': model.fittedvalues,
        'r2': model.rsquared,
        'adj_r2': model.rsquared_adj,
        'summary': model.summary(),
        'note': 'Dynamic model in first differences (not strict ECM)'
    }


def predict_econometric(model_result, X_future):
    """
    Make predictions using fitted econometric model.
    
    Parameters
    ----------
    model_result : dict
        Result dictionary from fit_ols or similar
    X_future : pd.DataFrame
        Future feature values
        
    Returns
    -------
    np.ndarray
        Predictions
    """
    model = model_result['model']
    
    # Add constant if needed
    if 'const' in model.params.index:
        X_future_const = sm.add_constant(X_future)
    else:
        X_future_const = X_future
    
    return model.predict(X_future_const)


if __name__ == '__main__':
    from data_loader import load_data, get_feature_columns
    
    df = load_data()
    features = get_feature_columns()
    
    # Select subset of features for testing
    test_features = ['investment_agri', 'labor_productivity', 'employment_total']
    X = df[test_features].dropna()
    y = df.loc[X.index, 'gross_output']
    
    print("Testing OLS model...")
    ols_result = fit_ols(X, y)
    print(f"\nOLS R²: {ols_result['r2']:.4f}")
    print("\nCoefficients:")
    print(ols_result['coefficients'])
