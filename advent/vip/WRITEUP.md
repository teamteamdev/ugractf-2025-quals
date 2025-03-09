# Про, Макс: Write-up

Сельский клуб когда-то давно [распространял инвитики](https://github.com/teamteamdev/ugractf-2021-quals/tree/master/tasks/thevillage). Затем что-то поменялось, клуб развалился, потом был гологизирован согласно легенде, описанной в телеграм-канале [@teamteam](https://t.me/teamteam), но это история сложная и в целом не имеющая почти никакого отношения к сути данного задания.

Перед нами полный, что называется, рефреш Сельского клуба: и, как это часто бывает, новое ничего общего со старым не имеет, кроме, может быть, названия.

Взглянем на то, что нам дают.

Дают скрипт с расширением `.jl`. Он составлен на языке программирования Julia, известном в основном в кругах программирующих учёных: физиков, математиков, тарологов и экономистов. Язык Julia выбирают за то, что она быстра как Си и элегантна как Питон.

Установим интерпретатор `julia` и запустим скрипт в нём:
```
$ julia VIP-KUPONCHIK.jl
                                 (C) Author rights protected.
                         TheVillage (OOO), AGS Elite (Agrokekstroy JSC).

    V       V   ii   PPPP
     V     V    ii   P   P
      V   V     ii   PPPP
       V V      ii   P
        V       ii   P

      ViP - K U P O N C H I Q U E
         for entrancing
        the PRIVATE club
      <<THE VILLAGE PRO MAX>>

     POZDRAVL'AEM VI PRIGLASHENY NA VE4NUU VECHERINKU

    N ADO LISH ZAPUSTIT ETOT KUPON V VASHEM RABOCHEM PK.

     1. ECLI HE PA6OTAET, TO OT UMENU ADMINISTRATORA.
     2. ECLI HE PA6OTAET POTOM TO}|{E, YCTAHOBUTE XZ.
     3. ZATEM VVEDITE PAROLCHIK NA KYPOH4IK ....


INSIDE PAROLchik u [ENTER] >
```

Опа. Парольчик. Наугад введённый не подходит. Приплыли. Придётся читать [код](attachments/VIP-KUPONCHIK.jl). Помните тезис об элегантности Питона при быстроте Си? К сожалению, в этом скрипте получился антитезис: читать *это* невозможно.

Программа устроена так:

1. Объявляют пять переменных `CALL_N`, N от 1 до 5.
2. Объявляют ещё переменных, суть которых никогда не станет ясна.
3. Считывают парольчик у пользователя.
4. Делают `GC.@preserve ... @ccall ... CALL_N` (???) несколько раз.
5. Результаты как-то с чем-то сравниваются.
6. Пароль расшифровывается с помощью операции `key .⨷ res |> String |> println` (какой кошмар).

Если понять, что такое `@ccall`, то есть, куда звонит программа, понять идею автора будет намного проще.

Просто выполним релевантные куски кода в интерпретаторе Julia и посмотрим, что к чему. Удобнее закомментировать вызовы `exit()` на строках 123 и 128.

Итак:
```
julia> include("VIP-KUPONCHIK.jl")
    [...]
julia> VILLAGE_SMART_KUPON.CALL_1
"lzma_stream_buffer_bound"
julia> VILLAGE_SMART_KUPON.CALL_2
"lzma_easy_buffer_encode"
julia> VILLAGE_SMART_KUPON.CALL_3
"lzma_auto_decoder"
julia> VILLAGE_SMART_KUPON.CALL_4
"lzma_code"
julia> VILLAGE_SMART_KUPON.CALL_5
"lzma_end"
```

Звонят в `xz`! Это архиватор. Что-то разархивируется, сравнивается с чем-то, и потом распаковывается автоматическим декодером. Попробуем распаковать то, с чем сравнивают код. Похоже, что это значение переменной `ID`, потому что оно очень большое и участвует в этом сравнении:
``` julia
# [...]
    # пустой массив
    tip                                          =  Vector{UInt8}()
    # res — упакованный пользовательский ввод
    append!(tip, res...)
    # key — не ключ! согласно Гуглу, это стандартная шапка LZMA-архива
    append!(tip, key...)
    # ID — тело архива
    append!(tip, ID... )
    # tip должен быть чётной длины: подразумевается, что длина res совпадает с длиной key + ID
    length(tip) & 1 == 0 || begin @error("UNFORTUNATELY NOT 2X AND YOU WRONG.") end
end

# outl — длина архива res, а это какие-то опорные точки в tip
(lxb, lya, lyb)                                  = (outl[], outl[] + 1, outl[] * 2)
# первая половина tip: res
cx                                               = tip[begin:lxb]
# вторая половина tip: key + ID
cy                                               = tip[lya:lyb]
# они должны быть равны:
cx - cy |> sum |> iszero || begin @error("UNFORTUNATELY YOU TRIED AND WRONG. NOT TRY, JUST DO!") end
```

Элегантно? Возможно. Не важно. Бежим распаковывать `key + ID`. Получится вот что:

`----VIP-PAROLCHIK-2505411-premium-plus-----000000000000000000000000000000000000000000...`

Парольчик надо отрезать от нолей, потому что скрипт добавляет их сам (`*` конкатенирует строки):
```julia
inpb = *(begin print("INSIDE PAROLchik u [ENTER] > "); readline() end,
         ['0' for _ ∈ 1:100] |> String
```

Дальше можно просто ввести парольчик в программу, чтобы она сама расшифровала ключ.

А можно раскукожить флаг самостоятельно. Помните переменную `key`? Это ключ. И ещё это шапка архива. Как так? Где-то в середине скрипта переменная просто полностью переопределяется. Полностью. Вообще другим массивом других байтов. И смысл у них другой. Была шапка архива — стал ключ от флага. Как так? Ну вот так:
```julia
key = [0x58, 0x4a, 0x5f, 0x4c, 0x09, 0x24, 0x35, 0x5e, 0x23, 0x0d, ...
```

А что за цепочка преобразований? `key .⨷ res |> String |> println`. Запись с оператором `|>` эквивалентна такой записи: `println(String((key .⨷ res)))`, а оператор `⨷` определён в самом начале:
```julia
⨷(x::CT, y::CT) = convert(UInt128, x) ⊻ convert(UInt128, y) |> Char
```

Вопрос напрашивается сам: что за `⊻`!?

```
help?> ⊻
"⊻" can be typed by \xor<tab>

search: ⊻

  xor(x, y)
  ⊻(x, y)

  Bitwise exclusive or of x and y. Implements three-valued logic (https://en.wikipedia.org/wiki/Three-valued_logic), returning missing if one of the arguments is missing.
```

Ясно.

Ксорим.

Флаг: **ugra_mess_with_the_best_stick_to_the_rest_fafe9832**
