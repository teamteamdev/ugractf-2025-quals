# 行くよ: Write-up

![](./writeup/mojibake.png)

Офигенно. Скачиваем файл утилитой `curl` и смотрим в hex-виде, что же туда положили.

![](./writeup/hexdump.png)

Ага, файл начинается с `ef bb bf` (UTF-8 BOM), в `<meta>` файл говорит, что это UTF-8, в `<title>` и в начале `<body>` совпадает текст побайтово и записан тоже в UTF-8, а дальше начинаются кракозябры. Аккуратно выдираем только часть с кракозябрами (начиная `0xca` размером `0x9b` байт) и идём перебирать кодировку.

Брутить можно чем угодно — [glibc'шным iconv](https://www.gnu.org/software/libc/manual/html_node/glibc-iconv-Implementation.html), [ICU'шным uconv](http://www.uconv.com/), chromium'ом, Word'ом, [Cyber Chef'ом](https://gchq.github.io/CyberChef/)... Самый простой в написании для знакомых с шеллом — `uconv`:

```bash
for source in $(uconv -l | cut -d' ' -f1); do uconv -f $source -t utf8 /tmp/mojibake 2>/dev/null; echo; done | less
```

в одной из них будет флаг широкими символами

```
ｕｇｒａ＿ｓｈｉｆｔ＿ｊｉｓ＿ｉｓ＿ｂｅｔｔｅｒ＿ｔｈａｎ＿ｕｎｉｃｏｄｅ＿ｄｏｎｔ＿ｙｏｕ＿ｔｈｉｎｋ＿２ｑｈ３ｃ３ｎｚｐｐｎ４ｉｗ０２ｙ７５６１ｒｓｆ
```

Аккуратно перепечатываем и сдаём.

Флаг: **ugra_shift_jis_is_better_than_unicode_dont_you_think_2qh3c3nzppn4iw02y7561rsf**

## Интересные факты

Кракозябры в английском языке называют [Mojibake](https://en.wikipedia.org/wiki/Mojibake) — так их называют в Японии.
