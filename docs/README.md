# Документация DiGr

## Как читать документацию

Если нужно быстро войти в проект, оптимальный порядок такой:

1. [Файловая структура проекта](./project_structure.md)
2. [Архитектура акторов](./actor_architecture.md)
3. [Архитектура AST-парсера](./ast_parser_architecture.md)
4. [Конфигурация AST-парсера](./ast_parser_configuration.md)
5. [Архитектура DSL](./dsl_architecture.md)
6. [Описание DSL](./dsl_language.md)
7. [DSL: расстояния и примеры на GA_1_2025.tex](./dsl_distance_functionality.md)
8. [Быстрый старт по DSL](./dsl_quickstart.md)

Такой порядок соответствует реальной зависимости подсистем:

- сначала базовый actor runtime;
- затем построение `AstDocument`;
- затем выполнение запросов DSL по уже построенному дереву.

## Акторная подсистема

- [Архитектура акторов](./actor_architecture.md)
- [Быстрый старт по акторам](./actor_quickstart.md)

## AST-парсер

- [Архитектура AST-парсера](./ast_parser_architecture.md)
- [Конфигурация AST-парсера](./ast_parser_configuration.md)
- [Быстрый старт по AST-парсеру](./ast_parser_quickstart.md)
- [Быстрый старт по формату tex](./tex_format_quickstart.md)

## DSL

- [Архитектура DSL](./dsl_architecture.md)
- [Описание DSL](./dsl_language.md)
- [DSL: расстояния и примеры на GA_1_2025.tex](./dsl_distance_functionality.md)
- [EBNF-грамматика DSL](./dsl_grammar.ebnf)
- [Быстрый старт по DSL](./dsl_quickstart.md)

## Навигация по репозиторию

- [Файловая структура проекта](./project_structure.md)

## UML-диаграммы

- [Class diagram actor runtime](./uml/actor_architecture.puml)
- [Class diagram AST-парсера](./uml/ast_parser_architecture.puml)
- [Sequence diagram AST-парсера](./uml/ast_parser_sequence.puml)
- [Fan-out / Fan-in sequence diagram AST-парсера](./uml/fanout_sequence.puml)
- [Class diagram DSL](./uml/dsl_architecture.puml)
- [Sequence diagram DSL](./uml/dsl_sequence.puml)
- [Компонентная диаграмма проекта](./uml/component_overview.puml)
- [Презентационный overview: TeX -> AST -> DSL](./uml/tex_pipeline_overview.puml)
- [Презентационная AST-модель формата tex](./uml/tex_ast_model.puml)
- [Презентационный sequence: разбор GA_1_2025.tex](./uml/tex_parsing_sequence.puml)
- [Презентационный sequence: DSL-поиск по TeX AST](./uml/tex_dsl_query_sequence.puml)

## Презентационный материал

- [Подробный рассказ о текущем состоянии проекта](../present.md)
