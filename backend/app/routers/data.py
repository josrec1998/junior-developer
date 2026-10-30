
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Depends
from gliner2 import GLiNER2
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult

from app.dependencies import get_model
from app.models import Data, Source

router = APIRouter(tags=["data"])

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "mock.json"

PII_LABELS = [
    "full_name",
    "first_name",
    "last_name",
    "email",
    "phone_number",
]

REPLACEMENTS = {
    "full_name": "[NAME]",
    "first_name": "[NAME]",
    "last_name": "[NAME]",
    "email": "[EMAIL]",
    "phone_number": "[PHONE]",
}


def get_favicon(url: str) -> str | None:
    """Build a favicon URL from a source website."""

    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
        return None

    return f"{parsed_url.scheme}://{parsed_url.hostname}/favicon.ico"


def link_citations(content: str, sources: list[Source]) -> str:
    """Replace reference tags with links to matching sources."""

    source_lookup = {source.id: source for source in sources}

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

    return re.sub(r"<ref>(.*?)</ref>", replace_reference, content)


def redact_question(question: str, model: GLiNER2) -> str:
    """Detect personal details with GLiNER2 and replace them using Presidio."""

    detections = model.extract_entities(
        question,
        PII_LABELS,
        include_spans=True,
        include_confidence=True,
    )

    results = []

    for label, entities in detections["entities"].items():
        if label not in REPLACEMENTS:
            continue

        for entity in entities:
            results.append(
                RecognizerResult(
                    entity_type=label,
                    start=entity["start"],
                    end=entity["end"],
                    score=entity.get("confidence", 1.0),
                )
            )

    if not results:
        return question

    operators = {
        label: OperatorConfig(
            "replace",
            {"new_value": replacement},
        )
        for label, replacement in REPLACEMENTS.items()
    }

    anonymizer = AnonymizerEngine()

    return anonymizer.anonymize(
        text=question,
        analyzer_results=results,
        operators=operators,
    ).text


@router.get("/data")
def get_data(model: GLiNER2 = Depends(get_model)) -> list[Data]:
    """Return records with redacted questions, linked citations and favicons."""

    items = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    processed_items = []

    for item in items:
        data = Data.model_validate(item)

        data.question = redact_question(data.question, model)
        data.content = link_citations(data.content, data.sources)

        for source in data.sources:
            source.favicon = get_favicon(source.source)

        processed_items.append(data)

    return processed_items
