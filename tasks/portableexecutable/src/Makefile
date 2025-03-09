# llvm >= 20 is required to support /stub:...
# https://github.com/llvm/llvm-project/commit/fb974e89095af01a15cf959ba0694c0beb404b9f

all: main.exe

stub.exe: stub.asm
	nasm -fbin -ostub.exe stub.asm

main.o: main.c
	clang -target x86_64-pc-windows-gnu -DUNICODE -D_UNICODE -I/usr/lib/zig/libc/include/any-windows-any \
		-fno-ident -fno-stack-protector -fomit-frame-pointer -fno-unwind-tables -fno-asynchronous-unwind-tables \
		-falign-functions=1 -falign-loops=1 -Wno-macro-redefined -Wno-missing-declarations -Wno-pragma-pack \
		-O3 -c -o main.o main.c

main.exe: main.o stub.exe
	test $(shell lld-link --version | cut -d' ' -f2 | cut -d. -f1) -ge 20
	lld-link /machine:x64 /subsystem:console /nodefaultlib /align:16 /filealign:16 /usr/lib/wine/x86_64-windows/libkernel32.a /stub:stub.exe /entry:_start /out:main.exe main.o
