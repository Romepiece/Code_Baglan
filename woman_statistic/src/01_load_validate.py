"""
ЭТАП 1: ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ

Задачи:
- Читать sheet="panel" из Excel
- Проверить типы данных
- Проверить уникальность (region_id, year)
- Создать таблицы пропусков
- Создать краткое описание выборки
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

# Импорт конфигурации
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    DATA_PATH, 
    TABLES_01_VALIDATE,
    SEED
)

warnings.filterwarnings('ignore')

# Установка random seed для воспроизводимости
np.random.seed(SEED)

print("=" * 80)
print("ЭТАП 1: ЗАГРУЗКА И ВАЛИДАЦИЯ ДАННЫХ")
print("=" * 80)

# 1. Загрузка данных
print("\n1. Загрузка данных из Excel...")
print(f"   Путь: {DATA_PATH}")
df = pd.read_excel(DATA_PATH, sheet_name="panel")
print(f"   ✓ Загружено {len(df)} строк и {len(df.columns)} столбцов")
print(f"   ✓ Датасет занимает {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# 2. Проверка типов данных
print("\n2. Проверка типов данных...")
print("\nТипы данных:")
print(df.dtypes)

# 3. Первые строки
print("\n3. Первые строки данных:")
print(df.head())

# 4. Проверка уникальности ключа (region_id, year)
print("\n4. Проверка уникальности ключа (region_id, year)...")
total_rows = len(df)
unique_keys = df[["region_id", "year"]].drop_duplicates().shape[0]
print(f"   Всего строк: {total_rows}")
print(f"   Уникальных (region_id, year): {unique_keys}")
if total_rows == unique_keys:
    print("   ✓ Ключ уникален (панель не имеет дублей)")
else:
    print("   ⚠ ВНИМАНИЕ: Обнаружены дубли!")
    dups = df[df.duplicated(subset=["region_id", "year"], keep=False)]
    print(dups.sort_values(["region_id", "year"]))

# 5. Диапазон наблюдений
print("\n5. Диапазон наблюдений...")
years = sorted(df["year"].unique())
print(f"   Годы: {min(years)} — {max(years)}")
print(f"   Уникальных лет: {len(years)}")
print(f"   Регионы ({df['region_id'].nunique()}): {sorted(df['region_id'].unique())}")

# 6. Матрица пропусков по переменным
print("\n6. Матрица пропусков по переменным...")
missing_by_var = pd.DataFrame({
    "Variable": df.columns,
    "Missing_Count": df.isnull().sum(),
    "Missing_Percent": (df.isnull().sum() / len(df) * 100).round(2)
})
missing_by_var = missing_by_var[missing_by_var["Missing_Count"] > 0].sort_values("Missing_Count", ascending=False)
print(missing_by_var.to_string(index=False))
missing_by_var.to_csv(TABLES_01_VALIDATE / "missing_overall.csv", index=False)
print(f"   ✓ Сохранено: missing_overall.csv")

# 7. Матрица пропусков по годам
print("\n7. Матрица пропусков по годам...")
missing_by_year = df.groupby("year").apply(lambda x: x.isnull().sum())
missing_by_year = missing_by_year.assign(
    Total_Rows=df.groupby("year").size(),
    Region_Count=df.groupby("year")["region_id"].nunique()
)
print(missing_by_year)
missing_by_year.to_csv(TABLES_01_VALIDATE / "missing_by_year.csv")
print(f"   ✓ Сохранено: missing_by_year.csv")

# 8. Краткое описание выборки
print("\n8. Краткое описание выборки...")
sample_summary = pd.DataFrame({
    "Metric": [
        "Total Observations",
        "Total Years",
        "Year Range",
        "Total Regions",
        "Unbalanced Panel",
        "Min Regions per Year",
        "Max Regions per Year",
        "Key Variable: women_farms - Missing",
        "Key Variable: credit_total - Missing",
        "Key Variable: land_share - Missing"
    ],
    "Value": [
        len(df),
        len(years),
        f"{min(years)}-{max(years)}",
        df['region_id'].nunique(),
        "Yes (see missing_by_year.csv)",
        df.groupby("year")["region_id"].nunique().min(),
        df.groupby("year")["region_id"].nunique().max(),
        f"{df['women_farms'].isnull().sum()} ({df['women_farms'].isnull().sum()/len(df)*100:.2f}%)",
        f"{df['credit_total'].isnull().sum()} ({df['credit_total'].isnull().sum()/len(df)*100:.2f}%)",
        f"{df['land_share'].isnull().sum()} ({df['land_share'].isnull().sum()/len(df)*100:.2f}%)"
    ]
})
print(sample_summary.to_string(index=False))
sample_summary.to_csv(TABLES_01_VALIDATE / "sample_summary.csv", index=False)
print(f"   ✓ Сохранено: sample_summary.csv")

# 9. Описательная статистика
print("\n9. Описательная статистика ключевых переменных...")
descriptive = df[["women_farms", "credit_total", "credit_kaf", "credit_acc", 
                   "credit_fund", "land_share"]].describe().round(4)
print(descriptive)

# 10. Проверка логарифмов
print("\n10. Проверка логарифмических переменных...")
if "log_women_farms" in df.columns:
    print(f"   ✓ log_women_farms найден: {df['log_women_farms'].notna().sum()} значений")
else:
    print("   ✗ log_women_farms отсутствует")
    
if "log_credit_total" in df.columns:
    print(f"   ✓ log_credit_total найден: {df['log_credit_total'].notna().sum()} значений")
else:
    print("   ✗ log_credit_total отсутствует")

# 11. Сохранение полного датасета для дальнейшей обработки
print("\n11. Сохранение исходного датасета...")
df.to_csv(TABLES_01_VALIDATE / "raw_panel_data.csv", index=False)
print(f"   ✓ Сохранено: raw_panel_data.csv")

print("\n" + "=" * 80)
print("ЭТАП 1 ЗАВЕРШЁН")
print("=" * 80)
print(f"\nВыходные файлы в {TABLES_01_VALIDATE}:")
print(f"  - missing_overall.csv")
print(f"  - missing_by_year.csv")
print(f"  - sample_summary.csv")
print(f"  - raw_panel_data.csv")
