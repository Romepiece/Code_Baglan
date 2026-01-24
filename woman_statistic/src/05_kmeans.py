"""
STAGE 5: K-MEANS CLUSTERING ANALYSIS
Regional clustering based on women entrepreneurship patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_03_PREPARE,
    TABLES_05_KMEANS,
    INFOGRAPHICS_05_KMEANS,
    PROMPT_05_KMEANS,
    SEED
)

# Set random seed
np.random.seed(SEED)

print("=" * 80)
print("STAGE 5: K-MEANS CLUSTERING ANALYSIS")
print("=" * 80)

# Load prepared data
print("\n1. Loading prepared data...")
df = pd.read_csv(TABLES_03_PREPARE / "prepared_panel.csv")
print(f"   [OK] Loaded {len(df)} rows")

# Aggregate data by region
print("\n2. Creating regional features for clustering...")
regional_data = df.groupby('region_id').agg({
    'log_women_farms': ['mean', 'std', 'min', 'max'],
    'log_credit_total': ['mean', 'std', 'min', 'max'],
    'land_share': 'mean',
    'year': 'count'
}).reset_index()

regional_data.columns = ['_'.join(col).strip('_') for col in regional_data.columns.values]
regional_data.rename(columns={
    'region_id': 'region_id',
    'year_count': 'n_years'
}, inplace=True)

print(f"   [OK] Aggregated data for {len(regional_data)} regions")

# Calculate trend slopes (growth dynamics)
print("\n3. Computing trend slopes by region...")
trend_data = []
for region_id in df['region_id'].unique():
    region_df = df[df['region_id'] == region_id].sort_values('year')
    if len(region_df) > 1:
        # Linear trend for women farms
        years = region_df['year'].values.reshape(-1, 1)
        women_farms = region_df['log_women_farms'].values
        valid_mask = ~np.isnan(women_farms)
        if valid_mask.sum() > 1:
            slope = np.polyfit(years[valid_mask].flatten(), women_farms[valid_mask], 1)[0]
        else:
            slope = np.nan
        trend_data.append({'region_id': region_id, 'women_farms_trend': slope})

trend_df = pd.DataFrame(trend_data)
regional_data = regional_data.merge(trend_df, on='region_id', how='left')

print(f"   [OK] Computed trend slopes for {len(trend_df)} regions")

# Save regional features
regional_data.to_csv(TABLES_05_KMEANS / "kmeans_region_features.csv", index=False)
print(f"\n   [OK] Regional features saved to kmeans_region_features.csv")

# Prepare features for clustering
print("\n4. Preparing features for K-Means...")
clustering_features = regional_data[
    ['log_women_farms_mean', 'log_women_farms_std', 
     'log_credit_total_mean', 'log_credit_total_std',
     'land_share_mean', 'women_farms_trend']
].fillna(0)

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(clustering_features)
print(f"   [OK] Features standardized: {X_scaled.shape}")

# Find optimal K using silhouette score
print("\n5. Finding optimal number of clusters...")
silhouette_scores = []
K_range = range(2, min(7, len(regional_data)))  # K from 2 to 6

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=SEED, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores.append({'K': k, 'silhouette_score': score})
    print(f"   K={k}: silhouette_score = {score:.4f}")

silhouette_df = pd.DataFrame(silhouette_scores)
optimal_k = silhouette_df.loc[silhouette_df['silhouette_score'].idxmax(), 'K']
print(f"\n   [OK] Optimal K = {optimal_k}")

# Train final K-Means model
print(f"\n6. Training K-Means with K={optimal_k}...")
kmeans_final = KMeans(n_clusters=int(optimal_k), random_state=SEED, n_init=10)
clusters = kmeans_final.fit_predict(X_scaled)
regional_data['cluster'] = clusters

print(f"   [OK] Clustering completed")

# Save cluster assignments
assignments_df = regional_data[['region_id', 'cluster']].copy()
assignments_df.to_csv(TABLES_05_KMEANS / "kmeans_assignments.csv", index=False)
print(f"   [OK] Cluster assignments saved to kmeans_assignments.csv")

# Create cluster profiles
print("\n7. Creating cluster profiles...")
cluster_profiles = regional_data.groupby('cluster').agg({
    'log_women_farms_mean': 'mean',
    'log_credit_total_mean': 'mean',
    'land_share_mean': 'mean',
    'women_farms_trend': 'mean',
    'region_id': 'count'
}).round(4)
cluster_profiles.rename(columns={'region_id': 'n_regions'}, inplace=True)

cluster_profiles.to_csv(TABLES_05_KMEANS / "kmeans_cluster_profiles.csv")
print(f"   [OK] Cluster profiles saved to kmeans_cluster_profiles.csv")
print("\nCluster Profiles:")
print(cluster_profiles)

# Create visualization
print("\n8. Creating cluster visualization...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter plot: women_farms vs credit
scatter = axes[0].scatter(regional_data['log_credit_total_mean'], 
                          regional_data['log_women_farms_mean'],
                          c=regional_data['cluster'], cmap='viridis',
                          s=200, alpha=0.7, edgecolors='black', linewidth=1.5)
axes[0].set_xlabel('Average Credit (log scale)', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Average Women Farms (log scale)', fontsize=11, fontweight='bold')
axes[0].set_title('K-Means Clustering: Credit vs Women Entrepreneurship', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[0])
cbar.set_label('Cluster', fontsize=10)

# Bar plot: cluster sizes
cluster_counts = regional_data['cluster'].value_counts().sort_index()
axes[1].bar(cluster_counts.index, cluster_counts.values, color='steelblue', alpha=0.7, edgecolor='black')
axes[1].set_xlabel('Cluster', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Number of Regions', fontsize=11, fontweight='bold')
axes[1].set_title('Cluster Distribution', fontsize=12, fontweight='bold')
axes[1].set_xticks(range(int(optimal_k)))
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(INFOGRAPHICS_05_KMEANS / "kmeans_clusters.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"   [OK] Cluster visualization saved to kmeans_clusters.png")

# Generate summary report in Russian
print("\n9. Generating summary report...")
summary_text = """# Результаты K-Means кластеризации регионов

## Методология
- Признаки кластеризации:
  - Среднее логарифмированное число женских фермерств
  - Стандартное отклонение женских фермерств
  - Среднее логарифмированное значение сельскохозяйственного кредита
  - Стандартное отклонение сельскохозяйственного кредита
  - Среднее значение доли земли
  - Тренд развития женских фермерств (линейный наклон по времени)

- Оптимальное число кластеров: K = {k} (по максимуму Silhouette Score)
- Метод стандартизации: StandardScaler
- Семя случайности: {seed}

## Оптимальность кластеризации
Silhouette Score по числу кластеров:
{silhouette_table}

## Профили кластеров

{profiles_table}

## Интерпретация

Кластеризация выявила {k} групп регионов с различными характеристиками развития женского предпринимательства в сельском хозяйстве:

{interpretations}

## Распределение регионов по кластерам

{cluster_distribution}

## Файлы результатов
- `kmeans_region_features.csv` - Признаки каждого региона
- `kmeans_assignments.csv` - Назначение регионов кластерам
- `kmeans_cluster_profiles.csv` - Профили кластеров
- `kmeans_clusters.png` - Визуализация кластеров
"""

# Create silhouette table
silhouette_table = "\n".join([f"K={row['K']}: {row['silhouette_score']:.4f}" 
                               for _, row in silhouette_df.iterrows()])

# Create profiles table
profiles_text = []
for cluster_id in sorted(regional_data['cluster'].unique()):
    profile = cluster_profiles.loc[cluster_id]
    profiles_text.append(f"""
### Кластер {cluster_id} ({int(profile['n_regions'])} регионов)
- Среднее значение женских фермерств: {profile['log_women_farms_mean']:.4f}
- Среднее значение кредита: {profile['log_credit_total_mean']:.4f}
- Средняя доля земли: {profile['land_share_mean']:.4f}
- Тренд развития: {profile['women_farms_trend']:.4f}
""")

# Create interpretations
interpretations = []
for cluster_id in sorted(regional_data['cluster'].unique()):
    profile = cluster_profiles.loc[cluster_id]
    n_regions = int(profile['n_regions'])
    
    # Determine cluster characteristics
    if profile['log_women_farms_mean'] > regional_data['log_women_farms_mean'].median():
        level = "с высоким уровнем"
    else:
        level = "с низким уровнем"
    
    if profile['women_farms_trend'] > 0:
        trend = "растущий тренд"
    else:
        trend = "снижающийся тренд"
    
    interpretations.append(f"**Кластер {cluster_id}**: {n_regions} регионов, {level} женского предпринимательства, {trend}.")

# Create cluster distribution table
cluster_dist = regional_data.groupby('cluster')['region_id'].apply(
    lambda x: ', '.join(map(str, sorted(x.unique())))
)
cluster_distribution = "\n".join([f"Кластер {i}: Регионы {cluster_dist[i]}" 
                                   for i in sorted(cluster_dist.index)])

summary_text = summary_text.format(
    k=int(optimal_k),
    seed=SEED,
    silhouette_table=silhouette_table,
    profiles_table="\n".join(profiles_text),
    interpretations=" ".join(interpretations),
    cluster_distribution=cluster_distribution
)

summary_text.encode('utf-8')  # Validate encoding
with open(PROMPT_05_KMEANS / "kmeans_summary.md", 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(f"   [OK] Summary report saved to kmeans_summary.md")

print("\n" + "=" * 80)
print("STAGE 5 COMPLETED")
print("=" * 80)
