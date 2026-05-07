Publication package contents

Folders:
- source: clean LaTeX source package
- figures: only the images referenced by the article

Included files in source:
- sn-article-eng.tex
- sn-article-eng.pdf
- sn-jnl.cls

Build from source folder with:
xelatex -interaction=nonstopmode sn-article-eng.tex

Notes:
- Log files, auxiliary files, template examples, manuals, and unused images were intentionally excluded.
- Figure paths in sn-article-eng.tex were rewritten to use ../figures/...
