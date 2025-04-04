# Постановление: Write-up

Нам дан серьёзный PDF-документ, составленный самим У. Ц. Уцугом.

![](writeup/patch.png)

Немного почитав и осмыслив документ, понимаем, что это — патч в ядро Linux. К сожалению, в отличие от [нормальных](https://docs.kernel.org/process/submitting-patches.html) патчей этот экземпляр представлен в виде PDF-документа, который требует вносить изменения в определённом порядке. Что ж, попробуем это сделать.

Ознакомимся с пунктом 2 «Постановления», где указано, какую версию ядра необходимо выбрать, и клонируем исходники ядра [версии 6.8](https://github.com/torvalds/linux/tree/v6.8).

Пункты 1.1 и 1.2 применить просто даже вручную — и уже по ним можно понять, что добавленный патч реализует некий дополнительный модуль ядра с названием `virtio_flag` и незамысловатым описанием `Enable additional security module`. А вот пункт 1.4 содержит уже 122 подпункта, и для их применения нам понадобится написать программу.

Для начала скопируем текст из PDF куда-нибудь ещё (например, в текстовый редактор), и попробуем автозаменой нормализовать текст: уберём все переносы строк, перед которыми нет `;` и заменим их на пробелы. Это можно сделать с помощью регулярных выражений заменой `([^;])\n` на `$1 ` — мы берём последний символ строки перед переносом, если это не точка с запятой, и меняем на этот же символ, но уже с пробелом. Теперь мы получили строки, в каждой из которых ровно один пункт патча.

Можно заметить, что вариантов замен всего три:
* после строки N добавить пустую строку
* после строки N добавить строку опредёленного содержания (возможно, с табами в начале)
* вставить текст в строку на указанную позицию

Отличить эти замены друг от друга и достать параметры можно с помощью регулярных выражений.

[Пример кода для реализации замен](dev/applier.py)

В результате мы должны получить файл [virtio_flag.c](dev/virtio_flag.c). Если поискать ключевые слова, встречающиеся в коде, то по названию функции [`register_chrdev`](https://www.opennet.ru/man.shtml?topic=register_chrdev&category=9&russian=2) можно найти описание того, что эта функция регистрирует [драйвер символьного устройства](https://linux-kernel-labs.github.io/refs/heads/master/labs/device_drivers.html) — такое устройство поддерживает чтение или запись потока символов.

Если внимательно изучить пояснительную записку к постановлению, мы узнаем, что цель патча — безопасное хранение секретов непосредственно в ядре. Следовательно, можно заключить, что это устройство умеет такие секреты предоставлять по запросу.

Дальше есть два подхода к решению задания:

1. Можно собрать этот модуль ядра и запустить его.

   > Для запуска недоверенного кода — а тем более недоверенного _ядра_ — всегда используйте виртуальную машину.

   Самый простой способ — включить новую опцию `CONFIG_VIRTIO_FLAG=y` в `.config` и собрать ядро командой `make -j$(nproc)`. Это долго, но надёжно. Получившееся ядро в директории `arch/x86/boot` можно положить в `/boot` и запуститься с него.

   Чуть более сложный — собрать модуль отдельно и подключить его. Скопируйте `virtio_flag.c` куда-нибудь ещё, установите заголовки вашего ядра (пакет вида `linux-6.8*-headers`), добавьте новый `Makefile`:

   ```makefile
   obj-m += virtio_flag.o
   all:
   	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules
   clean:
   	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
   ```

   И выполните `make`. У вас появится модуль `virtio_flag.ko`, который можно подключить командой `insmod`.

   В обоих случаях в системном логе (`dmesg` или `journalctl -b`) у вас появится сообщение вида `flag loaded, major = 240`. 240 — номер нашего модуля в системе (он присваивается автоматически). Теперь можно создать файл, через который можно читать данные:

   ```bash
   $ mknod /dev/flag c 240 0
   $ cat /dev/flag
   ugra_please_burn_that_patch_in_the_darkest_pits_of_hell_qez9peqhcqpi3xif7kikza0u$
   ```

2. Просто почитать, что же происходит в модуле.

   Основные содержательные функции — `virtio_flag_chr` и `virtio_flag_device_read`, которая вызывает первую.

   По стандартной конвенции для функций, которые что-то читают, возвращаемое значение функции `read` — количество прочитанных байт. Она всегда возвращает 1 (и в таком случае двигает `offset`) или 0 (если `virtio_flag_chr` вернула нулевой байт). Можно сделать вывод, что символы флага читаются по одному по очереди.

   Функция `virtio_flag_chr` возвращает по оффсету один символ — судя по ограничениям, это число от 0 до 80 (размера массива `data`). Этих знаний нам достаточно — мы можем скопировать эту функцию целиком и просто запустить в цикле для всех оффсетов.

   Нужно лишь аккуратно понять изначальное значение переменной `forty` — она инициализируется при каждом открытии файла в значение `0x4b - 0x04 = 0x47`.

   [Пример программы](dev/virtio_flag_us.c)

Флаг: **ugra_[please_burn_that_patch_in_the_darkest_pits_of_hell](https://lore.kernel.org/lkml/CAHk-=whogEk1UJfU3E7aW18PDYRbdAzXta5J0ECg=CB5=sCe7g@mail.gmail.com/)_qez9peqhcqpi3xif7kikza0u**

----

## Постмортем

Уже 9 марта мы обнаружили, что в трёх строках номера отличаются на единицу. Ошибка была в нашем генераторе — он выдавал строки для подстановки во фразу «После строки N». При проверке действительно ошибка возникла при прогоне авторского решения, но мы подумали, что проблема в решении, а не в генераторе.

В любом случае, поскольку строка с длинными последовательностями байт в коде одна, корректное место вставки вычислялось тривиально, и эта ошибка не оказала существенного влияния на ход решения.

В репозитории все ошибки и в генераторе, и в решении исправлены; но мы приняли решение не заменять файлы участников на корректные.
