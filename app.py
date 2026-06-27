"""Streamlit app for the Embodied AI Research Assistant MVP."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from research_assistant.arxiv_client import search_papers
from research_assistant.config import DEFAULT_MAX_RESULTS, MAX_RESULTS_OPTIONS
from research_assistant.models import Paper
from research_assistant.ranking import rank_papers
from research_assistant.storage import (
    add_to_reading_list,
    load_reading_list,
    remove_from_reading_list,
)


@st.cache_data(ttl=600)
def cached_search(query: str, max_results: int) -> list[Paper]:
    """Cache arXiv search results for a short period to reduce repeat calls."""
    papers = search_papers(query, max_results)
    return rank_papers(papers, query)


def main() -> None:
    st.set_page_config(page_title="Embodied AI Research Assistant", layout="wide")

    st.title("Embodied AI Research Assistant")
    st.caption(
        "A rule-based tool for discovering and organizing arXiv papers in "
        "embodied AI and robotics research."
    )
    st.caption(
        "MVP scope: arXiv retrieval, transparent keyword-based ranking, and "
        "local reading-list management."
    )

    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""

    query = st.text_input(
        "Search keywords",
        value=st.session_state.last_query,
        placeholder="embodied AI, vision-language-action, robot navigation",
    )
    max_results = st.selectbox(
        "Max results",
        options=MAX_RESULTS_OPTIONS,
        index=MAX_RESULTS_OPTIONS.index(DEFAULT_MAX_RESULTS),
    )

    if st.button("Search", type="primary"):
        try:
            st.session_state.search_results = cached_search(query, int(max_results))
            st.session_state.last_query = query
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error while searching papers: {exc}")

    st.divider()
    _render_search_results(st.session_state.search_results)

    st.divider()
    _render_reading_list()


def _render_search_results(papers: list[Paper]) -> None:
    st.subheader("Search Results")
    if not papers:
        st.write("No search results yet.")
        return

    for paper in papers:
        with st.container(border=True):
            _render_paper_metadata(paper)
            if st.button(
                "Add to Reading List",
                key=f"add-{_safe_key(paper.paper_id)}",
            ):
                try:
                    added = add_to_reading_list(paper)
                    if added:
                        st.success("Added to reading list.")
                    else:
                        st.info("This paper is already in the reading list.")
                except ValueError as exc:
                    st.error(str(exc))


def _render_reading_list() -> None:
    st.subheader("Reading List")
    try:
        papers = load_reading_list()
    except ValueError as exc:
        st.error(str(exc))
        return

    if not papers:
        st.write("Your reading list is empty.")
        return

    for paper in papers:
        with st.container(border=True):
            _render_paper_metadata(paper)
            if st.button("Remove", key=f"remove-{_safe_key(paper.paper_id)}"):
                try:
                    removed = remove_from_reading_list(paper.paper_id)
                    if removed:
                        st.success("Removed from reading list.")
                        st.rerun()
                    else:
                        st.info("This paper was not found in the reading list.")
                except ValueError as exc:
                    st.error(str(exc))


def _render_paper_metadata(paper: Paper) -> None:
    st.markdown(f"### {paper.title}")
    st.write(f"**Authors:** {', '.join(paper.authors) or 'Unknown'}")
    st.write(f"**Published:** {paper.published or 'Unknown'}")
    st.write(f"**Categories:** {', '.join(paper.categories) or 'Uncategorized'}")
    st.write(f"**Rule relevance score:** {paper.relevance_score:.1f}")
    st.write(paper.summary)
    st.markdown(f"[arXiv]({paper.arxiv_url}) | [PDF]({paper.pdf_url})")


def _safe_key(value: str) -> str:
    return value.replace("/", "-").replace(".", "-")


if __name__ == "__main__":
    main()
