# revision/ — ревизия статьи по замечаниям рецензента

## Состав

- Трекер всех замечаний рецензента (программные / текстовые, статусы, план и результат по
  каждому пункту) теперь живёт в
  [`../comment_agricultural_lending_women_kazakhstan_bilingual.md`](../comment_agricultural_lending_women_kazakhstan_bilingual.md) —
  прямо под каждым пунктом оригинального отзыва, а не в отдельном файле. Программные пункты
  помечены 🧮. `revision/referee_tracker.md` больше не существует — весь трекер там.
- `manuscript/` — **рабочая копия** рукописи (`sn-article-eng.tex`). Все правки делаются здесь;
  оригинал в `journal_submission_package/` не трогаем — он нужен как база для diff.
- `make_diff.ps1` — собирает автоматическую diff-версию.
- `diff/` — генерируется скриптом, в git не хранится.

## Как помечать правки в manuscript/

В преамбуле определены два макроса (блок `REVISION MARKUP`):

```tex
\rev{новый или изменённый текст}     % красный текст
\hlrev{короткая вставка}             % жёлтая заливка (не использовать в формулах)
```

Пример:

```tex
Access to credit does not have a statistically significant
\rev{positive within-region} effect ...
```

**Финальная чистовая версия:** в преамбуле заменить `\revmarkstrue` на `\revmarksfalse` —
вся раскраска исчезает, текст остаётся. Ничего вычищать по документу не нужно.

## Сборка

Рабочая копия (с цветными правками):

```powershell
cd revision\manuscript
pdflatex sn-article-eng.tex; bibtex sn-article-eng; pdflatex sn-article-eng.tex; pdflatex sn-article-eng.tex
```

Diff-версия (оригинал vs правки; удалённое — красным зачёркнуто, добавленное — синим подчёркнуто):

```powershell
powershell -ExecutionPolicy Bypass -File revision\make_diff.ps1
# → revision\diff\sn-article-diff.pdf
```

Примечание: `latexdiff` из MiKTeX запускается через Strawberry Perl
(`C:\Strawberry\perl\bin\perl.exe`) — perl из Git Bash не имеет модуля Algorithm::Diff.

## Что отправлять в журнал

1. Чистовую ревизию (manuscript с `\revmarksfalse`) — как новый manuscript.
2. Помеченную версию — либо цветную (`\revmarkstrue`), либо `diff/sn-article-diff.pdf`,
   смотря что просит редакция.
3. Point-by-point письмо-ответ (собирается по ID из `comment_agricultural_lending_women_kazakhstan_bilingual.md`).
