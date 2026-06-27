"""Shared data models for paper metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Paper:
    """Normalized paper metadata used across the application."""

    paper_id: str
    title: str
    authors: list[str]
    summary: str
    published: str
    arxiv_url: str
    pdf_url: str
    categories: list[str]
    relevance_score: float = field(default=0.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert a paper into a JSON-serializable dictionary."""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": list(self.authors),
            "summary": self.summary,
            "published": self.published,
            "arxiv_url": self.arxiv_url,
            "pdf_url": self.pdf_url,
            "categories": list(self.categories),
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        """Create a paper from a dictionary loaded from JSON."""
        required_fields = {
            "paper_id",
            "title",
            "authors",
            "summary",
            "published",
            "arxiv_url",
            "pdf_url",
            "categories",
        }
        missing_fields = required_fields.difference(data)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Paper data is missing required field(s): {missing}")

        authors = data["authors"]
        categories = data["categories"]
        if not isinstance(authors, list) or not all(
            isinstance(item, str) for item in authors
        ):
            raise ValueError("Paper authors must be a list of strings.")
        if not isinstance(categories, list) or not all(
            isinstance(item, str) for item in categories
        ):
            raise ValueError("Paper categories must be a list of strings.")

        return cls(
            paper_id=str(data["paper_id"]),
            title=str(data["title"]),
            authors=list(authors),
            summary=str(data["summary"]),
            published=str(data["published"]),
            arxiv_url=str(data["arxiv_url"]),
            pdf_url=str(data["pdf_url"]),
            categories=list(categories),
            relevance_score=float(data.get("relevance_score", 0.0)),
        )
