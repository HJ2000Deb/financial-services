#!/usr/bin/env python3
"""Bundle the dashboard sources into two single-file builds.

    dist/debretts-portfolio-reporting.html   a complete HTML document, opens
                                             from the filesystem in any browser
    dist/artifact.html                       the same page as a content-only
                                             fragment, for publishing as an
                                             Artifact (the host supplies the
                                             doctype, head and body wrapper)

Usage:  python3 build.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

PARTS_JS = ["data.js", "charts.js", "app.js"]


def read(name: str) -> str:
    return (SRC / name).read_text(encoding="utf-8").rstrip() + "\n"


def guard(name: str, body: str) -> str:
    """Reject anything that would break out of the tag we inline it into."""
    lowered = body.lower()
    for needle in ("</script", "</style"):
        if needle in lowered:
            raise SystemExit(f"{name} contains a literal {needle!r} and cannot be inlined")
    return body


def build() -> None:
    head = read("head.html").rstrip()
    css = guard("styles.css", read("styles.css"))
    body = read("body.html").rstrip()
    js = "\n".join(guard(p, read(p)) for p in PARTS_JS)

    fragment = "\n".join([
        head,
        "<style>",
        css.rstrip(),
        "</style>",
        body,
        "<script>",
        js.rstrip(),
        "</script>",
        "",
    ])

    document = "\n".join([
        "<!doctype html>",
        '<html lang="en-GB">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        head,
        "<style>",
        css.rstrip(),
        "</style>",
        "</head>",
        "<body>",
        body,
        "<script>",
        js.rstrip(),
        "</script>",
        "</body>",
        "</html>",
        "",
    ])

    DIST.mkdir(exist_ok=True)
    (DIST / "artifact.html").write_text(fragment, encoding="utf-8")
    (DIST / "debretts-portfolio-reporting.html").write_text(document, encoding="utf-8")

    for name in ("artifact.html", "debretts-portfolio-reporting.html"):
        size = (DIST / name).stat().st_size
        print(f"wrote dist/{name}  ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
