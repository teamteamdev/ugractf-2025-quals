all: main.exe

resource.res: resource.rc
	zig rc /dUNICODE /d_UNICODE $^ $@

main.exe: main.c resource.res
	zig cc \
		-target x86_64-windows-gnu \
		-DUNICODE \
		-D_UNICODE \
		-nostdinc \
		-I /usr/lib/zig/libc/include/any-windows-any \
		-nostdlib \
		-nodefaultlibs \
		-Wl,/subsystem:console \
		-luser32 \
		-lkernel32 \
		-fno-ident \
		-fno-stack-protector \
		-fomit-frame-pointer \
		-fno-unwind-tables \
		-fno-asynchronous-unwind-tables \
		-falign-functions=1 \
		-falign-loops=1 \
		-Wno-macro-redefined \
		-Wno-missing-declarations \
		-s \
		-O3 \
		-flto=fat \
		-o $@ \
		$^
