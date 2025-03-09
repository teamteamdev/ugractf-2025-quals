#include <stdbool.h>
#include <stdio.h>
#include <sys/types.h>

#define N \
	5
const char data[] = {
	'\x26', '\x32', '\x20', '\x35', '\x18', '\x3f', '\x2e', '\x32', '\x3b', '\x2d', '\x00', '\x10', '\x2a', '\x17', '\x07', '\xe4', '\xe2', '\xd3', '\xf8', '\xed','\xc2', '\xd7', '\xfc', '\xd3', '\xd7', '\xd3', '\xd9', '\xd2', '\xe5', '\xd4', '\xb4', '\x8e', '\xa5', '\xb9', '\x8e', '\x83', '\x8c', '\x89', '\x9a', '\x8d','\x8f', '\x8c', '\x8b', '\xa0', '\x96', '\x79', '\x62', '\x65', '\x49', '\x70', '\x41', '\x72', '\x45', '\x48', '\x41', '\x76', '\x1b', '\x74', '\x75', '\x77','\x6c', '\x6f', '\x6e', '\x6d', '\x63', '\x40', '\x4b', '\x42', '\x43', '\x41', '\xbe', '\xbd', '\xbc', '\xbf', '\xb1', '\x92', '\x99', '\x90', '\x91', '\x93',
};
static char forty = 0x47;

char virtio_flag_chr(loff_t buffer)
{
	bool amend = false;
	if (buffer < 0 || buffer >= sizeof(data))
	{
		return 0;
	}
	if (buffer % N == 0)
	{
		buffer += 1;
	}
	else if (buffer % N == 1)
	{
		buffer += 1;
	}
	else if (buffer % N == 2)
	{
		buffer += 1;
	}
	else if (buffer % N == 3)
	{
		buffer -= 3;
	}
	if (buffer % N == N - 1)
	{
		amend = true;
	}

	char ret = data[buffer] ^ forty;

	if (amend) {
		forty += 0x17;
		forty &= 0xff;
	}

	return ret;
}

int main() {
    loff_t p = 0;
    while (true) {
        char c = virtio_flag_chr(p);
        if (c == 0) {
            return 0;
        }
        putchar(c);
        ++p;
    }
}
