# legacy/

Архив. Ничего здесь не относится к текущей рабочей версии статьи
(`woman_statistic/` + `journal_submission_package/`) и не должно подключаться к рабочему коду.

## Содержимое

- `python_version/`, `notebooks/`, `data/`, `prompts/`, `README_gross_output_project.md`
  — **первый вариант проекта**: прогноз валового выпуска (`gross_output`) со сценариями.
  Вытеснен «женским» исследованием 2026-01-24. `forecast.py` использует пути относительно
  корня репозитория, поэтому из `legacy/` без правок не запустится.

- `article_scopus/` — ранние черновики и конвертации **текущей** статьи
  (Word → LaTeX/MD/HTML). `Article_fixed/fixed.tex` был эталоном, с которым сверяли
  финальную рукопись при переносе в шаблон Springer Nature.

- Одноразовые скрипты сборки/проверки рукописи (2026-05), ссылаются на уже
  несуществующие пути (`publication_package/`, `sn-article-template/sn-article-eng.tex`),
  поэтому в текущем виде не запускаются:
  - `fix_file.py` — правка экранирования `\real` в LaTeX-исходнике.
  - `fix_latex.py` — правка экранирования `\setlength{\LTright}{\fill}` в таблицах.
  - `compare_sections.py` — посекционное сравнение `article_scopus/Article_fixed/fixed.tex`
    с итоговой рукописью.
