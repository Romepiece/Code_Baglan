import re
from difflib import SequenceMatcher
from pathlib import Path

src = Path(r"article_scopus/Article_fixed/fixed.tex").read_text(encoding="utf-8")
tgt = Path(r"publication_package/sn-article-eng.tex").read_text(encoding="utf-8")

def extract_body(text):
    start_markers = [r"\\section\{Introduction\}", r"\\section\{INTRODUCTION\}"]
    end_markers = [r"\\section\{References\}", r"\\bibliography\{", r"\\backmatter"]
    start = 0
    for m in start_markers:
        found = re.search(m, text)
        if found:
            start = found.start()
            break
    end = len(text)
    for m in end_markers:
        found = re.search(m, text)
        if found:
            end = min(end, found.start())
    return text[start:end]


def normalize(text):
    text = extract_body(text)
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}", r"\n\2\n", text)
    text = re.sub(r"\\begin\{(figure|table|table\*|figure\*)\}.*?\\end\{\1\}", " ", text, flags=re.S)
    text = re.sub(r"\\caption\{[^}]*\}", " ", text)
    text = re.sub(r"\\label\{[^}]*\}", " ", text)
    text = re.sub(r"\\cite[t|p]?\{[^}]*\}", " CITATION ", text)
    text = re.sub(r"\\citet\{[^}]*\}", " CITATION ", text)
    text = re.sub(r"\\citep\{[^}]*\}", " CITATION ", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\begin\{itemize\}|\\end\{itemize\}|\\begin\{enumerate\}|\\end\{enumerate\}", " ", text)
    text = re.sub(r"\\item", "\n- ", text)
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

src_n = normalize(src)
tgt_n = normalize(tgt)
sm = SequenceMatcher(None, src_n, tgt_n)
blocks = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    a = src_n[max(0, i1-80):min(len(src_n), i2+80)]
    b = tgt_n[max(0, j1-80):min(len(tgt_n), j2+80)]
    blocks.append((tag, a, b))

out = Path(r"publication_package/strict_diff_after_patch.txt")
with out.open("w", encoding="utf-8") as f:
    f.write(f"diff_groups={len(blocks)}\n\n")
    for idx, (tag, a, b) in enumerate(blocks, 1):
        f.write(f"## DIFF {idx} [{tag}]\n")
        f.write("SOURCE:\n")
        f.write(a + "\n")
        f.write("TARGET:\n")
        f.write(b + "\n\n")
print(f"diff_groups={len(blocks)}")
print(out)
