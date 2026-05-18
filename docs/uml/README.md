# Каталог UML-диаграмм DiGr

Этот документ — навигация по всему набору диаграмм проекта. Диаграммы разложены
по подкаталогам соответственно типу формализма UML (или родственного нотационного
языка). В конце есть отдельный раздел [«Новые диаграммы»](#новые-диаграммы)
со ссылками только на свежедобавленные артефакты.

## Рендер `.puml` → `.png`

В проекте используется VS Code расширение **[jebbs.plantuml](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)**
(установлено: `jebbs.plantuml-2.18.1`). Это предпочтительный способ рендера — он
понимает все `skinparam` и работает офлайн через локальный `plantuml.jar`.

- Превью текущего файла: `Alt+D` (открывает live-preview сбоку).
- Экспорт текущего файла в PNG: палитра `Ctrl+Shift+P` → **PlantUML: Export Current
  Diagram** → выбрать `png`. Файл сохраняется рядом с `.puml`.
- Экспорт всего каталога: **PlantUML: Export Workspace Diagrams** → `png`. По
  настройке `plantuml.exportSubFolder` (по умолчанию `true`) PNG могут попасть
  во вложенный каталог `out/`; для рядом-лежащих файлов в `settings.json` стоит
  поставить `"plantuml.exportSubFolder": false`.
- Формат и имя выходного файла настраиваются `plantuml.exportFormat` и
  `plantuml.exportOutDir`. Для railroad-схемы DSL см. отдельные инструкции в
  [`grammar/dsl-grammar-railroad.md`](./grammar/dsl-grammar-railroad.md) — она
  не PlantUML и рендерится другими средствами.

## Типы диаграмм в проекте

| Тип | Каталог | Назначение |
|---|---|---|
| Class | `class/` | Структурные отношения между классами/типами без поведения. |
| Component | `component/` | Подсистемы и устойчивые зависимости между ними. |
| Sequence | `sequence/` | Временной порядок взаимодействий между ролями/объектами. |
| State machine | `state/` | Состояния и переходы конкретного FSM. |
| Activity | `activity/` | Логические потоки управления и параллелизма, без объектов и сообщений. |
| Object | `object/` | Снимок инстансов для конкретного примера (комплементарно class). |
| Package | `package/` | Зависимости между Python-пакетами/модулями. |
| Deployment | `deployment/` | Узлы исполнения и артефакты, размещённые на них. |
| Use case | `usecase/` | Внешняя функциональность и роли пользователей. |
| Communication | `communication/` | Структурная сторона обмена сообщениями (альтернатива sequence). |
| Timing | `timing/` | Состояния lifeline-объектов во времени. |
| Grammar (railroad) | `grammar/` | Формализованная грамматика DSL (не UML, но строгая нотация). |

## Принципы формализации

1. **Одна ответственность — одна диаграмма.** Class diagram не содержит lifeline
   и сообщений; sequence не показывает наследование (`<|--`, `*--`);
   state diagram не содержит классов и объектов; activity не содержит сообщений
   между ролями.
2. **Тип задаётся каталогом**, а не префиксом имени файла. Имена файлов —
   `kebab-case` или snake-case (для уже существующих).
3. **Единые `skinparam`:** `shadowing false`, `hide empty members` для class,
   `linetype ortho` для крупных class. На каждой диаграмме — заголовок (`title`)
   и завершающая `note` с пояснением области и ссылками на смежные диаграммы.
4. **State machines** содержат явные `[*]` начальное и конечное состояния и
   гварды через `[guard]`.
5. **Activity** использует `:action;` и `if/else/fork` строго по UML2;
   participant'ов и messages не использует.
6. **Object diagrams** именуют инстансы как `name:Class` и приводят минимально
   необходимые поля.
7. **Каждая диаграмма указывает источник** (файл из `src/...`), на основе
   которого она построена.

## Карта связей между диаграммами

- `class/ast_parser_architecture.puml` + `class/format-config.puml` + `sequence/config-loading.puml` — структура и загрузка парсера AST.
- `class/ast-model.puml` ↔ `object/ast-tex-snapshot.puml` — модель AST и пример инстансов.
- `class/query-ast.puml` ↔ `object/query-ast-snapshot.puml` ↔ `grammar/dsl-grammar-railroad` — AST DSL, пример инстансов и грамматика.
- `class/actor_architecture.puml` + `class/actor-drivers.puml` + `state/ready-actors.puml` + `state/fsm-actor-lifecycle.puml` + `sequence/actor-driver-scheduling.puml` + `timing/actor-scheduling-timing.puml` — actor runtime в разных проекциях.
- `class/dsl_architecture.puml` + `class/dsl-execution-semantics.puml` + `class/lexer-tokens.puml` + state-машины + sequence DSL — DSL-подсистема.
- `sequence/fanout_sequence.puml` ↔ `communication/fanout-collaboration.puml` — fan-out, временной vs. структурный взгляд.
- `activity/dsl-pipeline.puml` ↔ `sequence/dsl-engine-end-to-end.puml` — логический и фасадный взгляды на запрос.

---

## Class diagrams (`class/`)

| Файл | Описание |
|---|---|
| [actor_architecture.puml](./class/actor_architecture.puml) ([png](./class/actor_architecture.png)) | Actor runtime целиком: Fsm, Actor, Mailbox, Driver, ReadyActors. |
| [ast_parser_architecture.puml](./class/ast_parser_architecture.puml) ([png](./class/ast_parser_architecture.png)) | Парсер AST + связь с конфигурацией формата. |
| [dsl_architecture.puml](./class/dsl_architecture.puml) ([png](./class/dsl_architecture.png)) | DSL-подсистема: модель запроса, парсер, executor, акторы. |
| [tex_ast_model.puml](./class/tex_ast_model.puml) ([png](./class/tex_ast_model.png)) | Презентационная иерархия TeX-entities. |
| [ast-model.puml](./class/ast-model.puml) | Только модель данных AST: SourceDocument, AstNode, AstDocument, TextSegment. |
| [query-ast.puml](./class/query-ast.puml) | Только модель DSL-запроса (`src/dsl/model/query_ast.py`). |
| [format-config.puml](./class/format-config.puml) | Классы конфигурации форматов: ConfigLoader, ParserConfig, FormatConfig, EntityConfig. |
| [dsl-execution-semantics.puml](./class/dsl-execution-semantics.puml) | Только семантика выполнения: DocumentIndex, PredicateEvaluator, QueryValidator, DistanceCalculator, результирующие dataclass'ы. |
| [lexer-tokens.puml](./class/lexer-tokens.puml) | Синхронные классы лексера и парсера DSL: DslToken, TokenKind, Lexer, RecursiveDescentParser. |
| [actor-drivers.puml](./class/actor-drivers.puml) | Иерархия драйверов: ActorDriver, BaseActorDriver, ProceedableActorDriver, Asyncio/Threaded/Manual. |

## Component diagrams (`component/`)

| Файл | Описание |
|---|---|
| [component_overview.puml](./component/component_overview.puml) ([png](./component/component_overview.png)) | Подсистемы DiGr и устойчивые зависимости между ними. |
| [tex_pipeline_overview.puml](./component/tex_pipeline_overview.puml) ([png](./component/tex_pipeline_overview.png)) | Презентационный overview: TeX → AST → DSL. |

## Sequence diagrams (`sequence/`)

| Файл | Описание |
|---|---|
| [ast_parser_sequence.puml](./sequence/ast_parser_sequence.puml) ([png](./sequence/ast_parser_sequence.png)) | Общий поток парсинга документа. |
| [fanout_sequence.puml](./sequence/fanout_sequence.puml) ([png](./sequence/fanout_sequence.png)) | Fan-out/fan-in subtree-воркеров. |
| [dsl_sequence.puml](./sequence/dsl_sequence.puml) ([png](./sequence/dsl_sequence.png)) | Сквозной поток DSL. |
| [dsl_parser_sequence.puml](./sequence/dsl_parser_sequence.puml) ([png](./sequence/dsl_parser_sequence.png)) | Парсинг DSL-запроса (внутри parser-runtime). |
| [dsl_executor_sequence.puml](./sequence/dsl_executor_sequence.puml) ([png](./sequence/dsl_executor_sequence.png)) | Выполнение DSL-запроса (внутри execution-runtime). |
| [tex_parsing_sequence.puml](./sequence/tex_parsing_sequence.puml) ([png](./sequence/tex_parsing_sequence.png)) | Парсинг GA_1_2025.tex. |
| [tex_dsl_query_sequence.puml](./sequence/tex_dsl_query_sequence.puml) ([png](./sequence/tex_dsl_query_sequence.png)) | DSL-запрос по TeX AST. |
| [actor-driver-scheduling.puml](./sequence/actor-driver-scheduling.puml) | Один шаг планирования BaseActorDriver: Actor ↔ Mailbox ↔ Driver ↔ ReadyActors ↔ Worker. |
| [config-loading.puml](./sequence/config-loading.puml) | Загрузка YAML-конфига: ConfigLoader → FormatConfig/EntityConfig → ParserConfig. |
| [dsl-engine-end-to-end.puml](./sequence/dsl-engine-end-to-end.puml) | Фасадный уровень `ActorDslEngine.execute`: Parser → Executor. |

## State machine diagrams (`state/`)

| Файл | Описание |
|---|---|
| [ready-actors.puml](./state/ready-actors.puml) | FSM записи актора в ReadyActors: scheduled → ready → inflight → (scheduled\|terminal). |
| [fsm-actor-lifecycle.puml](./state/fsm-actor-lifecycle.puml) | Жизненный цикл `Fsm.step(limit)`: Idle / Handling / Unhandled / Terminated. |
| [ast-coordinator.puml](./state/ast-coordinator.puml) | FSM ParseCoordinatorActor: IDLE → WAITING_FOR_DOCUMENT → BUILDING_SUBTREES → COMPLETED. |
| [dsl-parser-coordinator.puml](./state/dsl-parser-coordinator.puml) | FSM DSL ParserCoordinator: IDLE → WAITING_FOR_TOKENS → WAITING_FOR_QUERY_AST → COMPLETED. |
| [dsl-query-parser.puml](./state/dsl-query-parser.puml) | Многошаговый FSM QueryParserActor с Continue*-self-transitions. |
| [dsl-execution-coordinator.puml](./state/dsl-execution-coordinator.puml) | FSM DslExecutionCoordinator: IDLE → EVALUATING_FIND_CANDIDATES → EVALUATING_CONTEXT_WINDOWS → COMPLETED. |

## Activity diagrams (`activity/`)

| Файл | Описание |
|---|---|
| [ast-build-flow.puml](./activity/ast-build-flow.puml) | Логический поток построения AstDocument (read source → segment → fan-out → assemble). |
| [dsl-pipeline.puml](./activity/dsl-pipeline.puml) | Логический пайплайн DSL: lex → parse → validate → execute → results. |
| [cli-entrypoint.puml](./activity/cli-entrypoint.puml) | Поток `src/main.py`: batch и интерактивный режимы. |
| [distance-calculation.puml](./activity/distance-calculation.puml) | Алгоритм `DistanceCalculator.calculate_pairs`. |

## Object diagrams (`object/`)

| Файл | Описание |
|---|---|
| [ast-tex-snapshot.puml](./object/ast-tex-snapshot.puml) | Снимок инстансов AstNode для фрагмента GA_1_2025.tex. |
| [query-ast-snapshot.puml](./object/query-ast-snapshot.puml) | Снимок инстансов DslQuery для distance-запроса. |

## Package diagram (`package/`)

| Файл | Описание |
|---|---|
| [module-dependencies.puml](./package/module-dependencies.puml) | Зависимости Python-пакетов `actor` ← `document_ast` ← `dsl` ← `main`. |

## Deployment diagram (`deployment/`)

| Файл | Описание |
|---|---|
| [runtime-deployment.puml](./deployment/runtime-deployment.puml) | Три execution environment'а драйверов (asyncio, threaded, manual) и внешние артефакты. |

## Use case diagram (`usecase/`)

| Файл | Описание |
|---|---|
| [digr-use-cases.puml](./usecase/digr-use-cases.puml) | Use cases для CLI-пользователя, автора формата, разработчика. |

## Communication diagrams (`communication/`)

| Файл | Описание |
|---|---|
| [fanout-collaboration.puml](./communication/fanout-collaboration.puml) | Структурный взгляд на fan-out при построении AST (нумерованные сообщения). |

## Timing diagrams (`timing/`)

| Файл | Описание |
|---|---|
| [actor-scheduling-timing.puml](./timing/actor-scheduling-timing.puml) | Состояния `Driver / Coordinator / Worker_A / Worker_B` во времени; cooperative scheduling. |

## Grammar / Railroad (`grammar/`)

| Файл | Описание |
|---|---|
| [dsl-grammar-railroad.md](./grammar/dsl-grammar-railroad.md) | Текстовое представление railroad-диаграммы DSL + инструкции для рендера SVG. |
| [dsl-grammar-railroad.html](./grammar/dsl-grammar-railroad.html) | Интерактивный railroad через `railroad-diagrams.js` (открыть в браузере). |

---

## Новые диаграммы

Этот раздел дублирует ссылки на артефакты, добавленные в рамках расширения набора —
полезно для демонстрации на защите.

### State machine (`state/`)
1. [ready-actors.puml](./state/ready-actors.puml) — *state machine*: позиция актора в ReadyActors.
2. [fsm-actor-lifecycle.puml](./state/fsm-actor-lifecycle.puml) — *state machine*: шаг Fsm.step.
3. [ast-coordinator.puml](./state/ast-coordinator.puml) — *state machine*: ParseCoordinatorActor.
4. [dsl-parser-coordinator.puml](./state/dsl-parser-coordinator.puml) — *state machine*: DSL ParserCoordinator.
5. [dsl-query-parser.puml](./state/dsl-query-parser.puml) — *state machine*: QueryParserActor (многошаговый).
6. [dsl-execution-coordinator.puml](./state/dsl-execution-coordinator.puml) — *state machine*: DslExecutionCoordinator.

### Activity (`activity/`)
7. [ast-build-flow.puml](./activity/ast-build-flow.puml) — *activity*: построение AstDocument.
8. [dsl-pipeline.puml](./activity/dsl-pipeline.puml) — *activity*: логический пайплайн DSL.
9. [cli-entrypoint.puml](./activity/cli-entrypoint.puml) — *activity*: поток `main.py`.
10. [distance-calculation.puml](./activity/distance-calculation.puml) — *activity*: DistanceCalculator.

### Class — узкие срезы (`class/`)
11. [ast-model.puml](./class/ast-model.puml) — *class*: модель AST.
12. [query-ast.puml](./class/query-ast.puml) — *class*: модель DSL-запроса.
13. [format-config.puml](./class/format-config.puml) — *class*: конфигурация форматов.
14. [dsl-execution-semantics.puml](./class/dsl-execution-semantics.puml) — *class*: семантика выполнения DSL.
15. [lexer-tokens.puml](./class/lexer-tokens.puml) — *class*: синхронный лексер и парсер DSL.
16. [actor-drivers.puml](./class/actor-drivers.puml) — *class*: иерархия драйверов.

### Object (`object/`)
17. [ast-tex-snapshot.puml](./object/ast-tex-snapshot.puml) — *object*: инстансы AstNode для GA_1_2025.tex.
18. [query-ast-snapshot.puml](./object/query-ast-snapshot.puml) — *object*: инстансы DslQuery для distance-запроса.

### Package (`package/`)
19. [module-dependencies.puml](./package/module-dependencies.puml) — *package*: зависимости Python-пакетов.

### Deployment (`deployment/`)
20. [runtime-deployment.puml](./deployment/runtime-deployment.puml) — *deployment*: три execution environment'а драйверов.

### Use case (`usecase/`)
21. [digr-use-cases.puml](./usecase/digr-use-cases.puml) — *use case*: внешняя функциональность DiGr.

### Sequence — дополнительные (`sequence/`)
22. [actor-driver-scheduling.puml](./sequence/actor-driver-scheduling.puml) — *sequence*: один шаг scheduling'а.
23. [config-loading.puml](./sequence/config-loading.puml) — *sequence*: загрузка YAML-конфига.
24. [dsl-engine-end-to-end.puml](./sequence/dsl-engine-end-to-end.puml) — *sequence*: фасад ActorDslEngine.

### Communication (`communication/`)
25. [fanout-collaboration.puml](./communication/fanout-collaboration.puml) — *communication*: fan-out при построении AST.

### Timing (`timing/`)
26. [actor-scheduling-timing.puml](./timing/actor-scheduling-timing.puml) — *timing*: cooperative scheduling.

### Grammar / Railroad (`grammar/`)
27. [dsl-grammar-railroad.md](./grammar/dsl-grammar-railroad.md) + [.html](./grammar/dsl-grammar-railroad.html) — *railroad*: грамматика DSL.
