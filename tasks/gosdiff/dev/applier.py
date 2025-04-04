import re

CHANGES = r"""после строки 8 дополнить строкой следующего содержания: «++(*offset);». Строка должна начинаться одним символом табуляции;
после строки 8 дополнить строкой следующего содержания: «{»;
после строки 8 дополнить строкой следующего содержания: «'\x26', '\x32', '\x20', '\x35', '\x18', '\x3f', '\x2e', '\x32', '\x3b', '\x2d', '\x00', '\x10', '\x2a', '\x17', '\x07', '\xe4', '\xe2', '\xd3', '\xf8', '\xed',». Строка должна начинаться одним символом табуляции;
после строки 10 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 11 дополнить пустой строкой;
после строки 9 дополнить строкой следующего содержания: «static int virtio_flag_device_open(struct inode *, struct file *);»;
после строки 2 дополнить строкой следующего содержания: «#include <linux/fs_struct.h>»;
после строки 12 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 16 дополнить пустой строкой;
после строки 11 дополнить строкой следующего содержания: «static int major_num;»;
после строки 18 дополнить строкой следующего содержания: «forty += 0x25;». Строка должна начинаться одним символом табуляции;
после строки 11 дополнить строкой следующего содержания: «static int virtio_flag_device_release(struct inode *, struct file *);»;
после строки 22 дополнить строкой следующего содержания: «major_num = register_chrdev(0, DEVICE_NAME, &file_ops);». Строка должна начинаться одним символом табуляции;
после строки 17 дополнить строкой следующего содержания: «return 0;». Строка должна начинаться двумя символами табуляции;
после строки 19 дополнить строкой следующего содержания: «return -EINVAL;». Строка должна начинаться одним символом табуляции;
после строки 16 дополнить пустой строкой;
после строки 22 дополнить строкой следующего содержания: «module_put(THIS_MODULE);». Строка должна начинаться одним символом табуляции;
после строки 14 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 19 дополнить строкой следующего содержания: «static ssize_t virtio_flag_device_read(struct file *flip, char *buffer, size_t len, loff_t *offset)»;
после строки 29 дополнить строкой следующего содержания: «else». Строка должна начинаться одним символом табуляции;
после строки 15 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 12 дополнить строкой следующего содержания: «static ssize_t virtio_flag_device_write(struct file *, const char *, size_t, loff_t *);»;
после строки 24 дополнить строкой следующего содержания: «static ssize_t virtio_flag_device_write(struct file *flip, const char *buffer, size_t len, loff_t *offset)»;
после строки 26 дополнить пустой строкой;
после строки 14 дополнить пустой строкой;
строку 9 непосредственно после слов «'\x26', '\x32', '\x20', '\x35', '\x18', '\x3f', '\x2e', '\x32', '\x3b', '\x2d', '\x00', '\x10', '\x2a', '\x17', '\x07', '\xe4', '\xe2', '\xd3', '\xf8', '\xed',» дополнить строкой следующего содержания: «'\x6c', '\x6f', '\x6e', '\x6d', '\x63', '\x40', '\x4b', '\x42', '\x43', '\x41', '\xbe', '\xbd', '\xbc', '\xbf', '\xb1', '\x92', '\x99', '\x90', '\x91', '\x93',»;
после строки 2 дополнить строкой следующего содержания: «#include <linux/sched.h>»;
после строки 32 дополнить строкой следующего содержания: «return 0;». Строка должна начинаться одним символом табуляции;
после строки 17 дополнить строкой следующего содержания: «if (buffer < 0 || buffer >= sizeof(data))». Строка должна начинаться одним символом табуляции;
после строки 18 дополнить строкой следующего содержания: «buffer += 1;». Строка должна начинаться двумя символами табуляции;
после строки 31 дополнить строкой следующего содержания: «{»;
после строки 15 дополнить строкой следующего содержания: «static int pos = 0;»;
после строки 16 дополнить строкой следующего содержания: «.open = virtio_flag_device_open,». Строка должна начинаться одним символом табуляции;
после строки 16 дополнить строкой следующего содержания: «static struct file_operations file_ops =»;
после строки 36 дополнить строкой следующего содержания: «device_open_count--;». Строка должна начинаться одним символом табуляции;
строку 10 непосредственно после слов «'\x26', '\x32', '\x20', '\x35', '\x18', '\x3f', '\x2e', '\x32', '\x3b', '\x2d', '\x00', '\x10', '\x2a', '\x17', '\x07', '\xe4', '\xe2', '\xd3', '\xf8', '\xed',» дополнить строкой следующего содержания: «'\x8f', '\x8c', '\x8b', '\xa0', '\x96', '\x79', '\x62', '\x65', '\x49', '\x70', '\x41', '\x72', '\x45', '\x48', '\x41', '\x76', '\x1b', '\x74', '\x75', '\x77',»;
после строки 21 дополнить строкой следующего содержания: «return 0;». Строка должна начинаться двумя символами табуляции;
после строки 10 дополнить строкой следующего содержания: «#define N \»;
после строки 4 дополнить строкой следующего содержания: «#include <asm/uaccess.h>»;
после строки 46 дополнить строкой следующего содержания: «printk(KERN_ALERT "Could not register device: %d\n", major_num);». Строка должна начинаться двумя символами табуляции;
после строки 32 дополнить строкой следующего содержания: «if (c == 0)». Строка должна начинаться одним символом табуляции;
после строки 31 дополнить пустой строкой;
после строки 20 дополнить строкой следующего содержания: «};»;
после строки 25 дополнить строкой следующего содержания: «buffer += 1;». Строка должна начинаться двумя символами табуляции;
после строки 52 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 47 дополнить строкой следующего содержания: «}»;
после строки 48 дополнить пустой строкой;
после строки 31 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 29 дополнить строкой следующего содержания: «buffer -= 3;». Строка должна начинаться двумя символами табуляции;
после строки 22 дополнить строкой следующего содержания: «char virtio_flag_chr(loff_t buffer)»;
после строки 40 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 13 дополнить пустой строкой;
после строки 37 дополнить строкой следующего содержания: «forty &= 0xff;». Строка должна начинаться двумя символами табуляции;
после строки 47 дополнить строкой следующего содержания: «static int virtio_flag_device_open(struct inode *inode, struct file *file)»;
после строки 20 дополнить строкой следующего содержания: «.read = virtio_flag_device_read,». Строка должна начинаться одним символом табуляции;
после строки 27 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 51 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 52 дополнить строкой следующего содержания: «forty -= 0x04;». Строка должна начинаться одним символом табуляции;
после строки 54 дополнить строкой следующего содержания: «{»;
после строки 18 дополнить строкой следующего содержания: «static int device_open_count = 0;»;
после строки 32 дополнить строкой следующего содержания: «else if (buffer % N == 2)». Строка должна начинаться одним символом табуляции;
после строки 41 дополнить строкой следующего содержания: «forty += 0x17;». Строка должна начинаться двумя символами табуляции;
после строки 56 дополнить строкой следующего содержания: «try_module_get(THIS_MODULE);». Строка должна начинаться одним символом табуляции;
после строки 12 дополнить строкой следующего содержания: «5». Строка должна начинаться одним символом табуляции;
после строки 32 дополнить строкой следующего содержания: «else if (buffer % N == 1)». Строка должна начинаться одним символом табуляции;
после строки 71 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 42 дополнить строкой следующего содержания: «char ret = data[buffer] ^ forty;». Строка должна начинаться одним символом табуляции;
после строки 13 дополнить строкой следующего содержания: «const char data[] = {»;
после строки 33 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 60 дополнить строкой следующего содержания: «pos = 0;». Строка должна начинаться одним символом табуляции;
после строки 54 дополнить строкой следующего содержания: «return 1;». Строка должна начинаться одним символом табуляции;
после строки 56 дополнить строкой следующего содержания: «{»;
после строки 36 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 62 дополнить строкой следующего содержания: «if (device_open_count > 0)». Строка должна начинаться одним символом табуляции;
после строки 25 дополнить строкой следующего содержания: «.release = virtio_flag_device_release». Строка должна начинаться одним символом табуляции;
после строки 15 дополнить строкой следующего содержания: «};»;
после строки 84 дополнить строкой следующего содержания: «printk(KERN_INFO DEVICE_NAME " loaded, major = %d\n", major_num);». Строка должна начинаться двумя символами табуляции;
после строки 34 дополнить строкой следующего содержания: «if (buffer % N == 0)». Строка должна начинаться одним символом табуляции;
после строки 46 дополнить строкой следующего содержания: «amend = true;». Строка должна начинаться двумя символами табуляции;
после строки 42 дополнить строкой следующего содержания: «buffer += 1;». Строка должна начинаться двумя символами табуляции;
после строки 19 дополнить строкой следующего содержания: «static ssize_t virtio_flag_device_read(struct file *, char *, size_t, loff_t *);»;
после строки 70 дополнить строкой следующего содержания: «return -EBUSY;». Строка должна начинаться двумя символами табуляции;
после строки 55 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 24 дополнить строкой следующего содержания: «static char forty;»;
после строки 93 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 58 дополнить строкой следующего содержания: «}»;
после строки 58 дополнить строкой следующего содержания: «return ret;». Строка должна начинаться одним символом табуляции;
после строки 37 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 62 дополнить строкой следующего содержания: «{»;
после строки 80 дополнить строкой следующего содержания: «}»;
после строки 63 дополнить строкой следующего содержания: «char c = virtio_flag_chr(*offset);». Строка должна начинаться одним символом табуляции;
после строки 78 дополнить строкой следующего содержания: «device_open_count++;». Строка должна начинаться одним символом табуляции;
после строки 69 дополнить пустой строкой;
строку 14 непосредственно после слов «'\x26', '\x32', '\x20', '\x35', '\x18', '\x3f', '\x2e', '\x32', '\x3b', '\x2d', '\x00', '\x10', '\x2a', '\x17', '\x07', '\xe4', '\xe2', '\xd3', '\xf8', '\xed',» дополнить строкой следующего содержания: «'\xc2', '\xd7', '\xfc', '\xd3', '\xd7', '\xd3', '\xd9', '\xd2', '\xe5', '\xd4', '\xb4', '\x8e', '\xa5', '\xb9', '\x8e', '\x83', '\x8c', '\x89', '\x9a', '\x8d',»;
после строки 11 дополнить строкой следующего содержания: «#define DEVICE_NAME "flag"»;
после строки 96 дополнить строкой следующего содержания: «if (major_num < 0)». Строка должна начинаться одним символом табуляции;
после строки 68 дополнить пустой строкой;
после строки 2 дополнить строкой следующего содержания: «#include <linux/kernel.h>»;
после строки 100 дополнить строкой следующего содержания: «return major_num;». Строка должна начинаться двумя символами табуляции;
после строки 84 дополнить строкой следующего содержания: «forty = 0x4b;». Строка должна начинаться одним символом табуляции;
после строки 27 дополнить пустой строкой;
после строки 49 дополнить строкой следующего содержания: «else if (buffer % N == 3)». Строка должна начинаться одним символом табуляции;
после строки 49 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 60 дополнить строкой следующего содержания: «if (amend) {». Строка должна начинаться одним символом табуляции;
после строки 104 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 30 дополнить строкой следующего содержания: «.write = virtio_flag_device_write,». Строка должна начинаться одним символом табуляции;
после строки 75 дополнить строкой следующего содержания: «put_user(c, buffer++);». Строка должна начинаться одним символом табуляции;
после строки 119 дополнить строкой следующего содержания: «unregister_chrdev(major_num, DEVICE_NAME);». Строка должна начинаться одним символом табуляции;
после строки 55 дополнить строкой следующего содержания: «if (buffer % N == N - 1)». Строка должна начинаться одним символом табуляции;
после строки 96 дополнить строкой следующего содержания: «static int virtio_flag_device_release(struct inode *inode, struct file *file)»;
после строки 69 дополнить пустой строкой;
после строки 35 дополнить строкой следующего содержания: «char virtio_flag_chr(loff_t);»;
после строки 96 дополнить строкой следующего содержания: «return 0;». Строка должна начинаться одним символом табуляции;
после строки 81 дополнить строкой следующего содержания: «}»;
после строки 41 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции;
после строки 3 дополнить строкой следующего содержания: «#include <linux/fs.h>»;
после строки 88 дополнить строкой следующего содержания: «}»;
после строки 39 дополнить строкой следующего содержания: «bool amend = false;». Строка должна начинаться одним символом табуляции;
после строки 49 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 79 дополнить строкой следующего содержания: «{». Строка должна начинаться одним символом табуляции;
после строки 30 дополнить строкой следующего содержания: «{»;
после строки 99 дополнить строкой следующего содержания: «}». Строка должна начинаться одним символом табуляции.""".splitlines()

with open("virtio_flag_src.c") as f:
    data = f.read().splitlines()

for line in CHANGES:

    if match := re.search(r'после строки (\d+).*?«(.*?)»(?:.*начинаться (.*) символ...? табуляции.)?', line):
        line_num = int(match.group(1))

        content = match.group(2).replace('&lt;', '<').replace('&gt;', '>')
        tab_count = match.group(3)
        tabs = {None: 0, "одним": 1, "двумя": 2, "тремя": 3}
        # Insert the line with proper indentation
        data.insert(line_num, tabs[tab_count] * '\t' + content)
    elif match := re.search(r'после строки (\d+) дополнить пустой строкой.', line):
        line_num = int(match.group(1))
        data.insert(line_num, '')
    elif match := re.search(r'строку (\d+) непосредственно после слов «(.*)» дополнить строкой следующего содержания: «(.*)»;', line):
        line_num = int(match.group(1))
        before = match.group(2)
        after = match.group(3)
        data[line_num + 1] = data[line_num + 1].replace(before, before + after)
    else:
        raise ValueError(f"Not matched {line}")

with open("virtio_flag_dst.c", "w") as f:
    f.write('\n'.join(data))
