"""
Enhanced visualization for scenario forecasts with clear differences.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

# Output directory
FIGURES_DIR = Path('python_version/outputs/figures')

# Load data
forecast_df = pd.read_csv('python_version/outputs/tables/scenario_forecasts.csv')
historical_df = pd.read_csv('data/processed/agro_dataset_ml.csv')

# Clean historical
historical_df = historical_df.dropna(subset=['gross_output'])

# ============================================
# Figure 1: Scenario Spreads (Lasso Best Model)
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Filter Lasso predictions
lasso_data = forecast_df[forecast_df['model'] == 'Lasso']

# Plot 1: All three scenarios together
ax = axes[0, 0]
for scenario in ['pessimistic', 'base', 'optimistic']:
    data = lasso_data[lasso_data['scenario'] == scenario]
    ax.plot(data['year'], data['gross_output_pred'], marker='o', linewidth=2.5, 
            markersize=8, label=scenario.capitalize())

ax.plot(historical_df['year'], historical_df['gross_output'], 'ko-', 
        linewidth=2.5, markersize=8, label='Historical', zorder=5)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Gross Output (млн тенге)', fontsize=12)
ax.set_title('Lasso: Three Scenarios Comparison', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Plot 2: Scenario Ranges (Spread)
ax = axes[0, 1]
years = sorted(lasso_data['year'].unique())
pess = []
base = []
opt = []

for year in years:
    pess.append(lasso_data[(lasso_data['year']==year) & (lasso_data['scenario']=='pessimistic')]['gross_output_pred'].values[0])
    base.append(lasso_data[(lasso_data['year']==year) & (lasso_data['scenario']=='base')]['gross_output_pred'].values[0])
    opt.append(lasso_data[(lasso_data['year']==year) & (lasso_data['scenario']=='optimistic')]['gross_output_pred'].values[0])

# Shaded area between scenarios
ax.fill_between(years, pess, opt, alpha=0.3, color='gray', label='Forecast Range')
ax.plot(years, base, 'b-o', linewidth=2.5, markersize=8, label='Base Scenario', zorder=5)
ax.plot(years, pess, 'r--', linewidth=2, markersize=6, label='Pessimistic', zorder=4)
ax.plot(years, opt, 'g--', linewidth=2, markersize=6, label='Optimistic', zorder=4)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Gross Output (млн тенге)', fontsize=12)
ax.set_title('Scenario Range (Shaded Area)', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Plot 3: Percentage Difference from Base
ax = axes[1, 0]
pct_pess = [(p/b - 1)*100 for p, b in zip(pess, base)]
pct_opt = [(o/b - 1)*100 for o, b in zip(opt, base)]

ax.plot(years, pct_pess, 'r-o', linewidth=2.5, markersize=8, label='Pessimistic vs Base')
ax.plot(years, pct_opt, 'g-o', linewidth=2.5, markersize=8, label='Optimistic vs Base')
ax.axhline(y=0, color='b', linestyle='--', linewidth=2, label='Base Scenario')
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Difference from Base (%)', fontsize=12)
ax.set_title('Scenario Divergence Over Time', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Plot 4: Comparison with Historical
ax = axes[1, 1]
# Calculate growth rates
hist_growth = []
for i in range(1, len(historical_df)):
    growth = (historical_df.iloc[i]['gross_output'] / historical_df.iloc[i-1]['gross_output'] - 1) * 100
    hist_growth.append(growth)

forecast_growth_base = [(base[i]/base[i-1] - 1)*100 for i in range(1, len(base))]
forecast_growth_pess = [(pess[i]/pess[i-1] - 1)*100 for i in range(1, len(pess))]
forecast_growth_opt = [(opt[i]/opt[i-1] - 1)*100 for i in range(1, len(opt))]

years_hist = historical_df['year'].values[1:]
years_forecast = years[1:]

ax.bar(np.array(years_hist) - 0.15, hist_growth, width=0.3, label='Historical', alpha=0.7)
ax.bar(np.array(years_forecast) + 0.15, forecast_growth_base, width=0.3, label='Base Forecast', alpha=0.7)
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('YoY Growth Rate (%)', fontsize=12)
ax.set_title('Year-over-Year Growth: Historical vs Forecast', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'scenario_analysis_detailed.png', dpi=300, bbox_inches='tight')
print(f"Saved: {FIGURES_DIR / 'scenario_analysis_detailed.png'}")
plt.close()

# ============================================
# Figure 2: All Models Comparison (Base Scenario)
# ============================================
fig, ax = plt.subplots(figsize=(14, 7))

# Plot historical
ax.plot(historical_df['year'], historical_df['gross_output'], 'ko-', 
        linewidth=2.5, markersize=9, label='Historical Data', zorder=10)

# Plot all models for base scenario
colors = {'LinearRegression': 'blue', 'Ridge': 'orange', 'Lasso': 'green', 
          'ElasticNet': 'red', 'ARIMA': 'purple'}

base_forecast = forecast_df[forecast_df['scenario'] == 'base']

for model in base_forecast['model'].unique():
    model_data = base_forecast[base_forecast['model'] == model].sort_values('year')
    ax.plot(model_data['year'], model_data['gross_output_pred'], 
            marker='s', linewidth=2, markersize=7, label=model, 
            color=colors.get(model, 'gray'), alpha=0.8)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Gross Output (млн тенге)', fontsize=12)
ax.set_title('Base Scenario: All Models Comparison', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'all_models_comparison.png', dpi=300, bbox_inches='tight')
print(f"Saved: {FIGURES_DIR / 'all_models_comparison.png'}")
plt.close()

# ============================================
# Figure 3: Summary Statistics Table
# ============================================
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('tight')
ax.axis('off')

# Create summary table
summary_data = []
for scenario in ['pessimistic', 'base', 'optimistic']:
    lasso_vals = lasso_data[lasso_data['scenario'] == scenario]['gross_output_pred'].values
    y2025 = lasso_vals[0]
    y2030 = lasso_vals[-1]
    growth = (y2030 / y2025 - 1) * 100
    cagr = ((y2030 / y2025) ** (1/5) - 1) * 100
    
    summary_data.append([
        scenario.capitalize(),
        f"{y2025:,.0f}",
        f"{y2030:,.0f}",
        f"{growth:+.1f}%",
        f"{cagr:+.2f}%"
    ])

table = ax.table(cellText=summary_data,
                colLabels=['Scenario', '2025 (млн)', '2030 (млн)', 'Total Growth', 'CAGR'],
                cellLoc='center',
                loc='center',
                colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# Color header
for i in range(5):
    table[(0, i)].set_facecolor('#40466e')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Color rows
colors_row = ['#ffcccc', '#ccffcc', '#ccccff']
for i in range(1, 4):
    for j in range(5):
        table[(i, j)].set_facecolor(colors_row[i-1])

plt.title('Lasso Model: Scenario Summary Statistics', fontsize=14, fontweight='bold', pad=20)
plt.savefig(FIGURES_DIR / 'scenario_summary_table.png', dpi=300, bbox_inches='tight')
print(f"Saved: {FIGURES_DIR / 'scenario_summary_table.png'}")
plt.close()

print("\n✅ Enhanced visualizations created!")
print(f"\nNew files:")
print(f"  1. scenario_analysis_detailed.png - 4 subplots showing scenario analysis")
print(f"  2. all_models_comparison.png - All 5 models for base scenario")
print(f"  3. scenario_summary_table.png - Summary statistics")
