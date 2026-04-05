from __future__ import annotations

import argparse
import json
import sys

from document_ast import ActorAstParser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build AST for a document using actor pipeline")
    parser.add_argument("source", nargs="?", default="text.txt", help="Path to source document")
    parser.add_argument(
        "--config-dir",
        default="config/formats",
        help="Directory with per-format YAML configs (<format>.yaml)",
    )
    parser.add_argument(
        "--format",
        dest="format_name",
        default=None,
        help="Explicit format name. By default it is detected from file extension.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    parser = ActorAstParser.from_config_dir(args.config_dir)
    document = parser.parse(args.source, format_name=args.format_name)
    print(json.dumps(document.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
