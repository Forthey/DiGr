# Файловая структура проекта

## Назначение документа

Этот документ описывает репозиторий как карту ответственности:

- где находится инфраструктура;
- где строится `AstDocument`;
- где реализован DSL;
- какие каталоги являются публичными точками входа;
- какие каталоги являются внутренней реализацией.

## Верхний уровень репозитория

```text
DiGr/
├── config/
│   └── formats/
├── docs/
│   └── uml/
├── src/
│   ├── actor/
│   ├── document_ast/
│   └── dsl/
├── tests/
├── text.txt
├── examples_dsl.md
├── pre_tz.md
└── present.md
```

Смысл верхнего уровня:

- `config/` хранит внешние описания форматов документов;
- `docs/` хранит инженерную документацию и UML;
- `src/` содержит весь исполняемый код;
- `tests/` содержит проверки синтаксиса и выполнения DSL;
- `text.txt` это локальный пример документа;
- `examples_dsl.md` и `pre_tz.md` фиксируют постановку задачи и примеры запросов;
- `present.md` содержит развёрнутый текст для презентации прогресса.

## `config/`

`config/` содержит не код, а модель форматов.

Сейчас используется директория:

```text
config/
└── formats/
    └── txt.yaml
```

В каждом `<format>.yaml` задаётся:

- имя формата;
- reader, который умеет превратить файл в `SourceDocument`;
- корневая сущность прикладного дерева;
- список сущностей и правила сегментации;
- отношение вложения `contains`.

Именно здесь описывается структура документа, а не в Python-коде.

## `docs/`

`docs/` содержит три типа материалов:

- архитектурные описания;
- quickstart-руководства;
- UML-диаграммы в `docs/uml/`.

Принцип простой: markdown объясняет систему словами, а `.puml` фиксируют её структуру графически. Оба слоя документации должны соответствовать текущему коду.

## `src/`

`src/` разделён на три основные подсистемы:

```text
src/
├── actor/
├── document_ast/
└── dsl/
```

Их зависимость однонаправленная:

```text
actor        -> инфраструктура исполнения
document_ast -> строит AstDocument поверх actor
dsl          -> выполняет запросы поверх AstDocument и actor
```

## `src/actor/`

`src/actor/` это базовый actor runtime проекта.

Структура:

```text
src/actor/
├── arch/
├── drivers/
├── handles/
└── output/
```

Роли:

- `arch/` содержит базовые контракты и общую логику актора;
- `drivers/` содержит способы исполнения и планирования;
- `handles/` содержит безопасные ссылки для отправки сообщений;
- `output/` содержит минимальный протокол доставки сообщений.

Этот пакет не знает ничего про документы, AST или DSL. Он является общей инфраструктурой.

## `src/document_ast/`

`src/document_ast/` отвечает за построение `AstDocument`.

Структура пакета:

```text
src/document_ast/
├── api/
├── config/
├── model/
├── segmentation/
├── source/
└── runtime/
    └── actors/
```

### `src/document_ast/api/`

Публичная точка входа подсистемы:

- `document_parser.py` с классом `ActorAstParser`

Этот слой нужен для того, чтобы внешний код не зависел напрямую от внутреннего actor pipeline.

### `src/document_ast/model/`

Модель данных AST:

- `ast_document.py`
- `ast_node.py`
- `source_document.py`

Здесь находятся структуры, которые используются и внутри рантайма, и извне:

- `SourceDocument` для прочитанного источника;
- `AstNode` для одного узла дерева;
- `AstDocument` для результата разбора целого документа.

### `src/document_ast/config/`

Слой конфигурации форматов:

- `config_loader.py`
- `parser_config.py`
- `format_config.py`
- `entity_config.py`

Этот пакет отвечает за:

- загрузку YAML;
- структурную валидацию;
- проверку `root_entity`;
- проверку ссылок `contains`;
- обнаружение циклов в иерархии сущностей.

### `src/document_ast/source/`

Чтение исходных файлов:

- `source_reader.py`
- `plain_text_reader.py`
- `source_reader_registry.py`

Именно этот слой отделяет прикладной AST-пайплайн от формата хранения документа на диске.

### `src/document_ast/segmentation/`

Выделение сегментов из текста:

- `text_segment.py`
- `text_segmenter.py`

Этот слой реализует стратегии сегментации, используемые конфигом формата:

- `passthrough`
- `split`
- `match`

### `src/document_ast/runtime/`

Внутренний actor runtime AST-парсера:

```text
src/document_ast/runtime/
├── ast_builder.py
├── messages.py
├── pipeline_runtime.py
├── states.py
└── actors/
    ├── parse_coordinator_actor.py
    ├── parse_result_collector_actor.py
    ├── source_reader_actor.py
    └── subtree_builder_worker_actor.py
```

Назначение этого слоя:

- собрать runtime из акторов и драйвера;
- описать протокол обмена сообщениями;
- реализовать fan-out/fan-in разбор документа.

`runtime/actors/` содержит именно внутреннюю механику исполнения, а не внешний API.

## `src/dsl/`

`src/dsl/` отвечает за два шага:

- разобрать текст запроса в AST языка;
- выполнить этот AST по `AstDocument`.

Структура пакета:

```text
src/dsl/
├── api/
├── model/
├── parsing/
├── execution/
└── actors/
    ├── parsing/
    └── execution/
```

### `src/dsl/api/`

Публичные точки входа DSL:

- `query_parser.py` с `ActorDslParser`
- `query_executor.py` с `ActorDslExecutor`
- `engine.py` с `ActorDslEngine`

Это слой, которым должен пользоваться внешний код.

### `src/dsl/model/`

AST самого языка:

- `query_ast.py`

Здесь находятся классы вроде:

- `FindQuery`
- `ContextQuery`
- `Selector`
- `Pattern`
- `ComparisonExpression`
- `FunctionExpression`

### `src/dsl/parsing/`

Синтаксический разбор DSL:

- `lexer.py`
- `token.py`
- `token_kind.py`
- `recursive_descent_parser.py`
- `errors.py`
- `messages.py`
- `states.py`
- `runtime.py`

Этот слой ничего не знает о `AstDocument`. Его задача только одна: превратить текст запроса в `DslQuery`.

### `src/dsl/execution/`

Семантика исполнения DSL:

- `document_index.py`
- `predicate_evaluator.py`
- `query_validator.py`
- `query_results.py`
- `messages.py`
- `states.py`
- `runtime.py`

Этот слой уже знает про `AstDocument` и `AstNode`, потому что выполняет запрос по дереву документа.

### `src/dsl/actors/`

Внутренние actor pipeline DSL разделены на две поддиректории:

```text
src/dsl/actors/
├── execution/
└── parsing/
```

Это сделано специально, чтобы не смешивать:

- акторов синтаксического разбора DSL;
- акторов выполнения DSL по документу.

## `tests/`

`tests/` содержит автоматические проверки.

Сейчас основные тесты сосредоточены вокруг:

- парсинга DSL;
- выполнения DSL поверх реального `AstDocument`.

Для этого проекта это критично, потому что корректность зависит сразу от трёх слоёв:

- конфигурации формата;
- структуры AST;
- семантики DSL.

## Как быстро находить нужный код

Практическое правило навигации:

- нужен внешний интерфейс — искать в `api/`;
- нужна структура данных — искать в `model/`;
- нужна конфигурация формата — искать в `config/`;
- нужно чтение файлов — искать в `source/`;
- нужна сегментация текста — искать в `segmentation/`;
- нужен runtime AST-парсера — искать в `document_ast/runtime/`;
- нужен синтаксис DSL — искать в `dsl/parsing/`;
- нужна семантика DSL — искать в `dsl/execution/`;
- нужны акторы DSL — искать в `dsl/actors/`.

## Почему структура сделана глубже

Более глубокая структура здесь не косметическая, а инженерная.

Она:

- отделяет публичный API от внутренней реализации;
- делает зависимости слоёв видимыми прямо по пути к файлу;
- снижает шум в корне пакетов;
- упрощает навигацию после роста подсистемы;
- уменьшает риск смешать семантику DSL, runtime и модель данных.
