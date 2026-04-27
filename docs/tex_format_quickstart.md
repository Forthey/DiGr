# Быстрый старт по формату `tex`

## Что именно поддерживается

Формат `tex` в DiGr сделан как прикладной разбор для `GA_1_2025.tex`, а не как полный TeX-парсер.

Он строит AST со следующими сущностями:

- `section`
- `subsection_scope`
- `content_scope`
- `semantic_block`
- `definition`
- `symbol`

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

`definition` выделяет inline-команды `\odmkey{...}{...}` внутри `semantic_block`.
В `metadata.name` сохраняется первый аргумент, а в `metadata.index` второй аргумент.

`symbol` создаётся автоматически под `semantic_block`.
Он соответствует одному Unicode code point исходного TeX-текста и доступен для `FIND`, `CONTEXT` и `DISTANCE`, например через `distance(symbol)`.

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

Найти все определения/термины, размеченные `\odmkey`:

```dsl
FIND definition
RETURN text, count
```

Найти определение по названию:

```dsl
FIND definition
WHERE metadata.name = "алфавитом"
RETURN text, nodes, count
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

Найти смысловые блоки, внутри которых есть определения:

```dsl
FIND semantic_block
WHERE has_child(definition)
RETURN text, count
```

## Ограничения

- `frame` не выделяется отдельной AST-сущностью; вместо этого используется `content_scope[metadata.kind = "frame"]`.
- окружение `\begin{definition}...\end{definition}` остаётся отдельным видом `semantic_block` и в `GA_1_2025.tex` встречается редко; для терминологических определений используйте entity `definition`.
- Разбор ориентирован на реальные конвенции `GA_1_2025.tex`; для произвольного TeX-документа правила могут потребовать отдельной настройки.
