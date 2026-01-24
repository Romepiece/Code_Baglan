"""
STAGE 3: VARIABLE PREPARATION AND LAG CREATION

Tasks:
- Create log1p if needed
- Create lags (L1) by region
- Save lags preview and prepared dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_01_VALIDATE,
    TABLES_03_PREPARE,
    SEED
)

np.random.seed(SEED)

print("=" * 80)
print("STAGE 3: VARIABLE PREPARATION AND LAG CREATION")
print("=" * 80)

# Load data
print("\n1. Loading data...")
df = pd.read_csv(TABLES_01_VALIDATE / "raw_panel_data.csv")
print(f"   [OK] Loaded {len(df)} rows")

# Sort for correct lag creation
print("\n2. Sorting by region_id and year...")
df = df.sort_values(["region_id", "year"]).reset_index(drop=True)
print(f"   [OK] Data sorted")

# Create lags by region
print("\n3. Creating lag variables (L1 by region)...")

def create_lags_by_group(group_df, variable_names, lag_periods=[1]):
    """
    Creates lags for variables within each group (region)
    """
    for var in variable_names:
        for lag in lag_periods:
            group_df[f"lag{lag}_{var}"] = group_df[var].shift(lag)
    return group_df

# Create lags for log variables
lag_vars = ["log_women_farms", "log_credit_total"]
df = df.groupby("region_id", group_keys=False).apply(
    lambda x: create_lags_by_group(x, lag_vars, [1])
)

print(f"   [OK] Created lags: lag1_log_women_farms, lag1_log_credit_total")

# Create lags for credit components (for robustness)
credit_components = ["credit_kaf", "credit_acc", "credit_fund"]
for comp in credit_components:
    df[f"log_{comp}"] = np.log1p(df[comp])
    df = df.groupby("region_id", group_keys=False).apply(
        lambda x: create_lags_by_group(x, [f"log_{comp}"], [1])
    )
print(f"   [OK] Created logarithms and lags for credit components")

# Check lags
print("\n4. Verifying created lags...")
lags_preview = df[["region_id", "year", "log_women_farms", "lag1_log_women_farms", 
                    "log_credit_total", "lag1_log_credit_total"]].head(30)
print(lags_preview.to_string(index=False))
lags_preview.to_csv(TABLES_03_PREPARE / "lags_preview.csv", index=False)
print(f"   [OK] Saved to lags_preview.csv")

# Missing statistics after lag creation
print("\n5. Missing data statistics after lag creation...")
missing_stats = pd.DataFrame({
    "Variable": ["log_women_farms", "lag1_log_women_farms", "log_credit_total", "lag1_log_credit_total"],
    "Missing_Count": [
        df["log_women_farms"].isna().sum(),
        df["lag1_log_women_farms"].isna().sum(),
        df["log_credit_total"].isna().sum(),
        df["lag1_log_credit_total"].isna().sum()
    ]
})
missing_stats["Missing_Percent"] = (missing_stats["Missing_Count"] / len(df) * 100).round(2)
print(missing_stats.to_string(index=False))
missing_stats.to_csv(TABLES_03_PREPARE / "missing_after_lags.csv", index=False)
print(f"   [OK] Saved to missing_after_lags.csv")

# Create year FE variable
print("\n6. Preparing variables for econometrics...")
df["year_fe"] = df["year"].astype(str)
print(f"   [OK] Created year_fe variable for fixed effects")

# Panel structure analysis
print("\n7. Analyzing unbalanced panel structure...")
panel_structure = df.groupby("year")["region_id"].nunique().reset_index()
panel_structure.columns = ["Year", "N_Regions"]
panel_structure["Total_Obs"] = df.groupby("year").size().values
print(panel_structure.to_string(index=False))

# Save prepared dataset
print("\n8. Saving prepared dataset...")
df.to_csv(TABLES_03_PREPARE / "prepared_panel.csv", index=False)
print(f"   [OK] Saved to prepared_panel.csv")

# Descriptive statistics for prepared variables
print("\n9. Descriptive statistics for prepared dataset...")
prep_stats = df[[
    "log_women_farms", "lag1_log_women_farms",
    "log_credit_total", "lag1_log_credit_total",
    "land_share", "log_credit_kaf", "log_credit_acc", "log_credit_fund"
]].describe().round(4)
print(prep_stats)
prep_stats.to_csv(TABLES_03_PREPARE / "prepared_variables_statistics.csv")
print(f"   [OK] Saved to prepared_variables_statistics.csv")

print("\n" + "=" * 80)
print("STAGE 3 COMPLETED")
print("=" * 80)
print(f"\nOutput files in {TABLES_03_PREPARE}:")
print(f"  - prepared_panel.csv (main dataset for analysis)")
print(f"  - lags_preview.csv")
print(f"  - missing_after_lags.csv")
print(f"  - prepared_variables_statistics.csv")
print(f"\nDataset ready for econometric analysis!")
