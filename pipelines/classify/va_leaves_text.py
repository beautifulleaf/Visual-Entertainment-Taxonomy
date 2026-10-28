"""Write the Visual Art leaf list for reviewers and auditors: taxonomy/visual_art/review/va_tree.txt."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import tree_visual_art as VA  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "taxonomy", "visual_art", "review", "va_tree.txt")


def text():
    st = lambda s: re.sub(r"<[^>]+>", "", s or "")
    out = ["TAB KEY"] + [st(k) for k in VA.FAMILY_KEY]
    for fam in VA.FAMILIES:
        out.append(f"\n## {fam['code']} {fam['label']} — test: {st(fam['test'])}")
        out += ["  key: " + st(k) for k in fam["key"]]
        for s, lab, ax in fam["subs"]:
            out.append(f"### {s} {lab} — {ax}")
            for l in VA.LEAVES.get(s, []):
                out.append(f"{l[0]} {l[1]}: {st(l[3])}" + (f" [aka {l[4]}]" if l[4] else ""))
    out.append("\nPRECEDENCE")
    out += [f"{c} {n}: {st(s)}" for c, n, s in VA.PRECEDENCE]
    out.append("\nMODIFIERS (tags and filters, never nodes)")
    out += [st(m) for m in VA.MODIFIERS]
    return "\n".join(out)


if __name__ == "__main__":
    open(OUT, "w", encoding="utf-8").write(text())
    print(OUT, os.path.getsize(OUT) // 1024, "KB")
