from __future__ import annotations

from pathlib import Path

import pytest

from document_ast import ActorAstParser
from dsl import ActorDslEngine


@pytest.fixture(scope="session")
def ga_tex_path(repo_root: Path) -> Path:
    path = repo_root / "GA_1_2025.tex"
    if not path.exists():
        pytest.skip("GA_1_2025.tex is required for tex integration checks")
    return path


@pytest.fixture(scope="session")
def ga_tex_document(ga_tex_path: Path, config_dir: Path):
    parser = ActorAstParser.from_config_dir(config_dir)
    return parser.parse(ga_tex_path, format_name="tex")


def test_tex_parser_builds_ast_for_ga_source(ga_tex_document) -> None:
    assert ga_tex_document.format_name == "tex"
    assert ga_tex_document.root_entity == "section"
    assert ga_tex_document.root.children


def test_tex_dsl_finds_definitions_theorems_and_frame_scopes(ga_tex_document) -> None:
    engine = ActorDslEngine()

    definitions = engine.execute(
        ga_tex_document,
        'FIND semantic_block WHERE metadata.kind = "definition" RETURN count',
    ).to_dict()
    theorems = engine.execute(
        ga_tex_document,
        'FIND semantic_block WHERE metadata.kind = "theorem" RETURN count',
    ).to_dict()
    frame_scopes = engine.execute(
        ga_tex_document,
        'FIND content_scope WHERE metadata.kind = "frame" RETURN count',
    ).to_dict()

    assert definitions["count"] >= 1
    assert theorems["count"] >= 1
    assert frame_scopes["count"] >= 1


def test_tex_dsl_finds_definition_text_within_section_context(ga_tex_document) -> None:
    engine = ActorDslEngine()

    payload = engine.execute(
        ga_tex_document,
        """
        FIND semantic_block
        WHERE metadata.kind = "definition"
          AND has_ancestor(section[text ~= /Языки и грамматики/])
        RETURN text, count
        """.strip(),
    ).to_dict()

    assert payload["count"] >= 1
    assert "левым разбором" in payload["items"][0]["text"].lower()
