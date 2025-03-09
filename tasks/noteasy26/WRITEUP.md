# noteasy26: Write-up

Как и в [noteasy](https://github.com/teamteamdev/ugractf-2019-quals/tree/master/tasks/noteasy), [noteasy₅](https://github.com/teamteamdev/ugractf-2020-quals/tree/master/tasks/noteasy5), [noteasy+82](https://github.com/teamteamdev/ugractf-2021-quals/tree/master/tasks/noteasy82) и [noteasy03](https://github.com/teamteamdev/ugractf-2022-quals/tree/master/tasks/noteasy03), мы имеем дело с флагом, который зашифрован шифром простой замены. Кроме флага, не дано по сути ничего:

```
rpef_ogznuxkbq_fvsxetfebfm_bylxeyflbnyfmbwflbny_crftbifh_jfqdabext_wufceghdeuvdggab
```

26 — количество букв английского алфавита, все они представлены в шифровке (а значит, все будут во флаге). Попробуем распутать.

Будем обозначать заглавными буквами то, что мы уже расшифровали. С началом всё понятно — это гарантированный префикс `ugra_`:

```bash
$ tr rpef UGRA < noteasy26.txt 
UGRA_ogznuxkbq_AvsxRtARbAm_bylxRyAlbnyAmbwAlbny_cUAtbiAh_jAqdabRxt_wuAcRghdRuvdggab
```

Мы знаем, что флаги обычно содержат слова английского языка. [Поищем](https://www.google.com/search?q=dictionary+of+english+words+github) словарь пожирнее — и скачаем его:

```bash
$ wget https://github.com/dwyl/english-words/raw/refs/heads/master/words_alpha.txt
```

Начнём с самого длинного слова в середине. Позиции некоторых букв мы уже знаем достоверно. Поищем подходящие слова в списке:

```bash
$ grep ....r.a....a...a.... < words_alpha.txt 
internationalisation
internationalization
internationalizations
```

Проверяем: действительно вторая буква совпадает с последней, третья с начала — с четвёртой с конца, и так далее. Подходят оба варианта — с `s` и с `z` в середине, поэтому эту букву пока оставим под вопросом.

```bash
$ tr rpef_bylxeyflbnyfmb_flbny UGRA_INTERNATIONALI_ATION < noteasy26.txt 
UGRA_ogzOuEkIq_AvsERtARIAL_INTERNATIONALIwATION_cUAtIiAh_jAqdaIREt_wuAcRghdRuvdggaI
```

Второе слово вырисовалось почти полностью. Ещё один поход в словарь:

```bash
$ grep a..er.arial < words_alpha.txt
adversarial

$ tr rpef_bylxeyflbnyfmb_flbny_fvsxetfebfm UGRA_INTERNATIONALI_ATION_ADVERSARIAL < noteasy26.txt 
UGRA_ogzOuEkIq_ADVERSARIAL_INTERNATIONALIwATION_cUASIiAh_jAqdaIRES_wuAcRghdRuDdggaI
```

Для оставшихся слов воспользуемся свойством шифра простой замены: те буквы, которые мы уже нашли, не могут встретиться нам повторно. На данный момент среди расшифрованных у нас нет букв `B`, `C`, `F`, `H`, `J`, `K`, `M`, `P`, `Q`, `W`, `X`, `Y`, `Z`.

```bash
$ grep '[bcfhjkmpqwxyz][bcfhjkmpqwxyz][bcfhjkmpqwxyz]o[bcfhjkmpqwxyz]e[bcfhjkmpqwxyz]i[bcfhjkmpqwxyz]' < words_alpha.txt 
hypoxemic

$ tr rpef_bylxeyflbnyfmb_flbny_fvsxetfebfm_ogznuxkbq UGRA_INTERNATIONALI_ATION_ADVERSARIAL_HYPOXEMIC < noteasy26.txt 
UGRA_HYPOXEMIC_ADVERSARIAL_INTERNATIONALIwATION_cUASIiAh_jACdaIRES_wXAcRYhdRXDdYYaI
```

Остались `B`, `F`, `J`, `K`, `Q`, `W`, `Z`:

```bash
$ grep '[bfjkqwz]ac[bfjkqwz][bfjkqwz]ires' < words_alpha.txt 
backfires

UGRA_HYPOXEMIC_ADVERSARIAL_INTERNATIONALIwATION_cUASIiAh_BACKFIRES_wXAcRYhKRXDKYYFI
```

Про букву в слове `INTERNATIONALI.ATION` понимаем, что это `Z`, а не `S`, потому что `S` уже есть в других местах.

Остались `J`, `Q`, `W` и слово `.UASI.A.`, которое в словарях не находится. Переберём все варианты:

```
JUASIQAW
JUASIWAQ
QUASIJAW
QUASIWAJ
WUASIJAQ
WUASIQAJ
```

Сколько-нибудь осмысленным из них является только слово `QUASIJAW` (_квазичелюсть_; его нет в словаре, но оно даже [один раз встречается](https://google.com/search?q=quasijaw) в интернете!).

Осталось получить ответ.

```
$ tr rpef_bylxeyflbnyfmbwflbny_fvsxetfebfm_ogznuxkbq_jfqdabext_crftbifh UGRA_INTERNATIONALIZATION_ADVERSARIAL_HYPOXEMIC_BACKFIRES_QUASIJAW < noteasy26.txt | tr A-Z a-z
ugra_hypoxemic_adversarial_internationalization_quasijaw_backfires_zxaqrywkrxdkyyfi
```

Флаг: **ugra_hypoxemic_adversarial_internationalization_quasijaw_backfires_zxaqrywkrxdkyyfi**
