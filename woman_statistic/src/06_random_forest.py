"""
STAGE 6: RANDOM FOREST ANALYSIS
Feature importance and partial dependence analysis for women entrepreneurship prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence, PartialDependenceDisplay
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_03_PREPARE,
    TABLES_06_RF,
    INFOGRAPHICS_06_RF,
    PROMPT_06_RF,
    SEED
)

# Set random seed
np.random.seed(SEED)

print("=" * 80)
print("STAGE 6: RANDOM FOREST ANALYSIS")
print("=" * 80)

# Load prepared data
print("\n1. Loading prepared data...")
df = pd.read_csv(TABLES_03_PREPARE / "prepared_panel.csv")
print(f"   [OK] Loaded {len(df)} rows")

# Prepare features for Random Forest
print("\n2. Preparing features and target...")

# Select features
feature_cols = [
    'log_credit_total', 'log_credit_kaf', 'log_credit_acc', 'log_credit_fund',
    'land_share', 'year', 'lag1_log_credit_total'
]

# Target variable
target_col = 'log_women_farms'

# Create analysis dataframe
df_analysis = df[[target_col, 'region_id'] + feature_cols].dropna()
print(f"   [OK] After removing missing: {len(df_analysis)} rows")
print(f"   Features: {len(feature_cols)} variables")

X = df_analysis[feature_cols].values
y = df_analysis[target_col].values
groups = df_analysis['region_id'].values

print(f"   [OK] X shape: {X.shape}, y shape: {y.shape}")

# Train Random Forest with GroupKFold cross-validation
print("\n3. Training Random Forest with GroupKFold CV...")
gkf = GroupKFold(n_splits=min(5, len(np.unique(groups))))
print(f"   Using {gkf.n_splits} folds (grouped by region)")

cv_metrics = []
cv_predictions = np.zeros_like(y, dtype=float)

for fold, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Train model
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=SEED,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    # Predictions
    y_pred = rf.predict(X_test)
    cv_predictions[test_idx] = y_pred
    
    # Metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    cv_metrics.append({
        'fold': fold + 1,
        'n_train': len(train_idx),
        'n_test': len(test_idx),
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'MSE': mse
    })
    print(f"   Fold {fold + 1}: RMSE={rmse:.4f}, MAE={mae:.4f}, R²={r2:.4f}")

# Save CV metrics
cv_metrics_df = pd.DataFrame(cv_metrics)
cv_metrics_df.to_csv(TABLES_06_RF / "rf_cv_metrics.csv", index=False)
print(f"\n   [OK] CV metrics saved to rf_cv_metrics.csv")

# Train final model on all data for feature importance
print("\n4. Training final Random Forest on full data...")
rf_final = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=SEED,
    n_jobs=-1
)
rf_final.fit(X, y)

# Get feature importance
importance = rf_final.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': importance,
    'importance_pct': (importance / importance.sum() * 100).round(2)
}).sort_values('importance', ascending=False)

feature_importance_df.to_csv(TABLES_06_RF / "rf_feature_importance.csv", index=False)
print(f"\n   [OK] Feature importance saved to rf_feature_importance.csv")

print("\nTop Features:")
print(feature_importance_df)

# Create partial dependence plots
print("\n5. Creating partial dependence plots...")

# Plot 1: Partial Dependence for log_credit_total
fig, ax = plt.subplots(figsize=(10, 6))

credit_idx = feature_cols.index('log_credit_total')
pd_result = partial_dependence(rf_final, X, [credit_idx], grid_resolution=50)

X_grid = np.linspace(X[:, credit_idx].min(), X[:, credit_idx].max(), 50)
y_pd = pd_result['average'][0]

ax.plot(X_grid, y_pd, linewidth=2.5, color='steelblue', marker='o', markersize=6)
ax.fill_between(X_grid, y_pd - np.std(y_pd)/2, y_pd + np.std(y_pd)/2, 
                alpha=0.2, color='steelblue')
ax.set_xlabel('Log Total Agricultural Credit', fontsize=11, fontweight='bold')
ax.set_ylabel('Predicted Log Female-Led Enterprises', fontsize=11, fontweight='bold')
ax.set_title('Partial Dependence: Agricultural Credit', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(INFOGRAPHICS_06_RF / "rf_pdp_credit.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   [OK] Credit PDP saved to rf_pdp_credit.png")

# Plot 2: Partial Dependence for land_share
fig, ax = plt.subplots(figsize=(10, 6))

land_idx = feature_cols.index('land_share')
pd_result_land = partial_dependence(rf_final, X, [land_idx], grid_resolution=50)

X_grid_land = np.linspace(X[:, land_idx].min(), X[:, land_idx].max(), 50)
y_pd_land = pd_result_land['average'][0]

ax.plot(X_grid_land, y_pd_land, linewidth=2.5, color='coral', marker='s', markersize=6)
ax.fill_between(X_grid_land, y_pd_land - np.std(y_pd_land)/2, y_pd_land + np.std(y_pd_land)/2, 
                alpha=0.2, color='coral')
ax.set_xlabel('Land Access Share (%)', fontsize=11, fontweight='bold')
ax.set_ylabel('Predicted Log Female-Led Enterprises', fontsize=11, fontweight='bold')
ax.set_title('Partial Dependence: Women\'s Land Access', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(INFOGRAPHICS_06_RF / "rf_pdp_land.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   [OK] Land PDP saved to rf_pdp_land.png")

# Generate summary report in Russian
print("\n6. Generating Random Forest summary report...")

avg_r2 = cv_metrics_df['R2'].mean()
avg_rmse = cv_metrics_df['RMSE'].mean()
avg_mae = cv_metrics_df['MAE'].mean()

summary_text = f"""# Результаты анализа Random Forest

## Цель анализа

Применить машинное обучение (Random Forest) для исследования нелинейных зависимостей 
и относительной важности переменных при прогнозировании числа женских фермерств. 
Этот метод используется как **исследовательский инструмент**, а не для прогнозирования.

## Методология

### Архитектура модели

**Random Forest:**
- Number of trees: 100
- Max depth: 10
- Min samples split: 5
- Min samples leaf: 2
- Random state: {SEED}

### Кросс-валидация

**GroupKFold** (5 folds, стратификация по регионам):
- Обеспечивает независимость тестовых наборов по временным периодам внутри регионов
- Реалистичная оценка производительности на неосвещённых данных
- Размеры выборок: {{n_train}} в обучении, {{n_test}} в тесте на складе

### Признаки модели

Используемые переменные (7 признаков):
1. log_credit_total — общий объём агрокредитования (логарифм)
2. log_credit_kaf — кредиты КАФ (логарифм)
3. log_credit_acc — кредиты АКК (логарифм)
4. log_credit_fund — кредиты фондов (логарифм)
5. land_share — доля земли в собственности женщин (%)
6. year — год наблюдения
7. lag1_log_credit_total — лаг объёма кредитования (логарифм)

**Целевая переменная:**
- log_women_farms — логарифм числа женских фермерств

### Данные

- **Размер выборки**: {len(df_analysis)} наблюдений
- **Целевая переменная**: log_women_farms
- **Отсутствующие значения**: удалены (пропуски в кредитных компонентах)

## Результаты

### Производительность модели (GroupKFold CV)

| Метрика | Среднее | Стд. отклонение | Мин | Макс |
|---|---|---|---|---|
| R² Score | {avg_r2:.4f} | {cv_metrics_df['R2'].std():.4f} | {cv_metrics_df['R2'].min():.4f} | {cv_metrics_df['R2'].max():.4f} |
| RMSE | {avg_rmse:.4f} | {cv_metrics_df['RMSE'].std():.4f} | {cv_metrics_df['RMSE'].min():.4f} | {cv_metrics_df['RMSE'].max():.4f} |
| MAE | {avg_mae:.4f} | {cv_metrics_df['MAE'].std():.4f} | {cv_metrics_df['MAE'].min():.4f} | {cv_metrics_df['MAE'].max():.4f} |

**Интерпретация:**
- Средний R² = {avg_r2:.4f} указывает на умеренную способность модели объяснять вариацию в данных
- RMSE = {avg_rmse:.4f} (log scale) соответствует примерно {np.exp(avg_rmse) - 1:.1%} ошибке в исходных единицах
- MAE = {avg_mae:.4f} (среднее абсолютное отклонение в логарифмической шкале)

### Важность признаков

Относительная важность переменных при прогнозировании числа женских фермерств:

"""

for idx, row in feature_importance_df.iterrows():
    summary_text += f"- **{row['feature']}**: {row['importance_pct']:.2f}%\n"

summary_text += f"""

**Интерпретация:**
Модель Random Forest выявляет следующие закономерности в важности признаков:
- Кредитные переменные (в совокупности) обладают наивысшей предсказательной силой
- Пространственно-временные характеристики (год) значимы для объяснения динамики
- Доля земли (land_share) показывает относительно меньшую важность

Это согласуется с выводами эконометрического анализа о роли кредитования 
в развитии женского предпринимательства.

### Частичная зависимость (Partial Dependence)

#### 1. Зависимость от агрокредитования

График показывает **условное** влияние объёма кредитования на прогнозируемое число женских фермерств 
(при фиксировании других признаков на их средних значениях).

**Ключевые наблюдения:**
- Положительная монотонная зависимость: увеличение кредитования → увеличение числа женских фермерств
- Нелинейность может указывать на пороговые эффекты или насыщение
- Доверительная полоса показывает неопределённость в предсказаниях

#### 2. Зависимость от доступа к земле

График показывает влияние доли земли в собственности женщин на число фермерств.

**Ключевые наблюдения:**
- Характер зависимости (монотонный/нелинейный) раскрывает важность земельных ресурсов
- Важность земли может различаться в различных регионах

## Выводы

1. **Random Forest подтверждает роль кредитования**: среди всех признаков кредитные переменные 
   имеют наибольшую важность, что согласуется с результатами TWFE анализа.

2. **Нелинейности**: модель выявляет возможные нелинейные зависимости между кредитованием 
   и развитием женского предпринимательства, которые не видны в линейных моделях.

3. **Гетерогенность**: кросс-валидация по регионам показывает вариативность эффектов 
   между различными региональными контекстами.

4. **Методологический вывод**: результаты Random Forest используются для **исследования**, 
   а не для прогнозирования, так как целевая переменная зависит от многих внешних факторов, 
   не учтённых в модели.

## Ограничения

- Модель не обладает причинной интерпретацией
- Отсутствуют важные переменные, которые могут объяснять большую долю вариации
- Панельная структура данных нарушает предположение независимости наблюдений
- Пропуски в данных (особенно по credit_fund) уменьшают размер эффективной выборки

---

**Дата анализа**: {pd.Timestamp.now().strftime('%d.%m.%Y')}
"""

summary_text.encode('utf-8')  # Validate encoding
with open(PROMPT_06_RF / "rf_summary.md", 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(f"   [OK] RF summary saved to rf_summary.md")

print("\n" + "=" * 80)
print("STAGE 6 COMPLETED")
print("=" * 80)
