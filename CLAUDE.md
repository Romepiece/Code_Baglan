# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A research repository whose **active work is a single published study**, with an earlier abandoned study and disposable tooling archived under [legacy/](legacy/):

- **Active — Women's agricultural entrepreneurship & credit.** Panel study (region × year, 2015–2024) of how institutional agri-lending relates to women-led farms/SMEs. Pipeline: [woman_statistic/](woman_statistic/). This is the study behind the journal submission in [journal_submission_package/](journal_submission_package/).
- **Archived — Gross agricultural output forecasting.** The repo's *first version* (git: "Первый вариант проекта", 2026-01-16), superseded on 2026-01-24 by the "Woman variant". Scenario forecasting of `gross_output`. Now under [legacy/python_version/](legacy/python_version/) with its data/notebooks/prompts. **Not referenced by the article** — treat as history unless explicitly asked to revive it.

Working language of domain content (result narratives, article prose) is **Russian**; all code identifiers, data columns, and figure text are **English snake_case / English**.

## Study — Women & agri-credit ([woman_statistic/](woman_statistic/))

A staged, sequentially-numbered pipeline. Each script in [woman_statistic/src/](woman_statistic/src/) is **standalone**, imports [config.py](woman_statistic/src/config.py) for all paths, and writes only to its own `output/` subfolder. Run in order:

```
01_load_validate.py → 02_eda.py → 03_prepare_variables.py →
04_econometrics.py → 05_kmeans.py → 06_random_forest.py → 99_article_pack.py
```

- Paths are anchored via `PROJECT_ROOT = Path(__file__).parent.parent` in config.py, so scripts are **cwd-independent**. `config.py` calls `ensure_dirs()` on import to create the output tree; `SEED = 42`.
- Input: `woman_statistic/data/women_agri_panel.xlsx`, sheet **`panel`** only (region × year). Other sheets (`coverage_by_year`, `region_mapping`, `Data Dictionary`) are diagnostic/reference — do not model on them.
- Method core: **Two-way Fixed Effects (region + year)** on an unbalanced panel (`linearmodels`/`statsmodels`); ML (KMeans, Random Forest w/ partial-dependence) is supplementary for heterogeneity/nonlinearity. **No causal claims; do not fill missing values.**
- Hard language rule (from [woman_statistic/promnt/promnt.md](woman_statistic/promnt/promnt.md)): all PNG chart text (titles/axes/legends) in **English**; all `.md` interpretation text in **Russian**; filenames English.
- Outputs: tables → `output/tables/<stage>/`, charts → `output/infographics/<stage>/`, RU narrative → `output/prompt/<stage>/`, final bundle → `output/tables/99_article_pack/article_tables.xlsx` and `output/prompt/99_article_pack/results_ready_text.md`.

### Figure provenance (article ← woman_statistic)

The 8 figures in [journal_submission_package/figures/](journal_submission_package/figures/) are byte-identical renamed copies of `woman_statistic/output/infographics/` PNGs (except figure01, a hand-drawn design diagram). When a figure needs regenerating, rerun the source stage and re-copy:

| Article figure | Source PNG in `woman_statistic/output/infographics/` |
|---|---|
| figure01 | *(none — hand-made research-design diagram)* |
| figure02 | `02_eda/avg_women_farms_over_time.png` |
| figure03 | `02_eda/avg_credit_total_over_time.png` |
| figure04 | `02_eda/scatter_log_credit_vs_log_women.png` |
| figure05 | `04_econometrics/coef_plot.png` |
| figure06 | `05_kmeans/kmeans_clusters.png` |
| figure07 | `06_random_forest/rf_pdp_credit.png` |
| figure08 | `06_random_forest/rf_pdp_land.png` |

## Manuscript

- [journal_submission_package/](journal_submission_package/) — the Springer Nature manuscript: `sn-article-eng.tex` compiled to `sn-article-eng.pdf` with `sn-bibliography.bib`. `sn-jnl.cls` and the `.bst` files are the SN template. Build with the usual LaTeX + BibTeX cycle (`pdflatex` → `bibtex` → `pdflatex` ×2). Its `figures/figureNN.png` come from `woman_statistic/` (see mapping above).
- [sn-article-template/](sn-article-template/) — pristine upstream Springer Nature template download (reference material: `sn-article.tex/pdf`, `user-manual.pdf`, `bst/`).
- [comment_agricultural_lending_women_kazakhstan_bilingual.md](comment_agricultural_lending_women_kazakhstan_bilingual.md) — a standalone bilingual commentary piece, related to the study's topic.

## legacy/ — archived, not active

[legacy/](legacy/) is history only; nothing here feeds the current study or the article. Do not wire active code to these paths.

- `python_version/`, `notebooks/`, `data/`, `prompts/`, `README_gross_output_project.md` — the entire superseded gross-output study. Its `forecast.py` used repo-root-relative paths (`data/processed/...`, `python_version/outputs/...`) and bare intra-package imports, so it will not run unmodified from inside `legacy/`.
- `article_scopus/` — earlier manuscript drafts and format conversions of the *current* study (Word → Markdown/LaTeX/HTML); `article_scopus/Article_fixed/fixed.tex` was the source draft the Springer Nature `.tex` was reconciled against. The live manuscript is `journal_submission_package/`.
- `fix_file.py`, `fix_latex.py`, `compare_sections.py` — retired one-off LaTeX build/QA scripts from article prep. They reference paths that no longer exist (`publication_package/`, `sn-article-template/sn-article-eng.tex`) and don't run as-is. See [legacy/README.md](legacy/README.md).

## Conventions

- Data/model identifiers are English snake_case; do not introduce Cyrillic into code or column names. Prose, section headings, and result narratives are typically Russian.
- Result narratives (Russian `.md` summaries) are regenerated deliverables, not code — they describe a specific run and can go stale after pipeline changes.
- `texput.log` is a pdfTeX crash artifact and is gitignored — never commit it.
