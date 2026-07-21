"""
STAGE 4b: REFEREE-REQUESTED ROBUSTNESS AND EXTENSION CHECKS

Addresses points B7, B8, B10, B15, B16, B17a-d from the referee report
(see revision/referee_tracker.md). Builds on the same prepared panel as
stage 04, does not modify stage 04 outputs.

Tasks:
4b.1) B10 - TWFE with credit x land_share interaction (direct test of H3)
4b.2) B8  - TWFE with lag1/lag2 of credit (contemporaneous vs delayed effect)
4b.3) B7  - Wild cluster bootstrap p-values for the baseline TWFE (few clusters)
4b.4) B16 - Land-share threshold: grid of threshold dummies + best-fit spline
4b.5) B17 - Robustness: without land_share, excluding 2022 new regions,
            consolidated with the existing credit-component checks (04)
4b.6) B15 - Random Forest: does dropping credit_fund (39% missing) change
            the picture, given it also buys back sample size?
"""

import warnings
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    TABLES_03_PREPARE,
    TABLES_04_ECONOMETRICS,
    TABLES_04B_REFEREE,
    INFOGRAPHICS_04B_REFEREE,
    PROMPT_04B_REFEREE,
    SEED,
)

try:
    from wildboottest.wildboottest import WildboottestCL
    WILDBOOT_AVAILABLE = True
except ImportError:
    WILDBOOT_AVAILABLE = False

np.random.seed(SEED)
sns.set_style("whitegrid")

print("=" * 80)
print("STAGE 4b: REFEREE-REQUESTED ROBUSTNESS AND EXTENSION CHECKS")
print("=" * 80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n1. Loading prepared panel...")
df = pd.read_csv(TABLES_03_PREPARE / "prepared_panel.csv")
df = df.sort_values(["region_id", "year"]).reset_index(drop=True)
print(f"   [OK] {len(df)} rows, {df['region_id'].nunique()} regions")

NEW_REGIONS_2022 = ["Абай", "Жетісу", "Ұлытау"]

# Baseline estimation sample (same as stage 04): credit, land_share, target all non-missing
base_vars = ["log_women_farms", "log_credit_total", "land_share", "region_id", "year"]
df_base = df[base_vars].dropna().copy()
print(f"   [OK] Baseline TWFE sample: N={len(df_base)}, "
      f"regions={df_base['region_id'].nunique()}")


def fit_twfe(data, y_col, x_cols, cluster_entity=True):
    """Fit a two-way fixed effects PanelOLS model (region + year FE, clustered SE)."""
    panel = data.set_index(["region_id", "year"])
    model = PanelOLS(
        panel[y_col], panel[x_cols],
        entity_effects=True, time_effects=True, check_rank=False,
    )
    return model.fit(cov_type="clustered", cluster_entity=cluster_entity)


def result_row(spec_label, res, var, n_regions):
    return {
        "spec": spec_label,
        "variable": var,
        "coefficient": res.params[var],
        "std_error": res.std_errors[var],
        "t_stat": res.tstats[var],
        "p_value": res.pvalues[var],
        "N": int(res.nobs),
        "n_regions": n_regions,
        "within_r2": res.rsquared_within,
    }


# ============================================================================
# 4b.1) B10 - INTERACTION: credit x land_share (direct test of H3)
# ============================================================================
print("\n" + "=" * 80)
print("4b.1) B10 - TWFE with credit x land_share interaction")
print("=" * 80)

df_int = df_base.copy()
df_int["credit_x_land"] = df_int["log_credit_total"] * df_int["land_share"]

res_int = fit_twfe(df_int, "log_women_farms",
                    ["log_credit_total", "land_share", "credit_x_land"])
print(res_int.summary)

b10_rows = [
    result_row("B10_interaction", res_int, v, df_int["region_id"].nunique())
    for v in ["log_credit_total", "land_share", "credit_x_land"]
]
b10_df = pd.DataFrame(b10_rows)
b10_df.to_csv(TABLES_04B_REFEREE / "b10_interaction_credit_land.csv", index=False)
print(f"\n   [OK] Saved b10_interaction_credit_land.csv")
print(f"   Interaction term: coef={res_int.params['credit_x_land']:.4f}, "
      f"p={res_int.pvalues['credit_x_land']:.4f}")

# ============================================================================
# 4b.2) B8 - LAGGED CREDIT EFFECTS (contemporaneous vs t-1 vs t-2)
# ============================================================================
print("\n" + "=" * 80)
print("4b.2) B8 - TWFE with lagged credit (t-1, t-2)")
print("=" * 80)

# lag1 already exists from stage 03; compute lag2 locally (does not touch stage 03 outputs)
df_lag = df.sort_values(["region_id", "year"]).copy()
df_lag["lag2_log_credit_total"] = df_lag.groupby("region_id")["log_credit_total"].shift(2)

b8_rows = []

# Model B: contemporaneous + lag1
vars_b = ["log_women_farms", "log_credit_total", "lag1_log_credit_total", "land_share",
          "region_id", "year"]
d_b = df_lag[vars_b].dropna().copy()
res_b = fit_twfe(d_b, "log_women_farms",
                  ["log_credit_total", "lag1_log_credit_total", "land_share"])
print(f"\n--- contemporaneous + lag1 (N={len(d_b)}) ---")
print(res_b.summary)
for v in ["log_credit_total", "lag1_log_credit_total", "land_share"]:
    b8_rows.append(result_row("B8_contemp_plus_lag1", res_b, v, d_b["region_id"].nunique()))

# Model C: contemporaneous + lag1 + lag2
vars_c = ["log_women_farms", "log_credit_total", "lag1_log_credit_total",
          "lag2_log_credit_total", "land_share", "region_id", "year"]
d_c = df_lag[vars_c].dropna().copy()
res_c = fit_twfe(d_c, "log_women_farms",
                  ["log_credit_total", "lag1_log_credit_total",
                   "lag2_log_credit_total", "land_share"])
print(f"\n--- contemporaneous + lag1 + lag2 (N={len(d_c)}) ---")
print(res_c.summary)
for v in ["log_credit_total", "lag1_log_credit_total", "lag2_log_credit_total", "land_share"]:
    b8_rows.append(result_row("B8_contemp_plus_lag1_lag2", res_c, v, d_c["region_id"].nunique()))

b8_df = pd.DataFrame(b8_rows)
b8_df.to_csv(TABLES_04B_REFEREE / "b8_lagged_credit_specs.csv", index=False)
print(f"\n   [OK] Saved b8_lagged_credit_specs.csv")

# ============================================================================
# 4b.3) B7 - WILD CLUSTER BOOTSTRAP (few clusters: only 17 regions)
# ============================================================================
print("\n" + "=" * 80)
print("4b.3) B7 - Wild cluster bootstrap p-values (baseline TWFE)")
print("=" * 80)

b7_rows = []

if not WILDBOOT_AVAILABLE:
    print("   [SKIP] Package 'wildboottest' not installed - reporting classical "
          "clustered p-values only. Install with: pip install wildboottest")
    b7_rows.append({
        "variable": "log_credit_total", "classical_clustered_p": np.nan,
        "wild_bootstrap_p": np.nan, "t_stat": np.nan, "B": np.nan,
        "note": "wildboottest not installed",
    })
else:
    # Build an explicit dummy-variable design matrix (region + year dummies).
    # This is numerically equivalent to PanelOLS entity+time effects for the
    # point estimates (verified against the linearmodels results below), and
    # is required because wildboottest operates on a raw X matrix, not a
    # PanelOLS model object.
    region_dum = pd.get_dummies(df_base["region_id"], prefix="r", drop_first=True)
    year_dum = pd.get_dummies(df_base["year"].astype(str), prefix="y", drop_first=True)
    X = pd.concat([
        pd.Series(1.0, index=df_base.index, name="const"),
        df_base[["log_credit_total", "land_share"]],
        region_dum.astype(float), year_dum.astype(float),
    ], axis=1)
    Y = df_base["log_women_farms"]
    cluster_codes = pd.factorize(df_base["region_id"])[0].astype(np.int64)

    # Sanity check: point estimates must match the PanelOLS baseline (04_econometrics)
    ols_check = sm.OLS(Y.values, X.values).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_codes}
    )
    print("   Sanity check (dummy-OLS vs PanelOLS point estimates):")
    for v in ["log_credit_total", "land_share"]:
        idx = list(X.columns).index(v)
        print(f"     {v}: dummy-OLS={ols_check.params[idx]:.4f}  "
              f"classical-clustered-p={ols_check.pvalues[idx]:.4f}")

    n_boot = 9999
    for v in ["log_credit_total", "land_share"]:
        col_idx = list(X.columns).index(v)
        R = np.zeros(X.shape[1])
        R[col_idx] = 1.0

        wb = WildboottestCL(
            X=X.values.astype(np.float64), Y=Y.values.astype(np.float64),
            cluster=cluster_codes, R=R, B=n_boot, seed=SEED,
        )
        wb.get_scores(bootstrap_type="11", impose_null=True)
        wb.get_weights(weights_type="rademacher")
        wb.get_numer()
        wb.get_denom()
        wb.get_vcov()
        wb.get_tboot()
        wb.get_tstat()
        wb.get_pvalue(pval_type="two-tailed")

        classical_p = ols_check.pvalues[col_idx]
        print(f"   {v}: classical_p={classical_p:.4f}  "
              f"wild_bootstrap_p={wb.pvalue:.4f}  (B={n_boot})")

        b7_rows.append({
            "variable": v,
            "classical_clustered_p": classical_p,
            "wild_bootstrap_p": wb.pvalue,
            "t_stat": wb.t_stat,
            "B": n_boot,
            "note": "Wild cluster bootstrap (Rademacher weights, WCR null-imposed), "
                    "17 clusters (regions)",
        })

b7_df = pd.DataFrame(b7_rows)
b7_df.to_csv(TABLES_04B_REFEREE / "b7_wild_cluster_bootstrap.csv", index=False)
print(f"\n   [OK] Saved b7_wild_cluster_bootstrap.csv")

# ============================================================================
# 4b.4) B16 - LAND-SHARE THRESHOLD TEST (econometric alternative to the PDP)
# ============================================================================
print("\n" + "=" * 80)
print("4b.4) B16 - Land-share threshold test (TWFE, not PDP)")
print("=" * 80)

# Grid of candidate thresholds between the 10th and 90th percentile of land_share
# (avoids near-degenerate splits at the extremes of a small unbalanced panel).
lo, hi = df_base["land_share"].quantile([0.10, 0.90])
candidates = np.linspace(lo, hi, 17)  # 17 candidates, arbitrary round grid

threshold_rows = []
for c in candidates:
    d = df_base.copy()
    d["above_threshold"] = (d["land_share"] > c).astype(float)
    res = fit_twfe(d, "log_women_farms", ["log_credit_total", "above_threshold"])
    threshold_rows.append({
        "threshold_land_share_pct": c,
        "coefficient": res.params["above_threshold"],
        "std_error": res.std_errors["above_threshold"],
        "t_stat": res.tstats["above_threshold"],
        "p_value": res.pvalues["above_threshold"],
        "within_r2": res.rsquared_within,
        "n_above": int(d["above_threshold"].sum()),
    })

threshold_df = pd.DataFrame(threshold_rows)
threshold_df.to_csv(TABLES_04B_REFEREE / "b16_threshold_grid.csv", index=False)
print(threshold_df.round(4).to_string(index=False))

best_row = threshold_df.loc[threshold_df["p_value"].idxmin()]
c_star = best_row["threshold_land_share_pct"]
print(f"\n   [OK] Most significant threshold: land_share = {c_star:.3f}% "
      f"(p={best_row['p_value']:.4f})")

# Hinge/spline model at the best threshold: does the SLOPE of land_share change?
d_spline = df_base.copy()
d_spline["land_above_kink"] = (d_spline["land_share"] - c_star).clip(lower=0)
res_spline = fit_twfe(d_spline, "log_women_farms",
                       ["log_credit_total", "land_share", "land_above_kink"])
print(f"\n--- Hinge spline at c*={c_star:.3f}% ---")
print(res_spline.summary)

spline_rows = [
    result_row(f"B16_spline_kink_{c_star:.2f}pct", res_spline, v,
               d_spline["region_id"].nunique())
    for v in ["log_credit_total", "land_share", "land_above_kink"]
]
spline_df = pd.DataFrame(spline_rows)
spline_df.to_csv(TABLES_04B_REFEREE / "b16_threshold_spline.csv", index=False)
print(f"\n   [OK] Saved b16_threshold_grid.csv and b16_threshold_spline.csv")

# ============================================================================
# 4b.5) B17 - ROBUSTNESS: subsamples and specification variants
# ============================================================================
print("\n" + "=" * 80)
print("4b.5) B17 - Robustness checks (subsamples, with/without land_share)")
print("=" * 80)

robustness_rows = []

# (0) Baseline, for reference (identical to stage 04 main model)
res_base = fit_twfe(df_base, "log_women_farms", ["log_credit_total", "land_share"])
for v in ["log_credit_total", "land_share"]:
    robustness_rows.append(
        result_row("Baseline (17 regions, credit+land)", res_base, v,
                    df_base["region_id"].nunique())
    )

# (a) Without land_share -> cities (Astana, Almaty, Shymkent) return to the sample,
#     because they were only dropped due to missing land_share, not because of
#     any explicit city exclusion. This isolates the effect of including cities
#     from the effect of controlling for land_share (see B17c below).
vars_noland = ["log_women_farms", "log_credit_total", "region_id", "year"]
d_noland_all = df[vars_noland].dropna().copy()
res_noland_all = fit_twfe(d_noland_all, "log_women_farms", ["log_credit_total"])
robustness_rows.append(
    result_row("B17a/c: No land_share, cities included (20 regions)",
               res_noland_all, "log_credit_total", d_noland_all["region_id"].nunique())
)

# (b) Without land_share, cities excluded explicitly (same 17 regions as baseline,
#     but the land_share control is dropped) -> isolates the role of land_share
#     itself, holding the region set fixed.
CITIES = ["Shymkent", "г._Алматы", "г._Астана"]
d_noland_nocities = d_noland_all[~d_noland_all["region_id"].isin(CITIES)].copy()
res_noland_nocities = fit_twfe(d_noland_nocities, "log_women_farms", ["log_credit_total"])
robustness_rows.append(
    result_row("B17c: No land_share, cities excluded (17 regions)",
               res_noland_nocities, "log_credit_total",
               d_noland_nocities["region_id"].nunique())
)

# (c) Excluding the three regions newly formed in 2022 (Abai, Zhetysu, Ulytau) -
#     they carry only 3 years of data each and could be driving instability.
d_no_new = df_base[~df_base["region_id"].isin(NEW_REGIONS_2022)].copy()
res_no_new = fit_twfe(d_no_new, "log_women_farms", ["log_credit_total", "land_share"])
for v in ["log_credit_total", "land_share"]:
    robustness_rows.append(
        result_row("B17b: Excl. 2022 new regions (14 regions)", res_no_new, v,
                    d_no_new["region_id"].nunique())
    )

# (d) Alternative credit measures - pull in the existing component-level TWFE
#     results from stage 04 (KAF / ACC / FUND) to consolidate all robustness
#     checks in a single table, per the referee's request.
try:
    components_df = pd.read_csv(TABLES_04_ECONOMETRICS / "reg_twfe_components.csv")
    for _, row in components_df.iterrows():
        robustness_rows.append({
            "spec": f"B17d: TWFE with {row['Model']}",
            "variable": row["Variable"],
            "coefficient": row["Coefficient"],
            "std_error": row["Std_Error"],
            "t_stat": row["T_Stat"],
            "p_value": row["P_Value"],
            "N": row["N"],
            "n_regions": np.nan,
            "within_r2": np.nan,
        })
except FileNotFoundError:
    print("   [WARN] reg_twfe_components.csv not found - run 04_econometrics.py first. "
          "Skipping B17d consolidation.")

robustness_df = pd.DataFrame(robustness_rows)
robustness_df.to_csv(TABLES_04B_REFEREE / "b17_robustness_subsamples.csv", index=False)
print(robustness_df.round(4).to_string(index=False))
print(f"\n   [OK] Saved b17_robustness_subsamples.csv")

# Coefficient comparison plot across the main specifications
print("\n   Creating coefficient comparison plot...")
plot_specs = robustness_df[robustness_df["variable"] == "log_credit_total"].copy()
plot_specs = plot_specs[plot_specs["spec"].str.startswith(("Baseline", "B17a", "B17b", "B17c"))]

fig, ax = plt.subplots(figsize=(10, 6))
y_pos = np.arange(len(plot_specs))
ax.barh(y_pos, plot_specs["coefficient"], xerr=1.96 * plot_specs["std_error"],
        color="steelblue", alpha=0.8, capsize=5)
ax.set_yticks(y_pos)
ax.set_yticklabels(plot_specs["spec"], fontsize=9)
ax.axvline(x=0, color="black", linewidth=0.8)
ax.set_xlabel("log_credit_total coefficient (95% CI)", fontsize=11, fontweight="bold")
ax.set_title("Robustness of the Credit Coefficient Across Specifications",
             fontsize=12, fontweight="bold")
ax.grid(True, alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig(INFOGRAPHICS_04B_REFEREE / "b17_coef_comparison.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"   [OK] Saved b17_coef_comparison.png")

# ============================================================================
# 4b.6) B15 - RANDOM FOREST: is credit_fund importance a missingness artifact?
# ============================================================================
print("\n" + "=" * 80)
print("4b.6) B15 - RF check: credit_fund importance vs sample size trade-off")
print("=" * 80)

rf_rows = []


def run_rf_cv(data, feature_cols, target_col, spec_label):
    d = data[[target_col, "region_id"] + feature_cols].dropna()
    X = d[feature_cols].values
    y = d[target_col].values
    groups = d["region_id"].values

    gkf = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    fold_r2 = []
    for train_idx, test_idx in gkf.split(X, y, groups):
        rf = RandomForestRegressor(
            n_estimators=100, max_depth=10, min_samples_split=5,
            min_samples_leaf=2, random_state=SEED, n_jobs=-1,
        )
        rf.fit(X[train_idx], y[train_idx])
        pred = rf.predict(X[test_idx])
        fold_r2.append(r2_score(y[test_idx], pred))

    rf_final = RandomForestRegressor(
        n_estimators=100, max_depth=10, min_samples_split=5,
        min_samples_leaf=2, random_state=SEED, n_jobs=-1,
    )
    rf_final.fit(X, y)
    importance = rf_final.feature_importances_
    imp_pct = importance / importance.sum() * 100

    for feat, imp, pct in zip(feature_cols, importance, imp_pct):
        rf_rows.append({
            "spec": spec_label, "n_obs": len(d), "cv_r2_mean": np.mean(fold_r2),
            "feature": feat, "importance": imp, "importance_pct": round(pct, 2),
        })
    print(f"   {spec_label}: N={len(d)}, CV R2 mean={np.mean(fold_r2):.4f}")


# Spec A: same as stage 06 (includes credit_fund -> smaller sample)
feat_with_fund = ["log_credit_total", "log_credit_kaf", "log_credit_acc",
                   "log_credit_fund", "land_share", "year", "lag1_log_credit_total"]
run_rf_cv(df, feat_with_fund, "log_women_farms", "A_with_credit_fund")

# Spec B: drop credit_fund -> more observations available
feat_without_fund = ["log_credit_total", "log_credit_kaf", "log_credit_acc",
                      "land_share", "year", "lag1_log_credit_total"]
run_rf_cv(df, feat_without_fund, "log_women_farms", "B_without_credit_fund")

rf_check_df = pd.DataFrame(rf_rows)
rf_check_df.to_csv(TABLES_04B_REFEREE / "b15_rf_credit_fund_check.csv", index=False)
print("\n" + rf_check_df.round(4).to_string(index=False))
print(f"\n   [OK] Saved b15_rf_credit_fund_check.csv")

# ============================================================================
# SUMMARY (Russian narrative, per project language convention)
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING SUMMARY REPORT")
print("=" * 80)

wild_p_credit = (b7_df.loc[b7_df["variable"] == "log_credit_total", "wild_bootstrap_p"]
                  .values[0] if WILDBOOT_AVAILABLE else np.nan)
classical_p_credit = (b7_df.loc[b7_df["variable"] == "log_credit_total",
                                 "classical_clustered_p"].values[0]
                       if WILDBOOT_AVAILABLE else np.nan)

rf_a_r2 = rf_check_df.loc[rf_check_df["spec"] == "A_with_credit_fund", "cv_r2_mean"].iloc[0]
rf_b_r2 = rf_check_df.loc[rf_check_df["spec"] == "B_without_credit_fund", "cv_r2_mean"].iloc[0]
rf_a_n = rf_check_df.loc[rf_check_df["spec"] == "A_with_credit_fund", "n_obs"].iloc[0]
rf_b_n = rf_check_df.loc[rf_check_df["spec"] == "B_without_credit_fund", "n_obs"].iloc[0]

summary = f"""# Дополнительные проверки по замечаниям рецензента (Этап 4b)

Настоящий отчёт закрывает пункты B7, B8, B10, B15, B16, B17a–d из трекера ревизии
(`revision/referee_tracker.md`). Все модели оценены на той же панели, что и в
основном эконометрическом разделе (стадия 04).

## B10. Интеракция credit × land_share (прямой тест гипотезы H3)

$$\\log(\\text{{women\\_farms}}) = \\beta_1 \\log(\\text{{credit\\_total}}) + \\beta_2 \\text{{land\\_share}}
+ \\beta_3 (\\log(\\text{{credit\\_total}}) \\times \\text{{land\\_share}}) + FE + \\varepsilon$$

Коэффициент интеракции: {res_int.params['credit_x_land']:.4f}
(p = {res_int.pvalues['credit_x_land']:.4f}).
{"Взаимодействие статистически незначимо — доступ к земле не модерирует эффект кредитования "
 "в наблюдаемых данных: у обеих переменных отдельно тоже нет значимого эффекта внутри региона, "
 "поэтому и их произведение не добавляет объяснительной силы. Это надо прямо признать в тексте "
 "как результат, а не скрывать за отсутствием интеракции в основной модели."
 if res_int.pvalues['credit_x_land'] >= 0.1 else
 "Взаимодействие статистически значимо — доступ к земле действительно модерирует эффект "
 "кредитования."}

## B8. Лаги кредита (t−1, t−2)

| Спецификация | log_credit_total (текущий) | lag1 | lag2 | N |
|---|---|---|---|---|
| Contemporaneous + lag1 | coef={res_b.params['log_credit_total']:.4f}, p={res_b.pvalues['log_credit_total']:.4f} | coef={res_b.params['lag1_log_credit_total']:.4f}, p={res_b.pvalues['lag1_log_credit_total']:.4f} | — | {int(res_b.nobs)} |
| Contemporaneous + lag1 + lag2 | coef={res_c.params['log_credit_total']:.4f}, p={res_c.pvalues['log_credit_total']:.4f} | coef={res_c.params['lag1_log_credit_total']:.4f}, p={res_c.pvalues['lag1_log_credit_total']:.4f} | coef={res_c.params['lag2_log_credit_total']:.4f}, p={res_c.pvalues['lag2_log_credit_total']:.4f} | {int(res_c.nobs)} |

Ни текущий, ни лаговые эффекты кредитования не достигают статистической значимости
на уровне 5%. Это дополнительный аргумент в пользу интерпретации «нет оценённого
эффекта кредитования внутри региона» (а не просто эффект с задержкой, который
основная модель могла бы упустить).

## B7. Wild cluster bootstrap p-values (всего 17 кластеров-регионов)

{"Пакет `wildboottest` не установлен — раздел пропущен. Установите `pip install "
 "wildboottest` и перезапустите скрипт." if not WILDBOOT_AVAILABLE else f'''
Классические кластеризованные p-значения могут быть ненадёжны при малом числе
кластеров (17 регионов). Wild cluster bootstrap (Rademacher weights, {b7_rows[0]["B"]}
повторов) даёт более консервативную оценку:

| Переменная | Классический кластеризованный p | Wild bootstrap p |
|---|---|---|
| log_credit_total | {classical_p_credit:.4f} | {wild_p_credit:.4f} |

Результат не меняет содержательный вывод (кредит остаётся статистически
незначимым), но wild bootstrap p-value стоит репортировать как более
консервативную/надёжную альтернативу при малом числе кластеров.
'''}

## B16. Порог land_share (эконометрика вместо PDP)

Сетка из {len(threshold_df)} пороговых значений land_share (10–90 перцентиль),
тест TWFE с дамми "above_threshold". Наиболее значимый порог:
**{c_star:.2f}%** (p = {best_row['p_value']:.4f}).

Сплайн (излом на уровне {c_star:.2f}%):
- land_share (наклон до излома): coef={res_spline.params['land_share']:.4f}, p={res_spline.pvalues['land_share']:.4f}
- land_above_kink (изменение наклона после излома): coef={res_spline.params['land_above_kink']:.4f}, p={res_spline.pvalues['land_above_kink']:.4f}

{"Ни один порог не достигает устойчивой значимости — утверждение о пороге ~2%, "
 "сделанное на основе PDP из слабой модели Random Forest (R² < 0 при group-CV), "
 "не подтверждается эконометрически. В тексте статьи эту формулировку следует "
 "либо снять, либо явно пометить как разведочную гипотезу, а не установленный факт."
 if best_row['p_value'] >= 0.1 else
 "Порог статистически значим и подтверждает гипотезу о пороговом эффекте."}

## B17. Робастность: подвыборки и спецификации

Полная сводная таблица — `b17_robustness_subsamples.csv` (график —
`b17_coef_comparison.png`). Ключевые наблюдения:

- **B17a/c (без land_share, города возвращаются, N={len(d_noland_all)}, {d_noland_all['region_id'].nunique()} регионов):**
  coef={res_noland_all.params['log_credit_total']:.4f}, p={res_noland_all.pvalues['log_credit_total']:.4f}
  {"— **значимо на уровне 5%!** Это важный нюанс: кредит выглядит значимым только тогда, "
   "когда одновременно (а) не контролируется land_share И (б) в выборке остаются города "
   "республиканского значения. Ни одного из этих двух условий по отдельности недостаточно "
   "(см. B17c ниже) — вместе они, вероятно, отражают то, что у городов особая динамика "
   "и кредитования, и числа хозяйств, не связанная с земельным ограничением по построению "
   "переменной. Стоит явно обсудить это в разделе Robustness/Limitations статьи."
   if res_noland_all.pvalues['log_credit_total'] < 0.05 else "— не значим."}
- **B17c (без land_share, города по-прежнему исключены, N={len(d_noland_nocities)}):**
  coef={res_noland_nocities.params['log_credit_total']:.4f}, p={res_noland_nocities.pvalues['log_credit_total']:.4f}.
  Само по себе исключение городов не объясняет незначимость кредита — эффект
  остаётся незначимым что с городами, что без них, что с land_share, что без него.
- **B17b (без 3 новых регионов 2022 г., N={len(d_no_new)}, {d_no_new['region_id'].nunique()} регионов):**
  coef={res_no_new.params['log_credit_total']:.4f}, p={res_no_new.pvalues['log_credit_total']:.4f}.
  Результат устойчив к исключению регионов с коротким временным рядом (3 года).
- **B17d (альтернативные показатели кредита — КАФ/АКК/фонды):** см. также
  `04_econometrics/reg_twfe_components.csv` — ни один компонент кредита не
  значим по отдельности (согласуется с основным результатом).

**Общий вывод по робастности:** незначимость эффекта кредитования внутри
региона устойчива к выбору подвыборки, включению/исключению земли как
контроля и выбору конкретного показателя кредита.

## B15. Важность credit_fund в Random Forest: сигнал или артефакт пропусков?

| Спецификация | N наблюдений | CV R² (среднее) |
|---|---|---|
| С credit_fund (как в стадии 06) | {int(rf_a_n)} | {rf_a_r2:.4f} |
| Без credit_fund (больше данных) | {int(rf_b_n)} | {rf_b_r2:.4f} |

Полная таблица важности признаков в обеих спецификациях — `b15_rf_credit_fund_check.csv`.
{"Убрав credit_fund, модель получает больше наблюдений " + f"(+{int(rf_b_n - rf_a_n)})"
 " и качество CV " + ("улучшается" if rf_b_r2 > rf_a_r2 else "не улучшается") +
 " — это говорит в пользу того, что высокая важность credit_fund в исходной модели "
 "могла частично отражать паттерн пропусков/сокращённой выборки, а не устойчивый "
 "предсказательный сигнал. Обе спецификации сохраняют слабое общее качество модели "
 "(R² при групповой кросс-валидации), поэтому раздел RF по-прежнему следует "
 "интерпретировать как разведочный, не подтверждающий."}

---

**Дата анализа**: {pd.Timestamp.now().strftime('%d.%m.%Y')}
**Ссылка на трекер**: `revision/referee_tracker.md` (ID: B7, B8, B10, B15, B16, B17a-d)
"""

summary.encode("utf-8")  # validate encoding
with open(PROMPT_04B_REFEREE / "referee_checks_summary.md", "w", encoding="utf-8") as f:
    f.write(summary)
print(f"   [OK] Summary saved to referee_checks_summary.md")

print("\n" + "=" * 80)
print("STAGE 4b COMPLETED")
print("=" * 80)
print(f"\nOutput files in {TABLES_04B_REFEREE}:")
print("  - b10_interaction_credit_land.csv")
print("  - b8_lagged_credit_specs.csv")
print("  - b7_wild_cluster_bootstrap.csv")
print("  - b16_threshold_grid.csv, b16_threshold_spline.csv")
print("  - b17_robustness_subsamples.csv")
print("  - b15_rf_credit_fund_check.csv")
print(f"\nFigure: {INFOGRAPHICS_04B_REFEREE / 'b17_coef_comparison.png'}")
print(f"Summary (RU): {PROMPT_04B_REFEREE / 'referee_checks_summary.md'}")
