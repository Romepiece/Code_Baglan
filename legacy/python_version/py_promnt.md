# Спецификация AI-промта — Python pipeline (.py), без ноутбука

## Роль
Ты — аналитический AI-ассистент в VS Code с GitHub Copilot.
Задача: реализовать воспроизводимый Python-пайплайн сценарного прогнозирования
для научного исследования (социально-экономические временные ряды).

## Статус данных (ВАЖНО)
Данные уже очищены и подготовлены.
Используй готовый датасет:
- формат: wide (1 строка = 1 год)
- период: 2015–2024
- файл: `data/processed/agro_dataset_ml.csv`

Запрещено: повторная очистка, reshaping, переименование столбцов.

## Единицы измерения и масштабирование (ВАЖНО)
В датасете смешанные шкалы:
- деньги (млн тенге): `gross_output`, `investment_agri`, `net_profit`
- проценты: `*_rate`, `*_share`, `profitability`
- количество: тыс. чел (`employment_total`, `employment_women`), млн га (`agri_land_area_mha`)

Правила:
- не приводить всё к одной шкале без обоснования
- `StandardScaler` применять ТОЛЬКО для Ridge/Lasso/ElasticNet и только после time-split
  (через Pipeline или fit на train → transform test)
- эконометрика (OLS/ARDL/динамика в разностях): в исходных единицах, с интерпретацией коэффициентов

## Имена переменных (КРИТИЧЕСКИ ВАЖНО)
Использовать только snake_case. Кириллица запрещена.

Цель: `gross_output`
Время: `year`

Факторы:
- `employment_total`, `employment_women`, `labor_productivity`, `investment_agri`,
  `profitability`, `net_profit`, `agri_land_area_mha`
- `agri_gdp_share`, `gov_support_index`
- `poverty_rate`, `undernourishment_rate`, `youth_neet_rate`,
  `women_land_share`, `rural_housing_share`, `rural_internet_share`

Полные названия см. `variables_mapping.md`. Ничего не переименовывать.

## Цель исследования
Построить прогноз `gross_output` до 2035 года на основе интерпретируемых моделей
и экзогенных сценариев факторов (pessimistic/base/optimistic).

## Методологические ограничения (ЖЁСТКО)
- только интерпретируемые модели
- никаких deep learning (LSTM/GRU/Transformers) и «чёрных ящиков»
- никаких случайных разбиений и shuffled-CV для time series
- сценарии НЕ зависят от ошибок моделей (не использовать RMSE/±% для сценариев)

## Требуемая структура проекта (она уже частично готова, найди папки)

python_version/src/
data_loader.py
features.py
econometrics.py
ml_models.py
scenarios.py
forecast.py

python_version/outputs/
python_version/outputs/tables/
python_version/outputs/figures/
requirements.txt
README.md


## Логика модулей

### python_version/src/data_loader.py
- загрузка CSV, сортировка по `year`
- базовые проверки (shape/dtypes/missing)
- возвращает DataFrame

### python_version/src/features.py
- генерация признаков:
  - лаги (t−1, t−2)
  - темпы роста
  - индексация (база = 100)
- без обучения моделей

### python_version/src/econometrics.py
- OLS
- ARDL
- динамическая модель в разностях (как приближение; НЕ называть строгим ECM)
- возвращать коэффициенты и предсказания

### python_version/src/ml_models.py
- LinearRegression (baseline)
- Ridge / Lasso / ElasticNet (с масштабированием через Pipeline)
- оценка только по time-based split

### python_version/src/scenarios.py
Сценарии строятся ТОЛЬКО по траекториям факторов:
- выбрать 3–5 ключевых драйверов (например: `investment_agri`, `labor_productivity`,
  `gov_support_index`, `employment_total`)
- рассчитать исторические темпы роста (2015–2024)
- задать:
  - base = P50 (или mean/median)
  - optimistic = P75
  - pessimistic = P25 (или стагнация)
- вернуть будущие значения факторов по годам до 2035

### python_version/src/forecast.py (ТОЧКА ВХОДА)
- обучить модели на истории
- построить 3 сценария факторов
- прогнать одинаковые сценарные входы через все модели
- сохранить результаты и графики (см. ниже)

## Выходы: сохранение результатов (MANDATORY)

### Таблицы (CSV → outputs/tables/)
Обязательные файлы:
- `model_coefficients.csv` (модель, переменная, коэффициент)
- `model_metrics.csv` (модель, R2/RMSE/MAE; только справочно)
- `scenario_assumptions.csv` (сценарий, фактор, темп/правило)
- `scenario_forecasts.csv` (year, scenario, model, gross_output_pred)

Никаких “принтов вместо сохранения”.

### Графики (PNG → outputs/figures/)
Сгенерировать и сохранить:
1) `target_history.png` — фактический `gross_output` (2015–2024)
2) `scenario_forecasts_by_model.png` — 3 сценария для ключевой модели (OLS и/или Ridge)
3) `scenario_compare_models.png` — сравнение моделей по одному сценарию (base)
4) `coefficients_overview.png` — коэффициенты/влияния (интерпретируемо)

Графики должны иметь: заголовок, подписи осей, единицы измерения.  
Допускается перенос длинных подписей в легенду/подписи, но без “каши”.

## Definition of Done (ОБЯЗАТЕЛЬНО)
Считай задачу выполненной только если:
- `python python_version/src/forecast.py` запускается без ошибок
- папки `python_version/outputs/tables/` и `python_version/outputs/figures/` заполнены файлами
- сценарии построены экзогенно (без RMSE/±% вокруг прогноза)
- разбиение и оценка моделей корректны для time series (time-based split)

## Стиль кода
- функции с docstring
- минимум магии, максимум прозрачности
- комментарии только по делу (академически нейтрально)

## Не генерируй лишние .md файлы, можно сдлать потом один финальный в котором будут результаты все. 