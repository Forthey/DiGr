# DSL: запросы, расстояния и примеры на GA_1_2025.tex

Этот документ описывает текущий пользовательский функционал DSL после добавления расстояний между элементами.
DSL работает поверх уже построенного `AstDocument`: он не читает исходный файл сам и не меняет структуру документа.
Структура сущностей берётся из YAML-конфига формата, например для TeX из `config/formats/tex.yaml`.

## Текущая модель TeX AST

Для `GA_1_2025.tex` используется формат `tex`.
Важные сущности:

- `section` - корневой уровень документа;
- `subsection_scope` - область подраздела или текст до первого подраздела;
- `content_scope` - область содержимого, в том числе `frame` или свободный текст;
- `semantic_block` - прикладной TeX-блок.

У `content_scope` и `semantic_block` есть `metadata.kind`.
Для `semantic_block` практически важны значения:

- `theorem`;
- `lemma`;
- `proof`;
- `example`;
- `remark`;
- `digress`;
- `plain`;
- `itemize`;
- `enumerate`;
- `frametitle`;
- `subsubsection`.

Отдельно про определения в `GA_1_2025.tex`: окружение `\begin{definition}...\end{definition}` встречается только один раз.
Поэтому примеры и аналитические запросы не должны опираться на `metadata.kind = "definition"` как на регулярную разметку определений.
В этом файле большинство терминологических определений размечены командой `\odmkey{...}{...}` внутри обычных `semantic_block`, чаще всего с `metadata.kind = "plain"`.
Если нужно искать именно учебные определения/термины, практичнее использовать selector по тексту:

```dsl
semantic_block[text ~= /\\odmkey/]
```

Важно: текущий `tex.yaml` не строит сущность `word`.
Зато во всех форматах теперь автоматически есть универсальная сущность `symbol`.
Для TeX она создаётся под leaf-узлами `semantic_block`, поэтому `distance(symbol)` позволяет измерять расстояние в символах исходного TeX-текста.
Если нужно исключать пробелы или переводы строк из `symbol`, это настраивается в `format.symbols.exclude`.

## Какие запросы есть

### FIND

`FIND` выбирает существующие узлы AST одного типа.

Общая форма:

```dsl
FIND entity
WHERE predicate
WITHIN entity[count]
RETURN item, item, ...
```

Пример:

```dsl
FIND semantic_block
WHERE text ~= /\\odmkey/
RETURN text, count
```

Что делает:

1. Берёт все узлы `semantic_block`.
2. Оставляет блоки, внутри которых встречается команда `\odmkey`.
3. Возвращает текст найденных блоков и их количество.

### CONTEXT

`CONTEXT` ищет минимальные окна из подряд идущих узлов одного базового типа.

Общая форма:

```dsl
CONTEXT entity[count]
FOR pattern, pattern, ...
WITHIN entity[count]
WHERE predicate
RETURN item, item, ...
```

Паттерны в `FOR` могут быть:

- строкой;
- regex;
- selector-ом, например `semantic_block[metadata.kind = "theorem"]`.

После добавления расстояний `CONTEXT` поддерживает `RETURN distance(entity)`.
Расстояния считаются только между selector-паттернами, потому что строка и regex не имеют собственного AST-узла.

### DISTANCE

`DISTANCE` измеряет расстояния между парами элементов.

Общая форма:

```dsl
DISTANCE selector
TO selector
WITHIN entity[count]
LIMIT_PAIRS nearest
RETURN pairs, stats, distance(entity), count
```

`distance(entity)` обязателен для `DISTANCE`.
Он задаёт, какие AST-узлы считаются единицей расстояния.
Например:

- `distance(semantic_block)` считает количество semantic-блоков между двумя элементами;
- `distance(content_scope)` считает content-scope между двумя элементами;
- `distance(symbol)` считает символы между двумя элементами.

Семантика расстояния:

1. DSL выбирает все элементы левого selector-а.
2. DSL выбирает все элементы правого selector-а.
3. Строятся пары непересекающихся элементов.
4. Если указан `WITHIN`, пара проходит фильтр только когда оба элемента удовлетворяют контейнерному ограничению.
5. Для каждой пары элементы упорядочиваются по позиции в документе.
6. Расстояние равно количеству узлов `distance(entity)`, которые лежат строго между концом первого элемента и началом второго.
7. Результат сортируется по расстоянию, затем по позиции в документе.
8. `LIMIT_PAIRS` выбирает, сколько пар вернуть.

`LIMIT_PAIRS`:

- отсутствует или `nearest` - вернуть одну ближайшую пару;
- `all_nearest` - вернуть все пары с минимальным расстоянием;
- целое число, например `3` - вернуть k ближайших пар;
- `all` - вернуть все валидные пары.

`RETURN` для `DISTANCE`:

- `pairs` - сами пары;
- `stats` - агрегаты по расстояниям;
- `distance(entity)` - единица измерения;
- `count` - количество возвращённых пар;
- `source` - путь к исходному файлу.

`stats` содержит:

- `count`;
- `mean`;
- `variance`;
- `min`;
- `max`.

## Примеры на GA_1_2025.tex: DISTANCE

### 1. Ближайшие theorem/proof по semantic-блокам

Запрос:

```dsl
DISTANCE semantic_block[metadata.kind = "theorem"]
TO semantic_block[metadata.kind = "proof"]
LIMIT_PAIRS all_nearest
RETURN pairs, stats, distance(semantic_block), count
```

Общий смысл:

Найти ближайшие пары "теорема - доказательство" в документе и измерить, сколько `semantic_block` находится между элементами пары.
Это устойчивый пример для `GA_1_2025.tex`, потому что theorem и proof встречаются много раз.

Пошагово:

1. Берутся все `semantic_block` с `metadata.kind = "theorem"`.
2. Берутся все `semantic_block` с `metadata.kind = "proof"`.
3. Строятся все непересекающиеся пары theorem/proof.
4. Для каждой пары определяется более ранний и более поздний блок.
5. Между ними считаются `semantic_block`, лежащие строго в промежутке.
6. Пары сортируются по расстоянию.
7. `LIMIT_PAIRS all_nearest` оставляет все пары с минимальным расстоянием.
8. `stats` считает агрегаты по возвращённым расстояниям.

На текущем `GA_1_2025.tex` ближайшие theorem/proof-пары часто имеют расстояние `0`, то есть proof идёт сразу после theorem.

### 2. Три ближайшие пары theorem/example

Запрос:

```dsl
DISTANCE semantic_block[metadata.kind = "theorem"]
TO semantic_block[metadata.kind = "example"]
LIMIT_PAIRS 3
RETURN pairs, stats, distance(semantic_block), count
```

Общий смысл:

Посмотреть три ближайшие пары theorem/example.
Это полезно, если нужно понять, насколько близко примеры расположены к теоретическим утверждениям.

Пошагово:

1. Выбираются theorem-блоки и example-блоки.
2. Строятся все валидные пары.
3. Для каждой пары считается количество `semantic_block` между элементами.
4. Пары сортируются от меньшего расстояния к большему.
5. `LIMIT_PAIRS 3` оставляет первые три пары.
6. `stats` агрегирует расстояния только по этим трём возвращённым парам.

На текущем `GA_1_2025.tex` результат содержит `3` пары.
Статистика по ним: `mean = 0.6666666666666666`, `variance = 0.22222222222222224`, `min = 0`, `max = 1`.

### 3. Терминологические определения через odmkey рядом с theorem

Запрос:

```dsl
DISTANCE semantic_block[text ~= /\\odmkey/]
TO semantic_block[metadata.kind = "theorem"]
LIMIT_PAIRS 3
RETURN pairs, stats, distance(semantic_block), count
```

Общий смысл:

Найти терминологические блоки с `\odmkey` рядом с theorem.
В `GA_1_2025.tex` это более корректная модель "определений", чем `metadata.kind = "definition"`, потому что терминология размечена командой `\odmkey`.

Пошагово:

1. Выбираются все `semantic_block`, в тексте которых есть `\odmkey`.
2. Выбираются все theorem-блоки.
3. Строятся пары "терминологический блок - theorem".
4. Считается число `semantic_block` между ними.
5. `LIMIT_PAIRS 3` возвращает три ближайшие пары.

На текущем `GA_1_2025.tex` для трёх ближайших пар расстояние равно `0`: терминологический блок непосредственно соседствует с theorem.

### 4. Ограничение пары контейнером WITHIN

Запрос:

```dsl
DISTANCE semantic_block[metadata.kind = "theorem"]
TO semantic_block[metadata.kind = "proof"]
WITHIN content_scope[=1]
LIMIT_PAIRS all_nearest
RETURN pairs, stats, distance(semantic_block), count
```

Общий смысл:

Найти ближайшие пары theorem/proof, но учитывать только такие пары, где оба элемента лежат внутри одного `content_scope`.

Пошагово:

1. Выбираются theorem и proof.
2. Для каждой пары находятся ancestor-контейнеры типа `content_scope`.
3. Условие `WITHIN content_scope[=1]` требует, чтобы пара принадлежала ровно одному общему content-scope.
4. Пары из разных content-scope отбрасываются.
5. Для оставшихся пар считается `distance(semantic_block)`.

Такой запрос полезен, если нужно не смешивать элементы из разных frame/free-областей.

### 5. Расстояние в символах между терминологическим блоком и theorem

Запрос:

```dsl
DISTANCE semantic_block[text ~= /Степень!слова/]
TO semantic_block[metadata.kind = "theorem"]
LIMIT_PAIRS all_nearest
RETURN pairs, stats, distance(symbol), count
```

Общий смысл:

Измерить расстояние не в semantic-блоках, а в символах между конкретным терминологическим блоком и ближайшей theorem.

Пошагово:

1. Выбирается `semantic_block`, где встречается `Степень!слова`.
2. Выбираются все theorem-блоки.
3. Строятся пары между выбранным терминологическим блоком и theorem.
4. Для каждой пары считаются `symbol`, лежащие строго между блоками.
5. `all_nearest` оставляет ближайшую пару или несколько пар с одинаковым минимальным расстоянием.

В текущем `GA_1_2025.tex` ближайший theorem идёт сразу после такого терминологического блока, поэтому `distance(symbol)` равно `0`.

## Примеры на GA_1_2025.tex: CONTEXT с distance

### 1. Окна theorem/proof с расстоянием

Запрос:

```dsl
CONTEXT semantic_block[<=8]
FOR th: semantic_block[metadata.kind = "theorem"],
    pr: semantic_block[metadata.kind = "proof"]
RETURN matches, distance(semantic_block), count
```

Общий смысл:

Найти короткие окна из `semantic_block`, где одновременно есть theorem и proof, и добавить расстояние между найденными selector-паттернами.

Пошагово:

1. `CONTEXT semantic_block[<=8]` строит окна из подряд идущих `semantic_block` длиной до 8.
2. Паттерн `th` требует theorem внутри окна.
3. Паттерн `pr` требует proof внутри окна.
4. Executor оставляет минимальные окна, где оба selector-паттерна найдены.
5. `RETURN matches` возвращает найденные selector-совпадения.
6. `RETURN distance(semantic_block)` добавляет поле `distances`.
7. В `distances` для каждой пары selector-узлов указывается, сколько `semantic_block` лежит между ними.

На текущем `GA_1_2025.tex` такой запрос возвращает окна, где proof часто идёт сразу после theorem.
Для таких окон расстояние равно `0`.

### 2. Окно theorem/example

Запрос:

```dsl
CONTEXT semantic_block[<=8]
FOR th: semantic_block[metadata.kind = "theorem"],
    ex: semantic_block[metadata.kind = "example"]
RETURN matches, distance(semantic_block), count
```

Общий смысл:

Найти локальные фрагменты, где рядом встречаются theorem и example, и измерить расстояние между ними внутри окна.

Пошагово:

1. Строятся окна из подряд идущих `semantic_block` длиной до 8.
2. В каждом окне ищется theorem-паттерн `th`.
3. В каждом окне ищется example-паттерн `ex`.
4. Окна без обоих паттернов отбрасываются.
5. Для найденных selector-узлов считается `distance(semantic_block)`.
6. Результат показывает не только факт совместного появления theorem/example, но и насколько близко они стоят.

На текущем `GA_1_2025.tex` первый найденный такой контекст даёт расстояние `5` `semantic_block` между theorem и example.

### 3. Окно с терминологическим блоком odmkey и theorem

Запрос:

```dsl
CONTEXT semantic_block[<=4]
FOR term: semantic_block[text ~= /\\odmkey/],
    th: semantic_block[metadata.kind = "theorem"]
RETURN matches, distance(semantic_block), count
```

Общий смысл:

Проверить, есть ли терминологический блок с `\odmkey` рядом с theorem в коротком окне до 4 semantic-блоков.

Пошагово:

1. Строятся окна до 4 подряд идущих `semantic_block`.
2. В каждом окне ищется блок с `\odmkey`.
3. В каждом окне ищется theorem.
4. Если оба элемента не попали в одно окно, окно не возвращается.
5. Для найденных selector-узлов считается расстояние в `semantic_block`.

На текущем `GA_1_2025.tex` такой запрос возвращает локальные окна.
Первый найденный контекст имеет расстояние `0`: блок с `\odmkey` непосредственно предшествует theorem.

### 4. Окно с расстоянием в символах

Запрос:

```dsl
CONTEXT semantic_block[<=4]
FOR term: semantic_block[text ~= /Степень!слова/],
    th: semantic_block[metadata.kind = "theorem"]
RETURN matches, distance(symbol), count
```

Общий смысл:

Найти короткое окно, где конкретный терминологический блок расположен рядом с theorem, и измерить расстояние между ними в символах.

Пошагово:

1. Строятся окна до 4 подряд идущих `semantic_block`.
2. В окне ищется блок с `Степень!слова`.
3. В том же окне ищется theorem.
4. `RETURN distance(symbol)` добавляет расстояние между найденными selector-узлами в символах.

Такой запрос показывает, что `symbol` можно использовать в `CONTEXT` так же, как любую другую entity.

## Практическая разница DISTANCE и CONTEXT

`DISTANCE` отвечает на вопрос:

```text
Какие пары X/Y ближе всего друг к другу в документе или внутри заданного контейнера?
```

`CONTEXT ... RETURN distance(entity)` отвечает на вопрос:

```text
В каких локальных окнах одновременно встречаются нужные паттерны, и какое расстояние между найденными AST-узлами внутри этих окон?
```

То есть:

- используйте `DISTANCE`, когда нужна глобальная таблица пар и статистика;
- используйте `CONTEXT`, когда сначала важна локальная совместная встречаемость, а расстояние нужно как дополнительная характеристика найденного окна.
