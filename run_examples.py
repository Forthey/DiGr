from __future__ import annotations

import json
import sys

from document_ast import ActorAstParser
from dsl import ActorDslEngine

QUERIES = [
    ("FIND definition", """FIND definition
WHERE metadata.index ~= "Язык"
RETURN text, count"""),
    ("DISTANCE definition->definition (symbol)", """DISTANCE definition [metadata.index ~= "Язык"]
TO definition [metadata.index ~= "Язык"]
LIMIT_PAIRS all
RETURN pairs, stats, distance(symbol), count"""),
    ("DISTANCE definition->definition (definition)", """DISTANCE definition [metadata.index ~= "Язык"]
TO definition [metadata.index ~= "Язык"]
LIMIT_PAIRS all
RETURN pairs, stats, distance(definition), count"""),
    ("DISTANCE definition->theorem (symbol)", """DISTANCE definition [metadata.index ~= "Язык"]
TO semantic_block [metadata.kind = "theorem"]
LIMIT_PAIRS all
RETURN pairs, stats, distance(symbol), count"""),
]


def main() -> int:
    source = sys.argv[1] if len(sys.argv) > 1 else "GA_1_2025.tex"
    parser = ActorAstParser.from_config_dir("config/formats")
    document = parser.parse(source)
    engine = ActorDslEngine()

    for title, query in QUERIES:
        print("=" * 80)
        print(f"### {title}")
        print("--- query ---")
        print(query)
        print("--- result ---")
        try:
            result = engine.execute(document, query)
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
