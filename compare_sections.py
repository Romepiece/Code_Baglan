from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "article_scopus" / "Article_fixed" / "fixed.tex"
TARGET_PATH = ROOT / "publication_package" / "sn-article-eng.tex"
REPORT_PATH = ROOT / "publication_package" / "section_diff_report.md"
METHODOLOGY_SENTENCE = "1. The systematic logic of the study's design ensures a phased approach to addressing the following tasks:"

SOURCE_HEADINGS = {
    "Introduction",
    "Literature review: a critical synthesis",
    "Theoretical foundations of inclusive development",
    "Financial inclusion: correlation and causality",
    "Gender barriers: an institutional approach",
    "Regional heterogeneity: a gap in the literature",
    "Research methodology",
    "Description of variables and transformation",
    "Analytical modules",
    "Module 1: Identifying causal relationships (fixed-effects panel regression)",
    "Module 2: Analysis of regional heterogeneity by clustering",
    "Module 3: Machine learning for predictive power and nonlinearity assessment",
    "Synthesis of methods and model comparison strategy",
    "Analysis of panel data for 20 regions of Kazakhstan",
    "Panel regression results: econometric analysis",
    "Regional clustering",
    "Analysis of feature importance: random forest",
    "Discussion of the results",
    "Interpretation of key findings: lending constraints",
    "Research results. Therefore, why do not have loans work?",
    "Land as a factor in institutional constraints on the sustainable development of women's entrepreneurship in Kazakhstan",
    "Regional characteristics of support policies for female farmers in Kazakhstan",
    "Reliability of results: methodological aspects",
    "Study limitations and directions for future research",
    "Recommendations for improving Kazakhstan's state agricultural policy",
    "Recommendations at the national level",
    "Differentiated recommendations by region type",
    "Conclusion",
    "Key findings",
    "Contribution to the research",
    "Directions for future research",
    "Directions for improving Kazakhstan's agricultural policy",
    "Basic model",
    "Fixed-effects model",
    "Control variables:",
    "Identifiers:",
    "Key independent variables:",
    "Handling of missing values:",
    "Data sources: National Statistics Bureau of the Agency for Strategic Planning and Reforms of the Republic of Kazakhstan https://stat.gov.kz/:",
}


@dataclass(frozen=True)
class Block:
    name: str
    source_start: str | None
    source_end: str | None
    target_start: str | None
    target_end: str | None
    source_skip_start: bool = False
    target_skip_start: bool = False


BLOCKS = [
    Block(
        name="abstract",
        source_start="Women's entrepreneurship in agriculture is recognized as an important\nfactor in inclusive growth;",
        source_end="Keywords:",
        target_start="\\abstract{",
        target_end="}\n\n\\keywords{",
        source_skip_start=False,
        target_skip_start=True,
    ),
    Block(
        name="introduction",
        source_start="\nIntroduction\n",
        source_end="\n2. Literature review: a critical synthesis\n",
        target_start="\\section{Introduction}",
        target_end="\n\\section{Literature review: a critical synthesis}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="literature_review",
        source_start="\n2. Literature review: a critical synthesis\n",
        source_end="\nResearch methodology\n",
        target_start="\\section{Literature review: a critical synthesis}",
        target_end="\n\\section{Research methodology}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="research_methodology",
        source_start="\nResearch methodology\n",
        source_end="\n4. Synthesis of methods and model comparison strategy\n",
        target_start="\\section{Research methodology}",
        target_end="\n\\section{Synthesis of methods and model comparison strategy}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="results",
        source_start="\n4. Synthesis of methods and model comparison strategy\n",
        source_end="\n5. Discussion of the results\n",
        target_start="\\section{Synthesis of methods and model comparison strategy}",
        target_end="\n\\section{Discussion of the results}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="discussion",
        source_start="\n5. Discussion of the results\n",
        source_end="\n6. Recommendations for improving Kazakhstan's state agricultural policy\n",
        target_start="\\section{Discussion of the results}",
        target_end="\n\\section{Recommendations for improving Kazakhstan's state agricultural policy}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="recommendations",
        source_start="\n6. Recommendations for improving Kazakhstan's state agricultural policy\n",
        source_end="\n7. Conclusion\n",
        target_start="\\section{Recommendations for improving Kazakhstan's state agricultural policy}",
        target_end="\n\\section{Conclusion}",
        source_skip_start=True,
        target_skip_start=True,
    ),
    Block(
        name="conclusion",
        source_start="\n7. Conclusion\n",
        source_end="\nData availability statement\n",
        target_start="\\section{Conclusion}",
        target_end="\n\\backmatter",
        source_skip_start=True,
        target_skip_start=True,
    ),
]


def extract_block(
    text: str,
    start_marker: str | None,
    end_marker: str | None,
    *,
    skip_start_marker: bool,
) -> str:
    start = 0
    if start_marker is not None:
        start = text.find(start_marker)
        if start == -1:
            raise ValueError(f"Start marker not found: {start_marker!r}")
        if skip_start_marker:
            start += len(start_marker)

    end = len(text)
    if end_marker is not None:
        end = text.find(end_marker, start)
        if end == -1:
            raise ValueError(f"End marker not found: {end_marker!r}")

    return text[start:end].strip()


def normalize_source(text: str) -> str:
    text = re.sub(
        r"1\.\s+The systematic logic of the study's design ensures a phased approach\s+to addressing the following tasks:",
        "METHODOLOGY_SENTENCE_PLACEHOLDER",
        text,
    )

    cleaned_lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"^\d+(?:\.\d+)*\.\s+", "", raw_line).strip()
        if line in SOURCE_HEADINGS:
            continue
        cleaned_lines.append(raw_line)
    text = "\n".join(cleaned_lines)

    text = text.replace(r"\textless{}", "<")
    text = text.replace(r"-\/-", "-/-")
    text = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", " ", text, flags=re.S)
    text = re.sub(r"\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}", " ", text, flags=re.S)
    text = text.replace("Descriptive statistics of key variables", " ")
    text = re.sub(r"(?m)^-\s+", "", text)
    text = re.sub(r"\\includegraphics\[[^\]]*\]\{[^}]*\}", " ", text)
    text = re.sub(r"Figure\s+\d+\.\s*", " ", text)
    text = re.sub(r"Table\s+\d+\.\s*", " ", text)
    text = re.sub(r"(?m)^\d+(?:\.\d+)*\.\s+", "", text)
    text = re.sub(r"\(([A-Za-z][^()]*)\d{4}[^()]*\)", " CITATION ", text)
    text = re.sub(r"\b[A-Z][A-Za-z-]+(?:\s+(?:et al\.|\\&|\&|and)\s+[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+)*)?\s*\(\d{4}\)", "CITATION", text)
    text = re.sub(r"\bR²\b", "R^2", text)
    text = re.sub(r"\s+", " ", text)
    for heading in sorted(SOURCE_HEADINGS, key=len, reverse=True):
        text = text.replace(heading, " ")
    text = text.replace("CITATION :", "CITATION:")
    text = text.replace("METHODOLOGY_SENTENCE_PLACEHOLDER", METHODOLOGY_SENTENCE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def strip_tex_command(text: str, command: str) -> str:
    pattern = re.compile(rf"\\{command}\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}", re.S)
    while True:
        updated = pattern.sub(r"\1", text)
        if updated == text:
            return text
        text = updated


def normalize_target(text: str) -> str:
    text = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\\caption\{[^}]*\}", " ", text)
    text = re.sub(r"\\label\{[^}]*\}", " ", text)
    text = text.replace(r"\textless{}", "<")
    text = text.replace("$R^2$", "R^2")
    text = re.sub(r"\\cite[t|p]?\{[^}]*\}", " CITATION ", text)
    text = re.sub(r"\\citet\{[^}]*\}", " CITATION ", text)
    text = re.sub(r"\\citep\{[^}]*\}", " CITATION ", text)
    text = strip_tex_command(text, "emph")
    text = strip_tex_command(text, "textbf")
    text = strip_tex_command(text, "textit")
    text = re.sub(r"\\begin\{itemize\}|\\end\{itemize\}|\\begin\{enumerate\}|\\end\{enumerate\}", " ", text)
    text = re.sub(r"\\item", " ", text)
    text = re.sub(r"\\(section|subsection|subsubsection|paragraph)\*?\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("CITATION :", "CITATION:")
    return text.strip()


def snippet(text: str, start: int, width: int = 120) -> str:
    left = max(0, start - width)
    right = min(len(text), start + width)
    return text[left:right].strip()


def compare_block(block: Block, source_text: str, target_text: str) -> dict[str, object]:
    source_raw = extract_block(
        source_text,
        block.source_start,
        block.source_end,
        skip_start_marker=block.source_skip_start,
    )
    target_raw = extract_block(
        target_text,
        block.target_start,
        block.target_end,
        skip_start_marker=block.target_skip_start,
    )
    source_norm = normalize_source(source_raw)
    target_norm = normalize_target(target_raw)
    matcher = SequenceMatcher(None, source_norm, target_norm)
    ratio = matcher.ratio()

    first_diff = None
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            first_diff = {
                "tag": tag,
                "source": snippet(source_norm, i1),
                "target": snippet(target_norm, j1),
            }
            break

    return {
        "name": block.name,
        "ratio": ratio,
        "source_length": len(source_norm),
        "target_length": len(target_norm),
        "first_diff": first_diff,
    }


def build_report(results: list[dict[str, object]]) -> str:
    lines = ["# Section Diff Report", ""]
    for result in results:
        lines.append(f"## {result['name']}")
        lines.append(f"- similarity: {result['ratio']:.4f}")
        lines.append(f"- source_length: {result['source_length']}")
        lines.append(f"- target_length: {result['target_length']}")
        first_diff = result["first_diff"]
        if first_diff is None:
            lines.append("- first_diff: none")
        else:
            lines.append(f"- first_diff_tag: {first_diff['tag']}")
            lines.append(f"- source_preview: {first_diff['source']}")
            lines.append(f"- target_preview: {first_diff['target']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sections", nargs="*", help="Optional subset of block names to compare")
    args = parser.parse_args()

    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    target_text = TARGET_PATH.read_text(encoding="utf-8")
    selected = {name.lower() for name in args.sections}

    results = []
    for block in BLOCKS:
        if selected and block.name not in selected:
            continue
        results.append(compare_block(block, source_text, target_text))

    report = build_report(results)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()