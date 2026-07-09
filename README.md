# Влияние агрокредитования на женское предпринимательство в сельском хозяйстве Казахстана

Репозиторий научной статьи и её эмпирической части:
**«The Impact of Agricultural Lending on Women's Entrepreneurship in Kazakhstan's
Agricultural Sector: The Role of Regional Factors and Access to Land»**
(грант AP26100879, ЕНУ им. Л.Н. Гумилёва).

Исследуется причинно-следственная связь между институциональным агрокредитованием
и развитием женских КФХ/агро-МСП по **20 регионам Казахстана за 2015–2024 гг.**
(панель, 175 наблюдений).

## Структура репозитория

| Папка | Назначение |
|---|---|
| `woman_statistic/` | **Эмпирический пайплайн** (Python): расчёты, таблицы и графики статьи |
| `journal_submission_package/` | **Итоговая рукопись** в шаблоне Springer Nature (`sn-article-eng.tex` → `.pdf`) |
| `sn-article-template/` | Оригинальный шаблон Springer Nature (референс) |
| `legacy/` | Архив: первый вариант проекта (`gross_output`), черновики статьи (`article_scopus/`) и устаревшие служебные скрипты |

## Эмпирическая часть (`woman_statistic/`)

Пошаговый пайплайн. Каждый скрипт автономен, берёт пути из `src/config.py`,
пишет результаты только в свою подпапку `output/`.

```bash
pip install pandas numpy openpyxl matplotlib statsmodels linearmodels scikit-learn
cd woman_statistic
python src/01_load_validate.py
python src/02_eda.py
python src/03_prepare_variables.py
python src/04_econometrics.py
python src/05_kmeans.py
python src/06_random_forest.py
python src/99_article_pack.py
```

- **Данные:** `woman_statistic/data/women_agri_panel.xlsx`, лист `panel` (region × year).
- **Метод:** двусторонние фиксированные эффекты (TWFE, регион + год) на несбалансированной
  панели; KMeans и Random Forest — как вспомогательные инструменты (гетерогенность, нелинейность).
- **Правила:** без каузальных заявлений, пропуски не заполняются, `SEED = 42`.
- **Язык:** текст графиков — английский; интерпретации в `.md` — русский.

Выходы: `output/tables/`, `output/infographics/`, `output/prompt/`, итоговая сборка —
`output/tables/99_article_pack/article_tables.xlsx`.

## Рукопись (`journal_submission_package/`)

Сборка LaTeX-статьи:

```bash
cd journal_submission_package
pdflatex sn-article-eng.tex
bibtex   sn-article-eng
pdflatex sn-article-eng.tex
pdflatex sn-article-eng.tex
```

Фигуры `figures/figureNN.png` — это переименованные графики из
`woman_statistic/output/infographics/` (соответствие описано в `CLAUDE.md`).
Исключение — `figure01`, нарисованная вручную схема дизайна исследования.

## legacy/

Архив, не относящийся к текущей рабочей версии:
- первый вариант проекта — прогноз `gross_output` (`python_version/`, `notebooks/`, `data/`,
  `prompts/`, `README_gross_output_project.md`);
- `article_scopus/` — ранние черновики и конвертации статьи (Word → LaTeX/MD/HTML),
  предшествовавшие шаблону Springer Nature;
- устаревшие одноразовые скрипты сборки/проверки рукописи (`fix_*.py`, `compare_sections.py`).

Подробности архитектуры — в `CLAUDE.md`.
