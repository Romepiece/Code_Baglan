Ты — научный ассистент по эконометрике и прикладному анализу данных.
Нужно реализовать практическую (эмпирическую) часть научной статьи.

Тема исследования:
«Влияние институционального агрокредитования на развитие женского предпринимательства
в сельском хозяйстве Казахстана: региональный панельный анализ агро-МСП и КФХ
за 2015–2024 гг.»

================================
КОРНЕВАЯ СТРУКТУРА ПРОЕКТА
================================

Проект расположен в папке:

woman_statistic/

Все пути чтения и записи данных
ДОЛЖНЫ выполняться строго внутри woman_statistic/.
Запрещено использовать ../ и выходить за пределы проекта.

================================
ОПИСАНИЕ ДАТАСЕТА
================================

Файл данных:
woman_statistic/data/women_agri_panel.xlsx

Листы Excel:

1) "panel" — ОСНОВНОЙ (использовать в моделях)
Панельные данные (region × year), 2015–2024.

Колонки:
- region_id
- region_id_en
- region_name_en
- year
- women_farms (count)
- credit_kaf (mln KZT)
- credit_acc (mln KZT)
- credit_fund (mln KZT)
- credit_total (mln KZT)
- land_share (%)
- log_women_farms = log(1 + women_farms)
- log_credit_total = log(1 + credit_total)

2) "coverage_by_year" — диагностический (НЕ использовать в моделях)
3) "region_mapping" — справочный (НЕ использовать в моделях)
4) "Data Dictionary" — справочный (единицы измерения)

================================
ЦЕЛЬ ИССЛЕДОВАНИЯ
================================

Цель — выявить и количественно оценить статистические зависимости
между институциональным агрокредитованием и развитием женского
предпринимательства в сельском хозяйстве Казахстана.

Исследование НЕ является прогнозным.
Методы машинного обучения используются только как
дополнительный аналитический инструмент
(гетерогенность и нелинейность).

================================
ОБЯЗАТЕЛЬНОЕ ЯЗЫКОВОЕ ПРАВИЛО
================================

- ВСЕ графики (png):
  * заголовки,
  * подписи осей,
  * легенды,
  * аннотации
  → ТОЛЬКО НА АНГЛИЙСКОМ ЯЗЫКЕ.

- ВСЕ текстовые файлы (.md),
  комментарии к результатам,
  интерпретации
  → ТОЛЬКО НА РУССКОМ ЯЗЫКЕ.

- Имена файлов — на английском языке.

================================
ТРЕБОВАНИЯ
================================

- Основной метод: Two-way Fixed Effects (region + year).
- Несбалансированная панель.
- Пропуски не заполнять.
- Без каузальных заявлений.
- Python:
  pandas, numpy, openpyxl,
  matplotlib, statsmodels,
  linearmodels, scikit-learn.
- Фиксировать random seed.
- Каждый скрипт автономен.

================================
СТРУКТУРА ВЫВОДА
================================

woman_statistic/output/

infographics/
  01_validate/
  02_eda/
  03_prepare/
  04_econometrics/
  05_kmeans/
  06_random_forest/

tables/
  01_validate/
  02_eda/
  03_prepare/
  04_econometrics/
  05_kmeans/
  06_random_forest/
  99_article_pack/

prompt/
  04_econometrics/
  05_kmeans/
  06_random_forest/
  99_article_pack/

Каждый этап сохраняет результаты
ТОЛЬКО в свою подпапку.

================================
КОНФИГУРАЦИЯ
================================

В woman_statistic/src/config.py:

- PROJECT_ROOT = Path("woman_statistic")
- DATA_PATH = PROJECT_ROOT / "data" / "women_agri_panel.xlsx"
- OUTPUT_ROOT = PROJECT_ROOT / "output"
- SEED = 42

Функция ensure_dirs() создаёт все подпапки output/.

================================
ЭТАПЫ АНАЛИЗА
================================

1) Проверка данных  
Файл: src/01_load_validate.py

- Проверка типов и дубликатов.
- Таблицы пропусков:
  tables/01_validate/missing_overall.csv
  tables/01_validate/missing_by_year.csv
- Краткое описание выборки:
  tables/01_validate/sample_summary.csv

2) EDA  
Файл: src/02_eda.py

Таблицы:
- tables/02_eda/descriptive_statistics.csv

Графики (EN):
- infographics/02_eda/avg_women_farms_over_time.png
  Title: "Average Number of Female-Led Agricultural SMEs Over Time"
  X: "Year"
  Y: "Number of Enterprises"

- infographics/02_eda/avg_credit_total_over_time.png
  Title: "Average Agricultural Credit Volume Over Time"
  X: "Year"
  Y: "Credit Volume (mln KZT)"

- infographics/02_eda/scatter_log_credit_vs_log_women.png
  Title: "Relationship Between Agricultural Credit and Female Entrepreneurship"
  X: "Log Total Agricultural Credit"
  Y: "Log Number of Female-Led Enterprises"

3) Подготовка переменных  
Файл: src/03_prepare_variables.py

- Логи и лаги.
- tables/03_prepare/lags_preview.csv
- tables/03_prepare/prepared_panel_preview.csv

4) Эконометрика  
Файл: src/04_econometrics.py

Таблицы:
- tables/04_econometrics/reg_pooled_ols.csv
- tables/04_econometrics/reg_twfe_main.csv
- tables/04_econometrics/reg_twfe_components.csv

График (EN, если делается):
- infographics/04_econometrics/coef_plot.png
  Title: "Estimated Coefficients from Fixed Effects Model"
  X: "Variables"
  Y: "Coefficient Value"

Текст (RU):
- prompt/04_econometrics/robustness_summary.md

5) ML: KMeans  
Файл: src/05_kmeans.py

Таблицы:
- tables/05_kmeans/kmeans_region_features.csv
- tables/05_kmeans/kmeans_assignments.csv
- tables/05_kmeans/kmeans_cluster_profiles.csv

График (EN):
- infographics/05_kmeans/kmeans_clusters.png
  Title: "Clustering of Regions by Credit Intensity and Female Entrepreneurship"
  X: "Mean Log Agricultural Credit"
  Y: "Mean Log Female-Led Enterprises"

Текст (RU):
- prompt/05_kmeans/kmeans_summary.md

6) ML: Random Forest  
Файл: src/06_random_forest.py

Таблицы:
- tables/06_random_forest/rf_cv_metrics.csv
- tables/06_random_forest/rf_feature_importance.csv

Графики (EN):
- infographics/06_random_forest/rf_pdp_credit.png
  Title: "Partial Dependence: Agricultural Credit"
  X: "Log Total Agricultural Credit"
  Y: "Predicted Log Female-Led Enterprises"

- infographics/06_random_forest/rf_pdp_land.png
  Title: "Partial Dependence: Women's Land Access"
  X: "Land Access Share (%)"
  Y: "Predicted Log Female-Led Enterprises"

Текст (RU):
- prompt/06_random_forest/rf_summary.md

7) Итоговый пакет  
Файл: src/99_article_pack.py

- tables/99_article_pack/article_tables.xlsx
- prompt/99_article_pack/results_ready_text.md
  (на русском языке)

================================
СТИЛЬ
================================

- Чистый, воспроизводимый код.
- Пути только через config.py.
- Каждый файл автономен.
- Графики — EN, тексты — RU.
