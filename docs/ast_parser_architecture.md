# Архитектура AST-парсера

## Назначение подсистемы

Подсистема `src/document_ast` строит `AstDocument` поверх actor runtime из `src/actor`.

Её задача:

- прочитать исходный документ;
- выбрать конфигурацию формата;
- сегментировать текст на структурные сущности;
- собрать дерево `AstNode`;
- вернуть единый `AstDocument`.

Подсистема не знает заранее про конкретные сущности вроде `sentence` или `paragraph`. Эти сущности задаются конфигурацией формата.

Класс-диаграмма подсистемы находится в [ast_parser_architecture.puml](./uml/ast_parser_architecture.puml).

## Текущая структура пакета

После рефакторинга `document_ast` разбит на смысловые слои:

- `api`
- `model`
- `config`
- `source`
- `segmentation`
- `runtime`

Это делает архитектуру читаемой прямо по дереву файлов.

## Публичный API

Публичная точка входа:

- [ActorAstParser](/home/forthey/projects/DiGr/src/document_ast/api/document_parser.py)

Этот класс отвечает за:

- определение формата по расширению файла;
- загрузку `config/formats/<format>.yaml`;
- создание actor runtime;
- запуск пайплайна разбора;
- возврат `AstDocument`.

## Слой модели

Модель данных лежит в `src/document_ast/model`:

- [AstDocument](/home/forthey/projects/DiGr/src/document_ast/model/ast_document.py)
- [AstNode](/home/forthey/projects/DiGr/src/document_ast/model/ast_node.py)
- [SourceDocument](/home/forthey/projects/DiGr/src/document_ast/model/source_document.py)

Роли:

- `SourceDocument` представляет уже прочитанный источник;
- `AstNode` представляет узел дерева с диапазоном `start/end`;
- `AstDocument` представляет итоговое дерево вместе с метаданными документа.

## Слой конфигурации

Конфигурация живёт в `src/document_ast/config`:

- [ConfigLoader](/home/forthey/projects/DiGr/src/document_ast/config/config_loader.py)
- [ParserConfig](/home/forthey/projects/DiGr/src/document_ast/config/parser_config.py)
- [FormatConfig](/home/forthey/projects/DiGr/src/document_ast/config/format_config.py)
- [EntityConfig](/home/forthey/projects/DiGr/src/document_ast/config/entity_config.py)

Этот слой отвечает за:

- загрузку YAML;
- проверку структуры конфига;
- проверку существования `root_entity`;
- проверку ссылок `contains`;
- проверку отсутствия циклов.

Именно здесь формируется формальная модель документа.

## Слой чтения источника

Чтение исходного документа живёт в `src/document_ast/source`:

- [SourceReader](/home/forthey/projects/DiGr/src/document_ast/source/source_reader.py)
- [PlainTextReader](/home/forthey/projects/DiGr/src/document_ast/source/plain_text_reader.py)
- [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source/source_reader_registry.py)

Ключевая идея:

- AST-парсер не читает `txt`, `xml` или `json` напрямую;
- он работает с абстракцией `SourceDocument`;
- конкретный способ чтения выбирается через `reader.kind`.

Сейчас реально поддержан `plain_text`, но архитектура уже готова к новым reader-ам.

## Слой сегментации

Сегментация живёт в `src/document_ast/segmentation`:

- [TextSegment](/home/forthey/projects/DiGr/src/document_ast/segmentation/text_segment.py)
- [TextSegmenter](/home/forthey/projects/DiGr/src/document_ast/segmentation/text_segmenter.py)

`TextSegmenter` работает как реестр стратегий сегментации.

Поддержанные виды:

- `passthrough`
- `split`
- `match`

Это позволяет описывать структуру формата декларативно через YAML.

## Runtime-слой

Runtime живёт в `src/document_ast/runtime`.

Основные элементы:

- [AstBuilder](/home/forthey/projects/DiGr/src/document_ast/runtime/ast_builder.py)
- [messages.py](/home/forthey/projects/DiGr/src/document_ast/runtime/messages.py)
- [states.py](/home/forthey/projects/DiGr/src/document_ast/runtime/states.py)
- [pipeline_runtime.py](/home/forthey/projects/DiGr/src/document_ast/runtime/pipeline_runtime.py)
- `runtime/actors/*`

### `AstBuilder`

`AstBuilder` рекурсивно строит поддеревья по `ParserConfig`.

Он не знает доменные сущности заранее. Он работает только с:

- `root_entity`;
- `contains`;
- правилами сегментации.

### Runtime messages

В `messages.py` лежит протокол обмена сообщениями:

- `ParseDocumentRequest`
- `ReadDocumentRequest`
- `DocumentLoaded`
- `BuildSubtreeRequest`
- `SubtreeCompleted`
- `ParseCompleted`

### Runtime states

В `states.py` определены состояния:

- `CoordinatorState`
- `WorkerState`

Координатор использует фазовые состояния:

- `IDLE`
- `WAITING_FOR_DOCUMENT`
- `BUILDING_SUBTREES`
- `COMPLETED`

## Actor pipeline AST-парсера

В `src/document_ast/runtime/actors` находятся:

- [SourceReaderActor](/home/forthey/projects/DiGr/src/document_ast/runtime/actors/source_reader_actor.py)
- [ParseCoordinatorActor](/home/forthey/projects/DiGr/src/document_ast/runtime/actors/parse_coordinator_actor.py)
- [SubtreeBuilderWorkerActor](/home/forthey/projects/DiGr/src/document_ast/runtime/actors/subtree_builder_worker_actor.py)
- [ParseResultCollectorActor](/home/forthey/projects/DiGr/src/document_ast/runtime/actors/parse_result_collector_actor.py)

Для совместимости сохранены старые алиасы:

- `DocumentReaderActor`
- `ParserCoordinatorActor`
- `SubtreeWorkerActor`
- `ResultCollectorActor`

Но основными именами теперь являются именно более выразительные:

- `SourceReaderActor`
- `ParseCoordinatorActor`
- `SubtreeBuilderWorkerActor`
- `ParseResultCollectorActor`

## Роли акторов

### `SourceReaderActor`

Читает документ через `SourceReaderRegistry` и отдаёт `DocumentLoaded`.

### `ParseCoordinatorActor`

Управляет жизненным циклом разбора:

- принимает `ParseDocumentRequest`;
- запускает чтение документа;
- сегментирует верхний уровень;
- раздаёт задачи worker-ам;
- собирает поддеревья;
- формирует итоговый `AstDocument`.

### `SubtreeBuilderWorkerActor`

Строит поддерево для одного сегмента верхнего уровня через `AstBuilder.build_entity_node(...)`.

### `ParseResultCollectorActor`

Сохраняет финальный результат.

## Runtime factory

Runtime создаётся в [ParserRuntimeFactory](/home/forthey/projects/DiGr/src/document_ast/runtime/pipeline_runtime.py).

Фабрика:

- создаёт driver;
- создаёт coordinator;
- создаёт reader;
- создаёт пул worker-ов;
- создаёт collector;
- связывает их между собой через handle-ы.

Наружу выдаётся `ParserRuntime`, содержащий:

- `driver`;
- `coordinator`;
- `collector`.

Reader и worker-ы остаются внутренними деталями runtime.

## Как проходит разбор документа

Полный жизненный цикл:

1. `ActorAstParser.parse(...)` получает путь и формат;
2. грузится YAML-конфиг формата;
3. `ParserRuntimeFactory` создаёт runtime;
4. координатор получает `ParseDocumentRequest`;
5. `SourceReaderActor` читает документ;
6. координатор получает `DocumentLoaded`;
7. координатор выделяет сегменты верхнего уровня по `root_entity`;
8. для каждого сегмента отправляется `BuildSubtreeRequest`;
9. `SubtreeBuilderWorkerActor` строят поддеревья;
10. координатор получает `SubtreeCompleted`;
11. координатор собирает итоговое дерево;
12. collector получает `ParseCompleted`.

Это fan-out / fan-in pipeline:

- fan-out: coordinator -> workers;
- fan-in: workers -> coordinator.

## Почему эта архитектура полезна

Она даёт:

- отсутствие хардкода структур документа;
- разделение конфигурации и исполнения;
- возможность масштабировать worker-ов;
- естественное место для интеграции с DSL.

Главный результат этой подсистемы — не просто распарсенный текст, а дерево, по которому можно выполнять структурные запросы.

## Связанные материалы

- [Конфигурация AST-парсера](./ast_parser_configuration.md)
- [Быстрый старт по AST-парсеру](./ast_parser_quickstart.md)
- [Архитектура DSL](./dsl_architecture.md)
- [Файловая структура проекта](./project_structure.md)
