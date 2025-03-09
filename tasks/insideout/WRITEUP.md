# Наизнанку: Write-up

Отлично, 300 килобайт какого-то EXE-шника. Чего же туда напихали?

```shell
$ wine flag.exe
??h?e? ?f?l?a?g? ?i?s? ?h?i?d?d?e?n? ?s?o?m?e?w?h?e?r?e?
?
```

А, да, винда же использует UTF-16, а не UTF-8. Ошибочка.

```shell
$ wine ./flag.exe | iconv -f utf16 -t utf8
The flag is hidden somewhere
```

Ничего нового, мы это и так знали. Посмотрим, чем набили этот бинарь. Проще всего это сделать с помощью некоторых архиваторов, например, [7-Zip](https://www.7-zip.org/):

```shell
$ 7z l flag.exe

7-Zip 24.09 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-11-29
 64-bit locale=en_US.UTF-8 Threads:4 OPEN_MAX:1024, ASM

Scanning the drive for archives:
1 file, 323072 bytes (316 KiB)

Listing archive: flag.exe

--
Path = flag.exe
Type = PE
Physical Size = 323072
CPU = x64
64-bit = +
Characteristics = Executable LargeAddress
Created = 2025-03-08 07:10:28
Headers Size = 1024
Checksum = 0
Image Size = 339968
Section Alignment = 4096
File Alignment = 512
Code Size = 512
Initialized Data Size = 321536
Uninitialized Data Size = 0
Linker Version = 14.0
OS Version = 6.0
Image Version = 0.0
Subsystem Version = 6.0
Subsystem = Windows CUI
DLL Characteristics = HighEntropyVA Relocated NX-Compatible TerminalServerAware
Stack Reserve = 16777216
Stack Commit = 4096
Heap Reserve = 1048576
Heap Commit = 4096
Virtual Address = 0x400000
Comment = 
{

Data Directories: 16
{
index=1 name=IMPORT VA=0x2020 Size=60
index=2 name=RESOURCE VA=0x4000 Size=320528
index=12 name=IAT VA=0x2090 Size=48
}
}

   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2025-03-08 07:10:28 .....          155          512  .text
2025-03-08 07:10:28 .....          272          512  .rdata
2025-03-08 07:10:28 .....            0            0  .data
                    .....          172          172  .rsrc/string.txt
                    .....       315654       315640  .rsrc/BITMAP/124.bmp
                    .....         4314         4292  .rsrc/ICON/1.ico
                    .....           20           20  .rsrc/GROUP_ICON/20
------------------- ----- ------------ ------------  ------------------------
2025-03-08 07:10:28             320587       321148  7 files
```

Отлично, есть какие-то ресурсы. Посмотрим, что в них:

- `124.bmp` — картинка-рикролл с википедии
- [`1.ico`](./src/icon.ico) — иконка флага, нарисованная на скорую руку
- `20` — не особо понятно, что это, но связано с иконкой
- `string.txt` — файл со строками, содержимое:

```
100 ugra_windows_resources_are_simple_bme9n9r1rhnpyalpnmli01yk
256 hidden somewhere
```

Вот и флаг. Можно было ещё пореверсить `.text` и понять, что забирается ресурс `0x100`, а не `100` — из-за чего программа выдаёт не `The flag is ugra...`, а `The flag is hidden somewhere`.

Флаг: `ugra_windows_resources_are_simple_bme9n9r1rhnpyalpnmli01yk`

> Почитайте также райтап на [Portable executable](../portableexecutable/).
