# Документация

## Акторная архитектура

- [Архитектура акторов](./actor_architecture.md): устройство базовой actor-подсистемы, контракты, драйверы и модель исполнения
- [Быстрый старт по акторам](./actor_quickstart.md): минимальные примеры `Actor`, `ActorHandle` и разных драйверов

## AST-парсер

- [Архитектура AST-парсера](./ast_parser_architecture.md): устройство подсистемы `document_ast`, роли классов и жизненный цикл разбора
- [Конфигурация AST-парсера](./ast_parser_configuration.md): полная схема `<format>.yaml`, правила валидации и подробный разбор `txt.yaml`
- [Быстрый старт по AST-парсеру](./ast_parser_quickstart.md): запуск через CLI и Python API, а также расширение на новые форматы

## UML

- [Полная UML-диаграмма actor-архитектуры](./uml/actor_architecture.puml)
- [Компактная UML-диаграмма actor-архитектуры](./uml/actor_architecture_min.puml)
- [UML class diagram AST-парсера](./uml/ast_parser_architecture.puml)
- [UML sequence diagram AST-парсера](./uml/ast_parser_sequence.puml)
- [Компонентная диаграмма проекта](./uml/component_overview.puml)
- [Диаграмма состояний координатора AST-парсера](./uml/coordinator_state_machine.puml)
- [Fan-out / Fan-in sequence diagram AST-парсера](./uml/fanout_sequence.puml)

## Как читать документацию

Если нужно понять основу actor-модели, сначала стоит прочитать [Архитектуру акторов](./actor_architecture.md). Если задача связана именно с разбором документов в AST, лучше начать с [Архитектуры AST-парсера](./ast_parser_architecture.md), а затем перейти к [Конфигурации AST-парсера](./ast_parser_configuration.md), потому что структура разбора определяется именно YAML-конфигом формата.
