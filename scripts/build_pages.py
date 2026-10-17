from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "paginas"
MANIFEST = ROOT / "pages.json"


def clean(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", unescape(value)).strip()


def tag_content(html: str, tag: str) -> str:
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, flags=re.I | re.S)
    return clean(match.group(1)) if match else ""


def meta_content(html: str, name: str) -> str:
    patterns = [
        rf'<meta\s+[^>]*name=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
        rf'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']{re.escape(name)}["\'][^>]*>',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I | re.S)
        if match:
            return clean(match.group(1))
    return ""


def git_date(path: Path, first: bool = False) -> str:
    args = ["git", "log", "--follow", "--format=%cs"]
    if not first:
        args.append("-1")
    args += ["--", str(path.relative_to(ROOT))]
    try:
        output = subprocess.check_output(args, cwd=ROOT, text=True).strip().splitlines()
        if output:
            return output[-1] if first else output[0]
    except Exception:
        pass
    return date.today().isoformat()


def existing_manifest() -> dict[str, dict]:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        pages = data if isinstance(data, list) else data.get("pages", [])
        return {str(item.get("file")): item for item in pages if item.get("file")}
    except Exception:
        return {}


def build() -> None:
    previous = existing_manifest()
    result: list[dict] = []

    if PAGES_DIR.exists():
        for path in sorted(PAGES_DIR.rglob("*.html")):
            rel = path.relative_to(PAGES_DIR).as_posix()
            html = path.read_text(encoding="utf-8", errors="ignore")
            old = previous.get(rel, {})

            title = tag_content(html, "title") or old.get("title") or path.stem.replace("-", " ").replace("_", " ").title()
            description = meta_content(html, "description") or old.get("description") or "Página HTML publicada no hub."
            category = meta_content(html, "category") or old.get("category") or "Outros"

            keywords = meta_content(html, "keywords")
            tags = [clean(tag) for tag in keywords.split(",") if clean(tag)] if keywords else old.get("tags", [])

            item = {
                "title": title,
                "description": description,
                "file": rel,
                "category": category,
                "tags": tags,
                "created": old.get("created") or git_date(path, first=True),
                "updated": git_date(path),
                "views": old.get("views", 0),
            }

            for optional in ("readTime", "featured"):
                if optional in old:
                    item[optional] = old[optional]

            result.append(item)

    result.sort(key=lambda item: (item.get("created", ""), item.get("title", "")), reverse=True)
    MANIFEST.write_text(
        json.dumps({"pages": result}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Catálogo atualizado: {len(result)} página(s).")


if __name__ == "__main__":
    build()
