%include "exebin.mac"

    EXE_begin
    EXE_stack 64

    section .text

    push cs
    pop ds

    mov dx, message
    mov ah, 9
    int 0x21
    jmp forward

    nop

message db "This program cannot be run in DOS mode.", 0x0d, 0x0d, 0x0a, '$'

forward:
    mov cx, 48
    mov bp, flag

print_one:
    mov dl, [bp]
    xor dl, 0x80
    mov ah, 6
    int 0x21
    inc bp
    loop print_one

    mov ax, 0x4c00
    int 0x21

    section .data

flag: ; replace CC..CC with flag^0x80
    times 48 db 0CCh

    EXE_end
