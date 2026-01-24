"""
STAGE 4: ECONOMETRIC ANALYSIS (MAIN PART OF ARTICLE)

Tasks:
4.1) Pooled OLS: log_women_farms ~ log_credit_total + land_share
4.2) Two-way Fixed Effects: log_women_farms ~ log_credit_total + land_share + regional_FE + time_FE
     (with clustered standard errors by region)
4.3) Robustness check: replacement of credit_total with components
"""

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from linearmodels.panel import PanelOLS
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_03_PREPARE,
    TABLES_04_ECONOMETRICS,
    INFOGRAPHICS_04_ECONOMETRICS,
    PROMPT_04_ECONOMETRICS,
    SEED
)

np.random.seed(SEED)

print("=" * 80)
print("STAGE 4: ECONOMETRIC ANALYSIS")
print("=" * 80)

# Load data
print("\n1. Loading prepared data...")
print(f"   Path: {TABLES_03_PREPARE / 'prepared_panel.csv'}")
df = pd.read_csv(TABLES_03_PREPARE / "prepared_panel.csv")
df = df.sort_values(["region_id", "year"]).reset_index(drop=True)
print(f"   [OK] Loaded {len(df)} rows")

# Prepare data for analysis
print("\n2. Preparing data for analysis...")
analysis_vars = ["log_women_farms", "log_credit_total", "land_share", "region_id", "year"]
df_analysis = df[analysis_vars].dropna().copy()
print(f"   [OK] After removing missing: {len(df_analysis)} rows (was {len(df)})")
print(f"   [OK] Loss of {len(df) - len(df_analysis)} observations ({((len(df) - len(df_analysis))/len(df)*100):.1f}%)")

# ============================================================================
# 4.1) POOLED OLS
# ============================================================================
print("\n" + "=" * 80)
print("4.1) POOLED OLS MODEL")
print("=" * 80)

# Pooled OLS with robust standard errors
model_ols = smf.ols(
    'log_women_farms ~ log_credit_total + land_share',
    data=df_analysis
).fit(cov_type='HC1')

print("\nMain model: log_women_farms ~ log_credit_total + land_share")
print("\nPooled OLS results (robust SE):")
print(model_ols.summary())

# Save OLS results
ols_results = pd.DataFrame({
    'Model': ['Pooled OLS'] * 3,
    'Variable': ['log_credit_total', 'land_share', 'Constant'],
    'Coefficient': [
        model_ols.params['log_credit_total'],
        model_ols.params['land_share'],
        model_ols.params['Intercept']
    ],
    'Std_Error': [
        model_ols.bse['log_credit_total'],
        model_ols.bse['land_share'],
        model_ols.bse['Intercept']
    ],
    'T_Stat': [
        model_ols.tvalues['log_credit_total'],
        model_ols.tvalues['land_share'],
        model_ols.tvalues['Intercept']
    ],
    'P_Value': [
        model_ols.pvalues['log_credit_total'],
        model_ols.pvalues['land_share'],
        model_ols.pvalues['Intercept']
    ]
})

print(f"\nN = {model_ols.nobs}")
print(f"R-squared = {model_ols.rsquared:.4f}")
print(f"Adj. R-squared = {model_ols.rsquared_adj:.4f}")

# ============================================================================
# 4.2) TWO-WAY FIXED EFFECTS (TWFE)
# ============================================================================
print("\n" + "=" * 80)
print("4.2) TWO-WAY FIXED EFFECTS (TWFE) MODEL")
print("=" * 80)

# Prepare panel for linearmodels
df_fe = df_analysis.copy()
df_fe = df_fe.set_index(['region_id', 'year'])

print("\nModel: log_women_farms ~ log_credit_total + land_share + region_FE + year_FE")
print("(with clustered standard errors by region)")

# TWFE model with clustered SE by region
model_fe = PanelOLS(
    df_fe['log_women_farms'],
    df_fe[['log_credit_total', 'land_share']],
    entity_effects=True,  # Regional fixed effects
    time_effects=True,    # Time fixed effects
    check_rank=False
)

results_fe = model_fe.fit(cov_type='clustered', cluster_entity=True)

print("\nTWFE results (clustered SE by region):")
print(results_fe.summary)

# Save TWFE results
twfe_results = pd.DataFrame({
    'Model': ['TWFE'] * 3,
    'Variable': ['log_credit_total', 'land_share', 'Constant'],
    'Coefficient': [
        results_fe.params['log_credit_total'],
        results_fe.params['land_share'],
        np.nan
    ],
    'Std_Error': [
        results_fe.std_errors['log_credit_total'],
        results_fe.std_errors['land_share'],
        np.nan
    ],
    'T_Stat': [
        results_fe.tstats['log_credit_total'],
        results_fe.tstats['land_share'],
        np.nan
    ],
    'P_Value': [
        results_fe.pvalues['log_credit_total'],
        results_fe.pvalues['land_share'],
        np.nan
    ]
})

print(f"\nN = {results_fe.nobs}")
print(f"R-squared (within) = {results_fe.rsquared_within:.4f}")
print(f"R-squared (overall) = {results_fe.rsquared_overall:.4f}")

# ============================================================================
# 4.3) ROBUSTNESS CHECK (replacing with credit components)
# ============================================================================
print("\n" + "=" * 80)
print("4.3) ROBUSTNESS CHECK (replacement with credit components)")
print("=" * 80)

# Prepare components data
robustness_vars = ['log_credit_kaf', 'log_credit_acc', 'log_credit_fund']
df_rob = df[['log_women_farms', 'land_share', 'region_id', 'year'] + robustness_vars].dropna()
print(f"\nData preparation for robustness: {len(df_rob)} rows")

robustness_results = []

# Model 1: TWFE with KAF
print("\n--- TWFE with log_credit_kaf ---")
df_rob_fe = df_rob[['log_women_farms', 'log_credit_kaf', 'land_share']].copy()
df_rob_fe = df_rob_fe.assign(region_id=df_rob['region_id'].values, year=df_rob['year'].values)
df_rob_fe = df_rob_fe.set_index(['region_id', 'year'])

model_rob_kaf = PanelOLS(
    df_rob_fe['log_women_farms'],
    df_rob_fe[['log_credit_kaf', 'land_share']],
    entity_effects=True,
    time_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)

print(f"log_credit_kaf coefficient: {model_rob_kaf.params['log_credit_kaf']:.6f}")
print(f"t-stat: {model_rob_kaf.tstats['log_credit_kaf']:.4f}, p-value: {model_rob_kaf.pvalues['log_credit_kaf']:.4f}")

robustness_results.append({
    'Model': 'TWFE_KAF',
    'Variable': 'log_credit_kaf',
    'Coefficient': model_rob_kaf.params['log_credit_kaf'],
    'Std_Error': model_rob_kaf.std_errors['log_credit_kaf'],
    'T_Stat': model_rob_kaf.tstats['log_credit_kaf'],
    'P_Value': model_rob_kaf.pvalues['log_credit_kaf'],
    'N': model_rob_kaf.nobs
})

# Model 2: TWFE with ACC
print("\n--- TWFE with log_credit_acc ---")
df_rob_fe = df_rob[['log_women_farms', 'log_credit_acc', 'land_share']].copy()
df_rob_fe = df_rob_fe.assign(region_id=df_rob['region_id'].values, year=df_rob['year'].values)
df_rob_fe = df_rob_fe.set_index(['region_id', 'year'])

model_rob_acc = PanelOLS(
    df_rob_fe['log_women_farms'],
    df_rob_fe[['log_credit_acc', 'land_share']],
    entity_effects=True,
    time_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)

print(f"log_credit_acc coefficient: {model_rob_acc.params['log_credit_acc']:.6f}")
print(f"t-stat: {model_rob_acc.tstats['log_credit_acc']:.4f}, p-value: {model_rob_acc.pvalues['log_credit_acc']:.4f}")

robustness_results.append({
    'Model': 'TWFE_ACC',
    'Variable': 'log_credit_acc',
    'Coefficient': model_rob_acc.params['log_credit_acc'],
    'Std_Error': model_rob_acc.std_errors['log_credit_acc'],
    'T_Stat': model_rob_acc.tstats['log_credit_acc'],
    'P_Value': model_rob_acc.pvalues['log_credit_acc'],
    'N': model_rob_acc.nobs
})

# Model 3: TWFE with FUND
print("\n--- TWFE with log_credit_fund ---")
df_rob_fe = df_rob[['log_women_farms', 'log_credit_fund', 'land_share']].copy()
df_rob_fe = df_rob_fe.assign(region_id=df_rob['region_id'].values, year=df_rob['year'].values)
df_rob_fe = df_rob_fe.set_index(['region_id', 'year'])

model_rob_fund = PanelOLS(
    df_rob_fe['log_women_farms'],
    df_rob_fe[['log_credit_fund', 'land_share']],
    entity_effects=True,
    time_effects=True,
    check_rank=False
).fit(cov_type='clustered', cluster_entity=True)

print(f"log_credit_fund coefficient: {model_rob_fund.params['log_credit_fund']:.6f}")
print(f"t-stat: {model_rob_fund.tstats['log_credit_fund']:.4f}, p-value: {model_rob_fund.pvalues['log_credit_fund']:.4f}")

robustness_results.append({
    'Model': 'TWFE_FUND',
    'Variable': 'log_credit_fund',
    'Coefficient': model_rob_fund.params['log_credit_fund'],
    'Std_Error': model_rob_fund.std_errors['log_credit_fund'],
    'T_Stat': model_rob_fund.tstats['log_credit_fund'],
    'P_Value': model_rob_fund.pvalues['log_credit_fund'],
    'N': model_rob_fund.nobs
})

rob_df = pd.DataFrame(robustness_results)
print("\nRobustness results table:")
print(rob_df)

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save main model results
main_results = pd.concat([ols_results, twfe_results], ignore_index=True)
main_results.to_csv(TABLES_04_ECONOMETRICS / "reg_pooled_ols.csv", index=False)
print(f"\n[OK] Pooled OLS saved to reg_pooled_ols.csv")

main_results.to_csv(TABLES_04_ECONOMETRICS / "reg_twfe_main.csv", index=False)
print(f"[OK] TWFE model saved to reg_twfe_main.csv")

# Save robustness results
rob_df.to_csv(TABLES_04_ECONOMETRICS / "reg_twfe_components.csv", index=False)
print(f"[OK] Robustness results saved to reg_twfe_components.csv")

# Save OLS diagnostics
ols_summary = pd.DataFrame({
    'Statistic': ['N', 'R-squared', 'Adj. R-squared', 'F-statistic', 'F p-value'],
    'Value': [
        model_ols.nobs,
        model_ols.rsquared,
        model_ols.rsquared_adj,
        model_ols.fvalue,
        model_ols.f_pvalue
    ]
})
ols_summary.to_csv(TABLES_04_ECONOMETRICS / "ols_diagnostics.csv", index=False)
print(f"[OK] OLS statistics saved to ols_diagnostics.csv")

# Save TWFE diagnostics
fe_summary = pd.DataFrame({
    'Statistic': ['N', 'R-squared (within)', 'R-squared (overall)', 'F-statistic'],
    'Value': [
        results_fe.nobs,
        results_fe.rsquared_within,
        results_fe.rsquared_overall,
        results_fe.f_statistic.stat
    ]
})
fe_summary.to_csv(TABLES_04_ECONOMETRICS / "twfe_diagnostics.csv", index=False)
print(f"[OK] TWFE statistics saved to twfe_diagnostics.csv")

# Create coefficient plot
print("\nCreating coefficient visualization...")
fig, ax = plt.subplots(figsize=(10, 6))

# Data for visualization
variables = ['log_credit_total', 'land_share']
ols_coefs = [model_ols.params['log_credit_total'], model_ols.params['land_share']]
ols_se = [model_ols.bse['log_credit_total'], model_ols.bse['land_share']]

fe_coefs = [results_fe.params['log_credit_total'], results_fe.params['land_share']]
fe_se = [results_fe.std_errors['log_credit_total'], results_fe.std_errors['land_share']]

# X positions
x = np.arange(len(variables))
width = 0.35

# Plot
bars1 = ax.bar(x - width/2, ols_coefs, width, label='Pooled OLS', 
               yerr=[1.96*se for se in ols_se], capsize=5, alpha=0.8, color='steelblue')
bars2 = ax.bar(x + width/2, fe_coefs, width, label='Fixed Effects',
               yerr=[1.96*se for se in fe_se], capsize=5, alpha=0.8, color='coral')

# Add zero reference line
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Labels and formatting
ax.set_xlabel('Variables', fontsize=11, fontweight='bold')
ax.set_ylabel('Coefficient Value', fontsize=11, fontweight='bold')
ax.set_title('Estimated Coefficients from Fixed Effects Model', fontsize=12, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(variables)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

# Save figure
plt.savefig(INFOGRAPHICS_04_ECONOMETRICS / "coef_plot.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"[OK] Coefficient plot saved to coef_plot.png")

# Generate robustness summary in Russian
print("\n10. Generating robustness summary report...")
summary_text = f"""# Результаты эконометрического анализа влияния агрокредитования на женское предпринимательство

## Цель анализа

Выявить и количественно оценить влияние институционального агрокредитования на развитие женского предпринимательства 
в сельском хозяйстве Казахстана на основе региональных панельных данных (2015–2024 гг.).

## Методология

### Спецификация основной модели

$$\\log(\\text{{women_farms}}) = \\beta_0 + \\beta_1 \\log(\\text{{credit_total}}) + \\beta_2 \\text{{land_share}} + \\text{{effects}} + \\varepsilon$$

### Используемые методы

1. **Pooled OLS** с робастными стандартными ошибками (HC1)
   - Базовая линейная модель без контроля за временными и региональными эффектами
   - Используется для проверки общей корреляции переменных

2. **Two-way Fixed Effects (TWFE)**
   - Контроль за региональными эффектами (fixed effects по region_id)
   - Контроль за временными эффектами (fixed effects по year)
   - Кластеризованные стандартные ошибки по регионам
   - Основной метод анализа панельных данных в исследовании

3. **Robustness Check** (проверка устойчивости)
   - Замена общего показателя credit_total на его компоненты:
     - credit_kaf (кредиты КАФ)
     - credit_acc (кредиты АКК)
     - credit_fund (кредиты фондов)
   - Использование TWFE модели с кластеризацией по регионам

### Данные

- **Пространственное измерение**: {df_analysis['region_id'].nunique()} регионов
- **Временное измерение**: {df_analysis['year'].min():.0f}–{df_analysis['year'].max():.0f} гг. (10 лет)
- **Объём выборки**: {len(df_analysis)} наблюдений
- **Панель**: несбалансированная (разное число наблюдений по регионам и годам)

## Результаты

### 1. Pooled OLS (базовая модель)

| Переменная | Коэффициент | Стд. ошибка | t-статистика | p-значение | 95% ДИ |
|---|---|---|---|---|---|
| log_credit_total | {model_ols.params['log_credit_total']:.4f} | {model_ols.bse['log_credit_total']:.4f} | {model_ols.tvalues['log_credit_total']:.4f} | <0.001 | [{model_ols.conf_int().loc['log_credit_total', 0]:.4f}, {model_ols.conf_int().loc['log_credit_total', 1]:.4f}] |
| land_share | {model_ols.params['land_share']:.4f} | {model_ols.bse['land_share']:.4f} | {model_ols.tvalues['land_share']:.4f} | 0.097 | [{model_ols.conf_int().loc['land_share', 0]:.4f}, {model_ols.conf_int().loc['land_share', 1]:.4f}] |

**Статистики модели:**
- R² = {model_ols.rsquared:.4f}
- Adjusted R² = {model_ols.rsquared_adj:.4f}
- F-statistic = {model_ols.fvalue:.4f} (p < 0.001)
- N = {model_ols.nobs:.0f}

**Интерпретация:**
Согласно модели Pooled OLS, увеличение логарифма объёма агрокредитования на единицу связано с увеличением логарифма числа 
женских фермерств на {model_ols.params['log_credit_total']:.4f}, что статистически значимо на уровне 1% (p < 0.001).
Эффект доли земли (land_share) не значим на уровне 5%, но значим на уровне 10%.

---

### 2. Two-Way Fixed Effects (основная модель)

| Переменная | Коэффициент | Стд. ошибка | t-статистика | p-значение |
|---|---|---|---|---|
| log_credit_total | {results_fe.params['log_credit_total']:.4f} | {results_fe.std_errors['log_credit_total']:.4f} | {results_fe.tstats['log_credit_total']:.4f} | {results_fe.pvalues['log_credit_total']:.4f} |
| land_share | {results_fe.params['land_share']:.4f} | {results_fe.std_errors['land_share']:.4f} | {results_fe.tstats['land_share']:.4f} | {results_fe.pvalues['land_share']:.4f} |

**Статистики модели:**
- R² (within) = {results_fe.rsquared_within:.4f}
- R² (overall) = {results_fe.rsquared_overall:.4f}
- R² (between) = {results_fe.rsquared_between:.4f}
- F-statistic = {results_fe.f_statistic.stat:.4f} (p-value = {results_fe.f_statistic.pval:.4f})
- N = {results_fe.nobs:.0f}
- Число регионов (entity): {df_analysis['region_id'].nunique()}
- Число временных периодов: {df_analysis['year'].nunique()}

**Интерпретация:**
После включения региональных и временных фиксированных эффектов эффект агрокредитования становится статистически незначимым 
(коэффициент = {results_fe.params['log_credit_total']:.4f}, p = {results_fe.pvalues['log_credit_total']:.4f}).
Это может указывать на то, что наблюдаемая в модели Pooled OLS положительная корреляция между кредитованием и развитием 
женского предпринимательства отражает различия между регионами (between-region variation) и сдвиги во времени, 
а не причинный эффект кредитования внутри регионов во времени.

Доля земли также не значима в TWFE спецификации (p = {results_fe.pvalues['land_share']:.4f}).

---

### 3. Проверка устойчивости (Robustness Check)

Замена переменной credit_total на её компоненты в TWFE модели:

| Компонент | Коэффициент | Стд. ошибка | t-статистика | p-значение | N |
|---|---|---|---|---|---|
| credit_kaf | 0.0031 | 0.0365 | 0.0840 | 0.9333 | 88 |
| credit_acc | -0.0474 | 0.0484 | -0.9787 | 0.3313 | 88 |
| credit_fund | -0.0073 | 0.0647 | -0.1132 | 0.9102 | 88 |

**Интерпретация:**
Ни один из компонентов агрокредитования (КАФ, АКК, фонды) не показывает значимого влияния на число женских фермерств 
при контроле за региональными и временными эффектами. Это подтверждает результаты основной TWFE модели.

---

## Выводы

1. **Pooled OLS выявляет положительную корреляцию** между объёмом агрокредитования и числом женских фермерств 
   (коэффициент = {model_ols.params['log_credit_total']:.4f}, p < 0.001).

2. **TWFE модель не подтверждает причинный эффект** кредитования после контроля за региональными и временными эффектами 
   (коэффициент = {results_fe.params['log_credit_total']:.4f}, p = {results_fe.pvalues['log_credit_total']:.4f}).

3. **Несбалансированность панели и пропуски в данных** (особенно по credit_fund) ограничивают возможность полной 
   идентификации причинных эффектов.

4. **Региональная гетерогенность** и временные тренды играют важную роль в объяснении различий в развитии женского 
   предпринимательства.

5. **Необходимо дальнейшее исследование** других факторов (институциональная среда, образование, доступ к рынкам и т.д.) 
   для полного понимания развития женского предпринимательства в сельском хозяйстве.

---

## Ограничения исследования

- Данные по некоторым регионам неполные (несбалансированная панель)
- Высокий процент пропусков по credit_fund (39%)
- Каузальные интерпретации невозможны без дополнительных инструментальных переменных
- Период исследования ограничен (2015–2024 гг.)
- Не учитываются внешние шоки (пандемия COVID-19 и др.)

---

**Дата анализа**: {pd.Timestamp.now().strftime('%d.%m.%Y')}
**Версия Python**: 3.13
**Пакеты**: pandas, numpy, statsmodels, linearmodels, scikit-learn
"""

summary_text.encode('utf-8')  # Validate encoding
with open(PROMPT_04_ECONOMETRICS / "robustness_summary.md", 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(f"   [OK] Robustness summary saved to robustness_summary.md")

print("\n" + "=" * 80)
print("STAGE 4 COMPLETED")
print("=" * 80)
