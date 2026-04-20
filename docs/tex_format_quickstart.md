# Быстрый старт по формату `tex`

## Что именно поддерживается

Формат `tex` в DiGr сделан как прикладной разбор для `GA_1_2025.tex`, а не как полный TeX-парсер.

Он строит AST со следующими сущностями:

- `section`
- `subsection_scope`
- `content_scope`
- `semantic_block`

`content_scope` и `semantic_block` используют `metadata.kind`.

Поддержанные `content_scope.metadata.kind`:

- `frame`
- `free`

Поддержанные `semantic_block.metadata.kind`:

- `frametitle`
- `subsubsection`
- `definition`
- `theorem`
- `lemma`
- `proof`
- `example`
- `remark`
- `digress`
- `itemize`
- `enumerate`
- `plain`

Это позволяет искать смысловые блоки DSL-запросами, не делая полноценный синтаксический анализ TeX.

## Как загрузить `GA_1_2025.tex`

CLI:

```bash
PYTHONPATH=src python src/main.py GA_1_2025.tex --format tex
```

Python API:

```python
from document_ast import ActorAstParser


document = ActorAstParser.from_config_dir("config/formats").parse(
    "GA_1_2025.tex",
    format_name="tex",
)
```

## Как искать через DSL

Найти все определения:

```dsl
FIND semantic_block
WHERE metadata.kind = "definition"
RETURN text, count
```

Найти все теоремы:

```dsl
FIND semantic_block
WHERE metadata.kind = "theorem"
RETURN text, count
```

Найти доказательства в нужном разделе:

```dsl
FIND semantic_block
WHERE metadata.kind = "proof"
  AND has_ancestor(section[text ~= /Языки и грамматики/])
RETURN text, count
```

Найти реальные `frame`-области:

```dsl
FIND content_scope
WHERE metadata.kind = "frame"
RETURN text, count
```

Найти смысловые блоки с `\odmkey`:

```dsl
FIND semantic_block
WHERE text ~= /\\odmkey\{/ 
RETURN text, count
```

## Ограничения

- `frame` не выделяется отдельной AST-сущностью; вместо этого используется `content_scope[metadata.kind = "frame"]`.
- `\odmkey{...}{...}` остаётся inline-конструкцией внутри текста блока.
- Разбор ориентирован на реальные конвенции `GA_1_2025.tex`; для произвольного TeX-документа правила могут потребовать отдельной настройки.
