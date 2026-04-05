# Конфигурация AST-парсера

## Назначение конфигурации

Структура разбора документа задаётся отдельным YAML-файлом на каждый формат:

- `config/formats/txt.yaml`
- `config/formats/json.yaml`
- `config/formats/xml.yaml`
- и так далее

Правило простое: один формат, один файл `<format>.yaml`.

Это нужно для того, чтобы:

- не смешивать правила разных форматов в одном большом конфиге
- хранить полное описание структуры формата рядом
- расширять систему без изменения `AstBuilder`

## Общая схема `<format>.yaml`

Минимальная схема формата выглядит так:

```yaml
format:
  name: txt
  reader:
    kind: plain_text
  root_entity: page

entities:
  page:
    contains: paragraph
    segmenter:
      kind: passthrough

  paragraph:
    contains: sentence
    segmenter:
      kind: split
      boundary_pattern: '(?:\r?\n\s*\r?\n)+'
      trim: true
      drop_empty: true

  sentence:
    contains: word
    segmenter:
      kind: match
      pattern: '.+?(?:[.!?…]|$)'
```

Верхний уровень всегда содержит только два раздела:

- `format`
- `entities`

## Раздел `format`

### `format.name`

Имя формата. Оно должно:

- быть непустой строкой
- совпадать с ожидаемым именем формата
- обычно совпадать с расширением файла

Например, для `config/formats/txt.yaml` ожидается `name: txt`.

### `format.reader`

Настройка reader, который превращает исходный файл в [SourceDocument](/home/forthey/projects/DiGr/src/document_ast/source_document.py).

Обязательное поле:

- `kind`: имя reader-реализации

Текущая поддержка в коде:

- `plain_text`

Дополнительные поля reader-конфига зависят от конкретного `SourceReader`. Для `plain_text` используется:

- `encoding`

### `format.root_entity`

Имя корневой сущности дерева, с которой начинается рекурсивная сборка AST.

Важно:

- `root_entity` должна ссылаться на сущность из `entities`
- сам `AstBuilder` всегда создаёт технический корневой узел `document`
- `root_entity` определяет уже первый прикладной уровень под `document`

Например:

- `document`
  - `page`
    - `paragraph`
      - `sentence`
        - `clause`
          - `word`

Здесь `root_entity` равно `page`.

## Раздел `entities`

`entities` это mapping вида:

```yaml
entities:
  entity_name:
    contains: child_entity_name
    segmenter:
      ...
```

Каждая запись описывает:

- имя сущности
- дочернюю сущность, если она есть
- способ выделить экземпляры этой сущности из входного текста

### `contains`

Поле `contains` задаёт отношение включения:

- `page contains paragraph`
- `paragraph contains sentence`
- `sentence contains clause`
- `clause contains word`

Если `contains` отсутствует, сущность считается листовой.

Для листа это выглядит так:

```yaml
word:
  segmenter:
    kind: match
    pattern: "[^\\W_]+(?:[-'][^\\W_]+)*"
```

### `segmenter`

`segmenter` обязателен для каждой сущности. Он определяет, как из текста текущего уровня получить сегменты этой сущности.

Поддержанные виды сегментации:

- `passthrough`
- `split`
- `match`

## `segmenter.kind: passthrough`

`passthrough` не делит текст, а возвращает один сегмент, равный всему входу.

Пример:

```yaml
page:
  contains: paragraph
  segmenter:
    kind: passthrough
```

Это полезно, когда сущность на текущем этапе не нужно резать явно. В `txt.yaml` именно так задаётся `page`, потому что весь файл сначала рассматривается как одна страница.

## `segmenter.kind: split`

`split` режет текст по границам, заданным регулярным выражением `boundary_pattern`.

Пример:

```yaml
paragraph:
  contains: sentence
  segmenter:
    kind: split
    boundary_pattern: '(?:\r?\n\s*\r?\n)+'
    trim: true
    drop_empty: true
```

Поддержанные поля:

- `boundary_pattern`: обязательное регулярное выражение-разделитель
- `trim`: обрезать пробелы по краям сегмента, по умолчанию `true`
- `drop_empty`: выбрасывать пустые сегменты, по умолчанию `true`
- `flags`: список regex-флагов, дополнительно к `re.MULTILINE`

Важно понимать семантику:

- `split` ищет именно разделители
- текст между разделителями становится сегментом
- сами разделители в итоговые сегменты не входят

## `segmenter.kind: match`

`match` ищет сами сегменты регулярным выражением `pattern`.

Пример:

```yaml
sentence:
  contains: clause
  segmenter:
    kind: match
    pattern: '.+?(?:[.!?…](?:["»”’'']+)?|$)'
    trim: true
    drop_empty: true
    flags:
      - MULTILINE
      - DOTALL
```

Поддержанные поля:

- `pattern`: обязательное регулярное выражение
- `trim`
- `drop_empty`
- `flags`

Семантика здесь другая:

- `match` выбирает то, что совпало с регулярным выражением
- именно совпавший текст становится сегментом

Это удобно для предложений, клауз и слов, потому что можно точнее контролировать границы результата.

## Regex-флаги

Поле `flags` задаётся как список имён констант из модуля `re`.

Пример:

```yaml
flags:
  - MULTILINE
  - DOTALL
```

Сейчас [TextSegmenter](/home/forthey/projects/DiGr/src/document_ast/text_segmenter.py) всегда включает `re.MULTILINE`, а затем добавляет перечисленные во `flags` значения.

Если передать неподдержанное имя, будет выброшена ошибка конфигурации.

## Что валидирует `ConfigLoader`

[ConfigLoader](/home/forthey/projects/DiGr/src/document_ast/config_loader.py) проверяет:

- что корень YAML это mapping
- что есть раздел `format`
- что есть раздел `entities`
- что `format.name` непустой
- что `format.reader` это mapping
- что `format.root_entity` непустой
- что каждая сущность это mapping
- что `segmenter.kind` это строка
- что `root_entity` существует в `entities`
- что каждое `contains` ссылается на существующую сущность
- что в иерархии `contains` нет циклов

Последний пункт принципиален: структура сущностей должна быть деревом по отношению владения вниз, а не циклическим графом.

## Подробный разбор `config/formats/txt.yaml`

Файл [txt.yaml](/home/forthey/projects/DiGr/config/formats/txt.yaml) описывает формат plain text.

Его верхний раздел:

```yaml
format:
  name: txt
  reader:
    kind: plain_text
    encoding: utf-8
  root_entity: page
```

Смысл полей:

- `name: txt`: формат называется `txt`
- `reader.kind: plain_text`: источник читается обычным чтением текстового файла
- `reader.encoding: utf-8`: текст декодируется как UTF-8
- `root_entity: page`: первый прикладной уровень AST это страницы

### Сущность `page`

```yaml
page:
  contains: paragraph
  segmenter:
    kind: passthrough
```

Смысл:

- весь документ сначала рассматривается как одна страница
- отдельного деления на страницы для plain text сейчас нет
- содержимым страницы являются абзацы

Это важный архитектурный момент: сущность `page` здесь не захардкожена в коде. Она существует только потому, что так описано в конфиге.

### Сущность `paragraph`

```yaml
paragraph:
  contains: sentence
  segmenter:
    kind: split
    boundary_pattern: '(?:\r?\n\s*\r?\n)+'
    trim: true
    drop_empty: true
```

Смысл:

- абзацы отделяются одной или несколькими пустыми строками
- допускаются разные окончания строк
- пробелы по краям абзаца удаляются
- пустые сегменты после разрезания отбрасываются

Почему здесь `split`, а не `match`:

- нас интересуют блоки между пустыми строками
- сами пустые строки не должны попадать в AST

### Сущность `sentence`

```yaml
sentence:
  contains: clause
  segmenter:
    kind: match
    pattern: '.+?(?:[.!?…](?:["»”’'']+)?|$)'
    trim: true
    drop_empty: true
    flags:
      - MULTILINE
      - DOTALL
```

Эта настройка делает следующее:

- берёт минимальную последовательность символов `.+?`
- заканчивает предложение на `.`, `!`, `?`, `…` или на конце текста
- допускает завершающие кавычки после знака конца предложения
- позволяет предложению проходить через переводы строки за счёт `DOTALL`

Почему выбран `match`:

- предложение лучше определяется не разделителем, а полным паттерном границы
- так проще корректно захватить завершающую пунктуацию и кавычки

### Сущность `clause`

```yaml
clause:
  contains: word
  segmenter:
    kind: match
    pattern: '.+?(?:[,;:—]|$)'
    trim: true
    drop_empty: true
    flags:
      - MULTILINE
      - DOTALL
```

Смысл:

- клаузой считается фрагмент до запятой, точки с запятой, двоеточия, длинного тире или конца текста
- завершающий знак остаётся внутри сегмента

Это не универсальная лингвистическая модель и не претендует на полноту. Это конфигурируемое прикладное правило сегментации для данного формата.

### Сущность `word`

```yaml
word:
  segmenter:
    kind: match
    pattern: "[^\\W_]+(?:[-'][^\\W_]+)*"
```

Этот шаблон:

- берёт последовательности буквенно-цифровых word-символов без `_`
- допускает внутренние `-` и `'`
- позволяет корректно выделять составные токены вроде `кто-то` или `rock'n'roll`

Поскольку `word` не содержит дочерних сущностей, это листовой уровень дерева.

## Как расширять конфигурацию

### Новый text-based формат

Если новый формат можно читать как plain text:

1. скопируй `txt.yaml` в `<format>.yaml`
2. измени `format.name`
3. измени `root_entity` и `entities` под новый документный формат

### Новый бинарный или структурный формат

Если нужен собственный reader:

1. создай новый `SourceReader`
2. зарегистрируй его в [SourceReaderRegistry](/home/forthey/projects/DiGr/src/document_ast/source_reader_registry.py)
3. укажи новый `reader.kind` в `<format>.yaml`

## Связанные материалы

- [Архитектура AST-парсера](./ast_parser_architecture.md)
- [Быстрый старт по AST-парсеру](./ast_parser_quickstart.md)
