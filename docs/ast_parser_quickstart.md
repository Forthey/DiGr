# Быстрый старт по AST-парсеру

## Что делает парсер

Парсер из `src/document_ast`:

- читает документ
- определяет формат
- загружает `config/formats/<format>.yaml`
- строит AST по правилам этого формата

Результат возвращается как [AstDocument](/home/forthey/projects/DiGr/src/document_ast/ast_document.py).

## CLI

Точка входа находится в [main.py](/home/forthey/projects/DiGr/src/main.py).

Базовый запуск:

```bash
PYTHONPATH=src python3 src/main.py text.txt
```

По умолчанию:

- конфиги ищутся в `config/formats`
- формат определяется по расширению файла

Явное указание директории конфигов:

```bash
PYTHONPATH=src python3 src/main.py text.txt --config-dir config/formats
```

Явное указание формата:

```bash
PYTHONPATH=src python3 src/main.py text.txt --format txt
```

## Python API

Минимальный пример:

```python
from document_ast import ActorAstParser


parser = ActorAstParser.from_config_dir("config/formats")
document = parser.parse("text.txt")

print(document.format_name)
print(document.root_entity)
print(document.root.entity)
```

Если формат нужно задать явно:

```python
from document_ast import ActorAstParser


parser = ActorAstParser.from_config_dir("config/formats")
document = parser.parse("text.txt", format_name="txt")
```

## Что вернётся в результате

`AstDocument` содержит:

- `source_path`
- `format_name`
- `root_entity`
- `root`

`root` это [AstNode](/home/forthey/projects/DiGr/src/document_ast/ast_node.py) с полями:

- `entity`
- `text`
- `start`
- `end`
- `metadata`
- `children`

Сериализация в словарь:

```python
payload = document.to_dict()
```

## Как сейчас устроен разбор `txt`

Текущий [txt.yaml](/home/forthey/projects/DiGr/config/formats/txt.yaml) строит такую иерархию:

- `document`
- `page`
- `paragraph`
- `sentence`
- `clause`
- `word`

Для `text.txt` это означает:

- весь файл сначала рассматривается как одна `page`
- далее текст режется на `paragraph` по пустым строкам
- потом на `sentence`, `clause` и `word` по regex-правилам

## Как добавить новый формат

### Вариант 1. Достаточно plain text

Если источник можно читать как обычный текст:

1. создай `config/formats/<format>.yaml`
2. укажи `reader.kind: plain_text`
3. опиши `root_entity` и `entities`

### Вариант 2. Нужен отдельный reader

Если формат требует специального чтения:

1. создай реализацию [SourceReader](/home/forthey/projects/DiGr/src/document_ast/source_reader.py)
2. зарегистрируй её в [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source_reader_registry.py)
3. создай `config/formats/<format>.yaml`
4. укажи новый `reader.kind`

## Как это связано с actor-моделью

Внутри `ActorAstParser` создаётся runtime из четырёх акторов и [ManualActorDriver](/home/forthey/projects/DiGr/src/actor/drivers/manual_actor_driver.py). Это значит, что весь разбор выполняется как последовательность сообщений между стадиями пайплайна, а не как один монолитный метод.

Подробности:

- [Архитектура AST-парсера](./ast_parser_architecture.md)
- [Конфигурация AST-парсера](./ast_parser_configuration.md)
- [Архитектура акторов](./actor_architecture.md)
