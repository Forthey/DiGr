# Быстрый старт по DSL

## Что уже умеет подсистема DSL

Текущая реализация DSL умеет:

- разобрать текст запроса;
- построить `DslQuery`;
- выполнить этот запрос по `AstDocument`;
- вернуть structured result.

В проекте для этого есть три публичных класса:

- `ActorDslParser`
- `ActorDslExecutor`
- `ActorDslEngine`

## Полный сценарий

Самый удобный путь сейчас такой:

1. построить `AstDocument` через `document_ast`;
2. выполнить DSL-запрос через `ActorDslEngine`.

Пример:

```python
from document_ast import ActorAstParser
from dsl import ActorDslEngine


document = ActorAstParser.from_config_dir("config/formats").parse("text.txt", format_name="txt")
engine = ActorDslEngine()

result = engine.execute(
    document,
    """
    FIND sentence
    WHERE has_descendant(word[text ~= /телефон/i])
    RETURN text, count
    """.strip(),
)

print(result.to_dict())
```

## Разбор запроса отдельно

Если нужен только синтаксический разбор:

```python
from dsl import ActorDslParser


parser = ActorDslParser()
query = parser.parse(
    """
    CONTEXT sentence[<=4]
    FOR "дверь", "тишина"
    WITHIN paragraph[=1]
    RETURN text, matches
    """.strip()
)

print(type(query).__name__)
print(query.to_dict())
```

Это полезно, если:

- нужно проверить синтаксис;
- нужен AST запроса для отдельной обработки;
- хочется тестировать парсер независимо от executor-а.

## Выполнение AST запроса отдельно

Если запрос уже разобран, можно выполнять его отдельно:

```python
from document_ast import ActorAstParser
from dsl import ActorDslExecutor, ActorDslParser


document = ActorAstParser.from_config_dir("config/formats").parse("text.txt", format_name="txt")
query = ActorDslParser().parse(
    """
    FIND sentence
    WHERE follows(sentence[text ~= /Только тишина/])
    RETURN text
    """.strip()
)

result = ActorDslExecutor().execute(document, query)
print(result.to_dict())
```

## Примеры запросов

### 1. Найти предложения про телефон

```dsl
FIND sentence
WHERE has_descendant(word[text ~= /телефон/i])
RETURN text, count
```

Ожидаемый смысл:

- пройти по всем `sentence`;
- оставить только те, где в поддереве есть слово `телефон`;
- вернуть текст найденных предложений и их число.

### 2. Найти предложение после предложения про тишину

```dsl
FIND sentence
WHERE follows(sentence[text ~= /Только тишина/])
RETURN text
```

Ожидаемый смысл:

- взять все `sentence`;
- оставить то предложение, у которого непосредственный предыдущий `sentence` совпадает с `/Только тишина/`.

### 3. Найти минимальное контекстное окно

```dsl
CONTEXT sentence[<=4]
FOR "дверь", "тишина"
WITHIN paragraph[=1]
RETURN text, matches
```

Ожидаемый смысл:

- рассматривать окна из подряд идущих `sentence`;
- длина окна не больше 4;
- в окне должны встретиться `дверь` и `тишина`;
- окно должно лежать в одном `paragraph`;
- вернуть текст окна и найденные совпадения.

### 4. Найти определения в `GA_1_2025.tex`

```dsl
FIND semantic_block
WHERE metadata.kind = "definition"
RETURN text, count
```

### 5. Найти все теоремы

```dsl
FIND semantic_block
WHERE metadata.kind = "theorem"
RETURN text, count
```

### 6. Найти доказательства в нужном разделе

```dsl
FIND semantic_block
WHERE metadata.kind = "proof"
  AND has_ancestor(section[text ~= /Языки и грамматики/])
RETURN text, count
```

## Важная практическая оговорка

Запросы нужно писать в соответствии с реальной структурой AST.

Для текущего `txt.yaml` предложение содержит не слова напрямую, а `clause`, внутри которых уже лежат `word`.

Поэтому для `txt` надёжный запрос это:

```dsl
FIND sentence
WHERE has_descendant(word[text = "телефон"])
```

а не:

```dsl
FIND sentence
WHERE has_child(word[text = "телефон"])
```

Это не ошибка DSL, а следствие реальной иерархии AST.

## Что возвращает executor

Для `FIND` возвращается `FindQueryExecutionResult`.

Для `CONTEXT` возвращается `ContextQueryExecutionResult`.

Оба результата имеют `to_dict()`, так что их удобно:

- печатать;
- сериализовать в JSON;
- использовать в тестах.

## Что посмотреть дальше

- [Архитектура DSL](./dsl_architecture.md)
- [Описание DSL](./dsl_language.md)
- [Архитектура AST-парсера](./ast_parser_architecture.md)
