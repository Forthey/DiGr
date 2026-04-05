# Архитектура AST-парсера

## Назначение

Подсистема `src/document_ast` строит AST документа поверх actor-архитектуры из `src/actor`.

Её задача разделена на две независимые части:

- конфигурация формата описывает, какие сущности есть в документе и как они выделяются из текста
- actor-пайплайн исполняет разбор как последовательность сообщений между специализированными акторами

Из этого следует важный принцип: код парсера не знает заранее про `word`, `sentence`, `paragraph`, `page` или любые другие сущности. Он знает только про:

- формат
- корневую сущность
- иерархию `contains`
- правила сегментации, заданные в YAML

## Основные слои

### 1. Публичный API

Точка входа в подсистему это [ActorAstParser](/home/forthey/projects/DiGr/src/document_ast/actor_ast_parser.py).

Он отвечает за:

- определение формата по расширению файла, если формат не передан явно
- загрузку `config/formats/<format>.yaml`
- создание runtime с акторами
- запуск разбора и возврат готового `AstDocument`

### 2. Конфигурация формата

Конфигурация описывается следующими объектами:

- [ConfigLoader](/home/forthey/projects/DiGr/src/document_ast/config_loader.py)
- [ParserConfig](/home/forthey/projects/DiGr/src/document_ast/parser_config.py)
- [FormatConfig](/home/forthey/projects/DiGr/src/document_ast/format_config.py)
- [EntityConfig](/home/forthey/projects/DiGr/src/document_ast/entity_config.py)

Эта часть отвечает за:

- загрузку YAML
- проверку структуры конфига
- проверку существования `root_entity`
- проверку ссылок `contains`
- проверку отсутствия циклов в иерархии сущностей

Именно здесь формируется формальная модель разбора документа.

### 3. Чтение исходного документа

Подсистема чтения источника состоит из:

- [SourceReader](/home/forthey/projects/DiGr/src/document_ast/source_reader.py): абстрактный интерфейс чтения
- [PlainTextReader](/home/forthey/projects/DiGr/src/document_ast/plain_text_reader.py): текущая реализация для plain text
- [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source_reader_registry.py): выбор reader по `reader.kind`
- [SourceDocument](/home/forthey/projects/DiGr/src/document_ast/source_document.py): нормализованное представление исходного документа

Важная идея здесь такая: AST-построитель работает не с `txt` напрямую, а с `SourceDocument`. Поэтому для поддержки `json`, `xml`, `docx` или другого формата нужно:

1. добавить новый `SourceReader`
2. зарегистрировать его в [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source_reader_registry.py)
3. описать формат в отдельном `<format>.yaml`

### 4. Сегментация и построение AST

Слой сегментации и построения включает:

- [TextSegmenter](/home/forthey/projects/DiGr/src/document_ast/text_segmenter.py)
- [TextSegment](/home/forthey/projects/DiGr/src/document_ast/text_segment.py)
- [AstBuilder](/home/forthey/projects/DiGr/src/document_ast/ast_builder.py)
- [AstNode](/home/forthey/projects/DiGr/src/document_ast/ast_node.py)
- [AstDocument](/home/forthey/projects/DiGr/src/document_ast/ast_document.py)

Распределение ответственности следующее:

- `TextSegmenter` реализует примитивы сегментации `passthrough`, `split`, `match`
- `AstBuilder` рекурсивно проходит по иерархии `root_entity -> contains -> contains -> ...`
- `AstNode` хранит узел дерева вместе с диапазоном `start/end`
- `AstDocument` хранит корень AST и метаданные результата

`AstBuilder` не содержит хардкода предметных сущностей. Он просто берёт очередную сущность из `ParserConfig`, сегментирует текст по её правилам и, если указано `contains`, рекурсивно строит дочерние узлы.

### 5. Actor-runtime

Исполнение построено через четыре специализированных актора:

- [ParserCoordinatorActor](/home/forthey/projects/DiGr/src/document_ast/actors/parser_coordinator_actor.py)
- [DocumentReaderActor](/home/forthey/projects/DiGr/src/document_ast/actors/document_reader_actor.py)
- [AstBuilderActor](/home/forthey/projects/DiGr/src/document_ast/actors/ast_builder_actor.py)
- [ResultCollectorActor](/home/forthey/projects/DiGr/src/document_ast/actors/result_collector_actor.py)

Runtime создаётся в [ParserRuntimeFactory](/home/forthey/projects/DiGr/src/document_ast/runtime.py) и сейчас использует [ManualActorDriver](/home/forthey/projects/DiGr/src/actor/drivers/manual_actor_driver.py) со `step_limit=1`.

Роли акторов:

- `ParserCoordinatorActor` управляет жизненным циклом разбора
- `DocumentReaderActor` читает исходный документ через registry
- `AstBuilderActor` превращает `SourceDocument` в `AstDocument`
- `ResultCollectorActor` сохраняет итоговый результат

## Жизненный цикл разбора

Полный разбор одного документа выглядит так:

1. `ActorAstParser.parse()` получает путь и определяет `format_name`
2. Загружается `config/formats/<format>.yaml`
3. `ParserRuntimeFactory` создаёт driver и акторы
4. В `ParserCoordinatorActor` отправляется `ParseDocumentRequest`
5. `ManualActorDriver.drain()` начинает по одному шагу выполнять runnable-акторов
6. `ParserCoordinatorActor` отправляет `ReadDocumentRequest` в `DocumentReaderActor`
7. `DocumentReaderActor` читает источник и возвращает `DocumentLoaded`
8. `ParserCoordinatorActor` отправляет `BuildAstRequest` в `AstBuilderActor`
9. `AstBuilderActor` вызывает `AstBuilder.build()` и получает `AstDocument`
10. `AstBuilderActor` отправляет `ParseCompleted`
11. `ParserCoordinatorActor` пересылает результат в `ResultCollectorActor`
12. `ActorAstParser` забирает `collector.result` и возвращает `AstDocument`

Это означает, что actor-модель здесь используется не как украшение, а как явный execution model для стадий разбора.

## Как AST-парсер использует actor-архитектуру

AST-подсистема опирается только на несколько базовых сущностей actor-слоя:

- [Actor](/home/forthey/projects/DiGr/src/actor/arch/actor.py): базовый класс всех AST-акторов
- [ActorHandle](/home/forthey/projects/DiGr/src/actor/handles/actor_handle.py): передача сообщений между акторами без прямой зависимости на объект актора
- [ManualActorDriver](/home/forthey/projects/DiGr/src/actor/drivers/manual_actor_driver.py): детерминированное исполнение пайплайна

Это даёт два полезных свойства:

- прикладная логика разбора отделена от механики планирования и mailbox
- тот же пайплайн можно в будущем запускать на другом драйвере, если это понадобится

## Расширяемость

### Добавление нового формата без нового reader

Если новый формат уже может быть представлен как plain text, достаточно:

1. создать `config/formats/<format>.yaml`
2. указать `reader.kind: plain_text`
3. описать сущности и сегментацию

### Добавление нового формата с новым reader

Если формат требует отдельного извлечения текста или структуры:

1. реализовать новый класс, наследующий [SourceReader](/home/forthey/projects/DiGr/src/document_ast/source_reader.py)
2. зарегистрировать его в [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source_reader_registry.py)
3. создать `config/formats/<format>.yaml`
4. указать нужный `reader.kind`

### Добавление новой иерархии сущностей

Для этого не нужно менять `AstBuilder`. Достаточно:

1. описать новую цепочку `root_entity -> contains`
2. для каждой сущности задать `segmenter`

## Формальная UML-модель

Для AST-подсистемы подготовлены две UML-диаграммы:

- [ast_parser_architecture.puml](/home/forthey/projects/DiGr/docs/uml/ast_parser_architecture.puml): class diagram структуры подсистемы
- [ast_parser_sequence.puml](/home/forthey/projects/DiGr/docs/uml/ast_parser_sequence.puml): sequence diagram процесса разбора

При построении диаграмм соблюдены следующие правила моделирования:

- имена классов и enum совпадают с кодом
- внешние зависимости на actor-подсистему выделены в отдельный пакет
- композиция используется только там, где владение зафиксировано в коде
- generic-параметры не кодируются в имени класса, чтобы не ломать рендеринг PlantUML и не смешивать идентификатор типа с шаблонной спецификацией
- последовательность сообщений показана отдельно sequence diagram, а не смешана с class diagram

## Связанные материалы

- [Архитектура акторов](./actor_architecture.md)
- [Конфигурация AST-парсера](./ast_parser_configuration.md)
- [Быстрый старт по AST-парсеру](./ast_parser_quickstart.md)
