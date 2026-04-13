# Архитектура DSL

## Назначение подсистемы

Подсистема `src/dsl` решает две задачи:

1. разобрать текст DSL-запроса в AST запроса;
2. выполнить этот запрос по `AstDocument`, построенному в `document_ast`.

То есть DSL в проекте уже реализован как полноценная исполняемая подсистема:

```text
query text -> query AST -> execution over AstDocument -> structured result
```

Класс-диаграмма подсистемы находится в [dsl_architecture.puml](./uml/dsl_architecture.puml).

## Главная идея архитектуры

DSL разделён не по «техническим файлам», а по смысловым слоям:

- `api`
- `model`
- `parsing`
- `execution`
- `actors/parsing`
- `actors/execution`

Это отражает реальную логику работы:

- сначала есть внешний API;
- затем модель языка;
- затем синтаксический разбор;
- затем семантическое выполнение;
- и для parsing/execution отдельно используется actor runtime.

## Публичный API

Публичный слой лежит в `src/dsl/api`.

Ключевые классы:

- [ActorDslParser](/home/forthey/projects/DiGr/src/dsl/api/query_parser.py)
- [ActorDslExecutor](/home/forthey/projects/DiGr/src/dsl/api/query_executor.py)
- [ActorDslEngine](/home/forthey/projects/DiGr/src/dsl/api/engine.py)

Роли:

- `ActorDslParser` разбирает текст запроса и возвращает `DslQuery`;
- `ActorDslExecutor` принимает `DslQuery` и `AstDocument`, затем возвращает результат выполнения;
- `ActorDslEngine` объединяет оба шага и принимает уже строку запроса.

Именно `ActorDslEngine` удобен для end-to-end сценария.

## Модель языка

Синтаксическая модель языка лежит в [query_ast.py](/home/forthey/projects/DiGr/src/dsl/model/query_ast.py).

Ключевые типы:

- `ContextQuery`
- `FindQuery`
- `Pattern`
- `Selector`
- `SpanSpec`
- `WithinConstraint`
- `FieldRef`
- `RegexLiteral`
- `ComparisonExpression`
- `FunctionExpression`
- `BinaryExpression`
- `NotExpression`

Это означает, что запрос после парсинга хранится не в loosely-typed словаре, а в нормальном внутреннем AST.

## Parsing-слой

Слой синтаксического разбора живёт в `src/dsl/parsing`.

Его состав:

- [errors.py](/home/forthey/projects/DiGr/src/dsl/parsing/errors.py)
- [token_kind.py](/home/forthey/projects/DiGr/src/dsl/parsing/token_kind.py)
- [token.py](/home/forthey/projects/DiGr/src/dsl/parsing/token.py)
- [lexer.py](/home/forthey/projects/DiGr/src/dsl/parsing/lexer.py)
- [recursive_descent_parser.py](/home/forthey/projects/DiGr/src/dsl/parsing/recursive_descent_parser.py)
- [messages.py](/home/forthey/projects/DiGr/src/dsl/parsing/messages.py)
- [states.py](/home/forthey/projects/DiGr/src/dsl/parsing/states.py)
- [runtime.py](/home/forthey/projects/DiGr/src/dsl/parsing/runtime.py)

### Что делает lexer

`DslLexer` преобразует строку в поток токенов:

- keywords;
- identifiers;
- string literals;
- regex literals;
- integers;
- punctuation;
- operators.

Если в запросе синтаксическая ошибка на уровне лексики, выбрасывается `DslSyntaxError` с позицией:

- offset;
- line;
- column.

### Что делает parser

`DslTokenStreamParser` реализует recursive-descent parser для:

- `CONTEXT`;
- `FIND`;
- `WHERE`;
- `WITHIN`;
- `RETURN`;
- selectors;
- boolean expressions;
- function calls.

Это удобный выбор для текущего языка, потому что:

- грамматика достаточно компактна;
- приоритеты `NOT / AND / OR` задаются явно;
- ошибки можно формулировать детально.

## Actor runtime разбора DSL

Разбор DSL тоже реализован как actor pipeline.

Акторы лежат в `src/dsl/actors/parsing`:

- [lexer_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/parsing/lexer_actor.py)
- [query_parser_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/parsing/query_parser_actor.py)
- [parser_coordinator_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/parsing/parser_coordinator_actor.py)
- [parse_result_collector_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/parsing/parse_result_collector_actor.py)

Роли:

- `DslLexerActor` токенизирует запрос;
- `DslQueryParserActor` строит AST запроса;
- `DslParserCoordinatorActor` управляет последовательностью стадий;
- `DslParseResultCollectorActor` сохраняет результат или ошибку.

### Почему parser actor сделан фазовым FSM

`DslQueryParserActor` не живёт в состояниях вида `idle / working`.

У него есть фазовые состояния:

- `CLASSIFYING_QUERY`
- `PARSING_CONTEXT_SPAN`
- `PARSING_CONTEXT_PATTERNS`
- `PARSING_CONTEXT_CONSTRAINTS`
- `PARSING_FIND_TARGET`
- `PARSING_FIND_CONSTRAINTS`

Это важно, потому что тогда состояние актора отражает реальную стадию разбора.

## Execution-слой DSL

Слой исполнения лежит в `src/dsl/execution`.

Ключевые модули:

- [document_index.py](/home/forthey/projects/DiGr/src/dsl/execution/document_index.py)
- [predicate_evaluator.py](/home/forthey/projects/DiGr/src/dsl/execution/predicate_evaluator.py)
- [query_validator.py](/home/forthey/projects/DiGr/src/dsl/execution/query_validator.py)
- [query_results.py](/home/forthey/projects/DiGr/src/dsl/execution/query_results.py)
- [messages.py](/home/forthey/projects/DiGr/src/dsl/execution/messages.py)
- [states.py](/home/forthey/projects/DiGr/src/dsl/execution/states.py)
- [runtime.py](/home/forthey/projects/DiGr/src/dsl/execution/runtime.py)

### `DocumentIndex`

`DocumentIndex` строит навигационное представление по `AstDocument`:

- список всех узлов;
- узлы по типам сущностей;
- связи родитель/потомок;
- поиск соседних узлов;
- поиск контейнеров по span.

Это инфраструктурная часть execution-слоя.

### `PredicateEvaluator`

`PredicateEvaluator` реализует смысл операторов и функций DSL:

- сравнения полей;
- regex matching;
- `has_child`
- `has_descendant`
- `has_ancestor`
- `contains`
- `follows`
- `precedes`
- `intersects`
- `inside`

Кроме того, он умеет:

- искать pattern-совпадения внутри `CONTEXT`-окна;
- проверять `WITHIN`-ограничения;
- считать количество контейнеров нужного типа.

### `QueryValidator`

`QueryValidator` проверяет, что запрос совместим с реальным документом.

Например, если запрос ссылается на сущность, которой нет в AST данного формата, выполнение должно завершиться с понятной ошибкой, а не с неочевидным поведением evaluator-а.

### `QueryResults`

Результаты оформлены отдельно:

- `FindQueryExecutionResult`
- `ContextQueryExecutionResult`

Это удобно, потому что результат выполнения уже имеет свою модель, а не строится «на лету» ad hoc.

## Actor runtime выполнения DSL

Исполнение DSL тоже выполнено как actor pipeline.

Акторы лежат в `src/dsl/actors/execution`:

- [execution_coordinator_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/execution/execution_coordinator_actor.py)
- [execution_worker_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/execution/execution_worker_actor.py)
- [execution_result_collector_actor.py](/home/forthey/projects/DiGr/src/dsl/actors/execution/execution_result_collector_actor.py)

### Роли

- `DslExecutionCoordinatorActor` валидирует запрос, раздаёт задачи worker-ам и собирает результат;
- `DslExecutionWorkerActor` вычисляет соответствие для одного кандидата `FIND` или одного стартового окна `CONTEXT`;
- `DslExecutionResultCollectorActor` сохраняет финальный результат или ошибку.

### Разделение по состояниям

Координатор исполнения использует не абстрактные состояния «работает / не работает», а состояния доменной фазы:

- `IDLE`
- `EVALUATING_FIND_CANDIDATES`
- `EVALUATING_CONTEXT_WINDOWS`
- `COMPLETED`

Это делает FSM осмысленной и упрощает reasoning по коду.

## Как DSL связан с `document_ast`

DSL не читает файлы напрямую.

Он использует только внешний интерфейс `AstDocument` и `AstNode`, предоставленный `document_ast`.

Это означает:

- AST-парсер можно развивать отдельно от DSL;
- DSL executor ничего не знает о YAML-конфигах напрямую;
- единственная входная точка для выполнения запроса — уже построенное дерево документа.

С инженерной точки зрения это правильная зависимость:

```text
document_ast -> строит дерево
dsl          -> использует дерево
```

## Как DSL связан с actor runtime

DSL использует ту же actor-подсистему, что и `document_ast`.

Это даёт:

- одинаковую execution model;
- единый подход к состояниям;
- возможность использовать один и тот же driver style для разных подсистем.

Особенно полезно это в execution runtime DSL, где coordinator и worker-ы уже естественно выражают fan-out и fan-in.

## Что уже реализовано практически

Сейчас DSL уже умеет:

- разбирать запросы `FIND` и `CONTEXT`;
- строить внутренний AST запроса;
- выполнять запросы по реальному `AstDocument`;
- возвращать сериализуемый structured result;
- проходить автоматические тесты на разбор и execution.

То есть DSL-подсистема в проекте уже является работающим программным слоем, а не только формальной грамматикой.

## Связанные материалы

- [Описание DSL](./dsl_language.md)
- [Быстрый старт по DSL](./dsl_quickstart.md)
- [Архитектура AST-парсера](./ast_parser_architecture.md)
- [Файловая структура проекта](./project_structure.md)
