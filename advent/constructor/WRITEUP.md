# Конструктор: Write-up

Перед нами — новый сайт ПАО «АгроКекСтрой». Теперь, кроме улучшенной анимированной главной страницы, на нём появились «Очерки».

Обнаружить их существование довольно нетрудно: ссылка «О нас» в шапке ведёт на страницу с адресом `https://constructor.a.2025.ugractf.ru/ОЧЕРКИ/2/`.

Когда мы видим некое (очевидно, порядковое) число в пути, мы, конечно же, пытаемся посмотреть все остальные «очерки». Очерк №1, судя по всему, соответствует главной странице, второй мы уже видели. Кроме этого обнаруживаем ещё три очерка, которые, к сожалению, не особо помогают. Вместе с тем, из очерка №5 мы узнаем, что сайт собран на некой «системе управления контентом» «в коллаборации с WordPress». Что бы это могло значить, непонятно.

Попробуем передать вместо номера очерка что-нибудь некорректное — перейдём по ссылке `https://constructor.a.2025.ugractf.ru/ОЧЕРКИ/A/`. Получаем кое-что новое: ошибку «Вы уронили сервер» с кодом ошибки 500.

Можно лишь предположить, что раз данный сайт поддерживает некую возможность управления контентом, то этот самый контент хранится в некой базе данных. И в таком случае эта ошибка имеет смысл, если вместо числового аргумента в поиск по номеру поста передали букву. Что ж, в таком случае, можно сделать вывод, что запрос вообще никак не проверяется, и это значит, что можно применить атаку под названием [SQL-инъекция](https://ru.wikipedia.org/wiki/%D0%92%D0%BD%D0%B5%D0%B4%D1%80%D0%B5%D0%BD%D0%B8%D0%B5_SQL-%D0%BA%D0%BE%D0%B4%D0%B0).

Предположим, как может выглядеть запрос. Если ввод произвольной строки приводит к ошибке, скорее всего, он выглядит как-то так:

```sql
select * from post where id = <ввод>
```

Проверим это предположение. Убедимся, что очерка, например, №100 не существует. После этого подставим значение `100 or 1=1`: после подстановки получится

```sql
select * from post where id = 100 or 1=1
```

Этот запрос выберет очерки, у которых _либо_ ID равен 100, _либо_ для которых верно `1 = 1`. Поскольку второе условие верно всегда, запрос выберет все очерки. И действительно, мы получаем первый очерк — видимо, при выводе контент отфильтровывается и мы видим только одну строку вывода.

Чтобы получить какой-то ещё контент, кроме очерков, нам понадобится оператор `union`: он объединяет запрос до него и после в одну большую таблицу. Например, запрос

```sql
select * from post where id = 1 union select * from post where id = 2
```

выберет два очерка: первый и второй. Однако мы пока не знаем ни название таблицы, ни название столбцов, поэтому сделать так не можем.

Ещё одна проблема в том, что число столбцов в первой и во второй таблице должно совпадать (некоторые СУБД требуют ещё и совпадение типов). В SQL есть способ просто получить какие-то константные данные: `select 1, 2, 3` вернет одну строку и три столбца: в первом будет `1`, во втором `2`, в третьем `3`. Давайте перебором узнаем, сколько столбцов в нашей первой таблице.

Запрос `100 union select 1, 2` выполняется успешно, а все остальные такого вида — падают. Значит, в первой таблице два столбца. Причём, судя по выводу, первый — это заголовок очерка, а второй — его содержимое.

Теперь давайте больше узнаем про тип нашей базы данных. В разных базах данных разные особенности языка запросов, поэтому, зная, какая именно база используется, нам будет проще работать дальше.

Самый простой способ это узнать — воспользоваться функцией, которая возвращает версию СУБД. У каждой базы данных эта функция называется по-разному, перебрав все, мы найдём какую-то полезную. Например, можно воспользоваться [шпаргалкой](https://www.invicti.com/blog/web-security/sql-injection-cheat-sheet/). Запрос `100 union select sqlite_version(), 2` успешно проходит — теперь мы знаем, что это SQLite.

Ищем, как вытащить список таблиц и столбцов: находим, что в SQLite есть таблица `sqlite_master` (ещё она находится по имени `sqlite_schema`), содержащая, кроме всего прочего, столбцы `name` (название таблицы) и `sql` (структура таблицы). Пробуем:

```sql
100 union select name, sql FROM sqlite_master where type='table'
```

Получаем информацию о таблице ОЧЕРКИ (да-да, именно так она и называется):

![](writeup/ocherki.png)

В ней есть три столбца: численный столбец №_ПО_ПОРЯДКУ, и текстовые столбцы ЗАГОЛОВОК и СОДЕРЖИМОЕ. Теперь мы знаем даже точное начало запроса:

```sql
select ЗАГОЛОВОК, СОДЕРЖИМОЕ from ОЧЕРКИ where №_ПО_ПОРЯДКУ = <input>
```

Чтобы получить какие-то ещё записи, воспользуемся операторами `offset` и `limit`. Первый говорит, сколько записей пропустить, а второй — сколько записей взять.

Например, если наш запрос возвращает 123 записи, то запрос с `limit 50 offset 50` вернёт записи с 51-й по 100-ю.

```sql
100 union select name, sql FROM sqlite_master where type='table' limit 1 offset 1
-- а это вернёт вторую запись
```

Так мы узнаём о существовании таблицы РЕГУЛИРОВКИ, в которой есть столбцы НАЗВАНИЕ и СОДЕРЖИМОЕ. Узнаем, что там:

```sql
100 union select * from РЕГУЛИРОВКИ
-- заголовок сайта — АгроКекСтрой
100 union select * from РЕГУЛИРОВКИ limit 1 offset 1
-- ключ регистрации — ugra_welcome_to_cyberspace_1rk0upvny4wj
```

О, купончик!

Флаг: **ugra_welcome_to_cyberspace_1rk0upvny4wj**
