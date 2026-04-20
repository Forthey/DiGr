from __future__ import annotations

import pytest

from dsl import ActorDslExecutor, ActorDslParser


def test_actor_dsl_parser_and_executor_find_phone(sample_document) -> None:
    query = ActorDslParser().parse(
        """
        FIND sentence
        WHERE has_descendant(word[text ~= /телефон/i])
        RETURN text, count
        """.strip()
    )

    payload = ActorDslExecutor().execute(sample_document, query).to_dict()

    assert payload["count"] == 2
    assert [item["text"] for item in payload["items"]] == [
        "В девять часов телефон наконец завибрировал.",
        "Телефон снова завибрировал.",
    ]


def test_actor_dsl_engine_executes_context_query(dsl_engine, sample_document) -> None:
    payload = dsl_engine.execute(
        sample_document,
        """
        CONTEXT sentence[<=4]
        FOR "дверь", "тишина"
        WITHIN paragraph[=1]
        RETURN text, matches, count
        """.strip(),
    ).to_dict()

    assert payload["type"] == "context_query_execution_result"
    assert payload["count"] == 1
    assert "Только тишина." in payload["items"][0]["text"]
    assert [match["matched_text"] for match in payload["items"][0]["matches"]] == ["дверь", "тишина"]


def test_actor_dsl_engine_rejects_unknown_entities(sample_document, dsl_engine) -> None:
    with pytest.raises(ValueError, match="ghost"):
        dsl_engine.execute(sample_document, "FIND ghost RETURN text")
