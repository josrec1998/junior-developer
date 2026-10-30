import json
from pathlib import Path

from fastapi import APIRouter

from app.models import Data

router = APIRouter(tags=["data"])

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "mock.json"

def get_favicon(url: str) -> str | None:
    """Build a favicon from  source website."""

    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
        return None

    return f"{parsed_url.scheme}://{parsed_url.hostname}/favicon.ico"


def link_citations(content: str, sources: list) -> str:
    """Replace reference ids with clickable source links."""

    source_lookup = {
        source.id: source
        for source in sources
    }

    def replace_reference(match):
        source_id = match.group(1)
        source = source_lookup.get(source_id)

        if source is None:
            return escape(match.group(0))

        parsed_url = urlparse(source.source)

        if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
            return escape(match.group(0))

        safe_url = escape(source.source, quote=True)
        safe_title = escape(source.title)

        return (
            f'<a href="{safe_url}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'{safe_title}</a>'
        )

    return re.sub(
        r"<ref>(.*?)</ref>",
        replace_reference,
        content
    )


@router.get("/data")
def get_data() -> list[Data]:
    """Return data with linked citations and source favicons."""

    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    processed_items = []

    for item in items:
        data = Data.model_validate(item)

        data.content = link_citations(
            data.content,
            data.sources
        )

        for source in data.sources:
            source.favicon = get_favicon(source.source)

        processed_items.append(data)

    return processed_items