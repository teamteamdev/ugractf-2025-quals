# Летнее чтение: Write-up

На сайте видим страницу, где с очень маленькой скоростью прокручиваются лицензионные соглашения:

![Окно лицензионного соглашения](writeup/page.png)

Зайдем в _Inspect Element_. Это `<textarea>`, в которой раз в две секунды меняется содержимое, то есть напрямую прочитать всё лицензионное соглашение целиком явно не выйдет, а сделать нам надо, судя по всему, именно это.

Где же расположен код, который отвечает за прокрутку? Зайдём в раздел _Debugger_ (Firefox) или _Sources_ (Chromium) и посмотрим, какие файлы вообще загружены:

![Debugger в Firefox](writeup/debugger_firefox.png)

![Sources в Chromium](writeup/sources_chromium.png)

Включим pretty-printing и просмотрим все файлы глазами. Интересное находится в файле `page-137ea9639fb96376.js`, где мы видим строку, похожую на начало лицензий:

![Debugger в Firefox](writeup/debugger_firefox_page.png)

![Sources в Chromium](writeup/sources_chromium_page.png)

Скопируем её в текстовый файл, заменим `\n` на настоящие переводы строк, пролистаем и посмотрим, попадётся ли что-то интересное. Среди прочих лицензий находим некую _TEAMTEAM LICENSE_, включающую в себя флаг, но не как обычную строку, начинающуюся с `ugra_`, а закодированный [названиями Unicode-кодпоинтов](https://en.wikipedia.org/wiki/List_of_Unicode_characters#Latin_script):

![Лицензии](writeup/licenses.png)

Переписываем флаг руками или пользуясь функцией `unicodedata.lookup` в Python, и получаем флаг.

Флаг: **ugra_blindly_accepting_licenses_is_unacceptable_0e72cuhvo8a2**
