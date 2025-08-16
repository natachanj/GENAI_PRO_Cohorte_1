import re
from langchain.schema import Document

def clean_text(txt: str) -> str:
    txt = re.sub(r"\s+\n", "\n", txt)
    txt = re.sub(r"\n{2,}", "\n\n", txt)
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt.strip()

def table_to_markdown_and_flat(table):
    rows = [[(c or "").strip() for c in row] for row in table]
    n = max((len(r) for r in rows), default=0)
    header = (rows[0] if rows else []) + [""] * (n - len(rows[0] if rows else []))
    body = [r + [""] * (n - len(r)) for r in rows[1:]]
    md = []
    md.append("| " + " | ".join(header) + " |")
    md.append("| " + " | ".join(["---"] * n) + " |")
    for r in body:
        md.append("| " + " | ".join(r) + " |")
    md = "\n".join(md)
    flat = " | ".join([c for row in rows for c in row if c])
    return md, flat
