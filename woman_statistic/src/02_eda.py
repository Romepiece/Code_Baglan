"""
ЭТАП 2: ОПИСАТЕЛЬНЫЙ АНАЛИЗ (EDA)

Задачи:
- Рассчитать описательную статистику
- Построить графики динамики women_farms и credit_total по годам
- Построить scatter: log_credit_total vs log_women_farms
- Сохранить таблицы и графики в output/ подпапки
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Импорт конфигурации
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_01_VALIDATE,
    TABLES_02_EDA,
    INFOGRAPHICS_02_EDA,
    SEED
)

# Установка стиля
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
np.random.seed(SEED)

print("=" * 80)
print("ЭТАП 2: ОПИСАТЕЛЬНЫЙ АНАЛИЗ (EDA)")
print("=" * 80)

# Загрузка данных
print("\n1. Загрузка данных...")
df = pd.read_csv(TABLES_01_VALIDATE / "raw_panel_data.csv")
print(f"   ✓ Загружено {len(df)} строк")

# Описательная статистика
print("\n2. Описательная статистика по ключевым переменным...")
key_vars = ["women_farms", "credit_total", "credit_kaf", "credit_acc", 
            "credit_fund", "land_share", "log_women_farms", "log_credit_total"]

descriptive_stats = df[key_vars].describe().round(4).T
descriptive_stats.columns = ["Count", "Mean", "Std", "Min", "25%", "50%", "75%", "Max"]
print(descriptive_stats)
descriptive_stats.to_csv(TABLES_02_EDA / "descriptive_statistics.csv")
print(f"   ✓ Сохранено: descriptive_statistics.csv")

# Динамика women_farms по годам
print("\n3. Анализ динамики women_farms по годам...")
women_farms_by_year = df.groupby("year")["women_farms"].agg(["count", "mean", "sum", "std"]).round(2)
women_farms_by_year.columns = ["N_Regions", "Mean_Farms", "Total_Farms", "Std"]
print(women_farms_by_year)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(women_farms_by_year.index, women_farms_by_year["Mean_Farms"], 
        marker='o', linewidth=2.5, markersize=8, color='#2E86AB', label='Mean number of farms')
ax.fill_between(women_farms_by_year.index, 
                women_farms_by_year["Mean_Farms"] - women_farms_by_year["Std"],
                women_farms_by_year["Mean_Farms"] + women_farms_by_year["Std"],
                alpha=0.2, color='#2E86AB')
ax.set_xlabel("Year", fontsize=11, fontweight='bold')
ax.set_ylabel("Average number of women-led farms", fontsize=11, fontweight='bold')
ax.set_title("Dynamics of female entrepreneurship development in agriculture (women_farms)", 
             fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(INFOGRAPHICS_02_EDA / "avg_women_farms_over_time.png", dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: avg_women_farms_over_time.png")
plt.close()

# Динамика credit_total по годам
print("\n4. Анализ динамики credit_total по годам...")
credit_by_year = df.groupby("year")["credit_total"].agg(["count", "mean", "sum", "std"]).round(2)
credit_by_year.columns = ["N_Regions", "Mean_Credit", "Total_Credit", "Std"]
print(credit_by_year)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(credit_by_year.index, credit_by_year["Mean_Credit"], 
        marker='s', linewidth=2.5, markersize=8, color='#A23B72', label='Average credit volume')
ax.fill_between(credit_by_year.index,
                credit_by_year["Mean_Credit"] - credit_by_year["Std"],
                credit_by_year["Mean_Credit"] + credit_by_year["Std"],
                alpha=0.2, color='#A23B72')
ax.set_xlabel("Year", fontsize=11, fontweight='bold')
ax.set_ylabel("Average agricultural credit volume (mln KZT)", fontsize=11, fontweight='bold')
ax.set_title("Dynamics of agricultural credit provision to women farmers", 
             fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(INFOGRAPHICS_02_EDA / "avg_credit_total_over_time.png", dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: avg_credit_total_over_time.png")
plt.close()

# Scatter: log_credit_total vs log_women_farms
print("\n5. Анализ связи credit_total и women_farms...")
scatter_data = df[["log_credit_total", "log_women_farms", "year"]].dropna()
correlation = scatter_data[["log_credit_total", "log_women_farms"]].corr().iloc[0, 1]
print(f"   Корреляция: {correlation:.4f}")

fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(scatter_data["log_credit_total"], scatter_data["log_women_farms"],
                     c=scatter_data["year"], cmap='viridis', s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
ax.set_xlabel("log(1 + credit_total), mln KZT", fontsize=11, fontweight='bold')
ax.set_ylabel("log(1 + women_farms)", fontsize=11, fontweight='bold')
ax.set_title(f"Relationship between agricultural credit and female entrepreneurship development\n(Correlation: {correlation:.3f})",
             fontsize=12, fontweight='bold')

# Add trend line
z = np.polyfit(scatter_data["log_credit_total"], scatter_data["log_women_farms"], 1)
p = np.poly1d(z)
x_line = np.linspace(scatter_data["log_credit_total"].min(), scatter_data["log_credit_total"].max(), 100)
ax.plot(x_line, p(x_line), "r--", linewidth=2, alpha=0.8, label=f"Trend: y={z[0]:.3f}x+{z[1]:.3f}")

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Year", fontsize=10, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10, loc='upper left')
plt.tight_layout()
plt.savefig(INFOGRAPHICS_02_EDA / "scatter_log_credit_vs_log_women.png", dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: scatter_log_credit_vs_log_women.png")
plt.close()

# Таблица по компонентам кредитов
print("\n6. Анализ компонентов агрокредитования...")
credit_components = df[["year", "credit_kaf", "credit_acc", "credit_fund"]].groupby("year").mean().round(2)
print(credit_components)
credit_components.to_csv(TABLES_02_EDA / "credit_components_by_year.csv")
print(f"   ✓ Сохранено: credit_components_by_year.csv")

# Статистика по регионам
print("\n7. Анализ по регионам...")
regional_stats = df.groupby("region_name_en").agg({
    "women_farms": "mean",
    "credit_total": "mean",
    "land_share": "mean",
    "year": "count"
}).round(2)
regional_stats.columns = ["Avg_Women_Farms", "Avg_Credit_Total", "Avg_Land_Share", "N_Obs"]
regional_stats = regional_stats.sort_values("Avg_Women_Farms", ascending=False)
print(regional_stats.head(10))
regional_stats.to_csv(TABLES_02_EDA / "regional_statistics.csv")
print(f"   ✓ Сохранено: regional_statistics.csv")

print("\n" + "=" * 80)
print("ЭТАП 2 ЗАВЕРШЁН")
print("=" * 80)
print(f"\nВыходные файлы:")
print(f"  Таблицы ({TABLES_02_EDA}):")
print(f"    - descriptive_statistics.csv")
print(f"    - credit_components_by_year.csv")
print(f"    - regional_statistics.csv")
print(f"  Графики ({INFOGRAPHICS_02_EDA}):")
print(f"    - avg_women_farms_over_time.png")
print(f"    - avg_credit_total_over_time.png")
print(f"    - scatter_log_credit_vs_log_women.png")
