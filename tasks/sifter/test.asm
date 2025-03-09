hello:          ; at 00h
    mov b a     ; 01
    add c b     ; 16
    xor d c     ; 2b
    and d a     ; 33
    ldr a a     ; 40
    str b b     ; 55
    cmp b a     ; 61
    or  b a     ; 71

    imm a 10h   ; 80 10
    neg b       ; 85
    com c       ; 8a
    shl d 4h    ; 8f 04

    in  a       ; 90
    out d       ; 97
offset:         ; at 10h
    tst a       ; 98
    rbt d       ; 9f

    shr a 4h    ; a0 04
    sar a 4h    ; a4 04
    rol a 4h    ; a8 04
    ror a 4h    ; ac 04

    jmp hello   ; b0 00
    jl  offset  ; b1 10
    jbe 20h     ; b2 20
    jle 30h     ; b3 30
    jz  40h     ; b4 40
    js  50h     ; b5 50
    jc  60h     ; b6 60
    jo  70h     ; b7 70

    j0  80h     ; b8 80
    jge 90h     ; b9 90
    ja  a0h     ; ba a0
    jg  b0h     ; bb b0
    jnz c0h     ; bc c0
    jns d0h     ; bd d0
    jnc e0h     ; be e0
    jno f0h     ; bf f0

    nop         ; 00
    inc a       ; c0
    dec d       ; c7
    ud2         ; cc
    hlt         ; ff
