import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def time_split_data(df, target_col, feature_cols, train_years=None, test_years=None):
    """
    Split data by time periods for time series validation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with 'year' column
    target_col : str
        Target variable name
    feature_cols : list
        Feature column names
    train_years : tuple, optional
        (start_year, end_year) for training
    test_years : tuple, optional
        (start_year, end_year) for testing
        
    Returns
    -------
    tuple
        (X_train, X_test, y_train, y_test)
    """
    if train_years is not None:
        train_mask = (df['year'] >= train_years[0]) & (df['year'] <= train_years[1])
    else:
        # Default: use all but last 2 years for training
        train_mask = df['year'] <= df['year'].max() - 2
    
    if test_years is not None:
        test_mask = (df['year'] >= test_years[0]) & (df['year'] <= test_years[1])
    else:
        # Default: use last 2 years for testing
        test_mask = df['year'] > df['year'].max() - 2
    
    X_train = df.loc[train_mask, feature_cols]
    X_test = df.loc[test_mask, feature_cols]
    y_train = df.loc[train_mask, target_col]
    y_test = df.loc[test_mask, target_col]
    
    return X_train, X_test, y_train, y_test


def fit_linear_regression(X_train, X_test, y_train, y_test):
    """
    Fit Linear Regression baseline model.
    
    Parameters
    ----------
    X_train, X_test : pd.DataFrame
        Feature matrices
    y_train, y_test : pd.Series
        Target variables
        
    Returns
    -------
    dict
        Model results with coefficients and metrics
    """
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Coefficients
    coefficients = pd.DataFrame({
        'variable': X_train.columns,
        'coefficient': model.coef_
    })
    coefficients = pd.concat([
        pd.DataFrame({'variable': ['intercept'], 'coefficient': [model.intercept_]}),
        coefficients
    ], ignore_index=True)
    
    # Metrics
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred)
    }
    
    return {
        'model': model,
        'coefficients': coefficients,
        'metrics': metrics,
        'train_predictions': y_train_pred,
        'test_predictions': y_test_pred
    }


def fit_ridge(X_train, X_test, y_train, y_test, alpha=1.0):
    """
    Fit Ridge regression with scaling pipeline.
    
    Parameters
    ----------
    X_train, X_test : pd.DataFrame
        Feature matrices
    y_train, y_test : pd.Series
        Target variables
    alpha : float, default=1.0
        Regularization strength
        
    Returns
    -------
    dict
        Model results with coefficients and metrics
    """
    # Create pipeline with StandardScaler
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('ridge', Ridge(alpha=alpha))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    # Extract coefficients (from scaled features)
    ridge_model = pipeline.named_steps['ridge']
    coefficients = pd.DataFrame({
        'variable': X_train.columns,
        'coefficient': ridge_model.coef_
    })
    coefficients = pd.concat([
        pd.DataFrame({'variable': ['intercept'], 'coefficient': [ridge_model.intercept_]}),
        coefficients
    ], ignore_index=True)
    
    # Metrics
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred),
        'alpha': alpha
    }
    
    return {
        'model': pipeline,
        'coefficients': coefficients,
        'metrics': metrics,
        'train_predictions': y_train_pred,
        'test_predictions': y_test_pred
    }


def fit_lasso(X_train, X_test, y_train, y_test, alpha=1.0):
    """
    Fit Lasso regression with scaling pipeline.
    
    Parameters
    ----------
    X_train, X_test : pd.DataFrame
        Feature matrices
    y_train, y_test : pd.Series
        Target variables
    alpha : float, default=1.0
        Regularization strength
        
    Returns
    -------
    dict
        Model results with coefficients and metrics
    """
    # Create pipeline with StandardScaler
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('lasso', Lasso(alpha=alpha, max_iter=10000))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    # Extract coefficients
    lasso_model = pipeline.named_steps['lasso']
    coefficients = pd.DataFrame({
        'variable': X_train.columns,
        'coefficient': lasso_model.coef_
    })
    coefficients = pd.concat([
        pd.DataFrame({'variable': ['intercept'], 'coefficient': [lasso_model.intercept_]}),
        coefficients
    ], ignore_index=True)
    
    # Metrics
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred),
        'alpha': alpha
    }
    
    return {
        'model': pipeline,
        'coefficients': coefficients,
        'metrics': metrics,
        'train_predictions': y_train_pred,
        'test_predictions': y_test_pred
    }


def fit_elastic_net(X_train, X_test, y_train, y_test, alpha=1.0, l1_ratio=0.5):
    """
    Fit ElasticNet regression with scaling pipeline.
    
    Parameters
    ----------
    X_train, X_test : pd.DataFrame
        Feature matrices
    y_train, y_test : pd.Series
        Target variables
    alpha : float, default=1.0
        Regularization strength
    l1_ratio : float, default=0.5
        Mix of L1 and L2 (0=Ridge, 1=Lasso)
        
    Returns
    -------
    dict
        Model results with coefficients and metrics
    """
    # Create pipeline with StandardScaler
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('elastic', ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=10000))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    # Extract coefficients
    elastic_model = pipeline.named_steps['elastic']
    coefficients = pd.DataFrame({
        'variable': X_train.columns,
        'coefficient': elastic_model.coef_
    })
    coefficients = pd.concat([
        pd.DataFrame({'variable': ['intercept'], 'coefficient': [elastic_model.intercept_]}),
        coefficients
    ], ignore_index=True)
    
    # Metrics
    metrics = {
        'train_r2': r2_score(y_train, y_train_pred),
        'test_r2': r2_score(y_test, y_test_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'test_mae': mean_absolute_error(y_test, y_test_pred),
        'alpha': alpha,
        'l1_ratio': l1_ratio
    }
    
    return {
        'model': pipeline,
        'coefficients': coefficients,
        'metrics': metrics,
        'train_predictions': y_train_pred,
        'test_predictions': y_test_pred
    }


if __name__ == '__main__':
    from data_loader import load_data, get_feature_columns
    
    df = load_data()
    features = get_feature_columns()[:5]  # Test with subset
    
    # Time-based split
    X_train, X_test, y_train, y_test = time_split_data(
        df, 'gross_output', features
    )
    
    print("Testing Linear Regression...")
    lr_result = fit_linear_regression(X_train, X_test, y_train, y_test)
    print(f"Test R²: {lr_result['metrics']['test_r2']:.4f}")
    
    print("\nTesting Ridge...")
    ridge_result = fit_ridge(X_train, X_test, y_train, y_test, alpha=1.0)
    print(f"Test R²: {ridge_result['metrics']['test_r2']:.4f}")
