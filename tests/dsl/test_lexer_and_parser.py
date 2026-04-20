from __future__ import annotations

import pytest

from dsl import ActorDslParser, DslLexer, DslSyntaxError, DslTokenStreamParser, FindQuery, SpanSpec, TokenKind


def test_dsl_lexer_tokenizes_keywords_literals_and_regex() -> None:
    source = 'FIND sentence WHERE text ~= /телефон/i RETURN text, count'

    tokens = DslLexer().tokenize(source)

    assert [token.kind for token in tokens[:8]] == [
        TokenKind.FIND,
        TokenKind.IDENTIFIER,
        TokenKind.WHERE,
        TokenKind.IDENTIFIER,
        TokenKind.MATCH,
        TokenKind.REGEX,
        TokenKind.RETURN,
        TokenKind.IDENTIFIER,
    ]
    assert tokens[5].value == {"pattern": "телефон", "flags": "i"}


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('FIND sentence WHERE text = "bad\\q"', "Unsupported escape sequence"),
        ("FIND sentence WHERE text ~= /bad/x", "Unsupported regex flag"),
        ("FIND sentence @", "Unexpected character"),
    ],
)
def test_dsl_lexer_reports_syntax_errors(source: str, message: str) -> None:
    with pytest.raises(DslSyntaxError, match=message):
        DslLexer().tokenize(source)


def test_dsl_parser_builds_context_query_with_aliases_and_returns() -> None:
    source = """
    CONTEXT sentence[<=4]
    FOR door: "дверь", quiet: /тишина/i, hit: word[text = "дверь"]
    WITHIN paragraph[=1]
    WHERE NOT text = "x"
    RETURN text, matches, count;
    """

    query = DslTokenStreamParser(DslLexer().tokenize(source)).parse_query()
    payload = query.to_dict()

    assert payload["type"] == "context_query"
    assert payload["span"]["entity_name"] == "sentence"
    assert [pattern["alias"] for pattern in payload["patterns"]] == ["door", "quiet", "hit"]
    assert payload["within"][0]["entity_name"] == "paragraph"
    assert payload["returns"] == ["text", "matches", "count"]


def test_dsl_parser_builds_find_query() -> None:
    query = DslTokenStreamParser(
        DslLexer().tokenize('FIND sentence WHERE text ~= /тишина/i RETURN text')
    ).parse_query()

    assert isinstance(query, FindQuery)
    assert query.entity_name == "sentence"
    assert query.returns == ["text"]


def test_dsl_parser_treats_bracketed_argument_as_span_spec() -> None:
    source = "FIND sentence WHERE has_child(word[<=1])"

    query = DslTokenStreamParser(DslLexer().tokenize(source)).parse_query()

    assert isinstance(query.where.arguments[0], SpanSpec)
    assert query.where.arguments[0].entity_name == "word"


def test_actor_dsl_parser_surfaces_syntax_errors() -> None:
    with pytest.raises(DslSyntaxError, match="Expected comparison operator"):
        ActorDslParser().parse("FIND sentence WHERE text")
