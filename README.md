# Ugra CTF Quals 2025

8–9 марта 2025 | [Сайт](https://2025.ugractf.ru/) | [Результаты](SCOREBOARD.md)

## Разогревочные таски

В этом году каждый день перед Quals участники решали разогревочные задания и открывали [юбилейную планету югорских приколов](https://2025.ugractf.ru).

[Брайль](advent/dots/) (purplesyringa, misc)  
[Вращайте барабан!](advent/wheel/) (nsychev, misc)  
[Огни погони в городе](advent/racelights/) (nsychev, osint)  
[AAAAAA](advent/aaaaaa/) (sylfn, crypto)  
[Конструктор](advent/constructor/) (purplesyringa, web)  
[Про, Макс](advent/vip/) (ksixty, reverse)  
[ad lib](advent/adlib/) (ksixty, stegano)  
[Телеграфный перевод](advent/wiretransfer/) (purplesyringa, crypto)  
[Котёнок!](advent/kitty/) (sylfn, stegano)  
[行くよ](advent/ikuyo/) (sylfn, misc)

## Таски

[Вещает, видимо](tasks/apparentcast/) (enhydra, forensics 150)  
[Сервер с бородой](tasks/beardbox/) (enhydra, osint 300)  
[Коробкошка](tasks/boxcat/) (purplesyringa, crypto 250)  
[Кошкоробка](tasks/catbox/) (purplesyringa, misc 100)  
[CraftCraft](tasks/craftcraft/) (purplesyringa, ppc 300)  
[forked](tasks/forked/) (sylfn, admin 150)  
[Постановление](tasks/gosdiff/) (nsychev, ppc 150)  
[Решётка](tasks/grille/) (nsychev, crypto 100)  
[hypertext](tasks/hypertext/) (sylfn, ctb 200)  
[наизнанку](tasks/insideout/) (sylfn, forensics 100)  
[Но обещал вернуться](tasks/jetlagged/) (enhydra, osint 100)  
[Последний шанс](tasks/lastchance/) (sylfn, stegano 100)  
[Прачечная](tasks/laundromat/) (purplesyringa, reverse 400)  
[/locate](tasks/locate/) (purplesyringa, osint 200)  
[Medium rare](tasks/mediumrare/) (purplesyringa, web 250)  
[noteasy26](tasks/noteasy26/) (enhydra, crypto 100)  
[Санэпидемстанция](tasks/pestcontrol/) (baksist, web 100)  
[portable executable](tasks/portableexecutable/) (sylfn, reverse 100)  
[PNG](tasks/portablegraphics/) (purplesyringa, forensics 250)  
[SecuSafe](tasks/secusafe/) (rozetkinrobot, reverse 300)  
[Просеиватель](tasks/sifter/) (sylfn, reverse 400)  
[тишина](tasks/silence/) (sylfn, ppc 200)  
[Летнее чтение](tasks/summerreading/) (purplesyringa, web 100)  
[Yankbox](tasks/yankbox/) (sylfn, ctb 100)  
[Жужелица](tasks/zhuzhelitsa/) (purplesyringa, crypto 150)  
[Жужелица 2](tasks/zhuzhelitsa2/) (purplesyringa, crypto 300)  
[Зоопарк](tasks/zoo/) (rozetkinrobot, web 150)

## Команда разработки

Олимпиада была подготовлена командой [team Team].

[Никита Сычев](https://github.com/nsychev) — руководитель команды, разработчик тасков и системы регистрации  
[Калан Абе](https://github.com/kalan) — разработчик тасков  
[Коля Амиантов](https://github.com/abbradar) — инженер по надёжности  
[Ваня Клименко](https://github.com/ksixty) — разработчик тасков  
[Матвей Сердюков](https://github.com/baksist) — разработчик тасков  
[Алиса Сиренева](https://github.com/purplesyringa) — разработчица тасков и платформы  
[Юлия Сиренева](https://github.com/yuki0iq) — разработчица тасков  
[Евгений Черевацкий](https://github.com/rozetkinrobot) — разработчик тасков  
[Катя Ковальчук](https://behance.net/nclbrt) — иллюстратор

## Организаторы

Организаторы Ugra CTF — Югорский НИИ информационных технологий, Департамент информационных технологий и цифрового развития ХМАО–Югры, Департамент образования и науки ХМАО–Югры и команда [team Team].

## Генерация заданий

Некоторые таски создаются динамически — у каждого участника своя, уникальная версия задания. В таких заданиях вам необходимо запустить генератор. Путь к нему доступен в конфигурации таска — YAML-файле — в параметре `generator`.

Генератор запускается из директории задания и принимает три аргумента — уникальный идентификатор участника, директорию для сохранения файлов для участника и названия генерируемых тасков. Например, так:

```bash
export KYZYLBORDA_TMPDIR=/tmp
../_scripts/kyzylborda-lib-generator 12345 attachments beardbox
```

Уникальный идентификатор используется для инициализации генератора псевдослучайных чисел, если такой используется. Благодаря этому, повторные запуски генератора выдают одну и ту же версию задания.

Генератор выведет на стандартный поток вывода JSON-объект, содержащий флаг к заданию и информацию для участника, а в директории `attachments` появятся вложения, если они есть.

## Лицензия

Материалы соревнования можно использовать для тренировок, сборов и других личных целей, но запрещено использовать на своих соревнованиях. Подробнее — [в лицензии](LICENSE).
