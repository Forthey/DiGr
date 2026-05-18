# Railroad-диаграмма EBNF DSL

Это формализованная диаграмма синтаксиса DSL DiGr. Дополняет
[class/query-ast.puml](../class/query-ast.puml): railroad показывает
**грамматику** (правила вывода), а class diagram — **модель AST** после разбора.

Источник: [docs/dsl_grammar.ebnf](../../dsl_grammar.ebnf).

## Как рендерить

Для генерации SVG из EBNF можно использовать любой из инструментов:

- [`ebnf-railroad`](https://www.npmjs.com/package/ebnf-railroad) (Node.js):
  ```bash
  npx ebnf-railroad docs/dsl_grammar.ebnf > docs/uml/grammar/dsl-grammar-railroad.svg
  ```
- [`bottlecaps.de/rr`](https://www.bottlecaps.de/rr/ui) (онлайн): вставить содержимое
  `docs/dsl_grammar.ebnf` → Download Diagram (SVG).
- [`railroad-diagrams`](https://github.com/tabatkins/railroad-diagrams) (Python/JS):
  написать описания правил в DSL библиотеки.

Готовый SVG нужно положить рядом — `dsl-grammar-railroad.svg`.

## Текстовое представление верхнего уровня (для защиты без рендера)

```
query
  ├──▶ context_query  ─▶
  ├──▶ find_query     ─▶
  └──▶ distance_query ─▶

context_query:
    ┌──────────────────────────────────────────────────────────────┐
   ─▶ CONTEXT ─▶ span_spec ─▶ FOR ─▶ pattern_list ─┐               │
                                                   ▼               │
                                          ┌─▶ within_clause ──┐    │
                                          │     (0..n)        │    │
                                          └───────────────────┘    │
                                                   ▼               │
                                          ┌─▶ where_clause ───┐    │
                                          │     (0..1)        │    │
                                          └───────────────────┘    │
                                                   ▼               │
                                          ┌─▶ return_clause ──┐    │
                                          │     (0..1)        │    │
                                          └───────────────────┘    │
                                                   ▼               │
                                          ┌─▶ ";" (0..1)──────┘    │
                                          └────────────────────────┘

find_query:
   ─▶ FIND ─▶ entity_name ─┬─▶ where_clause ─┐
                           ├─▶ within_clause* ┤
                           ├─▶ return_clause ─┤
                           └─▶ ";"?  ────────▶

distance_query:
   ─▶ DISTANCE ─▶ selector ─▶ TO ─▶ selector
                ─▶ within_clause*
                ─▶ limit_pairs_clause?
                ─▶ return_clause            ─▶
                ─▶ ";"?

span_spec        = entity_name '[' count_constraint ']'
within_clause    = 'WITHIN' entity_name '[' count_constraint ']'
count_constraint = ('=' | '<=' | '<' | '>=' | '>') integer
limit_pairs      = 'LIMIT_PAIRS' ('nearest' | 'all_nearest' | 'all' | integer)

selector         = entity_name ( '[' boolean_expr ']' )?

boolean_expr     = disjunction
disjunction      = conjunction ( 'OR' conjunction )*
conjunction      = negation    ( 'AND' negation )*
negation         = 'NOT'? predicate
predicate        = comparison | function_call | '(' boolean_expr ')'

comparison       = field_ref comparison_op value
function_call    = function_name '(' argument_list? ')'
```

## Соответствие модели AST

| Правило грамматики    | Класс модели              |
|-----------------------|---------------------------|
| `context_query`       | `ContextQuery`            |
| `find_query`          | `FindQuery`               |
| `distance_query`      | `DistanceQuery`           |
| `span_spec`           | `SpanSpec`                |
| `within_clause`       | `WithinConstraint`        |
| `count_constraint`    | `CountConstraint`         |
| `selector`            | `Selector`                |
| `pattern`             | `Pattern`                 |
| `comparison`          | `ComparisonExpression`    |
| `function_call`       | `FunctionExpression`      |
| `negation` (NOT)      | `NotExpression`           |
| `disjunction` / `conjunction` | `BinaryExpression`|
| `field_ref`           | `FieldRef`                |
| `regex_literal`       | `RegexLiteral`            |
| `limit_pairs_clause`  | `PairLimit`               |
| `return_item` distance(...) | `DistanceReturn`    |
