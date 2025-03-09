# forked: Write-up

Подключаемся и нас встречает знакомый до боли busybox:
```shell
$ nc forked.q.2025.ugractf.ru 3254
Enter token: b7zyeh9l79sulrew
/bin/sh: can't access tty; job control turned off
/ $
```

Пробуем что-то сделать:

```shell
/ $ ls
/bin/sh: ls: not found
/ $ ps
/bin/sh: ps: not found
/ $ cat 
/bin/sh: cat: not found
```

Хорошее начало. А что вообще есть? Может хоть `/bin/sh`?

```shell
/ $ sh
/bin/sh: can't fork: Resource temporarily unavailable
```

Ну почти. Он-то есть (и есть только он), и вызвать ничего не можем — то файлов нет, то процессы кончились. Что вообще можно из этой ситуации сделать? Попросить о помощи.

```shell
/ $ help
Built-in commands:
------------------
    . : [ [[ alias bg break cd chdir command continue echo eval exec
    exit export false fg getopts hash help history jobs kill let
    local printf pwd read readonly return set shift source test times
    trap true type ulimit umask unalias unset wait
```

Хорошо, у нас есть билтины. Их немного, но этого хватит — на целых три решения!

## Вариант 1. Chaotic

Бизибокс, значит? Он славится тем, что является multi-call binary, и определяет, какой именно апплет запускать по `argv[0]`. Но как запускать хоть что-то, если подпроцессы создавать нельзя?

Вспомним, что в шеллах есть builtin `exec`, который позволяет заменять текущий процесс на другой, а не создавать новый. Посмотрим как им пользоваться в bash, шелле, который послужил вдохновением для busybox-ового:

```shell
$ help exec
exec: exec [-cl] [-a name] [command [argument ...]] [redirection ...]
    Replace the shell with the given command.
    
    Execute COMMAND, replacing this shell with the specified program.
    ARGUMENTS become the arguments to COMMAND.  If COMMAND is not specified,
    any redirections take effect in the current shell.
    
    Options:
      -a name   pass NAME as the zeroth argument to COMMAND
      -c    execute COMMAND with an empty environment
      -l    place a dash in the zeroth argument to COMMAND
    
    If the command cannot be executed, a non-interactive shell exits, unless
    the shell option `execfail' is set.
    
    Exit Status:
    Returns success unless COMMAND is not found or a redirection error occurs.
```

Билтину `exec` можно подать аргумент `-a`, и он выставит `argv[0]` в нужное значение. В busybox эта фича [поддерживается](https://elixir.bootlin.com/busybox/1.37.0/source/shell/ash.c#L10070) (можно не искать исходники, а просто проверить в контейнере с [Alpine Linux](https://hub.docker.com/_/alpine)).

Откуда взять бинарь? Из ошибок выше понятно, что можно использовать `/bin/sh`, но если хочется наверняка — `/proc/self/exe`.

Поверим, что из него не выпилили апплетов, и пойдём исследовать файловую систему.

```
/ $ exec -a tree /proc/self/exe /
/
├── bin
│   └── sh
├── dev
│   ├── core -> /proc/kcore
│   ├── fd -> /proc/self/fd
│   ├── full
│   ├── mqueue
│   ├── null
│   ├── ptmx -> pts/ptmx
│   ├── pts
│   │   └── ptmx
│   ├── random
│   ├── shm
│   ├── stderr -> /proc/self/fd/2
│   ├── stdin -> /proc/self/fd/0
│   ├── stdout -> /proc/self/fd/1
│   ├── tty
│   ├── urandom
│   └── zero
├── etc
│   ├── hostname
│   └── hosts
├── flag-RS5Rk1gLiQZns6dVSROnoEiO.txt
...
```

Отлично, теперь прочитаем флаг:

```shell
/ $ exec -a cat /proc/self/exe /flag*.txt
ugra_you_really_can_live_without_fork_7n75adhpdjek
```

## Варианты 2 и 3: Neutral и Lawful

Вспоминаем, что шелл умеет раскрывать [glob-ы](https://tldp.org/LDP/abs/html/globbingref.html):

```shell
/ $ echo /*
/bin /dev /etc /flag-RS5Rk1gLiQZns6dVSROnoEiO.txt /lib /proc
/ $ echo /*/
/bin/ /dev/ /etc/ /lib/ /proc/
```

О, а вот и файл с флагом. Как его прочитать?

### Neutral
```shell
/ $ source /flag*.txt
/bin/sh: /flag-RS5Rk1gLiQZns6dVSROnoEiO.txt: line 1: ugra_you_really_can_live_without_fork_7n75adhpdjek: not found
```

### Lawful
```shell
/ $ read flag </flag-RS5Rk1gLiQZns6dVSROnoEiO.txt
/ $ echo $flag
ugra_you_really_can_live_without_fork_7n75adhpdjek
```

Флаг: **ugra_you_really_can_live_without_fork_7n75adhpdjek**

## Интересные факты

Если вдруг окажетесь в ситуации, когда подпроцессы создавать нельзя, да и `execve` делать тоже не хочется, а потыкать систему желание есть, держите мои forkless builtins под [Unlicense](https://spdx.org/licenses/Unlicense.html).

```shell
ls() { echo "$1"*; }
cat() { while read line; do printf "%s\n" "$line"; done; printf "%s" "$line"; }
cat0() { while read -d '' line; do printf "%s\t" "$line"; done; printf "%s\n" "$line"; }
ps() { for fn in /proc/*/; do case $fn in /proc/[0-9]*/) echo $fn; cat0 <$fn/cmdline; cat0 <$fn/environ; echo ;; esac done; }
```

## Постмортем

Файл с флагом не содержит `\n` в конце, поэтому реализация `cat` через

```shell
cat() { while read line; do printf "%s\n" "$line"; done; }
```

не является корректной. Исправленная версия выглядит так:

```shell
cat() { while read line; do printf "%s\n" "$line"; done; printf "%s" "$line"; }
```
