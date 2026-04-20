from __future__ import annotations

from pathlib import Path

from document_ast import ActorAstParser


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def test_tex_format_builds_expected_scopes_and_semantic_blocks(workspace_tmp: Path, config_dir: Path) -> None:
    source = workspace_tmp / "sample.tex"
    source.write_text(
        r"""
\section{Раздел}
\begin{frame}
\frametitle{Слайд}
Вводный текст.
\begin{theorem}
Теорема внутри frame.
\end{theorem}
\end{frame}

\subsection{Подраздел}
\subsubsection{Деталь}\label{detail}
\begin{definition}
Определение вне frame.
\end{definition}
\begin{proof}
Доказательство вне frame.
\end{proof}
""".strip(),
        encoding="utf-8",
    )

    document = ActorAstParser.from_config_dir(config_dir).parse(source, format_name="tex")
    nodes = list(walk(document.root))

    assert document.root_entity == "section"
    assert [node.entity for node in document.root.children] == ["section"]

    content_scope_kinds = [node.metadata.get("kind") for node in nodes if node.entity == "content_scope"]
    assert content_scope_kinds == ["free", "frame", "free"]

    semantic_kinds = [node.metadata.get("kind") for node in nodes if node.entity == "semantic_block"]
    assert "frametitle" in semantic_kinds
    assert "theorem" in semantic_kinds
    assert "subsubsection" in semantic_kinds
    assert "definition" in semantic_kinds
    assert "proof" in semantic_kinds

    theorem = next(node for node in nodes if node.entity == "semantic_block" and node.metadata.get("kind") == "theorem")
    definition = next(node for node in nodes if node.entity == "semantic_block" and node.metadata.get("kind") == "definition")
    proof = next(node for node in nodes if node.entity == "semantic_block" and node.metadata.get("kind") == "proof")

    assert "Теорема внутри frame." in theorem.text
    assert "Определение вне frame." in definition.text
    assert "Доказательство вне frame." in proof.text
