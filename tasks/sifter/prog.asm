imm a pass
imm b pass_end
prompt:
ldr c a
out c
inc a
cmp a b
jnz prompt

imm a pass+8
input:
in c
str a c
inc a
cmp a b
jnz input
imm a 0ah
out a

; clone password to [pass; pass+8) reversed
; a = pass      --> pass + 8
; b = pass + 16 --> pass + 8
imm a pass
copy:
dec b
ldr c b
str a c
inc a
cmp a b
jnz copy

; password is [pass; b=pass+8)
shuffle:
    dec b   ; b = 7
    ldr a b ; a = *7
    neg a
    dec b   ; b = 6
    ldr c b ; c = *6
    dec c
    dec b   ; b = 5
    ldr d b ; d = *5
    rol d 5h
    add d a ; d = *5 + *7
    str b d ; *5 = d       ; *5 += *7
    dec b   ; b = 4
    dec b   ; b = 3
    ldr a b ; a = *3
    com a
    xor a d ; a = *3 ^ *5
    str b a ; *3 = a       ; *3 ^= *5
    dec b   ; b = 2
    dec b   ; b = 1
    ldr d b ; d = *1
    ror d 2h
    add d c ; d = *1 + *6
    str b d ; *1 = d       ; *1 += *6
    dec b   ; b = 0
    ldr c b ; c = *0
    rbt c
    xor c a ; c = *0 ^ *3
    str b c ; *0 = c       ; *0 ^= *3

    inc b   ; b = 1
    ldr a b ; a = *1
    inc b   ; b = 2
    ldr d b ; d = *2
    rol d 7h
    xor d c ; d = *2 ^ *0
    str b d ; *2 = d       ; *2 ^= *0
    inc b   ; b = 3
    ldr c b ; c = *3
    inc c
    add c a ; c = *3 + *1
    str b c ; *3 = c       ; *3 += *1
    inc b   ; b = 4
    ldr c b ; c = *4
    rbt c
    xor c a ; c = *4 ^ *1
    str b c ; *4 = c       ; *4 ^= *1
    inc b   ; b = 5
    ldr c b ; c = *5
    dec c
    inc b   ; b = 6
    ldr a b ; a = *6
    com a
    add a c ; a = *6 + *5
    str b a ; *6 = a       ; *6 += *5
    inc b   ; b = 7
    ldr a b ; a = *7
    xor a d ; a = *7 ^ *2
    str b a ; *7 = a       ; *7 ^= *2
    inc b   ; b = 8

imm d shuffle_count
ldr c d
dec c
str d c
tst c
jnz shuffle

; [a=ok; ok_end) correct
; [pass; b=pass+8) shuffled
; [pass+8; pass_end) original

imm a ok
check:
dec b
ldr d b
ldr c a
inc a
cmp c d
imm d wrong
jnz final
cmp a b
jnz check

part:
    ; prepare [pass+8; pass_end) password
    imm a pass_end-1
    ldr a a

    imm b pass+8
    imm d 04h
    pass_part:
        ldr c b
        xor a c
        rol a 03h
        str b a
        inc b

        ldr c b
        add a c
        neg a
        str b a
        inc b

        dec d
        tst d
        jnz pass_part

    ; [a-8; a) ^= [pass+8; b=pass_end)
    imm a flag_ptr
    ldr a a
    imm b pass_end
    xor_loop:
        dec a
        ldr c a
        dec b
        ldr d b
        xor c d
        str a c
        imm d pass+8
        cmp b d
        jnz xor_loop

    imm d flag_ptr
    str d a

imm d flag
cmp a d
jnz part
jmp final

ok:
db b1h
db dah
db c5h
db d5h
db 9ch
db 50h
db 26h
db 2ch
ok_end:

pass:
.ascii "Enter password: "
pass_end:

wrong:
.ascii "Forbidden.\n\0"

flag:
; ugra_placeholder_for_flagg_0123456789AB.
; .ascii "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
db 212
db 124
db 231
db 140
db 57
db 32
db 69
db 57
db 24
db 176
db 128
db 141
db 171
db 167
db 136
db 130
db 245
db 56
db 160
db 243
db 248
db 174
db 182
db 246
db 234
db 211
db 44
db 109
db 236
db 90
db 120
db 84
db 105
db 67
db 86
db 103
db 240
db 186
db 85
db 52
db 90
db 84
db 137
db 67
db 121
db 86
db 16
db 119
flag_end:
shuffle_count:
db 04h ; will become 00h when `flag` is read

flag_ptr:
db flag_end

final_start:
out a
inc d
final: ; nul-terminated at `d`
ldr a d
tst a
jnz final_start
imm b ffh
str a b
